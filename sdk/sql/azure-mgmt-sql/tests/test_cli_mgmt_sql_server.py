# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   Servers: 7/7
#   ServerKeys: 0/4
#   ServerUsages: 1/1
#   FirewallRules: 4/4
#   ServerCommunicationLinks: 4/4
#   ServerBlobAuditingPolicies: 0/3
#   ExtendedServerBlobAuditingPolicies: 0/3
#   ServerDnsAliases: 5/5

import unittest

import azure.mgmt.sql
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSqlTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_dns_alias(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        DNS_ALIAS_NAME = "mydnsalias"
        DNS_ALIAS_NAME_2 = "mydnsalias2"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerDnsAliases/put/Create server DNS alias[put]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_dns_aliases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, dns_alias_name=DNS_ALIAS_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerDnsAliases/get/Get server DNS alias[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_dns_aliases.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, dns_alias_name=DNS_ALIAS_NAME)

#--------------------------------------------------------------------------
        # /ServerDnsAliases/get/List server DNS aliases[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_dns_aliases.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerDnsAliases/post/Acquire server DNS alias[post]
#--------------------------------------------------------------------------
        BODY = {
          "old_server_dns_alias_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/dnsAliases/" + DNS_ALIAS_NAME_2
        }
        result = self.mgmt_client.server_dns_aliases.begin_acquire(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, dns_alias_name=DNS_ALIAS_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerDnsAliases/delete/Delete server DNS alias[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_dns_aliases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, dns_alias_name=DNS_ALIAS_NAME_2)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_blob_auditing_policy(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        PARTNER_SERVER_NAME = "mypartnerserverxpxy"
        COMMUNICATION_LINK_NAME = "mycommunicationlink"
 
#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerBlobAuditingPolicies/put/Update a server's blob auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.server_blob_auditing_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ExtendedServerBlobAuditingPolicies/put/Update a server's extended blob auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.extended_server_blob_auditing_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ExtendedServerBlobAuditingPolicies/get/Get a server's blob extended auditing policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.extended_server_blob_auditing_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerBlobAuditingPolicies/get/Get a server's blob auditing policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_blob_auditing_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerBlobAuditingPolicies/get/List auditing settings of a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_blob_auditing_policies.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ExtendedServerBlobAuditingPolicies/get/List extended auditing settings of a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.extended_server_blob_auditing_policies.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_communication_link(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        PARTNER_SERVER_NAME = "mypartnerserverxpxy"
        COMMUNICATION_LINK_NAME = "mycommunicationlink"
 
#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=PARTNER_SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerCommunicationLinks/put/Create a server communication link[put]
#--------------------------------------------------------------------------
        BODY = {
          "partner_server": PARTNER_SERVER_NAME 
        }
        result = self.mgmt_client.server_communication_links.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, communication_link_name=COMMUNICATION_LINK_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerCommunicationLinks/get/Get a server communication link[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_communication_links.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, communication_link_name=COMMUNICATION_LINK_NAME)

#--------------------------------------------------------------------------
        # /ServerCommunicationLinks/get/List server communication links[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_communication_links.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerCommunicationLinks/delete/Delete a server communication link[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_communication_links.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, communication_link_name=COMMUNICATION_LINK_NAME)

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_firewall_rule(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        FIREWALL_RULE_NAME = "myfirewallrule"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /FirewallRules/put/Create a firewall rule max/min[put]
#--------------------------------------------------------------------------
        BODY = {
          "start_ip_address": "0.0.0.3",
          "end_ip_address": "0.0.0.3"
        }
        result = self.mgmt_client.firewall_rules.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, firewall_rule_name=FIREWALL_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /FirewallRules/get/Get Firewall Rule[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, firewall_rule_name=FIREWALL_RULE_NAME)

#--------------------------------------------------------------------------
        # /FirewallRules/get/List Firewall Rules[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /FirewallRules/delete/Delete a firewall rule[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, firewall_rule_name=FIREWALL_RULE_NAME)

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myServerxpxy"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/get/Get server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /Servers/get/List servers by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /Servers/get/List servers[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.list()

#--------------------------------------------------------------------------
        # /ServerUsages/get/List servers usages[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_usages.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /Servers/patch/Update a server[patch]
#--------------------------------------------------------------------------
        BODY = {
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/post/Check for a server name that already exists[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "server1",
          "type": "Microsoft.Sql/servers"
        }
        result = self.mgmt_client.servers.check_name_availability(parameters=BODY)

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()
