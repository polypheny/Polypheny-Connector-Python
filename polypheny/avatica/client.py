#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2021 The Polypheny Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#  http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Implementation of the JSON-over-HTTP RPC protocol used by Avatica."""


import socket
import pprint
import math
import logging
import time
from polypheny.errors import *
from polypheny.avatica.protobuf import requests_pb2, common_pb2, responses_pb2

from html.parser import HTMLParser
import http.client as httplib
import urllib.parse as urlparse


from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)


# Default configs, tuple of default variable and accepted types
DEFAULT_CONFIGURATION: Dict[str, Tuple[Any, Union[Type, Tuple[Type, ...]]]] = {
    "host": ("127.0.0.1", str),  # standard
    "port": (20591, (int, str)),  # standard
    "max_retries": (3, (int, str)),  # standard
    "autocommit": (True, (bool, str)),  # standard
}



# Relevant properties as defined by https://calcite.apache.org/avatica/docs/client_reference.html
OPEN_CONNECTION_PROPERTIES = (
    'user',  # User for the database connection
    'password',  # Password for the user
)


__all__ = ['PolyphenyAvaticaClient']

logger = logging.getLogger(__name__)


#################
##    GLOBAL   ##
#################


def parse_connection_params(host, port, protocol):

    # Simplify protocol for construction
    protocol = protocol.replace('\\', '').replace(':','')

    if protocol != "http" and protocol != "https":
        raise ProgrammingError("Error: '%s' is not a supported protocol" % ( protocol ))

    url = _build_connection_string(protocol,host, port)

    url = urlparse.urlparse(url)
    if not url.scheme and not url.netloc and url.path:
        netloc = url.path
        if ':' not in netloc:
            netloc = '{}:20591'.format(netloc)
        return urlparse.ParseResult('http', netloc, '/', '', '', '')
    return url




def parse_error_page(html):
    parser = JettyErrorPageParser()
    parser.feed(html)
    if parser.title == ['HTTP ERROR: 500']:
        message = ' '.join(parser.message).strip()
        raise InternalError(message)
    


def parse_error_protobuf(text):
    message = common_pb2.WireMessage()
    message.ParseFromString(text)

    err = responses_pb2.ErrorResponse()
    err.ParseFromString(message.wrapped_message)

    raise Error(err.error_code, err.sql_state, err.error_message)



def _build_connection_string(protocol, host, port):
    return protocol + '://' + host + ':' + str(port)


####################
## HELPER Classes ##
####################


