# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Create assertions retained from original composite tests; other APIs are setup/verification."""

from copy import deepcopy
import json
import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from auth._token_credentials import make_sync_token_credential, skip_unless_token_auth
from config import clients
from create_item._legacy_contracts import (
    AAD_CONTENT, COMPACT_CONTENT, EMOJI_CASES, INVALID_IDS, MEBIBYTE,
    assert_native_body, assert_stored_sequence, large_cjk_body,
)
from create_item._legacy_variants import assert_created, assert_fields, observe_native_create
from create_item._legacy_variants import (  # pylint: disable=unused-import
    _make_variant_container_fixture, _variant_database_fixture,
)

pytestmark = [
    pytest.mark.parametrize("backend", ["rust", "core-python"]),
]


@pytest.fixture(name="contract_client")
def _contract_client_fixture(backend, request):
    with clients.create_data_client(
        _backend="rust" if backend == "rust" else "core-python", timeout=60,
        **getattr(request, "param", {}),
    ) as client:
        yield client


def target(client, database, container):
    return client.get_database_client(database.id).get_container_client(container.id)


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("item_id", INVALID_IDS)
def test_create_illegal_characters_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, item_id
):
    # Source: tests/test_resource_id.py::TestResourceIds.test_create_illegal_characters
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/id")))
    native = observe_native_create(monkeypatch, contract_client, backend)
    if len(item_id) > 1024:
        with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
            container.create_item({"id": item_id})
        assert caught.value.status_code == 400
        if native is not None:
            native.assert_called_once()
    else:
        with pytest.raises(ValueError):
            container.create_item({"id": item_id})
        if native is not None:
            native.assert_not_called()


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("ttl", [0, None, -10])
def test_invalid_document_ttl_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, ttl
):
    # Source: tests/test_ttl.py::TestTimeToLive.test_collection_and_document_ttl_values
    container = target(
        contract_client, variant_database, make_variant_container(PartitionKey(path="/id"), default_ttl=10)
    )
    native = observe_native_create(monkeypatch, contract_client, backend)
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        container.create_item({"id": uuid.uuid4().hex, "name": "sample document", "key": "value", "ttl": ttl})
    assert caught.value.status_code == 400
    if native is not None:
        native.assert_called_once()


def _round_trip_emoji_document(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
):
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/pk")))
    native = observe_native_create(monkeypatch, contract_client, backend)
    body = {"id": uuid.uuid4().hex, "pk": "pk", "multibyte_content": content}
    created = container.create_item(body)
    assert_created(created, body, False, native)
    if via_query:
        rows = list(container.query_items(
            "SELECT * FROM c WHERE c.id = @id", parameters=[{"name": "@id", "value": body["id"]}], partition_key="pk"
        ))
        assert len(rows) == 1
        read = rows[0]
    else:
        read = container.read_item(body["id"], partition_key="pk")
    assert_fields(read, body)
    assert read["multibyte_content"].encode("utf-8") == content.encode("utf-8")


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("via_query,content", [param for param in EMOJI_CASES if param.id == "point-read"])
def test_round_trip_emoji_document_through_full_sdk_stack_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
):
    # Source: tests/test_encoding.py::TestEncoding.test_round_trip_emoji_document_through_full_sdk_stack
    _round_trip_emoji_document(
        variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
    )


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("via_query,content", [param for param in EMOJI_CASES if param.id == "query"])
def test_round_trip_emoji_document_via_query_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
):
    # Source: tests/test_encoding.py::TestEncoding.test_round_trip_emoji_document_via_query
    _round_trip_emoji_document(
        variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
    )


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("contract_client", [{"enable_compact_utf8_item_writes": True}], indirect=True)
def test_compact_utf8_create_rust(variant_database, make_variant_container, contract_client, monkeypatch, backend):
    # Source: tests/test_encoding.py::TestEncoding.test_compact_utf8_item_writes_through_full_sdk_stack
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/pk")))
    native = observe_native_create(monkeypatch, contract_client, backend)
    body = {"id": uuid.uuid4().hex, "pk": "\u65e5\u672c", "content": COMPACT_CONTENT}
    created = container.create_item(body)
    assert_created(created, body, False, native)
    assert_native_body(native, body, compact=True)
    assert_fields(container.read_item(body["id"], partition_key=body["pk"]), body)


def _large_cjk_create(variant_database, make_variant_container, monkeypatch, backend, compact):
    owned = make_variant_container(PartitionKey(path="/pk"))
    body = large_cjk_body()
    encoded = json.dumps(body, separators=(",", ":"), ensure_ascii=not compact).encode("utf-8")
    assert (len(encoded) < 2 * MEBIBYTE) == compact
    with clients.create_data_client(
        _backend=backend,
        enable_compact_utf8_item_writes=compact, timeout=60,
    ) as client:
        container = target(client, variant_database, owned)
        native = observe_native_create(monkeypatch, client, backend)
        if compact:
            created = container.create_item(body)
            assert_created(created, body, False, native)
            assert_fields(container.read_item(body["id"], partition_key="pk"), body)
        else:
            with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
                container.create_item(body)
            assert caught.value.status_code == 413
        assert_native_body(native, body, compact=compact)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
