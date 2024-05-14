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

def test_serialize_time_with_micros(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a TIME(3) NOT NULL, PRIMARY KEY(i))')
    cur.execute('INSERT INTO t(i, a) VALUES (0, ?)', (datetime.time(15, 19, 10, 12),))
    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] != datetime.time(15, 19, 10, 12)  # This should be equal
    assert cur.fetchone() is None
