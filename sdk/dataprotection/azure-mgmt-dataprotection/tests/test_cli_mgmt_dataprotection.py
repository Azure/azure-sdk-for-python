# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from azure.mgmt.dataprotection import DataProtectionMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

class TestMgmtDataProtection(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(DataProtectionMgmtClient)

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_list_by_resource_group(self, resource_group):
        assert list(self.client.backup_vaults.get_in_resource_group(resource_group.name)) == []

    @recorded_by_proxy
    def test_list_operations(self):
        assert list(self.client.data_protection_operations.list())
