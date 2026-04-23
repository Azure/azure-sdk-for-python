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
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class _TestContext:
    def __init__(
        self,
        index_client: SearchIndexClient,
        index_name: str,
        source_name: str,
        created_source: SearchIndexKnowledgeSource,
        base_name: str,
        created_base: KnowledgeBase,
    ) -> None:
        self.index_client = index_client
        self.index_name = index_name
        self.source_name = source_name
        self.created_source = created_source
        self.base_name = base_name
        self.created_base = created_base


class TestKnowledgeBaseConfigurationLive(AzureRecordedTestCase):
    def _create_context(self, endpoint: str) -> "_TestContext":
        credential = get_credential()
        index_client = SearchIndexClient(endpoint, credential, retry_backoff_factor=60)

        index_name = self.get_resource_name("cfgidx")
        source_name = self.get_resource_name("cfgks")
        base_name = self.get_resource_name("cfgkb")

        # best-effort cleanup in case a previous run failed before teardown
        try:
            index_client.delete_knowledge_base(base_name)
        except HttpResponseError:
            pass
        try:
            index_client.delete_knowledge_source(source_name)
        except HttpResponseError:
            pass
        try:
            index_client.delete_index(index_name)
        except HttpResponseError:
            pass

        # Create a search index with semantic configuration (required for SearchIndexKnowledgeSource)
        index = SearchIndex(
            name=index_name,
            fields=[
                SearchField(name="id", type=SearchFieldDataType.String, key=True),
                SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
            ],
            semantic_search=SemanticSearch(
                default_configuration_name="default",
                configurations=[
                    SemanticConfiguration(
                        name="default",
                        prioritized_fields=SemanticPrioritizedFields(
                            content_fields=[SemanticField(field_name="content")]
                        ),
                    )
                ],
            ),
        )
        index_client.create_index(index)

        # Create knowledge source pointing to the index
        create_source = SearchIndexKnowledgeSource(
            name=source_name,
            description="configuration source",
            search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
        )
        created_source = index_client.create_knowledge_source(create_source)

        create_base = KnowledgeBase(
            name=base_name,
            description="configurable knowledge base",
            knowledge_sources=[KnowledgeSourceReference(name=source_name)],
        )

        try:
            created_base = index_client.create_knowledge_base(create_base)
        except HttpResponseError:
            # creation failed; remove the knowledge source and index before raising
            try:
                index_client.delete_knowledge_source(created_source)
            except HttpResponseError:
                pass
            try:
                index_client.delete_index(index_name)
            except HttpResponseError:
                pass
            raise

        return _TestContext(index_client, index_name, source_name, created_source, base_name, created_base)

    def _cleanup(self, ctx: "_TestContext") -> None:
        try:
            try:
                ctx.index_client.delete_knowledge_base(
                    ctx.created_base,
                    match_condition=MatchConditions.IfNotModified,
                )
            except HttpResponseError:
                pass
            try:
                ctx.index_client.delete_knowledge_source(
                    ctx.created_source,
                    match_condition=MatchConditions.IfNotModified,
                )
            except HttpResponseError:
                pass
            try:
                ctx.index_client.delete_index(ctx.index_name)
            except HttpResponseError:
                pass
        finally:
            ctx.index_client.close()

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy
    def test_knowledge_base_configuration_round_trip(self, endpoint: str) -> None:
        ctx = self._create_context(endpoint)
        try:
            created = ctx.created_base
            assert created.name == ctx.base_name
            assert created.description == "configurable knowledge base"
            assert len(created.knowledge_sources) == 1
            assert created.knowledge_sources[0].name == ctx.source_name
            assert created.e_tag is not None

            update_model = KnowledgeBase(
                name=ctx.base_name,
                description="config updated",
                knowledge_sources=[KnowledgeSourceReference(name=ctx.source_name)],
            )
            update_model.e_tag = created.e_tag

            updated = ctx.index_client.create_or_update_knowledge_base(
                update_model,
                match_condition=MatchConditions.IfNotModified,
            )
            assert updated.description == "config updated"
            assert updated.e_tag != created.e_tag

            fetched = ctx.index_client.get_knowledge_base(ctx.base_name)
            assert fetched.description == "config updated"
            assert len(fetched.knowledge_sources) == 1
        finally:
            self._cleanup(ctx)
