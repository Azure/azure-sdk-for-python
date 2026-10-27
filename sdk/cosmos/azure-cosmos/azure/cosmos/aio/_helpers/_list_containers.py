# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Prepare container feeds for the shared asynchronous metadata pager."""
from typing import Any

from azure.core.async_paging import AsyncItemPaged

from ..._helpers._list_containers import ListContainersConfig, QueryContainersConfig
from ._metadata_feed import AsyncMetadataFeedPageIterator


def list_containers(proxy: Any, kwargs: dict[str, Any]) -> AsyncItemPaged[dict[str, Any]]:
    config = ListContainersConfig(proxy, kwargs)
    pager: AsyncItemPaged[dict[str, Any]] = AsyncItemPaged(config, page_iterator_class=AsyncMetadataFeedPageIterator)
    config.bind_pager(pager)
    return pager


def query_containers(proxy: Any, query: Any, parameters: Any, kwargs: dict[str, Any]) -> AsyncItemPaged[Any]:
    config = QueryContainersConfig(proxy, query, parameters, kwargs)
    pager: AsyncItemPaged[Any] = AsyncItemPaged(config, page_iterator_class=AsyncMetadataFeedPageIterator)
    config.bind_pager(pager)
    return pager
