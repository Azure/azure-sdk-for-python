# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.mgmt.selfhelp import SelfHelpMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

class TestMgmtSelfHelp(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(SelfHelpMgmtClient)

    @recorded_by_proxy
    def test_list_operations(self):
        assert list(self.client.operations.list())