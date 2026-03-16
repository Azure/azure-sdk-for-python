# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# covered ops:
#   resource_skus: 1/1

import pytest
import azure.mgmt.compute
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "westus"


@pytest.mark.live_test_only
class TestMgmtComputeResourceSkus(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(azure.mgmt.compute.ComputeManagementClient)

    @recorded_by_proxy
    def test_get_resource_skus(self):
        """Lists all available Resource SKUs with filter and extended locations."""
        count = 0
        for resource_sku in self.mgmt_client.resource_skus.list(
            filter="location eq 'westus'",
            include_extended_locations="true"
        ):
            count += 1

        assert count > 0
