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

from contextlib import suppress
from typing import List, Any

from org.polypheny.prism import graph_frame_pb2, relational_frame_pb2, value_pb2
from polypheny import rpc
from polypheny.exceptions import Error, InterfaceError, NotSupportedError, ProgrammingError
from polypheny.serialize import proto2py, proto_graph_element2py


class Connection:
    def __init__(self, address, username, password, transport, kwargs):
        self.cursors = set()
        self.con = None  # Needed so destructor works

        self.con = rpc.Connection(address, transport, kwargs)
        try:
            resp = self.con.connect(username, password, False)
            if not resp.is_compatible:
                raise InterfaceError(
                    f"Client ({rpc.POLYPHENY_API_MAJOR}.{rpc.POLYPHENY_API_MINOR}) is incompatible with Server version ({resp.major_api_version}.{resp.minor_api_version})")
        except Error:
            self.con.abort()
            self.con = None
            raise

    def cursor(self):
        if self.con is None:
            raise ProgrammingError('Connection is closed')
        cur = Cursor(self)
        self.cursors.add(cur)
        return cur

    def commit(self):
        """
        .. Note::

            Performing a DDL automatically commits the transaction.
            See the :py:meth:`rollback` method for an example what this
            means.

        """
        if self.con is None:
            raise ProgrammingError('Connection is closed')
        self.con.commit()

    def rollback(self):
        """
        .. Note::

           It is not possible to rollback DDLs, as they commit automatically.

           >>> cur.execute('SELECT * FROM fruits WHERE name = ?', ('Pear',))
           >>> cur.fetchone()
           >>> cur.execute('INSERT INTO fruits (id, name) VALUES (2, ?)', ('Pear',))
           >>> cur.execute('CREATE TABLE demo(id INTEGER PRIMARY KEY)')
           >>> # Implicit commit here because of DDL
           >>> con.rollback()
           >>> cur.execute('SELECT name FROM fruits WHERE name = ?', ('Pear',))
           >>> print(cur.fetchone())
           ['Pear']
        """
        if self.con is None:
            raise ProgrammingError('Connection is closed')
        self.con.rollback()

    def __del__(self):
        with suppress(Error):
            self.close()

    def close(self):
        if self.con is None:
            return

        try:
            for cur in list(self.cursors):
                with suppress(Error):
                    cur.close()
            if self.con.con is not None:
                self.rollback()
        finally:
            self.con.close()
            self.con = None


class ResultCursor:
    _FRAME_ITEMS = {
        'relational_frame': 'rows',
        'document_frame': 'documents',
        'graph_frame': 'element',
    }

    def __init__(self, con, statement_id, frame, fetch_size):
        self.con = con
        self.statement_id = statement_id
        self.closed = False
        self.frame = frame
        self.fetch_size = fetch_size
        self.rows = self._frame_items(frame) if frame is not None else None

    def _frame_items(self, frame):
        result_type = frame.WhichOneof('result')
        if result_type not in self._FRAME_ITEMS:
            raise NotSupportedError(f'Unsupported Prism result frame: {result_type}')
        return iter(getattr(getattr(frame, result_type), self._FRAME_ITEMS[result_type]))

    def close(self):
        if self.closed:
            return
        try:
            if self.con.con is not None:
                self.con.con.close_statement(self.statement_id)
        finally:
            self.con = None
            self.closed = True

    def __next__(self):
        # frame is None when there were no results
        if self.frame is None:
            raise ProgrammingError("Previous statement did not produce any results")

        while True:
            try:
                return next(self.rows)
            except StopIteration:
                if self.frame.is_last:
                    raise
            self.frame = self.con.con.fetch(self.statement_id, self.fetch_size)
            self.rows = self._frame_items(self.frame)


