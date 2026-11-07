# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public Rust copies of quoted-path, suppressed-response and encoding creates."""

from copy import deepcopy

import pytest

from config import clients
from create_item._legacy_variants import (
    CASES,
    ENCODING_CASES,
    RESPONSE_MODES,
    assert_created,
    assert_fields,
    observe_native_create,
)
from create_item._legacy_variants import (  # pylint: disable=unused-import
    _make_variant_container_fixture,
    _variant_database_fixture,
)

from azure.cosmos import PartitionKey

@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
@pytest.mark.parametrize("client_suppressed,options,suppressed", RESPONSE_MODES)
def test_partition_key_extraction_special_chars_rust(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_partitioned_collection_partition_key_extraction_special_chars
    # Also covers the same method in test_crud_response_payload_on_write_disabled
    # and test_crud_subpartition's *_special_chars_subpartition.
    target = make_variant_container(case["definition"])
    with clients.create_data_client(
        _backend="rust" if backend == "rust" else "core-python",
        no_response_on_write=client_suppressed,
        timeout=30,
    ) as client:
        container = client.get_database_client(variant_database.id).get_container_client(target.id)
        native = observe_native_create(monkeypatch, client, backend)
        body = deepcopy(case["body"])
        created = container.create_item(body, **options)
        assert body == case["body"]
        assert_created(created, body, suppressed, native)
        assert_fields(container.read_item(body["id"], partition_key=case["key"]), body)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("body", ENCODING_CASES)
def test_unicode_partition_key_and_separator_round_trip_rust(
    variant_database, make_variant_container, monkeypatch, backend, body
):
    # Source: tests/test_encoding.py::TestEncoding.test_create_document_with_line_separator_para_seperator_next_line_unicodes
    # Also preserves test_unicode_characters_in_partition_key and its exact string.
    target = make_variant_container(PartitionKey(path="/pk"))
    with clients.create_data_client(_backend=backend, timeout=30) as client:
        container = client.get_database_client(variant_database.id).get_container_client(target.id)
        native = observe_native_create(monkeypatch, client, backend)
        original = deepcopy(body)
        created = container.create_item(body)
        assert body == original
        assert_created(created, original, False, native)
        read = container.read_item(created["id"], partition_key=body["pk"])
        assert_fields(read, original)
        for key in ("pk", "unicode_content"):
            if key in original:
                assert read[key].encode("utf-8") == original[key].encode("utf-8")
