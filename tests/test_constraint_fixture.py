# Copyright 2026 The Polypheny Project
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
from io import BytesIO
from unittest.mock import Mock

import pytest

import polypheny
import test_error_mapping
from test_error_mapping import enable_constraint_enforcement


WEBUI_URL = "http://polypheny.invalid:8765"
KEY = "uniqueConstraintEnforcement"
RUNTIME_KEY = f"runtime/{KEY}"


@pytest.fixture
def config_http(monkeypatch):
    monkeypatch.setenv("POLYPHENY_TEST_WEBUI_URL", f"{WEBUI_URL}/")
    urlopen = Mock(side_effect=[
        BytesIO(b'{"value": false}'),
        BytesIO(b'{"successful": true, "message": "All values were saved."}'),
    ])
    monkeypatch.setattr(test_error_mapping, "urlopen", urlopen)
    return urlopen


def assert_http_restore(config_http):
    assert config_http.call_count == 2
    lookup, restore = [call.args[0] for call in config_http.call_args_list]
    assert lookup.full_url == f"{WEBUI_URL}/config/v1/getConfig"
    assert lookup.data.decode() == RUNTIME_KEY
    assert restore.full_url == f"{WEBUI_URL}/config/v1/updateConfigs"
    assert restore.get_method() == "POST"
    assert restore.get_header("Content-type") == "application/json"
    assert json.loads(restore.data) == {RUNTIME_KEY: False}


def test_constraint_fixture_restores_after_lost_alter_reply(config_http):
    connection, cursor = Mock(), Mock()
    alter_error = polypheny.OperationalError("ALTER reply was lost")
    cursor.execute.side_effect = alter_error

    with pytest.raises(polypheny.OperationalError) as caught:
        with enable_constraint_enforcement(connection, cursor, KEY):
            pytest.fail("The fixture body should not run after a failed ALTER")

    assert caught.value is alter_error
    connection.rollback.assert_called_once_with()
    cursor.execute.assert_called_once_with(f"ALTER CONFIG '{RUNTIME_KEY}' SET true")
    assert_http_restore(config_http)


def test_constraint_fixture_restores_after_lost_rollback(config_http):
    connection, cursor = Mock(), Mock()
    rollback_error = polypheny.OperationalError("Prism transport lost during rollback")
    connection.rollback.side_effect = rollback_error

    with pytest.raises(polypheny.OperationalError) as caught:
        with enable_constraint_enforcement(connection, cursor, KEY):
            pass

    assert caught.value is rollback_error
    connection.rollback.assert_called_once_with()
    cursor.execute.assert_called_once_with(f"ALTER CONFIG '{RUNTIME_KEY}' SET true")
    assert_http_restore(config_http)


def test_constraint_fixture_preserves_test_failure_when_cleanup_fails(config_http, caplog):
    connection, cursor = Mock(), Mock()
    test_error = AssertionError("Original test failure")
    connection.rollback.side_effect = polypheny.OperationalError("Prism transport lost during rollback")
    config_http.side_effect = [
        BytesIO(b'{"value": false}'),
        BytesIO(b'{"successful": false, "message": "Setting was rejected."}'),
    ]

    with pytest.raises(AssertionError) as caught:
        with enable_constraint_enforcement(connection, cursor, KEY):
            raise test_error

    assert caught.value is test_error
    connection.rollback.assert_called_once_with()
    assert_http_restore(config_http)
    assert "Setting was rejected." in caplog.text
