import polypheny
import pytest

from test_helper import con, cur, cur_with_data

def test_cql(cur_with_data):
    if sys.platform == 'win32':
        pytest.skip()
    cur = cur_with_data
    cur.executeany('cql', "public.customers.id == 1 project public.customers.name")
    assert cur.fetchone()[0] == 'Maria'

def test_pig(cur_with_data):
    if sys.platform == 'win32':
        pytest.skip()
    cur = cur_with_data
    cur.executeany('pig', "A = LOAD 'customers'; B = FILTER A BY id == 1; DUMP B;")
    assert cur.fetchone()[1] == 'Maria'
