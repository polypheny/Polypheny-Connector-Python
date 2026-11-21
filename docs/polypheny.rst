Python API
==========

Module
------

.. automodule:: polypheny

Connections use a ``(host, port)`` tuple for plain TCP or a socket path
string for Unix transport. An argument-free connection uses the default
Unix socket and peer authentication. Use one connection and its cursors
from the same thread. The DB-API constants are ``apilevel = "2.0"``,
``threadsafety = 0``, and ``paramstyle = "qmark"``.
The connector reserves ``**kwargs`` without consuming transport options.

.. autofunction:: polypheny.connect

Value constructors
~~~~~~~~~~~~~~~~~~

- ``Date(year, month, day)``, ``Time(hour, minute, second)``, and
  ``Timestamp(year, month, day, hour, minute, second)`` return the
  corresponding Python date and time objects. ``Timestamp()`` is naive.
- ``DateFromTicks(ticks)``, ``TimeFromTicks(ticks)``, and
  ``TimestampFromTicks(ticks)`` use whole seconds from the Unix epoch in the
  process's local timezone.
- ``Binary(string)`` encodes a string as UTF-8 bytes. You can bind existing
  bytes directly.

Connection
----------

Create connections with ``polypheny.connect()``. Cursors opened on a connection
share its transaction. Auto-commit starts disabled, and DDL commits automatically.

.. autoclass:: polypheny.Connection()

   .. automethod:: cursor
   .. automethod:: commit
   .. automethod:: rollback
   .. automethod:: close

``close()`` closes the cursors and rolls back pending work. Use
``contextlib.closing`` or ``try`` / ``finally`` to manage the connection lifetime.
Call ``commit()`` before closing to persist pending writes.

Cursor
------

Obtain a cursor from ``Connection.cursor()``. Each new execution releases the
previous result on that cursor. ``execute()`` runs SQL. ``executeany()`` takes
an explicit language and can select a default namespace for the statement.
Use ``?`` with a list or tuple of parameters, or ``:name`` with a dictionary
for named SQL parameters. Cypher execution uses the direct statement path.

.. autoclass:: polypheny.Cursor()

   .. automethod:: execute
   .. automethod:: executemany
   .. automethod:: executeany
   .. automethod:: fetchone
   .. automethod:: fetchmany
   .. automethod:: fetchall
   .. automethod:: reset
   .. automethod:: close
   .. automethod:: setinputsizes
   .. automethod:: setoutputsize

Iterate over a cursor or use ``fetchone()``, ``fetchmany()``, and
``fetchall()`` to consume results. A row is a list. A document or an item
from a flat graph stream is a dictionary. ``fetchone()`` returns ``None``
at exhaustion.

- ``arraysize`` defaults to ``1`` after each execution and supplies the
  default item count for ``fetchmany()``. ``fetch_size`` is a separate limit
  for each server frame.
- ``rowcount`` is the server's scalar result or ``-1`` when there is a
  result set or before execution.
- ``description`` is ``None`` before execution and for scalar results,
  document results, or flat graph streams. For tabular results, each column
  is described by an eight-item tuple ``(label, None, None, None, None,
  precision, scale, is_nullable)``. The extra placeholder differs from
  the seven-item DB-API tuple.

``reset()`` releases the current result and resets metadata and ``arraysize``.
``close()`` also unregisters the cursor from its connection.
``setinputsizes()`` and ``setoutputsize()`` are no-ops.

Exceptions
----------

The connector exports ``Warning`` and ``Error``. Prism server errors use
``Error``. The DB-API subclasses are ``InterfaceError`` and ``DatabaseError``.
The latter has subclasses ``DataError``, ``OperationalError``,
``IntegrityError``, ``InternalError``, ``ProgrammingError``, and
``NotSupportedError``. Closed connection operations such as
``cursor()``, ``commit()``, or ``rollback()`` raise ``ProgrammingError``.
Socket failures can surface as ``OSError`` or ``EOFError``.

See the `official Python API reference <https://docs.polypheny.com/en/latest/drivers/python/api/polypheny>`_
and `error handling guide <https://docs.polypheny.com/en/latest/drivers/python/error-handling>`_.
