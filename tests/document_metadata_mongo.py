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

"""Explicit live MongoDB source tests, including real DocumentIndex metadata.

Run with ``pytest -v tests/document_metadata_mongo.py`` against a MongoDB
replica set (defaults to 127.0.0.1:27017). This file is intentionally outside
pytest's default ``test_*.py`` selection, since ordinary connector tests need
only Polypheny. An explicit run fails if either service is unavailable.
"""

import json
import os
import time
import uuid

import pytest

from document_metadata import con, get_document, document_metadata_schema


@pytest.fixture
def mongo_source(con):
    # Ordinary --doctest-modules collection also imports this opt-in module.
    # Require pymongo only when its live MongoDB fixture is actually executed.
    from pymongo import MongoClient

    suffix = uuid.uuid4().hex
    database = "prism_metadata_" + suffix
    adapter = "prism_mongo_" + suffix
    host = os.environ.get("POLYPHENY_MONGO_HOST", "127.0.0.1")
    port = int(os.environ.get("POLYPHENY_MONGO_PORT", "27017"))
    client = MongoClient(host, port, directConnection=True, serverSelectionTimeoutMS=5000)
    cursor = con.cursor()
    registered = False
    try:
        client.admin.command("ping")
        collection = client[database]["symptoms"]
        collection.insert_many([
            {"_id": "p1", "patient_id": "p1", "age": 23, "complications": {"renal": "mild"}},
            {"_id": "p2", "patient_id": "p2", "age": 64, "complications": {"renal": "severe"}},
        ])
        collection.create_index("patient_id", unique=True)
        collection.create_index([("age", "hashed")])
        collection.create_index("complications.renal")
        collection.create_index([("$**", 1)])

        settings = {
            "mode": "remote", "host": host, "port": str(port),
            "database": database, "username": "", "password": "", "authSource": "",
        }
        cursor.execute(
            'ALTER ADAPTERS ADD "' + adapter + '" USING \'MongoDB\' AS \'Source\' WITH \''
            + json.dumps(settings) + "'"
        )
        registered = True

        # Source discovery may run asynchronously. Poll the public namespaces
        # endpoint instead of assuming a fixed startup delay.
        deadline = time.monotonic() + 30
        while True:
            message = con.con.new_request()
            message.namespaces_request.namespace_pattern = adapter
            response = con.con.call(message)
            if any(item.namespace_name == adapter for item in response.namespaces_response.namespaces):
                break
            assert time.monotonic() < deadline, "MongoDB source namespace was not discovered"
            time.sleep(0.1)

        yield adapter
    finally:
        try:
            con.rollback()
            if registered:
                cursor.execute('ALTER ADAPTERS DROP "' + adapter + '"')
        finally:
            cursor.close()
            client.drop_database(database)
            client.close()


def test_real_document_indexes_cover_every_index_field(con, mongo_source):
    metadata = get_document(con, mongo_source, "symptoms")
    actual = {(index.field_path, index.index_type, index.unique) for index in metadata.document_indexes}
    assert actual == {
        ("_id", "btree", True),
        ("patient_id", "btree", True),
        ("age", "hash", False),
        ("complications.renal", "btree", False),
        ("$**", "wildcard", False),
    }
    assert len(metadata.document_indexes) == len(actual), "Indexes must not be duplicated"
    assert metadata.namespace_name == mongo_source
    assert metadata.collection_name == "symptoms"
    assert metadata.HasField("sample_document_json")
    assert json.loads(metadata.sample_document_json)["patient_id"] in {"p1", "p2"}
