# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest
import azure.mgmt.recoveryservices
from testutils.common_recordingtestcase import record
import azure.mgmt.resource.resources.models
from tests.mgmt_testcase import AzureMgmtTestCase,HttpStatusCode
import azure.common.exceptions
from azure.mgmt.recoveryservices.models import (StorageModelType, Vault, Sku, SkuName, VaultProperties,
                                                VaultExtendedInfoResource, VaultUsage, EnhancedSecurityState,
                                                StorageModelType
                                                      )
from tests.recoveryservices_testcase import MgmtRecoveryServicesTestDefinition, MgmtRecoveryServicesTestHelper

class MgmtRecoveryServicesTests(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRecoveryServicesTests, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.recoveryservices.RecoveryServicesClient
        )
        self.location = "westus"
        self.resource_name = "PythonSDKTestResource"
        self.test_definition = MgmtRecoveryServicesTestDefinition(self.settings.SUBSCRIPTION_ID, self.resource_name,
                                                                        self.group_name)
        self.test_helper = MgmtRecoveryServicesTestHelper(self)
        self.create_resource_group()

    @record
    def can_create_get_list_delete_vault_test(self):
        vault_name = self.test_definition.get_vault_name
        vault_name2 = "PythonSDKVault2"

        self.test_helper.create_vault(vault_name)
        vault = self.test_helper.get_vault(vault_name)
        self.assertIsNotNone(vault)

        self.test_helper.create_vault(vault_name2)
        vaults = self.test_helper.list_vaults()
        self.assertIsNotNone(vaults)
        self.assertTrue(vaults)

        self.test_helper.delete_vaults(vault_name2)

    @record
    def can_create_get_list_delete_vault_extended_info_test(self):
        vault_name = self.test_definition.get_vault_name
        self.test_helper.create_vault(vault_name)
        vault = self.test_helper.get_vault(vault_name)
        self.assertIsNotNone(vault)

        extended_info = self.test_helper.create_or_update_vault_extended_info(vault)

        self.assertIsNotNone(extended_info.integrity_key)

    @record
    def retrieve_vault_usages_test(self):
        vault_name = self.test_definition.get_vault_name
        self.test_helper.create_vault(vault_name)
        vault = self.test_helper.get_vault(vault_name)
        self.assertIsNotNone(vault)

        response = self.test_helper.list_vault_usages(vault_name)
        self.assertIsNotNone(response)
        self.assertNotEqual(len(response), 0)

        replication_usages = self.test_helper.list_replication_usages(vault_name)

        self.assertIsNotNone(replication_usages)
        self.assertEqual(len(replication_usages),0)













