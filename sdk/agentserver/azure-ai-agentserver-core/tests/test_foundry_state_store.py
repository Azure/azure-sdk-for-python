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
    DeletedStateStore,
    DeletedStateStoreItem,
    FoundryStateStore,
    FoundryStorageConflictError,
    FoundryStorageEndpoint,
    FoundryStorageNotFoundError,
    StateStoreItemKeyPage,
    StateStore,
    StateStoreItem,
    StateStoreItemRef,
    StateStoreItemKey,
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


def _make_store_with_responses(
    *responses: MagicMock, name: str = "langGraphCheckpoints/thread-abc"
) -> FoundryStateStore:
    store = _make_store(responses[0], name=name)
    store._client.send_request = AsyncMock(side_effect=list(responses))
    return store


def _sent_request(store: FoundryStateStore) -> Any:
    return store._client.send_request.call_args[0][0]


def _state_store_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ss_1",
        "object": "state_store",
        "name": "checkpoints",
        "user_isolation": False,
        "item_ttl_seconds": 2592000,
        "description": None,
        "tags": {},
        "created_at": 1,
        "updated_at": 1,
    }
    body.update(overrides)
    return body


def _state_store(**overrides: Any) -> StateStore:
    return StateStore(_state_store_body(**overrides))


def _item_metadata_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "it_1",
        "object": "state_store.item",
        "key": "step/1",
        "etag": '"0x8DD"',
        "created_at": 10,
        "updated_at": 20,
    }
    body.update(overrides)
    return body


def _item_metadata(**overrides: Any) -> StateStoreItemRef:
    return StateStoreItemRef(_item_metadata_body(**overrides))


def _item_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "it_1",
        "object": "state_store.item",
        "key": "step/1",
        "value": {},
        "etag": '"0x8DD"',
        "created_at": 10,
        "updated_at": 20,
    }
    body.update(overrides)
    return body


def _item(**overrides: Any) -> StateStoreItem:
    return StateStoreItem(_item_body(**overrides))


def _key_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "it_1",
        "object": "state_store.item",
        "key": "step/1",
        "etag": '"0x8DD"',
        "created_at": 10,
        "updated_at": 20,
    }
    body.update(overrides)
    return body


def _key(**overrides: Any) -> StateStoreItemKey:
    return StateStoreItemKey(_key_body(**overrides))


# ---------------------------------------------------------------------------
# get_or_create (classmethod orchestration: fetch / create / conflict-refetch)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_or_create_returns_existing_store_when_present(monkeypatch: pytest.MonkeyPatch) -> None:
    info = _state_store()
    fetch = AsyncMock(return_value=info)
    create = AsyncMock()
    monkeypatch.setattr(FoundryStateStore, "_fetch_properties", fetch)
    monkeypatch.setattr(FoundryStateStore, "_create_properties", create)

    store = await FoundryStateStore.get_or_create("checkpoints", credential=MagicMock(), endpoint=_ENDPOINT)
    try:
        fetch.assert_awaited_once()
        create.assert_not_awaited()
        assert store.name == "checkpoints"
    finally:
        await store.aclose()


@pytest.mark.asyncio
async def test_get_or_create_creates_store_when_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    info = _state_store()
    fetch = AsyncMock(side_effect=FoundryStorageNotFoundError("not found"))
    create = AsyncMock(return_value=info)
    monkeypatch.setattr(FoundryStateStore, "_fetch_properties", fetch)
    monkeypatch.setattr(FoundryStateStore, "_create_properties", create)

    store = await FoundryStateStore.get_or_create("checkpoints", credential=MagicMock(), endpoint=_ENDPOINT)
    try:
        fetch.assert_awaited_once()
        create.assert_awaited_once()
        assert store.name == "checkpoints"
    finally:
        await store.aclose()


@pytest.mark.asyncio
async def test_get_or_create_refetches_when_create_races_with_another_caller(monkeypatch: pytest.MonkeyPatch) -> None:
    created_elsewhere = _state_store()
    fetch = AsyncMock(side_effect=[FoundryStorageNotFoundError("not found"), created_elsewhere])
    create = AsyncMock(side_effect=FoundryStorageConflictError("duplicate store"))
    monkeypatch.setattr(FoundryStateStore, "_fetch_properties", fetch)
    monkeypatch.setattr(FoundryStateStore, "_create_properties", create)

    store = await FoundryStateStore.get_or_create("checkpoints", credential=MagicMock(), endpoint=_ENDPOINT)
    try:
        assert fetch.await_count == 2
        create.assert_awaited_once()
        assert store.name == "checkpoints"
    finally:
        await store.aclose()


