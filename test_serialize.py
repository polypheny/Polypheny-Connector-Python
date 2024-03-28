import datetime
import decimal
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
    ints = {1, 2**42, -1, (2**63)-1, -2**63}
    for i in ints:
        cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (i,))
    cur.execute('SELECT a FROM t')
    res = set(map(lambda x: x[0], cur.fetchall()))
    assert ints == res

def test_serialize_decimal_local():
    pytest.skip('Needs correct float comparison')
    decimals = {2**64, -2**64, 0, 0.49, 0.5, 0.51, -0.49, -0.5, -0.51}
    for d in decimals:
        d = decimal.Decimal(d)
        assert polypheny.serialize.proto2py(polypheny.serialize.py2proto(d)) == float(d)

def test_serialize_floats(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DOUBLE NOT NULL, PRIMARY KEY(i))')
    floats = {0, 0.49, 0.5, 0.51, -0.49, -0.5, -0.51}
    for i, f in enumerate(floats):
        cur.execute('INSERT INTO t(i, a) VALUES (?, ?)', (i, f,))
        cur.execute('SELECT a FROM t WHERE i = ?', (i,))
        assert cur.fetchone()[0] == f
        assert cur.fetchone() is None

def test_serialize_decimal(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DECIMAL(2, 2) NOT NULL, PRIMARY KEY(i))')
    decimals = {0, 0.49, 0.5, 0.51, -0.49, -0.5, -0.51}
    for i, d in enumerate(decimals):
        d = decimal.Decimal(d)
        cur.execute('INSERT INTO t(i, a) VALUES (?, ?)', (i, d,))
        cur.execute('SELECT a FROM t WHERE i = ?', (i,))
        assert cur.fetchone()[0] == d
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
    cur.execute('DROP TABLE IF EXISTS t')
    with pytest.raises(polypheny.Error):
        cur.execute('CREATE TABLE t(a BOOLEAN)')
