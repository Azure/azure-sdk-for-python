# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   Operations: 1/1
#   MigrationConfigs: 6/6
#   Namespaces: 17/17
#   EventHubs: 1/1
#   Regions: 1/1
#   PremiumMessagingRegions: 1/1
#   DisasterRecoveryConfigs: 10/10

import time
import unittest

import azure.mgmt.servicebus
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, ResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtServiceBus(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient
        )
        self.mgmt_client2017 = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient,
            api_version="2017-04-01"
        )
    
        # # No testcases to test
        # if self.is_live:
        #     from azure.mgmt.network import NetworkManagementClient
        #     self.network_client = self.create_mgmt_client(
        #         NetworkManagementClient
        #     )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):

        azure_operation_poller = self.network_client.virtual_networks.begin_create_or_update(
            group_name,
            network_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            },
        )
        result_create = azure_operation_poller.result()

        async_subnet_creation = self.network_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()

        return subnet_info
    
    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_namespace(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        NAMESPACE_NAME = "myNamespacexxyyzzxyx"
        AUTHORIZATION_RULE_NAME = "myAuthorizationRule"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mySubnet"
        SKU = "Premium"

        if self.is_live:
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "Premium",
            "tier": "Premium"
          },
          "location": AZURE_LOCATION,
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)
        namespace = result.result()

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceAuthorizationRuleCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.mgmt_client.namespaces.create_or_update_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceNetworkRuleSetCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "default_action": "Deny",
          "virtual_network_rules": [
            {
              "subnet": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME
              },
              "ignore_missing_vnet_service_endpoint": True
            }
          ],
          "ip_rules": [
            {
              "ip_mask": "1.1.1.1",
              "action": "Allow"
            },
            {
              "ip_mask": "1.1.1.2",
              "action": "Allow"
            },
            {
              "ip_mask": "1.1.1.3",
              "action": "Allow"
            },
            {
              "ip_mask": "1.1.1.4",
              "action": "Allow"
            },
            {
              "ip_mask": "1.1.1.5",
              "action": "Allow"
            }
          ]
        }
        result = self.mgmt_client.namespaces.create_or_update_network_rule_set(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceAuthorizationRuleGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.get_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceNetworkRuleSetGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.get_network_rule_set(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceAuthorizationRuleListAll[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list_authorization_rules(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceListByResourceGroup[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list()

#--------------------------------------------------------------------------
        # /Operations/get/OperationsList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.operations.list()

#--------------------------------------------------------------------------
        # /PremiumMessagingRegions/get/PremiumMessagingRegionsList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.premium_messaging_regions.list()

#--------------------------------------------------------------------------
        # /Regions/get/RegionsListBySku[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.regions.list_by_sku(sku=SKU)

#--------------------------------------------------------------------------
        # /EventHubs/get/RulesCreateOrUpdate[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.event_hubs.list_by_namespace(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/post/NameSpaceAuthorizationRuleRegenerateKey[post]
#--------------------------------------------------------------------------
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.mgmt_client.namespaces.regenerate_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Namespaces/post/NameSpaceAuthorizationRuleListKey[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/post/NameSpaceUpdate[post]
#--------------------------------------------------------------------------
        BODY = {
          "target_namespace_type": "EventHub"
        }
        # result = self.mgmt_client.namespaces.migrate(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Namespaces/patch/NameSpaceUpdate[patch]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "tag3": "value3",
            "tag4": "value4"
          }
        }
        result = self.mgmt_client.namespaces.update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Namespaces/post/NameSpaceCheckNameAvailability[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "sdk-Namespace-2924"
        }
        result = self.mgmt_client.namespaces.check_name_availability(parameters=BODY)

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceAuthorizationRuleDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.delete_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)
        try:
            result = result.result()
        except HttpResponseError as e:
            if not str(e).startswith("(ResourceNotFound)"):
                raise e
    
    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_migration_configs(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        RESOURCE_GROUP = resource_group.name
        NAMESPACE_NAME = "myNamespacexxyyzzxyyma"
        NAMESPACE_NAME_PRIMARY = "myNamespacexxyyzzykksecondm"
        AUTHORIZATION_RULE_NAME = "myAuthorizationRule"
        CONFIG_NAME = "$default"
        POST_MIGRATION_NAME = "postmigrationxxxky"

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceCreate[put] Standard
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "Standard",
            "tier": "Standard"
          },
          "location": AZURE_LOCATION,
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)
        namespace = result.result()

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceCreate[put] Primary
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "Premium",
            "tier": "Premium"
          },
          "location": "westus",
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME_PRIMARY, parameters=BODY)
        second_namespace = result.result()

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceAuthorizationRuleCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.mgmt_client.namespaces.create_or_update_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /MigrationConfigs/put/MigrationConfigurationsStartMigration[put]
#--------------------------------------------------------------------------
        BODY = {
          "target_namespace": second_namespace.id,
          "post_migration_name": POST_MIGRATION_NAME
        }
        result = self.mgmt_client.migration_configs.begin_create_and_start_migration(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /MigrationConfigs/get/MigrationConfigurationsList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.migration_configs.list(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/post/NameSpaceUpdate[post]
#--------------------------------------------------------------------------
        BODY = {
          "target_namespace_type": "EventHub"
        }
        result = self.mgmt_client.namespaces.migrate(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /MigrationConfigs/post/MigrationConfigurationsRevert[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.migration_configs.revert(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)

#--------------------------------------------------------------------------
        # /MigrationConfigs/post/MigrationConfigurationsCompleteMigration[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.migration_configs.complete_migration(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)

#--------------------------------------------------------------------------
        # /MigrationConfigs/get/MigrationConfigurationsGet[get]
#--------------------------------------------------------------------------
        migration = self.mgmt_client.migration_configs.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)
        if self.is_live:
            count = 0
            while migration.provisioning_state != "Succeeded":
                time.sleep(30)
                migration = self.mgmt_client.migration_configs.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)
                count += 1
                if count>10:
                    break

#--------------------------------------------------------------------------
        # /MigrationConfigs/delete/MigrationConfigurationsDelete[delete]
#--------------------------------------------------------------------------
        try:
            result = self.mgmt_client.migration_configs.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)
        except HttpResponseError as e:
            if not str(e).startswith("(NotFound)"):
                raise e

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete] Primary
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME_PRIMARY)
        try:
            result = result.result()
        except HttpResponseError as e:
            if not str(e).startswith("(ResourceNotFound)"):
                raise e

    @unittest.skip("unsupport.")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_disaster_recovery_configs(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        RESOURCE_GROUP = resource_group.name
        NAMESPACE_NAME = "myNamespacexxyyzzxyyab"
        NAMESPACE_NAME_PRIMARY = "myNamespacexxyyzzzyasecond"
        AUTHORIZATION_RULE_NAME = "myAuthorizationRule"
        ALIAS = "mydisasterrecovercf"

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "Premium",
            "tier": "Premium"
          },
          "location": AZURE_LOCATION,
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)
        namespace = result.result()

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceCreate[put] Primary
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "Premium",
            "tier": "Premium"
          },
          "location": "westus",
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME_PRIMARY, parameters=BODY)
        second_namespace = result.result()

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceAuthorizationRuleCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.mgmt_client.namespaces.create_or_update_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/post/AliasNameAvailability[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "sdk-DisasterRecovery-9474"
        }
        result = self.mgmt_client2017.disaster_recovery_configs.check_name_availability(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/put/SBAliasCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "partner_namespace": second_namespace.id,
        }
        result = self.mgmt_client2017.disaster_recovery_configs.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS, parameters=BODY)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/get/SBAliasGet[get]
