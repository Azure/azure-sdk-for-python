# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   Queues: 10/10

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
    def test_queue(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        RESOURCE_GROUP = resource_group.name
        NAMESPACE_NAME = "myNamespacexxyyzzybx"
        AUTHORIZATION_RULE_NAME = "myAuthorizationRule"
        QUEUE_NAME = "myQueue"

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
        # /Queues/put/QueueCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "enable_partitioning": True
        }
        result = self.mgmt_client.queues.create_or_update(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, parameters=BODY)

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
        # /Queues/get/QueueAuthorizationRuleGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.get_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Queues/get/QueueAuthorizationRuleListAll[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.list_authorization_rules(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME)

#--------------------------------------------------------------------------
        # /Queues/get/QueueGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.get(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME)

#--------------------------------------------------------------------------
        # /Queues/get/QueueListByNameSpace[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.list_by_namespace(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)

#--------------------------------------------------------------------------
        # /Queues/post/QueueAuthorizationRuleRegenerateKey[post]
#--------------------------------------------------------------------------
        BODY = {
          "key_type": "PrimaryKey"
        }
        result = self.mgmt_client.queues.regenerate_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Queues/post/QueueAuthorizationRuleListKey[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.list_keys(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Queues/delete/QueueAuthorizationRuleDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.delete_authorization_rule(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME, authorization_rule_name=AUTHORIZATION_RULE_NAME)

#--------------------------------------------------------------------------
        # /Queues/delete/QueueDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.queues.delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME, queue_name=QUEUE_NAME)

#--------------------------------------------------------------------------
        # /Namespaces/delete/NameSpaceDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.namespaces.begin_delete(resource_group_name=RESOURCE_GROUP, namespace_name=NAMESPACE_NAME)
        result = result.result()
