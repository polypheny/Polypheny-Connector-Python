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

import polypheny
import pytest
import time

from test_helper import con, cur

# tests the con fixture helper works
def test_conn(con):
    pass

def test_commit(con):
    cur = con.cursor()

    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    cur.execute('INSERT INTO t(id, a) VALUES (1, 2)')
    con.commit()

    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == 2

def test_rollback(con):
    cur = con.cursor()

    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    cur.execute('INSERT INTO t(id, a) VALUES (1, 2)')
    con.rollback()

    cur.execute('SELECT a FROM t')
    assert cur.fetchone() is None

def test_fetch_size(con):
    cur = con.cursor()

    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    for i in range(30):
        cur.execute('INSERT INTO t(id, a) VALUES (?, ?)', (i, i))
    con.commit()

    for i in (1, 5, 30, 60):
        cur.execute('SELECT id, a FROM t', fetch_size=i)
        assert len(cur.fetchall()) == 30

def test_fetch_insert(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    cur.execute('INSERT INTO t(id, a) VALUES (1, 1)')
    with pytest.raises(polypheny.Error):
        cur.fetchone()

def test_error_on_closed_con(con):
    con.close()
    with pytest.raises(polypheny.ProgrammingError):
        con.cursor()
    with pytest.raises(polypheny.ProgrammingError):
        con.commit()
    with pytest.raises(polypheny.ProgrammingError):
        con.rollback()
    # Raises no exception
    con.close()

def test_cursor_autoclose(con):
    cur = con.cursor()
    cur.execute('SELECT 1')
    con.close()

def test_execute_wrongparams(cur):
    with pytest.raises(polypheny.Error):
        cur.execute('SELECT ?', 5)

def test_execute_closed_cursor(cur):
    with pytest.raises(polypheny.Error):
        cur.close()
        cur.executeany('mql', 'db.abc.find()')

def test_fetch_closed_cursor(cur):
    with pytest.raises(polypheny.Error):
        cur.execute('SELECT  1')
        cur.close()
        cur.fetchone()

def test_invalid_creds():
    with pytest.raises(polypheny.Error):
        polypheny.connect(('127.0.0.1', 20590), username='unknown', password='', transport='plain')

def test_invalid_version():
    import polypheny.rpc as rpc
    major = rpc.POLYPHENY_API_MAJOR
    try:
        with pytest.raises(polypheny.Error):
            rpc.POLYPHENY_API_MAJOR = major - 1
            polypheny.connect(('127.0.0.1', 20590), username='pa', password='', transport='plain')
    finally:
        rpc.POLYPHENY_API_MAJOR = major
