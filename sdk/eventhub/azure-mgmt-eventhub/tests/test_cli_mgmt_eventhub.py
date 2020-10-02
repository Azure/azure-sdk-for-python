# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 43
# Methods Covered : 43
# Examples Total  : 44
# Examples Tested : 44
# Coverage %      : 100
# ----------------------

# covered ops:
#   operations: 1/1
#   event_hubs: 10/10
#   namespaces: 17/17
#   regions: 1/1
#   disaster_recovery_configs: 10/10
#   consumer_groups: 4/4

import time
import unittest

import azure.core
import azure.mgmt.eventhub
# import azure.mgmt.network
# import azure.mgmt.network.models
# import azure.mgmt.storage
# import azure.mgmt.storage.models
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtEventHubTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtEventHubTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.eventhub.EventHubManagementClient
        )

        if self.is_live:
            from azure.mgmt.storage import StorageManagementClient
            self.storage_client = self.create_mgmt_client(
                StorageManagementClient
            )
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

    # TODO: use track 2 later
    def create_storage_account(self, group_name, location, storage_name):
        import azure.mgmt.storage
        import azure.mgmt.storage.models
        params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
            sku=azure.mgmt.storage.models.Sku(name=azure.mgmt.storage.models.SkuName.standard_lrs),
            kind=azure.mgmt.storage.models.Kind.storage,
            location=location
        )
        result_create = self.storage_client.storage_accounts.create(
            group_name,
            storage_name,
            params_create,
        )
        return result_create.result()

    # TODO: use track 2 later
    def create_virtual_network(self, group_name, location, network_name, subnet_name):
        import azure.mgmt.network
        import azure.mgmt.network.models
        params_create = azure.mgmt.network.models.VirtualNetwork(
            location=location,
            address_space=azure.mgmt.network.models.AddressSpace(
                address_prefixes=[
                    '10.0.0.0/16',
                ],
            ),
            subnets=[
                azure.mgmt.network.models.Subnet(
                    name=subnet_name,
                    address_prefix='10.0.0.0/24',
                ),
            ],
        )
        azure_operation_poller = self.network_client.virtual_networks.create_or_update(
            group_name,
            network_name,
            params_create,
        )
        result_create = azure_operation_poller.result()
        self.assertEqual(result_create.name, network_name)

        result_get = self.network_client.subnets.get(
            group_name,
            network_name,
            subnet_name,
        )
        self.assertEqual(result_get.name, subnet_name)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_eventhub(self, resource_group):

        SKU_NAME = "Basic"
        RESOURCE_GROUP = resource_group.name
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        SUBNET_NAME = self.get_resource_name("subnet")
        EVENTHUB_NAME = self.get_resource_name("eventhub")
        NAMESPACE_NAME = self.get_resource_name("namespace")
        CONSUMERGROUP_NAME = self.get_resource_name("consumergroup")
        STORAGE_ACCOUNT_NAME = self.get_resource_name("storageaccount")
        VIRTUAL_NETWORK_NAME = self.get_resource_name("virtualnetwork")
        NETWORK_RULE_SET_NAME = self.get_resource_name("networkruleset")
        AUTHORIZATION_RULE_NAME = self.get_resource_name("authorizationrule")

        if self.is_live:
            self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, STORAGE_ACCOUNT_NAME)
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

        # NamespaceCreate[put]
        BODY = {
          "sku": {
            "name": "Standard",
            "tier": "Standard"
          },
          "location": "South Central US",
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group.name, NAMESPACE_NAME, BODY)
        result = result.result()

        # GetNamespaceMessagingPlan[get]
        result = self.mgmt_client.namespaces.get_messaging_plan(resource_group.name, NAMESPACE_NAME)

        # EventHubCreate[put]
        BODY = {
          "message_retention_in_days": "4",
          "partition_count": "4",
          "status": "Active",
          "capture_description": {
            "enabled": True,
            "encoding": "Avro",
            "interval_in_seconds": "120",
            "size_limit_in_bytes": "10485763",
            "destination": {
              "name": "EventHubArchive.AzureBlockBlob",
              "storage_account_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
              "blob_container": "container",
              "archive_name_format": "{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}"
            }
          }
        }
        result = self.mgmt_client.event_hubs.create_or_update(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, BODY)

        # NameSpaceNetworkRuleSetCreate[put]
        BODY = {
          "default_action": "Deny",
          "virtual_network_rules": [
            {
              "subnet": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
              },
              "ignore_missing_vnet_service_endpoint": True
            }
          ],
          "ip_rules": [
            {
              "ip_mask": "1.1.1.1",
              "action": "Allow"
            }
          ]
        }
        result = self.mgmt_client.namespaces.create_or_update_network_rule_set(resource_group.name, NAMESPACE_NAME, BODY)

        # NameSpaceAuthorizationRuleCreate[put]
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.mgmt_client.namespaces.create_or_update_authorization_rule(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME, BODY)

        # ConsumerGroupCreate[put]
        BODY = {
          "user_metadata": "New consumergroup"
        }
        result = self.mgmt_client.consumer_groups.create_or_update(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, CONSUMERGROUP_NAME, BODY)

        # EventHubAuthorizationRuleCreate[put]
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.mgmt_client.event_hubs.create_or_update_authorization_rule(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME, BODY)

        # NameSpaceAuthorizationRuleGet[get] TODO: need check
        result = self.mgmt_client.namespaces.get_authorization_rule(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME)

        # EventHubAuthorizationRuleGet[get]
        result = self.mgmt_client.event_hubs.get_authorization_rule(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME)

        # ConsumerGroupGet[get]
        result = self.mgmt_client.consumer_groups.get(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, CONSUMERGROUP_NAME)

        # EventHubAuthorizationRuleListAll[get]
        result = self.mgmt_client.event_hubs.list_authorization_rules(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME)

        # ConsumerGroupsListAll[get]
        result = self.mgmt_client.consumer_groups.list_by_event_hub(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME)

        # NameSpaceNetworkRuleSetGet[get]
        result = self.mgmt_client.namespaces.get_network_rule_set(resource_group.name, NAMESPACE_NAME)

        # EventHubGet[get]
        result = self.mgmt_client.event_hubs.get(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME)

        # ListAuthorizationRules[get] #TODO: NEED CHECK
        result = self.mgmt_client.namespaces.list_authorization_rules(resource_group.name, NAMESPACE_NAME)

        # NameSpaceNetworkRuleSetList[get]
        result = self.mgmt_client.namespaces.list_network_rule_sets(resource_group.name, NAMESPACE_NAME)

        # EventHubsListAll[get]
        result = self.mgmt_client.event_hubs.list_by_namespace(resource_group.name, NAMESPACE_NAME)

        # NameSpaceGet[get]
        result = self.mgmt_client.namespaces.get(resource_group.name, NAMESPACE_NAME)

        # NamespaceListByResourceGroup[get]
        result = self.mgmt_client.namespaces.list_by_resource_group(resource_group.name)

        # RegionsListBySkuStandard[get]
        # result = self.mgmt_client.regions.list_by_sku(SKU_NAME)

        # RegionsListBySkuBasic[get]
        result = self.mgmt_client.regions.list_by_sku(SKU_NAME)

        # NamespacesListBySubscription[get]
        result = self.mgmt_client.namespaces.list()

        # EHOperations_List[get]
        result = self.mgmt_client.operations.list()

        # EventHubAuthorizationRuleRegenerateKey[post]
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.mgmt_client.event_hubs.regenerate_keys(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME, BODY)

        # EventHubAuthorizationRuleListKey[post]
        result = self.mgmt_client.event_hubs.list_keys(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME)

        # NameSpaceAuthorizationRuleRegenerateKey[post]
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.mgmt_client.namespaces.regenerate_keys(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME, BODY)

        # NameSpaceAuthorizationRuleListKey[post] TODO: need check
        result = self.mgmt_client.namespaces.list_keys(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME)

        # NamespacesUpdate[patch]
        BODY = {
          "location": "South Central US",
          "tags": {
            "tag3": "value3",
            "tag4": "value4"
          }
        }
        result = self.mgmt_client.namespaces.update(resource_group.name, NAMESPACE_NAME, BODY)

        # NamespacesCheckNameAvailability[post] TODO: need fix
        BODY = {
          "name": "sdk-DisasterRecovery-9474"
        }
        result = self.mgmt_client.namespaces.check_name_availability(BODY)

        # EventHubAuthorizationRuleDelete[delete]
        result = self.mgmt_client.event_hubs.delete_authorization_rule(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME)

        # ConsumerGroupDelete[delete]
        result = self.mgmt_client.consumer_groups.delete(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, CONSUMERGROUP_NAME)

        # NameSpaceAuthorizationRuleDelete[delete]
        result = self.mgmt_client.namespaces.delete_authorization_rule(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME)

        # EventHubDelete[delete]
        result = self.mgmt_client.event_hubs.delete(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME)

        # NameSpaceDelete[delete]
        result = self.mgmt_client.namespaces.begin_delete(resource_group.name, NAMESPACE_NAME)
        result = result.result()
   
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_disaster_recovery_configs(self, resource_group):
        RESOURCE_GROUP = resource_group.name
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        NAMESPACE_NAME = self.get_resource_name("namesp2test")
        NAMESPACE_NAME_2 = self.get_resource_name("namesptest")
        AUTHORIZATION_RULE_NAME = self.get_resource_name("authorizationrule")
        DISASTER_RECOVERY_CONFIG_NAME = self.get_resource_name("disasterdecoveryconfig")

        # NamespaceCreate[put]
        BODY = {
          "sku": {
            "name": "Standard",
            "tier": "Standard"
          },
          "location": "South Central US",
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group.name, NAMESPACE_NAME, BODY)
        primery_namespace = result.result()

        # Second namespace [put]
        BODY = {
          "sku": {
            "name": "Standard",
            "tier": "Standard"
          },
          "location": "NorthCentralUS",
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group.name, NAMESPACE_NAME_2, BODY)
        second_namespace = result.result()

        # NameSpaceAuthorizationRuleCreate[put]
        BODY = {
          "rights": [
            # "Listen",
            "Send"
          ]
        }
        result = self.mgmt_client.namespaces.create_or_update_authorization_rule(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME, BODY)

        # DRCCheckNameAvailability[post]
        BODY = {
          "name": "sdk-DisasterRecovery-9474"
        }
        result = self.mgmt_client.disaster_recovery_configs.check_name_availability(resource_group.name, NAMESPACE_NAME, BODY)

        # EHAliasCreate[put]
        BODY = {
          # "partner_namespace": NAMESPACE_NAME_2
          "partner_namespace": second_namespace.id
        }
        result = self.mgmt_client.disaster_recovery_configs.create_or_update(resource_group.name, NAMESPACE_NAME, DISASTER_RECOVERY_CONFIG_NAME, BODY)

        # EHAliasGet[get]
        result = self.mgmt_client.disaster_recovery_configs.get(resource_group.name, NAMESPACE_NAME, DISASTER_RECOVERY_CONFIG_NAME)
        while result.provisioning_state != "Succeeded":
            result = self.mgmt_client.disaster_recovery_configs.get(resource_group.name, NAMESPACE_NAME, DISASTER_RECOVERY_CONFIG_NAME)
            time.sleep(30)
        
        # GetNamespaceMessagingPlan[get]
        result = self.mgmt_client.namespaces.get_messaging_plan(resource_group.name, NAMESPACE_NAME)

        # ListAuthorizationRules[get]
        result = self.mgmt_client.disaster_recovery_configs.list_authorization_rules(resource_group.name, NAMESPACE_NAME, DISASTER_RECOVERY_CONFIG_NAME)

        # NameSpaceAuthorizationRuleGet[get]
        result = self.mgmt_client.disaster_recovery_configs.get_authorization_rule(resource_group.name, NAMESPACE_NAME, DISASTER_RECOVERY_CONFIG_NAME, AUTHORIZATION_RULE_NAME)

        # EHAliasList[get]
        result = self.mgmt_client.disaster_recovery_configs.list(resource_group.name, NAMESPACE_NAME)

        # NameSpaceAuthorizationRuleListKey[post]
        result = self.mgmt_client.disaster_recovery_configs.list_keys(resource_group.name, NAMESPACE_NAME, DISASTER_RECOVERY_CONFIG_NAME, AUTHORIZATION_RULE_NAME)

        # EHAliasBreakPairing[post]
        result = self.mgmt_client.disaster_recovery_configs.break_pairing(resource_group.name, NAMESPACE_NAME, DISASTER_RECOVERY_CONFIG_NAME)

        # EHAliasFailOver[post]
        result = self.mgmt_client.disaster_recovery_configs.fail_over(resource_group.name, NAMESPACE_NAME_2, DISASTER_RECOVERY_CONFIG_NAME)

        # EHAliasDelete[delete]
        while True:
            try:
                result = self.mgmt_client.disaster_recovery_configs.delete(resource_group.name, NAMESPACE_NAME_2, DISASTER_RECOVERY_CONFIG_NAME)
            except azure.core.exceptions.HttpResponseError:
                time.sleep(30)
            else:
                break


        

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
