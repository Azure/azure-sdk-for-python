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
        self.region = 'East US 2' # this is the ADL produciton region for now.
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
        params_create = azure.mgmt.datalake.store.models.DataLakeStoreAccount(
            location = self.region,
            identity = azure.mgmt.datalake.store.models.EncryptionIdentity(),
            encryption_config = azure.mgmt.datalake.store.models.EncryptionConfig(
                type = azure.mgmt.datalake.store.models.EncryptionConfigType.service_managed
            ),
            encryption_state = azure.mgmt.datalake.store.models.EncryptionState.enabled,
            tags={
                'tag1': 'value1'
            }
        )

        params_create_no_encryption = azure.mgmt.datalake.store.models.DataLakeStoreAccount(
            location = self.region,
            tags={
                'tag1': 'value1'
            }
        )
        # create and validate an ADLS account
        result_create = self.adls_account_client.account.create(
            self.group_name,
            account_name,
            params_create,
        )

        adls_account = result_create.result()
        
        # full validation of the create
        self.assertEqual(adls_account.name, account_name)

        # TODO: re-enable once it is determined why this property is still in "creating" state.
        # self.assertEqual(azure.mgmt.datalake.store.models.DataLakeStoreAccountStatus.succeeded, adls_account.provisioning_state)

        self.assertIsNotNone(adls_account.id)
        self.assertIn(account_name, adls_account.id)
        # self.assertIn(account_name, adls_account.endpoint)
        self.assertEqual(self.region, adls_account.location)
        self.assertEqual('Microsoft.DataLakeStore/accounts', adls_account.type)
        # self.assertEqual(azure.mgmt.datalake.store.models.EncryptionState.enabled, adls_account.encryption_state)
        self.assertEqual('SystemAssigned', adls_account.identity.type)
        # self.assertIsNotNone(adls_account.identity.principal_id)
        # self.assertIsNotNone(adls_account.identity.tenant_id)
        self.assertEqual(adls_account.tags['tag1'], 'value1')

        # get the account and do the same checks
        adls_account = self.adls_account_client.account.get(
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
        result_create = self.adls_account_client.account.create(
            self.group_name,
            account_name_no_encryption,
            params_create_no_encryption,
        )

        adls_account_no_encryption = result_create.result()
        adls_account_no_encryption = self.adls_account_client.account.get(
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
        result_list = self.adls_account_client.account.list_by_resource_group(
            self.group_name,
        )
        result_list = list(result_list)
        self.assertGreater(len(result_list), 1)

        result_list = self.adls_account_client.account.list()
        result_list = list(result_list)
        self.assertGreater(len(result_list), 1)

        
        # update the tags
        adls_account = self.adls_account_client.account.update(
            self.group_name,
            account_name,
            azure.mgmt.datalake.store.models.DataLakeStoreAccountUpdateParameters(
                tags = {
                    'tag2': 'value2'
                }
            )
        ).result()

        self.assertEqual(adls_account.tags['tag2'], 'value2')
        self.adls_account_client.account.delete(
            self.group_name,
            account_name
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
