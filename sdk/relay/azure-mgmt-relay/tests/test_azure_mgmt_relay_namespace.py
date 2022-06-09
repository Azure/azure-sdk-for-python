# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import azure.mgmt.relay
from azure.mgmt.relay.models import RelayNamespace, Sku, AccessRights

from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy


class TestMgmtRelayNamespace(AzureMgmtRecordedTestCase):

    def setup_method(self, method):

        self.relay_client = self.create_mgmt_client(
            azure.mgmt.relay.RelayAPI
        )

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_relay_namespace_curd(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")

        resource_group_name = resource_group.name

        # Create a Namespace
        namespace_name = "testingpythontestcasenamespace"
        namespaceparameter=RelayNamespace(location=location, tags={'tag1':'value1', 'tag2':'value2'}, sku=Sku(tier="standard"))
        creatednamespace = self.relay_client.namespaces.begin_create_or_update(resource_group_name, namespace_name, namespaceparameter).result()
        assert creatednamespace.name == namespace_name
        #
        # # Get created Namespace
        #
        getnamespaceresponse = self.relay_client.namespaces.get(resource_group_name, namespace_name)
        assert getnamespaceresponse.name == namespace_name

        # Update a Namespace
        namespaceparameter={'tags': {'tag1':'value1', 'tag2':'value2'}}
        updatenamespace = self.relay_client.namespaces.update(resource_group_name, namespace_name, namespaceparameter)

        # Get the List of Namespaces under the resourceGroup - list_by_resource_group
        listbyresourcegroupresponse = list(self.relay_client.namespaces.list_by_resource_group(resource_group_name))
        assert len(listbyresourcegroupresponse) > 0, "No Namespace returned > List is empty"
        assert listbyresourcegroupresponse[0].name == namespace_name, "Created namespace not found - ListByResourgroup"

        # Get the List of namespace under the subscription  - list
        listbysubscriptionresponse = list(self.relay_client.namespaces.list())
        assert len(listbysubscriptionresponse) > 0, "No Namespace returned > List is empty"
        # get the default authorizationrule
        defaultauthorule_name = "RootManageSharedAccessKey"
        defaultamespaceauthorule = self.relay_client.namespaces.get_authorization_rule(resource_group_name, namespace_name, defaultauthorule_name)
        assert defaultamespaceauthorule.name == defaultauthorule_name, "Default Authorization rule not returned - RootManageSharedAccessKey"
        assert len(defaultamespaceauthorule.rights) == 3, "rights for deafult not as required - send == listen and manage "

        # Create a new authorizationrule
        authoRule_name = "testingauthrulepy"
        createnamespaceauthorule = self.relay_client.namespaces.create_or_update_authorization_rule(resource_group_name,namespace_name,authoRule_name, {
            "rights": [AccessRights('Send'),AccessRights('Listen')]
        })
        assert createnamespaceauthorule.name,authoRule_name == "Authorization rule name not as created - create_or_update_authorization_rule "
        assert len(createnamespaceauthorule.rights) ==2

        # Get the created authorizationrule
        getnamespaceauthorule = self.relay_client.namespaces.get_authorization_rule(resource_group_name, namespace_name, authoRule_name)
        assert getnamespaceauthorule.name, authoRule_name == "Authorization rule name not as passed as parameter - get_authorization_rule "
        assert len(getnamespaceauthorule.rights), 2 == "Access rights mis match as created  - get_authorization_rule "

        # update the rights of the authorizatiorule
        getnamespaceauthorule.rights.append('Manage')
        updatenamespaceauthorule = self.relay_client.namespaces.create_or_update_authorization_rule(resource_group_name, namespace_name, authoRule_name, getnamespaceauthorule)
        assert updatenamespaceauthorule.name, authoRule_name == "Authorization rule name not as passed as parameter for update call - create_or_update_authorization_rule "
        assert len(updatenamespaceauthorule.rights), 3 == "Access rights mis match as updated  - create_or_update_authorization_rule "

        # list all the authorization ruels for the given namespace
        createnamespaceauthorule = list(self.relay_client.namespaces.list_authorization_rules(resource_group_name, namespace_name))
        assert len(createnamespaceauthorule),2 == "number of authorization rule mismatch with the created + default = 2 - list_authorization_rules"

        # List keys for the authorization rule
        listkeysauthorizationrule = self.relay_client.namespaces.list_keys(resource_group_name, namespace_name, authoRule_name)
        assert listkeysauthorizationrule is not None

        # regenerate Keys for authorizationrule - Primary
        regenratePrimarykeyauthorizationrule = self.relay_client.namespaces.regenerate_keys(resource_group_name, namespace_name,authoRule_name,{
            "key_type": 'PrimaryKey'
        })
        assert listkeysauthorizationrule.primary_key !=regenratePrimarykeyauthorizationrule.primary_key

        # regenerate Keys for authorizationrule - Primary
        regenrateSecondarykeyauthorizationrule = self.relay_client.namespaces.regenerate_keys(resource_group_name,namespace_name,authoRule_name, {
            "key_type": 'SecondaryKey'
        })
        assert listkeysauthorizationrule.secondary_key != regenrateSecondarykeyauthorizationrule.secondary_key

        # delete the authorizationrule
        self.relay_client.namespaces.delete_authorization_rule(resource_group_name, namespace_name, authoRule_name)

        # list all the authorization ruels for the given namespace
        createnamespaceauthorule = list(self.relay_client.namespaces.list_authorization_rules(resource_group_name, namespace_name))
        assert len(createnamespaceauthorule) == 1
        assert createnamespaceauthorule[0].name == defaultauthorule_name

        # Delete the create namespace
        deletenamespace = self.relay_client.namespaces.begin_delete(resource_group_name, namespace_name).result()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
