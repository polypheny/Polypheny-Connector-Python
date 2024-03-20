import datetime

import polypheny.interval as interval
from polypheny.exceptions import Error
from polyprism import value_pb2


# See ProtoValueDeserializer
def py2proto(value, v=None):
    if v is None:
        v = value_pb2.ProtoValue()
    if type(value) == bool:
        v.boolean.boolean = value
    elif type(value) == int:
        if -2 ** 31 <= value <= 2 ** 31 - 1:
            v.integer.integer = value
        elif -2 ** 63 <= value <= 2 ** 63 - 1:
            v.long.long = value
        else:
            n = ((value.bit_length() - 1) // 8) + 1  # TODO: Does this work for negative numbers?
            v.big_decimal.unscaled_value = value.to_bytes(n, byteorder='big', signed=True)
            v.big_decimal.scale = 0
            v.big_decimal.precision = 0
            print(v.big_decimal)
    elif type(value) == float:
        v.double.double = value
        # TODO: Use BigDecimal as well?
    elif type(value) == datetime.date:
        diff = value - datetime.date(1970, 1, 1)
        v.date.date = diff.days
    elif type(value) == datetime.time:
        v.time.time = (value.hour * 3600 + value.minute * 60 + value.second) * 1000 + value.microsecond * 10
    elif type(value) == datetime.datetime:
        v.timestamp.timestamp = int(value.timestamp() * 1000)
    elif type(value) == str:
        v.string.string = value
    elif type(value) == bytes:
        v.binary.binary = value
    elif value is None:
        v.null.CopyFrom(value_pb2.ProtoNull())
    elif type(value) == list:
        for element in value:
            v.list.values.append(py2proto(element))
    elif type(value) == dict:  # experiment to test the server with unset values
        pass
    else:
        raise NotImplementedError

    return v

def parse_big_decimal(value):
    raw = value.unscaled_value
    scale = value.scale
    prec = value.precision

    if scale > (2 ** 31) - 1:
        scale = scale - 2 ** 32

    i = int.from_bytes(raw, byteorder='big', signed=True)
    i = i * 10 ** (-scale)
    return round(i, prec + 1)  # TODO: Round Up/Down?

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
        print(t)
        millis = t % 1000
        t = t / 1000
        hour = int(t/3600)
        t = t % 3600
        minute = int(t/60)
        t = t % 60
        second = int(t)
        return datetime.time(hour, minute, second, microsecond=int(millis/10))
    elif name == "timestamp":
        return datetime.datetime.fromtimestamp(value.timestamp.timestamp / 1000, datetime.timezone.utc)
    elif name == "interval":
        unit = value.interval.WhichOneof("unit")
        if unit == "milliseconds":
            return datetime.timedelta(milliseconds=value.interval.milliseconds)
        elif unit == "months":
            return interval.IntervalMonth(value.interval.months)
        else:
            raise Error("Unset or unknown interval unit")
    elif name == "string":
        return value.string.string
    elif name == "binary":
        return value.binary.binary
    elif name == "null":
        return None
    elif name == "list":
        return list(map(lambda v: proto2py(v), value.list.values))
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
