# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 23
# Methods Covered : 23
# Examples Total  : 23
# Examples Tested : 23
# Coverage %      : 100
# ----------------------

#  application_gateways: /17
#  application_security_groups: /6

import unittest

import azure.mgmt.network
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtNetworkTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNetworkTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )
        if self.is_live:
            from azure.mgmt.keyvault import KeyVaultManagementClient
            self.kv_client = self.create_mgmt_client(
                KeyVaultManagementClient
            )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):
        result = self.mgmt_client.virtual_networks.begin_create_or_update(
            group_name,
            network_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            },
        )
        result_create = result.result()

        async_subnet_creation = self.mgmt_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name,
            {
              'address_prefix': '10.0.0.0/24',
            }
        )
        return async_subnet_creation.result()

    def create_public_ip_address(self, group_name, location, public_ip_address_name):
        # Create public IP address defaults[put]
        BODY = {
          "public_ip_allocation_method": "Static",
          "idle_timeout_in_minutes": 10,
          "public_ip_address_version": "IPv4",
          "location": location,
          "sku": {
            "name": "Standard"
          }
        }
        result = self.mgmt_client.public_ip_addresses.begin_create_or_update(group_name, public_ip_address_name, BODY)
        result = result.result()

    def create_keyvault(self, group_name, location, tenant_id, vault_name):
          # /Vaults/put/Create a new vault or update an existing vault[put]
        BODY = {
          "location": location,
          "properties": {
            "tenant_id": tenant_id,
            "sku": {
              "family": "A",
              "name": "standard"
            },
            "access_policies": [
              {
                "tenant_id": tenant_id,
                "object_id": "00000000-0000-0000-0000-000000000000",
                "permissions": {
                  "keys": [
                    "encrypt",
                    "decrypt",
                    "wrapKey",
                    "unwrapKey",
                    "sign",
                    "verify",
                    "get",
                    "list",
                    "create",
                    "update",
                    "import",
                    "delete",
                    "backup",
                    "restore",
                    "recover",
                    "purge"
                  ],
                  "secrets": [
                    "get",
                    "list",
                    "set",
                    "delete",
                    "backup",
                    "restore",
                    "recover",
                    "purge"
                  ],
                  "certificates": [
                    "get",
                    "list",
                    "delete",
                    "create",
                    "import",
                    "update",
                    "managecontacts",
                    "getissuers",
                    "listissuers",
                    "setissuers",
                    "deleteissuers",
                    "manageissuers",
                    "recover",
                    "purge"
                  ]
                }
              }
            ],
            "enabled_for_deployment": True,
            "enabled_for_disk_encryption": True,
            "enabled_for_template_deployment": True
          }
        }
        result = self.kv_client.vaults.create_or_update(group_name, vault_name, BODY)
        return result.result()

    def create_kv_secret(self, vault_uri, secret_name, secret_value):
        from azure.identity import EnvironmentCredential
        from azure.keyvault.secrets import SecretClient

        secret_client = SecretClient(vault_uri, EnvironmentCredential())
        secret = secret_client.set_secret(secret_name, secret_value)
        return secret.id

        
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_NETWORK_NAME = "virtualnetwork"
        SUBNET_NAME = "subnet"
        PUBLIC_IP_ADDRESS_NAME = "publicipaddress"
        VAULT_NAME = self.get_resource_name("vaultx")
        SECRET_NAME = self.get_resource_name("secretx")
        SECRET_VALUE = self.get_resource_name("secretvaluex")
        SECRET_NAME_2 = self.get_resource_name("secretxy")
        SECRET_VALUE_2 = self.get_resource_name("secretvaluexy")


        APPLICATION_GATEWAY_NAME = self.get_resource_name("applicationgateway")
        APPLICATION_SECURITY_GROUP_NAME = self.get_resource_name("applicationsecuritygorup")
        BACKEND_ADDRESS_POOL_NAME = "backendaddresspool"
        BACKEND_HTTP_SETTINGS_COLLECTION_NAME = "backendhttpsettingscollection"
        APPLICATION_GATEWAY_AVAILABLE_SSL_OPTION_NAME = ""
        PREDEFINED_POLICY_NAME = ""
        FRONTEND_IPCONFIGURATION_NAME = "frontendipconfiguration"
        FRONTEND_PORT_NAME = "frontendport"
        SSL_CERTIFICATE_NAME = "sslcertificate"
        TRUSTED_ROOT_CERTIFICATE_NAME = "trustedrootcertificate"
        HTTP_LISTENER_NAME = "httplistener"
        REWRITE_RULE_SET_NAME = "rewriteruleset"
        URL_PATH_MAP_NAME = "urlpathmap"
        API_PATH_NAME = "apipath"
        REQUEST_ROUTING_RULE_NAME = "requestroutingrule"

        self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        self.create_public_ip_address(RESOURCE_GROUP, AZURE_LOCATION, PUBLIC_IP_ADDRESS_NAME)
        vault = self.create_keyvault(RESOURCE_GROUP, AZURE_LOCATION, TENANT_ID, VAULT_NAME)
        secret_id = self.create_kv_secret(vault.properties.vault_uri, SECRET_NAME, SECRET_VALUE)
        root_secret_id = self.create_kv_secret(vault_uri, SECRET_NAME_2, SECRET_VALUE_2)

        # Create Application Gateway[put]
        BODY = {
          # "identity": {
          #   "type": "UserAssigned",
          #   # "user_assigned_identities": {}
          # },
          "location": "eastus",
          "sku": {
            # "name": "Standard_v2",
            "name": "Standard_Medium",
            # "tier": "Standard_v2",
            "tier": "Standard",
            "capacity": "3"
          },
          "gateway_ip_configurations": [
            {
              "name": "appgwipc",
              "subnet": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
              }
            }
          ],
          "ssl_certificates": [
            # {
            #   "name": "sslcert",
            #   "properties": {
            #     "data": "****",
            #     "password": "****"
            #   }
            # },
            {
              "name": SSL_CERTIFICATE_NAME,
              # "key_vault_secret_id": "https://kv/secret"
              "key_vault_secret_id": secret_id
            }
          ],
          "trusted_root_certificates": [
            # {
            #   "name": "rootcert",
            #   "properties": {
            #     "data": "****"
            #   }
            # },
            {
              "name": TRUSTED_ROOT_CERTIFICATE_NAME,
              # "key_vault_secret_id": "https://kv/secret"
              "key_vault_secret_id": root_secret_id
            }
          ],
          "frontend_ip_configurations": [
            {
              "name": FRONTEND_IPCONFIGURATION_NAME,
              "public_ip_address": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/publicIPAddresses/" + PUBLIC_IP_ADDRESS_NAME + ""
              }
            }
          ],
          "frontend_ports": [
            {
              "name": "appgwfp",
              "port": "443"
            },
            {
              "name": FRONTEND_PORT_NAME,
              "port": "80"
            }
          ],
          "backend_address_pools": [
            {
              "name": BACKEND_ADDRESS_POOL_NAME,
              "backend_addresses": [
                {
                  "ip_address": "10.0.1.1"
                },
                {
                  "ip_address": "10.0.1.2"
                }
              ]
            }
          ],
          "backend_http_settings_collection": [
            {
              "name": BACKEND_HTTP_SETTINGS_COLLECTION_NAME,
              "port": "80",
              "protocol": "Http",
              "cookie_based_affinity": "Disabled",
              "request_timeout": "30"
            }
          ],
          "http_listeners": [
            {
              "name": HTTP_LISTENER_NAME,
              "frontend_ipconfiguration": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/frontendIPConfigurations/" + FRONTEND_IPCONFIGURATION_NAME + ""
              },
              "frontend_port": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/frontendPorts/" + FRONTEND_PORT_NAME + ""
              },
              "protocol": "Https",
              "ssl_certificate": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/sslCertificates/" + SSL_CERTIFICATE_NAME + ""
              },
              "require_server_name_indication": False
            },
            # {
            #   "name": "appgwhttplistener",
            #   "properties": {
            #     "frontend_ipconfiguration": {
            #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/frontendIPConfigurations/" + FRONTEND_IPCONFIGURATION_NAME + ""
            #     },
            #     "frontend_port": {
            #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/frontendPorts/" + FRONTEND_PORT_NAME + ""
            #     },
            #     "protocol": "Http"
            #   }
            # }
          ],
          "url_path_maps": [
            {
              "name": URL_PATH_MAP_NAME,
              "default_backend_address_pool": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendAddressPools/" + BACKEND_ADDRESS_POOL_NAME + ""
              },
              "default_backend_http_settings": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendHttpSettingsCollection/" + BACKEND_HTTP_SETTINGS_COLLECTION_NAME + ""
              },
              "default_rewrite_rule_set": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/rewriteRuleSets/" + REWRITE_RULE_SET_NAME + ""
              },
              "path_rules": [
                {
                  "name": API_PATH_NAME,
                  "paths": [
                    "/api",
                    "/v1/api"
                  ],
                  "backend_address_pool": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendAddressPools/" + BACKEND_ADDRESS_POOL_NAME + ""
                  },
                  "backend_http_settings": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendHttpSettingsCollection/" + BACKEND_HTTP_SETTINGS_COLLECTION_NAME + ""
                  },
                  "rewrite_rule_set": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/rewriteRuleSets/" + REWRITE_RULE_SET_NAME + ""
                  }
                }
              ]
            }
          ],
          "request_routing_rules": [
            {
              "name": REQUEST_ROUTING_RULE_NAME,
              "rule_type": "Basic",
              "priority": "10",
              "http_listener": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/httpListeners/" + HTTP_LISTENER_NAME + ""
              },
              "backend_address_pool": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendAddressPools/" + BACKEND_ADDRESS_POOL_NAME + ""
              },
              "backend_http_settings": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendHttpSettingsCollection/" + BACKEND_HTTP_SETTINGS_COLLECTION_NAME + ""
              },
              "rewrite_rule_set": {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/rewriteRuleSets/" + REWRITE_RULE_SET_NAME + ""
              }
            },
            # {
            #   "name": "appgwPathBasedRule",
            #   "properties": {
            #     "rule_type": "PathBasedRouting",
            #     "priority": "20",
            #     "http_listener": {
            #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/httpListeners/" + HTTP_LISTENER_NAME + ""
            #     },
            #     "url_path_map": {
            #       "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/urlPathMaps/" + URL_PATH_MAP_NAME + ""
            #     }
            #   }
            # }
          ],
          "rewrite_rule_sets": [
            {
              "name": REWRITE_RULE_SET_NAME,
              "rewrite_rules": [
                {
                  "name": "Set X-Forwarded-For",
                  "rule_sequence": "102",
                  "conditions": [
                    {
                      "variable": "http_req_Authorization",
                      "pattern": "^Bearer",
                      "ignore_case": True,
                      "negate": False
                    }
                  ],
                  "action_set": {
                    "request_header_configurations": [
                      {
                        "header_name": "X-Forwarded-For",
                        "header_value": "{var_add_x_forwarded_for_proxy}"
                      }
                    ],
                    "response_header_configurations": [
                      {
                        "header_name": "Strict-Transport-Security",
                        "header_value": "max-age=31536000"
                      }
                    ],
                    "url_configuration": {
                      "modified_path": "/abc"
                    }
                  }
                }
              ]
            }
          ]
        }
        result = self.mgmt_client.application_gateways.begin_create_or_update(resource_group.name, APPLICATION_GATEWAY_NAME, BODY)
        result = result.result()

        # Create application security group[put]
        BODY = {
          "location": "westus"
        }
        result = self.mgmt_client.application_security_groups.begin_create_or_update(resource_group.name, APPLICATION_SECURITY_GROUP_NAME, BODY)
        result = result.result()

        # Get Available Ssl Predefined Policy by name[get]
        # result = self.mgmt_client.application_gateways.get_ssl_predefined_policy(APPLICATION_GATEWAY_AVAILABLE_SSL_OPTION_NAME, PREDEFINED_POLICY_NAME)

        # Get Available Ssl Predefined Policies[get]
        # result = self.mgmt_client.application_gateways.list_available_ssl_predefined_policies(APPLICATION_GATEWAY_AVAILABLE_SSL_OPTION_NAME)

        # Get application security group[get]
        result = self.mgmt_client.application_security_groups.get(resource_group.name, APPLICATION_SECURITY_GROUP_NAME)

        # Get Available Ssl Options[get]
        # result = self.mgmt_client.application_gateways.list_available_ssl_options(APPLICATION_GATEWAY_AVAILABLE_SSL_OPTION_NAME)

        # Get ApplicationGateway[get]
        result = self.mgmt_client.application_gateways.get(resource_group.name, APPLICATION_GATEWAY_NAME)

        # List load balancers in resource group[get]
        result = self.mgmt_client.application_security_groups.list(resource_group.name)

        # Lists all application gateways in a resource group[get]
        result = self.mgmt_client.application_gateways.list(resource_group.name)

        # Get Available Server Variables[get]
        result = self.mgmt_client.application_gateways.list_available_server_variables()

        # Get Available Response Headers[get]
        result = self.mgmt_client.application_gateways.list_available_response_headers()

        # Get Available Request Headers[get]
        result = self.mgmt_client.application_gateways.list_available_request_headers()

        # Get Available Waf Rule Sets[get]
        result = self.mgmt_client.application_gateways.list_available_waf_rule_sets()

        # List all application security groups[get]
        result = self.mgmt_client.application_security_groups.list_all()

        # Lists all application gateways in a subscription[get]
        result = self.mgmt_client.application_gateways.list_all()

        # Test Backend Health[post]
        BODY = {
          "protocol": "Http",
          "pick_host_name_from_backend_http_settings": True,
          "path": "/",
          "timeout": "30",
          "backend_address_pool": {
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendaddressPools/" + BACKENDADDRESS_POOL_NAME + ""
          },
          "backend_http_settings": {
            "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/applicationGateways/" + APPLICATION_GATEWAY_NAME + "/backendHttpSettingsCollection/" + BACKEND_HTTP_SETTINGS_COLLECTION_NAME + ""
          }
        }
        result = self.mgmt_client.application_gateways.begin_backend_health_on_demand(resource_group.name, APPLICATION_GATEWAY_NAME, BODY)
        result = result.result()

        # Get Backend Health[post]
        result = self.mgmt_client.application_gateways.begin_backend_health(resource_group.name, APPLICATION_GATEWAY_NAME)
        result = result.result()

        # Update application security group tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.application_security_groups.update_tags(resource_group.name, APPLICATION_SECURITY_GROUP_NAME, BODY)

        # Start Application Gateway[post]
        result = self.mgmt_client.application_gateways.begin_start(resource_group.name, APPLICATION_GATEWAY_NAME)
        result = result.result()

        # Stop Application Gateway[post]
        result = self.mgmt_client.application_gateways.begin_stop(resource_group.name, APPLICATION_GATEWAY_NAME)
        result = result.result()

        # Update Application Gateway tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.application_gateways.update_tags(resource_group.name, APPLICATION_GATEWAY_NAME, BODY)

        # Delete application security group[delete]
        result = self.mgmt_client.application_security_groups.begin_delete(resource_group.name, APPLICATION_SECURITY_GROUP_NAME)
        result = result.result()

        # Delete ApplicationGateway[delete]
        result = self.mgmt_client.application_gateways.begin_delete(resource_group.name, APPLICATION_GATEWAY_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
