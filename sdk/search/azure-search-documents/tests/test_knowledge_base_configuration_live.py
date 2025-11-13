# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from __future__ import annotations

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, get_credential

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeRetrievalMediumReasoningEffort,
    KnowledgeRetrievalMinimalReasoningEffort,
    KnowledgeSourceReference,
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
        created_source: WebKnowledgeSource,
        base_name: str,
        created_base: KnowledgeBase,
    ) -> None:
        self.index_client = index_client
        self.source_name = source_name
        self.created_source = created_source
        self.base_name = base_name
        self.created_base = created_base


class TestKnowledgeBaseConfigurationLive(AzureRecordedTestCase):
    def _create_context(self, endpoint: str) -> "_TestContext":
        credential = get_credential()
        index_client = SearchIndexClient(endpoint, credential, retry_backoff_factor=60)

        source_name = self.get_resource_name("cfgks")
        create_source = WebKnowledgeSource(
            name=source_name,
            description="configuration source",
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

        created_source = index_client.create_knowledge_source(create_source)

        create_base = KnowledgeBase(
            name=base_name,
            description="configurable knowledge base",
            knowledge_sources=[KnowledgeSourceReference(name=source_name)],
            retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
            output_mode="extractiveData",
        )

        try:
            created_base = index_client.create_knowledge_base(create_base)
        except HttpResponseError:
            # creation failed; remove the knowledge source created above before raising
            try:
                index_client.delete_knowledge_source(created_source)
            except HttpResponseError:
                pass
            raise

        return _TestContext(
            index_client, source_name, created_source, base_name, created_base
        )

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
        finally:
            ctx.index_client.close()

    @SearchEnvVarPreparer()
    @search_decorator(schema=None, index_batch=None)
    @recorded_by_proxy
    def test_knowledge_base_configuration_round_trip(self, endpoint: str) -> None:
        ctx = self._create_context(endpoint)
        try:
            created = ctx.created_base
            assert isinstance(
                created.retrieval_reasoning_effort,
                KnowledgeRetrievalMinimalReasoningEffort,
            )
            assert created.output_mode == "extractiveData"
            assert created.retrieval_instructions is None
            assert created.answer_instructions is None

            update_model = KnowledgeBase(
                name=ctx.base_name,
                description="config updated",
                knowledge_sources=[KnowledgeSourceReference(name=ctx.source_name)],
                retrieval_reasoning_effort=KnowledgeRetrievalMediumReasoningEffort(),
                output_mode="answerSynthesis",
                retrieval_instructions="summarize with details",
                answer_instructions="include citations and summaries",
            )
            update_model.e_tag = created.e_tag

            with pytest.raises(HttpResponseError) as ex:
                ctx.index_client.create_or_update_knowledge_base(
                    update_model,
                    match_condition=MatchConditions.IfNotModified,
                )

            assert "Retrieval instructions cannot be specified" in str(ex.value)

            fetched = ctx.index_client.get_knowledge_base(ctx.base_name)
            assert isinstance(
                fetched.retrieval_reasoning_effort,
                KnowledgeRetrievalMinimalReasoningEffort,
            )
            assert fetched.output_mode == "extractiveData"
            assert fetched.retrieval_instructions is None
            assert fetched.answer_instructions is None
        finally:
            self._cleanup(ctx)
