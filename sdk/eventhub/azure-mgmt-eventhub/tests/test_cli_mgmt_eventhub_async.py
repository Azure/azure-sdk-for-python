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
import azure.mgmt.eventhub.aio
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

from _aio_testcase import AzureMgmtAsyncTestCase 


AZURE_LOCATION = 'eastus'

class MgmtEventHubTest(AzureMgmtAsyncTestCase):

    def setUp(self):
        super(MgmtEventHubTest, self).setUp()
        self.mgmt_client = self.create_mgmt_aio_client(
            azure.mgmt.eventhub.aio.EventHubManagementClient
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

    @unittest.skip('skip temporarily')
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
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.begin_create_or_update(resource_group.name, NAMESPACE_NAME, BODY)
        )
        result = self.event_loop.run_until_complete(
            result.result()
        )

        # GetNamespaceMessagingPlan[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.get_messaging_plan(resource_group.name, NAMESPACE_NAME)
        )

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
        result = self.event_loop.run_until_complete(
            self.mgmt_client.event_hubs.create_or_update(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, BODY)
        )

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
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.create_or_update_network_rule_set(resource_group.name, NAMESPACE_NAME, BODY)
        )

        # NameSpaceAuthorizationRuleCreate[put]
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.create_or_update_authorization_rule(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME, BODY)
        )

        # ConsumerGroupCreate[put]
        BODY = {
          "user_metadata": "New consumergroup"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.consumer_groups.create_or_update(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, CONSUMERGROUP_NAME, BODY)
        )

        # EventHubAuthorizationRuleCreate[put]
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.event_hubs.create_or_update_authorization_rule(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME, BODY)
        )

        # NameSpaceAuthorizationRuleGet[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.get_authorization_rule(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME)
        )

        # EventHubAuthorizationRuleGet[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.event_hubs.get_authorization_rule(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME)
        )

        # ConsumerGroupGet[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.consumer_groups.get(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, CONSUMERGROUP_NAME)
        )

        # EventHubAuthorizationRuleListAll[get]
        result = self.to_list(
            self.mgmt_client.event_hubs.list_authorization_rules(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME)
        )

        # ConsumerGroupsListAll[get]
        result = self.to_list(
            self.mgmt_client.consumer_groups.list_by_event_hub(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME)
        )

        # NameSpaceNetworkRuleSetGet[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.get_network_rule_set(resource_group.name, NAMESPACE_NAME)
        )

        # EventHubGet[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.event_hubs.get(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME)
        )

        # ListAuthorizationRules[get]
        result = self.to_list(
            self.mgmt_client.namespaces.list_authorization_rules(resource_group.name, NAMESPACE_NAME)
        )

        # NameSpaceNetworkRuleSetList[get]
        result = self.to_list(
            self.mgmt_client.namespaces.list_network_rule_sets(resource_group.name, NAMESPACE_NAME)
        )

        # EventHubsListAll[get]
        result = self.to_list(
            self.mgmt_client.event_hubs.list_by_namespace(resource_group.name, NAMESPACE_NAME)
        )

        # NameSpaceGet[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.get(resource_group.name, NAMESPACE_NAME)
        )

        # NamespaceListByResourceGroup[get]
        result = self.to_list(
            self.mgmt_client.namespaces.list_by_resource_group(resource_group.name)
        )

        # RegionsListBySkuStandard[get]
        # result = self.mgmt_client.regions.list_by_sku(SKU_NAME)

        # RegionsListBySkuBasic[get]
        result = self.to_list(
            self.mgmt_client.regions.list_by_sku(SKU_NAME)
        )

        # NamespacesListBySubscription[get]
        result = self.to_list(
            self.mgmt_client.namespaces.list()
        )

        # EHOperations_List[get]
        result = self.to_list(
            self.mgmt_client.operations.list()
        )

        # EventHubAuthorizationRuleRegenerateKey[post]
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.event_hubs.regenerate_keys(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME, BODY)
        )

        # EventHubAuthorizationRuleListKey[post]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.event_hubs.list_keys(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME)
        )

        # NameSpaceAuthorizationRuleRegenerateKey[post]
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.regenerate_keys(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME, BODY)
        )

        # NameSpaceAuthorizationRuleListKey[post]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.list_keys(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME)
        )

        # NamespacesUpdate[patch]
        BODY = {
          "location": "South Central US",
          "tags": {
            "tag3": "value3",
            "tag4": "value4"
          }
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.update(resource_group.name, NAMESPACE_NAME, BODY)
        )

        # NamespacesCheckNameAvailability[post] TODO: need fix
        BODY = {
          "name": "sdk-DisasterRecovery-9474"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.check_name_availability(BODY)
        )

        # EventHubAuthorizationRuleDelete[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.event_hubs.delete_authorization_rule(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATION_RULE_NAME)
        )

        # ConsumerGroupDelete[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.consumer_groups.delete(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME, CONSUMERGROUP_NAME)
        )

        # NameSpaceAuthorizationRuleDelete[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.delete_authorization_rule(resource_group.name, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME)
        )

        # EventHubDelete[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.event_hubs.delete(resource_group.name, NAMESPACE_NAME, EVENTHUB_NAME)
        )

        # NameSpaceDelete[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.namespaces.begin_delete(resource_group.name, NAMESPACE_NAME)
        )
        result = self.event_loop.run_until_complete(
            result.result()
        )
   

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
