# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.mgmt.appcomplianceautomation import AppComplianceAutomationMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
import unittest

class TestMgmtAppComplianceAutomation(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(AppComplianceAutomationMgmtClient)

    @unittest.skip('lack of vaild token to authentication')
    @recorded_by_proxy
    def test_list_report(self):
        assert list(self.client.report.list()) == []

    @recorded_by_proxy
    def test_list_operations(self):
        assert list(self.client.operations.list())
