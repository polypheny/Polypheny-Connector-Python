import os

import polypheny

def test_connect_unix():
    con = polypheny.connect(os.path.expanduser("~/.polypheny/polypheny-prism.sock"), username='pa', password='', transport='unix')
    con.close()
