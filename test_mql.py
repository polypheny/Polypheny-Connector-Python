import polypheny
import pytest
import time

from test_helper import con, cur

def test_getstar(con):
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a INTEGER NOT NULL, PRIMARY KEY(i))')
    cur.executemany('INSERT INTO t(i, a) VALUES (?, ?)', [(0, 1), (1, 2), (2, 3)])
    con.commit()
    cur.executeany('mongo', 'db.t.find()')
    assert list(sorted(cur.fetchall(), key=lambda a: a['i'] )) == [{'i': 0, 'a': 1}, {'i': 1, 'a': 2}, {'i': 2, 'a': 3}]
