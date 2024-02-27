import socket

from exceptions import *
import protointerface_pb2
import transaction_requests_pb2

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
            self.con.disconnect()
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
            raise Error(r.error_response.message)
        return r

    def call(self, msg):
        self.send_msg(msg)
        response = self.recv_msg()
        assert response.id == msg.id
        assert response.last
        return response

    def connect(self, req):
        msg = self.new_request()
        msg.connection_request.MergeFrom(req)

        return self.call(msg).connection_response

    def disconnect(self):
        msg = self.new_request()
        req = transaction_requests_pb2.DisconnectRequest()
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