#--------------------------------------------------------------------------
        dr_config = self.mgmt_client2017.disaster_recovery_configs.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)
        if self.is_live:
            count = 0
            while dr_config.provisioning_state != "Succeeded":
                time.sleep(30)
                dr_config = self.mgmt_client2017.disaster_recovery_configs.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)
                count += 1
                if count>10:
                    break

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/get/DisasterRecoveryConfigsAuthorizationRuleGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client2017.disaster_recovery_configs.get_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/get/NameSpaceAuthorizationRuleListAll[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client2017.disaster_recovery_configs.list_authorization_rules(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/get/SBAliasList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client2017.disaster_recovery_configs.list(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/post/DisasterRecoveryConfigsAuthorizationRuleListKey[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client2017.disaster_recovery_configs.list_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/post/SBEHAliasBreakPairing[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client2017.disaster_recovery_configs.break_pairing(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/post/SBAliasFailOver[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client2017.disaster_recovery_configs.fail_over(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME_PRIMARY, alias=ALIAS)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/delete/SBAliasDelete[delete]
#--------------------------------------------------------------------------
        count = 0
        while count<10:
            try:
                result = self.mgmt_client2017.disaster_recovery_configs.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)
            except HttpResponseError as e:
                time.sleep(30)
                count += 1

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete] Primary
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME_PRIMARY)
        try:
            result = result.result()
        except HttpResponseError as e:
            if not str(e).startswith("(ResourceNotFound)"):
                raise e
