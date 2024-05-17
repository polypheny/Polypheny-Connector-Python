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

import datetime
import decimal
from functools import reduce

import polypheny.interval as interval
from org.polypheny.prism import value_pb2


def serialize_big_decimal(v, value):
    sign, digits, exponent = value.as_tuple()
    sign = -2 * sign + 1
    unscaled = sign * reduce(lambda r, d: r * 10 + d, digits)
    l = unscaled.bit_length() + 1  # add sign bit
    n = (l + 8) >> 3
    v.big_decimal.unscaled_value = unscaled.to_bytes(n, byteorder='big', signed=True)
    v.big_decimal.scale = -exponent


# See ProtoValueDeserializer
def py2proto(value, v=None):
    if v is None:
        v = value_pb2.ProtoValue()
    if type(value) is bool:
        v.boolean.boolean = value
    elif type(value) is int:
        if -2 ** 31 <= value <= 2 ** 31 - 1:
            v.integer.integer = value
        elif -2 ** 63 <= value <= 2 ** 63 - 1:
            v.long.long = value
        else:
            serialize_big_decimal(v, decimal.Decimal(value))
    elif type(value) is float:
        # TODO: Always use decimal?
        v.double.double = value
    elif type(value) is decimal.Decimal:
        serialize_big_decimal(v, value)
    elif type(value) is datetime.date:
        diff = value - datetime.date(1970, 1, 1)
        v.date.date = diff.days
    elif type(value) is datetime.time:
        v.time.time = (value.hour * 3600 + value.minute * 60 + value.second) * 1000 + value.microsecond * 10
    elif type(value) is datetime.datetime:
        v.timestamp.timestamp = int(value.timestamp() * 1000)
    elif type(value) is str:
        v.string.string = value
    elif type(value) is bytes:
        v.binary.binary = value
    elif value is None:
        v.null.CopyFrom(value_pb2.ProtoNull())
    elif type(value) is list:
        for element in value:
            v.list.values.append(py2proto(element))
    else:
        raise NotImplementedError

    return v


def parse_big_decimal(value):
    raw = value.unscaled_value
    scale = value.scale
    n = int.from_bytes(raw, byteorder='big', signed=True)
    sign = 0
    if n < 0:
        sign = 1
        n = -n
    return decimal.Decimal((sign, tuple(map(int, str(n))), -scale))


def proto2py(value):
    name = value.WhichOneof("value")
    assert name is not None
    if name == "boolean":
        return value.boolean.boolean
    elif name == "integer":
        return value.integer.integer
    elif name == "long":
        return value.long.long
    elif name == "big_decimal":
        return parse_big_decimal(value.big_decimal)
    elif name == "float":
        return value.float.float
    elif name == "double":
        return value.double.double
    elif name == "date":
        return datetime.date(1970, 1, 1) + datetime.timedelta(days=value.date.date)
    elif name == "time":
        t = value.time.time
        millis = t % 1000
        t = t / 1000
        hour = int(t / 3600)
        t = t % 3600
        minute = int(t / 60)
        t = t % 60
        second = int(t)
        return datetime.time(hour, minute, second, microsecond=int(millis * 1000))
    elif name == "timestamp":
        return datetime.datetime.fromtimestamp(value.timestamp.timestamp / 1000, datetime.timezone.utc)
    elif name == "interval":
        return interval.IntervalMonthMilliseconds(value.interval.months, value.interval.milliseconds)
    elif name == "string":
        return value.string.string
    elif name == "binary":
        return value.binary.binary
    elif name == "null":
        return None
    elif name == "list":
        return list(map(lambda e: proto2py(e), value.list.values))
    elif name == "document":
        res = {}
        for entry in value.document.entries:
            k = proto2py(entry.key)
            assert isinstance(k, str)  # TODO: Correct?
            v = proto2py(entry.value)
            res[k] = v
        return res
    else:
        raise RuntimeError("Unhandled value type")
