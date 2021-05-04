# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   Servers: 7/7
#   ServerUsages: 1/1
#   FirewallRules: 4/4
#   ServerCommunicationLinks: 4/4
#   ServerBlobAuditingPolicies: 3/3
#   ExtendedServerBlobAuditingPolicies: 3/3
#   ServerDnsAliases: 5/5
#   Capabilities: 1/1
#   ServerAzureADAdministrators: 0/4
#   ServiceObjectives: 2/2
#   VirtualNetworkRules: 4/4
#   SubscriptionUsages: 2/2
#   ServerAutomaticTuning: 2/2
#   ServerSecurityAlertPolicies: 3/3
#   TdeCertificates: 0/1
#   Capabilities: 1/1

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

        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

            from azure.mgmt.storage import StorageManagementClient
            self.storage_client = self.create_mgmt_client(
                StorageManagementClient
            )

    def create_blob_container(self, location, group_name, account_name, container_name):

        # StorageAccountCreate[put]
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
          "kind": "StorageV2",
          "location": location,
          "encryption": {
            "services": {
              "file": {
                "key_type": "Account",
                "enabled": True
              },
              "blob": {
                "key_type": "Account",
                "enabled": True
              }
            },
            "key_source": "Microsoft.Storage"
          },
          "tags": {
            "key1": "value1",
            "key2": "value2"
          }
        }
        result = self.storage_client.storage_accounts.begin_create(group_name, account_name, BODY)
        storageaccount = result.result()

        # PutContainers[put]
        result = self.storage_client.blob_containers.create(group_name, account_name, container_name, {})

        # StorageAccountRegenerateKey[post]
        BODY = {
          "key_name": "key2"
        }
        key = self.storage_client.storage_accounts.regenerate_key(group_name, account_name, BODY)
        return key.keys[0].value

    def create_virtual_network(self, group_name, location, network_name, subnet_name):

        # create virtual network
        azure_operation_poller = self.network_client.virtual_networks.begin_create_or_update(
            group_name,
            network_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            }
        )
        result_create = azure_operation_poller.result()

        # create subnet
        async_subnet_creation = self.network_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name,
            {
                'address_prefix': '10.0.0.0/24',
            }
        )
        subnet_info = async_subnet_creation.result()

        return subnet_info

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_tde_certificates(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"

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
        # /TdeCertificates/post/Upload a TDE certificate[post]
#--------------------------------------------------------------------------
        BODY = {
          "private_blob": "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",
          "cert_password": "Un53cuRE!"
        }
        result = self.mgmt_client.tde_certificates.begin_create(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_security_alert_policy(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        STORAGE_ACCOUNT_NAME = "mystorageaccountxyd"
        BLOB_CONTAINER_NAME = "myblobcontainer"
        SECURITY_ALERT_POLICY_NAME = "default"

        if self.is_live:
            ACCESS_KEY = self.create_blob_container(AZURE_LOCATION, RESOURCE_GROUP, STORAGE_ACCOUNT_NAME, BLOB_CONTAINER_NAME)
        else:
            ACCESS_KEY = "accesskey"

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
        # /ServerSecurityAlertPolicies/put/Update a server's threat detection policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Disabled",
          "email_account_admins": True,
          "storage_account_access_key": ACCESS_KEY,
          "storage_endpoint": "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net"
        }
        result = self.mgmt_client.server_security_alert_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerSecurityAlertPolicies/get/Get a server's threat detection policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_security_alert_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME)

#--------------------------------------------------------------------------
        # /ServerSecurityAlertPolicies/get/List the server's threat detection policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_security_alert_policies.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_automatic_tuning(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"

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
        # /DatabaseAutomaticTuning/get/Get a database's automatic tuning settings[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_automatic_tuning.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAutomaticTuning/patch/Updates database automatic tuning settings with minimal properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "desired_state": "Auto"
        }
        result = self.mgmt_client.server_automatic_tuning.update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_service_objective(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"

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
        # /ServiceObjectives/get/List service objectives[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.service_objectives.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        SERVICE_OBJECTIVE_NAME = result.next().name

#--------------------------------------------------------------------------
        # /ServiceObjectives/get/Get a service objective[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.service_objectives.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, service_objective_name=SERVICE_OBJECTIVE_NAME)

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_virtual_network_rule(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mysubnet"
        VIRTUAL_NETWORK_RULE_NAME = "myvirtualnetworkrule"

        if self.is_live:
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

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
        # /VirtualNetworkRules/put/Create or update a virtual network rule[put]
#--------------------------------------------------------------------------
        BODY = {
          "ignore_missing_vnet_service_endpoint": True,
          "virtual_network_subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME
        }
        result = self.mgmt_client.virtual_network_rules.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, virtual_network_rule_name=VIRTUAL_NETWORK_RULE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /VirtualNetworkRules/get/Gets a virtual network rule[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_network_rules.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, virtual_network_rule_name=VIRTUAL_NETWORK_RULE_NAME)

#--------------------------------------------------------------------------
        # /VirtualNetworkRules/get/List virtual network rules[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_network_rules.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /VirtualNetworkRules/delete/Delete a virtual network rule[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_network_rules.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, virtual_network_rule_name=VIRTUAL_NETWORK_RULE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_azure_adadministrator(self, resource_group):

        TENANT_ID = self.settings.TENANT_ID
        CLIENT_OID = self.settings.CLIENT_OID
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        ADMINISTRATOR_NAME = "myadministrator"

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
        # /ServerAzureADAdministrators/put/Creates or updates an existing Azure Active Directory administrator.[put]
#--------------------------------------------------------------------------
        BODY = {
          "administrator_type": "ActiveDirectory",
          "login": "bob@contoso.com",
        #   "sid": "c6b82b90-a647-49cb-8a62-0d2d3cb7ac7c",
          "sid": CLIENT_OID,
          "tenant_id": TENANT_ID
        }
        result = self.mgmt_client.server_azure_ad_administrators.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, administrator_name=ADMINISTRATOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerAzureADAdministrators/get/Gets a Azure Active Directory administrator.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_ad_administrators.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, administrator_name=ADMINISTRATOR_NAME)

#--------------------------------------------------------------------------
        # /ServerAzureADAdministrators/get/Gets a list of Azure Active Directory administrator.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_ad_administrators.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerAzureADAdministrators/delete/Delete Azure Active Directory administrator.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_ad_administrators.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, administrator_name=ADMINISTRATOR_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

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

    # @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_server_blob_auditing_policy(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxy"
        PARTNER_SERVER_NAME = "mypartnerserverxpxy"
        COMMUNICATION_LINK_NAME = "mycommunicationlink"
        STORAGE_ACCOUNT_NAME = "mystorageaccountxyr"
        BLOB_CONTAINER_NAME = "myblobcontainer"
        SECURITY_ALERT_POLICY_NAME = "default"

        if self.is_live:
            ACCESS_KEY = self.create_blob_container(AZURE_LOCATION, RESOURCE_GROUP, STORAGE_ACCOUNT_NAME, BLOB_CONTAINER_NAME)
        else:
            ACCESS_KEY = "accesskey"
 
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
        #   "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_account_access_key": ACCESS_KEY,
        #   "storage_endpoint": "https://mystorage.blob.core.windows.net"
          "storage_endpoint": "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net"
        }
        result = self.mgmt_client.server_blob_auditing_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ExtendedServerBlobAuditingPolicies/put/Update a server's extended blob auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
        #   "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_account_access_key": ACCESS_KEY,
        #   "storage_endpoint": "https://mystorage.blob.core.windows.net"
          "storage_endpoint": "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net"
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
        # /Capabilities/get/List subscription capabilities in the given location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.capabilities.list_by_location(location_name=AZURE_LOCATION)

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

    def test_subscription_usage(self):

#--------------------------------------------------------------------------
        # /SubscriptionUsages/get/List subscription usages in the given location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscription_usages.list_by_location(location_name=AZURE_LOCATION)
        USAGE_NAME = result.next().name

#--------------------------------------------------------------------------
        # /SubscriptionUsages/get/Get specific subscription usage in the given location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscription_usages.get(location_name=AZURE_LOCATION, usage_name=USAGE_NAME)

#--------------------------------------------------------------------------
        # /Capabilities/get/List subscription capabilities in the given location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.capabilities.list_by_location(location_name=AZURE_LOCATION)
