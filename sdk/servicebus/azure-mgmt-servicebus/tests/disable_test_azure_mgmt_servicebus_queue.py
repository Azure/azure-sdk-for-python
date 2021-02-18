# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time

import azure.mgmt.servicebus.models
from azure.mgmt.servicebus.models import SBNamespace,SBSku,SkuName,SBQueue,SBAuthorizationRule,AccessRights,AccessKeys
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer


class MgmtServiceBusTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServiceBusTest, self).setUp()

        self.servicebus_client = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient
        )

    @RandomNameResourceGroupPreparer()
    def test_sb_queue_curd(self, resource_group, location):
        # List all topic types
        resource_group_name = resource_group.name

        # Create a Namespace
        namespace_name = self.get_replayable_random_resource_name("testingpythontestcasequeue")

        namespaceparameter = SBNamespace(location=location, tags={'tag1': 'value1', 'tag2': 'value2'}, sku=SBSku(name=SkuName.standard))
        creatednamespace = self.servicebus_client.namespaces.create_or_update(resource_group_name, namespace_name, namespaceparameter).result()
        self.assertEqual(creatednamespace.name, namespace_name)

        while (self.servicebus_client.namespaces.get(resource_group_name, namespace_name).provisioning_state != 'Succeeded'):
            if self.is_live:
                time.sleep(15)
            continue

        # Create a Queue
        queue_name = self.get_replayable_random_resource_name("testingpythonsdkqueue")
        createqueueresponse = self.servicebus_client.queues.create_or_update(resource_group_name, namespace_name,queue_name,SBQueue())
        self.assertEqual(createqueueresponse.name, queue_name)

        # Get the created Queue
        getqueueresponse = self.servicebus_client.queues.get(resource_group_name, namespace_name,queue_name)
        self.assertEqual(getqueueresponse.name, queue_name)

        # Get all the queues
        listbynamespacequeueresponse = list(self.servicebus_client.queues.list_by_namespace(resource_group_name, namespace_name))
        self.assertEqual(len(listbynamespacequeueresponse),1)
        self.assertEqual(listbynamespacequeueresponse[0].name, queue_name)

        # update queue
        updatequeueresponse = self.servicebus_client.queues.create_or_update(resource_group_name, namespace_name, queue_name, SBQueue(enable_express=True, max_delivery_count=5, max_size_in_megabytes=1024 ))
        self.assertEqual(updatequeueresponse.name, queue_name)
        self.assertEqual(updatequeueresponse.max_delivery_count, 5)
        self.assertEqual(updatequeueresponse.max_size_in_megabytes, 1024)
        self.assertEqual(updatequeueresponse.enable_express, True)

        # Create a new authorizationrule
        authoRule_name = self.get_replayable_random_resource_name("testingauthrulepy")
        createqueueauthorule = self.servicebus_client.queues.create_or_update_authorization_rule(resource_group_name, namespace_name, queue_name, authoRule_name, [AccessRights('Send'), AccessRights('Listen')])
        self.assertEqual(createqueueauthorule.name, authoRule_name,"Authorization rule name not as created - create_or_update_authorization_rule ")
        self.assertEqual(len(createqueueauthorule.rights), 2)

        # Get the created authorizationrule
        getqueueauthorule = self.servicebus_client.queues.get_authorization_rule(resource_group_name, namespace_name, queue_name, authoRule_name)
        self.assertEqual(getqueueauthorule.name, authoRule_name, "Authorization rule name not as passed as parameter - get_authorization_rule")
        self.assertEqual(len(getqueueauthorule.rights), 2, "Access rights mis match as created  - get_authorization_rule ")

        # update the rights of the authorizatiorule
        getqueueauthorule.rights.append('Manage')
        updatequeueauthorule = self.servicebus_client.queues.create_or_update_authorization_rule(resource_group_name, namespace_name, queue_name, authoRule_name, getqueueauthorule.rights)
        self.assertEqual(updatequeueauthorule.name, authoRule_name,"Authorization rule name not as passed as parameter for update call - create_or_update_authorization_rule ")
        self.assertEqual(len(updatequeueauthorule.rights), 3,"Access rights mis match as updated  - create_or_update_authorization_rule ")

        # list all the authorization ruels for the given Queue
        listqueueauthorule = list(self.servicebus_client.queues.list_authorization_rules(resource_group_name, namespace_name, queue_name))
        self.assertEqual(len(listqueueauthorule), 1,"number of authorization rule mismatch, created = 1 - list_authorization_rules")

        # List keys for the authorization rule
        listkeysauthorizationrule = self.servicebus_client.queues.list_keys(resource_group_name, namespace_name, queue_name, authoRule_name)
        self.assertIsNotNone(listkeysauthorizationrule)

        # regenerate Keys for authorizationrule - Primary
        regenratePrimarykeyauthorizationrule = self.servicebus_client.queues.regenerate_keys(resource_group_name,namespace_name, queue_name, authoRule_name,'PrimaryKey')
        self.assertNotEqual(listkeysauthorizationrule.primary_key, regenratePrimarykeyauthorizationrule.primary_key)

        # regenerate Keys for authorizationrule - Primary
        regenrateSecondarykeyauthorizationrule = self.servicebus_client.queues.regenerate_keys(resource_group_name,namespace_name, queue_name, authoRule_name,'SecondaryKey')
        self.assertNotEqual(listkeysauthorizationrule.secondary_key, regenrateSecondarykeyauthorizationrule.secondary_key)

        # delete the authorizationrule
        self.servicebus_client.queues.delete_authorization_rule(resource_group_name, namespace_name, queue_name, authoRule_name)

        # list all the authorization ruels for the given Queue
        listqueueauthorule = list(self.servicebus_client.queues.list_authorization_rules(resource_group_name, namespace_name, queue_name))
        lenTemp = len(listqueueauthorule)

        # delete the Queue
        self.servicebus_client.queues.delete(resource_group_name, namespace_name, queue_name)

        # Delete the create namespace
        deletenamespace = self.servicebus_client.namespaces.delete(resource_group_name, namespace_name).result()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()