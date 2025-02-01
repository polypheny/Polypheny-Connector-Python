# Types

This page gives an overview how values are converted between Polypheny
and Python.  For more information of the Polypheny Types check
[this](https://docs.polypheny.com/en/latest/concepts/data-types) page.

## Polypheny to Python

| Polypheny                 | Python                               | Notes                                                                                             |
|---------------------------|--------------------------------------|---------------------------------------------------------------------------------------------------|
| BIGINT                    | {py:class}`int`                      |                                                                                                   |
| BOOLEAN                   | {py:class}`bool`                     |                                                                                                   |
| DATE                      | {py:class}`datetime.date`            |                                                                                                   |
| DECIMAL                   | {py:class}`int` or {py:class}`float` | Python type depends on if `DECIMAL` is a whole number or not.                                     |
| DOUBLE                    | {py:class}`float`                    |                                                                                                   |
| INTEGER                   | {py:class}`int`                      |                                                                                                   |
| REAL                      | {py:class}`float`                    |                                                                                                   |
| SMALLINT                  | {py:class}`int`                      |                                                                                                   |
| TEXT                      | {py:class}`str`                      |                                                                                                   |
| TIME                      | {py:class}`datetime.time`            |                                                                                                   |
| TIMESTAMP                 | {py:class}`datetime.datetime`        | When converting a `TIMESTAMP` to {py:class}`datetime.datetime` the timezone is always set to UTC. |
| TINYINT                   | {py:class}`int`                      |                                                                                                   |
| VARCHAR                   | {py:class}`str`                      |                                                                                                   |
| AUDIO, FILE, IMAGE, VIDEO | {py:class}`bytes`                    |                                                                                                   |

### Special types

| Special Type              | Python Type       | Notes |
|---------------------------|-------------------|-------|
| Arrays                    | {py:class}`list`  |       |
| Documents                 | {py:class}`dict`  |       |

### Intervals
To learn more about intervals see {doc}`interval`.

## Python to Polypheny

The following types can be serialized by the Python driver:

{py:class}`bool`, {py:class}`bytes`, {py:class}`datetime.date`,
{py:class}`datetime.datetime`, {py:class}`datetime.time`,
{py:class}`float`, {py:class}`int`, {py:class}`list` and
{py:class}`str`.

