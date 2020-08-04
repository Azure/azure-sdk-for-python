# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 37
# Methods Covered : 37
# Examples Total  : 42
# Examples Tested : 42
# Coverage %      : 100
# ----------------------

# Current Operation Coverage:
#   OpenShiftManagedClusters: 2/6
#   ContainerServices: 2/6
#   Operations: 1/1
#   ManagedClusters: 9/14
#   AgentPools: 0/6
#   PrivateEndpointConnections: 0/4

import unittest

import azure.mgmt.containerservice
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtContainerServiceClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtContainerServiceClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.containerservice.ContainerServiceClient
        )

    # @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)  # ISSUE:  node resource group name is too long
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_containerservice(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        CLIENT_ID = self.settings.CLIENT_ID or "123"
        CLIENT_SECRET = self.settings.CLIENT_SECRET or "123"
        CLIENT_OID = self.settings.CLIENT_OID if self.is_live else "000"
        KEY_VAULT_NAME = self.get_resource_name("keyvaultxmm")
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "myResource"
        CONTAINER_SERVICE_NAME = "myContainerService"
        UPGRADE_PROFILE_NAME = "myUpgradeProfile"
        ROLE_NAME = "myRole"
        DISK_ENCRYPTION_SET_NAME = "myDiskEncryptionSet"
        # MICROSOFT.COMPUTE_NAME = "myMicrosoftCompute"
        AGENT_POOL_NAME = "myAgentPool"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "myPrivateEndpointConnection"
        KEYDATA = self.settings.KEYDATA if self.is_live else "keydata"

#--------------------------------------------------------------------------
        # /ManagedClusters/put/Create/Update Managed Cluster[put]
#--------------------------------------------------------------------------

        # Create sample managed cluster

        BODY = {
          "dns_prefix": "akspythonsdk",
          "agent_pool_profiles": [
              {
                  "name": "aksagent",
                  "count": 1,
                  "vm_size": "Standard_DS2_v2",
                  "max_pods": 110,
                  "min_count": 1,
                  "max_count": 100,
                  "os_type": "Linux",
                  "type": "VirtualMachineScaleSets",
                  "enable_auto_scaling": True,
                  "mode": "System",
                  "node_image_version": "AKSUbuntu-1604-2020.06.301"
              }
          ],
          "service_principal_profile": {
              "client_id": CLIENT_ID,
              "secret": CLIENT_SECRET
          },
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedClusters/put/Create Managed Cluster with PPG[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "tier": "production",
            "archv2": ""
          },
          "sku": {
            "name": "Basic",
            "tier": "Free"
          },
          "kubernetes_version": "",
          "dns_prefix": "dnsprefix1",
          "agent_pool_profiles": [
            {
              "name": "nodepool1",
              "count": "3",
              "vm_size": "Standard_DS2_v2",
              "os_type": "Linux",
              "type": "VirtualMachineScaleSets",
              "enable_node_public_ip": True,
              "mode": "System",
              "node_image_version": "AKSUbuntu:1604:2020.03.11",
              # "proximity_placement_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers//Microsoft.Compute/" + MICROSOFT.COMPUTE_NAME + "/ppg1"
            }
          ],
          "linux_profile": {
            "admin_username": "azureuser",
            "ssh": {
              "public_keys": [
                {
                  "key_data": "keydata"
                }
              ]
            }
          },
          "network_profile": {
            "load_balancer_sku": "standard",
            "outbound_type": "loadBalancer",
            "load_balancer_profile": {
              "managed_outbound_ips": {
                "count": "2"
              }
            }
          },
          "auto_scaler_profile": {
            "scan-interval": "20s",
            "scale-down-delay-after-add": "15m"
          },
          "windows_profile": {
            "admin_username": "azureuser",
            "admin_password": "replacePassword1234$"
          },
          "service_principal_profile": {
            "client_id": "clientid",
            "secret": "secret"
          },
          "enable_rbac": True,
          "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME,
          "enable_pod_security_policy": True
        }
        # result = self.mgmt_client.managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ManagedClusters/put/Create/Update AAD Managed Cluster with EnableAzureRBAC[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "tier": "production",
            "archv2": ""
          },
          "sku": {
            "name": "Basic",
            "tier": "Free"
          },
          "kubernetes_version": "",
          "dns_prefix": "dnsprefix1",
          "agent_pool_profiles": [
            {
              "name": "nodepool1",
              "count": "3",
              "vm_size": "Standard_DS1_v2",
              "os_type": "Linux",
              "type": "VirtualMachineScaleSets",
              "availability_zones": [
                "1",
                "2",
                "3"
              ],
              "enable_node_public_ip": True,
              "mode": "System",
              "node_image_version": "AKSUbuntu:1604:2020.03.11"
            }
          ],
          "linux_profile": {
            "admin_username": "azureuser",
            "ssh": {
              "public_keys": [
                {
                  "key_data": "keydata"
                }
              ]
            }
          },
          "network_profile": {
            "load_balancer_sku": "standard",
            "outbound_type": "loadBalancer",
            "load_balancer_profile": {
              "managed_outbound_ips": {
                "count": "2"
              }
            }
          },
          "auto_scaler_profile": {
            "scan-interval": "20s",
            "scale-down-delay-after-add": "15m"
          },
          "windows_profile": {
            "admin_username": "azureuser",
            "admin_password": "replacePassword1234$"
          },
          "service_principal_profile": {
            "client_id": "clientid",
            "secret": "secret"
          },
          "aad_profile": {
            "managed": True,
            "enable_azure_rbac": True
          },
          "enable_rbac": True,
          "disk_encryption_set_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/diskEncryptionSets/" + DISK_ENCRYPTION_SET_NAME,
          "enable_pod_security_policy": True
        }
        # result = self.mgmt_client.managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /OpenShiftManagedClusters/put/Create/Update OpenShift Managed Cluster[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "tier": "production",
            "archv2": ""
          },
          "open_shift_version": "v3.11",
          "network_profile": {
            "vnet_cidr": "10.0.0.0/8"
          },
          "master_pool_profile": {
            "name": "master",
            "count": "3",
            "vm_size": "Standard_D4s_v3",
            "os_type": "Linux",
            "subnet_cidr": "10.0.0.0/24"
          },
          "agent_pool_profiles": [
            {
              "name": "infra",
              "role": "infra",
              "count": 2,
              "vm_size": "Standard_D4s_v3",
              "os_type": "Linux",
              "subnet_cidr": "10.0.0.0/24"
            },
            {
              "name": "compute",
              "role": "compute",
              "count": 2,
              "vm_size": "Standard_D4s_v3",
              "os_type": "Linux",
              "subnet_cidr": "10.0.0.0/24"
            }
          ],
          "router_profiles": [
            {
              "name": "default"
            }
          ],
          "auth_profile": {
            "identity_providers": [
              {
                "name": "Azure AD",
                "provider": {
                  "kind": "AADIdentityProvider",
                  "client_id": CLIENT_ID,
                  "secret": CLIENT_SECRET,
                  "tenant_id": TENANT_ID,
                #   "customer_admin_group_id": "customerAdminGroupId"
                  "customer_admin_group_id": RESOURCE_GROUP 
                }
              }
            ]
          }
        }
        # result = self.mgmt_client.open_shift_managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ContainerServices/put/Create/Update Container Service[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "agent_pool_profiles": [
              {
                  "name": "agentx",
                  "count": 1,
                  "vm_size": "Standard_DS2_v2",
                  "os_type": "Linux",
                  "dns_prefix": "agentdnsx"
              }
          ],
          "linux_profile": {
              "ssh": {
                  "public_keys": [
                      {
                          "key_data": KEYDATA
                      }
                  ]
              },
              "admin_username": "azureuser"
          },
          "master_profile": {
              "count": 1,
              "vm_size": "Standard_A3",
              "dns_prefix": "sdkmaster"
          },
          "orchestrator_profile": {
              "orchestrator_type": "DCOS"
          },
        #   "service_principal_profile": {
        #       "client_id": CLIENT_ID,
        #       "secret": CLIENT_SECRET
        #   }
        }
        # result = self.mgmt_client.container_services.begin_create_or_update(resource_group_name=RESOURCE_GROUP, container_service_name=CONTAINER_SERVICE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /AgentPools/put/Create/Update Agent Pool[put]
