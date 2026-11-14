<p align="center">
    <a href="https://polypheny.org/">
        <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/polypheny/Admin/master/Logo/logo-white-text_cropped.png">
            <img width='50%' alt="Light: 'Resume application project app icon' Dark: 'Resume application project app icon'" src="https://raw.githubusercontent.com/polypheny/Admin/master/Logo/logo-transparent_cropped.png">
        </picture>
    </a>    
</p> 


# Polypheny Connector for Python

This enables Python programs to access Polypheny databases, using an API that is compliant with the [Python Database API Specification v2.0 (PEP 249)](https://www.python.org/dev/peps/pep-0249/).


## Installation

The recommended way to install the Python Connector for Polypheny is via pip:
```bash
pip install polypheny
```

Alternatively, if you prefer to install the package manually you can also download the latest [release](https://github.com/polypheny/Polypheny-Connector-Python/releases/), extract the archive and install it manually:
```bash
cd /path/to/polyphney-connector-python-x.y.z/
python setup.py install
```

The connector uses Prism API 2.2 and requires a Polypheny server with Prism 2.x support.


## Getting Started

A few examples of the most common functionalities provided by the adapter:


```python3
import polypheny

# Connect to locally running Polypheny via UNIX sockets (on Linux, BSD and macOS)
con = polypheny.connect()

# Unencrypted over the network (all systems)
con = polypheny.connect(
  ('127.0.0.1', 20590),
  username='pa',
  password='',
  transport='plain',
)

# Get a cursor
cursor = con.cursor()

# Create a new table
cursor.execute("CREATE TABLE dummy (id INT NOT NULL, text VARCHAR(2), num INT, PRIMARY KEY(id))")

# Insert values into table
cursor.execute("INSERT INTO dummy VALUES (407 , 'de', 93)")
con.commit()

# Execute a query
cursor.execute("SELECT * from dummy")

print("\nRelational results from SQL")
for row in cursor:
    print("\t", row)

# Accessing data using MQL
cursor.executeany('mongo', 'db.dummy.find()', namespace='public')

print("\nDocument results from MQL (as Python dicts)")
for doc in cursor:
    print("\t", doc)

cursor.execute("DROP TABLE dummy")

# Close the connection
con.close()
```

An in-depth and more detailed documentation can be found [here](https://docs.polypheny.com/en/latest/drivers/python/overview).

## Tests
Run the tests with coverage report:
```
coverage run --source polypheny -m pytest && coverage report -m
```

### Document metadata integration tests

The document metadata suites cover the existing Prism `EntitiesRequest` /
`EntitiesResponse` exchange, all `Document` and `DocumentField` properties,
nested paths, heterogeneous and nullable values, sample JSON, collection
filters, empty namespaces, and relational metadata regression. The MongoDB
suite verifies every `DocumentIndex` property against real unique B-tree,
hash, nested-field, and wildcard indexes.

Use a Polypheny server that supports Prism 2.2 and document metadata. Install
the test requirements to get the released Prism API package.

```bash
python -m pip install -r requirements.txt
python -m pytest -v tests/document_metadata.py
```

The suites use plain Prism at `127.0.0.1:20590`, user `pa`, and an empty
password. Override these with `POLYPHENY_PRISM_HOST`, `POLYPHENY_PRISM_PORT`,
`POLYPHENY_PRISM_USER`, and `POLYPHENY_PRISM_PASSWORD` when needed.

The index tests also require a MongoDB replica set, reachable by both the tests
and Polypheny at `127.0.0.1:27017` by default.
Set `POLYPHENY_MONGO_HOST` and `POLYPHENY_MONGO_PORT` for another endpoint.
The tests create a private MongoDB database and a temporary Polypheny source
adapter, then remove both. Explicit runs fail if a required service is missing.

```bash
python -m pip install pymongo==4.10.1
python -m pytest -v tests/document_metadata_mongo.py
```

The `Document metadata integration` workflow runs both suites. Its manual
trigger accepts a `db_ref` for testing a different server build. Set the
`POLYPHENY_DB_REF` repository Actions variable to use the same server revision
in both integration workflows.


## Roadmap
See the [open issues](https://github.com/polypheny/Polypheny-DB/labels/A-python) for a list of proposed features (and known issues).


## Contributing
We highly welcome your contributions to the _Polypheny Connector for Python_. If you would like to contribute, please fork the repository and submit your changes as a pull request. Please consult our [Admin Repository](https://github.com/polypheny/Admin) and our [Website](https://polypheny.org) for guidelines and additional information.

Please note that we have a [code of conduct](https://github.com/polypheny/Admin/blob/master/CODE_OF_CONDUCT.md). Please follow it in all your interactions with the project. 


## License
The Apache 2.0 License
