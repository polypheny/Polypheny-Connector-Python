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

"""Various constants."""

import platform
import sys

from .version import VERSION

POLYPHENY_CONNECTOR_VERSION = ".".join(str(v) for v in VERSION[0:3])
PYTHON_VERSION = ".".join(str(v) for v in sys.version_info[:3])
OPERATING_SYSTEM = platform.system()
PLATFORM = platform.platform()

CLIENT_NAME = "PolyphenyPythonConnector"  # don't change!
CLIENT_VERSION = ".".join([str(v) for v in VERSION[:3]])