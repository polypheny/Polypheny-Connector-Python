import os
import subprocess

import pytest
import polypheny

@pytest.fixture(scope='session', autouse=True)
def run_polypheny():
    jar = os.environ.get('POLYPHENY_JAR', '')

    process = None
    if jar != '':
        process = subprocess.Popen(['java', '-jar', jar, '-resetCatalog'], stdout=subprocess.PIPE, universal_newlines=True)
        while True:
            line = next(process.stdout)
            if 'Polypheny-DB successfully started' in line:
                break

    yield process

    if process is not None:
        process.terminate()

@pytest.fixture(scope='session', autouse=True)
def add_cur(run_polypheny, doctest_namespace):
    con = polypheny.connect('127.0.0.1', 20590, username='pa', password='')
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS fruits')
    cur.execute('CREATE TABLE fruits(id INTEGER PRIMARY KEY, name VARCHAR(50)/*TEXT*/ NOT NULL)')
    cur.execute('INSERT INTO fruits (id, name) VALUES (1, ?)', ('Orange',))
    con.commit()
    cur.execute('DROP TABLE IF EXISTS demo')
    cur.close()
    doctest_namespace['con'] = con
    doctest_namespace['cur'] = con.cursor()
