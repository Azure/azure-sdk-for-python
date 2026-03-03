# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from __future__ import annotations

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, get_credential

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    WebKnowledgeSource,
    WebKnowledgeSourceDomain,
    WebKnowledgeSourceDomains,
    WebKnowledgeSourceParameters,
)

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class _TestContext:
    def __init__(
        self,
        index_client: SearchIndexClient,
        source_name: str,
        created_revision: WebKnowledgeSource,
    ):
        self.index_client = index_client
        self.source_name = source_name
        self.created_revision = created_revision


class TestWebKnowledgeSourceLive(AzureRecordedTestCase):
    def _create_context(self, endpoint: str) -> "_TestContext":
        credential = get_credential()
        index_client = SearchIndexClient(endpoint, credential, retry_backoff_factor=60)

        source_name = self.get_resource_name("websource")
        create_model = WebKnowledgeSource(
            name=source_name,
            description="initial web source",
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
        created = index_client.create_knowledge_source(create_model)
        return _TestContext(index_client, source_name, created)

    def _cleanup(self, ctx: "_TestContext") -> None:
        try:
            try:
                ctx.index_client.delete_knowledge_source(
                    ctx.created_revision,
                    match_condition=MatchConditions.IfNotModified,
                )
            except HttpResponseError:
                pass
        finally:
            ctx.index_client.close()

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy
    def test_web_knowledge_source_create(self, endpoint: str) -> None:
        ctx = self._create_context(endpoint)
        try:
            assert ctx.created_revision.name == ctx.source_name
            assert ctx.created_revision.kind == "web"
            assert ctx.created_revision.web_parameters is not None
            domains = ctx.created_revision.web_parameters.domains
            assert domains is not None and domains.allowed_domains is not None
            assert domains.allowed_domains[0].address == "https://learn.microsoft.com"
        finally:
            self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy
    def test_web_knowledge_source_update(self, endpoint: str) -> None:
        ctx = self._create_context(endpoint)
        try:
            update_model = WebKnowledgeSource(
                name=ctx.source_name,
                description="updated description",
                web_parameters=ctx.created_revision.web_parameters,
            )
            update_model.e_tag = ctx.created_revision.e_tag

            revised = ctx.index_client.create_or_update_knowledge_source(
                update_model,
                match_condition=MatchConditions.IfNotModified,
            )
            ctx.created_revision = revised
            assert revised.description == "updated description"
        finally:
            self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy
    def test_web_knowledge_source_read(self, endpoint: str) -> None:
        ctx = self._create_context(endpoint)
        try:
            fetched = ctx.index_client.get_knowledge_source(ctx.source_name)
            status = ctx.index_client.get_knowledge_source_status(ctx.source_name)
            listed = list(ctx.index_client.list_knowledge_sources())

            assert fetched.name == ctx.source_name
            assert status.synchronization_status in {"creating", "active", "deleting"}
            assert any(item.name == ctx.source_name for item in listed)
        finally:
            self._cleanup(ctx)

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy
    def test_web_knowledge_source_delete(self, endpoint: str) -> None:
        ctx = self._create_context(endpoint)
        try:
            ctx.index_client.delete_knowledge_source(
                ctx.created_revision,
                match_condition=MatchConditions.IfNotModified,
            )
            remaining = list(ctx.index_client.list_knowledge_sources())
            assert all(item.name != ctx.source_name for item in remaining)
        finally:
            ctx.index_client.close()
