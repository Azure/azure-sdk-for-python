# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time

from msrestazure.azure_exceptions import CloudError
import azure.mgmt.eventhub.models
from azure.mgmt.eventhub.models import EHNamespace
from azure.mgmt.eventhub.models import EHNamespace, Sku, SkuName, AuthorizationRule, AccessRights, AccessKeys, ErrorResponseException, ErrorResponse
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtEventHubTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtEventHubTest, self).setUp()

        self.eventhub_client = self.create_mgmt_client(
            azure.mgmt.eventhub.EventHubManagementClient
        )

    @ResourceGroupPreparer()
    def test_eh_namespace_curd(self, resource_group, location):

        resource_group_name = resource_group.name

        # Create a Namespace
        namespace_name = "pythontestcasenamespace"

        namespaceparameter=EHNamespace(location=location, tags={'tag1' : 'value1', 'tag2' : 'value2'}, sku=Sku(name=SkuName.standard))
        poller = self.eventhub_client.namespaces.create_or_update(resource_group_name, namespace_name, namespaceparameter)
        creatednamespace = poller.result()
        self.assertEqual(creatednamespace.name, namespace_name)
        #
        # # Get created Namespace
        #
        getnamespaceresponse = self.eventhub_client.namespaces.get(resource_group_name, namespace_name)
        self.assertEqual(getnamespaceresponse.name, namespace_name)

        # Get the List of Namespaces under the resourceGroup - list_by_resource_group

        listbyresourcegroupresponse = list(self.eventhub_client.namespaces.list_by_resource_group(resource_group_name, False, False))
        self.assertGreater(len(listbyresourcegroupresponse), 0, "No Namespace returned, List is empty")
        self.assertEqual(listbyresourcegroupresponse[0].name, namespace_name, "Created namespace not found - ListByResourgroup")

        # Get the List of namespace under the subscription  - list
        listbysubscriptionresponse = list(self.eventhub_client.namespaces.list())
        self.assertGreater(len(listbysubscriptionresponse), 0, "No Namespace returned, List is empty")

        # get the default authorizationrule
        defaultauthorule_name = "RootManageSharedAccessKey"
        defaultamespaceauthorule = self.eventhub_client.namespaces.get_authorization_rule(resource_group_name, namespace_name, defaultauthorule_name)
        self.assertEqual(defaultamespaceauthorule.name, defaultauthorule_name, "Default Authorization rule not returned - RootManageSharedAccessKey")
        self.assertEqual(len(defaultamespaceauthorule.rights), 3, "rights for deafult not as required - send, listen and manage ")

        # Create a new authorizationrule
        authoRule_name = "testingauthrulepy"
        createnamespaceauthorule = self.eventhub_client.namespaces.create_or_update_authorization_rule(resource_group_name,namespace_name,authoRule_name,[AccessRights('Send'),AccessRights('Listen')])
        self.assertEqual(createnamespaceauthorule.name,authoRule_name, "Authorization rule name not as created - create_or_update_authorization_rule ")
        self.assertEqual(len(createnamespaceauthorule.rights),2)

        # Get the created authorizationrule
        getnamespaceauthorule = self.eventhub_client.namespaces.get_authorization_rule(resource_group_name, namespace_name, authoRule_name)
        self.assertEqual(getnamespaceauthorule.name, authoRule_name, "Authorization rule name not as passed as parameter - get_authorization_rule ")
        self.assertEqual(len(getnamespaceauthorule.rights), 2, "Access rights mis match as created  - get_authorization_rule ")

        # update the rights of the authorizatiorule
        getnamespaceauthorule.rights.append('Manage')
        updatenamespaceauthorule = self.eventhub_client.namespaces.create_or_update_authorization_rule(resource_group_name, namespace_name, authoRule_name, getnamespaceauthorule.rights)
        self.assertEqual(updatenamespaceauthorule.name, authoRule_name, "Authorization rule name not as passed as parameter for update call - create_or_update_authorization_rule ")
        self.assertEqual(len(updatenamespaceauthorule.rights), 3, "Access rights mis match as updated  - create_or_update_authorization_rule ")

        #list all the authorization ruels for the given namespace
        createnamespaceauthorule = list(self.eventhub_client.namespaces.list_authorization_rules(resource_group_name, namespace_name))
        self.assertEqual(len(createnamespaceauthorule),2, "number of authorization rule mismatch with the created + default = 2 - list_authorization_rules")

        #List keys for the authorization rule
        listkeysauthorizationrule = self.eventhub_client.namespaces.list_keys(resource_group_name, namespace_name, authoRule_name)
        self.assertIsNotNone(listkeysauthorizationrule)

        # regenerate Keys for authorizationrule - Primary
        regenratePrimarykeyauthorizationrule = self.eventhub_client.namespaces.regenerate_keys(resource_group_name, namespace_name,authoRule_name,'PrimaryKey')
        self.assertNotEqual(listkeysauthorizationrule.primary_key,regenratePrimarykeyauthorizationrule.primary_key)

        # regenerate Keys for authorizationrule - Primary
        regenrateSecondarykeyauthorizationrule = self.eventhub_client.namespaces.regenerate_keys(resource_group_name,namespace_name,authoRule_name, 'SecondaryKey')
        self.assertNotEqual(listkeysauthorizationrule.secondary_key, regenrateSecondarykeyauthorizationrule.secondary_key)

        # delete the authorizationrule
        self.eventhub_client.namespaces.delete_authorization_rule(resource_group_name, namespace_name, authoRule_name)

        # list all the authorization ruels for the given namespace
        createnamespaceauthorule = list(self.eventhub_client.namespaces.list_authorization_rules(resource_group_name, namespace_name))
        self.assertEqual(len(createnamespaceauthorule), 1)
        self.assertEqual(createnamespaceauthorule[0].name, defaultauthorule_name)

        # Delete the create namespace
        try:
            deletenamespace = self.eventhub_client.namespaces.delete(resource_group_name, namespace_name).result()
        except CloudError as ErrorResponse:
            self.assertTrue("not found" in ErrorResponse.message)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()