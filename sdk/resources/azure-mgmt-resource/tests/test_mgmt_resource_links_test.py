# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.mgmt.resource.links import ManagementLinkClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
import pytest


@pytest.mark.live_test_only
class TestMgmtResourceLinks(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(ManagementLinkClient)

    @RandomNameResourceGroupPreparer()
    @recorded_by_proxy
    def test_links(self):
        list(self.client.resource_links.list_at_subscription())
