<!--<p align="center">
<picture>
  <source 
    srcset="https://raw.githubusercontent.com/polypheny/Admin/master/Logo/logo-white-text.png" 
    media="(prefers-color-scheme: dark)">
  <a href="https://polypheny.org/">
    <img align="center" width="300" height="300" src="https://raw.githubusercontent.com/polypheny/Admin/master/Logo/logo-transparent.png">
   </a>
</picture>
</p>
-->

 <a href="https://polypheny.org/">
    <img align="center" width="300" height="300" src="https://raw.githubusercontent.com/polypheny/Admin/master/Logo/logo-transparent.png">
</a>


# Polypheny Connector for Python

This enables Python programs to access Polypheny databases, using an API that is compliant with the [Python Database API Specification v2.0 (PEP 249)](https://www.python.org/dev/peps/pep-0249/).


### Installation

The recommended way to install the Python Connector for Polypheny is via pip:
```bash
pip install polypheny
```

Alternatively, if you prefer to install the package manually you can also download the latest [release](https://github.com/polypheny/Polypheny-Connector-Python/releases/), extract the archive and install it manually:
```bash
cd /path/to/polyphney-connector-python-x.y.z/
python setup.py install
```



## Getting Started

A few examples of the most common functionalities provided by the adapter:


```python
import polypheny

# Connect to Polypheny
connection = polypheny.connect('localhost', 20591, user='pa', password='')

# Get a cursor
cursor = connection.cursor()

# Create a new table
cursor.execute("CREATE TABLE dummy (id INT NOT NULL, text VARCHAR(2), num INT, PRIMARY KEY(id))")

# Insert values into table
cursor.execute("INSERT INTO dummy VALUES (407 , 'de', 93)")
connection.commit()

# Execute a query
cursor.execute("SELECT * from dummy")
result = cursor.fetchall()

# Close the connection
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
* [snowflake-connector-python](https://github.com/snowflakedb/snowflake-connector-python)


## License
The Apache 2.0 License
