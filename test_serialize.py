import math
import polypheny
import pytest

from test_helper import con, cur

def test_serialize_bool(cur):
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a BOOLEAN, PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (True,), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == True
    assert cur.fetchone() is None

def test_serialize_number(cur):
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a BIGINT NOT NULL, PRIMARY KEY(i))', ddl_hack=True)
    ints = {1, 2**42}
    for i in ints:
        cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (i,), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    res = set(map(lambda x: x[0], cur.fetchall()))
    assert ints == res

def test_serialize_decimal(cur):
    pytest.skip('Broken')
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DECIMAL NOT NULL, PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (2**77,), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == 2**77
    assert cur.fetchone() is None

def test_serialize_string(cur):
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a VARCHAR(255) NOT NULL, PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', ('Hello World',), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == 'Hello World'
    assert cur.fetchone() is None

def test_serialize_binary(cur):
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a FILE NOT NULL, PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (b'Hello World',), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == b'Hello World'
    assert cur.fetchone() is None

def test_serialize_float(cur):
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DOUBLE NOT NULL, PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (2.71,), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert math.isclose(cur.fetchone()[0], 2.71)
    assert cur.fetchone() is None

def test_serialize_null(cur):
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a INTEGER, PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (None,), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == None
    assert cur.fetchone() is None

def test_serialize_list(cur):
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a ARRAY, PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', ([1, 2, 3],), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == [1, 2, 3]
    assert cur.fetchone() is None

def test_deserialize_number(cur):
    cur.execute('SELECT 1') # TODO: This seems to return a big decimal.  Very inefficient...
    assert cur.fetchone()[0] == 1

def test_deserialize_float(cur):
    cur.execute('SELECT CAST(0.05 AS FLOAT)')
    assert cur.fetchone()[0] == 0.05

def test_deserialize_real(cur):
    cur.execute('SELECT 0.05') # TODO: Again a big decimal, but is it wrong?
    assert cur.fetchone()[0] == 0.05

def test_deserialize_string(cur):
    cur.execute("SELECT 'Hello World'")
    assert cur.fetchone()[0] == 'Hello World'

def test_deserialize_null(cur):
    pytest.skip('Illegal statement');
    cur.execute("SELECT NULL")
    assert cur.fetchone()[0] == None

def test_serialize_novalue(cur):
    pytest.skip('This throws on the receiver side');
    cur.execute("SELECT * FROM emps WHERE name = :name", {'name': {1: 2}})

def test_trailing_semicolon(cur):
    pytest.skip("Fails due to semicolon")
    cur.execute("SELECT 1;")

def test_fail_with_superfluous_param(cur):
    pytest.skip("Fails")
    cur.execute('DELETE TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(a BOOLEAN)')
    cur.execute('INSERT INTO t(a) VALUES (?)', (True,))
    cur.execute('SELECT a FROM t', (True,))
    assert cur.fetchone()[0] == True

def test_no_error_when_invalid_create(cur):
    pytest.skip("Does not properly error out")
    cur.execute('CREATE TABLE t(a BOOLEAN)', ddl_hack=True)

def test_serialize_null_string(cur):
    pytest.skip('Broken')
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a VARCHAR(255), PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (None,), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == None
    assert cur.fetchone() is None

def test_serialize_varbinary(cur):
    pytest.skip('Causes a HSQLDB exception')
    cur.execute('DROP TABLE IF EXISTS t', ddl_hack=True)
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a BINARY VARYING NOT NULL, PRIMARY KEY(i))', ddl_hack=True)
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (b'Hello World',), ddl_hack=True)
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == b'Hello World'
    assert cur.fetchone() is None

