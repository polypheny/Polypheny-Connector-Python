from polypheny.interval import IntervalMonthMilliseconds
from polypheny.serialize import proto2py
from polypheny import Error
from org.polypheny.prism import value_pb2

import pytest

def test_zero_months():
    m = IntervalMonthMilliseconds(0, 0)
    assert str(m) == "0 months and 0 milliseconds"

def test_one_month():
    m = IntervalMonthMilliseconds(1, 1)
    assert str(m) == "1 month and 1 millisecond"

def test_thirteen_months():
    m = IntervalMonthMilliseconds(2, 2)
    assert str(m) == "2 months and 2 milliseconds"
