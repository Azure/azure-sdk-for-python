# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time

import azure.mgmt.relay.models
from azure.mgmt.relay.models import RelayNamespace, Sku, Relaytype, AuthorizationRule, AccessRights, AccessKeys, WcfRelay, ErrorResponse
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtWcfRelayTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtWcfRelayTest, self).setUp()

        self.relay_client = self.create_mgmt_client(
            azure.mgmt.relay.RelayAPI
        )

    @ResourceGroupPreparer()
    def test_wcfrelay_curd(self, resource_group, location):

        resource_group_name = resource_group.name

        #Create a Namespace
        namespace_name = "testingpythontestcaseeventhubnamespaceEventhub"

        namespaceparameter = RelayNamespace(location=location, tags={'tag1': 'value1', 'tag2': 'value2'}, sku=Sku(tier="standard"))
        creatednamespace = self.relay_client.namespaces.begin_create_or_update(resource_group_name, namespace_name, namespaceparameter).result()
        self.assertEqual(creatednamespace.name, namespace_name)

        #
        # # Get created Namespace
        #
        getnamespaceresponse = self.relay_client.namespaces.get(resource_group_name, namespace_name)
        self.assertEqual(getnamespaceresponse.name, namespace_name)

        # Create a WcfRelay
        wcfrelay_name = "testingpythontestcasewcfrelay"
        wcfrelayparameter = WcfRelay(
            relay_type=Relaytype.net_tcp,
            requires_client_authorization=True,
            requires_transport_security=True,
            user_metadata="User data for WcfRelay"
            )

        createdwcfrelayresponse = self.relay_client.wcf_relays.create_or_update(resource_group_name, namespace_name, wcfrelay_name, wcfrelayparameter)

        self.assertEqual(createdwcfrelayresponse.name, wcfrelay_name)
        self.assertEqual(createdwcfrelayresponse.requires_client_authorization, True)

        #Get the created wcfRelay
        geteventhubresponse = self.relay_client.wcf_relays.get(resource_group_name, namespace_name, wcfrelay_name)
        self.assertEqual(geteventhubresponse.name, wcfrelay_name)
        self.assertEqual(geteventhubresponse.requires_transport_security, True)
        self.assertEqual(geteventhubresponse.user_metadata, "User data for WcfRelay")

        #Get the List of wcfRealy by namespaces
        getlistbynamespacewcfrelayresponse = list(self.relay_client.wcf_relays.list_by_namespace(resource_group_name, namespace_name))
        self.assertGreater(len(getlistbynamespacewcfrelayresponse), 0)

        # update the Created eventhub
        wcfrelayupdateparameter = WcfRelay(
            relay_type=Relaytype.net_tcp,
            user_metadata="User data for WcfRelay updated"
        )
        updatewcfrelayresponse = self.relay_client.wcf_relays.create_or_update(
            resource_group_name,
            namespace_name,
            wcfrelay_name,
            wcfrelayupdateparameter
        )
        self.assertEqual(updatewcfrelayresponse.name, wcfrelay_name)
        self.assertEqual(updatewcfrelayresponse.requires_transport_security, True)
        self.assertEqual(updatewcfrelayresponse.requires_client_authorization, True)
        self.assertEqual(updatewcfrelayresponse.user_metadata, "User data for WcfRelay updated")

        # Create a new authorizationrule
        authoRule_name = "testingauthrulepy"
        createwcfrelayauthorule = self.relay_client.wcf_relays.create_or_update_authorization_rule(resource_group_name, namespace_name, wcfrelay_name, authoRule_name, {
            "rights": [AccessRights('Send'),AccessRights('Listen')]
        })
        self.assertEqual(createwcfrelayauthorule.name, authoRule_name, "Authorization rule name not as created - create_or_update_authorization_rule ")
        self.assertEqual(len(createwcfrelayauthorule.rights), 2)

        # Get the created authorizationrule
        getwcfrelayauthorule = self.relay_client.wcf_relays.get_authorization_rule(resource_group_name, namespace_name, wcfrelay_name, authoRule_name)
        self.assertEqual(getwcfrelayauthorule.name, authoRule_name, "Authorization rule name not as passed as parameter - get_authorization_rule ")
        self.assertEqual(len(getwcfrelayauthorule.rights), 2, "Access rights mis match as created  - get_authorization_rule ")

        # update the rights of the authorizatiorule
        getwcfrelayauthorule.rights.append('Manage')
        updatewcfrelayauthorule = self.relay_client.wcf_relays.create_or_update_authorization_rule(resource_group_name, namespace_name, wcfrelay_name, authoRule_name, getwcfrelayauthorule)
        self.assertEqual(updatewcfrelayauthorule.name, authoRule_name, "Authorization rule name not as passed as parameter for update call - create_or_update_authorization_rule ")
        self.assertEqual(len(updatewcfrelayauthorule.rights), 3, "Access rights mis match as updated  - create_or_update_authorization_rule ")

        #list all the authorization ruels for the given namespace
        wcfrelayauthorulelist = list(self.relay_client.wcf_relays.list_authorization_rules(resource_group_name, namespace_name, wcfrelay_name))
        self.assertEqual(len(wcfrelayauthorulelist), 1, "number of authorization rule mismatch with the created + default = 2 - list_authorization_rules")

        #List keys for the authorization rule
        listkeysauthorizationrule = self.relay_client.wcf_relays.list_keys(resource_group_name, namespace_name, wcfrelay_name, authoRule_name)
        self.assertIsNotNone(listkeysauthorizationrule)

        # regenerate Keys for authorizationrule - Primary
        regenratePrimarykeyauthorizationrule = self.relay_client.wcf_relays.regenerate_keys(resource_group_name, namespace_name, wcfrelay_name, authoRule_name, {
            "key_type": 'PrimaryKey'
        })
        self.assertNotEqual(listkeysauthorizationrule.primary_key,regenratePrimarykeyauthorizationrule.primary_key)

        # regenerate Keys for authorizationrule - Primary
        regenrateSecondarykeyauthorizationrule = self.relay_client.wcf_relays.regenerate_keys(resource_group_name,namespace_name, wcfrelay_name, authoRule_name, {
            "key_type": 'SecondaryKey'
        })
        self.assertNotEqual(listkeysauthorizationrule.secondary_key, regenrateSecondarykeyauthorizationrule.secondary_key)

        # delete the authorizationrule
        self.relay_client.wcf_relays.delete_authorization_rule(resource_group_name, namespace_name, wcfrelay_name, authoRule_name)

        # Delete the created WcfRelay
        getwcfrelayresponse = self.relay_client.wcf_relays.delete(resource_group_name, namespace_name, wcfrelay_name)

        # Delete the create namespace
        self.relay_client.namespaces.begin_delete(resource_group_name, namespace_name).result()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
