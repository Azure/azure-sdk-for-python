# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Operations operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase


class TestOperations(DiscoveryMgmtTestCase):
    """Tests for Operations operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)

    @pytest.mark.skip(reason="operations.list() endpoint doesn't support 2026-02-01-preview API yet")
    @recorded_by_proxy
    def test_list_operations(self):
        """Test listing available API operations."""
        operations = list(self.client.operations.list())
        assert len(operations) > 0
        assert hasattr(operations[0], "name")
