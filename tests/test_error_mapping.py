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


import json
import logging
import os
from contextlib import contextmanager
from urllib.request import Request, urlopen

import pytest

import polypheny
from polypheny import rpc
from test_helper import con


@pytest.fixture
def errtest(con):
    cursor = con.cursor()
    cursor.execute("CREATE NAMESPACE errtest")
    try:
        cursor.execute("CREATE TABLE errtest.t (id INTEGER PRIMARY KEY, name VARCHAR(50) NOT NULL)")
        cursor.execute("INSERT INTO errtest.t VALUES (1, 'first')")
        con.commit()
        yield cursor
    finally:
        con.rollback()
        cursor.execute("DROP NAMESPACE errtest")
        cursor.close()


def assert_error(caught, exception_type, sqlstates):
    assert type(caught.value) is exception_type
    assert caught.value.sqlstate in sqlstates


def assert_recovered(connection, cursor):
    connection.rollback()
    cursor.execute("SELECT id, name FROM errtest.t")
    assert cursor.fetchall() == [[1, "first"]]
    connection.commit()


@pytest.mark.parametrize(("statement", "exception_type", "sqlstates"), [
    pytest.param("SELECT * FROM does_not_exist.t", polypheny.ProgrammingError, ("42P01", "3F000"), id="S1"),
    pytest.param("SELECT * FROM errtest.nope", polypheny.ProgrammingError, ("42P01",), id="S2"),
    pytest.param("SELECT nope FROM errtest.t", polypheny.ProgrammingError, ("42703",), id="S3"),
    pytest.param("SELEC * FROM errtest.t", polypheny.ProgrammingError, ("42601",), id="S4"),
    pytest.param("INSERT INTO errtest.t (id, name) VALUES (2, NULL)", polypheny.IntegrityError, ("23502",), id="S5"),
    pytest.param("INSERT INTO errtest.t (id, name) VALUES ('abc', 'x')", polypheny.ProgrammingError, ("42804",), id="S6"),
    pytest.param("SELECT CAST('abc' AS INTEGER) FROM errtest.t", polypheny.DataError, ("22018", "22P02"), id="S7"),
    pytest.param("SELECT 1/0 FROM errtest.t", polypheny.DataError, ("22012",), id="S8"),
    pytest.param("CREATE TABLE errtest.nopk (a INTEGER)", polypheny.ProgrammingError, ("42P16",), id="S9"),
])
def test_sql_statement_error(con, errtest, statement, exception_type, sqlstates):
    with pytest.raises(exception_type) as caught:
        errtest.execute(statement)
        if errtest.description is not None:
            errtest.fetchall()
    assert_error(caught, exception_type, sqlstates)
    assert_recovered(con, errtest)


def _config_request(webui_url, endpoint, data, content_type):
    request = Request(f"{webui_url}/config/v1/{endpoint}", data=data.encode(),
                      headers={"Content-Type": content_type})
    with urlopen(request, timeout=10) as response:
        return json.load(response)


@contextmanager
def enable_constraint_enforcement(connection, cursor, key):
    key = f"runtime/{key}"
    webui_url = os.environ.get("POLYPHENY_TEST_WEBUI_URL", "http://127.0.0.1:7659").rstrip("/")
    enabled = _config_request(webui_url, "getConfig", key, "text/plain")["value"]
    assert isinstance(enabled, bool), f"Expected a boolean runtime setting for {key}"

    def cleanup():
        try:
            connection.rollback()
        finally:
            if not enabled:
                # The config server can restore the setting even if Prism has disconnected.
                feedback = _config_request(webui_url, "updateConfigs", json.dumps({key: enabled}),
                                           "application/json")
                if feedback.get("successful") is not True:
                    raise RuntimeError(f"Could not restore {key}: {feedback}")

    try:
        if not enabled:
            cursor.execute(f"ALTER CONFIG '{key}' SET true")
        yield
    except BaseException:
        try:
            cleanup()
        except Exception:
            logging.getLogger(__name__).exception("Cleanup failed for %s", key)
        raise
    else:
        cleanup()


def test_s10_duplicate_primary_key_enforced(con, errtest):
    with enable_constraint_enforcement(con, errtest, "uniqueConstraintEnforcement"):
        with pytest.raises(polypheny.IntegrityError) as caught:
            errtest.execute("INSERT INTO errtest.t VALUES (1, 'duplicate')")
            con.commit()
        assert_error(caught, polypheny.IntegrityError, ("23505",))
        assert_recovered(con, errtest)


def test_s11_duplicate_primary_key_default(con, errtest):
    errtest.execute("INSERT INTO errtest.t VALUES (1, 'duplicate')")
    if os.getenv("DEFAULT_STORE") == "file":
        # The File adapter's physical row names enforce primary-key uniqueness.
        with pytest.raises(polypheny.IntegrityError) as caught:
            con.commit()
        assert_error(caught, polypheny.IntegrityError, ("23505",))
        assert_recovered(con, errtest)
        return

    con.commit()
    errtest.execute("SELECT COUNT(*) FROM errtest.t WHERE id = 1")
    assert errtest.fetchone() == [2]


def test_s12_foreign_key_violation(con, errtest):
    with enable_constraint_enforcement(con, errtest, "foreignKeyEnforcement"):
        errtest.execute("CREATE TABLE errtest.child (id INTEGER PRIMARY KEY, parent INTEGER)")
        errtest.execute(
            "ALTER TABLE errtest.child ADD CONSTRAINT fk_errtest "
            "FOREIGN KEY (parent) REFERENCES errtest.t(id) ON UPDATE RESTRICT ON DELETE RESTRICT"
        )
        with pytest.raises(polypheny.IntegrityError) as caught:
            errtest.execute("INSERT INTO errtest.child VALUES (1, 42)")
            con.commit()
        assert_error(caught, polypheny.IntegrityError, ("23503",))
        assert_recovered(con, errtest)


def test_s13_unsupported_query_language(con, errtest):
    with pytest.raises(polypheny.NotSupportedError) as caught:
        errtest.executeany("nosuchlanguage", "x")
    assert_error(caught, polypheny.NotSupportedError, ("0A000",))
    assert_recovered(con, errtest)


def test_s14_unknown_user(con, errtest):
    with pytest.raises(polypheny.OperationalError) as caught:
        polypheny.connect(("127.0.0.1", 20590), username="unknown", password="", transport="plain")
    assert_error(caught, polypheny.OperationalError, ("28000", "28P01"))
    assert_recovered(con, errtest)


def test_s15_incompatible_api_major(con, errtest, monkeypatch):
    monkeypatch.setattr(rpc, "POLYPHENY_API_MAJOR", rpc.POLYPHENY_API_MAJOR - 1)
    with pytest.raises(polypheny.InterfaceError, match="incompatible with Server version") as caught:
        polypheny.connect(("127.0.0.1", 20590), username="pa", password="", transport="plain")
    assert_error(caught, polypheny.InterfaceError, (None,))
    assert_recovered(con, errtest)
