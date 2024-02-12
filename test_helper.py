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
