from polypheny.connection import Connection, Cursor
from polypheny.exceptions import *

import datetime
from typing import Union, Tuple

apilevel = '2.0'
threadsafety = 0
paramstyle = 'qmark'


def Date(year, month, day):
    return datetime.date(year, month, day)


def Time(hour, minute, second):
    return datetime.time(hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):
    return datetime.datetime(year, month, day, hour, minute, second)


# See PEP 249
import time


def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])  # TODO: Really local time?


def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])


def Binary(string):
    return string.encode('UTF-8')


# Intentionally omitted, we always give type_code = None, like sqlite3
# STRING = 1
# BINARY = 2
# NUMBER = 3
# DATETIME = 4
# ROWID = 5


# TODO: Change Tuple to tuple when Python 3.8 is no longer supported
def connect(address: Union[Tuple[str, int], str] = None, *, username: str = None, password: str = None, transport: str = 'unix', **kwargs) -> Connection:
    """
    Connect to a Polypheny instance

    :param address:  A :py:class:`str` for ``unix`` transport or a (hostname, port) :py:class:`tuple` for ``plain`` transport.  :py:class:`None` tries to connect to ``~/.polypheny/polypheny-prism.sock``.
    :param username:  username
    :param password:  password
    :param transport:  Either ``plain`` or ``unix``
    """
    return Connection(address, username, password, transport, kwargs)
