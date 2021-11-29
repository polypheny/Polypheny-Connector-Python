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

import os

CLIENT_PROOF_SIZE = 32
CLIENT_KEY_SIZE = 64

class AuthManager(object):

    def __init__(self, connection, user, password):
        self.connection = connection
        self.user = user
        self.password = password

        self.method = b"SCRAMSHA256"
        self.client_key = os.urandom(CLIENT_KEY_SIZE)
        self.client_proof = None