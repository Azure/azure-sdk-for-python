# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.network import NetworkManagementClient
from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
    recorded_by_proxy,
)

API_VERSION = "2021-02-01"

def raw_requst_check(request):
    assert request.http_request.query["api-version"] == API_VERSION

class TestMgmtNetworkApiVersion(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            NetworkManagementClient,
            api_version=API_VERSION,
        )

    @RandomNameResourceGroupPreparer(location="eastus")
    @recorded_by_proxy
    def test_api_version(self, resource_group):
        # check api version validation
        with pytest.raises(ValueError):
            self.mgmt_client.list_active_security_admin_rules(resource_group.name, "network_manager_name", {})

        # check whether api version is passed to request for normal operation group
        result = list(self.mgmt_client.public_ip_addresses.list(resource_group.name, raw_request_hook=raw_requst_check))
        assert len(result) == 0

        # check whether api version is passed to request for mixin operation group
        self.mgmt_client.check_dns_name_availability(location="eastus", domain_name_label="mydomain", raw_request_hook=raw_requst_check)
