# Copyright 2024 The Polypheny Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
