import datetime
from typing import Union, List, Any, Dict
import secrets

import protointerface_pb2_grpc
import connection_requests_pb2
import relational_frame_pb2
import statement_requests_pb2
import transaction_requests_pb2
import value_pb2
import grpc
import rpc
from exceptions import *

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

POLYPHENY_API_MAJOR = 2
POLYPHENY_API_MINOR = 0

class Connection:
    def __init__(self, address, port, username, password):
        self.uuid = secrets.token_urlsafe(16)
        self.cursors = set()

        # TODO: default to 20590 when no port is given
        try:
            self.con = rpc.Connection(address, port)
        except ConnectionRefusedError:
            self.con = None  # Needed so destructor works
            raise Error("Connection refused") from None


        req = connection_requests_pb2.ConnectionRequest()
        req.major_api_version = POLYPHENY_API_MAJOR
        req.minor_api_version = POLYPHENY_API_MINOR
        req.username = username
        req.password = password
        req.connection_properties.is_auto_commit = False
        req.client_uuid = self.uuid
        try:
            resp = self.con.connect(req)
            if not resp.is_compatible:
                raise Error(f"Client ({POLYPHENY_API_MAJOR}.{POLYPHENY_API_MINOR}) is incompatible with Server version ({resp.major_api_version}.{resp.minor_api_version})")
        except Exception as e:
            self.con.close()
            self.con = None
            raise Error(str(e))


    def cursor(self):
        if self.chan is None:
            raise ProgrammingError('Connection is closed')
        cur = Cursor(self)
        self.cursors.add(cur)
        return cur

    def commit(self):
        if self.chan is None:
            raise ProgrammingError('Connection is closed')
        req = transaction_requests_pb2.CommitRequest()
        self.stub.CommitTransaction(req, metadata=[('clientuuid', self.uuid)])
        # TODO Handle error

    def rollback(self):
        if self.con is None:
            raise ProgrammingError('Connection is closed')
        #req = transaction_requests_pb2.RollbackRequest()
        #self.stub.RollbackTransaction(req, metadata=[('clientuuid', self.uuid)])
        # TODO Handle error

    def __del__(self):
        # TODO Thread-safety?
        self.close()

    def close(self):
        if self.con is None:
            assert len(self.cursors) == 0
            return
        self.rollback()
        for cur in list(self.cursors):  # self.cursors is materialized because cur.close modifies it
            cur.close()
        assert len(self.cursors) == 0
        req = connection_requests_pb2.DisconnectRequest()
        #self.stub.Disconnect(req, metadata=[('clientuuid', self.uuid)])
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
            # TODO when does this happen?
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
        assert self.con.stub != None
        r = statement_requests_pb2.CloseStatementRequest()
        r.statement_id = self.statement_id
        self.con.stub.CloseStatement(r, metadata=[('clientuuid', self.con.uuid)])
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
        r = statement_requests_pb2.FetchRequest()
        r.statement_id = self.statement_id
        self.frame = self.con.stub.FetchResult(r, metadata=[('clientuuid', self.con.uuid)])
        self.rows = iter(self.frame.relational_frame.rows)  # TODO result must not be relational
        return next(self.rows)  # TODO: What happens if this returns StopIteration, but another frame could be fetched?


