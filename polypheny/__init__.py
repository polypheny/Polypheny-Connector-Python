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

from polypheny.connection import Connection, Cursor
from polypheny.exceptions import *

import datetime
import time
from typing import Union

# See https://peps.python.org/pep-0249/#globals
apilevel = '2.0'
threadsafety = 0
paramstyle = 'qmark'


def _make_value(constructor, *args):
    try:
        return constructor(*args)
    except (TypeError, ValueError, OverflowError, OSError) as e:
        raise DataError(str(e)) from e


def Date(year, month, day):
    return _make_value(datetime.date, year, month, day)


def Time(hour, minute, second):
    return _make_value(datetime.time, hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):
    return _make_value(datetime.datetime, year, month, day, hour, minute, second)


def DateFromTicks(ticks):
    return Date(*_make_value(time.localtime, ticks)[:3])


def TimeFromTicks(ticks):
    return Time(*_make_value(time.localtime, ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(*_make_value(time.localtime, ticks)[:6])


def Binary(string):
    try:
        return _make_value(string.encode, 'UTF-8')
    except AttributeError as e:
        raise DataError(str(e)) from e


# Intentionally omitted, we always give type_code = None, like sqlite3
# STRING = 1
# BINARY = 2
# NUMBER = 3
# DATETIME = 4
# ROWID = 5


def connect(address: Union[tuple[str, int], str] = None, *, username: str = None, password: str = None,
            transport: str = None, **kwargs) -> Connection:
    """
    Connect to a Polypheny instance with the given parameters.  When
    no parameters are given, the driver will connect via the ``unix``
    transport to ``~/.polypheny/polypheny-prism.sock``.

    :param address:  A :py:class:`str` for ``unix`` transport or a (hostname, port) :py:class:`tuple` for ``plain`` transport.
    :param username:  username
    :param password:  password
    :param transport:  Either ``plain`` or ``unix``

    """
    if address is None and transport is None and username is None and password is None and len(kwargs) == 0:
        transport = 'unix'
    elif address is None or transport is None:
        raise InterfaceError("Address and transport must be given")

    return Connection(address, username, password, transport, kwargs)
