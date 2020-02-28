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

# current methods coverage: 20

import unittest

import azure.mgmt.storage
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtStorageTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtStorageTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.storage.StorageManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_storage(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        STORAGE_ACCOUNT_NAME = "storageaccountxxyyzz"
        FILE_SERVICE_NAME = "fileservicexxyyzz"
        BLOB_SERVICE_NAME = "blobservicexxyyzz"
        ENCRYPTION_SCOPE_NAME = "encryptionscopexxyyzz"

        # StorageAccountCreate[put]
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
          "kind": "Storage",
          "location": "eastus",

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
          "is_versioning_enabled": True,
          # TODO: unsupport
          # "change_feed": {
          #   "enabled": True
          # }
        }
        result = self.mgmt_client.blob_services.set_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

        # # StorageAccountPutEncryptionScope[put]
        # BODY = {}
        # result = self.mgmt_client.encryption_scopes.put(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME, BODY)

        """ Not Allow
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
        """

        # # PutShares[put]
        # BODY = {}
        # result = self.mgmt_client.file_shares.create(resource_group.name, STORAGE_ACCOUNT_NAME, FILE_SERVICE_NAME, SHARE_NAME, BODY)

        """TODO: not found
        PRIVATE_ENDPOINT_CONNECTION_NAME = "privateEndpointConnection"
        # StorageAccountPutPrivateEndpointConnection[put]
        BODY = {
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "Auto-Approved"
          }
        }
        result = self.mgmt_client.private_endpoint_connections.put(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME, BODY)
        """

        """
        # PutContainers[put]
        BODY = {}
        result = self.mgmt_client.blob_containers.create(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, BODY)

        # CreateOrUpdateImmutabilityPolicy[put]
        BODY = {
          "properties": {
            "immutability_period_since_creation_in_days": "3",
            "allow_protected_append_writes": True
          }
        }
        result = self.mgmt_client.blob_containers.create_or_update_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, IMMUTABILITY_POLICY_NAME, BODY)

        # GetImmutabilityPolicy[get]
        result = self.mgmt_client.blob_containers.get_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, IMMUTABILITY_POLICY_NAME)

        # GetContainers[get]
        result = self.mgmt_client.blob_containers.get(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME)
        """

        # # StorageAccountGetPrivateEndpointConnection[get]
        # result = self.mgmt_client.private_endpoint_connections.get(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)

        # # GetShares[get]
        # result = self.mgmt_client.file_shares.get(resource_group.name, STORAGE_ACCOUNT_NAME, FILE_SERVICE_NAME, SHARE_NAME)

        # # StorageAccountGetManagementPolicies[get]
        # result = self.mgmt_client.management_policies.get(resource_group.name, STORAGE_ACCOUNT_NAME)

        # ListContainers[get]
        result = self.mgmt_client.blob_containers.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # # StorageAccountGetEncryptionScope[get]
        # result = self.mgmt_client.encryption_scopes.get(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME)

        # ListShares[get]
        result = self.mgmt_client.file_shares.list(resource_group.name, STORAGE_ACCOUNT_NAME)

        # GetBlobServices[get]
        result = self.mgmt_client.blob_services.get_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME)

        # GetFileServices[get]
        result = self.mgmt_client.file_services.get_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME)

        # # StorageAccountListPrivateLinkResources[get]
        # result = self.mgmt_client.private_link_resources.list_by_storage_account(resource_group.name, STORAGE_ACCOUNT_NAME)

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

        LOCATION_NAME = "eastus"
        # UsageList[get]
        result = self.mgmt_client.usages.list_by_location(LOCATION_NAME)

        # StorageAccountList[get]
        result = self.mgmt_client.storage_accounts.list()

        # SkuList[get]
        result = self.mgmt_client.skus.list()

        # OperationsList[get]
        result = self.mgmt_client.operations.list()

        # # ExtendImmutabilityPolicy[post]
        # BODY = {
        #   "properties": {
        #     "immutability_period_since_creation_in_days": "100"
        #   }
        # }
        # result = self.mgmt_client.blob_containers.extend_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, IMMUTABILITY_POLICY_NAME, BODY)

        # # LockImmutabilityPolicy[post]
        # result = self.mgmt_client.blob_containers.lock_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, IMMUTABILITY_POLICY_NAME)

        # # ClearLegalHoldContainers[post]
        # BODY = {
        #   "tags": [
        #     "tag1",
        #     "tag2",
        #     "tag3"
        #   ]
        # }
        # result = self.mgmt_client.blob_containers.clear_legal_hold(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, BODY)

        # # SetLegalHoldContainers[post]
        # BODY = {
        #   "tags": [
        #     "tag1",
        #     "tag2",
        #     "tag3"
        #   ]
        # }
        # result = self.mgmt_client.blob_containers.set_legal_hold(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, BODY)

        """
        # Break a lease on a container[post]
        BODY = {
          "action": "Break",
          "lease_id": "8698f513-fa75-44a1-b8eb-30ba336af27d"
        }
        result = self.mgmt_client.blob_containers.lease(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, BODY)

        # Acquire a lease on a container[post]
        BODY = {
          "action": "Acquire",
          "lease_duration": "-1"
        }
        result = self.mgmt_client.blob_containers.lease(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, BODY)

        # UpdateContainers[patch]
        BODY = {
          "properties": {
            "public_access": "Container",
            "metadata": {
              "metadata": "true"
            }
          }
        }
        result = self.mgmt_client.blob_containers.update(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, BODY)
        """

        # # UpdateShares[patch]
        # BODY = {
        #   "properties": {
        #     "metadata": {
        #       "type": "image"
        #     }
        #   }
        # }
        # result = self.mgmt_client.file_shares.update(resource_group.name, STORAGE_ACCOUNT_NAME, FILE_SERVICE_NAME, SHARE_NAME, BODY)

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

        # TODO: FIX LATER
        # # BlobRangesRestore[post]
        # BODY = {
        #   "time_to_restore": "2019-04-20T15:30:00Z",
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
        # result = self.mgmt_client.storage_accounts.restore_blob_ranges(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        # result = result.result()

        """ TODO: fix later
        # StorageAccountListServiceSAS[post]
        BODY = {
          "canonicalized_resource": "/blob/sto1299/music",
          "signed_resource": "c",
          "signed_permission": "l",
          "signed_expiry": "2017-05-24T11:32:48.8457197Z"
        }
        result = self.mgmt_client.storage_accounts.list_service_sas(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)

        # StorageAccountListAccountSAS[post]
        BODY = {
          "signed_services": "b",
          "signed_resource_types": "s",
          "signed_permission": "r",
          "signed_protocol": "https,http",
          "signed_start": "2017-05-24T10:42:03.1567373Z",
          "signed_expiry": "2017-05-24T11:42:03.1567373Z",
          "key_to_sign": "key1"
        }
        result = self.mgmt_client.storage_accounts.list_account_sas(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        """

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

        # StorageAccountListKeys[post]
        result = self.mgmt_client.storage_accounts.list_keys(resource_group.name, STORAGE_ACCOUNT_NAME)
        """

        """TODO: DELETE LATER
        # StorageAccountCreate[put]
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
          "kind": "Storage",
          "location": "eastus",
          "is_hns_enabled": True,
          "routing_preference": {
            "routing_choice": "MicrosoftRouting",
            "publish_microsoft_endpoints": True,
            "publish_internet_endpoints": True
          },
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
        result = self.mgmt_client.storage_accounts.create(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        result = result.result()
        """

        """ TODO:
        E           msrestazure.azure_exceptions.CloudError: Azure Error: FeatureUnavailableInLocation
        E           Message: A feature was requested which is not yet available in this location.
        # StorageAccountEnableAD[patch]
        BODY = {
          "azure_files_identity_based_authentication": {
            "directory_service_options": "AD",
            "active_directory_properties": {
              "domain_name": "adtest.com",
              "net_bios_domain_name": "adtest.com",
              "forest_name": "adtest.com",
              "domain_guid": "aebfc118-9fa9-4732-a21f-d98e41a77ae1",
              "domain_sid": "S-1-5-21-2400535526-2334094090-2402026252",
              "azure_storage_sid": "S-1-5-21-2400535526-2334094090-2402026252-0012"
            }
          }
        }
        result = self.mgmt_client.storage_accounts.update(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        """

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

        # StorageAccountCheckNameAvailability[post]
        # BODY = {
        #   "name": "sto3363",
        #   "type": "Microsoft.Storage/storageAccounts"
        # }
        NAME = "sto3363"
        result = self.mgmt_client.storage_accounts.check_name_availability(NAME)

        # # DeleteImmutabilityPolicy[delete]
        # result = self.mgmt_client.blob_containers.delete_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME, IMMUTABILITY_POLICY_NAME)

        # # DeleteContainers[delete]
        # result = self.mgmt_client.blob_containers.delete(resource_group.name, STORAGE_ACCOUNT_NAME, BLOB_SERVICE_NAME, CONTAINER_NAME)

        # # StorageAccountDeletePrivateEndpointConnection[delete]
        # result = self.mgmt_client.private_endpoint_connections.delete(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)

        # # DeleteShares[delete]
        # result = self.mgmt_client.file_shares.delete(resource_group.name, STORAGE_ACCOUNT_NAME, FILE_SERVICE_NAME, SHARE_NAME)

        # # StorageAccountDeleteManagementPolicies[delete]
        # result = self.mgmt_client.management_policies.delete(resource_group.name, STORAGE_ACCOUNT_NAME)

        # StorageAccountDelete[delete]
        result = self.mgmt_client.storage_accounts.delete(resource_group.name, STORAGE_ACCOUNT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
