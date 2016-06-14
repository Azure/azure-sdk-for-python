# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.storage
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtStorageTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtStorageTest, self).setUp()
        self.storage_client = self.create_mgmt_client(
            azure.mgmt.storage.StorageManagementClient
        )

    @record
    def test_storage_accounts(self):
        self.create_resource_group()

        account_name = self.get_resource_name('pyarmstorage')

        result_check = self.storage_client.storage_accounts.check_name_availability(
            account_name
        )
        self.assertTrue(result_check)

        params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
            location=self.region,
            account_type=azure.mgmt.storage.models.AccountType.standard_lrs,
        )
        result_create = self.storage_client.storage_accounts.create(
            self.group_name,
            account_name,
            params_create,
        )
        result_create.wait()

        result_get = self.storage_client.storage_accounts.get_properties(
            self.group_name,
            account_name,
        )

        result_list_keys = self.storage_client.storage_accounts.list_keys(
            self.group_name,
            account_name,
        )
        self.assertGreater(len(result_list_keys.key1), 0)
        self.assertGreater(len(result_list_keys.key2), 0)

        result_regen_keys = self.storage_client.storage_accounts.regenerate_key(
            self.group_name,
            account_name,
            "key1"
        )
        self.assertNotEqual(
            result_regen_keys.key1,
            result_list_keys.key1,
        )
        self.assertEqual(
            result_regen_keys.key2,
            result_list_keys.key2,
        )

        result_list = self.storage_client.storage_accounts.list_by_resource_group(
            self.group_name,
        )
        result_list = list(result_list)
        self.assertGreater(len(result_list), 0)

        result_delete = self.storage_client.storage_accounts.delete(
            self.group_name,
            account_name,
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
