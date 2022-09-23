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

# current methods coverage:
#   blob_containers: 13/13
#   blob_services:  3/3
#   encryption_scopes:  4/4
#   file_services: 3/3
#   file_shares:  5/5
#   management_policies:  3/3
#   operations:  1/1
#   object_replication_policies_operations: 0/4
#   private_endpoint_connections:  3/3
#   private_link_resources:  1/1
#   skus:  1/1
#   storage_accounts:  10/14
#   usages:  1/1

import datetime as dt
import unittest

import azure.mgmt.storage as az_storage
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'westeurope'
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
        self.re_replacer.register_pattern_pair('"value":".{88}"', '"value":"FakeValue"')
        self.mgmt_client = self.create_mgmt_client(
            az_storage.StorageManagementClient
        )

        if self.is_live:
            import azure.mgmt.network as az_network
            self.network_client = self.create_mgmt_client(
              az_network.NetworkManagementClient
            )

    def create_endpoint(self, group_name, location, vnet_name, sub_net, endpoint_name, resource_id):
        if self.is_live:
            # Create VNet
            async_vnet_creation = self.network_client.virtual_networks.begin_create_or_update(
                group_name,
                vnet_name,
                {
                    'location': location,
                    'address_space': {
                        'address_prefixes': ['10.0.0.0/16']
                    }
                }
            )
            async_vnet_creation.result()

            # Create Subnet
            async_subnet_creation = self.network_client.subnets.begin_create_or_update(
                group_name,
                vnet_name,
                sub_net,
                {
                  'address_prefix': '10.0.0.0/24',
                  'private_link_service_network_policies': 'disabled',
                  'private_endpoint_network_policies': 'disabled'
                }
            )
            subnet_info = async_subnet_creation.result()

            # Create private endpoint
            BODY = {
              "location": location,
              "properties": {
                "privateLinkServiceConnections": [
                  {
                    "name": "myconnection",
                    # "private_link_service_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + group_name + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + ""
                    "private_link_service_id": resource_id,
                    "group_ids": ["blob"]
                  }
                ],
                "subnet": {
                  "id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + sub_net
                }
              }
            }
            result = self.network_client.private_endpoints.begin_create_or_update(group_name, endpoint_name, BODY)

            return result.result().id
        else:
            return "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/" + group_name + "/providers/Microsoft.Network/privateEndpoints/" + endpoint_name

    @unittest.skip("skip test")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_storage(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        STORAGE_ACCOUNT_NAME = "storageaccountxxyyzzccc"  # TODO: need change a random name, if need run live test again.
        DEST_STORAGE_ACCOUNT_NAME = "storageaccountxxyyzznnccc"
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
        PRIVATE_ENDPOINT = "endpoint123xxx"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "privateEndpointConnection"
        OBJECT_REPLICATION_POLICY_NAME = "default"

        # StorageAccountCreate[put]
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
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
          }
        }
        result = self.mgmt_client.storage_accounts.begin_create(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        storageaccount = result.result()

        # Create destination storage account
        # result = self.mgmt_client.storage_accounts.begin_create(resource_group.name, DEST_STORAGE_ACCOUNT_NAME, BODY)

        # TODO: [Kaihui] feature is unavailable
        # Create object replication policy
        # BODY = {
        #   "source_account": STORAGE_ACCOUNT_NAME,
        #   "destination_account": DEST_STORAGE_ACCOUNT_NAME,
        #   "rules": []
        # }
        # result = self.mgmt_client.object_replication_policies.create_or_update(resource_group.name, STORAGE_ACCOUNT_NAME, OBJECT_REPLICATION_POLICY_NAME, BODY)

        self.create_endpoint(
          resource_group.name,
          AZURE_LOCATION,
          VNET_NAME,
          SUB_NET,
          PRIVATE_ENDPOINT,
          storageaccount.id
        )

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
          # "is_versioning_enabled": True,
          # TODO: unsupport
          # "change_feed": {
          #   "enabled": True
          # }
        }
        result = self.mgmt_client.blob_services.set_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

        # StorageAccountPutEncryptionScope[put]
        BODY = {
          "source": "Microsoft.Storage",
          "state": "Enabled"
        }
        result = self.mgmt_client.encryption_scopes.put(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME, BODY)

        MANAGEMENT_POLICY_NAME = "managementPolicy"
        # StorageAccountSetManagementPolicies[put]
        BODY = {
          "policy": {
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
        }
        result = self.mgmt_client.management_policies.create_or_update(resource_group.name, STORAGE_ACCOUNT_NAME, "default", BODY)

        # PutShares[put]
        # result = self.mgmt_client.file_shares.create(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME, {})

        # StorageAccountGetProperties[get]
        storageaccount = self.mgmt_client.storage_accounts.get_properties(resource_group.name, STORAGE_ACCOUNT_NAME)

        # PRIVATE_ENDPOINT_CONNECTION_NAME = "privateEndpointConnection"
        PRIVATE_ENDPOINT_CONNECTION_NAME = storageaccount.private_endpoint_connections[0].name
        # StorageAccountPutPrivateEndpointConnection[put]
        BODY = {
          "private_link_service_connection_state": {
            # "status": "Approved",
            "status": "Rejected",  # it has been approved, so test `Rejected`
            "description": "Auto-Approved"
          }
        }
        result = self.mgmt_client.private_endpoint_connections.put(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME, BODY)

        # PutContainers[put]
        result = self.mgmt_client.blob_containers.create(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, {})

        # CreateOrUpdateImmutabilityPolicy[put]
        BODY = {
          "immutability_period_since_creation_in_days": "3",
          "allow_protected_append_writes": True
        }
        result = self.mgmt_client.blob_containers.create_or_update_immutability_policy(
          resource_group.name,
          STORAGE_ACCOUNT_NAME,
          CONTAINER_NAME,
          parameters=BODY)
        ETAG = result.etag

        # DeleteImmutabilityPolicy[delete]
        result = self.mgmt_client.blob_containers.delete_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG)

        # CreateOrUpdateImmutabilityPolicy[put] again
        BODY = {
          "immutability_period_since_creation_in_days": "3",
          "allow_protected_append_writes": True
        }
        result = self.mgmt_client.blob_containers.create_or_update_immutability_policy(
          resource_group.name,
          STORAGE_ACCOUNT_NAME,
          CONTAINER_NAME,
          parameters=BODY)
        ETAG = result.etag

        # TODO: [Kaihui] feature is unavailable
        # Get object replication policy
        # result = self.mgmt_client.object_replication_policies.get(resource_group.name, STORAGE_ACCOUNT_NAME, OBJECT_REPLICATION_POLICY_NAME)

        # GetImmutabilityPolicy[get]
        result = self.mgmt_client.blob_containers.get_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)

        # GetContainers[get]
        result = self.mgmt_client.blob_containers.get(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)

        # StorageAccountGetPrivateEndpointConnection[get]
        result = self.mgmt_client.private_endpoint_connections.get(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)

        # GetShares[get]
        # result = self.mgmt_client.file_shares.get(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME)

        # StorageAccountGetManagementPolicies[get]
        result = self.mgmt_client.management_policies.get(resource_group.name, STORAGE_ACCOUNT_NAME, "default")

        # ListContainers[get]
        result = self.mgmt_client.blob_containers.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # StorageAccountGetEncryptionScope[get]
        result = self.mgmt_client.encryption_scopes.get(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME)

        # ListShares[get]
        # result = self.mgmt_client.file_shares.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # GetBlobServices[get]
        result = self.mgmt_client.blob_services.get_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME)

        # GetFileServices[get]
        result = self.mgmt_client.file_services.get_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME)

        # StorageAccountListPrivateLinkResources[get]
        result = self.mgmt_client.private_link_resources.list_by_storage_account(resource_group.name, STORAGE_ACCOUNT_NAME)

        # StorageAccountEncryptionScopeList[get]
        result = self.mgmt_client.encryption_scopes.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # TODO: [Kaihui] feature is unavailable
        # List object replication policy
        # result = self.mgmt_client.object_replication_policies.list(resource_group.name, STORAGE_ACCOUNT_NAME)

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
        result = self.mgmt_client.blob_containers.update(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)

        # UpdateShares[patch]
        BODY = {
          "properties": {
            "metadata": {
              "type": "image"
            }
          }
        }
        # result = self.mgmt_client.file_shares.update(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME, BODY)

        # StorageAccountPatchEncryptionScope[patch]
        # BODY = {
        #   "source": "Microsoft.KeyVault",
        #   "key_vault_properties": {
        #     "key_uri": "https://testvault.vault.core.windows.net/keys/key1/863425f1358359c"
        #   }
        # }
        BODY = {
          "source": "Microsoft.Storage",
          "state": "Enabled"
        }
        result = self.mgmt_client.encryption_scopes.patch(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME, BODY)

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
        BODY = {
          "key_name": "key2"
        }
        result = self.mgmt_client.storage_accounts.regenerate_key(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

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
        # [ZIM] tis testcase fails
        # TODO: [Kaihui] about this issue: https://github.com/Azure/azure-sdk-for-python/issues/11292
        # result = self.mgmt_client.storage_accounts.begin_failover(resource_group.name, STORAGE_ACCOUNT_NAME)
        #result = result.result()

        # LockImmutabilityPolicy[post]
        result = self.mgmt_client.blob_containers.lock_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG)
        ETAG = result.etag

        # ExtendImmutabilityPolicy[post]
        BODY = {
          "immutability_period_since_creation_in_days": "100"
        }
        result = self.mgmt_client.blob_containers.extend_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG, BODY)
        ETAG = result.etag

        # StorageAccountCheckNameAvailability[post]
        BODY = {
          "name": "sto3363",
          "type": "Microsoft.Storage/storageAccounts"
        }
        result = self.mgmt_client.storage_accounts.check_name_availability(BODY)

        # DeleteContainers[delete]
        result = self.mgmt_client.blob_containers.delete(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)

        # # StorageAccountDeletePrivateEndpointConnection[delete]
        result = self.mgmt_client.private_endpoint_connections.delete(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)

        # DeleteShares[delete]
        # result = self.mgmt_client.file_shares.delete(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME)

        # StorageAccountDeleteManagementPolicies[delete]
        result = self.mgmt_client.management_policies.delete(resource_group.name, STORAGE_ACCOUNT_NAME, "default")

        # TODO: [Kaihui] feature is unavailable
        # Delete object replication policy
        # result = self.mgmt_client.object_replication_policies.delete(resource_group.name, STORAGE_ACCOUNT_NAME, OBJECT_REPLICATION_POLICY_NAME)

        # StorageAccountDelete[delete]
        result = self.mgmt_client.storage_accounts.delete(resource_group.name, STORAGE_ACCOUNT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
