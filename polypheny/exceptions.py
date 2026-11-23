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

import re as _re


class Warning(Exception):
    pass


class Error(Exception):
    def __init__(self, *args, sqlstate=None, errorcode=None):
        super().__init__(*args)
        self.sqlstate = sqlstate
        self.errorcode = errorcode


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class DataError(DatabaseError):
    pass


class OperationalError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class InternalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass


_SQLSTATE_CLASSES = {
    "08": OperationalError,
    "28": OperationalError,
    "40": OperationalError,
    "53": OperationalError,
    "57": OperationalError,
    "58": OperationalError,
    "0A": NotSupportedError,
    "22": DataError,
    "23": IntegrityError,
    "24": InternalError,
    "25": InternalError,
    "26": InternalError,
    "2D": InternalError,
    "XX": InternalError,
    "I9": InternalError,
    "3F": ProgrammingError,
    "42": ProgrammingError,
}


def _server_error(response):
    details = response.details
    sqlstate = details.state if _re.fullmatch(r"[A-Z0-9]{5}", details.state) else None
    errorcode = details.error_code if details.HasField("error_code") else None
    error_type = _SQLSTATE_CLASSES.get(sqlstate[:2], DatabaseError) if sqlstate else DatabaseError
    return error_type(response.message, sqlstate=sqlstate, errorcode=errorcode)
