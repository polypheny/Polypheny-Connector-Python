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


import pickle
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from org.polypheny.prism import protointerface_pb2, statement_responses_pb2, value_pb2

import polypheny
from polypheny import rpc
from polypheny.serialize import proto2py, py2proto


@pytest.mark.parametrize(("sqlstate", "exception_type"), [
    ("08006", polypheny.OperationalError),
    ("28P01", polypheny.OperationalError),
    ("40001", polypheny.OperationalError),
    ("53100", polypheny.OperationalError),
    ("57014", polypheny.OperationalError),
    ("58000", polypheny.OperationalError),
    ("0A000", polypheny.NotSupportedError),
    ("22012", polypheny.DataError),
    ("23505", polypheny.IntegrityError),
    ("24000", polypheny.InternalError),
    ("25000", polypheny.InternalError),
    ("26000", polypheny.InternalError),
    ("2D000", polypheny.InternalError),
    ("XX000", polypheny.InternalError),
    ("I9000", polypheny.InternalError),
    ("3F000", polypheny.ProgrammingError),
    ("42601", polypheny.ProgrammingError),
    ("ZZ123", polypheny.DatabaseError),
    ("42", polypheny.DatabaseError),
    ("42???", polypheny.DatabaseError),
    (None, polypheny.DatabaseError),
])
def test_server_error_mapping(sqlstate, exception_type):
    # The legacy message is authoritative even when the details carry different text.
    message = "server message: duplicate primary key\n"
    response = protointerface_pb2.Response(id=1, last=True)
    response.error_response.message = message
    if sqlstate is not None:
        response.error_response.details.state = sqlstate
        response.error_response.details.error_code = 0
        response.error_response.details.message = "different text"

    connection = rpc.Connection.__new__(rpc.Connection)
    connection.con = Mock()
    connection.con.recv_msg.return_value = response.SerializeToString()

    with pytest.raises(exception_type) as caught:
        connection.recv_msg(1)
    error = caught.value
    assert type(error) is exception_type
    assert str(error) == message
    assert error.sqlstate == (None if sqlstate in ("42", "42???") else sqlstate)
    assert error.errorcode == (0 if sqlstate is not None else None)

    restored = pickle.loads(pickle.dumps(error))
    assert type(restored) is exception_type
    assert restored.args == (message,)
    assert str(restored) == message
    assert restored.sqlstate == error.sqlstate
    assert restored.errorcode == error.errorcode


def test_exception_constructible_with_message():
    error = polypheny.ProgrammingError("x")
    assert str(error) == "x"
    assert error.args == ("x",)
    assert error.sqlstate is None
    assert error.errorcode is None


def test_prism_error_without_vendor_code():
    response = protointerface_pb2.Response(id=1, last=True)
    response.error_response.details.state = "23502"
    connection = rpc.Connection.__new__(rpc.Connection)
    connection.con = Mock()
    connection.con.recv_msg.return_value = response.SerializeToString()

    with pytest.raises(polypheny.IntegrityError) as caught:
        connection.recv_msg(1)
    assert caught.value.sqlstate == "23502"
    assert caught.value.errorcode is None


@pytest.fixture
def connection(monkeypatch):
    prism = Mock()
    prism.connect.return_value = SimpleNamespace(is_compatible=True)
    monkeypatch.setattr(rpc, "Connection", Mock(return_value=prism))
    connection = polypheny.connect(("localhost", 20590), transport="plain")
    yield connection
    connection.close()


@pytest.mark.parametrize(("operation", "args"), [
    ("execute", ("SELECT 1",)),
    ("executeany", ("sql", "SELECT 1")),
    ("executemany", ("SELECT 1", [])),
    ("fetchone", ()),
    ("fetchmany", (0,)),
    ("fetchall", ()),
])
def test_closed_cursor(connection, operation, args):
    cursor = connection.cursor()
    cursor.close()
    with pytest.raises(polypheny.ProgrammingError, match="Cursor is closed"):
        getattr(cursor, operation)(*args)


