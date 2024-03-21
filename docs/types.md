# Types

This page gives an overview how values are converted between Polypheny
and Python.  For more information of the Polypheny Types check
[this](https://docs.polypheny.com/en/latest/concepts/data-types) page.

| Python Type | Polypheny Type | Notes |
|-------------|----------------|-------|
|{py:class}`int`|BIGINT||
| {py:class}`bool` | BOOLEAN ||
|{py:class}`datetime.date`|DATE||
|{py:class}`int` or {py:class}`float`|DECIMAL| Python type depends on if `DECIMAL` is a whole number or not.|
|{py:class}`float`|DOUBLE||
|{py:class}`int`|INTEGER||
|{py:class}`float`|REAL||
|{py:class}`int`|SMALLINT||
|{py:class}`str`|TEXT||
|{py:class}`datetime.time`|TIME||
|{py:class}`datetime.datetime`|TIMESTAMP|When converting a `TIMESTAMP` to {py:class}`datetime.datetime` the timezone is always set to UTC.|
|{py:class}`int`|TINYINT||
|{py:class}`str`|VARCHAR||

## Special types
| Python Type | Special Type | Notes |
|-------------|----------------|-------|
|{py:class}`list`|Arrays||
|{py:class}`dict`|Documents||
|{py:class}`bytes`|AUDIO, FILE, IMAGE, VIDEO||

## Intervals
To learn more about intervals see {doc}`interval`.
