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

# Python Db API v2
# https://www.python.org/dev/peps/pep-0249/


apilevel = "2.0"
threadsafety = 1 # Threads may share the module, but not connections.
paramstyle = "qmark" # Question mark style, e.g. ...WHERE name=?

# TODO allow multiple paramstyles and parse individuallay:
# See: https://github.com/snowflakedb/snowflake-connector-python/blob/master/src/snowflake/connector/connection.py#L1126


from polypheny.version import VERSION
from polypheny.avatica import PolyphenyAvaticaClient
from polypheny.connection import PolyphenyConnection
from polypheny.environment import (POLYPHENY_CONNECTOR_VERSION)


def Connect(host, port, protocol="http", **kwargs):

    """Connects to a Polypheny server.

    :param host:
        Polypheny server host, e.g. ``localhost``

    :param port:
        port to the Phoenix query server, e.g. ``20591``

    :param protocol:
        Transport protocol to connect to host, e.g. ``http`` or ``https``

    :param max_retries:
        The maximum number of retries in case there is a connection error.

    :returns:
        :class:`~polypheny.connection.PolyphenyConnection` object.
    """

    polypheny_client = PolyphenyAvaticaClient(host, port, protocol)
    polypheny_client.connect()
    return PolyphenyConnection(polypheny_client, **kwargs)
    


connect = Connect

__version__ = POLYPHENY_CONNECTOR_VERSION


