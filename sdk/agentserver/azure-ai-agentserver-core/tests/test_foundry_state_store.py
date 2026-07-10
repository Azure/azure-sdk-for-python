# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for FoundryStateStore request construction and response handling."""

from __future__ import annotations

import base64
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.ai.agentserver.core.storage import (
    DeletedStateItem,
    DeletedStateStore,
    FoundryStateStore,
    FoundryStorageEndpoint,
    KeyPage,
    StateItem,
    StateItemMetadata,
    StateKey,
    StateStoreInfo,
)

_BASE_URL = "https://foundry.example.com/storage/"
_ENDPOINT = FoundryStorageEndpoint(storage_base_url=_BASE_URL)


def _encode_segment(value: str) -> str:
    encoded = base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def _make_response(status_code: int, body: Any, *, headers: dict[str, str] | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.text = MagicMock(return_value=json.dumps(body))
    return resp


def _make_store(
    response: MagicMock,
    *,
    name: str = "langGraphCheckpoints/thread-abc",
    user_isolation: bool = False,
    item_ttl_seconds: int = 2592000,
    description: str | None = None,
    tags: dict[str, str] | None = None,
    user_id: str | None = None,
) -> FoundryStateStore:
    store = FoundryStateStore.__new__(FoundryStateStore)
    store._endpoint = _ENDPOINT
    store._owns_credential = False
    store._name = name
    store._user_isolation = user_isolation
    store._item_ttl_seconds = item_ttl_seconds
    store._description = description
    store._tags = {} if tags is None else dict(tags)
    store._user_id = user_id
    mock_pipeline = AsyncMock()
    mock_pipeline.send_request = AsyncMock(return_value=response)
    mock_pipeline.close = AsyncMock()
    store._client = mock_pipeline
    return store


def _make_store_with_responses(*responses: MagicMock, name: str = "langGraphCheckpoints/thread-abc") -> FoundryStateStore:
    store = _make_store(responses[0], name=name)
    store._client.send_request = AsyncMock(side_effect=list(responses))
    return store


def _sent_request(store: FoundryStateStore) -> Any:
    return store._client.send_request.call_args[0][0]


@pytest.mark.asyncio
async def test_create_posts_store_descriptor() -> None:
    store = _make_store(
        _make_response(
            201,
            {
                "id": "ss_1",
                "object": "statestore",
                "name": "langGraphCheckpoints/thread-abc",
                "user_isolation": True,
                "item_ttl_seconds": 600,
                "description": "checkpoint store",
                "tags": {"team": "agents"},
                "created_at": 1,
                "updated_at": 1,
            },
        ),
        user_isolation=True,
        item_ttl_seconds=600,
        description="checkpoint store",
        tags={"team": "agents"},
    )

    result = await store.create()

    request = _sent_request(store)
    assert request.method == "POST"
    assert request.url == f"{_BASE_URL}state_stores?api-version=v1"
    assert request.headers["Content-Type"] == "application/json; charset=utf-8"
    assert "x-ms-user-id" not in request.headers
    assert json.loads(request.content.decode("utf-8")) == {
        "name": "langGraphCheckpoints/thread-abc",
        "user_isolation": True,
        "item_ttl_seconds": 600,
        "description": "checkpoint store",
        "tags": {"team": "agents"},
    }
    assert result == StateStoreInfo(
        id="ss_1",
        name="langGraphCheckpoints/thread-abc",
        user_isolation=True,
        item_ttl_seconds=600,
        description="checkpoint store",
        tags={"team": "agents"},
        created_at=1,
        updated_at=1,
    )


@pytest.mark.asyncio
async def test_create_or_get_returns_created_store_when_absent() -> None:
    store = _make_store(
        _make_response(
            201,
            {
                "id": "ss_1",
                "object": "statestore",
                "name": "checkpoints",
                "user_isolation": False,
                "item_ttl_seconds": 2592000,
                "description": None,
                "tags": {},
                "created_at": 1,
                "updated_at": 1,
            },
        ),
        name="checkpoints",
    )

    result = await store.create_or_get()

    request = _sent_request(store)
    assert request.method == "POST"
    assert request.url == f"{_BASE_URL}state_stores?api-version=v1"
    assert result.name == "checkpoints"


@pytest.mark.asyncio
async def test_create_or_get_fetches_existing_store_on_conflict() -> None:
    store = _make_store_with_responses(
        _make_response(409, {"error": {"message": "duplicate store"}}),
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "statestore",
                "name": "checkpoints",
                "user_isolation": False,
                "item_ttl_seconds": 2592000,
                "description": "existing",
                "tags": {"env": "dev"},
                "created_at": 1,
                "updated_at": 2,
            },
        ),
        name="checkpoints",
    )

    result = await store.create_or_get()

    first_request = store._client.send_request.call_args_list[0][0][0]
    second_request = store._client.send_request.call_args_list[1][0][0]
    assert first_request.method == "POST"
    assert second_request.method == "GET"
    assert second_request.url == f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}?api-version=v1"
    assert result.description == "existing"
    assert result.tags == {"env": "dev"}


