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
def wire(monkeypatch):
    transport = Mock()
    monkeypatch.setattr(rpc, "PlainTransport", Mock(return_value=transport))
    return transport


def reply(request_id, field):
    response = protointerface_pb2.Response(id=request_id, last=True)
    getattr(response, field).SetInParent()
    return response


def login_reply():
    response = reply(1, "connection_response")
    response.connection_response.is_compatible = True
    return response


def error_reply(request_id, message, sqlstate):
    response = reply(request_id, "error_response")
    response.error_response.message = message
    if sqlstate is not None:
        response.error_response.details.state = sqlstate
        response.error_response.details.error_code = 0
    return response


def statement_replies(request_id, statement_id, *, last=False):
    started = protointerface_pb2.Response(id=request_id)
    started.statement_response.statement_id = statement_id
    completed = reply(request_id, "statement_response")
    completed.statement_response.statement_id = statement_id
    frame = completed.statement_response.result.frame
    frame.is_last = last
    frame.relational_frame.SetInParent()
    if last:
        frame.relational_frame.rows.add().values.append(py2proto(1))
    return started, completed


def send_replies(wire, *responses):
    wire.recv_msg.side_effect = [response.SerializeToString() for response in responses]


def requests_sent(wire):
    return [
        protointerface_pb2.Request.FromString(call.args[0])
        for call in wire.send_msg.call_args_list
    ]


@pytest.mark.parametrize(("sqlstate", "exception_type"), [
    ("28P01", polypheny.OperationalError),
    (None, polypheny.DatabaseError),
])
def test_login_preserves_prism_error(wire, sqlstate, exception_type):
    message = "Login rejected.\n"
    send_replies(wire, error_reply(1, message, sqlstate))

    with pytest.raises(exception_type) as caught:
        polypheny.connect(("localhost", 20590), username="guest", transport="plain")

    error = caught.value
    assert type(error) is exception_type
    assert error.args == (message,)
    assert error.sqlstate == sqlstate
    assert error.errorcode == (0 if sqlstate is not None else None)
    assert [request.WhichOneof("type") for request in requests_sent(wire)] == ["connection_request"]
    wire.close.assert_called_once_with()


@pytest.mark.parametrize(("query", "params", "mode"), [
    ("INSERT INTO t VALUES (?)", (1,), "indexed"),
    ("INSERT INTO t VALUES (:id)", {"id": 1}, "named"),
])
def test_prepared_error_survives_statement_cleanup(wire, query, params, mode):
    signature = reply(2, "prepared_statement_signature")
    signature.prepared_statement_signature.statement_id = 42
    message = "Primary key conflict.\n"
    send_replies(
        wire,
        login_reply(),
        signature,
        error_reply(3, message, "23505"),
        error_reply(4, "Cleanup failed", "XX000"),
        reply(5, "rollback_response"),
        reply(6, "disconnect_response"),
    )

    connection = polypheny.connect(("localhost", 20590), transport="plain")
    try:
        cursor = connection.cursor()
        with pytest.raises(polypheny.IntegrityError) as caught:
            cursor.execute(query, params)
        assert caught.value.args == (message,)
        assert caught.value.sqlstate == "23505"
        assert caught.value.errorcode == 0
        with pytest.raises(polypheny.ProgrammingError, match="No statement was yet executed"):
            cursor.fetchone()
    finally:
        connection.close()

    requests = requests_sent(wire)
    assert [request.WhichOneof("type") for request in requests] == [
        "connection_request",
        f"prepare_{mode}_statement_request",
        f"execute_{mode}_statement_request",
        "close_statement_request",
        "rollback_request",
        "disconnect_request",
    ]
    assert requests[3].close_statement_request.statement_id == 42


@pytest.mark.parametrize("failure", ["server-error", "unsupported-frame", "unsupported-value"])
def test_fetch_failure_releases_result_and_cursor_can_recover(wire, failure):
    if failure == "server-error":
        message = "Division by zero.\n"
        continuation = error_reply(3, message, "22012")
        exception_type = polypheny.DataError
    else:
        continuation = reply(3, "frame")
        continuation.frame.is_last = True
        exception_type = polypheny.NotSupportedError
        if failure == "unsupported-value":
            rows = continuation.frame.relational_frame.rows
            rows.add().values.add(file=value_pb2.ProtoFile())
            rows.add().values.append(py2proto(7))
            message = "Unhandled value type"
        else:
            message = "Unsupported Prism result frame: None"

    send_replies(
        wire,
        login_reply(),
        *statement_replies(2, 42),
        continuation,
        reply(4, "close_statement_response"),
        reply(5, "rollback_response"),
        *statement_replies(6, 43, last=True),
        reply(7, "close_statement_response"),
        reply(8, "rollback_response"),
        reply(9, "disconnect_response"),
    )

    connection = polypheny.connect(("localhost", 20590), transport="plain")
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        with pytest.raises(exception_type) as caught:
            cursor.fetchone()
        assert type(caught.value) is exception_type
        assert caught.value.args == (message,)
        if failure == "server-error":
            assert caught.value.sqlstate == "22012"
            assert caught.value.errorcode == 0
        cleanup = requests_sent(wire)[-1]
        assert cleanup.WhichOneof("type") == "close_statement_request"
        assert cleanup.close_statement_request.statement_id == 42
        connection.rollback()
        with pytest.raises(polypheny.ProgrammingError, match="No statement was yet executed"):
            cursor.fetchone()
        cursor.execute("SELECT 1")
        assert cursor.fetchall() == [[1]]
    finally:
        connection.close()

    requests = requests_sent(wire)
    assert requests[2].fetch_request.statement_id == 42
    assert requests[4].WhichOneof("type") == "rollback_request"
    assert requests[6].close_statement_request.statement_id == 43


def test_vendor_code_without_sqlstate(wire):
    response = error_reply(1, "Login rejected.", None)
    response.error_response.details.error_code = 0
    send_replies(wire, response)

    with pytest.raises(polypheny.DatabaseError) as caught:
        polypheny.connect(("localhost", 20590), transport="plain")

    assert type(caught.value) is polypheny.DatabaseError
    assert caught.value.sqlstate is None
    assert caught.value.errorcode == 0


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
