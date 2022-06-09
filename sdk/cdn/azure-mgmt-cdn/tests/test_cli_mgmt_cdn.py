# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 41
# Methods Covered : 41
# Examples Total  : 42
# Examples Tested : 42
# Coverage %      : 100
# ----------------------

import os
import unittest

import azure.mgmt.cdn
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtCdn(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.cdn.CdnManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_cdn(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = None
        if self.is_live:
            SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", None)
        if not SUBSCRIPTION_ID:
            SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        PROFILE_NAME = "profilename"
        CDN_WEB_APPLICATION_FIREWALL_POLICY_NAME = "policyname"
        ENDPOINT_NAME = "endpoint9527x"
        CUSTOM_DOMAIN_NAME = "someDomain"
        ORIGIN_NAME = "origin1"

        # Profiles_Create[put]
        BODY = {
          "location": "WestUs",
          "sku": {
            "name": "Standard_Verizon"
          }
        }
        result = self.mgmt_client.profiles.begin_create(resource_group.name, PROFILE_NAME, BODY)
        result = result.result()

        """
        # Creates specific policy[put]
        BODY = {
          "location": "global",
          "sku": {
            "name": "Standard_Microsoft"
          },
          "policy_settings": {
            "default_redirect_url": "http://www.bing.com",
            "default_custom_block_response_status_code": "499",
            "default_custom_block_response_body": "PGh0bWw+CjxoZWFkZXI+PHRpdGxlPkhlbGxvPC90aXRsZT48L2hlYWRlcj4KPGJvZHk+CkhlbGxvIHdvcmxkCjwvYm9keT4KPC9odG1sPg=="
          },
          "rate_limit_rules": {
            "rules": [
              {
                "name": "RateLimitRule1",
                "priority": "1",
                "enabled_state": "Enabled",
                "rate_limit_duration_in_minutes": "0",
                "rate_limit_threshold": "1000",
                "match_conditions": [
                  {
                    "match_variable": "RemoteAddr",
                    "operator": "IPMatch",
                    "negate_condition": False,
                    "transforms": [],
                    "match_value": [
                      "192.168.1.0/24",
                      "10.0.0.0/24"
                    ]
                  }
                ],
                "action": "Block"
              }
            ]
          },
          "custom_rules": {
            "rules": [
              {
                "name": "CustomRule1",
                "priority": "2",
                "enabled_state": "Enabled",
                "match_conditions": [
                  {
                    "match_variable": "RemoteAddr",
                    "operator": "GeoMatch",
                    "negate_condition": False,
                    "transforms": [],
                    "match_value": [
                      "CH"
                    ]
                  },
                  {
                    "match_variable": "RequestHeader",
                    "selector": "UserAgent",
                    "operator": "Contains",
                    "negate_condition": False,
                    "transforms": [],
                    "match_value": [
                      "windows"
                    ]
                  },
                  {
                    "match_variable": "QueryString",
                    "selector": "search",
                    "operator": "Contains",
                    "negate_condition": False,
                    "transforms": [
                      "UrlDecode",
                      "Lowercase"
                    ],
                    "match_value": [
                      "<?php",
                      "?>"
                    ]
                  }
                ],
                "action": "Block"
              }
            ]
          },
          "managed_rules": {
            "managed_rule_sets": [
              {
                "rule_set_type": "DefaultRuleSet",
                "rule_set_version": "preview-1.0",
                "rule_group_overrides": [
                  {
                    "rule_group_name": "Group1",
                    "rules": [
                      {
                        "rule_id": "GROUP1-0001",
                        "enabled_state": "Enabled",
                        "action": "Redirect"
                      },
                      {
                        "rule_id": "GROUP1-0002",
                        "enabled_state": "Disabled"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        }
        result = self.mgmt_client.policies.create_or_update(resource_group.name, CDN_WEB_APPLICATION_FIREWALL_POLICY_NAME, BODY)
        result = result.result()
        """

        # Endpoints_Create[put]
        BODY = {
          "origin_host_header": "www.bing.com",
          "origin_path": "/image",
          "content_types_to_compress": [
            "text/html",
            "application/octet-stream"
          ],
          "is_compression_enabled": True,
          "is_http_allowed": True,
          "is_https_allowed": True,
          "query_string_caching_behavior": "BypassCaching",
          # "delivery_policy": {
          #   "description": "Test description for a policy.",
          #   "rules": [
          #     {
          #       "name": "rule1",
          #       "order": "1",
          #       "conditions": [
          #         {
          #           "name": "RemoteAddress",
          #           "parameters": {
          #             "operator": "IPMatch",
          #             "negate_condition": True,
          #             "match_values": [
          #               "192.168.1.0/24",
          #               "10.0.0.0/24"
          #             ],
          #             "@odata.type": "#Microsoft.Azure.Cdn.Models.DeliveryRuleRemoteAddressConditionParameters"
          #           }
          #         }
          #       ],
          #       "actions": [
          #         {
          #           "name": "CacheExpiration",
          #           "parameters": {
          #             "cache_behavior": "Override",
          #             "cache_duration": "10:10:09",
          #             "@odata.type": "#Microsoft.Azure.Cdn.Models.DeliveryRuleCacheExpirationActionParameters",
          #             "cache_type": "All"
          #           }
          #         },
          #         {
          #           "name": "ModifyResponseHeader",
          #           "parameters": {
          #             "header_action": "Overwrite",
          #             "header_name": "Access-Control-Allow-Origin",
          #             "value": "*",
          #             "@odata.type": "#Microsoft.Azure.Cdn.Models.DeliveryRuleHeaderActionParameters"
          #           }
          #         },
          #         {
          #           "name": "ModifyRequestHeader",
          #           "parameters": {
          #             "header_action": "Overwrite",
          #             "header_name": "Accept-Encoding",
          #             "value": "gzip",
          #             "@odata.type": "#Microsoft.Azure.Cdn.Models.DeliveryRuleHeaderActionParameters"
          #           }
          #         }
          #       ]
          #     }
          #   ]
          # },
          "origins": [
            {
              "name": "origin1",
              "host_name": "host1.hello.com"
            }
          ],
          # "web_application_firewall_policy_link": {
          #   "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Cdn/CdnWebApplicationFirewallPolicies/" + CDN_WEB_APPLICATION_FIREWALL_POLICY_NAME + ""
          # },
          "location": "WestUs",
          "tags": {
            "kay1": "value1"
          }
        }
        result = self.mgmt_client.endpoints.begin_create(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, BODY)
        result = result.result()

        """
        # CustomDomains_Create[put]
        # BODY = {
        #   "host_name": "www.someDomain.net"
        # }
        HOST_NAME = "www.someDomain.net"
        result = self.mgmt_client.custom_domains.create(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, CUSTOM_DOMAIN_NAME, HOST_NAME)
        result = result.result()

        # CustomDomains_Get[get]
        result = self.mgmt_client.custom_domains.get(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, CUSTOM_DOMAIN_NAME)
        """

        # Origins_Get[get]
        result = self.mgmt_client.origins.get(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, ORIGIN_NAME)

        """
        # Get Policy[get]
        result = self.mgmt_client.policies.get(resource_group.name, CDN_WEB_APPLICATION_FIREWALL_POLICY_NAME)
        """

        # CustomDomains_ListByEndpoint[get]
        result = self.mgmt_client.custom_domains.list_by_endpoint(resource_group.name, PROFILE_NAME, ENDPOINT_NAME)

        # Origins_ListByEndpoint[get]
        result = self.mgmt_client.origins.list_by_endpoint(resource_group.name, PROFILE_NAME, ENDPOINT_NAME)

        # Endpoints_Get[get]
        result = self.mgmt_client.endpoints.get(resource_group.name, PROFILE_NAME, ENDPOINT_NAME)

        # Endpoints_ListByProfile[get]
        result = self.mgmt_client.endpoints.list_by_profile(resource_group.name, PROFILE_NAME)

        # List Policies in a Resource Group[get]
        result = self.mgmt_client.policies.list(resource_group.name)

        # Profiles_Get[get]
        result = self.mgmt_client.profiles.get(resource_group.name, PROFILE_NAME)

        # Profiles_ListByResourceGroup[get]
        result = self.mgmt_client.profiles.list_by_resource_group(resource_group.name)

        # List Policies in a Resource Group[get]
        result = self.mgmt_client.policies.list(resource_group.name)

        # Profiles_List[get]
        result = self.mgmt_client.profiles.list()

        # Operations_List[get]
        result = self.mgmt_client.operations.list()

        # EdgeNodes_List[get]
        result = self.mgmt_client.edge_nodes.list()

        """
        # CustomDomains_DisableCustomHttps[post]
        result = self.mgmt_client.custom_domains.disable_custom_https(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, CUSTOM_DOMAIN_NAME)

        # CustomDomains_EnableCustomHttpsUsingYourOwnCertificate[post]
        BODY = {
          "certificate_source": "AzureKeyVault",
          "protocol_type": "ServerNameIndication",
          "certificate_source_parameters": {
            "odata.type": "#Microsoft.Azure.Cdn.Models.KeyVaultCertificateSourceParameters",
            "subscription_id": "subid",
            "resource_group_name": "RG",
            "vault_name": "kv",
            "secret_name": "secret1",
            "secret_version": "00000000-0000-0000-0000-000000000000",
            "update_rule": "NoAction",
            "delete_rule": "NoAction"
          }
        }
        result = self.mgmt_client.custom_domains.enable_custom_https(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, CUSTOM_DOMAIN_NAME, BODY)

        # CustomDomains_EnableCustomHttpsUsingCDNManagedCertificate[post]
        BODY = {
          "certificate_source": "Cdn",
          "protocol_type": "ServerNameIndication",
          "certificate_source_parameters": {
            "odata.type": "#Microsoft.Azure.Cdn.Models.CdnCertificateSourceParameters",
            "certificate_type": "Shared"
          }
        }
        result = self.mgmt_client.custom_domains.enable_custom_https(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, CUSTOM_DOMAIN_NAME, BODY)
        """

        # Origins_Update[patch]
        BODY = {
          "http_port": "42",
          "https_port": "43"
        }
        result = self.mgmt_client.origins.begin_update(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, ORIGIN_NAME, BODY)
        result = result.result()

        """
        # Creates specific policy[put]
        BODY = {
          "location": "WestUs",
          "sku": {
            "name": "Standard_Microsoft"
          },
          "policy_settings": {
            "default_redirect_url": "http://www.bing.com",
            "default_custom_block_response_status_code": "499",
            "default_custom_block_response_body": "PGh0bWw+CjxoZWFkZXI+PHRpdGxlPkhlbGxvPC90aXRsZT48L2hlYWRlcj4KPGJvZHk+CkhlbGxvIHdvcmxkCjwvYm9keT4KPC9odG1sPg=="
          },
          "rate_limit_rules": {
            "rules": [
              {
                "name": "RateLimitRule1",
                "priority": "1",
                "enabled_state": "Enabled",
                "rate_limit_duration_in_minutes": "0",
                "rate_limit_threshold": "1000",
                "match_conditions": [
                  {
                    "match_variable": "RemoteAddr",
                    "operator": "IPMatch",
                    "negate_condition": False,
                    "transforms": [],
                    "match_value": [
                      "192.168.1.0/24",
                      "10.0.0.0/24"
                    ]
                  }
                ],
                "action": "Block"
              }
            ]
          },
          "custom_rules": {
            "rules": [
              {
                "name": "CustomRule1",
                "priority": "2",
                "enabled_state": "Enabled",
                "match_conditions": [
                  {
                    "match_variable": "RemoteAddr",
                    "operator": "GeoMatch",
                    "negate_condition": False,
                    "transforms": [],
                    "match_value": [
                      "CH"
                    ]
                  },
                  {
                    "match_variable": "RequestHeader",
                    "selector": "UserAgent",
                    "operator": "Contains",
                    "negate_condition": False,
                    "transforms": [],
                    "match_value": [
                      "windows"
                    ]
                  },
                  {
                    "match_variable": "QueryString",
                    "selector": "search",
                    "operator": "Contains",
                    "negate_condition": False,
                    "transforms": [
                      "UrlDecode",
                      "Lowercase"
                    ],
                    "match_value": [
                      "<?php",
                      "?>"
                    ]
                  }
                ],
                "action": "Block"
              }
            ]
          },
          "managed_rules": {
            "managed_rule_sets": [
              {
                "rule_set_type": "DefaultRuleSet",
                "rule_set_version": "preview-1.0",
                "rule_group_overrides": [
                  {
                    "rule_group_name": "Group1",
                    "rules": [
                      {
                        "rule_id": "GROUP1-0001",
                        "enabled_state": "Enabled",
                        "action": "Redirect"
                      },
                      {
                        "rule_id": "GROUP1-0002",
                        "enabled_state": "Disabled"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        }
        result = self.mgmt_client.policies.create_or_update(resource_group.name, CDN_WEB_APPLICATION_FIREWALL_POLICY_NAME, BODY)
        result = result.result()
        """

        # Endpoints_ValidateCustomDomain[post]
        BODY = {
          "host_name": "www.someDomain.com"
        }
        # HOST_NAME = "www.someDomain.com"
        result = self.mgmt_client.endpoints.validate_custom_domain(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, BODY)

        # Endpoints_ListResourceUsage[post]
        result = self.mgmt_client.endpoints.list_resource_usage(resource_group.name, PROFILE_NAME, ENDPOINT_NAME)

        # Endpoints_PurgeContent[post]
        BODY = {
          "content_paths": [
            "/folder1"
          ]
        }
        # CONTENT_PATHS = ["/folder1"]
        result = self.mgmt_client.endpoints.begin_purge_content(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, BODY)
        result = result.result()

        # Endpoints_Stop[post]
        result = self.mgmt_client.endpoints.begin_stop(resource_group.name, PROFILE_NAME, ENDPOINT_NAME)
        result = result.result()

        # Endpoints_Start[post]
        result = self.mgmt_client.endpoints.begin_start(resource_group.name, PROFILE_NAME, ENDPOINT_NAME)
        result = result.result()

        # Endpoints_LoadContent[post]
        BODY = {
          "content_paths": [
            "/folder1"
          ]
        }
        # CONTENT_PATHS = ["/folder1"]
        result = self.mgmt_client.endpoints.begin_load_content(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, BODY)
        result = result.result()

        # Profiles_ListSupportedOptimizationTypes[post]
        result = self.mgmt_client.profiles.list_supported_optimization_types(resource_group.name, PROFILE_NAME)

        # Endpoints_Update[patch]
        BODY = {
          "tags": {
            "additional_properties": "Tag1"
          },
          # "web_application_firewall_policy_link": {
          #   "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Cdn/CdnWebApplicationFirewallPolicies/" + CDN_WEB_APPLICATION_FIREWALL_POLICY_NAME + ""
          # }
        }
        result = self.mgmt_client.endpoints.begin_update(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, BODY)
        result = result.result()

        # Profiles_ListResourceUsage[post]
        result = self.mgmt_client.profiles.list_resource_usage(resource_group.name, PROFILE_NAME)

        # Profiles_GenerateSsoUri[post]
        result = self.mgmt_client.profiles.generate_sso_uri(resource_group.name, PROFILE_NAME)

        # Profiles_Update[patch]
        BODY = {
          "tags": {
            "additional_properties": "Tag1"
          }
        }
        result = self.mgmt_client.profiles.begin_update(resource_group.name, PROFILE_NAME, BODY)
        result = result.result()

        # CheckNameAvailabilityWithSubscription[post]
        BODY = {
          "name": "sampleName",
          "type": "Microsoft.Cdn/Profiles/Endpoints"
        }
        # CHECK_NAME = "sampleName"
        result = self.mgmt_client.check_name_availability_with_subscription(BODY)

        # ResourceUsage_List[post]
        result = self.mgmt_client.resource_usage.list()

        # ValidateProbe[post]
        BODY = {
          "probe_url": "https://www.bing.com/image"
        }
        # PROBEURL = "https://www.bing.com/image"
        result = self.mgmt_client.validate_probe(BODY)

        # CheckNameAvailability[post]
        BODY = {
          "name": "sampleName",
          "type": "Microsoft.Cdn/Profiles/Endpoints"
        }
        # CHECKNAME = "sampleName"
        result = self.mgmt_client.check_name_availability(BODY)

        # CustomDomains_Delete[delete]
        result = self.mgmt_client.custom_domains.begin_delete(resource_group.name, PROFILE_NAME, ENDPOINT_NAME, CUSTOM_DOMAIN_NAME)
        result = result.result()

        """
        # Delete protection policy[delete]
        result = self.mgmt_client.policies.delete(resource_group.name, CDN_WEB_APPLICATION_FIREWALL_POLICY_NAME)
        """

        # Endpoints_Delete[delete]
        result = self.mgmt_client.endpoints.begin_delete(resource_group.name, PROFILE_NAME, ENDPOINT_NAME)
        result = result.result()

        # Profiles_Delete[delete]
        result = self.mgmt_client.profiles.begin_delete(resource_group.name, PROFILE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
