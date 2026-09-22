# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Map Python wrapper operation names to Python/Rust binding functions.

For example, OP_READ_ITEM identifies the binding's read_item function.
The async Python wrapper uses the same table and adds the _async suffix.

Page fetches use separate tables. The binding can keep an in-memory object
containing a query's plan and progress between requests. Calls passing that
object use CURSOR_QUERY_TO_BINDING_METHOD. Calls without it use
STATELESS_QUERY_TO_BINDING_METHOD and may pass a continuation token instead.

These tables choose functions, not whether Python fallback is allowed. That
decision belongs to capabilities.py.
"""

from __future__ import annotations

# Operation names stored in PreparedRequest.op and PreparedQuery.op.
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
OP_QUERY_ITEMS_CHANGE_FEED = "query_items_change_feed"
OP_LIST_DATABASES = "list_databases"
OP_READ_FEED_RANGES = "read_feed_ranges"
OP_FEED_RANGE_FROM_PARTITION_KEY = "feed_range_from_partition_key"
OP_IS_FEED_RANGE_SUBSET = "is_feed_range_subset"
OP_READ_OFFER = "read_offer"
OP_REPLACE_OFFER = "replace_offer"


# ``PreparedRequest.op`` -> binding function name. Shared by the sync and
# async Python wrappers so a new operation is connected in one place, not two.
#
# ``query_items`` / ``read_all_items`` / ``list_databases`` are deliberately NOT
# here: they are multi-page feeds, not single-reply operations, so they are
# registered in the applicable page tables below and called through
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
    # A local key-range check reached through the Python/Rust binding.
    OP_IS_FEED_RANGE_SUBSET: "is_feed_range_subset",
    # The two throughput operations: the public ``get_throughput`` /
    # ``replace_throughput`` calls reach the driver as offer reads and writes.
    OP_READ_OFFER: "read_offer",
    OP_REPLACE_OFFER: "replace_offer",
}


# Requests without the binding's query-progress object use this table, even
# when they carry a continuation token. Requests with that object use the next table.
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
    OP_QUERY_ITEMS_CHANGE_FEED: "fetch_page_with_cursor",
}


def get_page_binding_method(op: str, *, uses_cursor: bool) -> str | None:
    """Find the page-fetch function for requests with or without saved query progress."""
    methods = (
        CURSOR_QUERY_TO_BINDING_METHOD
        if uses_cursor
        else STATELESS_QUERY_TO_BINDING_METHOD
    )
    return methods.get(op)
