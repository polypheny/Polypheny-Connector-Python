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

from test_helper import con


def test_nodes_match_and_order_by(con):
    cur = con.cursor()
    cur.execute("DROP NAMESPACE IF EXISTS cyphertest")
    cur.execute("CREATE GRAPH NAMESPACE cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 1, name: 'Alice'})", namespace="cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 2, name: 'Bob'})", namespace="cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 3, name: 'Charlie'})", namespace="cyphertest")
    con.commit()
    cur.executeany("cypher", 'MATCH (n:Person) RETURN n ORDER BY n.id', namespace="cyphertest")
    result = cur.fetchall()

    expected = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie'}
    ]
    assert (sorted(result, key=lambda x: x['id']), expected)
    cur.close()
    con.close()


def test_nodes(con):
    cur = con.cursor()
    cur.execute("DROP NAMESPACE IF EXISTS cyphertest")
    cur.execute("CREATE GRAPH NAMESPACE cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 1, name: 'Alice'})", namespace="cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 2, name: 'Bob'})", namespace="cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 3, name: 'Charlie'})", namespace="cyphertest")
    cur.executeany("cypher", "MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'}) CREATE (a)-[:KNOWS]->(b)",
                   namespace="cyphertest")
    cur.executeany("cypher", "MATCH (b:Person {name: 'Bob'}), (c:Person {name: 'Charlie'}) CREATE (b)-[:KNOWS]->(c)",
                   namespace="cyphertest")
    con.commit()
    cur.executeany("cypher", 'MATCH ()-[r:KNOWS]->() RETURN r', namespace="cyphertest")
    result = cur.fetchall()

    expected = [
        {'type': 'KNOWS'},
        {'type': 'KNOWS'}
    ]
    assert (sorted(result, key=lambda x: x['id']), expected)
    cur.close()
    con.close()


def test_nodes_relational(con):
    cur = con.cursor()
    cur.execute("DROP NAMESPACE IF EXISTS cyphertest")
    cur.execute("CREATE GRAPH NAMESPACE cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 1, name: 'Alice'})", namespace="cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 2, name: 'Bob'})", namespace="cyphertest")
    cur.executeany("cypher", "CREATE (:Person {id: 3, name: 'Charlie'})", namespace="cyphertest")
    con.commit()
    cur.executeany("cypher", "MATCH (n:Person {name: 'Alice'}) RETURN n.name, n.id", namespace="cyphertest")
    result = cur.fetchall()

    assert len(result) == 1
    row = result[0]
    assert row[0] == "Alice"
    assert row[1] == "1"
