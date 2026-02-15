# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.confidentialledger import ConfidentialLedger
from azure.mgmt.confidentialledger.aio import ConfidentialLedger as AsyncConfidentialLedger

from devtools_testutils import AzureMgmtRecordedTestCase


class TestApiVersion(AzureMgmtRecordedTestCase):
    """Test suite to verify API version handling"""

    def test_default_api_version_sync(self):
        """Test that default api_version is 2025-06-10-preview for sync client"""
        client = self.create_mgmt_client(ConfidentialLedger)
        assert client._config.api_version == "2025-06-10-preview"

    def test_override_api_version_sync(self):
        """Test backward compatibility: users can override api_version to older version"""
        client = self.create_mgmt_client(ConfidentialLedger, api_version="2024-09-19-preview")
        assert client._config.api_version == "2024-09-19-preview"

    def test_default_api_version_async(self):
        """Test that default api_version is 2025-06-10-preview for async client"""
        client = self.create_mgmt_client(AsyncConfidentialLedger)
        assert client._config.api_version == "2025-06-10-preview"

    def test_override_api_version_async(self):
        """Test backward compatibility: users can override api_version to older version (async)"""
        client = self.create_mgmt_client(AsyncConfidentialLedger, api_version="2024-09-19-preview")
        assert client._config.api_version == "2024-09-19-preview"
