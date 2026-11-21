Polypheny Python Driver
=======================

The Polypheny Python connector implements the connection and cursor conventions
of Python DB-API 2.0 and uses the Prism query interface. See the official
Python driver overview and integration guide for additional examples.

- `Python driver overview <https://docs.polypheny.com/en/latest/drivers/python/overview>`_
- `Python integration guide <https://docs.polypheny.com/en/latest/integration/python>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents

   polypheny
   types
   interval
   graph

Install
-------

Use Python 3.9 or later. Install the connector from PyPI in a virtual
environment.

.. code-block:: bash

   python -m pip install polypheny

The Cypher examples require a connector with Prism 2.3 graph support.
See :doc:`graph` for installation from source and the server requirements.

Enable the Prism query interface on the server. The connector uses the server's
compatibility response during the Prism handshake. Mixed graph and scalar
projections require Prism 2.3. Prism 1.x servers require a 1.x Prism client.
`Prism query interface <https://docs.polypheny.com/en/latest/query_interfaces/prism/overview>`_

Connect
-------

Configure the connection in your environment or use the defaults below for
a local plain TCP listener. Use a trusted network or a secure tunnel for the
unencrypted plain transport.

.. testcode::

   import os

   import polypheny

   def connect():
       address = (
           os.getenv("POLYPHENY_HOST", "127.0.0.1"),
           int(os.getenv("POLYPHENY_PORT", "20590")),
       )
       return polypheny.connect(
           address,
           username=os.getenv("POLYPHENY_USER", "pa"),
           password=os.getenv("POLYPHENY_PASSWORD", ""),
           transport="plain",
       )

On a system with Unix domain sockets, ``polypheny.connect()`` uses the default
listener at ``~/.polypheny/polypheny-prism.sock`` and peer authentication.
When supplying explicit connection settings, pass both the socket path and
``transport="unix"``. Supply a password when passing a username, including
an empty password if that is the server configuration. See :doc:`polypheny`.

.. testcode:: unix
   :skipif: __import__("sys").platform == "win32"

   from contextlib import closing
   from pathlib import Path

   import polypheny

   socket_path = Path.home() / ".polypheny" / "polypheny-prism.sock"
   with closing(polypheny.connect(str(socket_path), transport="unix")) as connection:
       with closing(connection.cursor()) as cursor:
           cursor.execute("SELECT 1")
           print(cursor.fetchone())

.. testoutput:: unix
   :skipif: __import__("sys").platform == "win32"

   [1]

Query with SQL and MongoQL
--------------------------

The example uses the ``connect()`` helper above. It creates a table, inserts two
rows with positional parameters, rolls back a third insert, and reads the
remaining rows. The last query uses MongoQL to read the same table as documents.
For named SQL parameters, use ``:name`` placeholders and pass a dictionary.

.. testcode::

   from contextlib import closing
   from uuid import uuid4

   table = f"py_docs_{uuid4().hex[:12]}"
   with closing(connect()) as connection, closing(connection.cursor()) as cursor:
       cursor.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, name VARCHAR(80))")
       try:
           cursor.executemany(
               f"INSERT INTO {table} VALUES (?, ?)", [(1, "Ada"), (2, "Grace")]
           )
           connection.commit()

           cursor.execute(f"INSERT INTO {table} VALUES (?, ?)", (3, "Lin"))
           connection.rollback()

           cursor.execute(f"SELECT id, name FROM {table} WHERE id >= ? ORDER BY id", (1,))
           print(cursor.fetchall())

           cursor.executeany("mongo", f'db.{table}.find({{"id": 1}})')
           print(cursor.fetchone()["name"])
       finally:
           connection.rollback()
           cursor.execute(f"DROP TABLE {table}")

.. testoutput::

   [[1, 'Ada'], [2, 'Grace']]
   Ada

Auto-commit starts disabled. Polypheny commits DDL such as ``CREATE TABLE``
and ``DROP TABLE`` automatically, so end pending writes before issuing DDL.
Closing a connection rolls back pending work. Use bound parameters for values
and trusted names for identifiers.

Use ``executeany("mongo", ..., namespace=...)`` to choose a document namespace.
Document collection metadata requires server support introduced in Prism 2.2.
The official guide shows how to request it through the lower-level Prism API.
`Document collection metadata <https://docs.polypheny.com/en/latest/drivers/python/document-metadata>`_

The error handling guide shows how to roll back after a failed statement and
reuse the connection. The :doc:`graph` guide demonstrates Cypher against a
graph namespace.
`Error handling guide <https://docs.polypheny.com/en/latest/drivers/python/error-handling>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
