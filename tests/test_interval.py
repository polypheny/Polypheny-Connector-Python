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
