.. Polypheny-Connector-Python documentation master file, created by
   sphinx-quickstart on Wed Mar 20 16:27:44 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Polypheny Driver for Python
======================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This is the official Python Driver for Polypheny.  Unless mentioned
otherwise it follows the DBI 2.0 specification.

Getting Started
---------------

In this tutorial we learn how to:
 - install the driver using `pip`
 - connect to local and remote Polypheny instances
 - perform SQL queries using the DBI 2.0 interface
 - perform multi model queries using different languages

First you need to get Polypheny running.  If you do not have Polypheny
yet, follow the instructions here_.

.. _here: https://docs.polypheny.com/en/latest/getting_started/setup/install

.. testsetup::

   import decimal
   import sys

   import polypheny
   oldconnect = polypheny.connect
   def connect(address=None, *, username=None, password=None, transport=None, **kwargs):
       if address == None and transport == None and sys.platform == 'win32':
	   return oldconnect(('127.0.0.1', 20590), username='pa', password='', transport='plain', **kwargs)
       elif transport == 'unix' and sys.platform == 'win32':
           return None
       return oldconnect(address, username=username, password=password, transport=transport, **kwargs)
   polypheny.connect = connect
   con = polypheny.connect()
   cur = con.cursor()
   cur.execute('DROP TABLE IF EXISTS fruits')
   cur.execute('CREATE TABLE fruits(id INTEGER PRIMARY KEY, name VARCHAR(50)/*TEXT*/ NOT NULL)')
   cur.execute('INSERT INTO fruits (id, name) VALUES (1, ?)', ('Orange',))
   con.commit()
   con.close()

   oldprint = print
   def myprint(*objects, sep=' ', end='\n', file=None, flush=False):
       def toint(i):
           if isinstance(i, decimal.Decimal) and int(i) == i:
               return int(i)
           else:
               return i

       if len(objects) == 1 and isinstance(objects[0], dict):
	   oldprint('{' + ', '.join(map(lambda i: f'{repr(i[0])}: {repr(toint(i[1]))}', sorted(objects[0].items()))) + '}')
       elif len(objects) == 1 and isinstance(objects[0], list):
           oldprint('[' + ', '.join(map(repr, map(toint, objects[0]))) + ']')
       else:
	   oldprint(*objects, sep=sep, end=end, file=file, flush=flush)

   print = myprint

Installation
^^^^^^^^^^^^

Using pip::

  pip install polypheny

Then import the package in your code:

.. code-block:: python

   import polypheny

Connect to Polypheny
^^^^^^^^^^^^^^^^^^^^

There are two ways to connect to Polypheny:

 1. Locally via Unix sockets (only Linux, BSD, macOS):

    .. testcode::

       con = polypheny.connect()

    Or passing an explicit path, username and password:

    .. testcode::

       import os
       con = polypheny.connect(
	   os.path.expanduser('~/.polypheny/polypheny-prism.sock'),
	   username='pa',
	   password='',
	   transport='unix',
       )

    .. note::

       If the user running the Python script has the same username as
       a database user, the user will automatically be logged in as that
       user and username and password are ignored.

 2. Unencrypted over the network (all systems):

    .. testcode::

       con = polypheny.connect(
	   ('127.0.0.1', 20590),
	   username='pa',
	   password='',
	   transport='plain',
       )

Executing a query
^^^^^^^^^^^^^^^^^

.. testcode::

   cur = con.cursor()
   cur.execute('SELECT id, name FROM fruits')
   for row in cur:
       print(row)
   cur.close()

Output:

.. testoutput::

   [1, 'Orange']

Multimodel queries
------------------

In addition to SQL, Polypheny supports many more query languages.  To
use another language, replace the
:py:meth:`~polypheny.Cursor.execute` with
:py:meth:`~polypheny.Cursor.executeany` and add the desired
language as first argument.

So instead of SQL, we can also use e.g the Mongo Query Language:

.. testcode::

   cur = con.cursor()
   cur.executeany('mongo', 'db.fruits.find({})')
   print(cur.fetchone())

Because this query returns documents, :py:meth:`~polypheny.Cursor.fetchone`
returns a :py:class:`dict` instead of a :py:class:`list`:

.. testoutput::

   {'id': 1, 'name': 'Orange'}

The return type of :py:meth:`~polypheny.Cursor.fetchone` depends on the
query.

.. note::

   Queries returning results of type graph are not supported yet.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
