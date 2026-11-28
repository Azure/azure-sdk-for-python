# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared original create vectors and owned live fixtures.

Partition-key vectors come from test_crud_container, test_crud_subpartition,
test_crud_response_payload_on_write_disabled, and their async counterparts.
The native binding test uses the same JSON to retain their wire-header checks.
Unicode strings are copied unchanged from test_encoding and test_encoding_async.
"""

import json
import logging
import os
from pathlib import Path
from unittest.mock import Mock
import uuid

import pytest

from common._rust_checks import backend_name
from config.provisioning import create_owned_container
from common.throughput_fixtures import owned_database

from azure.cosmos import CosmosClient, exceptions

_LOGGER = logging.getLogger(__name__)

CASES = json.loads(Path(__file__).with_name("partition_key_reference_cases.json").read_text(encoding="utf-8"))
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
def _make_variant_container_fixture(variant_database, request):
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
            except exceptions.CosmosHttpResponseError as error:
                # Keep the service explanation outside the long SDK traceback.
                _LOGGER.error(
                    "Variant container cleanup failed: test=%s database=%s container=%s "
                    "configured_auth=ACCOUNT_KEY backend=rust status=%s substatus=%s "
                    "activity_id=%s service_message=%s",
                    request.node.nodeid,
                    variant_database.id,
                    name,
                    error.status_code,
                    error.sub_status,
                    error.headers.get("x-ms-activity-id"),
                    error.http_error_message,
                )
                raise


def observe_native_create(monkeypatch, client, backend, *, asynchronous=False):
    assert backend_name(client) == backend
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
