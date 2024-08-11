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
