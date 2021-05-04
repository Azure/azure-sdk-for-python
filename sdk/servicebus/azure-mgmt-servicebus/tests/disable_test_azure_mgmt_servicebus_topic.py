# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time

import azure.mgmt.servicebus.models
from azure.mgmt.servicebus.models import SBNamespace,SBSku,SkuName,SBTopic,SBAuthorizationRule,AccessRights,AccessKeys
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer


class MgmtServiceBusTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServiceBusTest, self).setUp()

        self.servicebus_client = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient
        )

    @RandomNameResourceGroupPreparer()
    def test_sb_topic_curd(self, resource_group, location):
        # List all topic types
        resource_group_name = resource_group.name  # "ardsouza-resourcemovetest-group2"

        # Create a Namespace
        namespace_name = self.get_replayable_random_resource_name("testingpythontestcasetopic")

        namespaceparameter = SBNamespace(location=location, tags={'tag1': 'value1', 'tag2': 'value2'}, sku=SBSku(name=SkuName.standard))
        creatednamespace = self.servicebus_client.namespaces.create_or_update(resource_group_name, namespace_name, namespaceparameter).result()
        self.assertEqual(creatednamespace.name, namespace_name)

        while (self.servicebus_client.namespaces.get(resource_group_name, namespace_name).provisioning_state != 'Succeeded'):
            if self.is_live:
                time.sleep(15)
            continue

        # Create a Topic
        topic_name = self.get_replayable_random_resource_name("testingpythonsdktopic")
        createtopicresponse = self.servicebus_client.topics.create_or_update(resource_group_name, namespace_name,topic_name,SBTopic())
        self.assertEqual(createtopicresponse.name, topic_name)

        # Get the created Topic
        gettopicresponse = self.servicebus_client.topics.get(resource_group_name, namespace_name,topic_name)
        self.assertEqual(gettopicresponse.name, topic_name)

        # Get all the topics
        listbynamespacetopicresponse = list(self.servicebus_client.topics.list_by_namespace(resource_group_name, namespace_name))
        self.assertEqual(len(listbynamespacetopicresponse),1)
        self.assertEqual(listbynamespacetopicresponse[0].name, topic_name)

        # update topic
        updatetopicresponse = self.servicebus_client.topics.create_or_update(resource_group_name, namespace_name, topic_name, SBTopic( enable_express=True, enable_batched_operations=True, max_size_in_megabytes=1024 ))
        self.assertEqual(updatetopicresponse.name, topic_name)
        self.assertEqual(updatetopicresponse.enable_batched_operations, True)
        self.assertEqual(updatetopicresponse.max_size_in_megabytes, 1024)
        self.assertEqual(updatetopicresponse.enable_express, True)

        # Create a new authorizationrule
        authoRule_name = self.get_replayable_random_resource_name("testingauthrulepy")
        createtopicauthorule = self.servicebus_client.topics.create_or_update_authorization_rule(resource_group_name, namespace_name, topic_name, authoRule_name, [AccessRights('Send'), AccessRights('Listen')])
        self.assertEqual(createtopicauthorule.name, authoRule_name,"Authorization rule name not as created - create_or_update_authorization_rule ")
        self.assertEqual(len(createtopicauthorule.rights), 2)

        # Get the created authorizationrule
        gettopicauthorule = self.servicebus_client.topics.get_authorization_rule(resource_group_name, namespace_name, topic_name, authoRule_name)
        self.assertEqual(gettopicauthorule.name, authoRule_name, "Authorization rule name not as passed as parameter - get_authorization_rule")
        self.assertEqual(len(gettopicauthorule.rights), 2, "Access rights mis match as created  - get_authorization_rule ")

        # update the rights of the authorizatiorule
        gettopicauthorule.rights.append('Manage')
        updatetopicauthorule = self.servicebus_client.topics.create_or_update_authorization_rule(resource_group_name, namespace_name, topic_name, authoRule_name, gettopicauthorule.rights)
        self.assertEqual(updatetopicauthorule.name, authoRule_name,"Authorization rule name not as passed as parameter for update call - create_or_update_authorization_rule ")
        self.assertEqual(len(updatetopicauthorule.rights), 3,"Access rights mis match as updated  - create_or_update_authorization_rule ")

        # list all the authorization ruels for the given Topic
        listtopicauthorule = list(self.servicebus_client.topics.list_authorization_rules(resource_group_name, namespace_name, topic_name))
        self.assertEqual(len(listtopicauthorule), 1,"number of authorization rule mismatch, created = 1 - list_authorization_rules")

        # List keys for the authorization rule
        listkeysauthorizationrule = self.servicebus_client.topics.list_keys(resource_group_name, namespace_name, topic_name, authoRule_name)
        self.assertIsNotNone(listkeysauthorizationrule)

        # regenerate Keys for authorizationrule - Primary
        regenratePrimarykeyauthorizationrule = self.servicebus_client.topics.regenerate_keys(resource_group_name,namespace_name, topic_name, authoRule_name,'PrimaryKey')
        self.assertNotEqual(listkeysauthorizationrule.primary_key, regenratePrimarykeyauthorizationrule.primary_key)

        # regenerate Keys for authorizationrule - Primary
        regenrateSecondarykeyauthorizationrule = self.servicebus_client.topics.regenerate_keys(resource_group_name,namespace_name, topic_name, authoRule_name,'SecondaryKey')
        self.assertNotEqual(listkeysauthorizationrule.secondary_key,regenrateSecondarykeyauthorizationrule.secondary_key)

        # delete the authorizationrule
        self.servicebus_client.topics.delete_authorization_rule(resource_group_name, namespace_name, topic_name, authoRule_name)

        # list all the authorization ruels for the given Topic
        listtopicauthorule = list(self.servicebus_client.topics.list_authorization_rules(resource_group_name, namespace_name, topic_name))
        lenTemp = len(listtopicauthorule)

        # delete the Topic
        self.servicebus_client.topics.delete(resource_group_name, namespace_name, topic_name)

        # Delete the create namespace
        deletenamespace = self.servicebus_client.namespaces.delete(resource_group_name, namespace_name).result()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()