#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2021 The Polypheny Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#  http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


# According to https://www.python.org/dev/peps/pep-0249/#paramstyle
SUPPORTED_PARAMSTYLES = {
    "qmark",
    "numeric",
    "named",
    "format",
    "pyformat",
}

class PolyphenyConnection(object):
    """Implementation of the connection object for Polypheny-DB.
    Use connect(..) to get the object.

    """