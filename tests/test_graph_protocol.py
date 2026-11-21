from unittest.mock import Mock

import pytest
from org.polypheny.prism import graph_frame_pb2, statement_responses_pb2, value_pb2

from polypheny.connection import ResultCursor
from polypheny.exceptions import InterfaceError
from polypheny.rpc import PlainTransport
from polypheny.serialize import proto2py, proto_graph_element2py, py2proto


def test_graph_values_inside_documents_and_lists():
    node = value_pb2.ProtoNode(id="a", name="binding", labels=["Person", "Admin"])
    node.properties["scores"].CopyFrom(py2proto([1, None, True, "✓"]))
    isolated = value_pb2.ProtoNode(id="b")
    graph = value_pb2.ProtoGraph(nodes=[node, isolated])

    document = value_pb2.ProtoValue()
    document.document.entries["graphs"].list.values.add(graph=graph)
    assert proto2py(document) == {
        "graphs": [{
            "nodes": [
                {
                    "id": "a",
                    "name": "binding",
                    "labels": ["Person", "Admin"],
                    "properties": {"scores": [1, None, True, "✓"]},
                },
                {"id": "b", "name": "", "labels": [], "properties": {}},
            ],
            "edges": [],
        }],
    }


@pytest.mark.parametrize("direction", [
    value_pb2.ProtoEdge.UNSPECIFIED,
    value_pb2.ProtoEdge.LEFT_TO_RIGHT,
    value_pb2.ProtoEdge.RIGHT_TO_LEFT,
    value_pb2.ProtoEdge.NONE,
])
def test_edge_values_preserve_endpoints_and_direction(direction):
    edge = value_pb2.ProtoEdge(
        id="e", name="relationship", left="a", right="b", direction=direction,
        labels=["KNOWS"], properties={"since": py2proto(2026)},
    )
    expected = {
        "id": "e", "name": "relationship", "labels": ["KNOWS"],
        "properties": {"since": 2026}, "left": "a", "right": "b",
        "direction": direction,
    }
    assert proto2py(value_pb2.ProtoValue(edge=edge)) == expected
    assert proto_graph_element2py(graph_frame_pb2.GraphElement(edge=edge)) == expected


def test_empty_graph_element_reports_protocol_error():
    with pytest.raises(InterfaceError, match="neither a node nor an edge"):
        proto_graph_element2py(graph_frame_pb2.GraphElement())


@pytest.mark.parametrize(("frame_type", "items_field"), [
    ("graph_frame", "element"),
    ("relational_frame", "rows"),
    ("document_frame", "documents"),
])
def test_paging_skips_empty_nonfinal_frames(frame_type, items_field):
    def frame(last=False, populated=False):
        result = statement_responses_pb2.Frame(is_last=last)
        payload = getattr(result, frame_type)
        payload.SetInParent()
        if populated:
            getattr(payload, items_field).add()
        return result

    connection = Mock()
    last = frame(last=True, populated=True)
    connection.con.fetch.side_effect = [frame(), last]
    result = ResultCursor(connection, 7, frame(), 1)
    try:
        assert next(result) == getattr(getattr(last, frame_type), items_field)[0]
        with pytest.raises(StopIteration):
            next(result)
        assert connection.con.fetch.call_count == 2
        connection.con.fetch.assert_called_with(7, 1)
    finally:
        result.close()
    connection.con.close_statement.assert_called_once_with(7)


def test_fragmented_graph_message_is_read_in_full():
    response = statement_responses_pb2.Frame(is_last=True)
    response.graph_frame.element.add(node=value_pb2.ProtoNode(id="a"))
    wire = response.SerializeToString()
    length = len(wire).to_bytes(8, "little")
    transport = PlainTransport.__new__(PlainTransport)
    transport.con = Mock()
    transport.con.recv.side_effect = [length[:2], length[2:], wire[:1], wire[1:]]

    assert statement_responses_pb2.Frame.FromString(transport.recv_msg()) == response


def test_truncated_message_raises_eof():
    transport = PlainTransport.__new__(PlainTransport)
    transport.con = Mock()
    transport.con.recv.side_effect = [(3).to_bytes(8, "little"), b"x", b""]

    with pytest.raises(EOFError):
        transport.recv_msg()
