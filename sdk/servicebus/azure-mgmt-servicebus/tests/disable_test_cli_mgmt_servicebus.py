# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 65
# Methods Covered : 65
# Examples Total  : 67
# Examples Tested : 67
# Coverage %      : 100
# ----------------------

# Current Operation Coverage:
#   Operations: 1/1
#   Namespaces: 17/17
#   DisasterRecoveryConfigs: 1/10
#   MigrationConfigs: 6/6
#   Queues: 10/10
#   Topics: 10/10
#   Subscriptions: 4/4
#   Rules: 4/4
#   Regions: 1/1
#   PremiumMessagingRegions: 1/1
#   EventHubs: 1/1

import unittest

import azure.mgmt.servicebus
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtServiceBusTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServiceBusTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient
        )
    

        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

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

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_servicebus(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        NAMESPACE_NAME = "myNamespacexxyyzzy"
        NAMESPACE_NAME_SECOND = "myNamespacexxyyzzysecond"
        AUTHORIZATION_RULE_NAME = "myAuthorizationRule"
        # NETWORK_RULE_SET_NAME = "myNetworkRuleSet"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mySubnet"
        DISASTER_RECOVERY_CONFIG_NAME = "myDisasterRecoveryConfig"
        ALIAS = "myAlias"
        # CONFIG_NAME = "myConfig"
        CONFIG_NAME = "$default"
        QUEUE_NAME = "myQueue"
        TOPIC_NAME = "myTopic"
        RULE_NAME = "myRule"
        SKU = "mySku"

        if self.is_live:
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/put/NameSpaceCreate[put]
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
        # /Namespaces/put/NameSpaceCreate[put] (Second Namespace)
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "Premium",
            "tier": "Premium"
          },
          "location": "South Central US",
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.namespaces.begin_create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME_SECOND, parameters=BODY)
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
        # /Topics/put/TopicCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "enable_express": True
        }
        result = self.mgmt_client.topics.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Queues/put/QueueCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "enable_partitioning": True
        }
        result = self.mgmt_client.queues.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/put/SBAliasCreate[put]
#--------------------------------------------------------------------------
        BODY = {
        #   "partner_namespace": "sdk-Namespace-37",
          "partner_namespace": second_namespace.id,
        #   "alternate_name": "alternameforAlias-Namespace-8860"
        }
        # result = self.mgmt_client.disaster_recovery_configs.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS, parameters=BODY)

#--------------------------------------------------------------------------
        # /MigrationConfigs/put/MigrationConfigurationsStartMigration[put]
#--------------------------------------------------------------------------
        BODY = {
        #   "target_namespace": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceBus/namespaces/" + NAMESPACE_NAME,
          "target_namespace": second_namespace.id,
          "post_migration_name": "sdk-PostMigration-5919"
        }
        # result = self.mgmt_client.migration_configs.begin_create_and_start_migration(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME, parameters=BODY)
        # result = result.result()

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
            },
            # {
            #   "subnet": {
            #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME
            #   },
            #   "ignore_missing_vnet_service_endpoint": False
            # },
            # {
            #   "subnet": {
            #     "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME
            #   },
            #   "ignore_missing_vnet_service_endpoint": False
            # }
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
        # /Subscriptions/put/SubscriptionCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "enable_batched_operations": True
        }
        result = self.mgmt_client.subscriptions.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Queues/put/QueueAuthorizationRuleCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.mgmt_client.queues.create_or_update_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Topics/put/TopicAuthorizationRuleCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.mgmt_client.topics.create_or_update_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Rules/put/RulesCreateCorrelationFilter[put]
#--------------------------------------------------------------------------
        BODY = {
          "filter_type": "CorrelationFilter",
          "correlation_filter": {
            "properties": {
              "topic_hint": "Crop"
            }
          }
        }
        result = self.mgmt_client.rules.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, rule_name=RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Rules/put/RulesCreateSqlFilter[put]
#--------------------------------------------------------------------------
        BODY = {
          "filter_type": "SqlFilter",
          "sql_filter": {
            "sql_expression": "myproperty=test"
          }
        }
        result = self.mgmt_client.rules.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, rule_name=RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Rules/put/RulesCreateOrUpdate[put]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.rules.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, rule_name=RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/get/DisasterRecoveryConfigsAuthorizationRuleGet[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.disaster_recovery_configs.get_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Rules/get/RulesGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.rules.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, rule_name=RULE_NAME)

