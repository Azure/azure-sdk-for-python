# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 5
# Methods Covered : 5
# Examples Total  : 5
# Examples Tested : 5
# Coverage %      : 100
# ----------------------

#  web_application_firewall_policies: /5

import unittest

from azure.core.exceptions import ResourceNotFoundError
import azure.mgmt.network
from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
    recorded_by_proxy,
)
import pytest

AZURE_LOCATION = "eastus"


class TestMgmtNetworkMixinOperation(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mixin_operation(self, resource_group):
        with pytest.raises(ResourceNotFoundError):
          self.mgmt_client.list_network_manager_effective_connectivity_configurations(
              resource_group_name=resource_group.name,
              virtual_network_name="virtual_network_name",
              parameters={},
          )


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
