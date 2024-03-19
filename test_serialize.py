import datetime
import math

import polypheny
import pytest

from test_helper import con, cur

def test_serialize_bool(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a BOOLEAN, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (True,))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == True
    assert cur.fetchone() is None

def test_serialize_number(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a BIGINT NOT NULL, PRIMARY KEY(i))')
    ints = {1, 2**42}
    for i in ints:
        cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (i,))
    cur.execute('SELECT a FROM t')
    res = set(map(lambda x: x[0], cur.fetchall()))
    assert ints == res

def test_serialize_decimal(cur):
    pytest.skip('Broken')
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DECIMAL NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (2**77,))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == 2**77
    assert cur.fetchone() is None

def test_serialize_string(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a VARCHAR(255) NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', ('Hello World',))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == 'Hello World'
    assert cur.fetchone() is None

def test_serialize_binary(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a FILE NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (b'Hello World',))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == b'Hello World'
    assert cur.fetchone() is None

def test_serialize_date(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DATE NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (datetime.date(2024, 3, 8),))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == datetime.date(2024, 3, 8)
    assert cur.fetchone() is None

def test_serialize_float(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DOUBLE NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (2.71,))
    cur.execute('SELECT a FROM t')
    assert math.isclose(cur.fetchone()[0], 2.71)
    assert cur.fetchone() is None

def test_serialize_time(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a TIME NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (datetime.time(15, 19, 10),))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == datetime.time(15, 19, 10)
    assert cur.fetchone() is None

def test_serialize_time_with_micros(cur):
    pytest.skip("Microseconds are not returned by Polypheny")
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a TIME NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (datetime.time(15, 19, 10, 12),))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == datetime.time(15, 19, 10, 12)
    assert cur.fetchone() is None

def test_serialize_timestamp(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a TIMESTAMP NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (datetime.datetime(2024, 3, 8, 15, 19, 10),))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == datetime.datetime(2024, 3, 8, 15, 19, 10).astimezone(datetime.timezone.utc)
    assert cur.fetchone() is None

def test_serialize_interval(cur):
    cur.execute("SELECT INTERVAL '3' SECOND")
    assert cur.fetchone()[0] == datetime.timedelta(seconds=3)
    cur.execute("SELECT INTERVAL '3:7' MINUTE TO SECOND")
    assert cur.fetchone()[0] == datetime.timedelta(minutes=3, seconds=7)
    cur.execute("SELECT INTERVAL '3' MINUTE")
    assert cur.fetchone()[0] == datetime.timedelta(minutes=3)
    cur.execute("SELECT INTERVAL '3:0:7' HOUR TO SECOND")
    assert cur.fetchone()[0] == datetime.timedelta(hours=3, seconds=7)
    cur.execute("SELECT INTERVAL '3:7' HOUR TO MINUTE")
    assert cur.fetchone()[0] == datetime.timedelta(hours=3, minutes=7)
    cur.execute("SELECT INTERVAL '3' HOUR")
    assert cur.fetchone()[0] == datetime.timedelta(hours=3)
    cur.execute("SELECT INTERVAL '3 0:0:7' DAY TO SECOND")
    assert cur.fetchone()[0] == datetime.timedelta(days=3, seconds=7)
    cur.execute("SELECT INTERVAL '3 0:7' DAY TO MINUTE")
    assert cur.fetchone()[0] == datetime.timedelta(days=3, minutes=7)
    cur.execute("SELECT INTERVAL '3 7' DAY TO HOUR")
    assert cur.fetchone()[0] == datetime.timedelta(days=3, hours=7)
    cur.execute("SELECT INTERVAL '3' DAY")
    assert cur.fetchone()[0] == datetime.timedelta(days=3)
    cur.execute("SELECT INTERVAL '3' MONTH")
    assert cur.fetchone()[0] == polypheny.interval.IntervalMonth(3)
    cur.execute("SELECT INTERVAL '3-7' YEAR TO MONTH")
    assert cur.fetchone()[0] == polypheny.interval.IntervalMonth(43)
    cur.execute("SELECT INTERVAL '3' YEAR")
    assert cur.fetchone()[0] == polypheny.interval.IntervalMonth(36)

def test_serialize_null(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a INTEGER, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (None,))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == None
    assert cur.fetchone() is None

def test_serialize_list(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a ARRAY, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', ([1, 2, 3],))
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
    cur.execute("SELECT 1;")

def test_fail_with_superfluous_param(cur):
    pytest.skip("Fails")
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a BOOLEAN)')
    cur.execute('INSERT INTO t(id, a) VALUES (0, ?)', (True,))
    cur.execute('SELECT a FROM t', (True,))
    assert cur.fetchone()[0] == True

def test_no_error_when_invalid_create(cur):
    pytest.skip("Does not properly error out")
    cur.execute('CREATE TABLE t(a BOOLEAN)')

def test_serialize_null_string(cur):
    pytest.skip('Broken')
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a VARCHAR(255), PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (None,))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == None
    assert cur.fetchone() is None

def test_serialize_varbinary(cur):
    pytest.skip('Causes a HSQLDB exception')
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a BINARY VARYING NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (b'Hello World',))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == b'Hello World'
    assert cur.fetchone() is None


def test_insert_double(cur):
    pytest.skip('Fails with HSQLDB exception')
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    cur.execute('INSERT INTO t(id, a) VALUES (1, 2), (?, ?)', (2, 3))
    cur.execute('SELECT id, a FROM t ORDER BY id')
    assert cur.fetchone() == [1, 2]
    assert cur.fetchone() == [2, 3]
