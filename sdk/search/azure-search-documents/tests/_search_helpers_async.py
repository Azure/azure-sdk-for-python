# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared helpers for async live tests. Mirror of ``_search_helpers.py``."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Awaitable, Callable, Optional

from azure.core.exceptions import HttpResponseError
from azure.search.documents import IndexDocumentsBatch
from azure.search.documents.aio import SearchClient, SearchIndexingBufferedSender
from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    SearchIndexKnowledgeSource,
)
from devtools_testutils import get_credential
from devtools_testutils.aio import recorded_by_proxy_async

from search_service_preparer import SearchEnvVarPreparer, search_decorator

from _search_helpers import (
    HOTEL_DOCUMENT_COUNT,
    INDEXING_DELAY_SECONDS,
    KNOWLEDGE_BASE_DESCRIPTION,
    KNOWLEDGE_SOURCE_DESCRIPTION,
    SEARCH_RESOURCE_PREFIX,
    SearchLiveContext,
    build_hotel_documents,
    build_hotel_index,
    build_index,
    build_knowledge_base,
    build_knowledge_source,
)


# ---------------------------------------------------------------------------
# Shared operations
# ---------------------------------------------------------------------------


async def safe_delete(callable_: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> None:
    """Invoke an async delete callable, swallowing ``HttpResponseError``."""
    try:
        await callable_(*args, **kwargs)
    except HttpResponseError:
        pass


async def poll_until(
    fn: Callable[[], Awaitable[Any]],
    *,
    predicate: Callable[[Any], bool],
    interval: float = 5.0,
    attempts: int = 36,
) -> list:
    snapshots: list = []
    for attempt in range(attempts):
        snapshot = await fn()
        snapshots.append(snapshot)
        if predicate(snapshot):
            return snapshots
        if attempt < attempts - 1:
            await asyncio.sleep(interval)
    last_snapshot = snapshots[-1] if snapshots else None
    raise AssertionError(
        f"Polling timed out after {attempts} attempts; last snapshot: {last_snapshot!r}"
    )


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------


def make_index_client(endpoint: str, *, credential: Any = None) -> SearchIndexClient:
    cred = credential if credential is not None else get_credential(is_async=True)
    return SearchIndexClient(endpoint, cred, retry_backoff_factor=60)


def make_search_client(endpoint: str, index_name: str, *, credential: Any = None) -> SearchClient:
    cred = credential if credential is not None else get_credential(is_async=True)
    return SearchClient(endpoint, index_name, cred, retry_backoff_factor=60)


def make_indexer_client(endpoint: str, *, credential: Any = None) -> SearchIndexerClient:
    cred = credential if credential is not None else get_credential(is_async=True)
    return SearchIndexerClient(endpoint, cred, retry_backoff_factor=60)


async def wait_for_live_indexing(test: Any, *, delay_seconds: int = INDEXING_DELAY_SECONDS) -> None:
    if test.is_live:
        await asyncio.sleep(delay_seconds)


async def wait_for_document_count(test: Any, search_client: Any, expected_count: int) -> None:
    snapshots = await poll_until(
        search_client.get_document_count,
        predicate=lambda document_count: document_count == expected_count,
        interval=INDEXING_DELAY_SECONDS if test.is_live else 0,
        attempts=20,
    )
    assert snapshots[-1] == expected_count


async def upload_documents(search_client: Any, documents: list[dict[str, Any]]) -> None:
    batch = IndexDocumentsBatch()
    batch.add_upload_actions(documents)
    results = await search_client.index_documents(batch)
    assert all(result.succeeded for result in results)


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def live_test() -> Callable:
    """Compose the standard async live-test decorator stack."""

    def wrap(fn: Callable) -> Callable:
        return SearchEnvVarPreparer()(
            search_decorator()(recorded_by_proxy_async(fn))
        )

    return wrap


# ---------------------------------------------------------------------------
# Context managers (one per resource family)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def index_resources(
    test: Any, endpoint: str, *, semantic: bool = False, prefix: str = SEARCH_RESOURCE_PREFIX
) -> AsyncIterator[SearchLiveContext]:
    credential = get_credential(is_async=True)
    index_client = make_index_client(endpoint, credential=credential)
    index_name = test.get_resource_name(f"{prefix}-index")
    await index_client.create_index(build_index(index_name, semantic=semantic))
    ctx = SearchLiveContext(credential=credential, index_client=index_client, index_name=index_name)
    try:
        yield ctx
    finally:
        try:
            await safe_delete(index_client.delete_index, index_name)
        finally:
            await index_client.close()


