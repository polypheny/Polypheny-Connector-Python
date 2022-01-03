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



import uuid
import weakref
import logging as logger

from polypheny.cursor import PolyphenyCursor
from polypheny.avatica.client import OPEN_CONNECTION_PROPERTIES
from polypheny.auth import AuthManager
from polypheny.environment import (CLIENT_NAME, CLIENT_VERSION,PLATFORM,OPERATING_SYSTEM,POLYPHENY_CONNECTOR_VERSION,PYTHON_VERSION)

from polypheny.errors import *

__all__ = ['Connection']

# According to https://www.python.org/dev/peps/pep-0249/#paramstyle
SUPPORTED_PARAMSTYLES = {
    "qmark",
    "numeric",
    "named",
    "format",
    "pyformat",
}




class PolyphenyConnection(object):
    """Implementation of the connection object for Polypheny-DB.

    Use connect(..) to get the object.

    You should not construct this object manually, use :func:`~polypheny.connect` instead.

    Attributes:
        session_id: The session ID of the connection.
        user: The user name used in the connection.
        host: The host name the connection attempts to connect to.
        port: The port to communicate with on the host
    """

    def __init__(self, client, **kwargs):

        self._client = client
        self._closed = False


        logger.info(
            "Polypheny Connector for Python Version: %s, "
            "Python Version: %s, Platform: %s",
            POLYPHENY_CONNECTOR_VERSION,
            PYTHON_VERSION,
            PLATFORM,
        )

        self._cursors = []

        # Extract properties to pass to OpenConnectionRequest
        self._connection_args = {}
        # The rest of the kwargs
        self._filtered_args = {}
        for k in kwargs:
            if k in OPEN_CONNECTION_PROPERTIES:
                self._connection_args[k] = kwargs[k]
            else:
                self._filtered_args[k] = kwargs[k]
        
              
    
        logger.debug("Trying to connect to URL:'" + str(self._client.url) + "'" )
        self.open()



    def open(self):
        """Effectiviely opens the connection."""
        self._id = str(uuid.uuid4())
        logger.debug("New connection with id: ", self._id)
        self._client.open_connection(self._id, info=self._connection_args)



    def close(self):
        """Closes the connection.
        No further operations are allowed, either on the connection or any
        of its cursors, once the connection is closed.

        If the connection is used in a ``with`` statement, this method will
        be automatically called at the end of the ``with`` block.
        """
        if self._closed:
            raise ProgrammingError('the connection is already closed')
        for cursor_ref in self._cursors:
            cursor = cursor_ref()
            if cursor is not None and not cursor._closed:
                cursor.close()

        # TODO check for open transactions and then call self.rollback()

        self._client.close_connection(self._id)
        self._client.close()
        self._closed = True



    def is_closed(self):
        """Checks whether the connection has been closed."""
        return self._closed is None



    def commit(self):
        """Commits the current transaction."""
        self._client.commit(self._id)

        if self._closed:
            raise ProgrammingError('the connection is already closed')



    def rollback(self):
        """Rolls back the current transaction."""
        self._client.rollback(self._id)

        if self._closed:
            raise ProgrammingError('the connection is already closed')



    def cursor(self, **kwargs):
        if self._closed:
            raise ProgrammingError('the connection is already closed')

        cursor = PolyphenyCursor(self,**kwargs)
        self._cursors.append(weakref.ref(cursor, self._cursors.remove))

        return cursor



    
