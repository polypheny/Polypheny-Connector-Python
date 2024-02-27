import socket

from exceptions import *
import protointerface_pb2

class Connection:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.con = socket.create_connection((address, port))
        self.id = 1

    def close(self):
        if self.con is None:
            return
        self.con.close()
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
        
    def connect(self, req):
        msg = self.new_request()
        msg.connection_request.MergeFrom(req)

        self.send_msg(msg)
        r = self.recv_msg()
        assert r.id == msg.id
        assert r.last
        return r.connection_response
