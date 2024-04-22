# https://peps.python.org/pep-0249/

import polypheny
import pytest

from test_helper import con, cur, cur_with_data

# PEP: 249
# Title: Python Database API Specification v2.0
# Author: Marc-André Lemburg <mal@lemburg.com>
# Discussions-To: db-sig@python.org
# Status: Final
# Type: Informational
# Content-Type: text/x-rst
# Created: 12-Apr-1999
# Post-History:
# Replaces: 248
# 
# 
# Introduction
# ============
# 
# This API has been defined to encourage similarity between the Python
# modules that are used to access databases.  By doing this, we hope to
# achieve a consistency leading to more easily understood modules, code
# that is generally more portable across databases, and a broader reach
# of database connectivity from Python.
# 
# Comments and questions about this specification may be directed to the
# `SIG for Database Interfacing with Python <db-sig@python.org>`__.
# 
# For more information on database interfacing with Python and available
# packages see the `Database Topic Guide
# <http://www.python.org/topics/database/>`__.
# 
# This document describes the Python Database API Specification 2.0 and
# a set of common optional extensions.  The previous version 1.0 version
# is still available as reference, in :PEP:`248`. Package writers are
# encouraged to use this version of the specification as basis for new
# interfaces.
# 
# 
# Module Interface
# =================
# 
# Constructors
# ------------
# 
# Access to the database is made available through connection
# objects. The module must provide the following constructor for these:
# 
# .. _connect:
# 
# `connect`_\ ( *parameters...* )
#     Constructor for creating a connection to the database.
# 
#     Returns a Connection_ Object. It takes a number of parameters
#     which are database dependent. [1]_
def test_connection():
    con = polypheny.connect()
    assert type(con) == polypheny.Connection
    con.close()
# 
# 
# Globals
# -------
# 
# These module globals must be defined:
# 
# .. _apilevel:
# 
# `apilevel`_
#     String constant stating the supported DB API level.
# 
#     Currently only the strings "``1.0``" and "``2.0``" are allowed.
#     If not given, a DB-API 1.0 level interface should be assumed.
def test_apilevel():
    assert polypheny.apilevel == '2.0'
# 
# 
# .. _threadsafety:
# 
# `threadsafety`_
#     Integer constant stating the level of thread safety the interface
#     supports.  Possible values are:
# 
#     ============ =======================================================
#     threadsafety Meaning
#     ============ =======================================================
#                0 Threads may not share the module.
#                1 Threads may share the module, but not connections.
#                2 Threads may share the module and connections.
#                3 Threads may share the module, connections and cursors.
#     ============ =======================================================
# 
#     Sharing in the above context means that two threads may use a
#     resource without wrapping it using a mutex semaphore to implement
#     resource locking.  Note that you cannot always make external
#     resources thread safe by managing access using a mutex: the
#     resource may rely on global variables or other external sources
#     that are beyond your control.
def test_threadsafety():
    assert polypheny.threadsafety == 0
# 
# 
# .. _paramstyle:
# 
# `paramstyle`_
#     String constant stating the type of parameter marker formatting
#     expected by the interface. Possible values are [2]_:
# 
#     ============ ==============================================================
#     paramstyle   Meaning
#     ============ ==============================================================
#     ``qmark``    Question mark style, e.g. ``...WHERE name=?``
#     ``numeric``  Numeric, positional style, e.g. ``...WHERE name=:1``
#     ``named``    Named style, e.g. ``...WHERE name=:name``
#     ``format``   ANSI C printf format codes, e.g. ``...WHERE name=%s``
#     ``pyformat`` Python extended format codes, e.g.  ``...WHERE name=%(name)s``
#     ============ ==============================================================
def test_paramstyle():
    assert polypheny.paramstyle == 'qmark'
# 
# 
# Exceptions
# ----------
# 
# The module should make all error information available through these
# exceptions or subclasses thereof:
# 
# .. _Warning:
# 
# `Warning`_
#     Exception raised for important warnings like data truncations
#     while inserting, etc. It must be a subclass of the Python
#     ``Exception`` class [10]_ [11]_.
def test_warning():
    assert Exception in polypheny.Warning.__bases__
# 
# 
# .. _Error:
# 
# `Error`_
#     Exception that is the base class of all other error
#     exceptions. You can use this to catch all errors with one single
#     ``except`` statement. Warnings are not considered errors and thus
#     should not use this class as base. It must be a subclass of the
#     Python ``Exception`` class [10]_.
def test_error():
    assert Exception in polypheny.Error.__bases__
# 
# 
# .. _InterfaceError:
# 
# `InterfaceError`_
#     Exception raised for errors that are related to the database
#     interface rather than the database itself.  It must be a subclass
#     of Error_.
def test_interfaceerror():
    assert polypheny.Error in polypheny.InterfaceError.__bases__
# 
# 
# .. _DatabaseError:
# 
# `DatabaseError`_
#     Exception raised for errors that are related to the database.  It
#     must be a subclass of Error_.
def test_databaseerror():
    assert polypheny.Error in polypheny.DatabaseError.__bases__
# 
# 
# .. _DataError:
# 
# `DataError`_
#     Exception raised for errors that are due to problems with the
#     processed data like division by zero, numeric value out of range,
#     etc. It must be a subclass of DatabaseError_.
def test_dataerror():
    assert polypheny.DatabaseError in polypheny.DataError.__bases__
# 
# 
# .. _OperationalError:
# 
# `OperationalError`_
#     Exception raised for errors that are related to the database's
#     operation and not necessarily under the control of the programmer,
#     e.g. an unexpected disconnect occurs, the data source name is not
#     found, a transaction could not be processed, a memory allocation
#     error occurred during processing, etc.  It must be a subclass of
#     DatabaseError_.
def test_operationalerror():
    assert polypheny.DatabaseError in polypheny.OperationalError.__bases__
# 
# 
# .. _IntegrityError:
# 
# `IntegrityError`_
#     Exception raised when the relational integrity of the database is
#     affected, e.g. a foreign key check fails.  It must be a subclass
#     of DatabaseError_.
def test_integrityerror():
    assert polypheny.DatabaseError in polypheny.IntegrityError.__bases__
