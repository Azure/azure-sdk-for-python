# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from __future__ import annotations

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, get_credential
from devtools_testutils.aio import recorded_by_proxy_async

from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    RemoteSharePointKnowledgeSource,
    RemoteSharePointKnowledgeSourceParameters,
)

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class _AsyncTestContext:
    def __init__(
        self,
        index_client: SearchIndexClient,
        source_name: str,
        created_revision: RemoteSharePointKnowledgeSource,
    ) -> None:
        self.index_client = index_client
        self.source_name = source_name
        self.created_revision = created_revision


class TestRemoteSharePointKnowledgeSourceLiveAsync(AzureRecordedTestCase):
    async def _create_context(self, endpoint: str) -> "_AsyncTestContext":
        credential = get_credential(is_async=True)
        index_client = SearchIndexClient(endpoint, credential, retry_backoff_factor=60)

        source_name = self.get_resource_name("spsource")
        create_model = RemoteSharePointKnowledgeSource(
            name=source_name,
            description="initial sharepoint source",
            remote_share_point_parameters=RemoteSharePointKnowledgeSourceParameters(
                filter_expression="Title:Test",
                resource_metadata=["Title", "Path"],
            ),
        )
        created = await index_client.create_knowledge_source(create_model)
        return _AsyncTestContext(index_client, source_name, created)

    async def _cleanup(self, ctx: "_AsyncTestContext") -> None:
        try:
            try:
                await ctx.index_client.delete_knowledge_source(
                    ctx.created_revision,
                    match_condition=MatchConditions.IfNotModified,
                )
            except HttpResponseError:
                pass
        finally:
            await ctx.index_client.close()

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_remote_sharepoint_knowledge_source_create(
        self, endpoint: str
    ) -> None:
        ctx = await self._create_context(endpoint)
        try:
            assert ctx.created_revision.name == ctx.source_name
            assert ctx.created_revision.kind == "remoteSharePoint"
            params = ctx.created_revision.remote_share_point_parameters
            assert params is not None
            assert params.filter_expression == "Title:Test"
            assert params.resource_metadata is not None
            assert {"Title", "Path"}.issubset(set(params.resource_metadata))
        finally:
            await self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_remote_sharepoint_knowledge_source_update(
        self, endpoint: str
    ) -> None:
        ctx = await self._create_context(endpoint)
        try:
            update_model = RemoteSharePointKnowledgeSource(
                name=ctx.source_name,
                description="updated description",
                remote_share_point_parameters=ctx.created_revision.remote_share_point_parameters,
            )
            update_model.e_tag = ctx.created_revision.e_tag

            revised = await ctx.index_client.create_or_update_knowledge_source(
                update_model,
                match_condition=MatchConditions.IfNotModified,
            )
            ctx.created_revision = revised
            assert revised.description == "updated description"
        finally:
            await self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_remote_sharepoint_knowledge_source_read(self, endpoint: str) -> None:
        ctx = await self._create_context(endpoint)
        try:
            fetched = await ctx.index_client.get_knowledge_source(ctx.source_name)
            status = await ctx.index_client.get_knowledge_source_status(ctx.source_name)
            listed = [item async for item in ctx.index_client.list_knowledge_sources()]

            assert fetched.name == ctx.source_name
            assert status.synchronization_status in {"creating", "active", "deleting"}
            assert any(item.name == ctx.source_name for item in listed)
        finally:
            await self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy_async
    async def test_remote_sharepoint_knowledge_source_delete(
        self, endpoint: str
    ) -> None:
        ctx = await self._create_context(endpoint)
        try:
            await ctx.index_client.delete_knowledge_source(
                ctx.created_revision,
                match_condition=MatchConditions.IfNotModified,
            )
            remaining = [
                item async for item in ctx.index_client.list_knowledge_sources()
            ]
            assert all(item.name != ctx.source_name for item in remaining)
        finally:
            await ctx.index_client.close()
