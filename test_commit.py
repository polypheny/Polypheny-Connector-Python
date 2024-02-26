import polypheny
import pytest

def test_commit():
    con = polypheny.connect('localhost', 20590, username='pa', password='')
    cur = con.cursor()
    cur.execute('CREATE TABLE abc(a INTEGER)')
    con.close()
    con = polypheny.connect('localhost', 20590, 'pa', '')
    cur = con.cursor()
    cur.execute('CREATE TABLE abc(a INTEGER)')
    cur.execute('CREATE TABLE abc(a INTEGER)')
