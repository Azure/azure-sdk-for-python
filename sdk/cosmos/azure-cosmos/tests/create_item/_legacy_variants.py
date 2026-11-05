# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared original create vectors and owned live fixtures.

Partition-key vectors come from test_crud_container, test_crud_subpartition,
test_crud_response_payload_on_write_disabled, and their async counterparts.
The native binding test uses the same JSON to retain their wire-header checks.
Unicode strings are copied unchanged from test_encoding and test_encoding_async.
"""

import json
import os
from pathlib import Path
from unittest.mock import Mock
import uuid

import pytest

from common._parity_helpers import _observed_backend_name
from common.parity_provisioning import create_owned_container
from common.throughput_fixtures import owned_database

from azure.cosmos import CosmosClient, exceptions

CASES = json.loads(Path(__file__).with_name("legacy_partition_key_cases.json").read_text(encoding="utf-8"))
RESPONSE_MODES = [
    pytest.param(False, {}, False, id="body-default"),
    pytest.param(True, {}, True, id="suppressed-client-default"),
    pytest.param(False, {"no_response": True}, True, id="suppressed-call"),
    pytest.param(True, {"no_response": False}, False, id="body-call-override"),
]
UNICODE_KEY = "€€ کلید پارتیشن विभाजन कुंजी \t123"  # cspell:disable-line
UNICODE_CONTENT = (
    "Line Separator (\u2028) & Paragraph Separator (\u2029) & Next Line (\x85) & نیم\u200cفاصله"  # cspell:disable-line
)
ENCODING_CASES = [
    pytest.param({"id": "unicode-key", "pk": UNICODE_KEY}, id="unicode-partition-key"),
    pytest.param({"id": "unicode-separators", "pk": "pk", "unicode_content": UNICODE_CONTENT}, id="unicode-separators"),
]


@pytest.fixture(scope="module", name="variant_database")
def _variant_database_fixture():
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust", timeout=30) as client:
        with owned_database(client, "create_variants_" + uuid.uuid4().hex) as database:
            yield database


@pytest.fixture(name="make_variant_container")
def _make_variant_container_fixture(variant_database):
    owned = []

    def create(definition, **kwargs):
        name = "variant_" + uuid.uuid4().hex
        owned.append(name)
        try:
            return create_owned_container(variant_database, id=name, partition_key=definition, **kwargs)
        except exceptions.CosmosResourceExistsError:
            owned.remove(name)
            raise

    try:
        yield create
    finally:
        for name in reversed(owned):
            try:
                variant_database.delete_container(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


def observe_native_create(monkeypatch, client, backend, *, asynchronous=False):
    assert _observed_backend_name(client) == backend
    if backend != "rust":
        return None
    from azure.cosmos import _rust

    name = "create_item_async" if asynchronous else "create_item"
    native = Mock(wraps=getattr(_rust, name))
    monkeypatch.setattr(_rust, name, native)
    monkeypatch.setattr(
        client.client_connection, "CreateItem", Mock(side_effect=AssertionError("Rust create fell back to legacy"))
    )
    return native


def assert_created(created, body, suppressed, native):
    if native is not None:
        native.assert_called_once()
    if suppressed:
        assert created == {}
    else:
        assert_fields(created, body)
    assert created.get_response_headers().get("etag"), "Create lost response headers"


def assert_fields(actual, expected):
    for key, value in expected.items():
        assert actual[key] == value, f"Stored field changed: {key}"
