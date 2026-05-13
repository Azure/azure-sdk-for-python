# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchIndexClient`` web knowledge source operations."""

from __future__ import annotations

from azure.core import MatchConditions
from azure.search.documents.indexes.models import (
    KnowledgeSourceKind,
    WebKnowledgeSource,
    WebKnowledgeSourceDomain,
    WebKnowledgeSourceDomains,
    WebKnowledgeSourceParameters,
)
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import live_test, make_index_client, safe_delete

WEB_DOMAIN_ADDRESS = "https://learn.microsoft.com"
WEB_KNOWLEDGE_SOURCE_DESCRIPTION = "Web knowledge source for SearchIndexClient live coverage"
REPLACEMENT_WEB_KNOWLEDGE_SOURCE_DESCRIPTION = "Web knowledge source replacement for SearchIndexClient live coverage"


def _build_web_knowledge_source(knowledge_source_name: str) -> WebKnowledgeSource:
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


def _assert_web_knowledge_source(result: WebKnowledgeSource, knowledge_source_name: str) -> None:
    assert result.name == knowledge_source_name
    assert result.kind == KnowledgeSourceKind.WEB
    assert result.description == WEB_KNOWLEDGE_SOURCE_DESCRIPTION
    assert result.web_parameters is not None
    assert result.web_parameters.domains is not None
    assert result.web_parameters.domains.allowed_domains is not None
    assert result.web_parameters.domains.allowed_domains[0].address == WEB_DOMAIN_ADDRESS
    assert result.web_parameters.domains.allowed_domains[0].include_subpages is True


class TestSearchIndexClientWebKnowledgeSources(AzureRecordedTestCase):
    @live_test()
    def test_create_knowledge_source_returns_web_source(self, endpoint: str) -> None:
        knowledge_source_name = self.get_resource_name("knowledge-source-create-web")

        with make_index_client(endpoint) as client:
            try:
                result = client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                _assert_web_knowledge_source(result, knowledge_source_name)
                assert result.e_tag is not None
            finally:
                safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    def test_create_or_update_knowledge_source_uses_model_name_and_etag(self, endpoint: str) -> None:
        knowledge_source_name = self.get_resource_name("knowledge-source-create-or-update-web")

        with make_index_client(endpoint) as client:
            try:
                original = client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))
                replacement = WebKnowledgeSource(
                    name=knowledge_source_name,
                    description=REPLACEMENT_WEB_KNOWLEDGE_SOURCE_DESCRIPTION,
                    web_parameters=original.web_parameters,
                )
                replacement.e_tag = original.e_tag

                result = client.create_or_update_knowledge_source(
                    replacement,
                    match_condition=MatchConditions.IfNotModified,
                )

                assert result.name == knowledge_source_name
                assert result.kind == KnowledgeSourceKind.WEB
                assert result.description == REPLACEMENT_WEB_KNOWLEDGE_SOURCE_DESCRIPTION
                assert result.e_tag != original.e_tag
            finally:
                safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    def test_get_knowledge_source_returns_named_web_source(self, endpoint: str) -> None:
        knowledge_source_name = self.get_resource_name("knowledge-source-get-web")

        with make_index_client(endpoint) as client:
            try:
                client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                result = client.get_knowledge_source(knowledge_source_name)

                _assert_web_knowledge_source(result, knowledge_source_name)
            finally:
                safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    def test_list_knowledge_sources_includes_created_web_source(self, endpoint: str) -> None:
        knowledge_source_name = self.get_resource_name("knowledge-source-list-web")

        with make_index_client(endpoint) as client:
            try:
                client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                results = list(client.list_knowledge_sources())

                assert any(knowledge_source.name == knowledge_source_name for knowledge_source in results)
            finally:
                safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    def test_delete_knowledge_source_accepts_model_and_etag(self, endpoint: str) -> None:
        knowledge_source_name = self.get_resource_name("knowledge-source-delete-web")

        with make_index_client(endpoint) as client:
            try:
                original = client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                assert original.e_tag is not None
                client.delete_knowledge_source(
                    original,
                    match_condition=MatchConditions.IfNotModified,
                )
                results = list(client.list_knowledge_sources())

                assert all(knowledge_source.name != knowledge_source_name for knowledge_source in results)
            finally:
                safe_delete(client.delete_knowledge_source, knowledge_source_name)

    @live_test()
    def test_get_knowledge_source_status_returns_web_status(self, endpoint: str) -> None:
        knowledge_source_name = self.get_resource_name("knowledge-source-get-status-web")

        with make_index_client(endpoint) as client:
            try:
                client.create_knowledge_source(_build_web_knowledge_source(knowledge_source_name))

                result = client.get_knowledge_source_status(knowledge_source_name)

                assert result.kind == KnowledgeSourceKind.WEB
                assert result.synchronization_status in {"creating", "active", "deleting"}
            finally:
                safe_delete(client.delete_knowledge_source, knowledge_source_name)
