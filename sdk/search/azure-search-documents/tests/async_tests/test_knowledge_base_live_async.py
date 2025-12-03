# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from __future__ import annotations

import asyncio

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, get_credential
from devtools_testutils.aio import recorded_by_proxy_async

from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchServiceStatistics,
    ServiceIndexersRuntime,
    WebKnowledgeSource,
    WebKnowledgeSourceDomain,
    WebKnowledgeSourceDomains,
    WebKnowledgeSourceParameters,
)

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class _AsyncTestContext:
    def __init__(
        self,
        index_client: SearchIndexClient,
        source_name: str,
        created_source: WebKnowledgeSource,
        base_name: str,
        created_base: KnowledgeBase,
    ) -> None:
        self.index_client = index_client
        self.source_name = source_name
        self.created_source = created_source
        self.base_name = base_name
        self.created_base = created_base


class TestKnowledgeBaseLiveAsync(AzureRecordedTestCase):
    async def _create_context(self, endpoint: str) -> "_AsyncTestContext":
        credential = get_credential(is_async=True)
        index_client = SearchIndexClient(endpoint, credential, retry_backoff_factor=60)

        source_name = self.get_resource_name("ksrc")
        base_name = self.get_resource_name("kb")
        create_source = WebKnowledgeSource(
            name=source_name,
            description="knowledge base dependent source",
            web_parameters=WebKnowledgeSourceParameters(
                domains=WebKnowledgeSourceDomains(
                    allowed_domains=[
                        WebKnowledgeSourceDomain(
                            address="https://learn.microsoft.com",
                            include_subpages=True,
                        )
                    ]
                )
            ),
        )
        created_source = await index_client.create_knowledge_source(create_source)

        create_base = KnowledgeBase(
            name=base_name,
            description="initial knowledge base",
            knowledge_sources=[KnowledgeSourceReference(name=source_name)],
        )
        created_base = await index_client.create_knowledge_base(create_base)
        return _AsyncTestContext(index_client, source_name, created_source, base_name, created_base)

    async def _cleanup(self, ctx: "_AsyncTestContext") -> None:
        try:
            try:
                await ctx.index_client.delete_knowledge_base(
                    ctx.created_base,
                    match_condition=MatchConditions.IfNotModified,
                )
            except HttpResponseError:
                pass
            try:
                await ctx.index_client.delete_knowledge_source(
                    ctx.created_source,
                    match_condition=MatchConditions.IfNotModified,
                )
            except HttpResponseError:
                pass
        finally:
            await ctx.index_client.close()

    async def _poll_status_snapshots(
        self,
        ctx: "_AsyncTestContext",
        *,
        wait_for: str = "active",
        interval: float = 5.0,
        attempts: int = 36,
    ):
        snapshots = []
        for _ in range(attempts):
            status = await ctx.index_client.get_knowledge_source_status(ctx.source_name)
            snapshots.append(status)
            if status.synchronization_status == wait_for:
                return snapshots
            await asyncio.sleep(interval)
        return snapshots

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_knowledge_base_create(self, endpoint: str) -> None:
        ctx = await self._create_context(endpoint)
        try:
            assert ctx.created_base.name == ctx.base_name
            assert ctx.created_base.knowledge_sources
            assert ctx.created_base.knowledge_sources[0].name == ctx.source_name
        finally:
            await self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_knowledge_base_update(self, endpoint: str) -> None:
        ctx = await self._create_context(endpoint)
        try:
            update_model = KnowledgeBase(
                name=ctx.base_name,
                description="updated knowledge base description",
                knowledge_sources=[KnowledgeSourceReference(name=ctx.source_name)],
            )
            update_model.e_tag = ctx.created_base.e_tag

            revised = await ctx.index_client.create_or_update_knowledge_base(
                update_model,
                match_condition=MatchConditions.IfNotModified,
            )
            ctx.created_base = revised
            assert revised.description == "updated knowledge base description"
        finally:
            await self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_knowledge_base_read(self, endpoint: str) -> None:
        ctx = await self._create_context(endpoint)
        try:
            fetched = await ctx.index_client.get_knowledge_base(ctx.base_name)
            listed = [item async for item in ctx.index_client.list_knowledge_bases()]

            assert fetched.name == ctx.base_name
            assert fetched.knowledge_sources and fetched.knowledge_sources[0].name == ctx.source_name
            assert any(item.name == ctx.base_name for item in listed)
        finally:
            await self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_knowledge_base_delete(self, endpoint: str) -> None:
        ctx = await self._create_context(endpoint)
        try:
            await ctx.index_client.delete_knowledge_base(
                ctx.created_base,
                match_condition=MatchConditions.IfNotModified,
            )
            remaining = [item async for item in ctx.index_client.list_knowledge_bases()]
            assert all(item.name != ctx.base_name for item in remaining)
        finally:
            await self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_knowledge_source_status_tracking(self, endpoint: str) -> None:
        ctx = await self._create_context(endpoint)
        try:
            snapshots = await self._poll_status_snapshots(ctx)
            assert snapshots, "Expected at least one status snapshot"

            first = snapshots[0]
            last = snapshots[-1]
            assert first.synchronization_status in {"creating", "active"}
            assert last.synchronization_status == "active"

            if last.statistics is not None:
                assert last.statistics.total_synchronization >= 0
                assert last.statistics.average_items_processed_per_synchronization >= 0
            if last.current_synchronization_state is not None:
                assert last.current_synchronization_state.items_updates_processed >= 0
            if last.last_synchronization_state is not None:
                assert last.last_synchronization_state.items_updates_processed >= 0
        finally:
            await self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_service_indexer_runtime_statistics(self, endpoint: str) -> None:
        ctx = await self._create_context(endpoint)
        try:
            snapshots = await self._poll_status_snapshots(ctx)
            assert snapshots, "Expected at least one status snapshot"

            service_stats = await ctx.index_client._client.get_service_statistics()  # pylint:disable=protected-access
            assert isinstance(service_stats, SearchServiceStatistics)

            runtime = service_stats.indexers_runtime
            assert isinstance(runtime, ServiceIndexersRuntime)
            assert runtime.used_seconds >= -1
            assert runtime.beginning_time <= runtime.ending_time
            if runtime.remaining_seconds is not None:
                assert runtime.remaining_seconds >= -1

            counters = service_stats.counters
            assert counters.indexer_counter is not None
            assert counters.indexer_counter.usage >= 0
            assert counters.indexer_counter.quota >= counters.indexer_counter.usage

            limits = service_stats.limits
            if limits.max_cumulative_indexer_runtime_seconds is not None:
                assert limits.max_cumulative_indexer_runtime_seconds > 0
        finally:
            await self._cleanup(ctx)
