# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from collections import namedtuple

import azure.mgmt.keyvault.models
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtKeyVaultTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtKeyVaultTest, self).setUp()
        self.keyvault_client = self.create_mgmt_client(
            azure.mgmt.keyvault.KeyVaultManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_vaults_operations(self):
        account_name = self.get_resource_name('pykv')

        vault = self.keyvault_client.vaults.create_or_update(
            self.group_name,
            account_name,
            {
                'location': self.region,
                'properties': {
                    'sku': {
                        'name': 'standard'
                    },
                    # Fake random GUID
                    'tenant_id': '6819f86e-5d41-47b0-9297-334f33d7922d',
                    'access_policies': []
                }
            }
        )
        self.assertEqual(vault.name, account_name)

        vault = self.keyvault_client.vaults.get(
            self.group_name,
            account_name
        )
        self.assertEqual(vault.name, account_name)
        
        vaults = list(self.keyvault_client.vaults.list_by_resource_group(self.group_name))
        self.assertEqual(len(vaults), 1)
        self.assertIsInstance(vaults[0], azure.mgmt.keyvault.models.Vault)
        self.assertEqual(vaults[0].name, account_name)

        vaults = list(self.keyvault_client.vaults.list())
        self.assertGreater(len(vaults), 0)
        self.assertTrue(all(isinstance(v, azure.mgmt.keyvault.models.Resource) for v in vaults))

        self.keyvault_client.vaults.delete(
            self.group_name,
            account_name
        )



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
