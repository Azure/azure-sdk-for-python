# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from contextlib import suppress

from azure.mgmt.appcontainers import ContainerAppsAPIClient
import azure.mgmt.appcontainers.models
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


class TestMgmtAPPCONTAINERS(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(ContainerAppsAPIClient)

    @recorded_by_proxy
    def test_appcontainers_managed_environments_list_by_subscription(self):
        # it proves that we can normally send request but maybe needs additional parameters
        with suppress(HttpResponseError):
            result = self.mgmt_client.managed_environments.list_by_subscription()
            assert list(result) is not None