def test_compact_utf8_large_cjk_item_stays_under_wire_limit_rust(
    variant_database, make_variant_container, monkeypatch, backend
):
    # Source: tests/test_encoding.py::TestEncoding.test_compact_utf8_large_cjk_item_stays_under_wire_limit
    _large_cjk_create(variant_database, make_variant_container, monkeypatch, backend, compact=True)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
def test_default_ascii_escaping_rejects_large_cjk_item_rust(
    variant_database, make_variant_container, monkeypatch, backend
):
    # Source: tests/test_encoding.py::TestEncoding.test_default_ascii_escaping_rejects_large_cjk_item
    _large_cjk_create(variant_database, make_variant_container, monkeypatch, backend, compact=False)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("no_response", [False, True])
def test_create_response_headers_advance_lsn_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, no_response
):
    # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_point_operation_headers
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/company")))
    first = container.upsert_item({"id": uuid.uuid4().hex, "company": "Microsoft"})
    lsn = int(first.get_response_headers()["lsn"])
    native = observe_native_create(monkeypatch, contract_client, backend)
    body = {"id": uuid.uuid4().hex, "company": "Microsoft"}
    created = container.create_item(body, no_response=no_response)
    assert_created(created, body, no_response, native)
    assert created.get_response_headers()
    assert int(created.get_response_headers()["lsn"]) == lsn + 1


def _document_crud_create_persistence(
    variant_database, make_variant_container, contract_client, monkeypatch, backend
):
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/pk")))
    native = observe_native_create(monkeypatch, contract_client, backend)
    original = {"name": "sample document", "spam": "eggs", "key": "value", "pk": "pk"}
    body = deepcopy(original)
    assert container.create_item(body, enable_automatic_id_generation=True, no_response=True) == {}
    generated = container.create_item(body, enable_automatic_id_generation=True, no_response=False)
    explicit_body = dict(body, id=uuid.uuid4().hex)
    explicit = container.create_item(explicit_body, no_response=False)
    assert body == original
    assert_fields(generated, original)
    assert_fields(explicit, explicit_body)
    # All three writes use this partition in a new, empty container. Query keeps
    # the original persistence/count assertion independent of read-feed paging.
    stored = list(container.query_items("SELECT * FROM c", partition_key="pk"))
    assert_stored_sequence(stored, original, generated, explicit)
    if native is not None:
        assert native.call_count == 3
        assert {call.args[1].item_id for call in native.call_args_list} == {item["id"] for item in stored}
    with pytest.raises(exceptions.CosmosResourceExistsError) as caught:
        container.create_item(explicit_body)
    assert caught.value.status_code == 409
    assert len(list(container.query_items("SELECT * FROM c", partition_key="pk"))) == 3


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.parametrize("contract_client", [{"no_response_on_write": False}], indirect=True)
def test_document_crud_create_persistence_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend
):
    # Source: tests/test_crud.py::TestCRUDOperations.test_document_crud
    _document_crud_create_persistence(
        variant_database, make_variant_container, contract_client, monkeypatch, backend
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("contract_client", [{"no_response_on_write": True}], indirect=True)
def test_document_crud_response_payload_on_write_disabled_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend
):
    # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_document_crud
    _document_crud_create_persistence(
        variant_database, make_variant_container, contract_client, monkeypatch, backend
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("contract_client", [{"no_response_on_write": True}], indirect=True)
def test_document_crud_response_payload_enabled_via_override_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend
):
    # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_document_crud_response_payload_enabled_via_override
    _document_crud_create_persistence(variant_database, make_variant_container, contract_client, monkeypatch, backend)


def _token_credential_create(variant_database, make_variant_container, monkeypatch, backend, compact, query=False):
    owned = make_variant_container(PartitionKey(path="/pk"))
    credential = make_sync_token_credential()
    try:
        with CosmosClient(
            os.environ["ACCOUNT_HOST"], credential, _backend=backend,
            enable_compact_utf8_item_writes=compact, timeout=60,
        ) as client:
            container = target(client, variant_database, owned)
            native = observe_native_create(monkeypatch, client, backend)
            body = {"id": uuid.uuid4().hex, "pk": "pk", "content": AAD_CONTENT}
            created = container.create_item(body)
            assert_created(created, body, False, native)
            assert_native_body(native, body, compact=compact)
            assert_fields(container.read_item(body["id"], partition_key="pk"), body)
            if query:
                query_results = list(container.query_items(query='select * from c', partition_key='pk'))
                assert len(query_results) == 1
                assert_fields(query_results[0], body)
    finally:
        close = getattr(credential, "close", None)
        if close is not None:
            close()


@pytest.mark.cosmosEmulator
@skip_unless_token_auth()
def test_compact_utf8_item_write_with_aad_rust(variant_database, make_variant_container, monkeypatch, backend):
    # Source: tests/test_aad.py::TestAAD.test_compact_utf8_item_write_with_aad
    _token_credential_create(variant_database, make_variant_container, monkeypatch, backend, compact=True)


@pytest.mark.cosmosEmulator
@skip_unless_token_auth()
def test_aad_credentials_rust(variant_database, make_variant_container, monkeypatch, backend):
    # Source: tests/test_aad.py::TestAAD.test_aad_credentials
    _token_credential_create(variant_database, make_variant_container, monkeypatch, backend, compact=False, query=True)
