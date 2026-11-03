"""Creation ordering and cursor paging through the local state-store API."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import pytest

from azure.ai.agentserver.core.storage import FoundryStateStore, FoundryStorageBadRequestError, Order
from azure.ai.agentserver.core.storage import _local_state


@pytest.fixture()
def local_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.setattr(_local_state, "_now", lambda: 100)
    return tmp_path


async def _keys(store: FoundryStateStore, **options: Any) -> list[str]:
    return [item.key for item in (await store.list_keys(**options)).keys]


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["create_item", "set_item"])
async def test_same_second_creation_order_survives_reopen(local_root: Path, method: str) -> None:
    expected = [f"step-{index}" for index in range(12)]
    async with await FoundryStateStore.get_or_create("same-second") as store:
        for key in expected:
            created = await getattr(store, method)(key, {"key": key})
            assert created.created_at == 100
            assert isinstance(created.created_at, int)
        assert await _keys(store, order="asc") == expected

    async with await FoundryStateStore.get_or_create("same-second") as reopened:
        assert await _keys(reopened, order="desc") == list(reversed(expected))
        assert await _keys(reopened, limit=1) == [expected[-1]]
        item = await reopened.get_item(expected[-1])
        assert item is not None
        assert set(dict(item)) == {"id", "object", "key", "value", "tags", "etag", "created_at", "updated_at"}
        assert item.value == {"key": expected[-1]}


@pytest.mark.asyncio
async def test_updates_keep_position_and_recreation_gets_a_new_position(local_root: Path) -> None:
    async with await FoundryStateStore.get_or_create("mutations") as store:
        first = await store.create_item("first", {"value": 1})
        await store.set_item("second", {"value": 2})
        updated = await store.set_item("first", {"value": 3}, if_match=first.etag)
        assert updated.id == first.id
        assert updated.created_at == first.created_at
        assert updated.etag != first.etag
        assert await _keys(store, order="asc") == ["first", "second"]
        await store.delete_item("first")

    async with await FoundryStateStore.get_or_create("mutations") as reopened:
        recreated = await reopened.create_item("first", {"value": 4})
        assert recreated.id != first.id
        assert await _keys(reopened, order="asc") == ["second", "first"]
        assert await _keys(reopened, order="asc", after=first.id) == []
        assert await _keys(reopened, order="asc", before=first.id) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("order", ["asc", "desc"])
async def test_paging_traverses_creation_order_in_both_directions(local_root: Path, order: Order) -> None:
    expected = [f"step-{index}" for index in range(12)]
    if order == "desc":
        expected.reverse()
    async with await FoundryStateStore.get_or_create("pages") as store:
        for index in range(12):
            await store.set_item(f"step-{index}", {"index": index})
        page = await store.list_keys(order=order, limit=3)
        pages = [page]
        while page.has_more:
            assert page.last_id is not None
            page = await store.list_keys(order=order, limit=3, after=page.last_id)
            assert page.keys
            pages.append(page)
        assert [item.key for page in pages for item in page.keys] == expected
        for index in range(len(pages) - 1, 0, -1):
            previous = await store.list_keys(order=order, limit=3, before=pages[index].first_id)
            assert [item.key for item in previous.keys] == [item.key for item in pages[index - 1].keys]
            assert previous.has_more is (index > 1)


@pytest.mark.asyncio
@pytest.mark.parametrize("order", ["asc", "desc"])
@pytest.mark.parametrize("cursor", ["after", "before"])
async def test_tag_filter_does_not_remove_cursor_position(local_root: Path, order: Order, cursor: str) -> None:
    async with await FoundryStateStore.get_or_create("filtered-pages") as store:
        references = [
            await store.set_item(f"step-{index}", {"index": index}, tags={"kind": "keep" if index % 2 == 0 else "skip"})
            for index in range(12)
        ]
        ordered = list(range(12)) if order == "asc" else list(reversed(range(12)))
        pivot = ordered.index(5)
        candidates = ordered[pivot + 1 :] if cursor == "after" else ordered[:pivot]
        expected = [f"step-{index}" for index in candidates if index % 2 == 0]
        expected = expected[:2] if cursor == "after" else expected[-2:]
        page = await store.list_keys(tags={"kind": "keep"}, order=order, limit=2, **{cursor: references[5].id})
        assert [item.key for item in page.keys] == expected
        if page.keys:
            assert page.first_id == page.keys[0].id
            assert page.last_id == page.keys[-1].id


@pytest.mark.asyncio
async def test_legacy_file_order_is_stable_and_new_items_follow_it(local_root: Path) -> None:
    async with await FoundryStateStore.get_or_create("legacy") as store:
        for index in range(6):
            await store.set_item(f"step-{index}", {"index": index})
    path = next((local_root / "state_stores").glob("*.json"))
    document = json.loads(path.read_text(encoding="utf-8"))
    document.pop("_next_sequence", None)
    for item in document["items"].values():
        item.pop("_sequence", None)
    path.write_text(json.dumps(document, sort_keys=True), encoding="utf-8")
    legacy = sorted(document["items"].values(), key=lambda item: (item["created_at"], item["id"]))
    expected = [item["key"] for item in legacy]
    async with await FoundryStateStore.get_or_create("legacy") as reopened:
        assert await _keys(reopened, order="asc") == expected
        await reopened.set_item(expected[0], {"updated": True})
        await reopened.create_item("new", {"new": True})
    async with await FoundryStateStore.get_or_create("legacy") as reopened:
        assert await _keys(reopened, order="asc") == [*expected, "new"]


@pytest.mark.asyncio
async def test_expiry_preserves_surviving_order(local_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    now = [100]
    monkeypatch.setattr(_local_state, "_now", lambda: now[0])
    async with await FoundryStateStore.get_or_create("expiry", item_ttl_seconds=10) as store:
        await store.create_item("expired", {"value": 0})
        now[0] = 105
        for index in range(4):
            await store.create_item(f"live-{index}", {"value": index})
        now[0] = 111
        assert await _keys(store, order="asc") == [f"live-{index}" for index in range(4)]
        await store.create_item("expired", {"value": 5})
        assert await _keys(store, order="desc", limit=1) == ["expired"]


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, -1, 101, True])
async def test_invalid_page_size_is_rejected(local_root: Path, limit: int) -> None:
    async with await FoundryStateStore.get_or_create("invalid-limit") as store:
        await store.set_item("one", {"value": 1})
        with pytest.raises(FoundryStorageBadRequestError) as raised:
            await store.list_keys(limit=limit)
        assert raised.value.status_code == 400
        assert raised.value.param == "limit"


@pytest.mark.asyncio
async def test_invalid_sort_order_is_rejected(local_root: Path) -> None:
    async with await FoundryStateStore.get_or_create("invalid-order") as store:
        with pytest.raises(FoundryStorageBadRequestError) as raised:
            await store.list_keys(order=cast(Order, "invalid"))
        assert raised.value.status_code == 400
        assert raised.value.param == "order"


@pytest.mark.asyncio
async def test_legacy_order_survives_expiry_without_a_write(local_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    async with await FoundryStateStore.get_or_create("legacy-expiry", item_ttl_seconds=10) as store:
        await store.set_item("expired", {"value": 0})
    path = next((local_root / "state_stores").glob("*.json"))
    document = json.loads(path.read_text(encoding="utf-8"))
    document.pop("_next_sequence", None)
    for item in document["items"].values():
        item.pop("_sequence", None)
    path.write_text(json.dumps(document, sort_keys=True), encoding="utf-8")
    monkeypatch.setattr(_local_state, "_now", lambda: 111)
    async with await FoundryStateStore.get_or_create("legacy-expiry") as store:
        assert await _keys(store) == []
        await store.create_item("new", {"value": 1})
    async with await FoundryStateStore.get_or_create("legacy-expiry") as store:
        assert await _keys(store) == ["new"]


@pytest.mark.asyncio
async def test_creation_order_survives_a_new_process(local_root: Path) -> None:
    async with await FoundryStateStore.get_or_create("process-restart") as store:
        for index in range(4):
            await store.create_item(f"parent-{index}", {"index": index})
    script = """