#--------------------------------------------------------------------------
        # TODO: [kaihui]  (PreviewFeatureNotRegistered) Preview feature Microsoft.ContainerService/SpotPoolPreview not registered.)
        BODY = {
          "orchestrator_version": "",
          "count": "3",
          "vm_size": "Standard_DS1_v2",
          "os_type": "Linux",
          "tags": {
            "name1": "val1"
          },
          "node_labels": {
            "key1": "val1"
          },
          "node_taints": [
            "Key1=Value1:NoSchedule"
          ],
          "scale_set_priority": "Spot",
          "scale_set_eviction_policy": "Delete",
          "mode": "User"
        }
        # result = self.mgmt_client.agent_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /AgentPools/put/Update Agent Pool[put]
#--------------------------------------------------------------------------
        BODY = {
          "orchestrator_version": "",
          "count": "3",
          "enable_auto_scaling": True,
          "min_count": "2",
          "max_count": "2",
          "vm_size": "Standard_DS1_v2",
          "os_type": "Linux",
          "node_taints": [
            "Key1=Value1:NoSchedule"
          ],
          "scale_set_priority": "Spot",
          "scale_set_eviction_policy": "Delete"
        }
        # result = self.mgmt_client.agent_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /AgentPools/put/Create Spot Agent Pool[put]
