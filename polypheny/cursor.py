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
from polypheny.errors import *
from polypheny.types import TypeHelper
from polypheny.avatica.protobuf import common_pb2

from typing import (
    Any,
    Dict,
    Tuple,
    Type,
    Union,
)

__all__ = ['PolyphenyCursor']

# Default configs, tuple of default variable and accepted types
DEFAULT_CURSOR_CONFIGURATION: Dict[str, Tuple[Any, Union[Type, Tuple[Type, ...]]]] = {
    "language": ("sql", str),  # standard could be extended with MQL. CQL, Cypher etc.
}

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

    def __del__(self):
        if not self._connection._closed and not self._closed:
            self.close()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        if not self._closed:
            self.close()


    def __iter__(self):
        return self


    def __next__(self):
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row

    next = __next__



    def close(self):
        """Closes the cursor.
        No further operations are allowed once the cursor is closed.

        If the cursor is used in a ``with`` statement, this method will
        be automatically called at the end of the ``with`` block.
        """
        if self._closed:
            raise ProgrammingError('the cursor is already closed')

        if self._id is not None:
            self._connection._client.close_statement(self._connection._id, self._id)
            self._id = None

        self._signature = None
        self._column_data_types = []
        self._frame = None
        self._pos = None
        self._closed = True



    @property
    def is_closed(self):
        """Read-only attribute specifying if the cursor is closed or not."""
        return self._closed



    def execute(self, command, parameters=None):
        if self._closed:
            raise ProgrammingError('the cursor is already closed')

        command = command.strip(" \t\n\r") if command else None
        logger.debug("Executing command: ", command)

        if not command:
            logger.warning("execute: no query is given to execute")
        
        if parameters is None:
            if self._id is None:
                self._set_id(self._connection._client.create_statement(self._connection._id))
            results = self._connection._client.prepare_and_execute(
                self._connection._id, self._id,
                command, first_frame_max_size=self.itersize)

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



    def executemany(self, operation, seq_of_parameters):
        if self._closed:
            raise ProgrammingError('the cursor is already closed')

        self._updatecount = -1
        self._set_frame(None)
        statement = self._connection._client.prepare(
            self._connection._id, operation, max_rows_total=0)

        self._set_id(statement.id)
        self._set_signature(statement.signature)
        
        for parameters in seq_of_parameters:
            self._connection._client.execute(
                self._connection._id, self._id,
                statement.signature, self._transform_parameters(parameters),
                first_frame_max_size=0)



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


    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize

        rows = []

        while size > 0:
            row = self.fetchone()

            if row is None:
                break
            rows.append(row)
            size -= 1

        return rows



    def fetchall(self):
        rows = []

        while True:
            row = self.fetchone()

            if row is None:
                break
            rows.append(row)

        return rows



    def _set_signature(self, signature):    
        self._signature = signature
        self._column_data_types = []
        self._parameter_data_types = []
        if signature is None:
            return

        for column in signature.columns:
            dtype = TypeHelper.from_class(column.column_class_name)
            self._column_data_types.append(dtype)

        '''for parameter in signature.parameters:
            dtype = TypeHelper.from_class(parameter.class_name)
            self._parameter_data_types.append(dtype)
        ''' 
        



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
                
            # First Frame is currently skipped due to BUG described in:
            # https://github.com/polypheny/Polypheny-DB/blame/0a51f433440e4e6086c66da19e5f4f85cac1995e/jdbc-interface/src/main/java/org/polypheny/db/jdbc/DbmsMeta.java#L1293
            # Therefore we have to immediately execute another feth operation
            if result.HasField('first_frame'):
                frame = result.first_frame
            else:
                # Needed for DQL only (SELECT, etc.)
                if result.HasField('signature'):
                    frame = self._connection._client.fetch(
                        self._connection._id, self._id,
                        offset=0, frame_max_size=self.itersize)
                
                # For Non-DQL (DDL,DML,etc.)
                else:
                    frame = None

            self._set_signature(result.signature if result.HasField('signature') else None)
            self._set_frame(frame)

            self._updatecount = result.update_count



    def _transform_row(self, row):
        """Transforms a Row into Python values.
        :param row:
            A ``common_pb2.Row`` object.
        :returns:
            A list of values casted into the correct Python types.
        :raises:
            NotImplementedError
        """
        tmp_row = []

        for i, column in enumerate(row.value):

            if column.has_array_value:
                raise NotImplementedError('array types are not supported')
            elif column.scalar_value.null:
                tmp_row.append(None)
            else:
                field_name, rep, mutate_to, cast_from = self._column_data_types[i]

                # get the value from the field_name
                value = getattr(column.scalar_value, field_name)

                # cast the value
                if cast_from is not None:
                    value = cast_from(value)

                tmp_row.append(value)

        return tmp_row


    def _transform_parameters(self, parameters):
        typed_parameters = []
        for value, data_type in zip(parameters, self._parameter_data_types):
            field_name, rep, mutate_to, cast_from = data_type
            typed_value = common_pb2.TypedValue()

            if value is None:
                typed_value.null = True
                typed_value.type = common_pb2.NULL
            else:
                typed_value.null = False

                # use the mutator function
                if mutate_to is not None:
                    value = mutate_to(value)

                typed_value.type = rep
                setattr(typed_value, field_name, value)

            typed_parameters.append(typed_value)
        return typed_parameters

    def _set_id(self, id):
        if self._id is not None and self._id != id:
            self._connection._client.close_statement(self._connection._id, self._id)
        self._id = id
