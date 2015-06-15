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
from .testutil import HttpStatusCode
from .mgmtutil import AzureMgmtTestCase

class MgmtStorageTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtStorageTest, self).setUp()
        self.storage_client = self.create_mgmt_client(azure.mgmt.storage.StorageManagementClient)

    def test_storage_accounts(self):
        with self.recording():
            self.create_resource_group()

            account_name = self.get_resource_name('pyarmstorage')

            result_check = self.storage_client.storage_accounts.check_name_availability(
                account_name,
            )
            self.assertEqual(result_check.status_code, HttpStatusCode.OK)
            self.assertTrue(result_check.name_available)

            params_create = azure.mgmt.storage.StorageAccountCreateParameters(
                location=self.region,
                account_type=azure.mgmt.storage.AccountType.standard_lrs,
            )
            result_create = self.storage_client.storage_accounts.create(
                self.group_name,
                account_name,
                params_create,
            )
            self.assertEqual(result_create.status_code, HttpStatusCode.OK)

            result_get = self.storage_client.storage_accounts.get_properties(
                self.group_name,
                account_name,
            )
            self.assertEqual(result_get.status_code, HttpStatusCode.OK)
            #self.assertEqual(result_get.storage_account.name, account_name)
            #self.assertEqual(
            #    result_get.storage_account.location,
            #    params_create.location,
            #)
            #self.assertEqual(
            #    result_get.storage_account.type,
            #    params_create.account_type,
            #)

            result_list_keys = self.storage_client.storage_accounts.list_keys(
                self.group_name,
                account_name,
            )
            self.assertEqual(result_list_keys.status_code, HttpStatusCode.OK)
            self.assertGreater(len(result_list_keys.storage_account_keys.key1), 0)
            self.assertGreater(len(result_list_keys.storage_account_keys.key2), 0)

            result_regen_keys = self.storage_client.storage_accounts.regenerate_key(
                self.group_name,
                account_name,
                azure.mgmt.storage.KeyName.key1,
            )
            self.assertEqual(result_regen_keys.status_code, HttpStatusCode.OK)
            self.assertNotEqual(
                result_regen_keys.storage_account_keys.key1,
                result_list_keys.storage_account_keys.key1,
            )
            self.assertEqual(
                result_regen_keys.storage_account_keys.key2,
                result_list_keys.storage_account_keys.key2,
            )

            #params_update = azure.mgmt.storage.StorageAccountUpdateParameters()
            #params_update.tags['tagname1'] = 'tagvalue1'
            #result_update = self.storage_client.storage_accounts.update(
            #    self.group_name,
            #    account_name,
            #    params_update,
            #)
            #self.assertEqual(result_update.status_code, HttpStatusCode.OK)

            #result_get = self.client.storage_accounts.get_properties(
            #    self.group_name,
            #    account_name,
            #)
            #self.assertEqual(result_get.status_code, HttpStatusCode.OK)
            #self.assertEqual(
            #    result_get.storage_account.tags['tagname1'],
            #    'tagvalue1',
            #)

            result_list = self.storage_client.storage_accounts.list_by_resource_group(
                self.group_name,
            )
            self.assertEqual(result_list.status_code, HttpStatusCode.OK)
            self.assertGreater(len(result_list.storage_accounts), 0)
            #self.assertEqual(
            #    result_list.storage_accounts[0].name,
            #    account_name,
            #)

            result_delete = self.storage_client.storage_accounts.delete(
                self.group_name,
                account_name,
            )
            self.assertEqual(result_delete.status_code, HttpStatusCode.OK)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
