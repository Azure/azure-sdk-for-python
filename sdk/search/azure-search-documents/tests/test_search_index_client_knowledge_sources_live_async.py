# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``SearchIndexClient`` knowledge source operations."""

from __future__ import annotations

from typing import Any

from azure.core import MatchConditions
from devtools_testutils import AzureRecordedTestCase

from _capabilities import require_capability
from _search_helpers_async import index_resources, live_test, make_index_client, safe_delete

WEB_DOMAIN_ADDRESS = "https://learn.microsoft.com"
WEB_KNOWLEDGE_SOURCE_DESCRIPTION = "Web knowledge source for SearchIndexClient live coverage"
REPLACEMENT_WEB_KNOWLEDGE_SOURCE_DESCRIPTION = "Web knowledge source replacement for SearchIndexClient live coverage"
_WEB_KNOWLEDGE_SOURCE_MODEL_CAPABILITIES = (
    "azure.search.documents.indexes.models.KnowledgeSourceKind.WEB",
    "azure.search.documents.indexes.models.WebKnowledgeSource",
    "azure.search.documents.indexes.models.WebKnowledgeSourceDomain",
    "azure.search.documents.indexes.models.WebKnowledgeSourceDomains",
    "azure.search.documents.indexes.models.WebKnowledgeSourceParameters",
)


def _require_web_knowledge_source_capabilities(*methods: str) -> None:
    require_capability(*_WEB_KNOWLEDGE_SOURCE_MODEL_CAPABILITIES, *methods)


def _build_web_knowledge_source(knowledge_source_name: str) -> Any:
    from azure.search.documents.indexes.models import (
        WebKnowledgeSource,
        WebKnowledgeSourceDomain,
        WebKnowledgeSourceDomains,
        WebKnowledgeSourceParameters,
    )

    return WebKnowledgeSource(
        name=knowledge_source_name,
        description=WEB_KNOWLEDGE_SOURCE_DESCRIPTION,
        web_parameters=WebKnowledgeSourceParameters(
            domains=WebKnowledgeSourceDomains(
                allowed_domains=[
                    WebKnowledgeSourceDomain(
                        address=WEB_DOMAIN_ADDRESS,
                        include_subpages=True,
                    )
                ]
            )
        ),
    )


def _assert_web_knowledge_source(result: Any, knowledge_source_name: str) -> None:
    from azure.search.documents.indexes.models import KnowledgeSourceKind

    assert result.name == knowledge_source_name
    assert result.kind == KnowledgeSourceKind.WEB
    assert result.description == WEB_KNOWLEDGE_SOURCE_DESCRIPTION
    assert result.web_parameters is not None
    assert result.web_parameters.domains is not None
    assert result.web_parameters.domains.allowed_domains is not None
    assert result.web_parameters.domains.allowed_domains[0].address == WEB_DOMAIN_ADDRESS
    assert result.web_parameters.domains.allowed_domains[0].include_subpages is True


class TestSearchIndexClientSearchIndexKnowledgeSourcesAsync(AzureRecordedTestCase):
    @live_test()
    async def test_create_or_update_knowledge_source_preserves_facet_hint(self, endpoint: str) -> None:
        require_capability(
            "azure.search.documents.indexes.aio.SearchIndexClient.create_or_update_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.get_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_source",
            "azure.search.documents.indexes.models.SearchIndexKnowledgeSourceFilterHintAutoConfiguration",
        )
        from azure.search.documents.indexes.models import SearchFieldDataType, SimpleField
        from _preview_helpers import knowledge_source_configuration

        source_name = self.get_resource_name("knowledge-source-facet-hint")
        async with index_resources(self, endpoint, semantic=True, prefix="facet-hint") as context:
            client = context.index_client
            index = await client.get_index(context.index_name)
            index.fields.append(
                SimpleField(name="category", type=SearchFieldDataType.STRING, filterable=True, facetable=True)
            )
            await client.create_or_update_index(index)
            source = knowledge_source_configuration("facet_hint")
            source.name = source_name
            source.search_index_parameters.search_index_name = context.index_name
            try:
                await client.create_or_update_knowledge_source(source)
                retrieved = await client.get_knowledge_source(source_name)
                hint = retrieved.search_index_parameters.query_hints.filters[0]
                assert hint.field == "category"
                assert hint.field_values is None
                assert hint.auto_configuration.cache_ttl == 300
                assert hint.auto_configuration.max_facet_value_count == 16

                hint.auto_configuration.cache_ttl = 600
                await client.create_or_update_knowledge_source(retrieved)
                updated = await client.get_knowledge_source(source_name)
                assert updated.search_index_parameters.query_hints.filters[0].auto_configuration.cache_ttl == 600
            finally:
                await safe_delete(client.delete_knowledge_source, source_name)


