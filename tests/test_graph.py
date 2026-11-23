# Copyright 2026 The Polypheny Project
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
from contextlib import closing
from uuid import uuid4

import polypheny
import pytest
from org.polypheny.prism import value_pb2


PEOPLE = ["Alice", "Bob", "Charlie"]
PATH = (
    "MATCH p=(:Person {name: 'Alice'})-[:KNOWS*1..3]->(:Person {name: 'Charlie'}) "
    "RETURN p"
)


@pytest.fixture
def graph():
    host = os.environ.get("POLYPHENY_PRISM_HOST", "127.0.0.1")
    port = int(os.environ.get("POLYPHENY_PRISM_PORT", "20590"))
    user = os.environ.get("POLYPHENY_PRISM_USER", "pa")
    password = os.environ.get("POLYPHENY_PRISM_PASSWORD", "")
    namespace = f"pygraph_{uuid4().hex[:12]}"
    with closing(polypheny.connect((host, port), username=user, password=password, transport="plain")) as con:
        with closing(con.cursor()) as cur:
            cur.execute(f"CREATE GRAPH NAMESPACE {namespace}")
            try:
                cur.executeany(
                    "cypher",
                    "CREATE (:Person {rank: 1, name: 'Alice'})-[:KNOWS {since: 2020}]->"
                    "(:Person {rank: 2, name: 'Bob'})-[:KNOWS {since: 2021}]->"
                    "(:Person {rank: 3, name: 'Charlie'})",
                    namespace=namespace,
                )
                con.commit()
                yield con, cur, namespace
            finally:
                cur.close()
                con.rollback()
                with closing(con.cursor()) as cleanup:
                    cleanup.execute(f"DROP NAMESPACE IF EXISTS {namespace}")


def assert_node(node, name, rank):
    assert isinstance(node["id"], str) and node["id"]
    assert isinstance(node["name"], str)
    assert node["labels"] == ["Person"]
    assert node["properties"]["name"] == name
    assert int(node["properties"]["rank"]) == rank


def assert_edge(edge, left, right, year):
    assert isinstance(edge["id"], str) and edge["id"]
    assert isinstance(edge["name"], str)
    assert edge["labels"] == ["KNOWS"]
    assert edge["left"] == left["id"]
    assert edge["right"] == right["id"]
    assert edge["direction"] == value_pb2.ProtoEdge.LEFT_TO_RIGHT
    assert int(edge["properties"]["since"]) == year


def test_pages_graph_nodes_across_fetch_methods(graph):
    _, cur, namespace = graph
    cur.executeany("cypher", "MATCH (n:Person) RETURN n ORDER BY n.rank", fetch_size=1, namespace=namespace)

    alice = cur.fetchone()
    cur.arraysize = 1
    bob, = cur.fetchmany()
    charlie, = list(cur)
    for rank, (node, name) in enumerate(zip((alice, bob, charlie), PEOPLE), 1):
        assert_node(node, name, rank)
    assert len({node["id"] for node in (alice, bob, charlie)}) == 3
    assert cur.description is None
    assert cur.rowcount == -1
    assert cur.fetchone() is None
    assert cur.fetchmany(3) == []
    assert cur.fetchall() == []


def test_graph_stream_preserves_nodes_edges_and_endpoints(graph):
    _, cur, namespace = graph
    cur.executeany(
        "cypher", "MATCH (a:Person {name: 'Alice'})-[r:KNOWS]->(b:Person) RETURN a, r, b",
        fetch_size=1, namespace=namespace,
    )
    alice, edge, bob = cur.fetchall()
    assert_node(alice, "Alice", 1)
    assert_node(bob, "Bob", 2)
    assert_edge(edge, alice, bob, 2020)


def test_path_graph_stream_follows_traversal_order(graph):
    _, cur, namespace = graph
    cur.executeany("cypher", PATH, fetch_size=1, namespace=namespace)
    alice, first_edge, bob, second_edge, charlie = cur.fetchall()
    for rank, (node, name) in enumerate(zip((alice, bob, charlie), PEOPLE), 1):
        assert_node(node, name, rank)
    assert_edge(first_edge, alice, bob, 2020)
    assert_edge(second_edge, bob, charlie, 2021)


