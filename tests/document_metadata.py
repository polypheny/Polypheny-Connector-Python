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

"""Live regression tests for document metadata over the ordinary Prism RPC.

Run explicitly with ``pytest tests/document_metadata.py``. These tests need
Polypheny with the companion document metadata change and Python bindings
generated from the corresponding Prism definitions. They connect to the
ordinary plain Prism endpoint, just like the connector's Windows tests.
"""

import json
import os
import uuid

import pytest
import polypheny
from org.polypheny.prism import namespace_meta_requests_pb2
from org.polypheny.prism import namespace_meta_responses_pb2

DOCUMENTS = [
    {
        "_id": "patient-1",
        "patient_id": "p-001",
        "age": 23,
        "viral_load_day1": 6.25,
        "active": True,
        "symptoms": ["fever", "fatigue"],
        "progression": [{"day": 1, "viral_load": 6.25}],
        "complications": {"respiratory": {"onset_day": 2}, "renal": None},
        "notes": None,
        "score": 1,
        "mixed": 1,
        "optional_field": 42,
        "empty_object": {},
        "nullable": "present",
        "nullable_parent": {"child": 1},
    },
    {
        "_id": "patient-2",
        "patient_id": "p-002",
        "age": 64,
        "viral_load_day1": 3.5,
        "active": False,
        "symptoms": [],
        "progression": [],
        "complications": {"respiratory": {"onset_day": 4}, "renal": "mild"},
        "notes": None,
        "score": 1.5,
        "mixed": "unknown",
        "empty_object": {},
        "nullable": None,
        "nullable_parent": None,
    },
    {
        "_id": "patient-3",
        "patient_id": "p-003",
        "age": 7,
        "viral_load_day1": 5.75,
        "active": True,
        "symptoms": ["pain"],
        "progression": [{"day": 1, "viral_load": 5.75}],
        "complications": {},
        "notes": None,
        "score": 2,
        "mixed": True,
        "empty_object": {},
        "nullable": "again",
        "nullable_parent": {"child": 2},
    },
]


@pytest.fixture
def con():
    connection = polypheny.connect(
        (os.environ.get("POLYPHENY_PRISM_HOST", "127.0.0.1"),
         int(os.environ.get("POLYPHENY_PRISM_PORT", "20590"))),
        username=os.environ.get("POLYPHENY_PRISM_USER", "pa"),
        password=os.environ.get("POLYPHENY_PRISM_PASSWORD", ""),
        transport="plain",
    )
    try:
        yield connection
    finally:
        connection.close()


def get_entities(connection, namespace, pattern=None):
    """Use the same request wrapper and RPC call as relational metadata."""
    message = connection.con.new_request()
    request = namespace_meta_requests_pb2.EntitiesRequest(namespace_name=namespace)
    if pattern is not None:
        request.entity_pattern = pattern
    message.entities_request.CopyFrom(request)
    response = connection.con.call(message)
    assert response.HasField("entities_response")
    return response.entities_response


@pytest.fixture(autouse=True)
def document_metadata_schema():
    fields = namespace_meta_responses_pb2.Document.DESCRIPTOR.fields_by_name
    assert "collection_name" in fields, (
        "Document metadata requires the companion Prism schema. Run "
        "python scripts/test_document_metadata.py --prism-api /path/to/Polypheny-Prism-API"
    )


def get_document(connection, namespace, collection):
    response = get_entities(connection, namespace, collection)
    assert len(response.entities) == 1
    entity = response.entities[0]
    assert entity.WhichOneof("Entity") == "document"
    assert not entity.HasField("table")
    assert not entity.HasField("graph")
    return entity.document


@pytest.fixture
def document_namespace(con):
    # A private namespace avoids modifying user data or colliding with parallel runs.
    namespace = "prism_doc_meta_" + uuid.uuid4().hex
    cursor = con.cursor()
    cursor.execute("CREATE DOCUMENT NAMESPACE " + namespace)
    try:
        cursor.executeany("mongo", 'db.createCollection("symptoms")', namespace=namespace)
        cursor.executeany("mongo", 'db.createCollection("empty")', namespace=namespace)
        for document in DOCUMENTS:
            cursor.executeany(
                "mongo", "db.symptoms.insertOne(" + json.dumps(document) + ")",
                namespace=namespace,
            )
        con.commit()
        yield namespace
    finally:
        con.rollback()
        cursor.execute("DROP NAMESPACE " + namespace)
        cursor.close()


def test_document_identity_and_entity_wrapper(con, document_namespace):
    response = get_entities(con, document_namespace)
    assert {entity.document.collection_name for entity in response.entities} == {"symptoms", "empty"}
    for entity in response.entities:
        assert entity.WhichOneof("Entity") == "document"
        assert entity.document.namespace_name == document_namespace


def test_all_document_field_metadata(con, document_namespace):
    document = get_document(con, document_namespace, "symptoms")
    # Every DocumentField property is checked against input data. In particular,
    # false is_optional values must survive protobuf's default-value encoding.
    expected = {
        "_id": ("string", False),
        "patient_id": ("string", False),
        "age": ("int", False),
        "viral_load_day1": ("double", False),
        "active": ("bool", False),
        "symptoms": ("array", False),
        "progression": ("array", False),
        "complications": ("object", False),
        "complications.respiratory": ("object", True),
        "complications.respiratory.onset_day": ("int", True),
        "complications.renal": ("string", True),
        "notes": ("null", True),
        "score": ("double", False),
        "mixed": ("mixed", False),
        "optional_field": ("int", True),
        "empty_object": ("object", False),
        "nullable": ("string", True),
        "nullable_parent": ("object", True),
        "nullable_parent.child": ("int", True),
    }
    actual = {
        field.field_path: (field.type_name, field.is_optional)
        for field in document.fields
    }
    assert len(actual) == len(document.fields), "Field paths must not be duplicated"
    assert actual == expected


