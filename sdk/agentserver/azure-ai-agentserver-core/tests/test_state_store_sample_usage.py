# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Programmatic sample-flow coverage for the Foundry state-store sample."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.ai.agentserver.core.storage import (
    FoundryStateStore,
    FoundryStorageEndpoint,
    FoundryStoragePreconditionError,
)

_BASE_URL = "https://foundry.example.com/storage/"
_ENDPOINT = FoundryStorageEndpoint(storage_base_url=_BASE_URL)


def _make_response(status_code: int, body: object, *, headers: dict[str, str] | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = {} if headers is None else headers
    resp.text = MagicMock(return_value=json.dumps(body))
    return resp


def _make_store_with_responses(*responses: MagicMock) -> FoundryStateStore:
    store = FoundryStateStore.__new__(FoundryStateStore)
    store._endpoint = _ENDPOINT
    store._owns_credential = False
    store._name = "checkpoints/thread-abc"
    store._user_isolation = True
    store._item_ttl_seconds = 3600
    store._description = "Sample state store"
    store._tags = {}
    store._user_id = "user-42"
    mock_pipeline = AsyncMock()
    mock_pipeline.send_request = AsyncMock(side_effect=list(responses))
    mock_pipeline.close = AsyncMock()
    store._client = mock_pipeline
    return store


@pytest.mark.asyncio
async def test_state_store_sample_flow() -> None:
    store = _make_store_with_responses(
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "state_store",
                "name": "checkpoints/thread-abc",
                "user_isolation": True,
                "item_ttl_seconds": 3600,
                "description": "Sample state store",
                "tags": {},
                "created_at": 1,
                "updated_at": 1,
            },
        ),
        _make_response(
            201,
            {
                "id": "it_1",
                "object": "state_store.item",
                "key": "step-1",
                "etag": '"0x8DA"',
                "created_at": 2,
                "updated_at": 2,
            },
        ),
        _make_response(
            200,
            {
                "id": "it_1",
                "object": "state_store.item",
                "key": "step-1",
                "value": {"done": False, "attempt": 1},
                "tags": {"kind": "checkpoint"},
                "etag": '"0x8DA"',
                "created_at": 2,
                "updated_at": 2,
            },
        ),
        _make_response(
            200,
            {
                "id": "ss_1",
                "object": "state_store",
                "name": "checkpoints/thread-abc",
                "user_isolation": True,
                "item_ttl_seconds": 3600,
                "description": "Sample checkpoint store",
                "tags": {"scenario": "state-store-sample", "env": "dev"},
                "created_at": 1,
                "updated_at": 3,
            },
        ),
        _make_response(
            200,
            {
                "id": "it_1",
                "object": "state_store.item",
                "key": "step-1",
                "value": {"done": False, "attempt": 1},
                "tags": {"kind": "checkpoint"},
                "etag": '"0x8DA"',
                "created_at": 2,
                "updated_at": 2,
            },
        ),
        _make_response(
            200,
            {
                "id": "it_1",
                "object": "state_store.item",
                "key": "step-1",
                "etag": '"0x8DB"',
                "created_at": 2,
                "updated_at": 4,
            },
        ),
        _make_response(
            412,
            {"error": {"message": "etag mismatch"}},
            headers={"ETag": '"0x8DB"'},
        ),
        _make_response(
            201,
            {
                "id": "it_2",
                "object": "state_store.item",
                "key": "step-2",
                "etag": '"0x8DC"',
                "created_at": 5,
                "updated_at": 5,
            },
        ),
        _make_response(
            201,
            {
                "id": "it_3",
                "object": "state_store.item",
                "key": "audit-1",
                "etag": '"0x8DD"',
                "created_at": 6,
                "updated_at": 6,
            },
        ),
        _make_response(
            200,
            {
                "object": "list",
                "data": [
                    {
                        "id": "it_1",
                        "object": "state_store.item",
                        "key": "step-1",
                        "tags": {"kind": "checkpoint"},
                        "etag": '"0x8DB"',
                        "created_at": 2,
                        "updated_at": 4,
                    }
                ],
                "first_id": "it_1",
                "last_id": "it_1",
                "has_more": True,
            },
        ),
        _make_response(
            200,
            {
                "object": "list",
                "data": [
                    {
                        "id": "it_2",
                        "object": "state_store.item",
                        "key": "step-2",
                        "tags": {"kind": "checkpoint"},
                        "etag": '"0x8DC"',
                        "created_at": 5,
                        "updated_at": 5,
                    }
                ],
                "first_id": "it_2",
                "last_id": "it_2",
                "has_more": False,
            },
        ),
        _make_response(
            200,
            {"id": "it_3", "object": "state_store.item", "key": "audit-1", "deleted": True},
        ),
        _make_response(
            200,
            {"id": "ss_1", "object": "state_store", "name": "checkpoints/thread-abc", "deleted": True},
        ),
    )

    # This test drives a hand-built store double directly (bypassing the real
    # constructor/classmethod), so it exercises the store-resolution wire call
    # via the private helper get_or_create() delegates to, rather than the
    # classmethod itself (which constructs its own instance).
    store_info = await store._fetch_properties()
    assert store_info.id == "ss_1"

    created = await store.create_item("step-1", {"done": False, "attempt": 1}, tags={"kind": "checkpoint"})
    assert created.etag == '"0x8DA"'

    item = await store.get_item("step-1")
    assert item is not None
    assert item.value["attempt"] == 1

    updated_store = await store.update(
        description="Sample checkpoint store",
        tags={"scenario": "state-store-sample", "env": "dev"},
    )
    assert updated_store.tags is not None
    assert updated_store.tags["env"] == "dev"

    stale_item = await store.get_item("step-1")
    assert stale_item is not None
    await store.set_item("step-1", {"done": True, "attempt": 2}, tags={"kind": "checkpoint"})

    with pytest.raises(FoundryStoragePreconditionError) as exc:
        await store.set_item("step-1", {"done": True, "attempt": 3}, if_match=stale_item.etag)
    assert exc.value.current_etag == '"0x8DB"'

    await store.create_item("step-2", {"done": False, "attempt": 1}, tags={"kind": "checkpoint"})
    await store.create_item("audit-1", {"event": "created"}, tags={"kind": "audit"})

    first_page = await store.list_keys(tags={"kind": "checkpoint"}, limit=1, order="asc")
    assert [entry.key for entry in first_page.keys] == ["step-1"]
    assert first_page.has_more is True

    second_page = await store.list_keys(tags={"kind": "checkpoint"}, after=first_page.last_id, limit=1, order="asc")
    assert [entry.key for entry in second_page.keys] == ["step-2"]
    assert second_page.has_more is False

    deleted_item = await store.delete_item("audit-1")
    assert deleted_item.deleted is True

    deleted_store = await store.delete()
    assert deleted_store.deleted is True
