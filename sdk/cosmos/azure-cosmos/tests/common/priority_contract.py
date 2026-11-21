# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run original priority inputs through the real compiled binding, not legacy hooks.

These assertions cover prepared settings, not service-side priority enforcement.
The typed Rust path rejects unsupported priority strings with ValueError locally instead of
sending it for the legacy HTTP 400 response.
"""

from contextlib import contextmanager
from unittest.mock import patch

import pytest

from azure.cosmos import _rust


@contextmanager
def priority_request(operation, priority):
    with patch.object(_rust, operation, wraps=getattr(_rust, operation)) as native:
        yield
    assert native.call_count > 0
    for call in native.call_args_list:
        assert call.args[1].settings.priority == priority


def assert_priority_contract(container):
    for identifier, key, priority in (
        ("item1", "pk1", "High"),
        ("item2", "pk2", "Low"),
    ):
        with priority_request("upsert_item", priority):
            container.upsert_item({"id": identifier, "pk": key}, priority=priority)
    for identifier, key, priority in (
        ("item1", "pk1", "High"),
        ("item2", "pk2", "Low"),
    ):
        with priority_request("read_item", priority):
            item = container.read_item(identifier, key, priority=priority)
        assert item["id"] == identifier
    with priority_request("fetch_page_with_cursor", "High"):
        rows = list(container.query_items("Select * from c", partition_key="pk1", priority="High"))
    assert any(row["id"] == "item1" for row in rows)
    with patch.object(_rust, "read_item", wraps=_rust.read_item) as native:
        with pytest.raises(ValueError, match=r"^priority must be 'High' or 'Low'\.$"):
            container.read_item("item2", "pk2", priority="Medium")
    native.assert_not_called()


async def assert_priority_contract_async(container):
    for identifier, key, priority in (
        ("item1", "pk1", "High"),
        ("item2", "pk2", "Low"),
    ):
        with priority_request("upsert_item_async", priority):
            await container.upsert_item({"id": identifier, "pk": key}, priority=priority)
    for identifier, key, priority in (
        ("item1", "pk1", "High"),
        ("item2", "pk2", "Low"),
    ):
        with priority_request("read_item_async", priority):
            item = await container.read_item(identifier, key, priority=priority)
        assert item["id"] == identifier
    with priority_request("fetch_page_with_cursor_async", "High"):
        rows = [
            row async for row in container.query_items(
                "Select * from c", partition_key="pk1", priority="High"
            )
        ]
    assert any(row["id"] == "item1" for row in rows)
    with patch.object(_rust, "read_item_async", wraps=_rust.read_item_async) as native:
        with pytest.raises(ValueError, match=r"^priority must be 'High' or 'Low'\.$"):
            await container.read_item("item2", "pk2", priority="Medium")
    native.assert_not_called()
