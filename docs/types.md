# Value Types

The Prism value type sent by the server determines the Python result. The
[official data type guide](https://docs.polypheny.com/en/latest/concepts/data-types)
describes database types.

## Polypheny to Python

| Prism value | Python result |
| --- | --- |
| Boolean | `bool` |
| 32-bit or 64-bit integer | `int` |
| Big decimal | `decimal.Decimal`, including integral decimal values |
| Float or double | `float` |
| Date | `datetime.date` |
| Time | `datetime.time` with millisecond precision |
| Timestamp | A timezone-aware `datetime.datetime` in UTC |
| String | `str` |
| Binary | `bytes` |
| Null | `None` |
| List | `list` with recursively converted elements |
| Document | `dict` with string keys and recursively converted values |
| Interval | {doc}`interval` value |
| Graph node or edge | `dict` with identity, labels, and properties |
| Graph path or graph value | `dict` with `nodes` and `edges` lists |

SQL `DECIMAL` values are decoded as `Decimal`. Relational rows are lists of
values in column order. Nested values in documents, lists, and graph properties
are decoded recursively. See {doc}`graph` for graph dictionary keys and result
formats.

## Python to Polypheny

| Parameter value | Prism representation |
| --- | --- |
| `bool` | Boolean |
| `int` | 32-bit integer or 64-bit integer when in range, then big decimal |
| `float` | Double |
| Finite `decimal.Decimal` | Big decimal |
| `datetime.date` | Days since the Unix epoch |
| `datetime.time` | Time of day. Use whole seconds for parameters. |
| `datetime.datetime` | Unix epoch milliseconds. Naive datetimes use the process's local timezone. |
| `str` | String |
| `bytes` | Binary |
| `None` | Null |
| Nonempty `list` | List with recursively serialized elements |

Use a timezone-aware datetime for consistent timestamp parameters across hosts.
Use whole seconds for time parameters because the connector currently converts
fractional seconds incorrectly.

A list or tuple passed as `params` contains positional arguments. For a single
array parameter, pass a nonempty list as one element, such as `([1, 2, 3],)`.
A dictionary passed as `params` maps parameter names to values. Use
language-specific expressions for document and interval values and Cypher
statements to create or modify graph structures.

[Official Python type conversion guide](https://docs.polypheny.com/en/latest/drivers/python/types)