# 
# 
# .. _InternalError:
# 
# `InternalError`_
#     Exception raised when the database encounters an internal error,
#     e.g. the cursor is not valid anymore, the transaction is out of
#     sync, etc.  It must be a subclass of DatabaseError_.
def test_internalerror():
    assert polypheny.DatabaseError in polypheny.InternalError.__bases__
# 
# 
# .. _ProgrammingError:
# 
# `ProgrammingError`_
#     Exception raised for programming errors, e.g. table not found or
#     already exists, syntax error in the SQL statement, wrong number of
#     parameters specified, etc.  It must be a subclass of
#     DatabaseError_.
def test_programmingerror():
    assert polypheny.DatabaseError in polypheny.ProgrammingError.__bases__
# 
# 
# .. _NotSupportedError:
# 
# `NotSupportedError`_
#     Exception raised in case a method or database API was used which
#     is not supported by the database, e.g. requesting a
#     `.rollback()`_ on a connection that does not support transaction
#     or has transactions turned off.  It must be a subclass of
#     DatabaseError_.
def test_notsupportederror():
    assert polypheny.DatabaseError in polypheny.NotSupportedError.__bases__
# 
# This is the exception inheritance layout [10]_ [11]_:
# 
# .. code-block:: text
# 
#     Exception
#     |__Warning
#     |__Error
#        |__InterfaceError
#        |__DatabaseError
#           |__DataError
#           |__OperationalError
#           |__IntegrityError
#           |__InternalError
#           |__ProgrammingError
#           |__NotSupportedError
# 
# .. Note::
#     The values of these exceptions are not defined. They should give the user
#     a fairly good idea of what went wrong, though.
# 
# 
# .. _Connection:
# 
# Connection Objects
# ==================
# 
# Connection objects should respond to the following methods.
# 
# 
# Connection methods
# ------------------
# 
# .. .close():
# .. _Connection.close:
# 
# `.close() <#Connection.close>`_
#     Close the connection now (rather than whenever ``.__del__()`` is
#     called).
# 
#     The connection will be unusable from this point forward; an Error_
#     (or subclass) exception will be raised if any operation is
#     attempted with the connection. The same applies to all cursor
#     objects trying to use the connection.  Note that closing a
#     connection without committing the changes first will cause an
#     implicit rollback to be performed.
def test_con_close(con):
    con.close()
    err = None
    try:
        con.rollback()
    except polypheny.Error as e:
        err = e

    assert err is not None

# 
# 
# .. _.commit:
# .. _.commit():
# 
# `.commit`_\ ()
#     Commit any pending transaction to the database.
# 
#     Note that if the database supports an auto-commit feature, this must be
#     initially off. An interface method may be provided to turn it back on.
# 
#     Database modules that do not support transactions should implement this
#     method with void functionality.
def test_con_commit(con):
    con.commit()
# 
# 
# .. _.rollback:
# .. _.rollback():
# 
# `.rollback`_\ ()
#     This method is optional since not all databases provide transaction
#     support. [3]_
# 
#     In case a database does provide transactions this method causes the
#     database to roll back to the start of any pending transaction.  Closing a
#     connection without committing the changes first will cause an implicit
#     rollback to be performed.
def test_con_rollback(con):
    import sys
    if sys.platform == 'win32':
        pytest.skip()
    con.rollback()
# 
# 
# .. _.cursor:
# 
# `.cursor`_\ ()
#     Return a new Cursor_ Object using the connection.
# 
#     If the database does not provide a direct cursor concept, the module will
#     have to emulate cursors using other means to the extent needed by this
#     specification.  [4]_
def test_cursor(con):
    import sys
    if sys.platform == 'win32':
        pytest.skip()
    cur = con.cursor()
    assert type(cur) == polypheny.Cursor
    cur.close()

# 
# 
# 
# .. _Cursor:
# 
# Cursor Objects
# ==============
# 
# These objects represent a database cursor, which is used to manage the
# context of a fetch operation. Cursors created from the same connection
# are not isolated, *i.e.*, any changes done to the database by a cursor
# are immediately visible by the other cursors.  Cursors created from
# different connections can or can not be isolated, depending on how the
# transaction support is implemented (see also the connection's
# `.rollback`_\ () and `.commit`_\ () methods).
# 
# Cursor Objects should respond to the following methods and attributes.
# 
# 
# Cursor attributes
# -----------------
# 
# .. _.description:
# 
# `.description`_
#     This read-only attribute is a sequence of 7-item sequences.
# 
#     Each of these sequences contains information describing one result
#     column:
# 
#     * ``name``
#     * ``type_code``
#     * ``display_size``
#     * ``internal_size``
#     * ``precision``
#     * ``scale``
#     * ``null_ok``
# 
#     The first two items (``name`` and ``type_code``) are mandatory,
#     the other five are optional and are set to ``None`` if no
#     meaningful values can be provided.
# 
#     This attribute will be ``None`` for operations that do not return
#     rows or if the cursor has not had an operation invoked via the
#     `.execute*()`_ method yet.
# 
#     The ``type_code`` can be interpreted by comparing it to the `Type
#     Objects`_ specified in the section below.
def test_description(cur):
    assert cur.description is None
# 
# 
# .. _.rowcount:
# 
# `.rowcount`_
#     This read-only attribute specifies the number of rows that the last
#     `.execute*()`_ produced (for DQL statements like ``SELECT``) or affected
#     (for DML statements like ``UPDATE`` or ``INSERT``). [9]_
# 
#     The attribute is -1 in case no `.execute*()`_ has been performed
#     on the cursor or the rowcount of the last operation is cannot be
#     determined by the interface. [7]_
# 
#     .. note::
#         Future versions of the DB API specification could redefine the
#         latter case to have the object return ``None`` instead of -1.
def test_rowcount(cur):
    assert cur.rowcount == -1

