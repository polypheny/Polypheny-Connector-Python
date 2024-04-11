import polypheny

def test_connect_plain():
    con = polypheny.connect(('127.0.0.1', 20590), username='pa', password='', transport='plain')
    con.close()