def test_sample_document_is_actual_json_document(con, document_namespace):
    document = get_document(con, document_namespace, "symptoms")
    assert document.HasField("sample_document_json")
    sample = json.loads(document.sample_document_json)
    assert sample in DOCUMENTS
    # Sampling metadata must not consume or modify the collection.
    cursor = con.cursor()
    try:
        cursor.executeany("mongo", "db.symptoms.find({})", namespace=document_namespace)
        assert sorted(cursor.fetchall(), key=lambda item: item["_id"]) == DOCUMENTS
    finally:
        cursor.close()


def test_document_field_paths_escape_literal_separators(con, document_namespace):
    cursor = con.cursor()
    original = {
        "_id": "escaped",
        "literal.key": 1,
        "literal": {"key": "nested"},
        "slash\\key": True,
    }
    try:
        cursor.executeany("mongo", 'db.createCollection("escapedpaths")', namespace=document_namespace)
        cursor.executeany(
            "mongo", "db.escapedpaths.insertOne(" + json.dumps(original) + ")",
            namespace=document_namespace,
        )
        con.commit()
        document = get_document(con, document_namespace, "escapedpaths")
        actual = {
            field.field_path: (field.type_name, field.is_optional)
            for field in document.fields
        }
        assert actual == {
            "_id": ("string", False),
            r"literal\.key": ("int", False),
            "literal": ("object", False),
            "literal.key": ("string", False),
            r"slash\\key": ("bool", False),
        }
        assert len(actual) == len(document.fields), "Escaping must preserve distinct field paths"
        assert json.loads(document.sample_document_json) == original
    finally:
        cursor.close()


def test_empty_collection_has_valid_metadata(con, document_namespace):
    document = get_document(con, document_namespace, "empty")
    assert document.namespace_name == document_namespace
    assert document.collection_name == "empty"
    assert list(document.fields) == []
    assert not document.HasField("sample_document_json")
    # HSQLDB does not expose document indexes. Absence must be an empty list,
    # rather than invented metadata for an implicit MongoDB index.
    if os.environ.get("DEFAULT_STORE", "hsqldb").lower() == "hsqldb":
        assert list(document.document_indexes) == []


@pytest.mark.parametrize("pattern, expected", [
    ("symptoms", {"symptoms"}),
    ("sym%", {"symptoms"}),
    ("empt_", {"empty"}),
    ("%", {"symptoms", "empty"}),
    ("missing", set()),
])
def test_document_entity_patterns(con, document_namespace, pattern, expected):
    response = get_entities(con, document_namespace, pattern)
    assert {entity.document.collection_name for entity in response.entities} == expected


def test_metadata_reflects_committed_document_updates(con, document_namespace):
    before = get_document(con, document_namespace, "empty")
    assert not before.HasField("sample_document_json")
    cursor = con.cursor()
    try:
        cursor.executeany(
            "mongo", 'db.empty.insertOne({"_id":"new", "new_field":17})',
            namespace=document_namespace,
        )
        con.commit()
        after = get_document(con, document_namespace, "empty")
        fields = {field.field_path: field for field in after.fields}
        assert fields["new_field"].type_name == "int"
        assert not fields["new_field"].is_optional
        assert json.loads(after.sample_document_json) == {"_id": "new", "new_field": 17}
    finally:
        cursor.close()


def test_metadata_reads_pending_writes_without_committing(con, document_namespace):
    cursor = con.cursor()
    try:
        cursor.executeany(
            "mongo", 'db.empty.insertOne({"_id":"pending", "uncommitted":true})',
            namespace=document_namespace,
        )
        document = get_document(con, document_namespace, "empty")
        assert json.loads(document.sample_document_json) == {"_id": "pending", "uncommitted": True}
        field = next(item for item in document.fields if item.field_path == "uncommitted")
        assert (field.type_name, field.is_optional) == ("bool", False)
        con.rollback()
        after = get_document(con, document_namespace, "empty")
        assert list(after.fields) == []
        assert not after.HasField("sample_document_json")
    finally:
        cursor.close()


def test_empty_document_namespace_returns_empty_entities(con):
    namespace = "prism_doc_empty_" + uuid.uuid4().hex
    cursor = con.cursor()
    cursor.execute("CREATE DOCUMENT NAMESPACE " + namespace)
    try:
        assert list(get_entities(con, namespace).entities) == []
    finally:
        con.rollback()
        cursor.execute("DROP NAMESPACE " + namespace)
        cursor.close()


def test_relational_metadata_still_works_after_document_request(con, document_namespace):
    namespace = "prism_rel_meta_" + uuid.uuid4().hex
    cursor = con.cursor()
    cursor.execute("CREATE RELATIONAL NAMESPACE " + namespace)
    try:
        cursor.execute("CREATE TABLE " + namespace + ".patients(id INTEGER NOT NULL, name VARCHAR(50), PRIMARY KEY(id))")
        get_entities(con, document_namespace)
        response = get_entities(con, namespace, "patients")
        assert len(response.entities) == 1
        assert response.entities[0].WhichOneof("Entity") == "table"
        table = response.entities[0].table
        assert table.namespace_name == namespace
        assert table.table_name == "patients"
        assert {column.column_name for column in table.columns} == {"id", "name"}
        assert table.HasField("primary_key")
    finally:
        con.rollback()
        cursor.execute("DROP NAMESPACE " + namespace)
        cursor.close()
