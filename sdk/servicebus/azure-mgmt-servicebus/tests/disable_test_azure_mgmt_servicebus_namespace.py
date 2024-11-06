# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import azure.mgmt.servicebus.models
from azure.mgmt.servicebus.models import SBNamespace, SBSku, SkuName, SBAuthorizationRule, AccessRights, AccessKeys
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer


class MgmtServiceBusTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServiceBusTest, self).setUp()

        self.servicebus_client = self.create_mgmt_client(azure.mgmt.servicebus.ServiceBusManagementClient)

    @RandomNameResourceGroupPreparer()
    def test_sb_namespace_curd(self, resource_group, location):
        # List all topic types
        resource_group_name = resource_group.name  # "ardsouza-resourcemovetest-group2"

        # Create a Namespace
        namespace_name = self.get_replayable_random_resource_name("testingpythontestcasenamespace")

        namespaceparameter = SBNamespace(
            location=location, tags={"tag1": "value1", "tag2": "value2"}, sku=SBSku(name=SkuName.standard)
        )
        creatednamespace = self.servicebus_client.namespaces.create_or_update(
            resource_group_name, namespace_name, namespaceparameter
        ).result()
        self.assertEqual(creatednamespace.name, namespace_name)
        #
        # # Get created Namespace
        #
        getnamespaceresponse = self.servicebus_client.namespaces.get(resource_group_name, namespace_name)
        self.assertEqual(getnamespaceresponse.name, namespace_name)

        # Get the List of Namespaces under the resourceGroup - list_by_resource_group

        listbyresourcegroupresponse = list(
            self.servicebus_client.namespaces.list_by_resource_group(resource_group_name)
        )
        self.assertGreater(len(listbyresourcegroupresponse), 0, "No Namespace returned, List is empty")
        self.assertEqual(
            listbyresourcegroupresponse[0].name, namespace_name, "Created namespace not found - ListByResourgroup"
        )

        # Get the List of namespace under the subscription  - list
        listbysubscriptionresponse = list(self.servicebus_client.namespaces.list())
        self.assertGreater(len(listbysubscriptionresponse), 0, "No Namespace returned, List is empty")

        # get the default authorizationrule
        defaultauthorule_name = self.get_replayable_random_resource_name("RootManageSharedAccessKey")
        defaultamespaceauthorule = self.servicebus_client.namespaces.get_authorization_rule(
            resource_group_name, namespace_name, defaultauthorule_name
        )
        self.assertEqual(
            defaultamespaceauthorule.name,
            defaultauthorule_name,
            "Default Authorization rule not returned - RootManageSharedAccessKey",
        )
        self.assertEqual(
            len(defaultamespaceauthorule.rights), 3, "rights for deafult not as required - send, listen and manage "
        )

        # Create a new authorizationrule
        authoRule_name = self.get_replayable_random_resource_name("testingauthrulepy")
        createnamespaceauthorule = self.servicebus_client.namespaces.create_or_update_authorization_rule(
            resource_group_name, namespace_name, authoRule_name, [AccessRights("Send"), AccessRights("Listen")]
        )
        self.assertEqual(
            createnamespaceauthorule.name,
            authoRule_name,
            "Authorization rule name not as created - create_or_update_authorization_rule ",
        )
        self.assertEqual(len(createnamespaceauthorule.rights), 2)

        # Get the created authorizationrule
        getnamespaceauthorule = self.servicebus_client.namespaces.get_authorization_rule(
            resource_group_name, namespace_name, authoRule_name
        )
        self.assertEqual(
            getnamespaceauthorule.name,
            authoRule_name,
            "Authorization rule name not as passed as parameter - get_authorization_rule ",
        )
        self.assertEqual(
            len(getnamespaceauthorule.rights), 2, "Access rights mis match as created  - get_authorization_rule "
        )

        # update the rights of the authorizatiorule
        getnamespaceauthorule.rights.append("Manage")
        updatenamespaceauthorule = self.servicebus_client.namespaces.create_or_update_authorization_rule(
            resource_group_name, namespace_name, authoRule_name, getnamespaceauthorule.rights
        )
        self.assertEqual(
            updatenamespaceauthorule.name,
            authoRule_name,
            "Authorization rule name not as passed as parameter for update call - create_or_update_authorization_rule ",
        )
        self.assertEqual(
            len(updatenamespaceauthorule.rights),
            3,
            "Access rights mis match as updated  - create_or_update_authorization_rule ",
        )

        # list all the authorization ruels for the given namespace
        createnamespaceauthorule = list(
            self.servicebus_client.namespaces.list_authorization_rules(resource_group_name, namespace_name)
        )
        self.assertEqual(
            len(createnamespaceauthorule),
            2,
            "number of authorization rule mismatch with the created + default = 2 - list_authorization_rules",
        )

        # List keys for the authorization rule
        listkeysauthorizationrule = self.servicebus_client.namespaces.list_keys(
            resource_group_name, namespace_name, authoRule_name
        )
        self.assertIsNotNone(listkeysauthorizationrule)

        # regenerate Keys for authorizationrule - Primary
        regenratePrimarykeyauthorizationrule = self.servicebus_client.namespaces.regenerate_keys(
            resource_group_name, namespace_name, authoRule_name, "PrimaryKey"
        )
        self.assertNotEqual(listkeysauthorizationrule.primary_key, regenratePrimarykeyauthorizationrule.primary_key)

        # regenerate Keys for authorizationrule - Primary
        regenrateSecondarykeyauthorizationrule = self.servicebus_client.namespaces.regenerate_keys(
            resource_group_name, namespace_name, authoRule_name, "SecondaryKey"
        )
        self.assertNotEqual(
            listkeysauthorizationrule.secondary_key, regenrateSecondarykeyauthorizationrule.secondary_key
        )

        # delete the authorizationrule
        self.servicebus_client.namespaces.delete_authorization_rule(resource_group_name, namespace_name, authoRule_name)

        # list all the authorization ruels for the given namespace
        createnamespaceauthorule = list(
            self.servicebus_client.namespaces.list_authorization_rules(resource_group_name, namespace_name)
        )
        self.assertEqual(len(createnamespaceauthorule), 1)
        self.assertEqual(createnamespaceauthorule[0].name, defaultauthorule_name)

        # Delete the create namespace
        deletenamespace = self.servicebus_client.namespaces.delete(resource_group_name, namespace_name).result()


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