# 
# 
# Cursor methods
# --------------
# 
# .. _.callproc:
# .. _.callproc():
# 
# `.callproc`_\ ( *procname* [, *parameters* ] )
#     (This method is optional since not all databases provide stored
#     procedures. [3]_)
# 
#     Call a stored database procedure with the given name. The sequence
#     of parameters must contain one entry for each argument that the
#     procedure expects. The result of the call is returned as modified
#     copy of the input sequence. Input parameters are left untouched,
#     output and input/output parameters replaced with possibly new
#     values.
# 
#     The procedure may also provide a result set as output. This must
#     then be made available through the standard `.fetch*()`_ methods.
# 
# 
# .. .close:
# .. _Cursor.close:
# .. _Cursor.close():
# 
# `.close <#Cursor.close>`_\ ()
#     Close the cursor now (rather than whenever ``__del__`` is called).
# 
#     The cursor will be unusable from this point forward; an Error_ (or
#     subclass) exception will be raised if any operation is attempted
#     with the cursor.
def test_cursor_close(cur):
    cur.close()
    err = None
    try:
        cur.execute('SELECT 1')
    except polypheny.Error as e:
        err = e
    assert err is not None

# 
# 
# .. _.execute*:
# .. _.execute*():
# 
# .. _.execute:
# .. _.execute():
# 
# `.execute`_\ (*operation* [, *parameters*])
#     Prepare and execute a database operation (query or command).
# 
#     Parameters may be provided as sequence or mapping and will be
#     bound to variables in the operation.  Variables are specified in a
#     database-specific notation (see the module's paramstyle_ attribute
#     for details). [5]_
def test_cursor_execute(cur_with_data):
    pytest.skip('dict example does not work')
    cur = cur_with_data
    cur.execute('SELECT * FROM customers')
    cur.execute('SELECT * FROM customers WHERE year_joined > ?', (2007,))
    cur.execute('SELECT * FROM customers WHERE year_joined > :year',
                {'year': 2007})

# 
#     A reference to the operation will be retained by the cursor.  If
#     the same operation object is passed in again, then the cursor can
#     optimize its behavior.  This is most effective for algorithms
#     where the same operation is used, but different parameters are
#     bound to it (many times).
# 
#     For maximum efficiency when reusing an operation, it is best to
#     use the `.setinputsizes()`_ method to specify the parameter types
#     and sizes ahead of time.  It is legal for a parameter to not match
#     the predefined information; the implementation should compensate,
#     possibly with a loss of efficiency.
# 
#     The parameters may also be specified as list of tuples to
#     e.g. insert multiple rows in a single operation, but this kind of
#     usage is deprecated: `.executemany()`_ should be used instead.
# 
#     Return values are not defined.
# 
# 
# .. _.executemany:
# .. _.executemany():
# 
# `.executemany`_\ ( *operation*, *seq_of_parameters* )
#     Prepare a database operation (query or command) and then execute it
#     against all parameter sequences or mappings found in the sequence
#     *seq_of_parameters*.
# 
#     Modules are free to implement this method using multiple calls to
#     the `.execute()`_ method or by using array operations to have the
#     database process the sequence as a whole in one call.
# 
#     Use of this method for an operation which produces one or more
#     result sets constitutes undefined behavior, and the implementation
#     is permitted (but not required) to raise an exception when it
#     detects that a result set has been created by an invocation of the
#     operation.
# 
#     The same comments as for `.execute()`_ also apply accordingly to
#     this method.
# 
#     Return values are not defined.
def test_cursor_executemany(cur_with_data):
    cur = cur_with_data
    cur.executemany('INSERT INTO customers(id, name, year_joined) VALUES (?, ?, ?)',
                    [(8, 'Ruth', 2012,), (9, 'Claudia', 2016,)])

# 
# 
# .. _.fetch*:
# .. _.fetch*():
# 
# .. _.fetchone:
# .. _.fetchone():
# 
# `.fetchone`_\ ()
#     Fetch the next row of a query result set, returning a single
#     sequence, or ``None`` when no more data is available. [6]_
# 
#     An Error_ (or subclass) exception is raised if the previous call
#     to `.execute*()`_ did not produce any result set or no call was
#     issued yet.
def test_cursor_fetchone(cur_with_data):
    cur = cur_with_data
    err = None
    try:
        cur.fetchone()
    except polypheny.Error as e:
        err = e
    assert err is not None
    cur.execute('SELECT * FROM customers')
    for row in cur:
        _ = row
    cur.execute('SELECT * FROM customers WHERE year_joined = 2000')
    assert cur.fetchone() is None

    cur.execute('DELETE FROM customers WHERE year_joined = 2010')
    assert cur.rowcount == 1
    with pytest.raises(polypheny.Error):
        cur.fetchone()

# 
# 
# .. _.fetchmany:
# .. _.fetchmany():
# 
# `.fetchmany`_\ ([*size=cursor.arraysize*])
#     Fetch the next set of rows of a query result, returning a sequence
#     of sequences (e.g. a list of tuples). An empty sequence is
#     returned when no more rows are available.
# 
#     The number of rows to fetch per call is specified by the
#     parameter.  If it is not given, the cursor's arraysize determines
#     the number of rows to be fetched. The method should try to fetch
#     as many rows as indicated by the size parameter. If this is not
#     possible due to the specified number of rows not being available,
#     fewer rows may be returned.
# 
#     An Error_ (or subclass) exception is raised if the previous call
#     to `.execute*()`_ did not produce any result set or no call was
#     issued yet.
# 
#     Note there are performance considerations involved with the *size*
#     parameter.  For optimal performance, it is usually best to use the
#     `.arraysize`_ attribute.  If the size parameter is used, then it
#     is best for it to retain the same value from one `.fetchmany()`_
#     call to the next.
def test_cursor_fetchmany(cur_with_data):
    cur = cur_with_data
    with pytest.raises(polypheny.Error):
        cur.fetchmany()

    # customers has seven entries
    cur.execute('SELECT * FROM customers')
    cur.arraysize = 1
    assert len(cur.fetchmany(2)) == 2
    assert len(cur.fetchmany()) == 1
    cur.arraysize = 2
    assert len(cur.fetchmany()) == 2
    assert len(cur.fetchmany(100)) == 2

    cur.execute('SELECT * FROM customers WHERE year_joined = 2000')
    assert len(cur.fetchmany()) == 0

    cur.execute('DELETE FROM customers WHERE year_joined = 2010')
    assert cur.rowcount == 1
    with pytest.raises(polypheny.Error):
        cur.fetchmany()

