# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.exceptions import ResourceNotFoundError
import azure.mgmt.network
from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
    recorded_by_proxy,
)
import pytest


class TestMgmtNetworkMixinOperation(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

    @RandomNameResourceGroupPreparer(location="eastus")
    @recorded_by_proxy
    def test_mixin_operation(self, resource_group):
        with pytest.raises(ResourceNotFoundError):
            self.mgmt_client.list_network_manager_effective_connectivity_configurations(
                resource_group_name=resource_group.name,
                virtual_network_name="virtual_network_name",
                parameters={},
            )