#--------------------------------------------------------------------------
        # /Topics/get/TopicAuthorizationRuleGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.get_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Queues/get/QueueAuthorizationRuleGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.get_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Rules/get/RulesListBySubscriptions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.rules.list_by_subscriptions(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Subscriptions/get/SubscriptionGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscriptions.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Subscriptions/get/SubscriptionListByTopic[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscriptions.list_by_topic(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/get/NameSpaceAuthorizationRuleListAll[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.disaster_recovery_configs.list_authorization_rules(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceAuthorizationRuleGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.get_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceNetworkRuleSetGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.get_network_rule_set(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Topics/get/TopicAuthorizationRuleListAll[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.list_authorization_rules(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Queues/get/QueueAuthorizationRuleListAll[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.list_authorization_rules(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME)

#--------------------------------------------------------------------------
        # /MigrationConfigs/get/MigrationConfigurationsGet[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.migration_configs.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/get/SBAliasGet[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.disaster_recovery_configs.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/get/SBAliasList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.disaster_recovery_configs.list(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Queues/get/QueueGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME)

#--------------------------------------------------------------------------
        # /Topics/get/TopicGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.list_by_namespace(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /MigrationConfigs/get/MigrationConfigurationsList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.migration_configs.list(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceAuthorizationRuleListAll[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list_authorization_rules(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceNetworkRuleSetList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list_network_rule_sets(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /EventHubs/get/RulesCreateOrUpdate[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.event_hubs.list_by_namespace(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Topics/get/TopicGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.list_by_namespace(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Queues/get/QueueListByNameSpace[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.list_by_namespace(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceListByResourceGroup[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /PremiumMessagingRegions/get/PremiumMessagingRegionsList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.premium_messaging_regions.list()

#--------------------------------------------------------------------------
        # /Regions/get/RegionsListBySku[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.regions.list_by_sku(sku=SKU)

#--------------------------------------------------------------------------
        # /Namespaces/get/NameSpaceList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list()

#--------------------------------------------------------------------------
        # /Operations/get/OperationsList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.operations.list()

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/post/DisasterRecoveryConfigsAuthorizationRuleListKey[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.disaster_recovery_configs.list_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Topics/post/TopicAuthorizationRuleRegenerateKey[post]
#--------------------------------------------------------------------------
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.mgmt_client.topics.regenerate_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Queues/post/QueueAuthorizationRuleRegenerateKey[post]
#--------------------------------------------------------------------------
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.mgmt_client.queues.regenerate_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Topics/post/TopicAuthorizationRuleListKey[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.list_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Queues/post/QueueAuthorizationRuleListKey[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.list_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/post/NameSpaceAuthorizationRuleRegenerateKey[post]
#--------------------------------------------------------------------------
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.mgmt_client.namespaces.regenerate_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/post/AliasNameAvailability[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "sdk-DisasterRecovery-9474"
        }
        # result = self.mgmt_client.disaster_recovery_configs.check_name_availability_method(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, disaster_recovery_config_name=DISASTER_RECOVERY_CONFIG_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Namespaces/post/NameSpaceAuthorizationRuleListKey[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.list_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /MigrationConfigs/post/MigrationConfigurationsCompleteMigration[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.migration_configs.complete_migration(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)

#--------------------------------------------------------------------------
        # /MigrationConfigs/post/MigrationConfigurationsRevert[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.migration_configs.revert(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/post/SBEHAliasBreakPairing[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.disaster_recovery_configs.break_pairing(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/post/SBAliasFailOver[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.disaster_recovery_configs.fail_over(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)

#--------------------------------------------------------------------------
        # /Namespaces/post/NameSpaceUpdate[post]
#--------------------------------------------------------------------------
        BODY = {
          "target_namespace_type": "EventHub"
        }
        result = self.mgmt_client.namespaces.migrate(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, parameters=BODY)

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
        result = self.mgmt_client.namespaces.check_name_availability_method(parameters=BODY)

#--------------------------------------------------------------------------
        # /Rules/delete/RulesDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.rules.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, rule_name=RULE_NAME)

#--------------------------------------------------------------------------
        # /Queues/delete/QueueAuthorizationRuleDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.delete_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Topics/delete/TopicAuthorizationRuleDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.delete_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Subscriptions/delete/SubscriptionDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscriptions.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceAuthorizationRuleDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.delete_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /MigrationConfigs/delete/MigrationConfigurationsDelete[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.migration_configs.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, config_name=CONFIG_NAME)

#--------------------------------------------------------------------------
        # /DisasterRecoveryConfigs/delete/SBAliasDelete[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.disaster_recovery_configs.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, alias=ALIAS)

#--------------------------------------------------------------------------
        # /Topics/delete/TopicDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Queues/delete/QueueDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