@asynccontextmanager
async def hotel_index(
    test: Any,
    endpoint: str,
    index_name: str,
    *,
    documents: list[dict[str, Any]] | None = None,
    document_count: int | None = None,
) -> AsyncIterator[tuple[Any, list[dict[str, Any]]]]:
    index_client = make_index_client(endpoint)
    search_client = make_search_client(endpoint, index_name)
    index_documents = (
        documents
        if documents is not None
        else build_hotel_documents(document_count or HOTEL_DOCUMENT_COUNT)
    )
    try:
        await index_client.create_index(build_hotel_index(index_name))
        await upload_documents(search_client, index_documents)
        await wait_for_document_count(test, search_client, len(index_documents))
        yield search_client, index_documents
    finally:
        await safe_delete(index_client.delete_index, index_name)
        await search_client.close()
        await index_client.close()


@asynccontextmanager
async def hotel_index_with_buffered_sender(
    test: Any,
    endpoint: str,
    index_name: str,
    **sender_kwargs: Any,
) -> AsyncIterator[tuple[Any, SearchIndexingBufferedSender]]:
    async with hotel_index(test, endpoint, index_name) as (search_client, _):
        buffered_sender = SearchIndexingBufferedSender(
            endpoint,
            index_name,
            get_credential(is_async=True),
            retry_backoff_factor=60,
            **sender_kwargs,
        )
        try:
            yield search_client, buffered_sender
        finally:
            await buffered_sender.close()


@asynccontextmanager
async def knowledge_source_resources(
    test: Any,
    endpoint: str,
    *,
    prefix: str = SEARCH_RESOURCE_PREFIX,
    source_description: str = KNOWLEDGE_SOURCE_DESCRIPTION,
) -> AsyncIterator[SearchLiveContext]:
    credential = get_credential(is_async=True)
    index_client = make_index_client(endpoint, credential=credential)
    index_name = test.get_resource_name(f"{prefix}-index")
    knowledge_source_name = test.get_resource_name(f"{prefix}-source")
    index_create_attempted = False
    source_create_attempted = False
    try:
        index_create_attempted = True
        await index_client.create_index(build_index(index_name, semantic=True))
        source_create_attempted = True
        created_source = await index_client.create_knowledge_source(
            build_knowledge_source(index_name, knowledge_source_name, description=source_description)
        )
        ctx = SearchLiveContext(
            credential=credential,
            index_client=index_client,
            index_name=index_name,
            knowledge_source_name=knowledge_source_name,
            knowledge_source=created_source,
        )
        yield ctx
    finally:
        try:
            if source_create_attempted:
                await safe_delete(index_client.delete_knowledge_source, knowledge_source_name)
            if index_create_attempted:
                await safe_delete(index_client.delete_index, index_name)
        finally:
            await index_client.close()


@asynccontextmanager
async def knowledge_base_resources(
    test: Any,
    endpoint: str,
    *,
    prefix: str = SEARCH_RESOURCE_PREFIX,
    wait_for_active: bool = False,
    description: str = KNOWLEDGE_BASE_DESCRIPTION,
    source_description: str = KNOWLEDGE_SOURCE_DESCRIPTION,
) -> AsyncIterator[SearchLiveContext]:
    credential = get_credential(is_async=True)
    index_client = make_index_client(endpoint, credential=credential)
    index_name = test.get_resource_name(f"{prefix}-index")
    knowledge_source_name = test.get_resource_name(f"{prefix}-source")
    knowledge_base_name = test.get_resource_name(f"{prefix}-base")
    index_create_attempted = False
    source_create_attempted = False
    base_create_attempted = False
    try:
        index_create_attempted = True
        await index_client.create_index(build_index(index_name, semantic=True))
        source_create_attempted = True
        created_source = await index_client.create_knowledge_source(
            build_knowledge_source(index_name, knowledge_source_name, description=source_description)
        )
        base_create_attempted = True
        created_base = await index_client.create_knowledge_base(
            build_knowledge_base(knowledge_base_name, knowledge_source_name, description=description)
        )

        if wait_for_active:
            await poll_until(
                lambda: index_client.get_knowledge_source_status(knowledge_source_name),
                predicate=lambda s: s.synchronization_status == "active",
            )

        ctx = SearchLiveContext(
            credential=credential,
            index_client=index_client,
            index_name=index_name,
            knowledge_source_name=knowledge_source_name,
            knowledge_source=created_source,
            knowledge_base_name=knowledge_base_name,
            knowledge_base=created_base,
        )
        yield ctx
    finally:
        try:
            if base_create_attempted:
                await safe_delete(index_client.delete_knowledge_base, knowledge_base_name)
            if source_create_attempted:
                await safe_delete(index_client.delete_knowledge_source, knowledge_source_name)
            if index_create_attempted:
                await safe_delete(index_client.delete_index, index_name)
        finally:
            await index_client.close()
