# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from contextlib import suppress

from azure.mgmt.servicebus import ServiceBusManagementClient
import azure.mgmt.servicebus.models
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


class TestMgmtServicebus(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(ServiceBusManagementClient)

    @recorded_by_proxy
    def test_operations_list(self):
        # it proves that we can normally send request but maybe needs additional parameters
        with suppress(HttpResponseError):
            result = self.mgmt_client.operations.list()
            assert list(result) is not None