@pytest.mark.parametrize(("operation", "args"), [
    ("fetchone", ()),
    ("fetchmany", (0,)),
    ("fetchall", ()),
])
def test_fetch_without_result(connection, operation, args):
    cursor = connection.cursor()
    fetch = getattr(cursor, operation)
    with pytest.raises(polypheny.ProgrammingError, match="No statement was yet executed"):
        fetch(*args)

    connection.con.execute_unparameterized_statement.return_value = (
        statement_responses_pb2.StatementResponse(
            statement_id=42, result=statement_responses_pb2.StatementResult(scalar=1),
        )
    )
    cursor.execute("INSERT INTO t VALUES (1)")
    with pytest.raises(polypheny.ProgrammingError, match="Previous statement did not produce any results"):
        fetch(*args)


@pytest.mark.parametrize("params", [1, "string", object()])
def test_invalid_query_parameters(connection, params):
    with pytest.raises(polypheny.ProgrammingError, match="Unexpected type for params"):
        connection.cursor().execute("SELECT ?", params)


@pytest.mark.parametrize("operation", ["cursor", "commit", "rollback"])
def test_closed_connection(connection, operation):
    connection.close()
    with pytest.raises(polypheny.ProgrammingError, match="Connection is closed"):
        getattr(connection, operation)()


@pytest.mark.parametrize("options", [
    {"address": ("localhost", 20590)},
    {"username": "pa"},
    {"transport": "plain"},
    {"address": ("localhost", 20590), "transport": "unknown"},
])
def test_connection_configuration(options):
    with pytest.raises(polypheny.InterfaceError):
        polypheny.connect(**options)


def test_connection_refused(monkeypatch):
    monkeypatch.setattr(rpc.socket, "create_connection", Mock(side_effect=ConnectionRefusedError))
    with pytest.raises(polypheny.OperationalError, match="^Connection refused$"):
        polypheny.connect(("localhost", 20590), transport="plain")


@pytest.mark.parametrize("during_fetch", [False, True])
def test_peer_closes_during_request(monkeypatch, during_fetch):
    def frame(response):
        wire = response.SerializeToString()
        return [len(wire).to_bytes(8, "little"), wire]

    connect = protointerface_pb2.Response(id=1, last=True)
    connect.connection_response.is_compatible = True
    messages = frame(connect)
    if during_fetch:
        started = protointerface_pb2.Response(id=2)
        started.statement_response.statement_id = 42
        completed = protointerface_pb2.Response(id=2, last=True)
        completed.statement_response.statement_id = 42
        completed.statement_response.result.frame.relational_frame.SetInParent()
        messages.extend(frame(started) + frame(completed))

    transport = rpc.PlainTransport.__new__(rpc.PlainTransport)
    socket = transport.con = Mock()
    socket.recv.side_effect = messages + [(3).to_bytes(8, "little"), b"x", b""]
    monkeypatch.setattr(rpc, "PlainTransport", Mock(return_value=transport))

    connection = polypheny.connect(("localhost", 20590), transport="plain")
    try:
        cursor = connection.cursor()
        if during_fetch:
            cursor.execute("SELECT 1")
        with pytest.raises(polypheny.OperationalError):
            if during_fetch:
                cursor.fetchone()
            else:
                cursor.execute("SELECT 1")
        with pytest.raises(polypheny.OperationalError):
            connection.rollback()
        cursor.close()
    finally:
        connection.close()
    socket.close.assert_called_once_with()
    assert socket.sendall.call_count == (3 if during_fetch else 2)


def test_unsupported_values_and_result_frames(connection):
    with pytest.raises(polypheny.NotSupportedError):
        py2proto(object())
    with pytest.raises(polypheny.NotSupportedError):
        proto2py(value_pb2.ProtoValue())

    response = statement_responses_pb2.StatementResponse(statement_id=42)
    response.result.frame.SetInParent()
    connection.con.execute_unparameterized_statement.return_value = response
    with pytest.raises(polypheny.NotSupportedError, match="Unsupported Prism result frame"):
        connection.cursor().execute("SELECT 1")
    connection.con.close_statement.assert_called_once_with(42)
