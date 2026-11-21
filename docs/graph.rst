Cypher and Graph Results
========================

Use ``cursor.executeany("cypher", query, namespace=namespace)`` against a
Polypheny server with Prism graph support and the Cypher plugin enabled.
Pass one Cypher statement per call and omit ``params``. The server supports
direct execution for Cypher. Commit writes with ``connection.commit()``.
A scalar write acknowledgement is available through ``cursor.rowcount``.

The examples match the development connector in pull request #3. Install it
with Python 3.9 or later. The package uses the released Prism 2.3 bindings.
Mixed projections require a Prism 2.3 server.

.. code-block:: bash

   python -m pip install "polypheny @ git+https://github.com/polypheny/Polypheny-Connector-Python.git@refs/pull/3/head"

Result formats
--------------

- A graph stream yields individual node and edge dictionaries. A path returned
  on its own expands into nodes and edges in traversal order. Repeated matches
  can repeat elements. ``cursor.description`` is ``None``.
- Scalar projections yield lists of values in column order. Adding a scalar
  column to a graph projection also produces lists that contain graph
  dictionaries as individual cells. Column names and aliases are available in
  ``cursor.description``, including for empty results.
- A positive ``fetch_size`` sets the size of a server frame in source rows.
  A single path can expand into multiple items in a graph stream. The count
  passed to ``fetchmany()`` measures returned items and can span frames.

Nodes have ``id``, ``name``, ``labels``, and ``properties``. The top-level
``name`` is a binding name when supplied by the server. Read a property named
``name`` from ``node["properties"]["name"]``. Edges add the endpoint IDs
``left`` and ``right``, plus the integer ``direction`` relative to those
endpoints. The values are ``0`` (UNSPECIFIED), ``1`` (LEFT_TO_RIGHT), ``2``
(RIGHT_TO_LEFT), and ``3`` (NONE).

A typed path cell has ``nodes`` and ``edges`` lists ordered by traversal.
Each edge retains its stored orientation. A typed graph cell has the same
keys and includes isolated nodes. Its lists have no ordering guarantee.
Property values use the conversions in :doc:`types`.

Read a graph and a mixed projection
-----------------------------------

The example uses the same connection environment variables as the main guide.
It creates a graph namespace, commits one path, then reads it in flat and
tabular formats.

.. testcode::

   import os
   from contextlib import closing
   from uuid import uuid4

   import polypheny

   address = (
       os.getenv("POLYPHENY_HOST", "127.0.0.1"),
       int(os.getenv("POLYPHENY_PORT", "20590")),
   )
   namespace = f"py_docs_graph_{uuid4().hex[:12]}"
   with closing(polypheny.connect(
       address,
       username=os.getenv("POLYPHENY_USER", "pa"),
       password=os.getenv("POLYPHENY_PASSWORD", ""),
       transport="plain",
   )) as connection, closing(connection.cursor()) as cursor:
       cursor.execute(f"CREATE GRAPH NAMESPACE {namespace}")
       try:
           cursor.executeany(
               "cypher",
               "CREATE (:Person {name: 'Ada'})-[:KNOWS]->(:Person {name: 'Lin'})",
               namespace=namespace,
           )
           connection.commit()

           match = "MATCH p=(a:Person)-[:KNOWS]->(b:Person)"
           cursor.executeany("cypher", f"{match} RETURN p", namespace=namespace, fetch_size=1)
           ada, edge, lin = cursor.fetchall()
           assert edge["left"] == ada["id"]
           assert edge["right"] == lin["id"]
           print(ada["properties"]["name"], edge["labels"][0], lin["properties"]["name"])

           cursor.executeany(
               "cypher", f"{match} RETURN p AS route, b.name AS destination",
               namespace=namespace, fetch_size=1,
           )
           print([column[0] for column in cursor.description])
           route, destination = cursor.fetchone()
           print([node["properties"]["name"] for node in route["nodes"]], destination)
       finally:
           connection.rollback()
           cursor.execute(f"DROP NAMESPACE {namespace}")

.. testoutput::

   Ada KNOWS Lin
   ['route', 'destination']
   ['Ada', 'Lin'] Lin

See the `official graph reference preview <https://docs-preview.polypheny.com/en/latest/drivers/python/graph-results>`_
and the `Cypher integration example <https://docs-preview.polypheny.com/en/latest/integration/python#query-a-graph-with-cypher>`_
for more projections and result shapes.
