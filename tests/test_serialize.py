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

import datetime
import decimal
import math
import os

import polypheny
import pytest

from polypheny.interval import IntervalMonthMilliseconds

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
    for n, i in enumerate(ints):
        cur.execute('INSERT INTO t(i, a) VALUES (?, ?)', (n, i,))
    cur.execute('SELECT a FROM t')
    res = set(map(lambda x: x[0], cur.fetchall()))
    assert ints == res

def test_serialize_decimal_local():
    decimals = {2**64, -2**64, 0, 0.49, 0.5, 0.51, -0.49, -0.5, -0.51}
    for d in map(decimal.Decimal, decimals):
        assert polypheny.serialize.proto2py(polypheny.serialize.py2proto(d)) == d

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
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DECIMAL(3, 2) NOT NULL, PRIMARY KEY(i))')
    decimals = {'0', '0.49', '0.5', '0.51', '-0.49', '-0.5', '-0.51'}
    for i, d in enumerate(map(decimal.Decimal, decimals)):
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
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 3000)
    cur.execute("SELECT INTERVAL '3:7' MINUTE TO SECOND")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 187000)
    cur.execute("SELECT INTERVAL '3' MINUTE")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 180000)
    cur.execute("SELECT INTERVAL '3:0:7' HOUR TO SECOND")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 10807000)
    cur.execute("SELECT INTERVAL '3:7' HOUR TO MINUTE")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 11220000)
    cur.execute("SELECT INTERVAL '3' HOUR")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 10800000)
    cur.execute("SELECT INTERVAL '3 0:0:7' DAY TO SECOND")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 259207000)
    cur.execute("SELECT INTERVAL '3 0:7' DAY TO MINUTE")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 259620000)
    cur.execute("SELECT INTERVAL '3 7' DAY TO HOUR")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 284400000)
    cur.execute("SELECT INTERVAL '3' DAY")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(0, 259200000)
    cur.execute("SELECT INTERVAL '3' MONTH")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(3, 0)
    cur.execute("SELECT INTERVAL '3-7' YEAR TO MONTH")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(43, 0)
    cur.execute("SELECT INTERVAL '3' YEAR")
    assert cur.fetchone()[0] == IntervalMonthMilliseconds(36, 0)

def test_serialize_null(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a INTEGER, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (None,))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == None
    assert cur.fetchone() is None

def test_serialize_list(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a INTEGER ARRAY(1, 3), PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', ([1, 2, 3],))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == [1, 2, 3]
    assert cur.fetchone() is None

def test_serialize_decimal_large(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DECIMAL(1) NOT NULL, PRIMARY KEY(i))')
    with pytest.raises(polypheny.Error):
        cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (2**77,))

def test_serialize_decimal_large2(cur):
    if os.getenv('DEFAULT_STORE', '') != 'monetdb':
        cur.execute('DROP TABLE IF EXISTS t')
        cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a DECIMAL NOT NULL, PRIMARY KEY(i))')
        cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (2**77,))
        cur.execute('SELECT a FROM t')

        if os.getenv('DEFAULT_STORE', '') == 'mongodb':
            assert cur.fetchone()[0] == 151115727451828646838272
        else:
            assert cur.fetchone()[0] == Decimal('1.5111572745182865E+23')
        assert cur.fetchone() is None

def test_deserialize_number(cur):
    cur.execute('SELECT 1')
    assert cur.fetchone()[0] == 1

def test_deserialize_float(cur):
    cur.execute('SELECT CAST(0.05 AS FLOAT)')
    assert cur.fetchone()[0] == decimal.Decimal('0.05')

def test_deserialize_real(cur):
    cur.execute('SELECT 0.05')
    assert cur.fetchone()[0] == decimal.Decimal('0.05')

def test_insert_double(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    cur.execute('INSERT INTO t(id, a) VALUES (1, 2), (?, ?)', (2, 3))
    cur.execute('SELECT id, a FROM t ORDER BY id')
    assert cur.fetchone() == [1, 2]
    assert cur.fetchone() == [2, 3]

def test_deserialize_string(cur):
    cur.execute("SELECT 'Hello World'")
    assert cur.fetchone()[0] == 'Hello World'

def test_serialize_null_string(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a VARCHAR(255), PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (None,))
    cur.execute('SELECT a FROM t')

    assert cur.fetchone()[0] == None
    assert cur.fetchone() is None

def test_deserialize_null(cur):
    cur.execute("SELECT NULL")

    assert cur.fetchone()[0] == None

def test_serialize_varbinary(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a BINARY VARYING NOT NULL, PRIMARY KEY(i))')

    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (b'Hello World',))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == b'Hello World'
    assert cur.fetchone() is None

def test_serialize_not_implemented(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a INTEGER, PRIMARY KEY(i))')
    with pytest.raises(NotImplementedError):
        cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', ({'a': 'b'},))

def test_trailing_semicolon(cur):
    cur.execute("SELECT 1;")

def test_with_superfluous_param(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a BOOLEAN)')
    cur.execute('INSERT INTO t(id, a) VALUES (0, ?)', (True,))
    cur.execute('SELECT a FROM t', (True,))
    assert cur.fetchone()[0] == True

def test_no_error_when_invalid_create(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    with pytest.raises(polypheny.Error):
        cur.execute('CREATE TABLE t(a BOOLEAN)')

def test_dynamic_text_parameter(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a TEXT NOT NULL, PRIMARY KEY(i))')
    cur.execute('SELECT a FROM t WHERE a = ?', ('Hello World',))

    assert cur.fetchone() is None
