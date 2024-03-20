from polypheny.interval import IntervalMonth
from polypheny.serialize import proto2py
from polypheny import Error
from polyprism import value_pb2

import pytest

def test_zero_months():
    m = IntervalMonth(0)
    assert str(m) == "0 months"

def test_one_month():
    m = IntervalMonth(1)
    assert str(m) == "1 month"

def test_twelve_months():
    m = IntervalMonth(12)
    assert str(m) == "1 year"

def test_thirteen_months():
    m = IntervalMonth(13)
    assert str(m) == "1 year and 1 month"

def test_interval_unit_unknown():
    v = value_pb2.ProtoValue()
    v.interval.CopyFrom(value_pb2.ProtoInterval())
    with pytest.raises(Error):
        proto2py(v)
