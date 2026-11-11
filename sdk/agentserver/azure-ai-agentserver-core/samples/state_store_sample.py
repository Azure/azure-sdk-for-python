# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: state_store_sample.py

DESCRIPTION:
    Demonstrates the explicit Foundry state-store client (`FoundryStateStore`):
    resolving a store with `get_or_create`, item create/update/get/delete,
    metadata updates, optimistic concurrency, and tag-filtered key listing.

USAGE:
    python state_store_sample.py

    Set these environment variables before running:
      1) FOUNDRY_PROJECT_ENDPOINT - the Azure AI Foundry project endpoint.

    The sample authenticates with DefaultAzureCredential, so sign in with the
    Azure CLI (`az login`) or configure another supported credential source.
    Requires the `azure-identity` package.
"""

import asyncio
from uuid import uuid4

from azure.ai.agentserver.core.storage import (
    FoundryStateStore,
    FoundryStoragePreconditionError,
)


async def create_and_get_item(store: FoundryStateStore) -> None:
    """Create an item, then fetch it back."""
    created = await store.create_item(
        "step-1",
        {"done": False, "attempt": 1},
        tags={"kind": "checkpoint"},
    )
    print(f"created step-1 with etag={created.etag}")

    item = await store.get_item("step-1")
    assert item is not None
    print(f"get step-1 -> value={item.value!r}, tags={item.tags}, etag={item.etag}")


async def update_metadata(store: FoundryStateStore) -> None:
    """Update mutable store metadata."""
    info = await store.update(
        description="Sample checkpoint store",
        tags={"scenario": "state-store-sample", "env": "dev"},
    )
    print(f"updated store metadata -> description={info.description!r}, tags={info.tags}")


async def optimistic_concurrency(store: FoundryStateStore) -> None:
    """Guard a read-modify-write with if_match and handle the conflict."""
    item = await store.get_item("step-1")
    assert item is not None

    await store.set_item("step-1", {"done": True, "attempt": 2}, tags={"kind": "checkpoint"})

    try:
        await store.set_item(
            "step-1",
            {"done": True, "attempt": 3},
            tags={"kind": "checkpoint"},
            if_match=item.etag,
        )
    except FoundryStoragePreconditionError as err:
        print(f"lost the race as expected; current_etag={err.current_etag}")


async def list_with_tags(store: FoundryStateStore) -> None:
    """List keys filtered by tag and page using last_id."""
    await store.create_item("step-2", {"done": False, "attempt": 1}, tags={"kind": "checkpoint"})
    await store.create_item("audit-1", {"event": "created"}, tags={"kind": "audit"})

    page = await store.list_keys(tags={"kind": "checkpoint"}, limit=1, order="asc")
    while True:
        print(f"checkpoint keys: {[entry.key for entry in page.keys]}")
        if not page.has_more or page.last_id is None:
            break
        page = await store.list_keys(tags={"kind": "checkpoint"}, after=page.last_id, limit=1, order="asc")


async def delete_item_and_store(store: FoundryStateStore) -> None:
    """Delete one item, then cascade-delete the whole store."""
    deleted_item = await store.delete_item("audit-1")
    print(f"deleted item -> key={deleted_item.key}, deleted={deleted_item.deleted}")

    deleted_store = await store.delete()
    print(f"deleted store -> name={deleted_store.name}, deleted={deleted_store.deleted}")


async def main() -> None:
    store_name = f"checkpoints/sample-thread-{uuid4().hex}"
    # get_or_create resolves (or creates, on first use) the server-side store
    # resource in one call, so there is no separate lifecycle step before
    # reading or writing items.
    store = await FoundryStateStore.get_or_create(
        store_name,
        user_isolation=True,
        item_ttl_seconds=3600,
        description="Sample state store",
    )
    async with store:
        print(f"using store name={store.name}")
        await create_and_get_item(store)
        await update_metadata(store)
        await optimistic_concurrency(store)
        await list_with_tags(store)
        await delete_item_and_store(store)


if __name__ == "__main__":
    asyncio.run(main())
