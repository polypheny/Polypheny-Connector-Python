import os
import sys

import pytest

import polypheny

def unix_connect(args):
    if args:
        con = polypheny.connect(os.path.expanduser("~/.polypheny/polypheny-prism.sock"), username='pa', password='', transport='unix')
    else:
        con = polypheny.connect()
    con.close()

def test_connect_unix():
    if sys.platform == 'win32':  # TODO: Once this works the documentation needs to be updated
        with pytest.raises(AttributeError):
            unix_connect(False)
        with pytest.raises(AttributeError):
            unix_connect(True)
    else:
        unix_connect(True)
        unix_connect(False)
