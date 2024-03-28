import os
import subprocess

import pytest
import polypheny

@pytest.fixture(scope='session', autouse=True)
def run_polypheny():
    jar = os.environ.get('POLYPHENY_JAR', '')

    process = None
    if jar != '':
        argv = ['java', '-jar', jar, '-resetCatalog', '-resetDocker']
        store = os.environ.get('POLYPHENY_DEFAULT_STORE', '')
        if store != '':
            argv.extend(['-defaultStore', store])
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, universal_newlines=True)
        lines = []
        while True:
            try:
                line = next(process.stdout).strip()
            except StopIteration:
                print(lines)
                break
            if line != '':
                lines.append(line)
            if 'Polypheny-DB successfully started' in line:
                break

    yield process

    if process is not None:
        process.terminate()

@pytest.fixture(scope='function', autouse=True)
def add_cur(run_polypheny, request, doctest_namespace):
    # Only create tables, if we run a doctest
    # In case of a doctest, request.function is None
    if request.function is not None:
        yield
        return

    con = polypheny.connect('127.0.0.1', 20590, username='pa', password='')
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