def test_graph_scan_includes_isolated_nodes(graph):
    con, cur, namespace = graph
    cur.executeany("cypher", "CREATE (:Isolated {name: 'Solo'})", namespace=namespace)
    con.commit()

    cur.executeany("cypher", "MATCH (*) RETURN *", fetch_size=1, namespace=namespace)
    elements = cur.fetchall()
    nodes = {item["properties"]["name"]: item for item in elements if "left" not in item}
    edges = {int(item["properties"]["since"]): item for item in elements if "left" in item}
    assert len(elements) == 6
    assert set(nodes) == {*PEOPLE, "Solo"}
    assert nodes["Solo"]["labels"] == ["Isolated"]
    assert set(edges) == {2020, 2021}
    assert_edge(edges[2020], nodes["Alice"], nodes["Bob"], 2020)
    assert_edge(edges[2021], nodes["Bob"], nodes["Charlie"], 2021)


def test_empty_graph_cursor_can_be_reused(graph):
    _, cur, namespace = graph
    cur.executeany("cypher", "MATCH (n:Person {name: 'missing'}) RETURN n", fetch_size=1, namespace=namespace)
    assert cur.description is None
    assert cur.fetchone() is None
    assert list(cur) == []

    cur.executeany("cypher", "MATCH (n:Person) RETURN n.name AS name ORDER BY name", namespace=namespace)
    assert [column[0] for column in cur.description] == ["name"]
    assert cur.fetchall() == [[name] for name in PEOPLE]


def test_scalar_projections_and_early_close(graph):
    con, cur, namespace = graph
    cur.executeany("cypher", "MATCH (n:Person) RETURN n.name AS name ORDER BY name", fetch_size=1, namespace=namespace)
    assert [column[0] for column in cur.description] == ["name"]
    assert cur.fetchmany(2) == [["Alice"], ["Bob"]]
    cur.close()

    with closing(con.cursor()) as next_cursor:
        next_cursor.executeany("cypher", "MATCH (n:Person) RETURN n ORDER BY n.rank", fetch_size=1, namespace=namespace)
        assert_node(next_cursor.fetchone(), "Alice", 1)


@pytest.mark.parametrize("node_first", [True, False])
def test_pages_mixed_projections_with_aliases(graph, node_first):
    _, cur, namespace = graph
    projection = "n AS person, n.name AS name" if node_first else "n.name AS name, n AS person"
    labels = ["person", "name"] if node_first else ["name", "person"]
    cur.executeany("cypher", f"MATCH (n:Person) RETURN {projection} ORDER BY name", fetch_size=1, namespace=namespace)
    assert [column[0] for column in cur.description] == labels
    rows = cur.fetchall()
    assert len(rows) == len(PEOPLE)
    for rank, (row, expected) in enumerate(zip(rows, PEOPLE), 1):
        node, name = row if node_first else reversed(row)
        assert name == expected
        assert_node(node, expected, rank)


def test_mixed_edge_endpoints_and_scalar(graph):
    _, cur, namespace = graph
    cur.executeany(
        "cypher",
        "MATCH (a:Person {name: 'Alice'})-[r:KNOWS]->(b:Person) RETURN a, r, b, b.name AS name",
        fetch_size=1, namespace=namespace,
    )
    assert [column[0] for column in cur.description] == ["a", "r", "b", "name"]
    alice, edge, bob, name = cur.fetchone()
    assert_node(alice, "Alice", 1)
    assert_node(bob, "Bob", 2)
    assert_edge(edge, alice, bob, 2020)
    assert name == "Bob"
    assert cur.fetchone() is None


@pytest.mark.parametrize("reverse", [False, True])
def test_preserves_path_cell_and_edge_orientation(graph, reverse):
    _, cur, namespace = graph
    query = PATH
    if reverse:
        query = (
            "MATCH p=(:Person {name: 'Charlie'})<-[:KNOWS*1..3]-(:Person {name: 'Alice'}) "
            "RETURN p"
        )
    cur.executeany("cypher", query + ", 'route' AS title", fetch_size=1, namespace=namespace)
    assert [column[0] for column in cur.description] == ["p", "title"]
    path, title = cur.fetchone()
    assert title == "route"
    expected_names = PEOPLE[::-1] if reverse else PEOPLE
    assert [node["properties"]["name"] for node in path["nodes"]] == expected_names
    alice, bob, charlie = reversed(path["nodes"]) if reverse else path["nodes"]
    first_edge, second_edge = reversed(path["edges"]) if reverse else path["edges"]
    assert_edge(first_edge, alice, bob, 2020)
    assert_edge(second_edge, bob, charlie, 2021)
    assert cur.fetchone() is None


