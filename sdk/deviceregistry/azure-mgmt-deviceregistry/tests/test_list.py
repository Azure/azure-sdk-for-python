# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import azure.mgmt.deviceregistry
from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
    recorded_by_proxy,
)

AZURE_LOCATION = "eastus"

@pytest.mark.live_test_only
class TestMgmtDeviceRegistryList(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(azure.mgmt.deviceregistry.DeviceRegistryMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_list_by_subscription(self):
        result = self.mgmt_client.asset_endpoint_profiles.list_by_subscription()
        assert len(list(result)) == 0

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_list_by_resource_group(self, resource_group):
        result = self.mgmt_client.asset_endpoint_profiles.list_by_resource_group(
            resource_group_name=resource_group.name
        )
        assert len(list(result)) == 0
