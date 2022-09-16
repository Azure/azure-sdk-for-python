# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import azure.mgmt.appcontainers
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


class TestMgmtappcontainers(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(azure.mgmt.appcontainers.ContainerAppsAPIClient)

    def test_appcontainers_ContainerAppsOperations_list(self):
        result = self.mgmt_client.ContainerAppsOperations.list_by_subscription()
        assert list(result) is not None