@pytest.mark.asyncio
async def test_get_or_create_closes_store_when_fetch_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(FoundryStateStore, "_fetch_properties", AsyncMock(side_effect=RuntimeError("boom")))
    closed = AsyncMock()
    monkeypatch.setattr(FoundryStateStore, "aclose", closed)

    with pytest.raises(RuntimeError, match="boom"):
        await FoundryStateStore.get_or_create("checkpoints", credential=MagicMock(), endpoint=_ENDPOINT)

    closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_or_create_closes_store_when_create_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        FoundryStateStore, "_fetch_properties", AsyncMock(side_effect=FoundryStorageNotFoundError("not found"))
    )
    monkeypatch.setattr(
        FoundryStateStore, "_create_properties", AsyncMock(side_effect=RuntimeError("create-fail"))
    )
    closed = AsyncMock()
    monkeypatch.setattr(FoundryStateStore, "aclose", closed)

    with pytest.raises(RuntimeError, match="create-fail"):
        await FoundryStateStore.get_or_create("checkpoints", credential=MagicMock(), endpoint=_ENDPOINT)

    closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_or_create_forwards_creation_options_to_create() -> None:
    info = _state_store(
        user_isolation=True,
        item_ttl_seconds=600,
        description="checkpoint store",
        tags={"team": "agents"},
    )
    store = _make_store(
        _make_response(
            201,
            _state_store_body(
                user_isolation=True,
                item_ttl_seconds=600,
                description="checkpoint store",
                tags={"team": "agents"},
            ),
        ),
        name="checkpoints",
        user_isolation=True,
        item_ttl_seconds=600,
        description="checkpoint store",
        tags={"team": "agents"},
    )

    result = await store._create_properties()

    request = _sent_request(store)
    assert json.loads(request.content.decode("utf-8")) == {
        "name": "checkpoints",
        "user_isolation": True,
        "item_ttl_seconds": 600,
        "description": "checkpoint store",
        "tags": {"team": "agents"},
    }
    assert result == info


# ---------------------------------------------------------------------------
# get() -- overloaded on key: None fetches the store descriptor, else an item
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_with_no_key_returns_the_store_descriptor() -> None:
    store_name = "langGraphCheckpoints/thread-abc"
    store = _make_store(
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "state_store",
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

    result = await store.get()

    request = _sent_request(store)
    assert request.method == "GET"
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment(store_name)}?api-version=v1"
    assert "x-ms-user-id" not in request.headers  # store-level ops never send the delegated user header
    assert result is not None
    assert result.name == store_name
    assert result.id == "ss_1"


@pytest.mark.asyncio
async def test_get_with_no_key_raises_when_store_is_absent() -> None:
    store = _make_store(_make_response(404, {"error": {"message": "not found"}}), name="checkpoints")

    with pytest.raises(FoundryStorageNotFoundError):
        await store.get()


@pytest.mark.asyncio
async def test_get_with_key_returns_state_item_with_value_and_metadata() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "id": "it_1",
                "object": "state_store.item",
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

    result = await store.get_item("step/1")

    request = _sent_request(store)
    assert request.method == "GET"
    assert request.headers["x-ms-user-id"] == "user-42"
    assert request.url == (
        f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}/items/{_encode_segment('step/1')}?api-version=v1"
    )
    assert result == _item(
        value={"done": True},
        tags={"kind": "checkpoint"},
    )


@pytest.mark.asyncio
async def test_get_with_key_returns_none_when_item_is_absent() -> None:
    store = _make_store(_make_response(404, {"error": {"message": "not found"}}), name="checkpoints")
    assert await store.get_item("missing") is None


# ---------------------------------------------------------------------------
# update() -- store mutable metadata (was update_metadata)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_sends_only_present_fields() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "state_store",
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

    result = await store.update(description="updated", tags={"env": "prod"})

    request = _sent_request(store)
    assert request.method == "PATCH"
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment('prefs')}?api-version=v1"
    assert json.loads(request.content.decode("utf-8")) == {"description": "updated", "tags": {"env": "prod"}}
    assert result.updated_at == 3


