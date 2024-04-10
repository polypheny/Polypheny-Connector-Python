import os
import sys

import polypheny

def unix_connect():
    con = polypheny.connect(os.path.expanduser("~/.polypheny/polypheny-prism.sock"), username='pa', password='', transport='unix')
    con.close()

def test_connect_unix():
    if sys.platform == 'win32':  # TODO: Once this works the documentation needs to be updated
        with pytest.raises(AttributeError):
            unix_connect()
    else:
        unix_connect()
