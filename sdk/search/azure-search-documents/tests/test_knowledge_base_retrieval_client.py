# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``KnowledgeBaseRetrievalClient`` patched public behavior."""

from azure.core.credentials import AzureKeyCredential

from _capabilities import require_capability

ENDPOINT = "https://my-search-service.search.windows.net"
KEY = "fake-api-key"
KNOWLEDGE_BASE_NAME = "hotel-kb"
AUDIENCE = "https://search.azure.com/"


class TestKnowledgeBaseRetrievalClientConstructor:
    def test_constructor_translates_audience_to_credential_scope(self):
        require_capability("KnowledgeBaseRetrievalClient")
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient

        client = KnowledgeBaseRetrievalClient(
            ENDPOINT,
            AzureKeyCredential(KEY),
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            audience=AUDIENCE,
        )

        assert client._config.endpoint == ENDPOINT
        assert client._config.knowledge_base_name == KNOWLEDGE_BASE_NAME
        assert client._config.credential_scopes == ["https://search.azure.com/.default"]
