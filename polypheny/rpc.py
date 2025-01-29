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

from polypheny.exceptions import Error
from polypheny.serialize import *
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
        self.con.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.exchange_version(self.VERSION)

    def exchange_version(self, version):
        bl = self.con.recv(1)
        if len(bl) != 1:
            raise EOFError
        n = int.from_bytes(bl, byteorder='little')
        if n > 127:
            raise Error("Invalid version length")
        remote_version = self.con.recv(n)
        if remote_version[-1] != 0x0a:
            raise Error("Invalid version message")

        if remote_version[0:-1] != version.encode():
            raise Error(f"Unsupported version: {repr(remote_version[0:-1])} expected {version.encode()}")

        self.con.sendall(bl + remote_version)

    def send_msg(self, serialized):
        n = len(serialized)
        bl = n.to_bytes(length=8, byteorder='little')
        self.con.sendall(bl + serialized)

    def recv_msg(self):
        bl = self.con.recv(8)
        if len(bl) != 8:
            raise EOFError
        n = int.from_bytes(bl, 'little')
        raw = self.con.recv(n)
        if len(raw) != n:
            raise EOFError
        return raw

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
        self.con.connect(path)
        self.exchange_version(self.VERSION)


class Connection:
    def __init__(self, address, transport, kwargs):
        if transport == "plain":
            self.con = PlainTransport(address)
        elif transport == "unix":
            self.con = UnixTransport(address)
        else:
            raise Exception("Unknown transport: " + transport)
        self.id = 1

    def close(self):
        if self.con is None:
            return
        try:
            self.disconnect()
        except Exception:
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
        self.con.send_msg(msg.SerializeToString())

    def recv_msg(self):
        r = protointerface_pb2.Response()
        r.ParseFromString(self.con.recv_msg())
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
        if username is not None:
            req.username = username
        if password is not None:
            req.password = password
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
        self.recv_msg()
        r = self.recv_msg()
        assert r.id == msg.id
        assert r.last
        return r.statement_response

    def prepare_indexed_statement(self, language_name, statement, namespace):
        msg = self.new_request()
        req = msg.prepare_indexed_statement_request
        req.language_name = language_name
        req.statement = statement
        if namespace:
            req.namespace_name = namespace
        return self.call(msg).prepared_statement_signature

    def execute_indexed_statement(self, statement_id, params, fetch_size):
        msg = self.new_request()
        req = msg.execute_indexed_statement_request
        req.statement_id = statement_id
        req.parameters.parameters.extend(list(map(py2proto, params)))
        if fetch_size:
            req.fetch_size = fetch_size
        return self.call(msg).statement_result

    def prepare_named_statement(self, language_name, statement, namespace):
        msg = self.new_request()
        req = msg.prepare_named_statement_request
        req.language_name = language_name
        req.statement = statement
        if namespace:
            req.namespace_name = namespace
        return self.call(msg).prepared_statement_signature

    def execute_named_statement(self, statement_id, params, fetch_size):
        msg = self.new_request()
        req = msg.execute_named_statement_request
        req.statement_id = statement_id
        if fetch_size:
            req.fetch_size = fetch_size
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
