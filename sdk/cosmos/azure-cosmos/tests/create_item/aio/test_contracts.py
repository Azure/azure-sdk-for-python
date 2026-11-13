# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async create assertions retained from original composite tests."""

from copy import deepcopy
import json
import os
import uuid

import pytest
import pytest_asyncio

from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient
from auth._token_credentials import make_async_token_credential, skip_unless_token_auth
from config import clients
from create_item._contract_cases import (
    AAD_CONTENT, COMPACT_CONTENT, EMOJI_CASES, INVALID_IDS, MEBIBYTE,
    assert_native_body, assert_stored_sequence, large_cjk_body,
)
from create_item._input_variants import assert_created, assert_fields, observe_native_create
from create_item._input_variants import (  # pylint: disable=unused-import
    _make_variant_container_fixture, _variant_database_fixture,
)

pytestmark = [
    pytest.mark.asyncio, 
    pytest.mark.parametrize("backend", ["rust", "core-python"]),
]


@pytest_asyncio.fixture(name="contract_client")
async def _contract_client_fixture(backend, request):
    async with clients.create_data_client_async(
        _backend="rust" if backend == "rust" else "core-python", timeout=60,
        **getattr(request, "param", {}),
    ) as client:
        yield client


def target(client, database, container):
    return client.get_database_client(database.id).get_container_client(container.id)


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("item_id", INVALID_IDS)
async def test_create_illegal_characters_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, item_id
):
    # Source: tests/test_resource_id_async.py::TestResourceIdsAsync.test_create_illegal_characters_async
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/id")))
    native = observe_native_create(monkeypatch, contract_client, backend, asynchronous=True)
    if len(item_id) > 1024:
        with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
            await container.create_item({"id": item_id})
        assert caught.value.status_code == 400
        if native is not None:
            native.assert_called_once()
    else:
        with pytest.raises(ValueError):
            await container.create_item({"id": item_id})
        if native is not None:
            native.assert_not_called()


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("ttl", [0, None, -10])
async def test_invalid_document_ttl_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, ttl
):
    # Source: tests/test_ttl.py::TestTimeToLive.test_collection_and_document_ttl_values
    container = target(
        contract_client, variant_database, make_variant_container(PartitionKey(path="/id"), default_ttl=10)
    )
    native = observe_native_create(monkeypatch, contract_client, backend, asynchronous=True)
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        await container.create_item({"id": uuid.uuid4().hex, "name": "sample document", "key": "value", "ttl": ttl})
    assert caught.value.status_code == 400
    if native is not None:
        native.assert_called_once()


async def _round_trip_emoji_document(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
):
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/pk")))
    native = observe_native_create(monkeypatch, contract_client, backend, asynchronous=True)
    body = {"id": uuid.uuid4().hex, "pk": "pk", "multibyte_content": content}
    created = await container.create_item(body)
    assert_created(created, body, False, native)
    if via_query:
        rows = [item async for item in container.query_items(
            "SELECT * FROM c WHERE c.id = @id", parameters=[{"name": "@id", "value": body["id"]}], partition_key="pk"
        )]
        assert len(rows) == 1
        read = rows[0]
    else:
        read = await container.read_item(body["id"], partition_key="pk")
    assert_fields(read, body)
    assert read["multibyte_content"].encode("utf-8") == content.encode("utf-8")


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("via_query,content", [param for param in EMOJI_CASES if param.id == "point-read"])
async def test_round_trip_emoji_document_through_full_sdk_stack_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
):
    # Source: tests/test_encoding_async.py::TestEncodingAsync.test_round_trip_emoji_document_through_full_sdk_stack_async
    await _round_trip_emoji_document(
        variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
    )


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("via_query,content", [param for param in EMOJI_CASES if param.id == "query"])
async def test_round_trip_emoji_document_via_query_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
):
    # Source: tests/test_encoding_async.py::TestEncodingAsync.test_round_trip_emoji_document_via_query_async
    await _round_trip_emoji_document(
        variant_database, make_variant_container, contract_client, monkeypatch, backend, via_query, content
    )


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("contract_client", [{"enable_compact_utf8_item_writes": True}], indirect=True)
async def test_compact_utf8_create_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend
):
    # Source: tests/test_encoding_async.py::TestEncodingAsync.test_compact_utf8_item_writes_through_full_sdk_stack_async
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/pk")))
    native = observe_native_create(monkeypatch, contract_client, backend, asynchronous=True)
    body = {"id": uuid.uuid4().hex, "pk": "\u65e5\u672c", "content": COMPACT_CONTENT}
    created = await container.create_item(body)
    assert_created(created, body, False, native)
    assert_native_body(native, body, compact=True)
    assert_fields(await container.read_item(body["id"], partition_key=body["pk"]), body)


async def _large_cjk_create(variant_database, make_variant_container, monkeypatch, backend, compact):
    owned = make_variant_container(PartitionKey(path="/pk"))
    body = large_cjk_body()
    encoded = json.dumps(body, separators=(",", ":"), ensure_ascii=not compact).encode("utf-8")
    assert (len(encoded) < 2 * MEBIBYTE) == compact
    async with clients.create_data_client_async(
        _backend=backend,
        enable_compact_utf8_item_writes=compact, timeout=60,
    ) as client:
        container = target(client, variant_database, owned)
        native = observe_native_create(monkeypatch, client, backend, asynchronous=True)
        if compact:
            created = await container.create_item(body)
            assert_created(created, body, False, native)
            assert_fields(await container.read_item(body["id"], partition_key="pk"), body)
        else:
            with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
                await container.create_item(body)
            assert caught.value.status_code == 413
        assert_native_body(native, body, compact=compact)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
