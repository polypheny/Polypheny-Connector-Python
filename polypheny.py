import datetime
from typing import Union, List, Any, Dict

import relational_frame_pb2
import rpc
from exceptions import *
from serialize import *

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

class Connection:
    def __init__(self, address, port, username, password):
        self.cursors = set()

        # TODO: default to 20590 when no port is given
        try:
            self.con = rpc.Connection(address, port)
        except ConnectionRefusedError:
            self.con = None  # Needed so destructor works
            raise Error("Connection refused") from None

        try:
            resp = self.con.connect(username, password, False)
            if not resp.is_compatible:
                raise Error(
                    f"Client ({rpc.POLYPHENY_API_MAJOR}.{rpc.POLYPHENY_API_MINOR}) is incompatible with Server version ({resp.major_api_version}.{resp.minor_api_version})")
        except Exception as e:
            self.con.close()
            self.con = None
            raise Error(str(e))

    def cursor(self):
        if self.con is None:
            raise ProgrammingError('Connection is closed')
        cur = Cursor(self)
        self.cursors.add(cur)
        return cur

    def commit(self):
        if self.con is None:
            raise ProgrammingError('Connection is closed')
        self.con.commit()

    def rollback(self):
        if self.con is None:
            raise ProgrammingError('Connection is closed')
        self.con.rollback()

    def __del__(self):
        # TODO Thread-safety?
        self.close()

    def close(self):
        if self.con is None:
            assert len(self.cursors) == 0
            return

        for cur in list(self.cursors):  # self.cursors is materialized because cur.close modifies it
            cur.close()
        assert len(self.cursors) == 0

        try:
            self.rollback()
        except:
            pass
        self.con.close()
        self.con = None


class ResultCursor:
    def __init__(self, con, statement_id, frame):
        self.con = con
        self.statement_id = statement_id
        self.closed = False
        self.frame = frame
        restype = self.frame.WhichOneof('result')
        if restype is None:
            # TODO does this happen?
            self.closed = True
            return
        if restype == 'relational_frame':
            self.rows = iter(self.frame.relational_frame.rows)  # TODO result could be not relational
        elif restype == 'document_frame':
            self.rows = iter(self.frame.document_frame.documents)
        else:
            self.closed = True
            raise NotImplementedError(f'Resultset of type {restype} is not implemented')

    def __del__(self):
        assert self.closed
        self.close()

    def close(self):
        if self.closed:
            return
        assert self.con.con is not None
        try:
            self.con.con.close_statement(self.statement_id)
        except Exception:
            pass
        self.con = None
        self.closed = True

    def __next__(self):
        assert self.rows is not None

        try:
            return next(self.rows)
        except StopIteration:
            if self.frame.is_last:
                raise
            return self.nextframe()

    def nextframe(self):
        self.frame = self.con.con.fetch(self.statement_id, None)  # TODO
        self.rows = iter(self.frame.relational_frame.rows)  # TODO result must not be relational
        return next(self.rows)  # TODO: What happens if this returns StopIteration, but another frame could be fetched?


class Cursor:
    def __init__(self, con):
        self.con = con
        self.result = None
        self.reset()

    def reset(self):
        if self.result is not None:
            self.result.close()
        self.description = None
        self.rowcount = -1
        self.arraysize = 1
        self.result = None

    # def callproc(self):
    # optional

    def __del__(self):
        self.close()

    def close(self):
        # TODO: Error when already closed?
        assert self.con is not None or self.result is None
        if self.con is not None:
            if self.result is not None:
                self.result.close()
                self.result = None
            self.con.cursors.remove(self)
            self.con = None

    def __iter__(self):
        return self

    def __next__(self):
        n = self.fetchone()
        if n is None:
            raise StopIteration
        return n

    def derive_description(self, relframe):
        self.description = []
        for column in relframe.column_meta:
            # TODO: Should we even bother with precision/scale/nullable?
            self.description.append(
                (column.column_label, None, None, None, None, column.precision, column.scale, column.is_nullable))

    def execute(self, query: str, params: Union[List[Any], Dict[str, Any]] = None, *, fetch_size: int = None) -> None:
        """
        Executes a SQL query.

        @param query:
        @param params:
        @param fetch_size:
        @return:
        """
        return self.executeany('sql', query, params, fetch_size=fetch_size)

    def executemany(self, query, params):
        # TODO: Optimize, this is to exercise the execute code more
        for param in params:
            self.execute(query, param)

    def executeany(self, lang: str, query: str, params: Union[List[Any], Dict[str, Any]] = None, *,
                   fetch_size: int = None) -> None:
        """
        Executes a query in language lang.

        @param lang:
        @param query:
        @param params:
        @param fetch_size:
        @return:
        """

        if self.con is None:
            raise Error("Cursor is closed")

        self.reset()

        if params is None:  # Unparameterized query
            r = self.con.con.execute_unparameterized_statement(lang, query, fetch_size)
            assert r.HasField("result")  # Is this always true?
            # self.rowcount = r.result.scalar # Can this be relied upon?
            if r.result.HasField(
                    "frame"):  # TODO Better Error when one of the fetch* methods is invoked.  Empty fake result?
                if r.result.frame.WhichOneof('result') == 'relational_frame':
                    self.derive_description(r.result.frame.relational_frame)
                self.result = ResultCursor(self.con, r.statement_id, r.result.frame)
        elif type(params) == list or type(params) == tuple:
            resp = self.con.con.prepare_indexed_statement(lang, query)
            statement_id = resp.statement_id
            resp = self.con.con.execute_indexed_statement(statement_id, params, fetch_size)
            if resp.HasField("frame"):  # TODO same as above
                if resp.frame.WhichOneof('result') == 'relational_frame':
                    self.derive_description(resp.frame.relational_frame)
                self.result = ResultCursor(self.con, statement_id, resp.frame)
        elif type(params) == dict:
            resp = self.con.con.prepare_named_statement(lang, query)
            statement_id = resp.statement_id
            resp = self.con.con.execute_named_statement(statement_id, params, fetch_size)
            if resp.HasField("frame"):  # TODO same as above
                if resp.frame.WhichOneof('result') == 'relational_frame':
                    self.derive_description(resp.frame.relational_frame)
                self.result = ResultCursor(self.con, statement_id, resp.frame)
        else:
            raise Error("Unexpected type for params " + str(type(params)))

    def fetchone(self):
        if self.con is None:
            raise ProgrammingError("Cursor is closed")

        if self.result is None:
            raise ProgrammingError("No statement was yet executed")

        try:
            n = next(self.result)
        except StopIteration:
            return None

        if isinstance(n, relational_frame_pb2.Row):
            v = []
            for value in n.values:
                v.append(proto2py(value))
            return v
        elif isinstance(n, value_pb2.ProtoDocument):
            value = value_pb2.ProtoValue()
            value.document.CopyFrom(n)
            return proto2py(value)

    def fetchmany(self, size=None):
        # TODO: Optimize, this is to exercise the fetch code more
        if size is None:
            size = self.arraysize
        results = []
        for _ in range(size):
            row = self.fetchone()
            if row is None:
                break
            results.append(row)
        return results

    def fetchall(self):
        results = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            results.append(row)
        return results

    # optional
    # def nextset(self):
    #    pass

    def setinputsizes(self, sizes):
        pass  # We are free to do nothing

    def setoutputsize(self, sizes, column=None):
        pass  # We are free to do nothing


def connect(address, port, /, username, password):
    """ Connect to a Polypheny instance
    """
    return Connection(address, port, username, password)
