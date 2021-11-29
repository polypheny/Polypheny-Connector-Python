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

import logging as logger
import requests
from polypheny.errors import *

class PolyphenyCursor:
    """Implementation of database cursor object that is returned from Connection.cursor() method.

     You should not construct this object manually!
    """

    arraysize = 1
    """
    Read/write attribute specifying the number of rows to fetch
    at a time with :meth:`fetchmany`. It defaults to 1 meaning to
    fetch a single row at a time.
    """

    itersize = 2000

    def __init__(self, connection, id=None):
        self._connection = connection
        self._id = id
        self._signature = None
        self._column_data_types = []
        self._frame = None
        self._pos = None
        self._closed = False
        self.arraysize = self.__class__.arraysize
        self.itersize = self.__class__.itersize
        self._updatecount = -1



    

    def execute(self, command, parameters=None):
        if self._closed:
            raise ProgrammingError('the cursor is already closed')

        command = command.strip(" \t\n\r") if command else None
        print("Command: ", command)
        if not command:
            logger.warning("execute: no query is given to execute")
        
        if parameters is None:
            if self._id is None:
                self._set_id(self._connection._client.create_statement(self._connection._id))
            results = self._connection._client.prepare_and_execute(
                self._connection._id, self._id,
                command, first_frame_max_size=self.itersize)
            self._process_results(results)
        else:
            statement = self._connection._client.prepare(
                self._connection._id, command)
            self._set_id(statement.id)
            self._set_signature(statement.signature)

            results = self._connection._client.execute(
                self._connection._id, self._id,
                statement.signature, self._transform_parameters(parameters),
                first_frame_max_size=self.itersize)
            self._process_results(results)



    def fetchone(self):
        if self._frame is None:
            raise ProgrammingError('no select statement was executed')
        if self._pos is None:
            return None
        rows = self._frame.rows
        row = self._transform_row(rows[self._pos])
        self._pos += 1
        if self._pos >= len(rows):
            self._pos = None
            if not self._frame.done:
                self._fetch_next_frame()
        return row



    def _set_signature(self, signature):    
        self._signature = signature
        self._column_data_types = []
        self._parameter_data_types = []
        if signature is None:
            return

        """        for column in signature.columns:
            dtype = TypeHelper.from_class(column.column_class_name)
            self._column_data_types.append(dtype)

        for parameter in signature.parameters:
            dtype = TypeHelper.from_class(parameter.class_name)
            self._parameter_data_types.append(dtype)
        """


    def _set_frame(self, frame):
        self._frame = frame
        self._pos = None

        if frame is not None:
            if frame.rows:
                self._pos = 0
            elif not frame.done:
                raise InternalError('got an empty frame, but the statement is not done yet')

    def _fetch_next_frame(self):
        offset = self._frame.offset + len(self._frame.rows)
        frame = self._connection._client.fetch(
            self._connection._id, self._id,
            offset=offset, frame_max_size=self.itersize)
        self._set_frame(frame)

    def _process_results(self, results):
        if results:
            result = results[0]
            if result.own_statement:
                self._set_id(result.statement_id)
            self._set_signature(result.signature if result.HasField('signature') else None)
            self._set_frame(result.first_frame if result.HasField('first_frame') else None)
            self._updatecount = result.update_count

    def _set_id(self, id):
        if self._id is not None and self._id != id:
            self._connection._client.close_statement(self._connection._id, self._id)
        self._id = id
