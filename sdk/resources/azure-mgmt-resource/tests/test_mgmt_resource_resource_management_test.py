# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from azure.mgmt.resource.resources import ResourceManagementClient
import pytest

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy


@pytest.mark.live_test_only
class TestMgmtResource(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.resource_client = self.create_mgmt_client(ResourceManagementClient)

    @recorded_by_proxy
    def test_operations(self):
        self.resource_client.operations.list()

    @RandomNameResourceGroupPreparer()
    @recorded_by_proxy
    def test_resources_list(self):
        result = list(self.resource_client.resources.list())
        assert len(result) > 0


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
