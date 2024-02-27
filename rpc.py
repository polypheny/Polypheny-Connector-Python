import socket

from exceptions import *
from serialize import *
import protointerface_pb2
import statement_requests_pb2
import transaction_requests_pb2
import connection_requests_pb2

POLYPHENY_API_MAJOR = 2
POLYPHENY_API_MINOR = 0


class Connection:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.con = socket.create_connection((address, port))
        self.id = 1

    def close(self):
        if self.con is None:
            return
        try:
            self.disconnect()
        except Exception as e:
            pass

        try:
            self.con.close()
        except Exception:
            pass
        self.con = None

    def new_request(self):
        msg = protointerface_pb2.Request()
        msg.id = self.id
        self.id += 1
        return msg

    def send_msg(self, msg):
        serialized = msg.SerializeToString()
        n = len(serialized)
        bl = n.to_bytes(length=8, byteorder='little')
        self.con.sendall(bl)
        self.con.sendall(serialized)

    def recv_msg(self):
        bl = self.con.recv(8)
        n = int.from_bytes(bl, 'little')
        serialized = self.con.recv(n)
        r = protointerface_pb2.Response()
        r.ParseFromString(serialized)
        if r.WhichOneof('type') == 'error_response':
            # TODO: Add to error_response something to decide if this is necessary
            # self.con.close()
            # self.con = None
            raise Error(r.error_response.message)
        return r

    def call(self, msg):
        self.send_msg(msg)
        response = self.recv_msg()
        assert response.id == msg.id
        assert response.last
        return response

    def connect(self, username, password, auto_commit):
        msg = self.new_request()
        req = msg.connection_request
        req.username = username
        req.password = ''
        req.major_api_version = POLYPHENY_API_MAJOR
        req.minor_api_version = POLYPHENY_API_MINOR
        req.connection_properties.is_auto_commit = auto_commit

        return self.call(msg).connection_response

    def disconnect(self):
        msg = self.new_request()
        req = connection_requests_pb2.DisconnectRequest()
        msg.disconnect_request.MergeFrom(req)

        return self.call(msg).disconnect_response

    def commit(self):
        msg = self.new_request()
        req = transaction_requests_pb2.CommitRequest()
        msg.commit_request.MergeFrom(req)

        return self.call(msg).commit_response

    def rollback(self):
        msg = self.new_request()
        req = transaction_requests_pb2.RollbackRequest()
        msg.rollback_request.MergeFrom(req)
        return self.call(msg).rollback_response

    def execute_unparameterized_statement(self, language_name, statement, fetch_size):
        msg = self.new_request()
        req = statement_requests_pb2.ExecuteUnparameterizedStatementRequest()
        req.language_name = language_name
        req.statement = statement
        if fetch_size:
            req.fetch_size = fetch_size

        msg.execute_unparameterized_statement_request.MergeFrom(req)

        self.send_msg(msg)
        self.recv_msg()
        r = self.recv_msg()
        assert r.id == msg.id
        assert r.last
        return r.statement_response

    def prepare_indexed_statement(self, language_name, statement):
        msg = self.new_request()
        req = msg.prepare_indexed_statement_request
        req.language_name = language_name
        req.statement = statement
        return self.call(msg).prepared_statement_signature

    def execute_indexed_statement(self, statement_id, params, fetch_size):
        msg = self.new_request()
        req = msg.execute_indexed_statement_request
        req.statement_id = statement_id
        req.parameters.parameters.extend(list(map(py2proto, params)))
        return self.call(msg).statement_result

    def prepare_named_statement(self, language_name, statement):
        msg = self.new_request()
        req = msg.prepare_named_statement_request
        req.language_name = language_name
        req.statement = statement
        return self.call(msg).prepared_statement_signature

    def execute_named_statement(self, statement_id, params, fetch_size):
        msg = self.new_request()
        req = msg.execute_named_statement_request
        req.statement_id = statement_id
        for k, v in params.items():
            py2proto(v, req.parameters.parameters[k])
        return self.call(msg).statement_result

    def fetch(self, statement_id, fetch_size):
        msg = self.new_request()
        req = msg.fetch_request
        req.statement_id = statement_id
        if fetch_size:
            req.fetch_size = fetch_size

        return self.call(msg).frame

    def close_statement(self, statement_id):
        msg = self.new_request()
        msg.close_statement_request.statement_id = statement_id
        return self.call(msg).close_statement_response