async def test_compact_utf8_large_cjk_item_stays_under_wire_limit_rust(
    variant_database, make_variant_container, monkeypatch, backend
):
    # Source: tests/test_encoding_async.py::TestEncodingAsync.test_compact_utf8_large_cjk_item_stays_under_wire_limit_async
    await _large_cjk_create(variant_database, make_variant_container, monkeypatch, backend, compact=True)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
async def test_default_ascii_escaping_rejects_large_cjk_item_rust(
    variant_database, make_variant_container, monkeypatch, backend
):
    # Source: tests/test_encoding_async.py::TestEncodingAsync.test_default_ascii_escaping_rejects_large_cjk_item_async
    await _large_cjk_create(variant_database, make_variant_container, monkeypatch, backend, compact=False)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("no_response", [False, True])
async def test_create_response_headers_advance_lsn_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend, no_response
):
    # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_point_operation_headers_async
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/company")))
    first = await container.upsert_item({"id": uuid.uuid4().hex, "company": "Microsoft"})
    lsn = int(first.get_response_headers()["lsn"])
    native = observe_native_create(monkeypatch, contract_client, backend, asynchronous=True)
    body = {"id": uuid.uuid4().hex, "company": "Microsoft"}
    created = await container.create_item(body, no_response=no_response)
    assert_created(created, body, no_response, native)
    assert created.get_response_headers()
    assert int(created.get_response_headers()["lsn"]) == lsn + 1


async def _document_crud_create_persistence(
    variant_database, make_variant_container, contract_client, monkeypatch, backend
):
    container = target(contract_client, variant_database, make_variant_container(PartitionKey(path="/pk")))
    native = observe_native_create(monkeypatch, contract_client, backend, asynchronous=True)
    original = {"name": "sample document", "spam": "eggs", "key": "value", "pk": "pk"}
    body = deepcopy(original)
    assert await container.create_item(body, enable_automatic_id_generation=True, no_response=True) == {}
    generated = await container.create_item(body, enable_automatic_id_generation=True, no_response=False)
    explicit_body = dict(body, id=uuid.uuid4().hex)
    explicit = await container.create_item(explicit_body, no_response=False)
    assert body == original
    assert_fields(generated, original)
    assert_fields(explicit, explicit_body)
    # All three writes use this partition in a new, empty container. Query keeps
    # the original persistence/count assertion independent of read-feed paging.
    stored = [item async for item in container.query_items("SELECT * FROM c", partition_key="pk")]
    assert_stored_sequence(stored, original, generated, explicit)
    if native is not None:
        assert native.call_count == 3
        assert {call.args[1].item_id for call in native.call_args_list} == {item["id"] for item in stored}
    with pytest.raises(exceptions.CosmosResourceExistsError) as caught:
        await container.create_item(explicit_body)
    assert caught.value.status_code == 409
    assert len([item async for item in container.query_items("SELECT * FROM c", partition_key="pk")]) == 3


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.parametrize("contract_client", [{"no_response_on_write": False}], indirect=True)
async def test_document_crud_create_persistence_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend
):
    # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_document_crud_async
    await _document_crud_create_persistence(
        variant_database, make_variant_container, contract_client, monkeypatch, backend
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("contract_client", [{"no_response_on_write": True}], indirect=True)
async def test_document_crud_response_payload_on_write_disabled_rust(
    variant_database, make_variant_container, contract_client, monkeypatch, backend
):
    # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_document_crud_async
    await _document_crud_create_persistence(
        variant_database, make_variant_container, contract_client, monkeypatch, backend
    )


async def _token_credential_create(variant_database, make_variant_container, monkeypatch, backend, compact, query=False):
    owned = make_variant_container(PartitionKey(path="/pk"))
    credential = make_async_token_credential()
    try:
        async with CosmosClient(
            os.environ["ACCOUNT_HOST"], credential, _backend=backend,
            enable_compact_utf8_item_writes=compact, timeout=60,
        ) as client:
            container = target(client, variant_database, owned)
            native = observe_native_create(monkeypatch, client, backend, asynchronous=True)
            body = {"id": uuid.uuid4().hex, "pk": "pk", "content": AAD_CONTENT}
            created = await container.create_item(body)
            assert_created(created, body, False, native)
            assert_native_body(native, body, compact=compact)
            assert_fields(await container.read_item(body["id"], partition_key="pk"), body)
            if query:
                query_results = [item async for item in container.query_items(query='select * from c', partition_key='pk')]
                assert len(query_results) == 1
                assert_fields(query_results[0], body)
    finally:
        close = getattr(credential, "close", None)
        if close is not None:
            await close()


@pytest.mark.cosmosEmulator
@skip_unless_token_auth()
async def test_compact_utf8_item_write_with_aad_rust(variant_database, make_variant_container, monkeypatch, backend):
    # Source: tests/test_aad_async.py::TestAADAsync.test_compact_utf8_item_write_with_aad_async
    await _token_credential_create(variant_database, make_variant_container, monkeypatch, backend, compact=True)


@pytest.mark.cosmosEmulator
@skip_unless_token_auth()
async def test_aad_credentials_rust(variant_database, make_variant_container, monkeypatch, backend):
    # Source: tests/test_aad_async.py::TestAADAsync.test_aad_credentials_async
    await _token_credential_create(variant_database, make_variant_container, monkeypatch, backend, compact=False, query=True)
