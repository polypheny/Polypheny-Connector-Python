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

import sys

import polypheny
import pytest

@pytest.fixture
def con():
    if sys.platform == 'win32':
        con = polypheny.connect(('127.0.0.1', 20590), username='pa', password='', transport='plain')
    else:
        con = polypheny.connect()
    #con = polypheny.connect(('127.0.0.1', 2020), username='pa', password='', transport='noise', transport_params={'insecure': True})
    yield con
    con.close()

@pytest.fixture
def cur(con):
    yield con.cursor()

@pytest.fixture
def cur_with_data(con, cur):
    cur.execute('DROP TABLE IF EXISTS customers')
    cur.execute("""
        CREATE TABLE customers(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            year_joined INTEGER NOT NULL
        )""")
    cur.executemany(
        'INSERT INTO customers(id, name, year_joined) VALUES (?, ?, ?)',
        [(1, 'Maria', 2012),
         (2, 'Daniel', 2020),
         (3, 'Peter', 2001),
         (4, 'Anna', 2001),
         (5, 'Thomas', 2004),
         (6, 'Andreas', 2014),
         (7, 'Michael', 2010)]
    )
    con.commit()

    yield cur

    cur.execute('DROP TABLE customers')