@pytest.mark.asyncio
async def test_update_with_only_description_omits_tags() -> None:
    store = _make_store(
        _make_response(200, _state_store_body(name="prefs", description="only-desc")),
        name="prefs",
    )

    await store.update(description="only-desc")

    request = _sent_request(store)
    assert json.loads(request.content.decode("utf-8")) == {"description": "only-desc"}


@pytest.mark.asyncio
async def test_update_with_only_tags_omits_description() -> None:
    store = _make_store(
        _make_response(200, _state_store_body(name="prefs", tags={"env": "prod"})),
        name="prefs",
    )

    await store.update(tags={"env": "prod"})

    request = _sent_request(store)
    assert json.loads(request.content.decode("utf-8")) == {"tags": {"env": "prod"}}


@pytest.mark.asyncio
async def test_update_with_no_arguments_sends_empty_body() -> None:
    store = _make_store(
        _make_response(200, _state_store_body(name="prefs")),
        name="prefs",
    )

    await store.update()

    request = _sent_request(store)
    assert json.loads(request.content.decode("utf-8")) == {}


# ---------------------------------------------------------------------------
# delete() -- overloaded on key: None deletes the store, else one item
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_with_no_key_deletes_the_store() -> None:
    store = _make_store(
        _make_response(200, {"id": "ss_1", "object": "state_store", "name": "prefs", "deleted": True}),
        name="prefs",
    )

    result = await store.delete()

    request = _sent_request(store)
    assert request.method == "DELETE"
    assert request.url == f"{_BASE_URL}state_stores/{_encode_segment('prefs')}?api-version=v1"
    assert "x-ms-user-id" not in request.headers
    assert result == DeletedStateStore({"id": "ss_1", "object": "state_store", "name": "prefs", "deleted": True})


@pytest.mark.asyncio
async def test_delete_with_key_returns_deleted_item_marker() -> None:
    store = _make_store(
        _make_response(200, {"id": "it_1", "object": "state_store.item", "key": "step/1", "deleted": True}),
        name="checkpoints",
        user_id="user-42",
    )

    result = await store.delete_item("step/1", if_match='"0x8DD"')

    request = _sent_request(store)
    assert request.method == "DELETE"
    assert request.headers["If-Match"] == '"0x8DD"'
    assert request.headers["x-ms-user-id"] == "user-42"
    assert result == DeletedStateStoreItem(
        {"id": "it_1", "object": "state_store.item", "key": "step/1", "deleted": True}
    )


# ---------------------------------------------------------------------------
# Item operations unaffected by the store-admin refactor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_item_posts_key_value_and_tags() -> None:
    store = _make_store(
        _make_response(
            201,
            {
                "id": "it_1",
                "object": "state_store.item",
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
    assert result == _item_metadata(etag='"0x8DC"', created_at=10, updated_at=10)


@pytest.mark.asyncio
async def test_set_puts_value_and_if_match_header() -> None:
    store = _make_store(
        _make_response(
            200,
            {
                "id": "it_1",
                "object": "state_store.item",
                "key": "step/1",
                "etag": '"0x8DD"',
                "created_at": 10,
                "updated_at": 20,
            },
            headers={"ETag": '"0x8DD"'},
        ),
        name="checkpoints",
    )

    result = await store.set_item("step/1", {"done": True}, tags={"kind": "checkpoint"}, if_match='"0x8DC"')

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
                "object": "state_store.item",
                "key": "step/1",
                "etag": '"0x8DD"',
                "created_at": 10,
                "updated_at": 20,
            },
        ),
        name="checkpoints",
    )

    await store.set_item("step/1", {"done": True}, require_exists=True)

    request = _sent_request(store)
    assert request.headers["If-Match"] == "*"


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
                        "object": "state_store.item",
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
    assert page == StateStoreItemKeyPage(
        keys=[_key(tags={"kind": "checkpoint"})],
        first_id="it_1",
        last_id="it_1",
        has_more=False,
    )


@pytest.mark.asyncio
async def test_list_keys_defaults_to_desc_order() -> None:
    store = _make_store(_make_response(200, {"object": "list", "data": [], "has_more": False}), name="checkpoints")

    await store.list_keys()

    request = _sent_request(store)
    assert (
        request.url == f"{_BASE_URL}state_stores/{_encode_segment('checkpoints')}/items:keys?api-version=v1&order=desc"
    )


def test_empty_key_is_rejected() -> None:
    store = _make_store(_make_response(200, {}), name="checkpoints")

    with pytest.raises(ValueError):
        store._item_path("")