@pytest.mark.asyncio
async def test_get_or_create_returns_existing_store_when_present() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "statestore",
                "name": "checkpoints",
                "user_isolation": False,
                "item_ttl_seconds": 2592000,
                "description": "existing",
                "tags": {"env": "dev"},
                "created_at": 1,
                "updated_at": 2,
            },
        ),
        name="checkpoints",
    )

    result = await store.get_or_create()

    request = _sent_request(store)
    assert request.method == "GET"
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}?api-version=v1"
    assert result.description == "existing"
    assert result.tags == {"env": "dev"}


@pytest.mark.asyncio
async def test_get_or_create_creates_store_when_absent() -> None:
    store = _make_store_with_responses(
        _make_response(404, {"error": {"message": "not found"}}),
        _make_response(
            201,
            {
                "id": "ss_1",
                "object": "statestore",
                "name": "checkpoints",
                "user_isolation": False,
                "item_ttl_seconds": 2592000,
                "description": None,
                "tags": {},
                "created_at": 1,
                "updated_at": 1,
            },
        ),
        name="checkpoints",
    )

    result = await store.get_or_create()

    first_request = store._client.send_request.call_args_list[0][0][0]
    second_request = store._client.send_request.call_args_list[1][0][0]
    assert first_request.method == "GET"
    assert second_request.method == "POST"
    assert second_request.url == f"{_BASE_URL}state_stores?api-version=v1"
    assert result.name == "checkpoints"


@pytest.mark.asyncio
async def test_get_or_create_fetches_store_when_create_races_with_another_caller() -> None:
    store = _make_store_with_responses(
        _make_response(404, {"error": {"message": "not found"}}),
        _make_response(409, {"error": {"message": "duplicate store"}}),
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "statestore",
                "name": "checkpoints",
                "user_isolation": False,
                "item_ttl_seconds": 2592000,
                "description": "created elsewhere",
                "tags": {"env": "dev"},
                "created_at": 1,
                "updated_at": 2,
            },
        ),
        name="checkpoints",
    )

    result = await store.get_or_create()

    requests = [call_args[0][0] for call_args in store._client.send_request.call_args_list]
    assert [request.method for request in requests] == ["GET", "POST", "GET"]
    assert requests[2].url == f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}?api-version=v1"
    assert result.description == "created elsewhere"


@pytest.mark.asyncio
async def test_get_properties_uses_base64url_store_name() -> None:
    store_name = "langGraphCheckpoints/thread-abc"
    store = _make_store(
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "statestore",
                "name": store_name,
                "user_isolation": False,
                "item_ttl_seconds": 2592000,
                "description": None,
                "tags": {},
                "created_at": 1,
                "updated_at": 2,
            },
        ),
        name=store_name,
    )

    result = await store.get_properties()

    request = _sent_request(store)
    assert request.method == "GET"
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment(store_name)}?api-version=v1"
    assert result.name == store_name
    assert result.id == "ss_1"


@pytest.mark.asyncio
async def test_update_metadata_sends_only_present_fields() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "statestore",
                "name": "prefs",
                "user_isolation": False,
                "item_ttl_seconds": 2592000,
                "description": "updated",
                "tags": {"env": "prod"},
                "created_at": 1,
                "updated_at": 3,
            },
        ),
        name="prefs",
    )

    result = await store.update_metadata(description="updated", tags={"env": "prod"})

    request = _sent_request(store)
    assert request.method == "PATCH"
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment('prefs')}?api-version=v1"
    assert json.loads(request.content.decode("utf-8")) == {"description": "updated", "tags": {"env": "prod"}}
    assert result.updated_at == 3


@pytest.mark.asyncio
async def test_delete_store_returns_deleted_marker() -> None:
    store = _make_store(
        _make_response(
            200,
            {"id": "ss_1", "object": "statestore.deleted", "name": "prefs", "deleted": True},
        ),
        name="prefs",
    )

    result = await store.delete_store()

    request = _sent_request(store)
    assert request.method == "DELETE"
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment('prefs')}?api-version=v1"
    assert result == DeletedStateStore(id="ss_1", name="prefs", deleted=True)


@pytest.mark.asyncio
async def test_create_item_posts_key_value_and_tags() -> None:
    store = _make_store(
        _make_response(
            201,
            {
                "id": "it_1",
                "object": "statestore_item",
                "key": "step/1",
                "etag": '"0x8DC"',
                "created_at": 10,
                "updated_at": 10,
            },
        ),
        name="checkpoints",
    )

    result = await store.create_item("step/1", {"done": False}, tags={"kind": "checkpoint"})

    request = _sent_request(store)
    assert request.method == "POST"
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}/items?api-version=v1"
    assert json.loads(request.content.decode("utf-8")) == {
        "key": "step/1",
        "value": {"done": False},
        "tags": {"kind": "checkpoint"},
    }
    assert "If-Match" not in request.headers
    assert result == StateItemMetadata(
        id="it_1",
        key="step/1",
        etag='"0x8DC"',
        created_at=10,
        updated_at=10,
    )