#--------------------------------------------------------------------------
        BODY = {
          "orchestrator_version": "",
          "count": "3",
          "vm_size": "Standard_DS1_v2",
          "os_type": "Linux",
          "tags": {
            "name1": "val1"
          },
          "node_labels": {
            "key1": "val1"
          },
          "node_taints": [
            "Key1=Value1:NoSchedule"
          ],
          "scale_set_priority": "Spot",
          "scale_set_eviction_policy": "Delete"
        }
        # result = self.mgmt_client.agent_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /AgentPools/put/Create Agent Pool with PPG[put]
#--------------------------------------------------------------------------
        BODY = {
          "orchestrator_version": "",
          "count": "3",
          "vm_size": "Standard_DS2_v2",
          "os_type": "Linux",
          # "proximity_placement_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers//Microsoft.Compute/" + MICROSOFT.COMPUTE_NAME + "/ppg1"
        }
        # result = self.mgmt_client.agent_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/put/Update Private Endpoint Connection[put]
#--------------------------------------------------------------------------
        BODY = {
          "private_link_service_connection_state": {
            "status": "Approved"
          }
        }
        # result = self.mgmt_client.private_endpoint_connections.update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /AgentPools/get/Get Upgrade Profile for Agent Pool[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.agent_pools.get_upgrade_profile(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME, upgrade_profile_name=UPGRADE_PROFILE_NAME)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/get/Get Private Endpoint Connection[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.private_endpoint_connections.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)

#--------------------------------------------------------------------------
        # /ManagedClusters/get/Get Upgrade Profile for Managed Cluster[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_clusters.get_upgrade_profile(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

#--------------------------------------------------------------------------
        # /AgentPools/get/Get Agent Pool[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.agent_pools.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/get/List Private Endpoint Connections by Managed Cluster[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.private_endpoint_connections.list(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

#--------------------------------------------------------------------------
        # /AgentPools/get/Get available versions for agent pool[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.agent_pools.get_available_agent_pool_versions(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