def test_preserves_null_cells_and_empty_mixed_metadata(graph):
    _, cur, namespace = graph
    cur.executeany(
        "cypher", "MATCH (n:Person) RETURN n, n.missing AS absent, n.name AS name ORDER BY name",
        fetch_size=1, namespace=namespace,
    )
    assert [column[0] for column in cur.description] == ["n", "absent", "name"]
    rows = cur.fetchall()
    assert len(rows) == len(PEOPLE)
    for rank, ((node, absent, name), expected) in enumerate(zip(rows, PEOPLE), 1):
        assert_node(node, expected, rank)
        assert absent is None
        assert name == expected

    cur.executeany(
        "cypher", "MATCH (n:Person {name: 'missing'}) RETURN n, n.name AS name",
        fetch_size=1, namespace=namespace,
    )
    assert [column[0] for column in cur.description] == ["n", "name"]
    assert cur.fetchall() == []


@pytest.mark.parametrize("commit", [False, True])
def test_graph_writes_follow_the_connection_transaction(graph, commit):
    con, cur, namespace = graph
    cur.executeany("cypher", "CREATE (:Scratch {name: 'Write'})", namespace=namespace)
    assert cur.rowcount >= 0
    assert cur.description is None
    with pytest.raises(polypheny.Error, match="did not produce any results"):
        cur.fetchall()
    if commit:
        con.commit()
    else:
        con.rollback()

    cur.executeany("cypher", "MATCH (n:Scratch) RETURN n.name AS name", namespace=namespace)
    assert cur.fetchall() == ([["Write"]] if commit else [])


def test_rejects_multiple_cypher_statements_and_recovers(graph):
    con, cur, namespace = graph
    with pytest.raises(polypheny.Error, match="exactly one Cypher statement"):
        cur.executeany(
            "cypher", "CREATE (:Scratch {name: 'Invalid'}); MATCH (n:Person) RETURN n",
            namespace=namespace,
        )
    con.rollback()
    cur.executeany("cypher", "MATCH (n:Scratch) RETURN n", namespace=namespace)
    assert cur.fetchall() == []
    cur.executeany("cypher", "MATCH (n:Person) RETURN n ORDER BY n.rank", fetch_size=1, namespace=namespace)
    assert len(cur.fetchall()) == 3


def test_reports_server_limit_on_indexed_cypher(graph):
    con, cur, namespace = graph
    with pytest.raises(polypheny.NotSupportedError, match="Indexed prepared Cypher statements are not supported") as caught:
        cur.executeany("cypher", "MATCH (n:Person) RETURN n", [], namespace=namespace)
    assert caught.value.sqlstate == "0A000"
    con.rollback()
    cur.executeany("cypher", "MATCH (n:Person) RETURN n.name AS name ORDER BY name", namespace=namespace)
    assert cur.fetchall() == [[name] for name in PEOPLE]


def test_prepared_named_cypher(graph):
    _, cur, namespace = graph
    cur.executeany(
        "cypher", "MATCH (n:Person) WHERE n.name = $name RETURN n.name AS name",
        {"name": "Alice"}, namespace=namespace,
    )
    assert cur.fetchall() == [["Alice"]]


def test_graph_namespace_metadata(graph):
    con, _, namespace = graph
    request = con.con.new_request()
    request.entities_request.namespace_name = namespace
    request.entities_request.entity_pattern = "pygraph%"
    response = con.con.call(request)
    assert response.WhichOneof("type") == "entities_response"
    entity, = response.entities_response.entities
    assert entity.HasField("graph")

    request = con.con.new_request()
    request.entities_request.namespace_name = namespace
    request.entities_request.entity_pattern = "does_not_match%"
    assert len(con.con.call(request).entities_response.entities) == 0
