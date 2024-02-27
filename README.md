WORK IN PROGRESS
================

This is the **work in progress** Python driver for Polypheny that uses the new
gRPC based interface.

## Usage

Install the dependencies
```
pip install -r requirements.txt
```

Generate the Python code:
```
python -m grpc_tools.protoc -I proto --python_out . proto/*
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

Run the test with coverage report:
```
coverage run --source polypheny -m pytest && coverage report -m
```