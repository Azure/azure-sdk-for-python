# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared checks that the priority option reaches each request the SDK sends.

They check that upsert_item, read_item and query_items pass the given priority
("High" or "Low") on to the request, and that any other value is rejected with
ValueError before a request is sent. They do not check how the service applies
the priority.
"""

from contextlib import contextmanager
from unittest.mock import patch

import pytest

from azure.cosmos import _rust


@contextmanager
def priority_request(operation, priority):
    """Watches one SDK request function and checks that every call carried the expected priority.

    Fails if the function was never called.
    """
    with patch.object(_rust, operation, wraps=getattr(_rust, operation)) as mock_request:
        yield
    assert mock_request.call_count > 0
    for call in mock_request.call_args_list:
        # The second argument is the prepared request.
        assert call.args[1].settings.priority == priority


def assert_priority_contract(container):
    """Upserts and reads two items with priority "High" and "Low", runs a query with
    "High", and checks that "Medium" is rejected before a request is sent.

    container must use pk as its partition key field.
    """
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
    with patch.object(_rust, "read_item", wraps=_rust.read_item) as mock_request:
        with pytest.raises(ValueError, match=r"^priority must be 'High' or 'Low'\.$"):
            container.read_item("item2", "pk2", priority="Medium")
    mock_request.assert_not_called()


async def assert_priority_contract_async(container):
    """Async version of assert_priority_contract."""
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
    with patch.object(_rust, "read_item_async", wraps=_rust.read_item_async) as mock_request:
        with pytest.raises(ValueError, match=r"^priority must be 'High' or 'Low'\.$"):
            await container.read_item("item2", "pk2", priority="Medium")
    mock_request.assert_not_called()