# See ProtoValueDeserializer
def py2proto(value, v=None):
    if v is None:
        v = value_pb2.ProtoValue()
    if type(value) == bool:
        # v.type = value_pb2.ProtoValue.ProtoValueType.BOOLEAN
        v.boolean.boolean = value
    elif type(value) == int:
        if -2 ** 31 <= value <= 2 ** 31 - 1:
            # v.type = value_pb2.ProtoValue.ProtoValueType.INTEGER
            v.integer.integer = value
        elif -2 ** 63 <= value <= 2 ** 63 - 1:
            # v.type = value_pb2.ProtoValue.ProtoValueType.LONG
            v.long.long = value
        else:
            # v.type = value_pb2.ProtoValue.ProtoValueType.BIG_DECIMAL
            n = ((value.bit_length() - 1) // 8) + 1  # TODO: Does this work for negative numbers?
            v.big_decimal.unscaled_value = value.to_bytes(n, byteorder='big', signed=True)
            v.big_decimal.scale = 0
            v.big_decimal.precision = 0
            print(v.big_decimal)
    elif type(value) == bytes:
        # v.type = value_pb2.ProtoValue.ProtoValueType.BINARY
        v.binary.binary = value
        # TODO: Date
    elif type(value) == float:
        # v.type = value_pb2.ProtoValue.ProtoValueType.DOUBLE
        v.double.double = value
        # TODO: Use BigDecimal as well?
    elif type(value) == str:
        # v.type = value_pb2.ProtoValue.ProtoValueType.VARCHAR
        v.string.string = value
        # TODO: Time, Timestamp
    elif value is None:
        # v.type = value_pb2.ProtoValue.ProtoValueType.NULL
        v.null.CopyFrom(value_pb2.ProtoNull())
    elif type(value) == list:
        # v.type = value_pb2.ProtoValue.ProtoValueType.LIST
        for element in value:
            v.list.values.append(py2proto(element))
    elif type(value) == dict:  # experiment to test the server with unset values
        pass
    else:
        raise NotImplementedError

    return v


def proto2py(value):
    name = value.WhichOneof("value")
    assert name is not None
    if name == "boolean":
        return value.boolean.boolean
    elif name == "integer":
        return value.integer.integer
    elif name == "long":
        return value.long.long
    elif name == "binary":
        return value.binary.binary
    elif name == "date":
        raise NotImplementedError()
    elif name == "double":
        return value.double.double
    elif name == "float":
        return value.float.float
    elif name == "string":
        return value.string.string
    elif name == "time":
        raise NotImplementedError()
    elif name == "null":
        return None
    elif name == "big_decimal":
        print(value)
        raw = value.big_decimal.unscaled_value
        scale = value.big_decimal.scale
        prec = value.big_decimal.precision

        if scale > (2**31) - 1:
            scale = scale - 2**32

        i = int.from_bytes(raw, byteorder='big', signed=True)
        print(f'i: {i}')
        i = i * 10 ** (-scale)
        print(f'i: {i} {2**77}')
        return round(i, prec + 1)  # TODO: Round Up/Down?
    elif name == "interval":
        raise NotImplementedError()
    elif name == "user_defined_type":
        raise NotImplementedError()
    elif name == "file":
        raise NotImplementedError()
    elif name == "list":
        return list(map(lambda v: proto2py(v), value.list.values))
    elif name == "map":
        raise NotImplementedError()
    elif name == "document":
        res = {}
        for entry in value.document.entries:
            k = proto2py(entry.key)
            assert isinstance(k, str)  # TODO: Correct?
            v = proto2py(entry.value)
            res[k] = v
        return res
    elif name == "node":
        raise NotImplementedError()
    elif name == "edge":
        raise NotImplementedError()
    elif name == "path":
        raise NotImplementedError()
    elif name == "graph":
        raise NotImplementedError()
    elif name == "row_id":
        raise NotImplementedError()
    else:
        raise RuntimeError("Unhandled value type")


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

    def execute(self, query: str, params: Union[List[Any], Dict[str, Any]] = None, *, fetch_size: int = None, ddl_hack: bool = False) -> None:
        """
        Executes a SQL query.

        @param query:
        @param params:
        @param fetch_size:
        @return:
        """
        if self.con is None:
            raise Error("Cursor is closed")

        self.reset()

        if params is None:  # Unparameterized query
            req = statement_requests_pb2.ExecuteUnparameterizedStatementRequest()
            req.language_name = 'sql'
            req.statement = query
            if fetch_size:
                req.fetch_size = fetch_size
            resp = self.con.stub.ExecuteUnparameterizedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            next(resp)  # Contains only statement_id
            if ddl_hack:
                return
            try:
                r = next(resp)
                assert r.HasField("result")  # Is this always true?
                # self.rowcount = r.result.scalar # Can this be relied upon?
                assert r.result.HasField("frame")  # Is this always true?
                self.derive_description(r.result.frame.relational_frame)
                self.result = ResultCursor(self.con, r.statement_id, r.result.frame)
            except Exception as e:
                print(e)
            return

        req = statement_requests_pb2.PrepareStatementRequest()
        req.language_name = "sql"
        req.statement = query
        if type(params) == list or type(params) == tuple:
            resp = self.con.stub.PrepareIndexedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            statement_id = resp.statement_id
            req = statement_requests_pb2.ExecuteIndexedStatementRequest()
            req.statement_id = statement_id
            req.parameters.parameters.extend(list(map(py2proto, params)))
            resp = self.con.stub.ExecuteIndexedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            self.derive_description(resp.frame.relational_frame)
            self.result = ResultCursor(self.con, statement_id, resp.frame)
        elif type(params) == dict:
            resp = self.con.stub.PrepareNamedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            statement_id = resp.statement_id
            req = statement_requests_pb2.ExecuteNamedStatementRequest()
            req.statement_id = statement_id
            for k, v in params.items():
                py2proto(v, req.parameters.parameters[k])
            resp = self.con.stub.ExecuteNamedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            self.derive_description(resp.frame.relational_frame)
            self.result = ResultCursor(self.con, statement_id, resp.frame)
        else:
            raise Error("Unexpected type for params " + str(type(params)))

    def executemany(self, query, params):
        # TODO: Optimize, this is to exercise the execute code more
        for param in params:
            self.execute(query, param)

    def executeany(self, lang: str, query: str, params: Union[List[Any], Dict[str, Any]] = None, *, fetch_size: int = None) -> None:
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
            req = statement_requests_pb2.ExecuteUnparameterizedStatementRequest()
            req.language_name = lang
            req.statement = query
            if fetch_size:
                req.fetch_size = fetch_size
            resp = self.con.stub.ExecuteUnparameterizedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            next(resp)  # Contains only statement_id
            try:
                r = next(resp)
                assert r.HasField("result")  # Is this always true?
                # self.rowcount = r.result.scalar # Can this be relied upon?
                assert r.result.HasField("frame")  # Is this always true?
                self.derive_description(r.result.frame.relational_frame)
                self.result = ResultCursor(self.con, r.statement_id, r.result.frame)
            except Exception as e:
                print(e)
            return

        req = statement_requests_pb2.PrepareStatementRequest()
        req.language_name = lang
        req.statement = query
        if type(params) == list or type(params) == tuple:
            resp = self.con.stub.PrepareIndexedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            statement_id = resp.statement_id
            req = statement_requests_pb2.ExecuteIndexedStatementRequest()
            req.statement_id = statement_id
            req.parameters.parameters.extend(list(map(py2proto, params)))
            resp = self.con.stub.ExecuteIndexedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            self.derive_description(resp.frame.relational_frame)
            self.result = ResultCursor(self.con, statement_id, resp.frame)
        elif type(params) == dict:
            resp = self.con.stub.PrepareNamedStatement(req, metadata=[('clientuuid', self.con.uuid)])
            statement_id = resp.statement_id
            req = statement_requests_pb2.ExecuteNamedStatementRequest()
            req.statement_id = statement_id
            for k, v in params.items():
                py2proto(v, req.parameters.parameters[k])
            resp = self.con.stub.ExecuteNamedStatement(req, metadata=[('clientuuid', self.con.uuid)])
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
