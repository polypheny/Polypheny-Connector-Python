"""
This file contains tests that do not work yet, but should work in future versions of Polypheny.
"""
import datetime

import polypheny
import pytest

from test_helper import con, cur, cur_with_data

def test_cypher(cur_with_data):
    cur = cur_with_data
    with pytest.raises(polypheny.Error):
        cur.executeany('cypher', 'MATCH (e:customers) WHERE e.id = 1 RETURN e.name')
        assert cur.fetchone()[0] == 'Maria'

def test_pig(cur_with_data):
    pytest.skip("Causes a hang on Polypheny side")
    cur = cur_with_data
    cur.executeany('pig', "A = LOAD 'customers'; B = FILTER A BY id == 1; DUMP B;")
    assert cur.fetchone()[0] == 'Maria'

def test_deserialize_null(cur):
    with pytest.raises(polypheny.Error):
        cur.execute("SELECT NULL")

    return  # remove if execute works
    assert cur.fetchone()[0] == None

def test_serialize_null_string(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a VARCHAR(255), PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (None,))
    with pytest.raises(polypheny.Error):
        cur.execute('SELECT a FROM t')

    return  # remove if execute works
    assert cur.fetchone()[0] == None
    assert cur.fetchone() is None

def test_serialize_varbinary(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    with pytest.raises(polypheny.Error):
        cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a BINARY VARYING NOT NULL, PRIMARY KEY(i))')

    return  # remove if execute works
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (b'Hello World',))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == b'Hello World'
    assert cur.fetchone() is None

def test_insert_double(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    with pytest.raises(polypheny.Error):
        cur.execute('INSERT INTO t(id, a) VALUES (1, 2), (?, ?)', (2, 3))

    return  # remove if execute works
    cur.execute('SELECT id, a FROM t ORDER BY id')
    assert cur.fetchone() == [1, 2]
    assert cur.fetchone() == [2, 3]

def test_dynamic_text_parameter(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a TEXT NOT NULL, PRIMARY KEY(i))')
    with pytest.raises(polypheny.Error):
        cur.execute('SELECT a FROM t WHERE a = ?', ('Hello World',))

    return  # remove if execute works
    assert cur.fetchone() is None

def test_serialize_time_with_micros(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a TIME(3) NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (datetime.time(15, 19, 10, 12),))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] != datetime.time(15, 19, 10, 12)  # This should be equal
    assert cur.fetchone() is None