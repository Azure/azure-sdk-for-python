# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import datetime as dt
import unittest

import azure.mgmt.storage.aio as az_storage_aio
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

from _aio_testcase import AzureMgmtAsyncTestCase

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

class MgmtStorageTest(AzureMgmtAsyncTestCase):

    def setUp(self):
        super(MgmtStorageTest, self).setUp()
        self.mgmt_client = self.create_mgmt_aio_client(
            az_storage_aio.StorageManagementClient
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
        

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_storage(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        STORAGE_ACCOUNT_NAME = "storageaccountxxyyzznzn"  # TODO: need change a random name, if need run live test again.
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

        # StorageAccountCreate[put]
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
          "kind": "StorageV2",  # Storage v2 support policy
          "location": "westeurope",
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
        result = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.begin_create(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        )
        storageaccount = self.event_loop.run_until_complete(
            result.result()
        )

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
        result = self.event_loop.run_until_complete(
            self.mgmt_client.file_services.set_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME, BODY["cors"])
        )

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
          }
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_services.set_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        )

        # StorageAccountPutEncryptionScope[put]
        BODY = {
          "source": "Microsoft.Storage",
          "state": "Enabled"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.encryption_scopes.put(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME, BODY)
        )

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
        result = self.event_loop.run_until_complete(
            self.mgmt_client.management_policies.create_or_update(resource_group.name, STORAGE_ACCOUNT_NAME, "default", BODY)
        )

        # PutShares[put]
        # result = self.event_loop.run_until_complete(
        #     self.mgmt_client.file_shares.create(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME, {})
        # )

        # StorageAccountGetProperties[get]
        storageaccount = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.get_properties(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

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
        result = self.event_loop.run_until_complete(
            self.mgmt_client.private_endpoint_connections.put(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME, BODY)
        )

        # PutContainers[put]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.create(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, {})
        )

        # CreateOrUpdateImmutabilityPolicy[put]
        BODY = {
          "immutability_period_since_creation_in_days": "3",
          "allow_protected_append_writes": True
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.create_or_update_immutability_policy(
                resource_group.name,
                STORAGE_ACCOUNT_NAME,
                CONTAINER_NAME,
                parameters=BODY)
        )
        ETAG = result.etag

        # DeleteImmutabilityPolicy[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.delete_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG)
        )

        # CreateOrUpdateImmutabilityPolicy[put] again
        BODY = {
          "immutability_period_since_creation_in_days": "3",
          "allow_protected_append_writes": True
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.create_or_update_immutability_policy(
              resource_group.name,
              STORAGE_ACCOUNT_NAME,
              CONTAINER_NAME,
              parameters=BODY)
        )
        ETAG = result.etag

        # GetImmutabilityPolicy[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.get_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)
        )

        # GetContainers[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.get(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)
        )

        # StorageAccountGetPrivateEndpointConnection[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.private_endpoint_connections.get(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)
        )

        # GetShares[get]
        # result = self.event_loop.run_until_complete(
        #     self.mgmt_client.file_shares.get(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME)
        # )

        # StorageAccountGetManagementPolicies[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.management_policies.get(resource_group.name, STORAGE_ACCOUNT_NAME, "default")
        )

        # ListContainers[get]
        result = self.to_list(
            self.mgmt_client.blob_containers.list(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # # StorageAccountGetEncryptionScope[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.encryption_scopes.get(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME)
        )

        # ListShares[get]
        # result = self.to_list(
        #     self.mgmt_client.file_shares.list(resource_group.name, STORAGE_ACCOUNT_NAME)
        # )

        # GetBlobServices[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_services.get_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # GetFileServices[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.file_services.get_service_properties(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # StorageAccountListPrivateLinkResources[get]
        # TODO: [Kaihui] Why this `list` operation doesn't return AsyncIterable like other list operation.
        result = self.event_loop.run_until_complete(
            self.mgmt_client.private_link_resources.list_by_storage_account(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # StorageAccountEncryptionScopeList[get]
        result = self.to_list(
            self.mgmt_client.encryption_scopes.list(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # ListBlobServices[get]
        result = self.to_list(
            self.mgmt_client.blob_services.list(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # ListFileServices[get]
        # TODO: [Kaihui] Why this `list` operation doesn't return AsyncIterable like other list operation.
        result = self.event_loop.run_until_complete(
            self.mgmt_client.file_services.list(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # StorageAccountGetProperties[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.get_properties(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # StorageAccountListByResourceGroup[get]
        result = self.to_list(
            self.mgmt_client.storage_accounts.list_by_resource_group(resource_group.name)
        )

        LOCATION_NAME = "westeurope"
        # UsageList[get]
        result = self.to_list(
            self.mgmt_client.usages.list_by_location(LOCATION_NAME)
        )

        # StorageAccountList[get]
        result = self.to_list(
            self.mgmt_client.storage_accounts.list()
        )

        # SkuList[get]
        result = self.to_list(
            self.mgmt_client.skus.list()
        )

        # OperationsList[get]
        result = self.to_list(
            self.mgmt_client.operations.list()
        )

        # SetLegalHoldContainers[post]
        BODY = {
          "tags": [
            "tag1",
            "tag2",
            "tag3"
          ]
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.set_legal_hold(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)
        )

        # ClearLegalHoldContainers[post]
        BODY = {
          "tags": [
            "tag1",
            "tag2",
            "tag3"
          ]
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.clear_legal_hold(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)
        )

        # Acquire a lease on a container[post]
        BODY = {
          "action": "Acquire",
          "lease_duration": "-1"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.lease(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)
        )
        LEASE_ID = result.lease_id

        # Break a lease on a container[post]
        BODY = {
          "action": "Break",
          "lease_id": LEASE_ID
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.lease(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)
        )

        # UpdateContainers[patch]
        BODY = {
          "public_access": "Container",
          "metadata": {
            "metadata": "true"
          }
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.update(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BODY)
        )

        # UpdateShares[patch]
        BODY = {
          "properties": {
            "metadata": {
              "type": "image"
            }
          }
        }
        # result = self.event_loop.run_until_complete(
        #     self.mgmt_client.file_shares.update(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME, BODY)
        # )

        # # StorageAccountPatchEncryptionScope[patch]
        BODY = {
          "source": "Microsoft.Storage",
          "state": "Enabled"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.encryption_scopes.patch(resource_group.name, STORAGE_ACCOUNT_NAME, ENCRYPTION_SCOPE_NAME, BODY)
        )

        # StorageAccountRevokeUserDelegationKeys[post]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.revoke_user_delegation_keys(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # StorageAccountRegenerateKey[post]
        BODY = {
          "key_name": "key2"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.regenerate_key(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        )

        # StorageAccountListKeys[post]
        # Why this `list` operation doesn't return AsyncIterable like other list operation.
        result = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.list_keys(resource_group.name, STORAGE_ACCOUNT_NAME)
        )

        # StorageAccountUpdate[patch]
        BODY = {
          "network_acls": {
            "default_action": "Allow"
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
          }
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.update(resource_group.name, STORAGE_ACCOUNT_NAME, BODY)
        )

        # LockImmutabilityPolicy[post]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.lock_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG)
        )
        ETAG = result.etag

        # ExtendImmutabilityPolicy[post]
        BODY = {
          "immutability_period_since_creation_in_days": "100"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.extend_immutability_policy(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, ETAG, BODY)
        )
        ETAG = result.etag

        # StorageAccountCheckNameAvailability[post]
        BODY = {
          "name": "sto3363",
          "type": "Microsoft.Storage/storageAccounts"
        }
        result = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.check_name_availability(BODY)
        )

        # DeleteContainers[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.blob_containers.delete(resource_group.name, STORAGE_ACCOUNT_NAME, CONTAINER_NAME)
        )

        # # StorageAccountDeletePrivateEndpointConnection[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.private_endpoint_connections.delete(resource_group.name, STORAGE_ACCOUNT_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)
        )

        # DeleteShares[delete]
        # result = self.event_loop.run_until_complete(
        #     self.mgmt_client.file_shares.delete(resource_group.name, STORAGE_ACCOUNT_NAME, SHARE_NAME)
        # )

        # StorageAccountDeleteManagementPolicies[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.management_policies.delete(resource_group.name, STORAGE_ACCOUNT_NAME, "default")
        )

        # StorageAccountDelete[delete]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.storage_accounts.delete(resource_group.name, STORAGE_ACCOUNT_NAME)
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
