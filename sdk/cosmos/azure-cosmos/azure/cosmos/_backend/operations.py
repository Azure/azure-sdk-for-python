# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Operation discriminators and native binding dispatch tables.

Single replies use OP_TO_BINDING_METHOD. Pages use either the stateless or
cursor table according to their call signature. Names and data are independent
of migration fallback policy; adding a migrated operation does not require a
new executor method."""

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
# registered in ``STATELESS_QUERY_TO_BINDING_METHOD`` below and dispatched through
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


# ``PreparedQuery.op`` -> binding function name, matching ``OP_TO_BINDING_METHOD``
# for the paged operations: the two container-scoped feeds (``query_items``,
# ``read_all_items``) and the account-scoped one (``list_databases``). A
# backend's ``execute_pages`` reads this (never ``OP_TO_BINDING_METHOD``) so a
# paged op can never be reached through the single-reply ``execute`` path by
# accident.
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
