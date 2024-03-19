import datetime

from polyprism import value_pb2


# See ProtoValueDeserializer
def py2proto(value, v=None):
    if v is None:
        v = value_pb2.ProtoValue()
    if type(value) == bool:
        # v.type = value_pb2.ProtoValue.ProtoValueType.BOOLEAN
        v.boolean.boolean = value
    elif type(value) == int:
        if -2 ** 31 <= value <= 2 ** 31 - 1:
            # v.type = value_pb2.ProtoValue.ProtoValueType.INTEGER
            v.integer.integer = value
        elif -2 ** 63 <= value <= 2 ** 63 - 1:
            # v.type = value_pb2.ProtoValue.ProtoValueType.LONG
            v.long.long = value
        else:
            # v.type = value_pb2.ProtoValue.ProtoValueType.BIG_DECIMAL
            n = ((value.bit_length() - 1) // 8) + 1  # TODO: Does this work for negative numbers?
            v.big_decimal.unscaled_value = value.to_bytes(n, byteorder='big', signed=True)
            v.big_decimal.scale = 0
            v.big_decimal.precision = 0
            print(v.big_decimal)
    elif type(value) == bytes:
        # v.type = value_pb2.ProtoValue.ProtoValueType.BINARY
        v.binary.binary = value
    elif type(value) == datetime.date:
        diff = value - datetime.date(1970, 1, 1)
        v.date.date = diff.days
    elif type(value) == float:
        # v.type = value_pb2.ProtoValue.ProtoValueType.DOUBLE
        v.double.double = value
        # TODO: Use BigDecimal as well?
    elif type(value) == str:
        # v.type = value_pb2.ProtoValue.ProtoValueType.VARCHAR
        v.string.string = value
    elif type(value) == datetime.time:
        v.time.time = (value.hour * 3600 + value.minute * 60 + value.second) * 1000 + value.microsecond * 10
    elif type(value) == datetime.datetime:
        v.timestamp.timestamp = int(value.timestamp() * 1000)
    elif value is None:
        # v.type = value_pb2.ProtoValue.ProtoValueType.NULL
        v.null.CopyFrom(value_pb2.ProtoNull())
    elif type(value) == list:
        # v.type = value_pb2.ProtoValue.ProtoValueType.LIST
        for element in value:
            v.list.values.append(py2proto(element))
    elif type(value) == dict:  # experiment to test the server with unset values
        pass
    else:
        raise NotImplementedError

    return v


def proto2py(value):
    name = value.WhichOneof("value")
    assert name is not None
    if name == "boolean":
        return value.boolean.boolean
    elif name == "integer":
        return value.integer.integer
    elif name == "long":
        return value.long.long
    elif name == "binary":
        return value.binary.binary
    elif name == "date":
        return datetime.date(1970, 1, 1) + datetime.timedelta(days=value.date.date)
    elif name == "double":
        return value.double.double
    elif name == "float":
        return value.float.float
    elif name == "string":
        return value.string.string
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
    elif name == "null":
        return None
    elif name == "big_decimal":
        # print(value)
        raw = value.big_decimal.unscaled_value
        scale = value.big_decimal.scale
        prec = value.big_decimal.precision

        if scale > (2 ** 31) - 1:
            scale = scale - 2 ** 32

        i = int.from_bytes(raw, byteorder='big', signed=True)
        # print(f'i: {i}')
        i = i * 10 ** (-scale)
        # print(f'i: {i} {2**77}')
        return round(i, prec + 1)  # TODO: Round Up/Down?
    elif name == "interval":
        raise NotImplementedError()
    elif name == "user_defined_type":
        raise NotImplementedError()
    elif name == "file":
        raise NotImplementedError()
    elif name == "list":
        return list(map(lambda v: proto2py(v), value.list.values))
    elif name == "map":
        raise NotImplementedError()
    elif name == "document":
        res = {}
        for entry in value.document.entries:
            k = proto2py(entry.key)
            assert isinstance(k, str)  # TODO: Correct?
            v = proto2py(entry.value)
            res[k] = v
        return res
    elif name == "node":
        raise NotImplementedError()
    elif name == "edge":
        raise NotImplementedError()
    elif name == "path":
        raise NotImplementedError()
    elif name == "graph":
        raise NotImplementedError()
    elif name == "row_id":
        raise NotImplementedError()
    else:
        raise RuntimeError("Unhandled value type")
