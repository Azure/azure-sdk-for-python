# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Prepare database feeds for the shared asynchronous metadata pager."""
from typing import Any

from azure.core.async_paging import AsyncItemPaged

from ..._helpers._list_databases import ListDatabasesConfig, QueryDatabasesConfig
from ._metadata_feed import AsyncMetadataFeedPageIterator


def list_databases(client: Any, kwargs: dict[str, Any]) -> AsyncItemPaged[dict[str, Any]]:
    return AsyncItemPaged(ListDatabasesConfig(client, kwargs), page_iterator_class=AsyncMetadataFeedPageIterator)


def query_databases(client: Any, query: Any, parameters: Any, kwargs: dict[str, Any]) -> AsyncItemPaged[Any]:
    return AsyncItemPaged(
        QueryDatabasesConfig(client, query, parameters, kwargs), page_iterator_class=AsyncMetadataFeedPageIterator,
    )
