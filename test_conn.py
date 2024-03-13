import polypheny
import pytest
import time

from test_helper import con, cur

# Heartbeat: isActive is only set to true, if the checkConnection
# call is made --- not for any of the others.  This would test
# that an active client would be kicked
#def test_heartbeat(cur):
#    while True:
#        cur.execute("SELECT 1");
#        for row in cur:
#            assert row[0] == 1
#        time.sleep(0.3)

# tests the con fixture helper works
def test_conn(con):
    pass

def test_commit(con):
    cur = con.cursor()

    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    cur.execute('INSERT INTO t(id, a) VALUES (1, 2)')
    con.commit()

    cur.execute('SELECT a FROM t')
    assert cur.fetchone()[0] == 2

def test_rollback(con):
    cur = con.cursor()

    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    cur.execute('INSERT INTO t(id, a) VALUES (1, 2)')
    con.rollback()

    cur.execute('SELECT a FROM t')
    assert cur.fetchone() is None

def test_fetch_size(con):
    cur = con.cursor()

    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    for i in range(30):
        cur.execute('INSERT INTO t(id, a) VALUES (?, ?)', (i, i))
    con.commit()

    for i in (1, 5, 30, 60):
        cur.execute('SELECT id, a FROM t', fetch_size=i)
        assert len(cur.fetchall()) == 30

def test_fetch_insert(cur):
    cur.execute('DROP TABLE IF EXISTS t')
    cur.execute('CREATE TABLE t(id INTEGER PRIMARY KEY, a INTEGER)')
    cur.execute('INSERT INTO t(id, a) VALUES (1, 1)')
    with pytest.raises(polypheny.Error):
        cur.fetchone()

def test_error_on_closed_con(con):
    con.close()
    with pytest.raises(polypheny.ProgrammingError):
        con.cursor()
    with pytest.raises(polypheny.ProgrammingError):
        con.commit()
    with pytest.raises(polypheny.ProgrammingError):
        con.rollback()
    # Raises no exception
    con.close()

def test_cursor_autoclose(con):
    cur = con.cursor()
    cur.execute('SELECT 1')
    con.close()

def test_execute_wrongparams(cur):
    with pytest.raises(polypheny.Error):
        cur.execute('SELECT ?', 5)

def test_execute_closed_cursor(cur):
    with pytest.raises(polypheny.Error):
        cur.close()
        cur.executeany('mql', 'db.abc.find()')

def test_fetch_closed_cursor(cur):
    with pytest.raises(polypheny.Error):
        cur.execute('SELECT  1')
        cur.close()
        cur.fetchone()

def test_invalid_creds():
    with pytest.raises(polypheny.Error):
        polypheny.connect('127.0.0.1', 20590, 'unknown', '')

def test_invalid_version():
    import polypheny.rpc as rpc
    major = rpc.POLYPHENY_API_MAJOR
    with pytest.raises(polypheny.Error):
        rpc.POLYPHENY_API_MAJOR = 1
        polypheny.connect('127.0.0.1', 20590, 'pa', '')
    rpc.POLYPHENY_API_MAJOR = major
