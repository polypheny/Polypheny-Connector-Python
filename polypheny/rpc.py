# Copyright 2024 The Polypheny Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import socket
from contextlib import suppress

from google.protobuf.message import DecodeError

from polypheny.exceptions import Error, InterfaceError, OperationalError, _server_error
from polypheny.serialize import py2proto
from org.polypheny.prism import protointerface_pb2
from org.polypheny.prism import statement_requests_pb2
from org.polypheny.prism import transaction_requests_pb2
from org.polypheny.prism import connection_requests_pb2
from org.polypheny.prism import version

POLYPHENY_API_MAJOR = version.MAJOR_VERSION
POLYPHENY_API_MINOR = version.MINOR_VERSION

class PlainTransport:
    VERSION = "plain-v1@polypheny.com"

    def __init__(self, address):
        self.con = socket.create_connection(address)
        try:
            self.con.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.exchange_version(self.VERSION)
        except (Error, OSError):
            with suppress(OSError):
                self.close()
            raise

    def exchange_version(self, version):
        bl = self._recv_exact(1)
        n = int.from_bytes(bl, byteorder='little')
        if n > 127:
            raise InterfaceError("Invalid version length")
        remote_version = self._recv_exact(n)
        if not remote_version.endswith(b'\n'):
            raise InterfaceError("Invalid version message")

        if remote_version[0:-1] != version.encode():
            raise InterfaceError(f"Unsupported version: {repr(remote_version[0:-1])} expected {version.encode()}")

        self.con.sendall(bl + remote_version)

    def send_msg(self, serialized):
        n = len(serialized)
        bl = n.to_bytes(length=8, byteorder='little')
        self.con.sendall(bl + serialized)

    def _recv_exact(self, size):
        data = bytearray()
        while len(data) < size:
            chunk = self.con.recv(size - len(data))
            if not chunk:
                raise OperationalError()
            data.extend(chunk)
        return bytes(data)

    def recv_msg(self):
        size = int.from_bytes(self._recv_exact(8), 'little')
        return self._recv_exact(size)

    def close(self):
        if self.con is not None:
            self.con.close()
            self.con = None


class UnixTransport(PlainTransport):
    VERSION = "unix-v1@polypheny.com"

    def __init__(self, path):
        self.con = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if path is None:
            path = os.path.expanduser("~/.polypheny/polypheny-prism.sock")
        try:
            self.con.connect(path)
            self.exchange_version(self.VERSION)
        except (Error, OSError, TypeError, ValueError):
            with suppress(OSError):
                self.close()
            raise