# 
# 
# .. _.fetchall:
# .. _.fetchall():
# 
# `.fetchall`_\ ()
#     Fetch all (remaining) rows of a query result, returning them as a
#     sequence of sequences (e.g. a list of tuples).  Note that the
#     cursor's arraysize attribute can affect the performance of this
#     operation.
# 
#     An Error_ (or subclass) exception is raised if the previous call
#     to `.execute*()`_ did not produce any result set or no call was
#     issued yet.
def test_cursor_fetchall(cur_with_data):
    cur = cur_with_data
    with pytest.raises(polypheny.Error):
        cur.fetchall()

    cur.execute('SELECT * FROM customers')
    cur.fetchall()
    assert cur.fetchone() is None

    cur.execute('SELECT * FROM customers WHERE year_joined = 2000')
    assert len(cur.fetchall()) == 0

# 
# 
# .. _.nextset:
# .. _.nextset():
# 
# `.nextset`_\ ()
#     (This method is optional since not all databases support multiple
#     result sets. [3]_)
# 
#     This method will make the cursor skip to the next available set,
#     discarding any remaining rows from the current set.
# 
#     If there are no more sets, the method returns ``None``. Otherwise,
#     it returns a true value and subsequent calls to the `.fetch*()`_
#     methods will return rows from the next result set.
# 
#     An Error_ (or subclass) exception is raised if the previous call
#     to `.execute*()`_ did not produce any result set or no call was
#     issued yet.
# 
# 
# .. _.arraysize:
# 
# `.arraysize`_
#     This read/write attribute specifies the number of rows to fetch at
#     a time with `.fetchmany()`_. It defaults to 1 meaning to fetch a
#     single row at a time.
# 
#     Implementations must observe this value with respect to the
#     `.fetchmany()`_ method, but are free to interact with the database
#     a single row at a time. It may also be used in the implementation
#     of `.executemany()`_.
def test_cursor_arraysize(cur):
    assert cur.arraysize == 1
# 
# 
# .. _.setinputsizes:
# .. _.setinputsizes():
# 
# `.setinputsizes`_\ (*sizes*)
#     This can be used before a call to `.execute*()`_ to predefine
#     memory areas for the operation's parameters.
# 
#     *sizes* is specified as a sequence — one item for each input
#     parameter.  The item should be a Type Object that corresponds to
#     the input that will be used, or it should be an integer specifying
#     the maximum length of a string parameter.  If the item is
#     ``None``, then no predefined memory area will be reserved for that
#     column (this is useful to avoid predefined areas for large
#     inputs).
# 
#     This method would be used before the `.execute*()`_ method is
#     invoked.
# 
#     Implementations are free to have this method do nothing and users
#     are free to not use it.
def test_setinputsizes(cur):
    cur.setinputsizes([])
# 
# 
# .. _.setoutputsize:
# .. _.setoutputsize():
# 
# `.setoutputsize`_\ (*size* [, *column*])
#     Set a column buffer size for fetches of large columns
#     (e.g. ``LONG``\s, ``BLOB``\s, etc.).  The column is specified as
#     an index into the result sequence.  Not specifying the column will
#     set the default size for all large columns in the cursor.
# 
#     This method would be used before the `.execute*()`_ method is
#     invoked.
# 
#     Implementations are free to have this method do nothing and users
#     are free to not use it.
def test_setoutputsize(cur):
    cur.setoutputsize([])
    cur.setoutputsize([], [])
# 
# 
# .. _Type Objects:
# 
# Type Objects and Constructors
# =============================
# 
# Many databases need to have the input in a particular format for
# binding to an operation's input parameters.  For example, if an input
# is destined for a ``DATE`` column, then it must be bound to the
# database in a particular string format.  Similar problems exist for
# "Row ID" columns or large binary items (e.g. blobs or ``RAW``
# columns).  This presents problems for Python since the parameters to
# the `.execute*()`_ method are untyped.  When the database module sees
# a Python string object, it doesn't know if it should be bound as a
# simple ``CHAR`` column, as a raw ``BINARY`` item, or as a ``DATE``.
# 
# To overcome this problem, a module must provide the constructors
# defined below to create objects that can hold special values.  When
# passed to the cursor methods, the module can then detect the proper
# type of the input parameter and bind it accordingly.
# 
# A Cursor_ Object's description attribute returns information about
# each of the result columns of a query.  The ``type_code`` must compare
# equal to one of Type Objects defined below. Type Objects may be equal
# to more than one type code (e.g. ``DATETIME`` could be equal to the
# type codes for date, time and timestamp columns; see the
# `Implementation Hints`_ below for details).
# 
# The module exports the following constructors and singletons:
# 
# .. _Date:
# 
# `Date`_\ (*year*, *month*, *day*)
#     This function constructs an object holding a date value.
def test_date():
    polypheny.Date(2023, 12, 12)
# 
# 
# .. _Time:
# 
# `Time`_\ (*hour*, *minute*, *second*)
#     This function constructs an object holding a time value.
def test_time():
    polypheny.Time(16, 49, 14)
# 
# 
# .. _Timestamp:
# 
# `Timestamp`_\ (*year*, *month*, *day*, *hour*, *minute*, *second*)
#     This function constructs an object holding a time stamp value.
def test_timestamp():
    polypheny.Timestamp(2023, 12, 12, 16, 49, 14)
# 
# 
# .. _DateFromTicks:
# 
# `DateFromTicks`_\ (*ticks*)
#     This function constructs an object holding a date value from the
#     given ticks value (number of seconds since the epoch; see the
#     documentation of `the standard Python time module
#     <http://docs.python.org/library/time.html>`__ for details).
def test_datefromticks():
    polypheny.DateFromTicks(42)
# 
# .. _TimeFromTicks:
# 
# `TimeFromTicks`_\ (*ticks*)
#     This function constructs an object holding a time value from the
#     given ticks value (number of seconds since the epoch; see the
#     documentation of the standard Python time module for details).
def test_timefromticks():
    polypheny.TimeFromTicks(42)
# 
# 
# .. _TimeStampFromTicks:
# 
# `TimestampFromTicks`_\ (*ticks*)
#     This function constructs an object holding a time stamp value from
#     the given ticks value (number of seconds since the epoch; see the
#     documentation of the standard Python time module for details).
def test_timestampfromticks():
    polypheny.TimestampFromTicks(42)
