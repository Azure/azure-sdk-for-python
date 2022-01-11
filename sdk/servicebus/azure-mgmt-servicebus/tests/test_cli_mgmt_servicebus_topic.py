# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   Topics: 10/10
#   Subscriptions: 4/4
#   Rules: 4/4

import unittest

import azure.mgmt.servicebus
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtServiceBus(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_subscrpition_and_rule(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        NAMESPACE_NAME = "myNamespacexxyyzzxyye"
        TOPIC_NAME = "myTopic"
        SUBSCRIPTION_NAME = "mySubscription"
        RULE_NAME = "myRule"

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
        # /Topics/put/TopicCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "enable_express": True
        }
        result = self.mgmt_client.topics.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Subscriptions/put/SubscriptionCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "enable_batched_operations": True
        }
        result = self.mgmt_client.subscriptions.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Rules/put/RulesCreateOrUpdate[put]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.rules.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME, rule_name=RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Subscriptions/get/SubscriptionGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscriptions.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME)

#--------------------------------------------------------------------------
        # /Rules/get/RulesGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.rules.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME, rule_name=RULE_NAME)

#--------------------------------------------------------------------------
        # /Subscriptions/get/SubscriptionListByTopic[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscriptions.list_by_topic(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Rules/get/RulesListBySubscriptions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.rules.list_by_subscriptions(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME)

#--------------------------------------------------------------------------
        # /Rules/delete/RulesDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.rules.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME,rule_name=RULE_NAME)

#--------------------------------------------------------------------------
        # /Subscriptions/delete/SubscriptionDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscriptions.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME)

#--------------------------------------------------------------------------
        # /Topics/delete/TopicDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_topic(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        NAMESPACE_NAME = "myNamespacexxyyzzxyyf"
        AUTHORIZATION_RULE_NAME = "myAuthorizationRule"
        TOPIC_NAME = "myTopic"

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
        # /Topics/put/TopicCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "enable_express": True
        }
        result = self.mgmt_client.topics.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, parameters=BODY)

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
        # /Topics/get/TopicAuthorizationRuleGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.get_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Topics/get/TopicAuthorizationRuleListAll[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.list_authorization_rules(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Topics/get/TopicGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.list_by_namespace(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Topics/get/TopicGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.list_by_namespace(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Topics/post/TopicAuthorizationRuleRegenerateKey[post]
#--------------------------------------------------------------------------
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.mgmt_client.topics.regenerate_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Topics/post/TopicAuthorizationRuleListKey[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.list_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Topics/delete/TopicAuthorizationRuleDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.delete_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Topics/delete/TopicDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.topics.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, topic_name=TOPIC_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)
        result = result.result()
