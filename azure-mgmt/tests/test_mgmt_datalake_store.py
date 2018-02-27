# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.datalake.store
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtDataLakeStoreTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDataLakeStoreTest, self).setUp()
        # this is the ADL produciton region for now
        self.region = 'East US 2'
        self.adls_account_client = self.create_mgmt_client(
            azure.mgmt.datalake.store.DataLakeStoreAccountManagementClient
        )

        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_adls_accounts(self):
        # define account params
        account_name = self.get_resource_name('pyarmadls')
        account_name_no_encryption = self.get_resource_name('pyarmadls2')

        params_create = azure.mgmt.datalake.store.models.CreateDataLakeStoreAccountParameters(
            location = self.region,
            identity = azure.mgmt.datalake.store.models.EncryptionIdentity(),
            encryption_config = azure.mgmt.datalake.store.models.EncryptionConfig(
                type = azure.mgmt.datalake.store.models.EncryptionConfigType.service_managed
            ),
            encryption_state = azure.mgmt.datalake.store.models.EncryptionState.enabled,
            tags = {
                'tag1' : 'value1'
            }
        )

        params_create_no_encryption = azure.mgmt.datalake.store.models.CreateDataLakeStoreAccountParameters(
            location = self.region,
            tags = {
                'tag1' : 'value1'
            }
        )

        # ensure that the account name is available
        name_availability = self.adls_account_client.accounts.check_name_availability(
            self.region.replace(" ", ""), 
            account_name
        )
        self.assertTrue(name_availability.name_available)

        # create and validate an ADLS account
        adls_account = self.adls_account_client.accounts.create(
            self.group_name,
            account_name,
            params_create,
        ).result()

        # ensure that the account name is no longer available
        name_availability = self.adls_account_client.accounts.check_name_availability(
            self.region.replace(" ", ""), 
            account_name
        )
        self.assertFalse(name_availability.name_available)
        
        # full validation of the create
        self.assertEqual(adls_account.name, account_name)
        self.assertEqual(azure.mgmt.datalake.store.models.DataLakeStoreAccountStatus.succeeded, adls_account.provisioning_state)
        self.assertIsNotNone(adls_account.id)
        self.assertIn(account_name, adls_account.id)
        self.assertIn(account_name, adls_account.endpoint)
        self.assertEqual(self.region, adls_account.location)
        self.assertEqual('Microsoft.DataLakeStore/accounts', adls_account.type)
        self.assertEqual(azure.mgmt.datalake.store.models.EncryptionState.enabled, adls_account.encryption_state)
        self.assertEqual('SystemAssigned', adls_account.identity.type)
        self.assertIsNotNone(adls_account.identity.principal_id)
        self.assertIsNotNone(adls_account.identity.tenant_id)
        self.assertEqual(adls_account.tags['tag1'], 'value1')

        # get the account and do the same checks
        adls_account = self.adls_account_client.accounts.get(
            self.group_name,
            account_name
        )

        # full validation
        self.assertEqual(adls_account.name, account_name)
        self.assertEqual(azure.mgmt.datalake.store.models.DataLakeStoreAccountStatus.succeeded, adls_account.provisioning_state)
        self.assertIsNotNone(adls_account.id)
        self.assertIn(account_name, adls_account.id)
        self.assertIn(account_name, adls_account.endpoint)
        self.assertEqual(self.region, adls_account.location)
        self.assertEqual('Microsoft.DataLakeStore/accounts', adls_account.type)
        self.assertEqual(azure.mgmt.datalake.store.models.EncryptionState.enabled, adls_account.encryption_state)
        self.assertEqual('SystemAssigned', adls_account.identity.type)
        self.assertIsNotNone(adls_account.identity.principal_id)
        self.assertIsNotNone(adls_account.identity.tenant_id)
        self.assertEqual(adls_account.tags['tag1'], 'value1')

        # create no encryption account
        # create and validate an ADLS account
        adls_account_no_encryption = self.adls_account_client.accounts.create(
            self.group_name,
            account_name_no_encryption,
            params_create_no_encryption,
        ).result()

        adls_account_no_encryption = self.adls_account_client.accounts.get(
            self.group_name,
            account_name_no_encryption
        )

        # full validation of the create
        self.assertEqual(adls_account_no_encryption.name, account_name_no_encryption)
        self.assertEqual(azure.mgmt.datalake.store.models.DataLakeStoreAccountStatus.succeeded, adls_account_no_encryption.provisioning_state)
        self.assertIsNotNone(adls_account_no_encryption.id)
        self.assertIn(account_name_no_encryption, adls_account_no_encryption.id)
        self.assertIn(account_name_no_encryption, adls_account_no_encryption.endpoint)
        self.assertEqual(self.region, adls_account_no_encryption.location)
        self.assertEqual('Microsoft.DataLakeStore/accounts', adls_account_no_encryption.type)
        self.assertEqual(azure.mgmt.datalake.store.models.EncryptionState.enabled, adls_account_no_encryption.encryption_state)
        self.assertIsNone(adls_account_no_encryption.identity)
        self.assertEqual(adls_account_no_encryption.tags['tag1'], 'value1')

        # list all the accounts
        result_list = list(self.adls_account_client.accounts.list_by_resource_group(self.group_name))
        self.assertGreater(len(result_list), 1)

        result_list = list(self.adls_account_client.accounts.list())
        self.assertGreater(len(result_list), 1)

        # update the tags
        adls_account = self.adls_account_client.accounts.update(
            self.group_name,
            account_name,
            azure.mgmt.datalake.store.models.UpdateDataLakeStoreAccountParameters(
                tags = {
                    'tag2' : 'value2'
                }
            )
        ).result()

        self.assertEqual(adls_account.tags['tag2'], 'value2')
        
        # confirm that 'locations.get_capability' is functional 
        get_capability = self.adls_account_client.locations.get_capability(self.region.replace(" ", ""))
        self.assertIsNotNone(get_capability)

        # confirm that 'operations.list' is functional
        operations_list = self.adls_account_client.operations.list()
        self.assertIsNotNone(operations_list)
        
        self.adls_account_client.accounts.delete(
            self.group_name,
            account_name
        ).wait()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