#--------------------------------------------------------------------------
        # /ContainerServices/get/Get Container Service[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.container_services.get(resource_group_name=RESOURCE_GROUP, container_service_name=CONTAINER_SERVICE_NAME)

#--------------------------------------------------------------------------
        # /AgentPools/get/List Agent Pools by Managed Cluster[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.agent_pools.list(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

#--------------------------------------------------------------------------
        # /OpenShiftManagedClusters/get/Get OpenShift Managed Cluster[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.open_shift_managed_clusters.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

#--------------------------------------------------------------------------
        # /ManagedClusters/get/Get Managed Cluster[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_clusters.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

#--------------------------------------------------------------------------
        # /OpenShiftManagedClusters/get/Get Managed Clusters by Resource Group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.open_shift_managed_clusters.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /ContainerServices/get/List Container Services by Resource Group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.container_services.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /ManagedClusters/get/Get Managed Clusters by Resource Group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_clusters.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /ContainerServices/get/List Container Service Orchestrators[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.container_services.list_orchestrators(location=AZURE_LOCATION)

#--------------------------------------------------------------------------
        # /OpenShiftManagedClusters/get/List Managed Clusters[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.open_shift_managed_clusters.list()

#--------------------------------------------------------------------------
        # /ContainerServices/get/List Container Services[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.container_services.list()

#--------------------------------------------------------------------------
        # /ManagedClusters/get/List Managed Clusters[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_clusters.list()

#--------------------------------------------------------------------------
        # /Operations/get/List Operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.operations.list()

#--------------------------------------------------------------------------
        # /ManagedClusters/post/Get Managed Cluster[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_clusters.get_access_profile(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, role_name=ROLE_NAME)

#--------------------------------------------------------------------------
        # /ManagedClusters/post/Get Managed Cluster[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_clusters.get_access_profile(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, role_name=ROLE_NAME)

#--------------------------------------------------------------------------
        # /ManagedClusters/post/Reset Service Principal Profile[post]
#--------------------------------------------------------------------------
        BODY = {
          "client_id": CLIENT_ID,
          "secret": CLIENT_SECRET
        }
        result = self.mgmt_client.managed_clusters.begin_reset_service_principal_profile(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedClusters/post/Get Managed Cluster[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_clusters.get_access_profile(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, role_name=ROLE_NAME)

#--------------------------------------------------------------------------
        # /ManagedClusters/post/Rotate Cluster Certificates[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_clusters.begin_rotate_cluster_certificates(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedClusters/post/Get Managed Cluster[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_clusters.get_access_profile(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, role_name=ROLE_NAME)

#--------------------------------------------------------------------------
        # /ManagedClusters/post/Reset AAD Profile[post]
#--------------------------------------------------------------------------
        BODY = {
          "client_app_id": "clientappid",
          "server_app_id": "serverappid",
          "server_app_secret": "serverappsecret",
          "tenant_id": "tenantid"
        }
        # result = self.mgmt_client.managed_clusters.begin_reset_aadprofile(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /OpenShiftManagedClusters/patch/Update OpenShift Managed Cluster Tags[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tier": "testing",
            "archv3": ""
          }
        }
        # result = self.mgmt_client.open_shift_managed_clusters.begin_update_tags(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ManagedClusters/patch/Update Managed Cluster Tags[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tier": "testing",
            "archv3": ""
          }
        }
        result = self.mgmt_client.managed_clusters.begin_update_tags(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/delete/Delete Private Endpoint Connection[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.private_endpoint_connections.begin_delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /AgentPools/delete/Delete Agent Pool[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.agent_pools.begin_delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ContainerServices/delete/Delete Container Service[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.container_services.begin_delete(resource_group_name=RESOURCE_GROUP, container_service_name=CONTAINER_SERVICE_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /OpenShiftManagedClusters/delete/Delete OpenShift Managed Cluster[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.open_shift_managed_clusters.begin_delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ManagedClusters/delete/Delete Managed Cluster[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_clusters.begin_delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
