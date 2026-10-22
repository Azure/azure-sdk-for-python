# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os

import pytest
from azure.mgmt.fileshares import FileSharesMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

# Per-package overrides. Values are loaded from
# `sdk/fileshares/azure-mgmt-fileshares/.env` by tests/conftest.py (load_dotenv).
ARM_ENDPOINT = os.environ.get("ARM_ENDPOINT", "https://eastus2euap.management.azure.com")


class TestFileSharesOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesMgmtClient,
            base_url=ARM_ENDPOINT,
            # Canary ARM endpoints accept tokens issued for the global ARM resource.
            credential_scopes=["https://management.azure.com/.default"],
        )

    # No proxy recording is committed for this test yet, so it only runs when
    # AZURE_TEST_RUN_LIVE=true. Once a recording is captured and pushed to the
    # assets repo, this marker can be removed.
    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_operations_list(self):
        # `operations.list()` is a tenant-scope ARM call that needs no resource group
        # or pre-existing resources, making it ideal for a smoke test.
        response = self.client.operations.list()
        result = [r for r in response]
        assert len(result) > 0
        # Every ARM operation should expose a name like "Microsoft.FileShares/..."
        for op in result:
            assert op.name and op.name.startswith("Microsoft.FileShares/")