class Connection:
    def __init__(self, address, transport, kwargs):
        try:
            if transport == "plain":
                self.con = PlainTransport(address)
            elif transport == "unix":
                self.con = UnixTransport(address)
            else:
                raise InterfaceError(f"Unknown transport: {transport}")
        except ConnectionRefusedError:
            raise OperationalError("Connection refused") from None
        except OSError as e:
            raise OperationalError(str(e)) from e
        except (AttributeError, TypeError, ValueError, OverflowError) as e:
            raise InterfaceError(str(e)) from e
        self.id = 1

    def close(self):
        if self.con is None:
            return
        try:
            self.disconnect()
        except Error:
            pass
        finally:
            self.abort()

    def abort(self):
        transport = self.con
        self.con = None
        if transport is not None:
            with suppress(OSError):
                transport.close()

    def new_request(self):
        msg = protointerface_pb2.Request()
        msg.id = self.id
        self.id += 1
        return msg

    def send_msg(self, msg):
        if self.con is None:
            raise OperationalError("Connection to the server is lost")
        try:
            self.con.send_msg(msg.SerializeToString())
        except OSError as e:
            self.abort()
            raise OperationalError(str(e)) from e

    def recv_msg(self, request_id=None):
        if self.con is None:
            raise OperationalError("Connection to the server is lost")
        r = protointerface_pb2.Response()
        try:
            r.ParseFromString(self.con.recv_msg())
        except OperationalError:
            self.abort()
            raise
        except OSError as e:
            self.abort()
            raise OperationalError(str(e)) from e
        except (DecodeError, ValueError, OverflowError) as e:
            self.abort()
            raise InterfaceError(str(e)) from e
        if request_id is not None and r.id != request_id:
            self.abort()
            raise InterfaceError(f"Unexpected Prism response ID {r.id}, expected {request_id}")
        if r.WhichOneof('type') == 'error_response':
            self._require_response(r, 'error_response')
            raise _server_error(r.error_response)
        return r

    def _require_response(self, response, response_type, *, last=True):
        actual_type = response.WhichOneof('type')
        if response.last != last or actual_type is None or (response_type and actual_type != response_type):
            self.abort()
            raise InterfaceError(f"Unexpected Prism response: {actual_type} (last={response.last})")

    def call(self, msg, response_type=None):
        self.send_msg(msg)
        response = self.recv_msg(msg.id)
        self._require_response(response, response_type)
        return response

    def connect(self, username, password, auto_commit):
        msg = self.new_request()
        req = msg.connection_request
        try:
            if username is not None:
                req.username = username
            if password is not None:
                req.password = password
            req.major_api_version = POLYPHENY_API_MAJOR
            req.minor_api_version = POLYPHENY_API_MINOR
            req.connection_properties.is_auto_commit = auto_commit
        except (TypeError, ValueError, OverflowError) as e:
            raise InterfaceError(str(e)) from e

        return self.call(msg, 'connection_response').connection_response

    def disconnect(self):
        msg = self.new_request()
        req = connection_requests_pb2.DisconnectRequest()
        msg.disconnect_request.MergeFrom(req)

        return self.call(msg, 'disconnect_response').disconnect_response

    def commit(self):
        msg = self.new_request()
        req = transaction_requests_pb2.CommitRequest()
        msg.commit_request.MergeFrom(req)

        return self.call(msg, 'commit_response').commit_response

    def rollback(self):
        msg = self.new_request()
        req = transaction_requests_pb2.RollbackRequest()
        msg.rollback_request.MergeFrom(req)
        return self.call(msg, 'rollback_response').rollback_response

    def execute_unparameterized_statement(self, language_name, statement, fetch_size, namespace):
        msg = self.new_request()
        req = statement_requests_pb2.ExecuteUnparameterizedStatementRequest()
        req.language_name = language_name
        req.statement = statement
        if fetch_size:
            req.fetch_size = fetch_size
        if namespace:
            req.namespace_name = namespace

        msg.execute_unparameterized_statement_request.MergeFrom(req)

        self.send_msg(msg)
        started = self.recv_msg(msg.id)
        self._require_response(started, 'statement_response', last=False)
        try:
            completed = self.recv_msg(msg.id)
        except Error:
            # Prism allocated a statement before evaluating the query.
            with suppress(Error):
                self.close_statement(started.statement_response.statement_id)
            raise
        self._require_response(completed, 'statement_response')
        return completed.statement_response

    def prepare_indexed_statement(self, language_name, statement, namespace):
        msg = self.new_request()
        req = msg.prepare_indexed_statement_request
        req.language_name = language_name
        req.statement = statement
        if namespace:
            req.namespace_name = namespace
        return self.call(msg, 'prepared_statement_signature').prepared_statement_signature

    def execute_indexed_statement(self, statement_id, params, fetch_size):
        msg = self.new_request()
        req = msg.execute_indexed_statement_request
        req.statement_id = statement_id
        req.parameters.parameters.extend(list(map(py2proto, params)))
        if fetch_size:
            req.fetch_size = fetch_size
        return self.call(msg, 'statement_result').statement_result

    def prepare_named_statement(self, language_name, statement, namespace):
        msg = self.new_request()
        req = msg.prepare_named_statement_request
        req.language_name = language_name
        req.statement = statement
        if namespace:
            req.namespace_name = namespace
        return self.call(msg, 'prepared_statement_signature').prepared_statement_signature

    def execute_named_statement(self, statement_id, params, fetch_size):
        msg = self.new_request()
        req = msg.execute_named_statement_request
        req.statement_id = statement_id
        if fetch_size:
            req.fetch_size = fetch_size
        for k, v in params.items():
            py2proto(v, req.parameters.parameters[k])
        return self.call(msg, 'statement_result').statement_result

    def fetch(self, statement_id, fetch_size):
        msg = self.new_request()
        req = msg.fetch_request
        req.statement_id = statement_id
        if fetch_size:
            req.fetch_size = fetch_size

        return self.call(msg, 'frame').frame

    def close_statement(self, statement_id):
        if self.con is None:
            return
        msg = self.new_request()
        msg.close_statement_request.statement_id = statement_id
        return self.call(msg, 'close_statement_response').close_statement_response
