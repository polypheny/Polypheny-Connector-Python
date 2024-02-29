import polypheny
import pytest

@pytest.fixture
def con():
    con = polypheny.connect('127.0.0.1', 20590, username='pa', password='')
    yield con
    con.close()

@pytest.fixture
def cur():
    con = polypheny.connect('127.0.0.1', 20590, username='pa', password='')
    yield con.cursor()
    con.close()

@pytest.fixture
def cur_with_data():
    con = polypheny.connect('127.0.0.1', 20590, username='pa', password='')
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS customers')
    cur.execute("""
        CREATE TABLE customers(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            year_joined INTEGER NOT NULL
        )""")
    cur.executemany(
        'INSERT INTO customers(id, name, year_joined) VALUES (?, ?, ?)',
        [(1, 'Maria', 2012),
         (2, 'Daniel', 2020),
         (3, 'Peter', 2001),
         (4, 'Anna', 2001),
         (5, 'Thomas', 2004),
         (6, 'Andreas', 2014),
         (7, 'Michael', 2010)]
    )
    con.commit()

    yield cur

    cur.execute('DROP TABLE customers')

    con.close()