# 
# 
# .. _Binary:
# 
# `Binary`_\ (*string*)
#     This function constructs an object capable of holding a binary
#     (long) string value.
def test_binary():
    polypheny.Binary("Hello World")
# 
# 
# .. _STRING:
# 
# `STRING`_ type
#     This type object is used to describe columns in a database that
#     are string-based (e.g. ``CHAR``).
# 
# 
# .. _Binary type:
# 
# `BINARY`_ type
#     This type object is used to describe (long) binary columns in a
#     database (e.g. ``LONG``, ``RAW``, ``BLOB``\s).
# 
# 
# .. _NUMBER:
# 
# `NUMBER`_ type
#     This type object is used to describe numeric columns in a
#     database.
# 
# 
# .. _DATETIME:
# 
# `DATETIME`_ type
#     This type object is used to describe date/time columns in a
#     database.
# 
# .. _ROWID:
# 
# `ROWID`_ type
#     This type object is used to describe the "Row ID" column in a
#     database.
# 
# 
# SQL ``NULL`` values are represented by the Python ``None`` singleton
# on input and output.
# 
# .. Note::
#     Usage of Unix ticks for database interfacing can cause troubles
#     because of the limited date range they cover.
# 
# 
# 
# .. _Implementation Hints:
# 
# Implementation Hints for Module Authors
# =======================================
# 
# * Date/time objects can be implemented as `Python datetime module
#   <http://docs.python.org/library/datetime.html>`__ objects (available
#   since Python 2.3, with a C API since 2.4) or using the `mxDateTime
#   <http://www.egenix.com/products/python/mxBase/mxDateTime/>`_ package
#   (available for all Python versions since 1.5.2). They both provide
#   all necessary constructors and methods at Python and C level.
# 
# * Here is a sample implementation of the Unix ticks based constructors
#   for date/time delegating work to the generic constructors::
# 
#         import time
# 
#         def DateFromTicks(ticks):
#             return Date(*time.localtime(ticks)[:3])
# 
#         def TimeFromTicks(ticks):
#             return Time(*time.localtime(ticks)[3:6])
# 
#         def TimestampFromTicks(ticks):
#             return Timestamp(*time.localtime(ticks)[:6])
# 
# * The preferred object type for Binary objects are the buffer types
#   available in standard Python starting with version 1.5.2.  Please
#   see the Python documentation for details. For information about the
#   C interface have a look at ``Include/bufferobject.h`` and
#   ``Objects/bufferobject.c`` in the Python source distribution.
# 
# * This Python class allows implementing the above type objects even
#   though the description type code field yields multiple values for on
#   type object::
# 
#         class DBAPITypeObject:
#             def __init__(self,*values):
#                 self.values = values
#             def __cmp__(self,other):
#                 if other in self.values:
#                     return 0
#                 if other < self.values:
#                     return 1
#                 else:
#                     return -1
# 
#   The resulting type object compares equal to all values passed to the
#   constructor.
# 
# * Here is a snippet of Python code that implements the exception
#   hierarchy defined above [10]_::
# 
#         class Error(Exception):
#             pass
# 
#         class Warning(Exception):
#             pass
# 
#         class InterfaceError(Error):
#             pass
# 
#         class DatabaseError(Error):
#             pass
# 
#         class InternalError(DatabaseError):
#             pass
# 
#         class OperationalError(DatabaseError):
#             pass
# 
#         class ProgrammingError(DatabaseError):
#             pass
# 
#         class IntegrityError(DatabaseError):
#             pass
# 
#         class DataError(DatabaseError):
#             pass
# 
#         class NotSupportedError(DatabaseError):
#             pass
# 
#   In C you can use the ``PyErr_NewException(fullname, base, NULL)``
#   API to create the exception objects.
# 
# 
# Optional DB API Extensions
# ==========================
# 
# During the lifetime of DB API 2.0, module authors have often extended
# their implementations beyond what is required by this DB API
# specification. To enhance compatibility and to provide a clean upgrade
# path to possible future versions of the specification, this section
# defines a set of common extensions to the core DB API 2.0
# specification.
# 
# As with all DB API optional features, the database module authors are
# free to not implement these additional attributes and methods (using
# them will then result in an ``AttributeError``) or to raise a
# NotSupportedError_ in case the availability can only be checked at
# run-time.
# 
# It has been proposed to make usage of these extensions optionally
# visible to the programmer by issuing Python warnings through the
# Python warning framework. To make this feature useful, the warning
# messages must be standardized in order to be able to mask them. These
# standard messages are referred to below as *Warning Message*.
# 
# 
# .. _.rownumber:
# 
# Cursor\ `.rownumber`_
#     This read-only attribute should provide the current 0-based index
#     of the cursor in the result set or ``None`` if the index cannot be
#     determined.
# 
#     The index can be seen as index of the cursor in a sequence (the
#     result set). The next fetch operation will fetch the row indexed
#     by `.rownumber`_ in that sequence.
# 
#     *Warning Message:* "DB-API extension cursor.rownumber used"
# 
# 
# .. _Connection.Error:
# .. _Connection.ProgrammingError:
# 
# `Connection.Error`_, `Connection.ProgrammingError`_, etc.
#     All exception classes defined by the DB API standard should be
#     exposed on the Connection_ objects as attributes (in addition to
#     being available at module scope).
# 
#     These attributes simplify error handling in multi-connection
#     environments.
# 
#     *Warning Message:* "DB-API extension connection.<exception> used"
# 
# 
# .. _.connection:
# 
# Cursor\ `.connection`_
#     This read-only attribute return a reference to the Connection_
#     object on which the cursor was created.
# 
#     The attribute simplifies writing polymorph code in
#     multi-connection environments.
# 
#     *Warning Message:* "DB-API extension cursor.connection used"
# 
# 
# .. _.scroll:
# .. _.scroll():
# 
# Cursor\ `.scroll`_\ (*value* [, *mode='relative'* ])
#     Scroll the cursor in the result set to a new position according to
#     *mode*.
# 
#     If mode is ``relative`` (default), value is taken as offset to the
#     current position in the result set, if set to ``absolute``, value
#     states an absolute target position.
# 
#     An ``IndexError`` should be raised in case a scroll operation
#     would leave the result set. In this case, the cursor position is
#     left undefined (ideal would be to not move the cursor at all).
# 
#     .. Note::
#         This method should use native scrollable cursors, if available,
#         or revert to an emulation for forward-only scrollable
#         cursors. The method may raise NotSupportedError_ to signal
#         that a specific operation is not supported by the database
#         (e.g. backward scrolling).
# 
#     *Warning Message:* "DB-API extension cursor.scroll() used"
# 
# 
# .. _Cursor.messages:
# 
# `Cursor.messages`_
#     This is a Python list object to which the interface appends tuples
#     (exception class, exception value) for all messages which the
#     interfaces receives from the underlying database for this cursor.
# 
#     The list is cleared by all standard cursor methods calls (prior to
#     executing the call) except for the `.fetch*()`_ calls
#     automatically to avoid excessive memory usage and can also be
#     cleared by executing ``del cursor.messages[:]``.
# 
#     All error and warning messages generated by the database are
#     placed into this list, so checking the list allows the user to
#     verify correct operation of the method calls.
# 
#     The aim of this attribute is to eliminate the need for a Warning
#     exception which often causes problems (some warnings really only
#     have informational character).
# 
#     *Warning Message:* "DB-API extension cursor.messages used"
# 
# 
# .. _Connection.messages:
# 
# `Connection.messages`_
#     Same as Cursor.messages_ except that the messages in the list are
#     connection oriented.
# 
#     The list is cleared automatically by all standard connection
#     methods calls (prior to executing the call) to avoid excessive
#     memory usage and can also be cleared by executing ``del
#     connection.messages[:]``.
# 
#     *Warning Message:* "DB-API extension connection.messages used"
# 
# 
# .. _.next:
# .. _.next():
# 
# Cursor\ `.next`_\ ()
#     Return the next row from the currently executing SQL statement
#     using the same semantics as `.fetchone()`_.  A ``StopIteration``
#     exception is raised when the result set is exhausted for Python
#     versions 2.2 and later.  Previous versions don't have the
#     ``StopIteration`` exception and so the method should raise an
#     ``IndexError`` instead.
# 
#     *Warning Message:* "DB-API extension cursor.next() used"
# 
# 
# .. _.__iter__:
# .. _.__iter__():
# 
# Cursor\ `.__iter__`_\ ()
#     Return self to make cursors compatible to the iteration protocol
#     [8]_.
# 
#     *Warning Message:* "DB-API extension cursor.__iter__() used"
# 
# 
# .. _.lastrowid:
# 
# Cursor\ `.lastrowid`_
#     This read-only attribute provides the rowid of the last modified
#     row (most databases return a rowid only when a single ``INSERT``
#     operation is performed). If the operation does not set a rowid or
#     if the database does not support rowids, this attribute should be
#     set to ``None``.
# 
#     The semantics of ``.lastrowid`` are undefined in case the last
#     executed statement modified more than one row, e.g. when using
#     ``INSERT`` with ``.executemany()``.
# 
#     *Warning Message:* "DB-API extension cursor.lastrowid used"
# 
# 
# .. _Connection.autocommit:
# .. _.autocommit:
# 
# Connection\ `.autocommit`_
#     Attribute to query and set the autocommit mode of the connection.
# 
#     Return ``True`` if the connection is operating in autocommit
#     (non-transactional) mode. Return ``False`` if the connection is
#     operating in manual commit (transactional) mode.
# 
#     Setting the attribute to ``True`` or ``False`` adjusts the
#     connection's mode accordingly.
# 
#     Changing the setting from ``True`` to ``False`` (disabling
#     autocommit) will have the database leave autocommit mode and start
#     a new transaction. Changing from ``False`` to ``True`` (enabling
#     autocommit) has database dependent semantics with respect to how
#     pending transactions are handled. [12]_
# 
#     *Deprecation notice*: Even though several database modules implement
#     both the read and write nature of this attribute, setting the
#     autocommit mode by writing to the attribute is deprecated, since
#     this may result in I/O and related exceptions, making it difficult
#     to implement in an async context. [13]_
# 
#     *Warning Message:* "DB-API extension connection.autocommit used"
# 
# 
# Optional Error Handling Extensions
# ==================================
# 
# The core DB API specification only introduces a set of exceptions
# which can be raised to report errors to the user. In some cases,
# exceptions may be too disruptive for the flow of a program or even
# render execution impossible.
# 
# For these cases and in order to simplify error handling when dealing
# with databases, database module authors may choose to implement user
# definable error handlers. This section describes a standard way of
# defining these error handlers.
# 
# .. _Connection.errorhandler:
# .. _Cursor.errorhandler:
# 
# `Connection.errorhandler`_, `Cursor.errorhandler`_
#     Read/write attribute which references an error handler to call in
#     case an error condition is met.
# 
#     The handler must be a Python callable taking the following arguments:
# 
#     .. parsed-literal::
# 
#         errorhandler(*connection*, *cursor*, *errorclass*, *errorvalue*)
# 
#     where connection is a reference to the connection on which the
#     cursor operates, cursor a reference to the cursor (or ``None`` in
#     case the error does not apply to a cursor), *errorclass* is an
#     error class which to instantiate using *errorvalue* as
#     construction argument.
# 
#     The standard error handler should add the error information to the
#     appropriate ``.messages`` attribute (`Connection.messages`_ or
#     `Cursor.messages`_) and raise the exception defined by the given
#     *errorclass* and *errorvalue* parameters.
# 
#     If no ``.errorhandler`` is set (the attribute is ``None``), the
#     standard error handling scheme as outlined above, should be
#     applied.
# 
#     *Warning Message:* "DB-API extension .errorhandler used"
# 
# Cursors should inherit the ``.errorhandler`` setting from their
# connection objects at cursor creation time.
# 
# 
# Optional Two-Phase Commit Extensions
# ====================================
# 
# Many databases have support for two-phase commit (TPC) which allows
# managing transactions across multiple database connections and other
# resources.
# 
# If a database backend provides support for two-phase commit and the
# database module author wishes to expose this support, the following
# API should be implemented. NotSupportedError_ should be raised, if the
# database backend support for two-phase commit can only be checked at
# run-time.
# 
# TPC Transaction IDs
# -------------------
# 
# As many databases follow the XA specification, transaction IDs are
# formed from three components:
# 
# * a format ID
# * a global transaction ID
# * a branch qualifier
# 
# For a particular global transaction, the first two components should
# be the same for all resources.  Each resource in the global
# transaction should be assigned a different branch qualifier.
# 
# The various components must satisfy the following criteria:
# 
# * format ID: a non-negative 32-bit integer.
# 
# * global transaction ID and branch qualifier: byte strings no
#   longer than 64 characters.
# 
# Transaction IDs are created with the `.xid()`_ Connection method:
# 
# 
# .. _.xid:
# .. _.xid():
# 
# `.xid`_\ (*format_id*, *global_transaction_id*, *branch_qualifier*)
#     Returns a transaction ID object suitable for passing to the
#     `.tpc_*()`_ methods of this connection.
# 
#     If the database connection does not support TPC, a
#     NotSupportedError_ is raised.
# 
#     The type of the object returned by `.xid()`_ is not defined, but
#     it must provide sequence behaviour, allowing access to the three
#     components.  A conforming database module could choose to
#     represent transaction IDs with tuples rather than a custom object.
# 
# 
# TPC Connection Methods
# ----------------------
# 
# .. _.tpc_*:
# .. _.tpc_*():
# 
# .. _.tpc_begin:
# .. _.tpc_begin():
# 
# `.tpc_begin`_\ (*xid*)
#     Begins a TPC transaction with the given transaction ID *xid*.
# 
#     This method should be called outside of a transaction (*i.e.*
#     nothing may have executed since the last `.commit()`_ or
#     `.rollback()`_).
# 
#     Furthermore, it is an error to call `.commit()`_ or `.rollback()`_
#     within the TPC transaction. A ProgrammingError_ is raised, if the
#     application calls `.commit()`_ or `.rollback()`_ during an active
#     TPC transaction.
# 
#     If the database connection does not support TPC, a
#     NotSupportedError_ is raised.
# 
# 
# .. _.tpc_prepare:
# .. _.tpc_prepare():
# 
# `.tpc_prepare`_\ ()
#     Performs the first phase of a transaction started with
#     `.tpc_begin()`_.  A ProgrammingError_ should be raised if this
#     method outside of a TPC transaction.
# 
#     After calling `.tpc_prepare()`_, no statements can be executed
#     until `.tpc_commit()`_ or `.tpc_rollback()`_ have been called.
# 
# 
# .. _.tpc_commit:
# .. _.tpc_commit():
# 
# `.tpc_commit`_\ ([ *xid* ])
#     When called with no arguments, `.tpc_commit()`_ commits a TPC
#     transaction previously prepared with `.tpc_prepare()`_.
# 
#     If `.tpc_commit()`_ is called prior to `.tpc_prepare()`_, a single
#     phase commit is performed.  A transaction manager may choose to do
#     this if only a single resource is participating in the global
#     transaction.
# 
#     When called with a transaction ID *xid*, the database commits the
#     given transaction.  If an invalid transaction ID is provided, a
#     ProgrammingError_ will be raised.  This form should be called
#     outside of a transaction, and is intended for use in recovery.
# 
#     On return, the TPC transaction is ended.
# 
# 
# .. _.tpc_rollback:
# .. _.tpc_rollback():
# 
# `.tpc_rollback`_\ ([ *xid* ])
#     When called with no arguments, `.tpc_rollback()`_ rolls back a TPC
#     transaction.  It may be called before or after `.tpc_prepare()`_.
# 
#     When called with a transaction ID *xid*, it rolls back the given
#     transaction.  If an invalid transaction ID is provided, a
#     ProgrammingError_ is raised.  This form should be called outside
#     of a transaction, and is intended for use in recovery.
# 
#     On return, the TPC transaction is ended.
# 
# .. _.tpc_recover:
# .. _.tpc_recover():
# 
# `.tpc_recover`_\ ()
#     Returns a list of pending transaction IDs suitable for use with
#     ``.tpc_commit(xid)`` or ``.tpc_rollback(xid)``.
# 
#     If the database does not support transaction recovery, it may
#     return an empty list or raise NotSupportedError_.
# 
# 
# 
# Frequently Asked Questions
# ==========================
# 
# The database SIG often sees reoccurring questions about the DB API
# specification. This section covers some of the issues people sometimes
# have with the specification.
# 
# **Question:**
# 
# How can I construct a dictionary out of the tuples returned by
# `.fetch*()`_:
# 
# **Answer:**
# 
# There are several existing tools available which provide helpers for
# this task. Most of them use the approach of using the column names
# defined in the cursor attribute `.description`_ as basis for the keys
# in the row dictionary.
# 
# Note that the reason for not extending the DB API specification to
# also support dictionary return values for the `.fetch*()`_ methods is
# that this approach has several drawbacks:
# 
# * Some databases don't support case-sensitive column names or
#   auto-convert them to all lowercase or all uppercase characters.
# 
# * Columns in the result set which are generated by the query (e.g.
#   using SQL functions) don't map to table column names and databases
#   usually generate names for these columns in a very database specific
#   way.
# 
# As a result, accessing the columns through dictionary keys varies
# between databases and makes writing portable code impossible.
# 
# 
# 
# Major Changes from Version 1.0 to Version 2.0
# =============================================
# 
# The Python Database API 2.0 introduces a few major changes compared to
# the 1.0 version. Because some of these changes will cause existing DB
# API 1.0 based scripts to break, the major version number was adjusted
# to reflect this change.
# 
# These are the most important changes from 1.0 to 2.0:
# 
# * The need for a separate dbi module was dropped and the functionality
#   merged into the module interface itself.
# 
# * New constructors and `Type Objects`_ were added for date/time
#   values, the ``RAW`` Type Object was renamed to ``BINARY``. The
#   resulting set should cover all basic data types commonly found in
#   modern SQL databases.
# 
# * New constants (apilevel_, threadsafety_, paramstyle_) and methods
#   (`.executemany()`_, `.nextset()`_) were added to provide better
#   database bindings.
# 
# * The semantics of `.callproc()`_ needed to call stored procedures are
#   now clearly defined.
# 
# * The definition of the `.execute()`_ return value changed.
#   Previously, the return value was based on the SQL statement type
#   (which was hard to implement right) — it is undefined now; use the
#   more flexible `.rowcount`_ attribute instead. Modules are free to
#   return the old style return values, but these are no longer mandated
#   by the specification and should be considered database interface
#   dependent.
# 
# * Class based exceptions_ were incorporated into the specification.
#   Module implementors are free to extend the exception layout defined
#   in this specification by subclassing the defined exception classes.
# 
# 
# Post-publishing additions to the DB API 2.0 specification:
# 
# * Additional optional DB API extensions to the set of core
#   functionality were specified.
# 
# 
# Open Issues
# ===========
# 
# Although the version 2.0 specification clarifies a lot of questions
# that were left open in the 1.0 version, there are still some remaining
# issues which should be addressed in future versions:
# 
# * Define a useful return value for `.nextset()`_ for the case where a
#   new result set is available.
# 
# * Integrate the `decimal module
#   <http://docs.python.org/library/decimal.html>`__ ``Decimal`` object
#   for use as loss-less monetary and decimal interchange format.
# 
# 
# 
# Footnotes
# =========
# 
# .. [1] As a guideline the connection constructor parameters should be
#     implemented as keyword parameters for more intuitive use and
#     follow this order of parameters:
# 
#     ============= ====================================
#     Parameter     Meaning
#     ============= ====================================
#     ``dsn``       Data source name as string
#     ``user``      User name as string (optional)
#     ``password``  Password as string (optional)
#     ``host``      Hostname (optional)
#     ``database``  Database name (optional)
#     ============= ====================================
# 
#     E.g. a connect could look like this::
# 
#         connect(dsn='myhost:MYDB', user='guido', password='234$')
# 
#     Also see [13]_ regarding planned future additions to this list.
# 
# .. [2] Module implementors should prefer ``numeric``, ``named`` or
#     ``pyformat`` over the other formats because these offer more
#     clarity and flexibility.
# 
# 
# .. [3] If the database does not support the functionality required by
#     the method, the interface should throw an exception in case the
#     method is used.
# 
#     The preferred approach is to not implement the method and thus have
#     Python generate an ``AttributeError`` in case the method is
#     requested. This allows the programmer to check for database
#     capabilities using the standard ``hasattr()`` function.
# 
#     For some dynamically configured interfaces it may not be
#     appropriate to require dynamically making the method
#     available. These interfaces should then raise a
#     ``NotSupportedError`` to indicate the non-ability to perform the
#     roll back when the method is invoked.
# 
# .. [4] A database interface may choose to support named cursors by
#     allowing a string argument to the method. This feature is not part
#     of the specification, since it complicates semantics of the
#     `.fetch*()`_ methods.
# 
# .. [5] The module will use the ``__getitem__`` method of the
#     parameters object to map either positions (integers) or names
#     (strings) to parameter values.  This allows for both sequences and
#     mappings to be used as input.
# 
#     The term *bound* refers to the process of binding an input value
#     to a database execution buffer. In practical terms, this means
#     that the input value is directly used as a value in the operation.
#     The client should not be required to "escape" the value so that it
#     can be used — the value should be equal to the actual database
#     value.
# 
# .. [6] Note that the interface may implement row fetching using arrays
#     and other optimizations. It is not guaranteed that a call to this
#     method will only move the associated cursor forward by one row.
# 
# .. [7] The ``rowcount`` attribute may be coded in a way that updates
#     its value dynamically. This can be useful for databases that
#     return usable ``rowcount`` values only after the first call to a
#     `.fetch*()`_ method.
# 
# .. [8] Implementation Note: Python C extensions will have to implement
#     the ``tp_iter`` slot on the cursor object instead of the
#     ``.__iter__()`` method.
# 
# .. [9] The term *number of affected rows* generally refers to the
#     number of rows deleted, updated or inserted by the last statement
#     run on the database cursor. Most databases will return the total
#     number of rows that were found by the corresponding ``WHERE``
#     clause of the statement. Some databases use a different
#     interpretation for ``UPDATE``\s and only return the number of rows
#     that were changed by the ``UPDATE``, even though the ``WHERE``
#     clause of the statement may have found more matching rows.
#     Database module authors should try to implement the more common
#     interpretation of returning the total number of rows found by the
#     ``WHERE`` clause, or clearly document a different interpretation
#     of the ``.rowcount`` attribute.
# 
# .. [10] In Python 2 and earlier versions of this PEP, ``StandardError``
#     was used as the base class for all DB-API exceptions. Since
#     ``StandardError`` was removed in Python 3, database modules
#     targeting Python 3 should use ``Exception`` as base class instead.
#     The PEP was updated to use ``Exception`` throughout the text, to
#     avoid confusion. The change should not affect existing modules or
#     uses of those modules, since all DB-API error exception classes are
#     still rooted at the ``Error`` or ``Warning`` classes.
# 
# .. [11] In a future revision of the DB-API, the base class for
#     ``Warning`` will likely change to the builtin ``Warning`` class. At
#     the time of writing of the DB-API 2.0 in 1999, the warning framework
#     in Python did not yet exist.
# 
# .. [12] Many database modules implementing the autocommit attribute will
#     automatically commit any pending transaction and then enter
#     autocommit mode. It is generally recommended to explicitly
#     `.commit()`_ or `.rollback()`_ transactions prior to changing the
#     autocommit setting, since this is portable across database modules.
# 
# .. [13] In a future revision of the DB-API, we are going to introduce a
#     new method ``.setautocommit(value)``, which will allow setting the
#     autocommit mode, and make ``.autocommit`` a read-only attribute.
#     Additionally, we are considering to add a new standard keyword
#     parameter ``autocommit`` to the Connection constructor. Modules
#     authors are encouraged to add these changes in preparation for this
#     change.
# 
# Acknowledgements
# ================
# 
# Many thanks go to Andrew Kuchling who converted the Python Database
# API Specification 2.0 from the original HTML format into the PEP
# format in 2001.
# 
# Many thanks to James Henstridge for leading the discussion which led to
# the standardization of the two-phase commit API extensions in 2008.
# 
# Many thanks to Daniele Varrazzo for converting the specification from
# text PEP format to ReST PEP format, which allows linking to various
# parts in 2012.
# 
# Copyright
# =========
# 
# This document has been placed in the Public Domain.
