# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Knowledge Bases operations.

Covers 1 method on BookshelfClient.knowledge_bases:
  - list (Paged)
"""
import pytest
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import HttpResponseError
from .testcase import DiscoveryBookshelfTestCase


class TestKnowledgeBasesOperations(DiscoveryBookshelfTestCase):
    """Tests for KnowledgeBasesOperations."""

    @recorded_by_proxy
    def test_list(self):
        """Test listing knowledge bases."""
        client = self.create_bookshelf_client()
        knowledge_bases = list(client.knowledge_bases.list())
        assert isinstance(knowledge_bases, list)
        assert len(knowledge_bases) > 0
        for kb in knowledge_bases:
            # Required read-visible fields per spec (BaseKnowledgeBase)
            assert kb.name is not None
            assert len(kb.name) <= 24                 # @maxLength(24)
            assert kb.version is not None
            assert kb.bookshelf_name is not None
            # Optional but useful sanity checks
            assert kb.provisioning_state is not None  # set after first reconcile
            assert kb.status is not None              # IndexingStatus
