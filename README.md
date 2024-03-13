WORK IN PROGRESS
================

This is the **work in progress** Python driver for Polypheny that uses the new
gRPC based interface.

## Usage

Install the dependencies
```
pip install -r requirements.txt
```

Install the package
```
pip install .
```

Simple example:

```python3
import polypheny

con = polypheny.connect('localhost', 20590, username='pa', password='')
cur = con.cursor()

cur.execute('SELECT * FROM emps')
for f in cur:
	print(f)
```

## Tests
Run the tests with coverage report:
```
coverage run --source polypheny -m pytest && coverage report -m
```