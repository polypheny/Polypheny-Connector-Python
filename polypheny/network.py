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


class PolyphenyRestful(object):
    """Polypheny Restful class."""

    def __init__(
        self,
        host="127.0.0.1",
        port=8080,
        protocol="http",
        connection=None,
    ):
        self._host = host
        self._port = port
        self._protocol = protocol
        self._connection = connection
        #self._lock_token = Lock()

def request(
        self,
        url,
        body=None,
        method="post",
        client="polysql",
        _no_results=False,
        timeout=None,
        _include_retry_params=False,
    ):
        if body is None:
            body = {}
       