

<a href="https://polypheny.org/">
    <img align="right" width="200" height="200" src="https://polypheny.org/community/logo/logo.png" alt="Resume application project app icon">
</a>




# Polypheny Connector for Python

This enables Python programs to access Polypheny databases, using an API that is compliant with the [Python Database API Specification v2.0 (PEP 249)](https://www.python.org/dev/peps/pep-0249/).


### Installation

Installing the python connector for Polypheny is as simple as calling:

```bash
pip install polypheny
```

Alternativiely if you don't want to install the package directly from [PyPi](https://pypi.org/project/polypheny).
You can also download the latest [release](https://github.com/polypheny/Polypheny-Connector-Python/releases/), extract the archive and install it manually:
```bash
cd /path/to/polyphney-connector-python-x.y.z/
python setup.py install
```



## Getting Started

A few examples of the most common functionalities provided by the adapter:


```python
import polypheny

# Connect to server
connection = polypheny.connect('localhost', 20591, user='pa', password='')
# Get a cursor
cursor = connection.cursor()

# Create a new Table
cursor.execute("CREATE TABLE dummy (id INT NOT NULL, text VARCHAR(2), num INT, PRIMARY KEY(id))")

# Insert Values into table
cursor.execute("INSERT INTO dummy VALUES (407 , 'de', 93)")

# Execute a query
cursor.execute("SELECT * from dummy")
result = cursor.fetchall()

connection.close()
```
An in-depth and more detailed documentation can be found [here]()




## Roadmap
See the [open issues](https://github.com/polypheny/Polypheny-DB/labels/A-python) for a list of proposed features (and known issues).


## Contributing
We highly welcome your contributions to the _Polypheny Connector for Python_. If you would like to contribute, please fork the repository and submit your changes as a pull request. Please consult our [Admin Repository](https://github.com/polypheny/Admin) and our [Website](https://polypheny.org) for guidelines and additional information.

Please note that we have a [code of conduct](https://github.com/polypheny/Admin/blob/master/CODE_OF_CONDUCT.md). Please follow it in all your interactions with the project. 


## Credits
This work was influenced by the following projects:

* [python-phoenixdb](https://github.com/lalinsky/python-phoenixdb)
* [snowflake-connector-python](https://github.com/lalinsky/python-phoenixdb)


## License
The Apache 2.0 License
