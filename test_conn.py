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

def test_commit(con):
    cur = con.cursor()

    cur.execute('SELECT COUNT(*) FROM emp')
    
    cur.fetchone()
    con.commit()
    cur.fetchone()

def test_commit_size(con):
    cur = con.cursor()

    cur.execute('SELECT COUNT(*) FROM emp', fetch_size=1)
    
    cur.fetchone()
    con.commit()
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

def test_fetch_closed_cursor(cur):
    with pytest.raises(polypheny.Error):
        cur.execute('SELECT  1')
        cur.close()
        cur.fetchone()

def test_invalid_creds():
    with pytest.raises(polypheny.Error):
        polypheny.connect('127.0.0.1', 20590, 'unknown', '')