import asyncio
from azure.ai.agentserver.core.storage import FoundryStateStore, _local_state

_local_state._now = lambda: 100

async def main():
    async with await FoundryStateStore.get_or_create("process-restart") as store:
        for index in range(4):
            await store.create_item(f"child-{index}", {"index": index})

asyncio.run(main())
"""
    subprocess.run([sys.executable, "-c", script], check=True, capture_output=True, text=True, timeout=30)
    async with await FoundryStateStore.get_or_create("process-restart") as reopened:
        assert await _keys(reopened, order="asc") == [
            *(f"parent-{index}" for index in range(4)),
            *(f"child-{index}" for index in range(4)),
        ]


@pytest.mark.asyncio
async def test_empty_missing_and_end_cursors(local_root: Path) -> None:
    async with await FoundryStateStore.get_or_create("cursor-boundaries") as store:
        empty = await store.list_keys()
        assert empty.keys == [] and not empty.has_more
        assert empty.first_id is None and empty.last_id is None
        first = await store.create_item("first", {"value": 1})
        last = await store.create_item("last", {"value": 2})
        assert await _keys(store, order="asc", before=first.id) == []
        assert await _keys(store, order="asc", after=last.id) == []
        assert await _keys(store, after="missing") == []
        assert await _keys(store, before="missing") == []


@pytest.mark.asyncio
async def test_missing_sequence_records_do_not_break_an_upgraded_store(local_root: Path) -> None:
    async with await FoundryStateStore.get_or_create("mixed-writers") as store:
        for index in range(4):
            await store.create_item(f"step-{index}", {"index": index})
    path = next((local_root / "state_stores").glob("*.json"))
    document = json.loads(path.read_text(encoding="utf-8"))
    document["items"]["step-1"].pop("_sequence")
    path.write_text(json.dumps(document, sort_keys=True), encoding="utf-8")
    async with await FoundryStateStore.get_or_create("mixed-writers") as reopened:
        previous = await _keys(reopened, order="asc")
        assert set(previous) == {f"step-{index}" for index in range(4)}
        await reopened.create_item("new", {"value": 5})
    async with await FoundryStateStore.get_or_create("mixed-writers") as reopened:
        assert await _keys(reopened, order="asc") == [*previous, "new"]
