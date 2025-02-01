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

from test_helper import con, cur, cur_with_data

def test_cql(cur_with_data):
    cur = cur_with_data
    cur.executeany('cql', "public.customers.id == 1 project public.customers.name")
    assert cur.fetchone()[0] == 'Maria'

def test_pig(cur_with_data):
    cur = cur_with_data
    cur.executeany('pig', "A = LOAD 'customers'; B = FILTER A BY id == 1; DUMP B;")
    assert cur.fetchone()[1] == 'Maria'
