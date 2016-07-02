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
        self.assertTrue(result_check.name_available)
        self.assertFalse(result_check.reason)
        self.assertFalse(result_check.message)

        params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
            sku=azure.mgmt.storage.models.Sku(azure.mgmt.storage.models.SkuName.standard_lrs),
            kind=azure.mgmt.storage.models.Kind.storage,
            location=self.region
        )
        result_create = self.storage_client.storage_accounts.create(
            self.group_name,
            account_name,
            params_create,
        )
        storage_account = result_create.result()
        self.assertEqual(storage_account.name, account_name)

        storage_account = self.storage_client.storage_accounts.get_properties(
            self.group_name,
            account_name,
        )
        self.assertEqual(storage_account.name, account_name)

        result_list_keys = self.storage_client.storage_accounts.list_keys(
            self.group_name,
            account_name,
        )
        keys = {v.key_name: (v.value, v.permissions) for v in result_list_keys.keys}
        self.assertEqual(len(keys), 2)
        self.assertGreater(len(keys['key1'][0]), 0)
        self.assertGreater(len(keys['key1'][0]), 0)

        result_regen_keys = self.storage_client.storage_accounts.regenerate_key(
            self.group_name,
            account_name,
            "key1"
        )
        new_keys = {v.key_name: (v.value, v.permissions) for v in result_regen_keys.keys}
        self.assertEqual(len(new_keys), 2)
        self.assertNotEqual(
            new_keys['key1'][0],
            keys['key1'][0],
        )
        self.assertEqual(
            new_keys['key2'][0],
            keys['key2'][0],
        )

        result_list = self.storage_client.storage_accounts.list_by_resource_group(
            self.group_name,
        )
        result_list = list(result_list)
        self.assertGreater(len(result_list), 0)

        result_list = self.storage_client.storage_accounts.list()
        result_list = list(result_list)
        self.assertGreater(len(result_list), 0)

        self.storage_client.storage_accounts.delete(
            self.group_name,
            account_name,
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
