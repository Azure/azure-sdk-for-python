# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 52
# Methods Covered : 52
# Examples Total  : 55
# Examples Tested : 55
# Coverage %      : 100
# ----------------------

# current methods coverage: 42

import datetime as dt
import unittest

import azure.mgmt.storage
# import azure.mgmt.network
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'
ZERO = dt.timedelta(0)

class UTC(dt.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

class MgmtStorageTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtStorageTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.storage.StorageManagementClient
        )
        # self.network_client = self.create_mgmt_client(
        #   azure.mgmt.network.NetworkManagementClient
        # )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_storage(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        STORAGE_ACCOUNT_NAME = "storageaccountxxyyzz"
        FILE_SERVICE_NAME = "fileservicexxyyzz"
        SHARE_NAME = "filesharenamexxyyzz"
        BLOB_SERVICE_NAME = "blobservicexxyyzz"
        CONTAINER_NAME = "containernamexxyyzz"
        ENCRYPTION_SCOPE_NAME = "encryptionscopexxyyzz"
        IMMUTABILITY_POLICY_NAME = "immutabilitypolicynamexxyyzz"
        VNET_NAME = "virualnetwork111"
        SUB_NET = "subnet111"
        LOAD_BALANCER = "loaderbalancer"
        FIPCONFIG = "fipconfig123"
        BAPOOL = "bapool123"
        PROBES = "probe123"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "privateEndpointConnection"

        """ TODO: set up for endpoint
        # -- SET UP --
        # Create VNet
        async_vnet_creation = self.network_client.virtual_networks.create_or_update(
            resource_group.name,
            VNET_NAME,
            {
                'location': AZURE_LOCATION,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            }
        )
        async_vnet_creation.wait()

        # Create Subnet
        async_subnet_creation = self.network_client.subnets.create_or_update(
            resource_group.name,
            VNET_NAME,
            SUB_NET,
            {
              'address_prefix': '10.0.0.0/24',
               'private_link_service_network_policies': 'disabled',
               'private_endpoint_network_policies': 'disabled'
            }
        )
        subnet_info = async_subnet_creation.result()

        # Create load balancer
        BODY = {
          "location": "westeurope",
          "sku": {
            "name": "Standard"
          },
          "properties": {
            "frontendIPConfigurations": [
              {
                "name": FIPCONFIG,
                "properties": {
                  "subnet": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VNET_NAME + "/subnets/" + SUB_NET
                  }
                }
              }
            ],
          }
        }

        result = self.network_client.load_balancers.create_or_update(resource_group.name, LOAD_BALANCER, BODY)
        result.result()

        # Create private link services
        PRIVATE_LINK_SERVICES = "privatelinkservice"
        BODY = {
          "location": "westeurope",
          "properties": {
            "visibility": {
              "subscriptions": [
                SUBSCRIPTION_ID
              ]
            },
            "autoApproval": {
              "subscriptions": [
                SUBSCRIPTION_ID
              ]
            },
            "fqdns": [
              # "fqdn1",
              # "fqdn2",
              # "fqdn3"
            ],
            "loadBalancerFrontendIpConfigurations": [
              {
                "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER + "/frontendIPConfigurations/" + FIPCONFIG,
              }
            ],
            "ipConfigurations": [
              {
                "name": FIPCONFIG,
                "properties": {
                  "privateIPAddress": "10.0.0.5",
                  "privateIPAllocationMethod": "Static",
                  "privateIPAddressVersion": "IPv4",
                  "subnet": {
                    "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VNET_NAME + "/subnets/" + SUB_NET
                  }
                }
              }
            ]
          }
        }
        result = self.network_client.private_link_services.create_or_update(resource_group.name, PRIVATE_LINK_SERVICES, BODY)

        # Create private endpoint
        PRIVATE_ENDPOINT = "privateendpoint"
        BODY = {
          "location": "westeurope",
          "properties": {
            "privateLinkServiceConnections": [
              {
                "name": PRIVATE_LINK_SERVICES,  # TODO: This is needed, but was not showed in swagger.
                "private_link_service_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/privateLinkServices/" + PRIVATE_LINK_SERVICES,
              },
              {
                "name": PRIVATE_ENDPOINT_CONNECTION_NAME,
                "private_link_service_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + ""
              }
            ],
            "subnet": {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VNET_NAME + "/subnets/" + SUB_NET
            }
          }
        }
        result = self.network_client.private_endpoints.create_or_update(resource_group.name, PRIVATE_ENDPOINT, BODY)
        # -- SET UP END --
        """

        # StorageAccountCreate[put]
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
          # "kind": "Storage",
          "kind": "StorageV2",  # Storage v2 support policy
          "location": "westeurope",

          # TODO: The value 'True' is not allowed for property isHnsEnabled
          # "is_hns_enabled": True,
          # TODO:Unsupport
          # "routing_preference": {
          #   "routing_choice": "MicrosoftRouting",
          #   "publish_microsoft_endpoints": True,
          #   "publish_internet_endpoints": True
          # },
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
          },
          "enable_https_traffic_only": True
        }
        result = self.mgmt_client.storage_accounts.create(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        result = result.result()

        # PutFileServices[put]
        BODY = {
          "cors": {
            "cors_rules": [
              {
                "allowed_origins": [
                  "http://www.contoso.com",
                  "http://www.fabrikam.com"
                ],
                "allowed_methods": [
                  "GET",
                  "HEAD",
                  "POST",
                  "OPTIONS",
                  "MERGE",
                  "PUT"
                ],
                "max_age_in_seconds": "100",
                "exposed_headers": [
                  "x-ms-meta-*"
                ],
                "allowed_headers": [
                  "x-ms-meta-abc",
                  "x-ms-meta-data*",
                  "x-ms-meta-target*"
                ]
              },
              {
                "allowed_origins": [
                  "*"
                ],
                "allowed_methods": [
                  "GET"
                ],
                "max_age_in_seconds": "2",
                "exposed_headers": [
                  "*"
                ],
                "allowed_headers": [
                  "*"
                ]
              },
              {
                "allowed_origins": [
                  "http://www.abc23.com",
                  "https://www.fabrikam.com/*"
                ],
                "allowed_methods": [
                  "GET",
                  "PUT"
                ],
                "max_age_in_seconds": "2000",
                "exposed_headers": [
                  "x-ms-meta-abc",
                  "x-ms-meta-data*",
                  "x-ms-meta-target*"
                ],
                "allowed_headers": [
                  "x-ms-meta-12345675754564*"
                ]
              }
            ]
          }
        }
        result = self.mgmt_client.file_services.set_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME, BODY["cors"])

        # PutBlobServices[put]
        BODY = {
          "cors": {
            "cors_rules": [
              {
                "allowed_origins": [
                  "http://www.contoso.com",
                  "http://www.fabrikam.com"
                ],
                "allowed_methods": [
                  "GET",
                  "HEAD",
                  "POST",
                  "OPTIONS",
                  "MERGE",
                  "PUT"
                ],
                "max_age_in_seconds": "100",
                "exposed_headers": [
                  "x-ms-meta-*"
                ],
                "allowed_headers": [
                  "x-ms-meta-abc",
                  "x-ms-meta-data*",
                  "x-ms-meta-target*"
                ]
              },
              {
                "allowed_origins": [
                  "*"
                ],
                "allowed_methods": [
                  "GET"
                ],
                "max_age_in_seconds": "2",
                "exposed_headers": [
                  "*"
                ],
                "allowed_headers": [
                  "*"
                ]
              },
              {
                "allowed_origins": [
                  "http://www.abc23.com",
                  "https://www.fabrikam.com/*"
                ],
                "allowed_methods": [
                  "GET",
                  "PUT"
                ],
                "max_age_in_seconds": "2000",
                "exposed_headers": [
                  "x-ms-meta-abc",
                  "x-ms-meta-data*",
                  "x -ms-meta-target*"
                ],
                "allowed_headers": [
                  "x-ms-meta-12345675754564*"
                ]
              }
            ]
          },
          "default_service_version": "2017-07-29",
          "delete_retention_policy": {
            "enabled": True,
            "days": "300"
          },
          "is_versioning_enabled": False,
          # TODO: unsupport
          # "change_feed": {
          #   "enabled": True
          # }
        }
        result = self.mgmt_client.blob_services.set_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

        # TODO: don't have encryption scopes
        # # StorageAccountPutEncryptionScope[put]
        # BODY = {}
        # result = self.mgmt_client.encryption_scopes.put(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME, BODY)

        MANAGEMENT_POLICY_NAME = "managementPolicy"
        # StorageAccountSetManagementPolicies[put]
        BODY = {
          "rules": [
            {
              "enabled": True,
              "name": "olcmtest",
              "type": "Lifecycle",
              "definition": {
                "filters": {
                  "blob_types": [
                    "blockBlob"
                  ],
                  "prefix_match": [
                    "olcmtestcontainer"
                  ]
                },
                "actions": {
                  "base_blob": {
                    "tier_to_cool": {
                      "days_after_modification_greater_than": "30"
                    },
                    "tier_to_archive": {
                      "days_after_modification_greater_than": "90"
                    },
                    "delete": {
                      "days_after_modification_greater_than": "1000"
                    }
                  },
                  "snapshot": {
                    "delete": {
                      "days_after_creation_greater_than": "30"
                    }
                  }
                }
              }
            }
          ]
        }
        result = self.mgmt_client.management_policies.create_or_update(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

        # PutShares[put]
        BODY = {}
        result = self.mgmt_client.file_shares.create(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME, BODY)

        """TODO: not found
        # PRIVATE_ENDPOINT_CONNECTION_NAME = "privateEndpointConnection"
        # StorageAccountPutPrivateEndpointConnection[put]
        BODY = {
          # "private_endpoint": {
          #   "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/privateEndpoints/" + PRIVATE_ENDPOINT
          # },
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "Auto-Approved"
          }
        }
        result = self.mgmt_client.private_endpoint_connections.put(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME, BODY)
        """
        blob_container = azure.mgmt.storage.models.BlobContainer(public_access=azure.mgmt.storage.models.PublicAccess.none, metadata=None)
        # PutContainers[put]
        result = self.mgmt_client.blob_containers.create(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, blob_container)

        # CreateOrUpdateImmutabilityPolicy[put]
        #BODY = {
        #  "properties": {
        #    "immutability_period_since_creation_in_days": "3",
        #    "allow_protected_append_writes": True
        #  }
        #}
        DAYS = 3
        result = self.mgmt_client.blob_containers.create_or_update_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, None, DAYS)
        ETAG = result.etag

        # DeleteImmutabilityPolicy[delete]
        result = self.mgmt_client.blob_containers.delete_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG)

        # CreateOrUpdateImmutabilityPolicy[put] again
        DAYS = 3
        result = self.mgmt_client.blob_containers.create_or_update_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, None, DAYS)
        ETAG = result.etag

        # GetImmutabilityPolicy[get]
        result = self.mgmt_client.blob_containers.get_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)

        # GetContainers[get]
        result = self.mgmt_client.blob_containers.get(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)

        # # StorageAccountGetPrivateEndpointConnection[get]
        # result = self.mgmt_client.private_endpoint_connections.get(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)

        # GetShares[get]
        result = self.mgmt_client.file_shares.get(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME)

        # StorageAccountGetManagementPolicies[get]
        result = self.mgmt_client.management_policies.get(resource_group.name, STORAGE_ACCOUNT_NAME)

        # ListContainers[get]
        result = self.mgmt_client.blob_containers.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # TODO: don't have encryption scopes
        # # StorageAccountGetEncryptionScope[get]
        # result = self.mgmt_client.encryption_scopes.get(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME)

        # ListShares[get]
        result = self.mgmt_client.file_shares.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # GetBlobServices[get]
        result = self.mgmt_client.blob_services.get_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME)

        # GetFileServices[get]
        result = self.mgmt_client.file_services.get_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME)

        # StorageAccountListPrivateLinkResources[get]
        result = self.mgmt_client.private_link_resources.list_by_storage_account(resource_group.name, STORAGE_ACCOUNT_NAME)

        # TODO: don't have encryption scopes
        # # StorageAccountEncryptionScopeList[get]
        # result = self.mgmt_client.encryption_scopes.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # ListBlobServices[get]
        result = self.mgmt_client.blob_services.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # ListFileServices[get]
        result = self.mgmt_client.file_services.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # StorageAccountGetProperties[get]
        result = self.mgmt_client.storage_accounts.get_properties(resource_group.name, STORAGE_ACCOUNT_NAME)

        # StorageAccountListByResourceGroup[get]
        result = self.mgmt_client.storage_accounts.list_by_resource_group(resource_group.name)

        LOCATION_NAME = "westeurope"
        # UsageList[get]
        result = self.mgmt_client.usages.list_by_location(LOCATION_NAME)

        # StorageAccountList[get]
        result = self.mgmt_client.storage_accounts.list()

        # SkuList[get]
        result = self.mgmt_client.skus.list()

        # OperationsList[get]
        result = self.mgmt_client.operations.list()

       

        # SetLegalHoldContainers[post]
        BODY = {
          "tags": [
            "tag1",
            "tag2",
            "tag3"
          ]
        }
        result = self.mgmt_client.blob_containers.set_legal_hold(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)

        # ClearLegalHoldContainers[post]
        BODY = {
          "tags": [
            "tag1",
            "tag2",
            "tag3"
          ]
        }
        result = self.mgmt_client.blob_containers.clear_legal_hold(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)

        # Acquire a lease on a container[post]
        BODY = {
          "action": "Acquire",
          "lease_duration": "-1"
        }
        result = self.mgmt_client.blob_containers.lease(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)
        LEASE_ID = result.lease_id

        # Break a lease on a container[post]
        BODY = {
          "action": "Break",
          "lease_id": LEASE_ID
        }
        result = self.mgmt_client.blob_containers.lease(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)

        # UpdateContainers[patch]
        BODY = {
          "public_access": "Container",
          "metadata": {
            "metadata": "true"
          }
        }
        blob_container = azure.mgmt.storage.models.BlobContainer(public_access=BODY["public_access"], metadata=BODY["metadata"])
        result = self.mgmt_client.blob_containers.update(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, blob_container)

        # UpdateShares[patch]
        BODY = {
          "properties": {
            "metadata": {
              "type": "image"
            }
          }
        }
        result = self.mgmt_client.file_shares.update(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME, BODY)

        # TODO: don't have encryption scopes
        # # StorageAccountPatchEncryptionScope[patch]
        # BODY = {
        #   "source": "Microsoft.KeyVault",
        #   "key_vault_properties": {
        #     "key_uri": "https://testvault.vault.core.windows.net/keys/key1/863425f1358359c"
        #   }
        # }
        # result = self.mgmt_client.encryption_scopes.patch(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME, BODY)

        # StorageAccountRevokeUserDelegationKeys[post]
        result = self.mgmt_client.storage_accounts.revoke_user_delegation_keys(resource_group.name, STORAGE_ACCOUNT_NAME)

        # # TODO: FeatureUnavailableInLocation
        # # # BlobRangesRestore[post]
        # time_to_restore = (dt.datetime.now(tz=UTC()) - dt.timedelta(minutes=10)).isoformat()
        # BODY = {
        #   "time_to_restore": time_to_restore,
        #   "blob_ranges": [
        #     {
        #       "start_range": "container/blobpath1",
        #       "end_range": "container/blobpath2"
        #     },
        #     {
        #       "start_range": "container2/blobpath3",
        #       "end_range": ""
        #     }
        #   ]
        # }
        # result = self.mgmt_client.storage_accounts.restore_blob_ranges(resource_group.name, STORAGE_ACCOUNT_NAME, BODY["time_to_restore"], BODY["blob_ranges"])
        # result = result.result()

        # # TODO: Wrong parameters
        # StorageAccountListServiceSAS[post]
        # signed_expiry = (dt.datetime.now(tz=UTC()) - dt.timedelta(days=2)).isoformat()
        # BODY = {
        #   "canonicalized_resource": "/blob/sto1299/music",
        #   "signed_resource": "c",
        #   "signed_permission": "l",
        #   "signed_expiry": signed_expiry
        # }
        # result = self.mgmt_client.storage_accounts.list_service_sas(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

        # TODO: Wrong parameters
        # # StorageAccountListAccountSAS[post]
        # signed_start = dt.datetime.now(tz=UTC()).isoformat()
        # BODY = {
        #   "signed_services": "b",
        #   "signed_resource_types": "s",
        #   "signed_permission": "r",
        #   "signed_protocol": "https,http",
        #   "signed_start": signed_start,
        #   "signed_expiry": signed_expiry,
        #   "key_to_sign": "key1"
        # }
        # result = self.mgmt_client.storage_accounts.list_account_sas(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

        # StorageAccountRegenerateKey[post]
        # BODY = {
        #   "key_name": "key2"
        # }
        KEY_NAME = "key2"
        result = self.mgmt_client.storage_accounts.regenerate_key(resource_group.name, STORAGE_ACCOUNT_NAME, KEY_NAME)

        """ TODO: Key name kerb2 is not valid.
        # StorageAccountRegenerateKerbKey[post]
        # BODY = {
        #   "key_name": "kerb2"
        # }
        KEY_NAME = "kerb2"
        result = self.mgmt_client.storage_accounts.regenerate_key(resource_group.name, STORAGE_ACCOUNT_NAME, KEY_NAME)
        """

        # StorageAccountListKeys[post]
        result = self.mgmt_client.storage_accounts.list_keys(resource_group.name, STORAGE_ACCOUNT_NAME)

        # """ TODO: FeatureUnavailableInLocation
        # # StorageAccountEnableAD[patch]
        # BODY = {
        #   "azure_files_identity_based_authentication": {
        #     "directory_service_options": "AD",
        #     "active_directory_properties": {
        #       "domain_name": "adtest.com",
        #       "net_bios_domain_name": "adtest.com",
        #       "forest_name": "adtest.com",
        #       "domain_guid": "aebfc118-9fa9-4732-a21f-d98e41a77ae1",
        #       "domain_sid": "S-1-5-21-2400535526-2334094090-2402026252",
        #       "azure_storage_sid": "S-1-5-21-2400535526-2334094090-2402026252-0012"
        #     }
        #   }
        # }
        # result = self.mgmt_client.storage_accounts.update(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        # """

        # StorageAccountUpdate[patch]
        BODY = {
          "network_acls": {
            "default_action": "Allow"
          },
          # TODO: Message: Routing Preferences is not supported for the account.
          # "routing_preference": {
          #   "routing_choice": "MicrosoftRouting",
          #   "publish_microsoft_endpoints": True,
          #   "publish_internet_endpoints": True
          # },
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
          }
        }
        result = self.mgmt_client.storage_accounts.update(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

        # StorageAccountFailover
        # result = self.mgmt_client.storage_accounts.failover(resource_group.name, STORAGE_ACCOUNT_NAME)
        # result = result.result()

        # LockImmutabilityPolicy[post]
        result = self.mgmt_client.blob_containers.lock_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG)
        ETAG = result.etag

        # ExtendImmutabilityPolicy[post]
        # BODY = {
        #   "properties": {
        #     "immutability_period_since_creation_in_days": "100"
        #   }
        # }
        DAYS = 100
        result = self.mgmt_client.blob_containers.extend_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG, DAYS)
        ETAG = result.etag

        # StorageAccountCheckNameAvailability[post]
        # BODY = {
        #   "name": "sto3363",
        #   "type": "Microsoft.Storage/storageAccounts"
        # }
        NAME = "sto3363"
        result = self.mgmt_client.storage_accounts.check_name_availability(NAME)

        # DeleteContainers[delete]
        result = self.mgmt_client.blob_containers.delete(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)

        # # StorageAccountDeletePrivateEndpointConnection[delete]
        # result = self.mgmt_client.private_endpoint_connections.delete(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)

        # DeleteShares[delete]
        result = self.mgmt_client.file_shares.delete(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME)

        # StorageAccountDeleteManagementPolicies[delete]
        result = self.mgmt_client.management_policies.delete(resource_group.name, STORAGE_ACCOUNT_NAME)

        # StorageAccountDelete[delete]
        result = self.mgmt_client.storage_accounts.delete(resource_group.name, STORAGE_ACCOUNT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
