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

TEST_API_VERSION = "2021-02-01"


def raw_requst_check(request):
    assert request.http_request.query["api-version"] == TEST_API_VERSION


@pytest.mark.live_test_only
class TestMgmtNetworkApiVersion(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            NetworkManagementClient,
            api_version=TEST_API_VERSION,
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
        self.mgmt_client.check_dns_name_availability(
            location="eastus", domain_name_label="mydomain", raw_request_hook=raw_requst_check
        )

    def fake_client(self, api_version):
        return NetworkManagementClient(credential="", subscription_id="", api_version=api_version)

    def test_invalid_api_version(self):
        client = self.fake_client(api_version="1000-01-01")
        # normal operation group
        with pytest.raises(ValueError):
            list(client.public_ip_addresses.list("resource_group_name"))

        # mixin operation group
        with pytest.raises(ValueError):
            client.check_dns_name_availability(location="eastus", domain_name_label="mydomain")
