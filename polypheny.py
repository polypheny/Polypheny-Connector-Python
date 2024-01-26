import protointerface_pb2_grpc
import connection_requests_pb2
import statement_requests_pb2
import transaction_requests_pb2
import value_pb2
import grpc
import secrets

import datetime

apilevel = '2.0'
threadsafety = 0
paramstyle = 'qmark'


# Errors
class Warning(Exception):
    pass


class Error(Exception):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class DataError(DatabaseError):
    pass


class OperationalError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class InternalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass


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
        self.uuid = secrets.token_urlsafe(16)
        self.cursors = set()

        # TODO: default to 20590 when no port is given
        self.chan = grpc.insecure_channel(address + ':' + str(port))
        self.stub = protointerface_pb2_grpc.ProtoInterfaceStub(self.chan)

        req = connection_requests_pb2.ConnectionRequest()
        req.major_api_version = 2
        req.minor_api_version = 0
        req.username = username
        req.password = password
        req.connection_properties.is_auto_commit = False
        req.client_uuid = self.uuid
        try:
            resp = self.stub.Connect(req)
        except grpc._channel._InactiveRpcError as e:
            if 'Connection refused' in e.details():  # Not pretty
                raise Error('Connection refused') from None
            raise Error(str(e)) from None

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
        if self.chan is None:
            raise ProgrammingError('Connection is closed')
        req = transaction_requests_pb2.RollbackRequest()
        self.stub.RollbackTransaction(req, metadata=[('clientuuid', self.uuid)])
        # TODO Handle error

    #def __del__(self):
    #    # TODO Thread-safety?
    #    try:
    #        if self.chan is not None: # move into close
    #            self.close()
    #    except Exception:
    #        pass # Happen when connecting without the database running, because self.chan is not None, but cannot be closed

    def close(self):
        if self.chan is None:
            assert len(self.cursors) == 0
            return
        assert self.chan is not None
        self.rollback()
        for cur in list(self.cursors):  # self.cursors is materialized because cur.close modifies it
            cur.close()
        assert len(self.cursors) == 0
        req = connection_requests_pb2.DisconnectRequest()
        self.stub.Disconnect(req, metadata=[('clientuuid', self.uuid)])
        self.chan.close()
        self.chan = None
        self.stub = None


class ResultCursor:
    def __init__(self, con, statement_id, frame):
        self.con = con
        self.statement_id = statement_id
        self.frame = frame
        self.rows = iter(self.frame.relational_frame.rows)  # TODO result could be not relational

    def __del__(self):
        self.close()

    def close(self):
        assert self.con.stub != None
        r = statement_requests_pb2.CloseStatementRequest()
        r.statement_id = self.statement_id
        self.con.stub.CloseStatement(r, metadata=[('clientuuid', self.con.uuid)])

    def __iter__(self):
        return self

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
        #v.type = value_pb2.ProtoValue.ProtoValueType.BOOLEAN
        v.boolean.boolean = value
    elif type(value) == int:
        if -2**31 <= value <= 2**31-1:
            #v.type = value_pb2.ProtoValue.ProtoValueType.INTEGER
            v.integer.integer = value
        elif -2**63 <= value <= 2**63-1:
            #v.type = value_pb2.ProtoValue.ProtoValueType.LONG
            v.long.long = value
        else:
            #v.type = value_pb2.ProtoValue.ProtoValueType.BIG_DECIMAL
            v.big_decimal.unscaled_value = value.to_bytes(8, byteorder='big', signed=True) # TODO: Fix length
            v.big_decimal.scale = 0
            v.big_decimal.precision = 0
    elif type(value) == bytes:
        #v.type = value_pb2.ProtoValue.ProtoValueType.BINARY
        v.binary.binary = value
        # TODO: Date
    elif type(value) == float:
        #v.type = value_pb2.ProtoValue.ProtoValueType.DOUBLE
        v.double.double = value
        # TODO: Use BigDecimal as well?
    elif type(value) == str:
        #v.type = value_pb2.ProtoValue.ProtoValueType.VARCHAR
        v.string.string = value
        # TODO: Time, Time Stamp
    elif type(value) == None:
        #v.type = value_pb2.ProtoValue.ProtoValueType.NULL
        v.null.CopyFrom(value_pb2.ProtoNull)
    elif type(value) == list:
        #v.type = value_pb2.ProtoValue.ProtoValueType.LIST
        for element in value:
            v.list.values.append(py2proto(element))
    elif type(value) == dict: # experiment to test the server with unset values
        pass
    else:
        raise NotImplementedError

    return v


def proto2py(value):
    name = value.WhichOneof("value")  # TODO: should we use the type?
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
        return value.date.date  # TODO: Wrong
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
        raw = value.big_decimal.unscaled_value
        scale = value.big_decimal.scale
        prec = value.big_decimal.precision

        i = int.from_bytes(raw, byteorder='big', signed=True)
        i = i * 10 ** (-scale)
        return round(i, prec + 1)  # TODO: Round Up/Down?
    elif name == "interval":
        raise NotImplementedError()
    elif name == "user":
        raise NotImplementedError()
    elif name == "file":
        raise NotImplementedError()
    elif name == "list":
        raise NotImplementedError()
    elif name == "map":
        raise NotImplementedError()
    elif name == "document":
        raise NotImplementedError()
    elif name == "node":
        raise NotImplementedError()
    elif name == "edge":
        raise NotImplementedError()
    elif name == "path":
        raise NotImplementedError()
    elif name == "graph":
        raise NotImplementedError()
    elif name == "row":
        raise NotImplementedError()
    else:
        breakpoint() # TODO
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

    #def callproc(self):
    # optional

    def __del__(self):
        self.close()

    def close(self):
        # TODO: Error when already closed?
        assert self.con is not None or self.result is None
        if self.con is not None:
            if self.result is not None:
                self.result.close()
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

    def execute(self, query, params=None, *, fetch_size=None):
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
            next(resp) # Contains only statement_id
            r = next(resp)
            assert r.HasField("result") # Is this always true?
            #self.rowcount = r.result.scalar # Can this be relied upon?
            if r.result.HasField("frame"):
                self.derive_description(r.result.frame.relational_frame)
                self.result = ResultCursor(self.con, r.statement_id, r.result.frame)
            else:
                #self.result = EmptyResultCursor()
                self.result = None
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

    def fetchone(self):
        if self.con is None:
            raise ProgrammingError("Cursor is closed")

        if self.result is None:
            raise ProgrammingError("No statement was yet executed")

        try:
            n = next(self.result)
        except StopIteration:
            return None

        v = []
        for value in n.values:
            v.append(proto2py(value))

        return v

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
    #def nextset(self):
    #    pass

    def setinputsizes(self, sizes):
        pass  # We are free to do nothing

    def setoutputsize(self, sizes, column=None):
        pass  # We are free to do nothing


def connect(address, port, /, username, password):
    return Connection(address, port, username, password)