class Cursor:
    def __init__(self, con):
        self.con = con
        self.result = None
        self.reset()

    def reset(self):
        self._require_open()
        previous, self.result = self.result, None
        self.description = None
        self.rowcount = -1
        self.arraysize = 1
        if previous is not None:
            previous.close()

    # def callproc(self):
    # optional

    def __del__(self):
        with suppress(Error):
            self.close()

    def close(self):
        if self.con is not None:
            try:
                if self.result is not None:
                    self.result.close()
            finally:
                self.result = None
                self.con.cursors.discard(self)
                self.con = None

    def _require_open(self):
        if self.con is None:
            raise ProgrammingError("Cursor is closed")

    def _require_result(self):
        self._require_open()
        if self.result is None:
            raise ProgrammingError("No statement was yet executed")
        if self.result.frame is None:
            raise ProgrammingError("Previous statement did not produce any results")

    def __iter__(self):
        return self

    def __next__(self):
        n = self.fetchone()
        if n is None:
            raise StopIteration
        return n

    def derive_description(self, relframe):
        self.description = []
        for column in relframe.column_meta:
            self.description.append(
                (column.column_label, None, None, None, None, column.precision, column.scale, column.is_nullable))

    def execute(self, query: str, params: List[Any] = None, *, fetch_size: int = None):
        """
        Executes a SQL query.
        """
        return self.executeany('sql', query, params, fetch_size=fetch_size)

    def executemany(self, query: str, params: List[List[Any]]):
        """
        Execute `query` once with each item in `params` as parameters.
        """
        self._require_open()
        try:
            batch = iter(params)
        except TypeError as e:
            raise ProgrammingError(str(e)) from e
        for param in batch:
            self.execute(query, param)

    def executeany(self, lang: str, query: str, params: List[Any] = None, *,
                   fetch_size: int = None, namespace: str = None):
        """
        This method is used to query Polypheny in any of the supported
        languages.  Dynamic parameter substitution is language
        specific

        :param lang:
        :param query:
        :param params:
        :param namespace: Sets the default namespace for the query.

        To query Polypheny using the MongoQL:

        >>> cur.executeany('mongo', 'db.fruits.find({"id": 1})')
        >>> print(cur.fetchone())
        {'id': 1, 'name': 'Orange'}

        Use ``lang='cypher'`` with a graph namespace. Graph streams yield
        one node or edge dictionary per item. Cypher projections returned
        as relational rows can contain graph values alongside scalar values.
        """

        self.reset()
        statement_id = None
        connection = self.con.con
        try:
            if params is None:  # Unparameterized query
                response = connection.execute_unparameterized_statement(lang, query, fetch_size, namespace)
                statement_id = response.statement_id
                if not response.HasField("result"):
                    raise InterfaceError("Prism statement response did not contain a result")
                result = response.result
            elif type(params) in (list, tuple):
                response = connection.prepare_indexed_statement(lang, query, namespace)
                statement_id = response.statement_id
                result = connection.execute_indexed_statement(statement_id, params, fetch_size)
            elif type(params) is dict:
                response = connection.prepare_named_statement(lang, query, namespace)
                statement_id = response.statement_id
                result = connection.execute_named_statement(statement_id, params, fetch_size)
            else:
                raise ProgrammingError("Unexpected type for params " + str(type(params)))

            frame = result.frame if result.HasField("frame") else None
            self.result = ResultCursor(self.con, statement_id, frame, fetch_size)
        except (Error, TypeError, ValueError, OverflowError) as e:
            if statement_id is not None:
                with suppress(Error):
                    connection.close_statement(statement_id)
            if isinstance(e, Error):
                raise
            raise ProgrammingError(str(e)) from e

        if frame is None:
            self.rowcount = result.scalar
        elif frame.WhichOneof('result') == 'relational_frame':
            self.derive_description(frame.relational_frame)

    def fetchone(self):
        self._require_result()
        try:
            n = next(self.result)
        except StopIteration:
            return None

        if isinstance(n, relational_frame_pb2.Row):
            v = []
            for value in n.values:
                v.append(proto2py(value))
            return v
        elif isinstance(n, value_pb2.ProtoDocument):
            value = value_pb2.ProtoValue()
            value.document.CopyFrom(n)
            return proto2py(value)
        elif isinstance(n, graph_frame_pb2.GraphElement):
            return proto_graph_element2py(n)
        else:
            raise NotSupportedError(f"Unknown result of type {type(n)}")

    def fetchmany(self, size=None):
        self._require_result()
        if size is None:
            size = self.arraysize
        try:
            batch = range(size)
        except (TypeError, ValueError, OverflowError) as e:
            raise ProgrammingError(str(e)) from e
        results = []
        for _ in batch:
            row = self.fetchone()
            if row is None:
                break
            results.append(row)
        return results

    def fetchall(self):
        results = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            results.append(row)
        return results

    # optional
    # def nextset(self):
    #    pass

    def setinputsizes(self, sizes):
        """ This method is a no-op. """
        pass  # We are free to do nothing

    def setoutputsize(self, sizes, column=None):
        """ This method is a no-op """
        pass  # We are free to do nothing