class TestSearchIndexClientWebKnowledgeSourcesAsync(AzureRecordedTestCase):
    @live_test()
    async def test_create_knowledge_source_returns_web_source(self, endpoint: str) -> None:
        _require_web_knowledge_source_capabilities(
            "azure.search.documents.indexes.aio.SearchIndexClient.create_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_source",
        )
        knowledge_source_name = self.get_resource_name("knowledge-source-create-web")

        async with make_index_client(endpoint) as client:
            try:
                result = await client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                _assert_web_knowledge_source(result, knowledge_source_name)
                assert result.e_tag is not None
            finally:
                await safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    async def test_create_or_update_knowledge_source_uses_model_name_and_etag(self, endpoint: str) -> None:
        _require_web_knowledge_source_capabilities(
            "azure.search.documents.indexes.aio.SearchIndexClient.create_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.create_or_update_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_source",
        )
        from azure.search.documents.indexes.models import KnowledgeSourceKind, WebKnowledgeSource

        knowledge_source_name = self.get_resource_name("knowledge-source-create-or-update-web")

        async with make_index_client(endpoint) as client:
            try:
                original = await client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))
                replacement = WebKnowledgeSource(
                    name=knowledge_source_name,
                    description=REPLACEMENT_WEB_KNOWLEDGE_SOURCE_DESCRIPTION,
                    web_parameters=original.web_parameters,
                )
                replacement.e_tag = original.e_tag

                result = await client.create_or_update_knowledge_source(
                    replacement,
                    match_condition=MatchConditions.IfNotModified,
                )

                assert result.name == knowledge_source_name
                assert result.kind == KnowledgeSourceKind.WEB
                assert result.description == REPLACEMENT_WEB_KNOWLEDGE_SOURCE_DESCRIPTION
                assert result.e_tag != original.e_tag
            finally:
                await safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    async def test_get_knowledge_source_returns_named_web_source(self, endpoint: str) -> None:
        _require_web_knowledge_source_capabilities(
            "azure.search.documents.indexes.aio.SearchIndexClient.create_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.get_knowledge_source",
        )
        knowledge_source_name = self.get_resource_name("knowledge-source-get-web")

        async with make_index_client(endpoint) as client:
            try:
                await client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                result = await client.get_knowledge_source(knowledge_source_name)

                _assert_web_knowledge_source(result, knowledge_source_name)
            finally:
                await safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    async def test_list_knowledge_sources_includes_created_web_source(self, endpoint: str) -> None:
        _require_web_knowledge_source_capabilities(
            "azure.search.documents.indexes.aio.SearchIndexClient.create_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.list_knowledge_sources",
        )
        knowledge_source_name = self.get_resource_name("knowledge-source-list-web")

        async with make_index_client(endpoint) as client:
            try:
                await client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                results = [knowledge_source async for knowledge_source in client.list_knowledge_sources()]

                assert any(knowledge_source.name == knowledge_source_name for knowledge_source in results)
            finally:
                await safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    async def test_delete_knowledge_source_accepts_model_and_etag(self, endpoint: str) -> None:
        _require_web_knowledge_source_capabilities(
            "azure.search.documents.indexes.aio.SearchIndexClient.create_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.list_knowledge_sources",
        )
        knowledge_source_name = self.get_resource_name("knowledge-source-delete-web")

        async with make_index_client(endpoint) as client:
            try:
                original = await client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                assert original.e_tag is not None
                await client.delete_knowledge_source(
                    original,
                    match_condition=MatchConditions.IfNotModified,
                )
                results = [knowledge_source async for knowledge_source in client.list_knowledge_sources()]

                assert all(knowledge_source.name != knowledge_source_name for knowledge_source in results)
            finally:
                await safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    async def test_get_knowledge_source_status_returns_web_status(self, endpoint: str) -> None:
        _require_web_knowledge_source_capabilities(
            "azure.search.documents.indexes.aio.SearchIndexClient.create_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.delete_knowledge_source",
            "azure.search.documents.indexes.aio.SearchIndexClient.get_knowledge_source_status",
        )
        from azure.search.documents.indexes.models import KnowledgeSourceKind

        knowledge_source_name = self.get_resource_name("knowledge-source-get-status-web")

        async with make_index_client(endpoint) as client:
            try:
                await client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                result = await client.get_knowledge_source_status(knowledge_source_name)

                if result.kind is not None:
                    assert result.kind == KnowledgeSourceKind.WEB
                assert result.synchronization_status in {"creating", "active", "deleting"}
            finally:
                await safe_delete(client.delete_knowledge_source, knowledge_source_name)
