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

from typing import List, Any

from org.polypheny.prism import relational_frame_pb2
from polypheny import rpc
from polypheny.exceptions import *
from polypheny.serialize import *


class Connection:
    def __init__(self, address, username, password, transport, kwargs):
        self.cursors = set()
        self.con = None  # Needed so destructor works

        try:
            self.con = rpc.Connection(address, transport, kwargs)
        except ConnectionRefusedError:
            raise Error("Connection refused") from None

        try:
            resp = self.con.connect(username, password, False)
            if not resp.is_compatible:
                raise Error(
                    f"Client ({rpc.POLYPHENY_API_MAJOR}.{rpc.POLYPHENY_API_MINOR}) is incompatible with Server version ({resp.major_api_version}.{resp.minor_api_version})")
        except Exception as e:
            # This manual dance prevents the disconnect message from being sent
            self.con.con.close()
            self.con.con = None
            self.con = None
            raise Error(str(e))

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
        # TODO Thread-safety?
        self.close()

    def close(self):
        if self.con is None:
            assert len(self.cursors) == 0
            return

        for cur in list(self.cursors):  # self.cursors is materialized because cur.close modifies it
            cur.close()
        assert len(self.cursors) == 0

        try:
            self.rollback()
        finally:
            self.con.close()
            self.con = None


class ResultCursor:
    def __init__(self, con, statement_id, frame, fetch_size):
        self.con = con
        self.statement_id = statement_id
        self.closed = False
        self.frame = frame
        self.fetch_size = fetch_size
        if frame is not None:
            restype = self.frame.WhichOneof('result')
            assert restype is not None
            if restype == 'relational_frame':
                self.rows = iter(self.frame.relational_frame.rows)
            elif restype == 'document_frame':
                self.rows = iter(self.frame.document_frame.documents)
            else:
                self.closed = True
                raise NotImplementedError(f'Resultset of type {restype} is not implemented')

    def __del__(self):
        assert self.closed
        self.close()

    def close(self):
        if self.closed:
            return
        assert self.con.con is not None
        try:
            self.con.con.close_statement(self.statement_id)
        finally:
            self.con = None
            self.closed = True

    def __next__(self):
        # frame is None when there were no results
        if self.frame is None:
            raise Error("Previous statement did not produce any results")

        assert self.rows is not None

        try:
            return next(self.rows)
        except StopIteration:
            if self.frame.is_last:
                raise
            return self.nextframe()

    def nextframe(self):
        self.frame = self.con.con.fetch(self.statement_id, self.fetch_size)
        self.rows = iter(self.frame.relational_frame.rows)  # TODO result must not be relational
        return next(self.rows)  # TODO: What happens if this returns StopIteration, but another frame could be fetched?


class Cursor:
    def __init__(self, con):
        self.con = con
        self.result = None
        self.reset()

    def reset(self):
        if self.result is not None:
            self.result.close()
        self.description = None
        self.rowcount = -1
        self.arraysize = 1
        self.result = None

    # def callproc(self):
    # optional

    def __del__(self):
        self.close()

    def close(self):
        # TODO: Error when already closed?
        assert self.con is not None or self.result is None
        if self.con is not None:
            if self.result is not None:
                self.result.close()
                self.result = None
            self.con.cursors.remove(self)
            self.con = None

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
        # TODO: Optimize, this is to exercise the execute code more
        for param in params:
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

        .. Note::

           Queries returning graphs are not supported yet.

        To query Polypheny using the MongoQL:

        >>> cur.executeany('mongo', 'db.fruits.find({"id": 1})')
        >>> print(cur.fetchone())
        {'id': 1, 'name': 'Orange'}
        """

        if self.con is None:
            raise Error("Cursor is closed")

        self.reset()

        if params is None:  # Unparameterized query
            r = self.con.con.execute_unparameterized_statement(lang, query, fetch_size, namespace)
            assert r.HasField("result")  # Is this always true?
            statement_id = r.statement_id
            result = r.result
        elif type(params) == list or type(params) == tuple:
            resp = self.con.con.prepare_indexed_statement(lang, query, namespace)
            statement_id = resp.statement_id
            result = self.con.con.execute_indexed_statement(statement_id, params, fetch_size)
        elif type(params) == dict:
            resp = self.con.con.prepare_named_statement(lang, query, namespace)
            statement_id = resp.statement_id
            result = self.con.con.execute_named_statement(statement_id, params, fetch_size)
        else:
            raise Error("Unexpected type for params " + str(type(params)))

        if result.HasField(
                "frame"):  # TODO Better Error when one of the fetch* methods is invoked.  Empty fake result?
            self.rowcount = -1
            if result.frame.WhichOneof('result') == 'relational_frame':
                self.derive_description(result.frame.relational_frame)
            frame = result.frame
        else:
            self.rowcount = result.scalar
            frame = None

        self.result = ResultCursor(self.con, statement_id, frame, fetch_size)

    def fetchone(self):
        if self.con is None:
            raise ProgrammingError("Cursor is closed")

        if self.result is None:
            raise ProgrammingError("No statement was yet executed")

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
        else:
            raise Error(f"Unknown result of type {type(n)}")

    def fetchmany(self, size=None):
        # TODO: Optimize, this is to exercise the fetch code more
        if size is None:
            size = self.arraysize
        results = []
        for _ in range(size):
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
