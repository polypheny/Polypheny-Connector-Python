import os
import sys

import pytest
import polypheny

@pytest.fixture(scope='function', autouse=True)
def add_cur(request, doctest_namespace):
    # Only create tables, if we run a doctest
    # In case of a doctest, request.function is None
    if request.function is not None:
        yield
        return

    if sys.platform == 'win32':
        con = polypheny.connect(('127.0.0.1', 20590), username='pa', password='', transport='plain')
    else:
        con = polypheny.connect()

    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS fruits')
    cur.execute('CREATE TABLE fruits(id INTEGER PRIMARY KEY, name VARCHAR(50)/*TEXT*/ NOT NULL)')
    cur.execute('INSERT INTO fruits (id, name) VALUES (1, ?)', ('Orange',))
    con.commit()
    cur.execute('DROP TABLE IF EXISTS demo')
    cur.close()

    def myprint(*objects, sep=' ', end='\n', file=None, flush=False):
        if len(objects) == 1 and isinstance(objects[0], dict):
            print('{' + ', '.join(map(lambda i: f'{repr(i[0])}: {repr(i[1])}', sorted(objects[0].items()))) + '}')
        else:
            print(*objects, sep=sep, end=end, file=file, flush=flush)

    doctest_namespace['con'] = con
    doctest_namespace['cur'] = con.cursor()
    doctest_namespace['print'] = myprint

    yield

    con.close()
