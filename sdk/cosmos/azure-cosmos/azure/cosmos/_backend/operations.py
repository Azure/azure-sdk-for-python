# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Operation names, and the tables that map them to binding functions.

Each operation has a name (the ``OP_*`` constants). Dispatch means looking up
which binding function to call for one of those names.

Operations that return a single reply use ``OP_TO_BINDING_METHOD``. Operations
that return pages use one of the two page tables instead, depending on whether
they keep a cursor between pages.

These tables hold names and data only. They say nothing about which operations
are allowed to fall back to the legacy path, so adding an operation here does
not mean writing a new method on the backend."""

from __future__ import annotations

# Operation discriminator values for ``PreparedRequest.op``.
OP_CREATE_DATABASE = "create_database"
OP_CREATE_CONTAINER = "create_container"
OP_READ_CONTAINER = "read_container"
OP_CREATE_ITEM = "create_item"
OP_DELETE_DATABASE = "delete_database"
OP_DELETE_CONTAINER = "delete_container"
OP_REPLACE_CONTAINER = "replace_container"
OP_DELETE_ITEM = "delete_item"
OP_READ_DATABASE = "read_database"
OP_READ_ITEM = "read_item"
OP_UPSERT_ITEM = "upsert_item"
OP_REPLACE_ITEM = "replace_item"
OP_PATCH_ITEM = "patch_item"
OP_QUERY_ITEMS = "query_items"
OP_QUERY_DATABASES = "query_databases"
OP_LIST_CONTAINERS = "list_containers"
OP_QUERY_CONTAINERS = "query_containers"
OP_READ_ALL_ITEMS = "read_all_items"
OP_QUERY_CHANGE_FEED = "query_items_change_feed"
OP_LIST_DATABASES = "list_databases"
OP_READ_FEED_RANGES = "read_feed_ranges"
OP_FEED_RANGE_FROM_PARTITION_KEY = "feed_range_from_partition_key"
OP_IS_FEED_RANGE_SUBSET = "is_feed_range_subset"
OP_READ_OFFER = "read_offer"
OP_REPLACE_OFFER = "replace_offer"


# ``PreparedRequest.op`` -> binding function name. Shared by the sync and
# async backends so a new operation is wired in one place, not two.
#
# ``query_items`` / ``read_all_items`` / ``list_databases`` are deliberately NOT
# here: they are multi-page feeds, not single-reply operations, so they are
# registered in the applicable page tables below and dispatched through
# ``execute_pages``, never through ``execute``.
OP_TO_BINDING_METHOD = {
    OP_CREATE_DATABASE: "create_database",
    OP_READ_DATABASE: "read_database",
    OP_DELETE_DATABASE: "delete_database",
    OP_CREATE_CONTAINER: "create_container",
    OP_READ_CONTAINER: "read_container",
    OP_DELETE_CONTAINER: "delete_container",
    OP_REPLACE_CONTAINER: "replace_container",
    OP_CREATE_ITEM: "create_item",
    OP_UPSERT_ITEM: "upsert_item",
    OP_REPLACE_ITEM: "replace_item",
    OP_DELETE_ITEM: "delete_item",
    OP_READ_ITEM: "read_item",
    OP_PATCH_ITEM: "patch_item",
    OP_READ_FEED_RANGES: "read_feed_ranges",
    OP_FEED_RANGE_FROM_PARTITION_KEY: "feed_range_from_partition_key",
    # A client-side subset check, still routed through the driver entry point.
    OP_IS_FEED_RANGE_SUBSET: "is_feed_range_subset",
    # The two throughput operations: the public ``get_throughput`` /
    # ``replace_throughput`` calls reach the driver as offer reads and writes.
    OP_READ_OFFER: "read_offer",
    OP_REPLACE_OFFER: "replace_offer",
}


# Stateless page operations use this table; retained item-feed cursors use the
# next table. Neither page table controls migration fallback policy.
STATELESS_QUERY_TO_BINDING_METHOD = {
    OP_QUERY_ITEMS: "query_items",
    OP_READ_ALL_ITEMS: "read_all_items",
    OP_LIST_DATABASES: "list_databases",
    OP_QUERY_DATABASES: "query_databases",
    OP_LIST_CONTAINERS: "list_containers",
    OP_QUERY_CONTAINERS: "query_containers",
}

CURSOR_QUERY_TO_BINDING_METHOD = {
    OP_READ_ALL_ITEMS: "fetch_page_with_cursor",
    OP_QUERY_ITEMS: "fetch_page_with_cursor",
    OP_QUERY_CHANGE_FEED: "fetch_page_with_cursor",
}


def get_page_binding_method(op: str, *, uses_cursor: bool) -> str | None:
    """Select the binding name for one stateless or retained-cursor request."""
    methods = (
        CURSOR_QUERY_TO_BINDING_METHOD
        if uses_cursor
        else STATELESS_QUERY_TO_BINDING_METHOD
    )
    return methods.get(op)