class JettyErrorPageParser(HTMLParser):
    """This is a helper class, which is used internally
    by class:`~polypheny.connection.PolyphenyAvaticaClient`
    
    to parse inforamtion and errors of the Avatica RPCs servers.
    JettyServer

    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.path = []
        self.title = []
        self.message = []



    def handle_starttag(self, tag, attrs):
        self.path.append(tag)



    def handle_endtag(self, tag):
        self.path.pop()



    def handle_data(self, data):
        if len(self.path) > 2 and self.path[0] == 'html' and self.path[1] == 'body':
            if len(self.path) == 3 and self.path[2] == 'h2':
                self.title.append(data.strip())
            elif len(self.path) == 4 and self.path[2] == 'p' and self.path[3] == 'pre':
                self.message.append(data.strip())





class PolyphenyAvaticaClient(object):
    """Client for Polypheny's custom Avatica-RPC server.
    It connects to Polyheny's JDBC Interface.

    This exposes all low-level functionality that the Avatica
    server provides, using the native terminology. 

    You most likely do not want to use this class directly, but rather get connect
    to a server using :func:`polypheny.connect`.
    """

    def __init__(self, host, port, protocol, max_retries=None):
        """Constructs a new client object.

        :param host:
            host which runs Polypheny's JDBC interface.

        :param port:
            connection port of server.

        :param protocol:
            protocol to use for connection setup ``https`` or ``http``. 
        """
        self.url = parse_connection_params(host, port, protocol)
        self.max_retries = max_retries if max_retries is not None else 3
        self.connection = None



    def connect(self):
        """Opens a HTTP connection to the RPC server."""
        logger.debug("Opening connection to %s:%s", self.url.hostname, self.url.port)
        try:
            self.connection = httplib.HTTPConnection(self.url.hostname, self.url.port)
            self.connection.connect()
            
        except (httplib.HTTPException, socket.error) as e:
            raise InterfaceError('Unable to connect to the specified service', e)



    def close(self):
        """Closes the HTTP connection to the RPC server."""
        if self.connection is not None:
            logger.debug("Closing connection to %s:%s", self.url.hostname, self.url.port)
            try:
                self.connection.close()
            except httplib.HTTPException:
                logger.warning("Error while closing connection", exc_info=True)
            self.connection = None



    def open_connection(self, connection_id, info=None):
        """Opens a new connection.
        :param connection_id:
            ID of the connection to open.
        
        :param info:
            Additional connectionParameters for
            openening the connection.
        """

        request = requests_pb2.OpenConnectionRequest()
        request.connection_id = connection_id

        if info is not None:
            # Info is a list of repeated pairs, setting a dict directly fails
            for k, v in info.items():
                request.info[k] = v

        logger.debug("Constructed REQUEST:" , request)

        response_data = self._apply(request)
        response = responses_pb2.OpenConnectionResponse()
        response.ParseFromString(response_data)

        logger.debug("RESPONSE: " + str(response))
    


    def close_connection(self, connection_id):
        """Closes a connection.

        :param connection_id:
            ID of the connection to close.
        """

        request = requests_pb2.CloseConnectionRequest()
        request.connection_id = connection_id
        self._apply(request)


    
    def create_statement(self, connection_id):
        """Creates a new statement.

        :param connection_id:
            ID of the current connection.

        :returns:
            New statement ID.
        """
        request = requests_pb2.CreateStatementRequest()
        request.connection_id = connection_id

        response_data = self._apply(request)
        response = responses_pb2.CreateStatementResponse()
        response.ParseFromString(response_data)

        return response.statement_id



    def close_statement(self, connection_id, statement_id):
        """Closes a statement.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to close.
        """
        request = requests_pb2.CloseStatementRequest()
        request.connection_id = connection_id
        request.statement_id = statement_id

        self._apply(request)



    def prepare_and_execute(self, connection_id, statement_id, sql, max_rows_total=None, first_frame_max_size=None):
        """Prepares and immediately executes a statement.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to prepare.

        :param sql:
            SQL query.

        :param max_rows_total:
            The maximum number of rows that will be allowed for this query.

        :param first_frame_max_size:
            The maximum number of rows that will be returned in the first Frame returned for this query.

        :returns:
            Result set with the signature of the prepared statement and the first frame data.
        """
        request = requests_pb2.PrepareAndExecuteRequest()
        request.connection_id = connection_id
        request.statement_id = statement_id
        request.sql = sql
        if max_rows_total is not None:
            request.max_rows_total = max_rows_total

        if first_frame_max_size is not None:
            request.first_frame_max_size = first_frame_max_size

        response_data = self._apply(request, 'ExecuteResponse')
        response = responses_pb2.ExecuteResponse()
        response.ParseFromString(response_data)

        return response.results



    def prepare(self, connection_id, command, max_rows_total=None):
        """Prepares a statement.

        :param connection_id:
            ID of the current connection.

        :param command:
            Qquery to be prepared SQL,CQL,MQL, etc.

        :param max_rows_total:
            The maximum number of rows that will be allowed for this query.

        :returns:
            Signature of the prepared statement.
        """
        
        request = requests_pb2.PrepareRequest()
        request.connection_id = connection_id
        request.sql = command
        if max_rows_total is not None:
            request.max_rows_total = max_rows_total

        response_data = self._apply(request)
        response = responses_pb2.PrepareResponse()
        response.ParseFromString(response_data)
        return response.statement


    def execute(self, connection_id, statement_id, signature, parameter_values=None, first_frame_max_size=None):
        """Returns a frame of rows.

        The frame describes whether there may be another frame. If there is not
        another frame, the current iteration is done when we have finished the
        rows in the this frame.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to fetch rows from.

        :param signature:
            common_pb2.Signature object

        :param parameter_values:
            A list of parameter values, if statement is to be executed; otherwise ``None``.

        :param first_frame_max_size:
            The maximum number of rows that will be returned in the first Frame returned for this query.

        :returns:
            Frame data, or ``None`` if there are no more.
        """
        request = requests_pb2.ExecuteRequest()
        request.statementHandle.id = statement_id
        request.statementHandle.connection_id = connection_id
        request.statementHandle.signature.CopyFrom(signature)

        if parameter_values is not None:
            request.parameter_values.extend(parameter_values)
            request.has_parameter_values = True

        if first_frame_max_size is not None:
            request.deprecated_first_frame_max_size = first_frame_max_size
            request.first_frame_max_size = first_frame_max_size

        response_data = self._apply(request)
        response = responses_pb2.ExecuteResponse()
        response.ParseFromString(response_data)

        return response.results


    def fetch(self, connection_id, statement_id, offset=0, frame_max_size=None):
        """Returns a frame of rows.

        The frame describes whether there may be another frame. If there is not
        another frame, the current iteration is done when we have finished the
        rows in the this frame.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to fetch rows from.

        :param offset:
            Zero-based offset of first row in the requested frame.

        :param frame_max_size:
            Maximum number of rows to return; negative means no limit.

        :returns:
            Frame data, or ``None`` if there are no more.
        """
        request = requests_pb2.FetchRequest()
        request.connection_id = connection_id
        request.statement_id = statement_id
        request.offset = offset

        if frame_max_size is not None:
            request.frame_max_size = frame_max_size

        response_data = self._apply(request)
        response = responses_pb2.FetchResponse()
        response.ParseFromString(response_data)

        return response.frame


    def commit(self, connection_id):
        """Commits the current active transaction of a connection

        :param connection_id:
            ID of the connection to commit.
        """

        request = requests_pb2.CommitRequest()
        request.connection_id = connection_id
        self._apply(request)


    def rollback(self, connection_id):
        """CommRolls back the current active transaction of a connection

        :param connection_id:
            ID of the connection to rollback.
        """

        request = requests_pb2.RollbackRequest()
        request.connection_id = connection_id
        self._apply(request)


    def _post_request(self, body, headers):
        retry_count = 2

        while True:
            logger.debug("POST %s %r %r", self.url.path, body, headers)
            try:
                self.connection.request('POST', self.url.path, body=body, headers=headers)
                response = self.connection.getresponse()

            # Graceful retry to resume and reestablish session
            except httplib.HTTPException as e:
                if retry_count > 0:
                    delay = math.exp(-retry_count)
                    logger.debug("HTTP protocol error, will retry in %s seconds...", delay, exc_info=True)
                    self.close()
                    self.connect()
                    time.sleep(delay)
                    retry_count -= 1
                    continue
                raise InterfaceError('RPC request failed', cause=e)
            else:
                if response.status == httplib.SERVICE_UNAVAILABLE:
                    if retry_count > 0:
                        delay = math.exp(-retry_count)
                        logger.debug("Service unavailable, will retry in %s seconds...", delay, exc_info=True)
                        time.sleep(delay)
                        retry_count -= 1
                        continue
                    
                return response



    def _apply(self, request_data, expected_response_type=None):
        logger.debug("Sending request\n%s", pprint.pformat(request_data))

        request_name = request_data.__class__.__name__
        message = common_pb2.WireMessage()
        message.name = 'org.apache.calcite.avatica.proto.Requests${}'.format(request_name)
        message.wrapped_message = request_data.SerializeToString()
        body = message.SerializeToString()
        headers = {'content-type': 'application/x-google-protobuf'}


        response = self._post_request(body, headers)
        response_body = response.read()

        if response.status != httplib.OK:
            logger.info("Received response\n%s", response_body)
            if b'<html>' in response_body:
                parse_error_page(response_body)
            else:
                # assume the response is in protobuf format
                parse_error_protobuf(response_body)
            raise InterfaceError('RPC request returned invalid status code', response.status)

        message = common_pb2.WireMessage()
        message.ParseFromString(response_body)

        logger.debug("Received response\n%s", message)

        if expected_response_type is None:
            expected_response_type = request_name.replace('Request', 'Response')

        expected_response_type = 'org.apache.calcite.avatica.proto.Responses$' + expected_response_type
        if message.name != expected_response_type:
            raise InterfaceError('unexpected response type "{}"'.format(message.name))

        return message.wrapped_message