@pytest.mark.asyncio
async def test_set_puts_value_and_if_match_header() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "id": "it_1",
                "object": "statestore_item",
                "key": "step/1",
                "etag": '"0x8DD"',
                "created_at": 10,
                "updated_at": 20,
            },
            headers={"ETag": '"0x8DD"'},
        ),
        name="checkpoints",
    )

    result = await store.set("step/1", {"done": True}, tags={"kind": "checkpoint"}, if_match='"0x8DC"')

    request = _sent_request(store)
    assert request.method == "PUT"
    assert request.url == (
        f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}/items/{_encode_segment('step/1')}?api-version=v1"
    )
    assert request.headers["If-Match"] == '"0x8DC"'
    assert json.loads(request.content.decode("utf-8")) == {"value": {"done": True}, "tags": {"kind": "checkpoint"}}
    assert result.etag == '"0x8DD"'


@pytest.mark.asyncio
async def test_set_require_exists_uses_wildcard_if_match() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "id": "it_1",
                "object": "statestore_item",
                "key": "step/1",
                "etag": '"0x8DD"',
                "created_at": 10,
                "updated_at": 20,
            },
        ),
        name="checkpoints",
    )

    await store.set("step/1", {"done": True}, require_exists=True)

    request = _sent_request(store)
    assert request.headers["If-Match"] == "*"


@pytest.mark.asyncio
async def test_get_returns_state_item_with_value_and_metadata() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "id": "it_1",
                "object": "statestore_item",
                "key": "step/1",
                "value": {"done": True},
                "tags": {"kind": "checkpoint"},
                "etag": '"0x8DD"',
                "created_at": 10,
                "updated_at": 20,
            },
        ),
        name="checkpoints",
        user_id="user-42",
    )

    result = await store.get("step/1")

    request = _sent_request(store)
    assert request.method == "GET"
    assert request.headers["x-ms-user-id"] == "user-42"
    assert request.url == (
        f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}/items/{_encode_segment('step/1')}?api-version=v1"
    )
    assert result == StateItem(
        id="it_1",
        key="step/1",
        value={"done": True},
        tags={"kind": "checkpoint"},
        etag='"0x8DD"',
        created_at=10,
        updated_at=20,
    )


@pytest.mark.asyncio
async def test_get_returns_none_when_item_is_absent() -> None:
    store = _make_store(_make_response(404, {"error": {"message": "not found"}}), name="checkpoints")
    assert await store.get("missing") is None


@pytest.mark.asyncio
async def test_delete_item_returns_deleted_marker() -> None:
    store = _make_store(
        _make_response(
            200,
            {"id": "it_1", "object": "statestore_item.deleted", "key": "step/1", "deleted": True},
        ),
        name="checkpoints",
        user_id="user-42",
    )

    result = await store.delete("step/1", if_match='"0x8DD"')

    request = _sent_request(store)
    assert request.method == "DELETE"
    assert request.headers["If-Match"] == '"0x8DD"'
    assert request.headers["x-ms-user-id"] == "user-42"
    assert result == DeletedStateItem(id="it_1", key="step/1", deleted=True)


@pytest.mark.asyncio
async def test_list_keys_uses_query_parameters_and_returns_page() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "object": "list",
                "data": [
                    {
                        "id": "it_1",
                        "object": "statestore_item",
                        "key": "step/1",
                        "tags": {"kind": "checkpoint"},
                        "etag": '"0x8DD"',
                        "created_at": 10,
                        "updated_at": 20,
                    }
                ],
                "first_id": "it_1",
                "last_id": "it_1",
                "has_more": False,
            },
        ),
        name="checkpoints",
        user_id="user-42",
    )

    page = await store.list_keys(tags={"kind": "checkpoint", "phase": "run"}, limit=10, after="it_0", order="asc")

    request = _sent_request(store)
    assert request.method == "GET"
    assert request.headers["x-ms-user-id"] == "user-42"
    assert request.url == (
        f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}/items:keys"
        "?api-version=v1&tags.kind=checkpoint&tags.phase=run&limit=10&after=it_0&order=asc"
    )
    assert page == KeyPage(
        keys=[
            StateKey(
                id="it_1",
                key="step/1",
                tags={"kind": "checkpoint"},
                etag='"0x8DD"',
                created_at=10,
                updated_at=20,
            )
        ],
        first_id="it_1",
        last_id="it_1",
        has_more=False,
    )


@pytest.mark.asyncio
async def test_list_keys_defaults_to_desc_order() -> None:
    store = _make_store(_make_response(200, {"object": "list", "data": [], "has_more": False}), name="checkpoints")

    await store.list_keys()

    request = _sent_request(store)
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}/items:keys?api-version=v1&order=desc"


def test_empty_key_is_rejected() -> None:
    store = _make_store(_make_response(200, {}), name="checkpoints")

    with pytest.raises(ValueError):
        store._item_path("")
