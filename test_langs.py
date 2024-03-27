import polypheny
import pytest

from test_helper import con, cur, cur_with_data

def test_cql(cur_with_data):
    cur = cur_with_data
    cur.executeany('cql', "public.customers.id == 1 project public.customers.name")
    assert cur.fetchone()[0] == 'Maria'
