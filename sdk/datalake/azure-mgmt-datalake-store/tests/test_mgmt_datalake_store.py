# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import azure.mgmt.datalake.store
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure.mgmt.datalake.store import models
# from azure.mgmt.network import NetworkManagementClient

# this is the ADL produciton region for now
LOCATION = 'eastus2'
VIRTUAL_NETWORK_NAME = 'Testvirtualnetworkname'
SUBNET_NAME = "TestSubnet"
PRIVATE_ENDPOINT_NAME = "myPrivateEndpoint"


@unittest.skip("skip test")
class MgmtDataLakeStoreTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDataLakeStoreTest, self).setUp()
        self.adls_account_client = self.create_mgmt_client(
            azure.mgmt.datalake.store.DataLakeStoreAccountManagementClient
        )

    # def _create_network(self, resource_group):
    #     self.network_client = self.create_mgmt_client(NetworkManagementClient)
    #
    #     # Create virtual network[put]
    #     BODY = {
    #         "address_space": {
    #             "address_prefixes": [
    #                 "10.0.0.0/16"
    #             ]
    #         },
    #         "location": LOCATION
    #     }
    #     result = self.network_client.virtual_networks.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME,
    #                                                                          BODY)
    #     result.result()
    #
    #     # Create subnet[put]
    #     BODY = {
    #         "address_prefix": "10.0.0.0/24"
    #     }
    #     result = self.network_client.subnets.begin_create_or_update(resource_group.name, VIRTUAL_NETWORK_NAME,
    #                                                                 SUBNET_NAME, BODY)
    #     result.result()
    #
    #     # Create private endpoint
    #     BODY = {
    #         "location": LOCATION,
    #         "properties": {
    #             "subnet": {
    #                 "id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME
    #             }
    #         }
    #     }
    #     result = self.network_client.private_endpoints.begin_create_or_update(resource_group.name,
    #                                                                           PRIVATE_ENDPOINT_NAME, BODY)
    #     result.result()
    #
    # def _delete_network(self, resource_group):
    #     result = self.network_client.private_endpoints.begin_delete(resource_group.name, PRIVATE_ENDPOINT_NAME)
    #     result.result()
    #
    #     result = self.network_client.subnets.begin_delete(resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
    #     result.result()
    #
    #     result = self.network_client.virtual_networks.begin_delete(resource_group.name, VIRTUAL_NETWORK_NAME)
    #     result.result()
    #
    # @unittest.skip("network has problems")
    # @ResourceGroupPreparer(location=LOCATION)
    # def test_vnet_operations(self, location, resource_group):
    #     self._create_network(resource_group)
    #
    #     account_name = self.get_resource_name('adlsacct')
    #     vnet_rule_name = self.get_resource_name('vnetrule1')
    #
    #     subnet_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(
    #         self.settings.SUBSCRIPTION_ID, resource_group.name, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
    #     virtual_network_rule = models.CreateVirtualNetworkRuleWithAccountParameters(
    #         name=vnet_rule_name,
    #         subnet_id=subnet_id
    #     )
    #
    #     params_create = models.CreateDataLakeStoreAccountParameters(
    #         location=location,
    #         firewall_state=models.FirewallState.enabled,
    #         firewall_allow_azure_ips=models.FirewallAllowAzureIpsState.enabled,
    #         virtual_network_rules=[virtual_network_rule]
    #     )
    #
    #     # create and validate an ADLS account
    #     response_create = self.adls_account_client.accounts.begin_create(
    #         resource_group.name,
    #         account_name,
    #         params_create,
    #     ).result()
    #     self.assertEqual(models.DataLakeStoreAccountStatus.succeeded, response_create.provisioning_state)
    #
    #     # get the account and ensure that all the values are properly set
    #     response_get = self.adls_account_client.accounts.get(
    #         resource_group.name,
    #         account_name
    #     )
    #
    #     # Validate the account creation process
    #     self.assertEqual(models.DataLakeStoreAccountStatus.succeeded, response_get.provisioning_state)
    #     self.assertEqual(response_get.name, account_name)
    #
    #     # Validate firewall state
    #     self.assertEqual(models.FirewallState.enabled, response_get.firewall_state)
    #     self.assertEqual(models.FirewallAllowAzureIpsState.enabled, response_get.firewall_allow_azure_ips)
    #
    #     # Validate virtual network state
    #     self.assertEqual(1, len(response_get.virtual_network_rules))
    #     self.assertEqual(vnet_rule_name, response_get.virtual_network_rules[0].name)
    #     self.assertEqual(subnet_id, response_get.virtual_network_rules[0].subnet_id)
    #
    #     vnet_rule = self.adls_account_client.virtual_network_rules.get(
    #         resource_group.name,
    #         account_name,
    #         vnet_rule_name
    #     )
    #     self.assertEqual(vnet_rule_name, vnet_rule.name)
    #     self.assertEqual(subnet_id, vnet_rule.subnet_id)
    #
    #     updated_subnet_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/updatedSubnetId'.format(
    #         self.settings.SUBSCRIPTION_ID, resource_group.name, VIRTUAL_NETWORK_NAME)
    #
    #     # Update the virtual network rule to change the subnetId
    #     vnet_rule = self.adls_account_client.virtual_network_rules.create_or_update(
    #         resource_group.name,
    #         account_name,
    #         vnet_rule_name,
    #         updated_subnet_id
    #     )
    #     self.assertEqual(updated_subnet_id, vnet_rule.subnet_id)
    #
    #     # Remove the virtual network rule and verify it is gone
    #     self.adls_account_client.virtual_network_rules.delete(
    #         resource_group.name,
    #         account_name,
    #         vnet_rule_name
    #     )
    #     # self.assertRaises(CloudError, lambda: self.adls_account_client.virtual_network_rules.get(
    #     #     resource_group.name,
    #     #     account_name,
    #     #     vnet_rule_name
    #     # ))
    #
    #     self._delete_network()

    @ResourceGroupPreparer(location=LOCATION)
    def test_adls_accounts(self, resource_group, location):
        # define account params
        account_name = self.get_resource_name('testadls')
        account_name_no_encryption = self.get_resource_name('testadls2')

        params_create = azure.mgmt.datalake.store.models.CreateDataLakeStoreAccountParameters(
            location=location,
            identity=azure.mgmt.datalake.store.models.EncryptionIdentity(),
            encryption_config=azure.mgmt.datalake.store.models.EncryptionConfig(
                type=azure.mgmt.datalake.store.models.EncryptionConfigType.service_managed
            ),
            encryption_state=azure.mgmt.datalake.store.models.EncryptionState.enabled,
            tags={
                'tag1': 'value1'
            }
        )

        params_create_no_encryption = azure.mgmt.datalake.store.models.CreateDataLakeStoreAccountParameters(
            location=location,
            tags={
                'tag1': 'value1'
            }
        )

        # ensure that the account name is available
        name_availability = self.adls_account_client.accounts.check_name_availability(
            location.replace(" ", ""),
            {
                'name': account_name,
                "type": "Microsoft.DataLakeStore/accounts"
            }
        )
        self.assertTrue(name_availability.name_available)

        # create and validate an ADLS account
        adls_account = self.adls_account_client.accounts.begin_create(
            resource_group.name,
            account_name,
            params_create,
        ).result()

        # ensure that the account name is no longer available
        name_availability = self.adls_account_client.accounts.check_name_availability(
            location.replace(" ", ""),
            {
                'name': account_name,
                "type": "Microsoft.DataLakeStore/accounts"
            }
        )
        self.assertFalse(name_availability.name_available)

        # full validation of the create
        self.assertEqual(adls_account.name, account_name)
        self.assertEqual(azure.mgmt.datalake.store.models.DataLakeStoreAccountStatus.succeeded,
                         adls_account.provisioning_state)
        self.assertIsNotNone(adls_account.id)
        self.assertIn(account_name, adls_account.id)
        self.assertIn(account_name, adls_account.endpoint)
        self.assertEqual(location, adls_account.location)
        self.assertEqual('Microsoft.DataLakeStore/accounts', adls_account.type)
        self.assertEqual(azure.mgmt.datalake.store.models.EncryptionState.enabled, adls_account.encryption_state)
        self.assertEqual('SystemAssigned', adls_account.identity.type)
        self.assertIsNotNone(adls_account.identity.principal_id)
        self.assertIsNotNone(adls_account.identity.tenant_id)
        self.assertEqual(adls_account.tags['tag1'], 'value1')

        # get the account and do the same checks
        adls_account = self.adls_account_client.accounts.get(
            resource_group.name,
            account_name
        )

        # full validation
        self.assertEqual(adls_account.name, account_name)
        self.assertEqual(azure.mgmt.datalake.store.models.DataLakeStoreAccountStatus.succeeded,
                         adls_account.provisioning_state)
        self.assertIsNotNone(adls_account.id)
        self.assertIn(account_name, adls_account.id)
        self.assertIn(account_name, adls_account.endpoint)
        self.assertEqual(location, adls_account.location)
        self.assertEqual('Microsoft.DataLakeStore/accounts', adls_account.type)
        self.assertEqual(azure.mgmt.datalake.store.models.EncryptionState.enabled, adls_account.encryption_state)
        self.assertEqual('SystemAssigned', adls_account.identity.type)
        self.assertIsNotNone(adls_account.identity.principal_id)
        self.assertIsNotNone(adls_account.identity.tenant_id)
        self.assertEqual(adls_account.tags['tag1'], 'value1')

        # create no encryption account
        # create and validate an ADLS account
        adls_account_no_encryption = self.adls_account_client.accounts.begin_create(
            resource_group.name,
            account_name_no_encryption,
            params_create_no_encryption,
        ).result()

        adls_account_no_encryption = self.adls_account_client.accounts.get(
            resource_group.name,
            account_name_no_encryption
        )

        # full validation of the create
        self.assertEqual(adls_account_no_encryption.name, account_name_no_encryption)
        self.assertEqual(azure.mgmt.datalake.store.models.DataLakeStoreAccountStatus.succeeded,
                         adls_account_no_encryption.provisioning_state)
        self.assertIsNotNone(adls_account_no_encryption.id)
        self.assertIn(account_name_no_encryption, adls_account_no_encryption.id)
        self.assertIn(account_name_no_encryption, adls_account_no_encryption.endpoint)
        self.assertEqual(location, adls_account_no_encryption.location)
        self.assertEqual('Microsoft.DataLakeStore/accounts', adls_account_no_encryption.type)
        self.assertEqual(azure.mgmt.datalake.store.models.EncryptionState.enabled,
                         adls_account_no_encryption.encryption_state)
        self.assertIsNone(adls_account_no_encryption.identity)
        self.assertEqual(adls_account_no_encryption.tags['tag1'], 'value1')

        # list all the accounts
        result_list = list(self.adls_account_client.accounts.list_by_resource_group(resource_group.name))
        self.assertGreater(len(result_list), 1)

        result_list = list(self.adls_account_client.accounts.list())
        self.assertGreater(len(result_list), 1)

        # update the tags
        adls_account = self.adls_account_client.accounts.begin_update(
            resource_group.name,
            account_name,
            azure.mgmt.datalake.store.models.UpdateDataLakeStoreAccountParameters(
                tags={
                    'tag2': 'value2'
                }
            )
        ).result()

        self.assertEqual(adls_account.tags['tag2'], 'value2')

        # confirm that 'locations.get_capability' is functional
        get_capability = self.adls_account_client.locations.get_capability(location.replace(" ", ""))
        self.assertIsNotNone(get_capability)

        # confirm that 'operations.list' is functional
        operations_list = self.adls_account_client.operations.list()
        self.assertIsNotNone(operations_list)

        self.adls_account_client.accounts.begin_delete(
            resource_group.name,
            account_name
        ).wait()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
