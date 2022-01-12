# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time

import azure.mgmt.relay.models
from azure.mgmt.relay.models import RelayNamespace, Sku, AccessRights
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy


class TestMgmtHybridConnection(AzureMgmtRecordedTestCase):

    def setup_method(self, method):

        self.relay_client = self.create_mgmt_client(
            azure.mgmt.relay.RelayAPI
        )

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_hybridconnetion_curd(self, resource_group, location):

        resource_group_name = resource_group.name

        #Create a Namespace
        namespace_name = "testingpythontestcasenamespacehybridconnection"

        namespaceparameter = RelayNamespace(location=location, tags={'tag1': 'value1', 'tag2': 'value2'}, sku=Sku(tier="standard"))
        creatednamespace = self.relay_client.namespaces.begin_create_or_update(resource_group_name, namespace_name, namespaceparameter).result()
        assert creatednamespace.name == namespace_name

        #
        # # Get created Namespace
        #
        getnamespaceresponse = self.relay_client.namespaces.get(resource_group_name, namespace_name)
        assert getnamespaceresponse.name == namespace_name

        # Create a HybridConnection
        hybridconnection_name = "testingpythontestcasehybridconnection"

        createdhybridconnectionresponse = self.relay_client.hybrid_connections.create_or_update(resource_group_name, namespace_name, hybridconnection_name, {
            "requires_client_authorization": True,
            "user_metadata": "User data for HybridConnection"
        })

        assert createdhybridconnectionresponse.name == hybridconnection_name
        assert createdhybridconnectionresponse.requires_client_authorization == True

        #Get the created Hybridconnection
        gethybridconnectionresponse = self.relay_client.hybrid_connections.get(resource_group_name, namespace_name, hybridconnection_name)
        assert gethybridconnectionresponse.name == hybridconnection_name
        assert gethybridconnectionresponse.user_metadata == "User data for HybridConnection"

        #Get the List of Hybridconnection by namespaces
        getlistbynamespacehybridconnectionresponse = list(self.relay_client.hybrid_connections.list_by_namespace(resource_group_name, namespace_name))
        assert len(getlistbynamespacehybridconnectionresponse) > 0

        updatehybridconnectionresponse = self.relay_client.hybrid_connections.create_or_update(resource_group_name, namespace_name, hybridconnection_name, {
            "user_metadata": "User data for HybridConnection updated"
        })

        assert updatehybridconnectionresponse.name == hybridconnection_name
        assert updatehybridconnectionresponse.requires_client_authorization == True
        assert updatehybridconnectionresponse.user_metadata == "User data for HybridConnection updated"

        # Create a new authorizationrule
        authoRule_name = "testingauthrulepy"
        createhybridconnectionauthorule = self.relay_client.hybrid_connections.create_or_update_authorization_rule(resource_group_name, namespace_name, hybridconnection_name, authoRule_name,{
            "rights": [AccessRights('Send'),AccessRights('Listen')]
        })
        assert createhybridconnectionauthorule.name, authoRule_name == "Authorization rule name not as created - create_or_update_authorization_rule "
        assert len(createhybridconnectionauthorule.rights) == 2

        # Get the created authorizationrule
        gethybridconnectionauthorule = self.relay_client.hybrid_connections.get_authorization_rule(resource_group_name, namespace_name, hybridconnection_name, authoRule_name)
        assert gethybridconnectionauthorule.name, authoRule_name == "Authorization rule name not as passed as parameter - get_authorization_rule "
        assert len(gethybridconnectionauthorule.rights), 2 == "Access rights mis match as created  - get_authorization_rule "

        # update the rights of the authorizatiorule
        gethybridconnectionauthorule.rights.append('Manage')
        updatehybridconnectionauthorule = self.relay_client.hybrid_connections.create_or_update_authorization_rule(resource_group_name, namespace_name, hybridconnection_name, authoRule_name, gethybridconnectionauthorule)
        assert updatehybridconnectionauthorule.name, authoRule_name == "Authorization rule name not as passed as parameter for update call - create_or_update_authorization_rule "
        assert len(updatehybridconnectionauthorule.rights), 3 == "Access rights mis match as updated  - create_or_update_authorization_rule "

        #list all the authorization ruels for the given namespace
        hybridconnectionauthorulelist = list(self.relay_client.hybrid_connections.list_authorization_rules(resource_group_name, namespace_name, hybridconnection_name))
        assert len(hybridconnectionauthorulelist), 1 == "number of authorization rule mismatch with the created + default = 2 - list_authorization_rules"

        #List keys for the authorization rule
        listkeysauthorizationrule = self.relay_client.hybrid_connections.list_keys(resource_group_name, namespace_name, hybridconnection_name, authoRule_name)
        assert listkeysauthorizationrule is not None

        # regenerate Keys for authorizationrule - Primary
        regenratePrimarykeyauthorizationrule = self.relay_client.hybrid_connections.regenerate_keys(resource_group_name, namespace_name, hybridconnection_name, authoRule_name, {
            "key_type": 'PrimaryKey'
        })
        assert listkeysauthorizationrule.primary_key !=regenratePrimarykeyauthorizationrule.primary_key

        # regenerate Keys for authorizationrule - Primary
        regenrateSecondarykeyauthorizationrule = self.relay_client.hybrid_connections.regenerate_keys(resource_group_name,namespace_name, hybridconnection_name, authoRule_name, {
            "key_type": 'SecondaryKey'
        })
        assert listkeysauthorizationrule.secondary_key != regenrateSecondarykeyauthorizationrule.secondary_key

        # delete the authorizationrule
        self.relay_client.hybrid_connections.delete_authorization_rule(resource_group_name, namespace_name, hybridconnection_name, authoRule_name)

        # Delete the created HybridConnection
        gethybridconnectionresponse = self.relay_client.hybrid_connections.delete(resource_group_name, namespace_name, hybridconnection_name)

        # Delete the create namespace
        self.relay_client.namespaces.begin_delete(resource_group_name, namespace_name).result()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
