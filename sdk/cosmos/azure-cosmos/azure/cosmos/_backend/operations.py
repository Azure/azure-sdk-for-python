# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Map Python wrapper operation names to Python/Rust binding functions.

For example, OP_READ_ITEM identifies the binding's read_item function.
The async Python wrapper uses the same table and adds the _async suffix.

Page fetches use separate tables. Requests passing a feed cursor use
RETAINED_PAGE_BINDING_FUNCTION_NAMES. Requests without a feed cursor use
STATELESS_PAGE_BINDING_FUNCTION_NAMES and may still carry a continuation token.

These tables choose binding function names, not whether fallback to the legacy
path is allowed. That decision belongs to capabilities.py.
"""

from __future__ import annotations

# Operation names stored in PreparedRequest.op and PreparedPageRequest.op.
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
# here: they are feeds, so they are registered in the page tables and called through
# ``execute_pages``, never through ``execute``.
OP_TO_BINDING_FUNCTION_NAME = {
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


# Stateless page requests use this table even when they carry a continuation
# token. Requests with a feed cursor use the retained-paging table below.
STATELESS_PAGE_BINDING_FUNCTION_NAMES = {
    OP_QUERY_ITEMS: "query_items",
    OP_READ_ALL_ITEMS: "read_all_items",
    OP_LIST_DATABASES: "list_databases",
    OP_QUERY_DATABASES: "query_databases",
    OP_LIST_CONTAINERS: "list_containers",
    OP_QUERY_CONTAINERS: "query_containers",
}

RETAINED_PAGE_BINDING_FUNCTION_NAMES = {
    OP_READ_ALL_ITEMS: "fetch_page_with_cursor",
    OP_QUERY_ITEMS: "fetch_page_with_cursor",
    OP_QUERY_ITEMS_CHANGE_FEED: "fetch_page_with_cursor",
}


def get_page_binding_function_name(op: str, *, uses_cursor: bool) -> str | None:
    """Return a binding function name for the operation and cursor mode.

    For example, query_items uses query_items without a feed cursor and
    fetch_page_with_cursor with one. None means this combination is unsupported,
    not necessarily that the operation has no paging implementation.
    """
    binding_function_names = (
        RETAINED_PAGE_BINDING_FUNCTION_NAMES
        if uses_cursor
        else STATELESS_PAGE_BINDING_FUNCTION_NAMES
    )
    return binding_function_names.get(op)
