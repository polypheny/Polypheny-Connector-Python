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

from test_helper import con, cur

def test_getstar(con):
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(i INTEGER NOT NULL, a INTEGER NOT NULL, PRIMARY KEY(i))')
    cur.executemany('INSERT INTO t(i, a) VALUES (?, ?)', [(0, 1), (1, 2), (2, 3)])
    con.commit()
    cur.executeany('mongo', 'db.t.find()')
    assert list(sorted(cur.fetchall(), key=lambda a: a['i'] )) == [{'i': 0, 'a': 1}, {'i': 1, 'a': 2}, {'i': 2, 'a': 3}]

def test_namespace(con):
    cur = con.cursor()
    cur.execute('DROP NAMESPACE IF EXISTS demo')
    cur.execute('CREATE RELATIONAL NAMESPACE demo')
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE demo.t(i INTEGER NOT NULL, a INTEGER NOT NULL, PRIMARY KEY(i))')
    cur.executemany('INSERT INTO demo.t(i, a) VALUES (?, ?)', [(0, 1), (1, 2), (2, 3)])
    con.commit()
    cur.executeany('mongo', 'db.t.find()', namespace='demo')
    assert list(sorted(cur.fetchall(), key=lambda a: a['i'] )) == [{'i': 0, 'a': 1}, {'i': 1, 'a': 2}, {'i': 2, 'a': 3}]
