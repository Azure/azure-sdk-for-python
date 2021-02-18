# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 30
# Methods Covered : 30
# Examples Total  : 20
# Examples Tested : 20
# Coverage %      : 67
# ----------------------

# Current Operation Coverage:
#   OpenShiftManagedClusters: 0/6 (only one preview version, so needn't test)
#   ContainerServices: 0/6 (the interface is going to retire, so needn't test)
#   Operations: 1/1
#   ManagedClusters: 13/17
#   AgentPools: 4/6
#   PrivateEndpointConnections: 0/4
#   PrivateLinkResourcesOperations: 1/1
#   ResolvePrivateLinkServiceIdOperations : 1/1

import unittest
import time

import azure.mgmt.containerservice
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'


class MgmtContainerServiceClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtContainerServiceClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.containerservice.ContainerServiceClient
        )

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_managed_clusters(self, resource_group):
        CLIENT_ID = getattr(self.settings, 'CLIENT_ID', "123")
        CLIENT_SECRET = getattr(self.settings, 'CLIENT_SECRET', "123")
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "7"

        # 1
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
                }
            ],
            "service_principal_profile": {
                "client_id": CLIENT_ID,
                "secret": CLIENT_SECRET
            },
            "location": AZURE_LOCATION
        }
        for i in range(10):
            try:
                result = self.mgmt_client.managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP,
                                                                                  resource_name=RESOURCE_NAME,
                                                                                  parameters=BODY)
                result.result()
            except azure.core.exceptions.ResourceExistsError:
                time.sleep(30)
            else:
                break
        # 2
        self.mgmt_client.managed_clusters.list_cluster_admin_credentials(resource_group_name=RESOURCE_GROUP,
                                                                         resource_name=RESOURCE_NAME)
        # 3
        self.mgmt_client.managed_clusters.list_cluster_user_credentials(resource_group_name=RESOURCE_GROUP,
                                                                        resource_name=RESOURCE_NAME)
        # 4
        self.mgmt_client.managed_clusters.get_upgrade_profile(resource_group_name=RESOURCE_GROUP,
                                                              resource_name=RESOURCE_NAME)
        # # 5
        # result = self.mgmt_client.managed_clusters.begin_stop(resource_group_name=RESOURCE_GROUP,
        #                                                       resource_name=RESOURCE_NAME)
        # result.result()
        # # 6
        # result = self.mgmt_client.managed_clusters.begin_start(resource_group_name=RESOURCE_GROUP,
        #                                                        resource_name=RESOURCE_NAME)
        # result.result()
        # 7
        self.mgmt_client.managed_clusters.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        # 8
        self.mgmt_client.managed_clusters.list_by_resource_group(resource_group_name=RESOURCE_GROUP)
        # 9
        self.mgmt_client.managed_clusters.list()
        # # 10
        # result = self.mgmt_client.managed_clusters.begin_rotate_cluster_certificates(resource_group_name=RESOURCE_GROUP,
        #                                                                              resource_name=RESOURCE_NAME)
        result.result()
        # 11
        BODY = {
            "tags": {
                "tier": "testing",
                "archv3": ""
            }
        }
        result = self.mgmt_client.managed_clusters.begin_update_tags(resource_group_name=RESOURCE_GROUP,
                                                                     resource_name=RESOURCE_NAME, parameters=BODY)
        result.result()
        # 12
        self.mgmt_client.managed_clusters.list_cluster_monitoring_user_credentials(resource_group_name=RESOURCE_GROUP,
                                                                                   resource_name=RESOURCE_NAME)
        # 13
        result = self.mgmt_client.managed_clusters.begin_delete(resource_group_name=RESOURCE_GROUP,
                                                                resource_name=RESOURCE_NAME)
        result.result()

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_operations(self):
        result = self.mgmt_client.operations.list()

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_privateLinkResources(self, resource_group):
        CLIENT_ID = getattr(self.settings, 'CLIENT_ID', "123")
        CLIENT_SECRET = getattr(self.settings, 'CLIENT_SECRET', "123")
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "2"

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
                }
            ],
            "api_server_access_profile": {
                "enable_private_cluster": True  # private cluster
            },
            "service_principal_profile": {
                "client_id": CLIENT_ID,
                "secret": CLIENT_SECRET
            },
            "location": AZURE_LOCATION
        }
        for i in range(10):
            try:
                result = self.mgmt_client.managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP,
                                                                                  resource_name=RESOURCE_NAME,
                                                                                  parameters=BODY)
                result.result()
            except azure.core.exceptions.ResourceExistsError:
                time.sleep(30)
            else:
                break

        # 1
        self.mgmt_client.private_link_resources.list(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_resolvePrivateLinkServiceId(self, resource_group):
        CLIENT_ID = getattr(self.settings, 'CLIENT_ID', "123")
        CLIENT_SECRET = getattr(self.settings, 'CLIENT_SECRET', "123")
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "3"

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
                }
            ],
            "api_server_access_profile": {
                "enable_private_cluster": True  # private cluster
            },
            "service_principal_profile": {
                "client_id": CLIENT_ID,
                "secret": CLIENT_SECRET
            },
            "location": AZURE_LOCATION
        }
        for i in range(10):
            try:
                result = self.mgmt_client.managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP,
                                                                                  resource_name=RESOURCE_NAME,
                                                                                  parameters=BODY)
                result.result()
            except azure.core.exceptions.ResourceExistsError:
                time.sleep(30)
            else:
                break

        # 1
        BODY = {
            "name": "testManagement"
        }
        self.mgmt_client.resolve_private_link_service_id.post(resource_group_name=RESOURCE_GROUP,
                                                              resource_name=RESOURCE_NAME, parameters=BODY)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_agentPools(self, resource_group):
        CLIENT_ID = getattr(self.settings, 'CLIENT_ID', "123")
        CLIENT_SECRET = getattr(self.settings, 'CLIENT_SECRET', "123")
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "4"
        AGENT_POOL_NAME = "aksagent"
        MODE = "System"
        VM_SIZE = "Standard_DS2_v2"

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
                }
            ],
            "service_principal_profile": {
                "client_id": CLIENT_ID,
                "secret": CLIENT_SECRET
            },
            "location": AZURE_LOCATION
        }
        result = self.mgmt_client.managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP,
                                                                          resource_name=RESOURCE_NAME, parameters=BODY)
        result.result()

        # 1
        BODY = {
            "orchestrator_version": "",
            "count": "3",
            "vm_size": VM_SIZE,
            "os_type": "Linux",
            "type": "VirtualMachineScaleSets",
            "mode": MODE,
            "availability_zones": [
                "1",
                "2",
                "3"
            ],
            # "scale_set_priority": "Regular",
            # "scale_set_eviction_policy": "Delete",
            "node_taints": []
        }
        for i in range(10):
            try:
                result = self.mgmt_client.agent_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP,
                                                                             resource_name=RESOURCE_NAME,
                                                                             agent_pool_name=AGENT_POOL_NAME,
                                                                             parameters=BODY)
                result = result.result()
            except azure.core.exceptions.ResourceExistsError:
                time.sleep(30)
            else:
                break

        # 2
        self.mgmt_client.agent_pools.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME,
                                         agent_pool_name=AGENT_POOL_NAME)
        # 3
        self.mgmt_client.agent_pools.get_available_agent_pool_versions(resource_group_name=RESOURCE_GROUP,
                                                                       resource_name=RESOURCE_NAME)
        # 4
        self.mgmt_client.agent_pools.list(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

        # result = self.mgmt_client.agent_pools.begin_delete(resource_group_name=RESOURCE_GROUP,
        #                                                    resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME)
        # result = result.result()

        # self.mgmt_client.agent_pools.get_upgrade_profile(resource_group_name=RESOURCE_GROUP,
        #                                                  resource_name=RESOURCE_NAME, agent_pool_name=AGENT_POOL_NAME,
        #                                                  upgrade_profile_name=UPGRADE_PROFILE_NAME)

    # @ResourceGroupPreparer(location=AZURE_LOCATION)
    # def test_privateEndpointConnections(self, resource_group):
    #     CLIENT_ID = self.settings.CLIENT_ID or "123"
    #     CLIENT_SECRET = self.settings.CLIENT_SECRET or "123"
    #     RESOURCE_GROUP = resource_group.name
    #     RESOURCE_NAME = "myResource"
    #     PRIVATE_ENDPOINT_CONNECTION_NAME = 'testPrivateEndPointConnectionName'
    #
    #     BODY = {
    #         "dns_prefix": "akspythonsdk",
    #         "agent_pool_profiles": [
    #             {
    #                 "name": "aksagent",
    #                 "count": 1,
    #                 "vm_size": "Standard_DS2_v2",
    #                 "max_pods": 110,
    #                 "min_count": 1,
    #                 "max_count": 100,
    #                 "os_type": "Linux",
    #                 "type": "VirtualMachineScaleSets",
    #                 "enable_auto_scaling": True,
    #                 "mode": "System",
    #             }
    #         ],
    #         "api_server_access_profile": {
    #             "enable_private_cluster": True  # private cluster
    #         },
    #         "service_principal_profile": {
    #             "client_id": CLIENT_ID,
    #             "secret": CLIENT_SECRET
    #         },
    #         "location": AZURE_LOCATION
    #     }
    #     result = self.mgmt_client.managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP,
    #                                                                       resource_name=RESOURCE_NAME, parameters=BODY)
    #     result.result()
    #
    #     # 1
    #     BODY = {
    #         "private_link_service_connection_state": {
    #             "status": "Approved"
    #         }
    #     }
    #     self.mgmt_client.private_endpoint_connections.update(resource_group_name=RESOURCE_GROUP,
    #                                                          resource_name=RESOURCE_NAME,
    #                                                          private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME,
    #                                                          parameters=BODY)
    #
    #     # 2
    #     self.mgmt_client.private_endpoint_connections.get(resource_group_name=RESOURCE_GROUP,
    #                                                       resource_name=RESOURCE_NAME,
    #                                                       private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
    #
    #     # 3
    #     self.mgmt_client.private_endpoint_connections.list(resource_group_name=RESOURCE_GROUP,
    #                                                        resource_name=RESOURCE_NAME)
    #
    #     # 4
    #     result = self.mgmt_client.private_endpoint_connections.begin_delete(resource_group_name=RESOURCE_GROUP,
    #                                                                         resource_name=RESOURCE_NAME,
    #                                                                         private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
    #     result = result.result()

    # # the interface is going to retire, so needn't test
    # @ResourceGroupPreparer(location=AZURE_LOCATION)
    # def test_containerServices(self, resource_group):
    #     CLIENT_ID = self.settings.CLIENT_ID or "123"
    #     CLIENT_SECRET = self.settings.CLIENT_SECRET or "123"
    #     RESOURCE_GROUP = resource_group.name
    #     CONTAINER_SERVICE_NAME = "myContainerService"
    #     KEYDATA = self.settings.KEYDATA  # git bash use 'cat ~/.ssh/id_rsa.pub'
    #
    #     # /ContainerServices/put/Create/Update Container Service[put]
    #
    #     BODY = {
    #         "location": AZURE_LOCATION,
    #         "agent_pool_profiles": [
    #             {
    #                 "name": "agentx",
    #                 "count": 1,
    #                 "vm_size": "Standard_DS2_v2",
    #                 "os_type": "Linux",
    #                 "dns_prefix": "agentdnsx"
    #             }
    #         ],
    #         "linux_profile": {
    #             "ssh": {
    #                 "public_keys": [
    #                     {
    #                         "key_data": KEYDATA
    #                     }
    #                 ]
    #             },
    #             "admin_username": "azureuser"
    #         },
    #         "master_profile": {
    #             "vm_size": "Standard_A3",
    #             "dns_prefix": "sdkmaster",
    #         },
    #         "orchestrator_profile": {
    #             "orchestrator_type": "DCOS"
    #         },
    #         # "address_space": {
    #         #     "address_prefixes": [
    #         #         "192.168.0.0/16"
    #         #         # "10.2.0.0/16"
    #         #     ]
    #         # },
    #         # "subnets": [
    #         #     {
    #         #         "properties": {
    #         #             "address_prefix": "192.168.0.0/24"
    #         #         },
    #         #         # "name": "clisubnet000005"
    #         #     }
    #         # ]
    #
    #     }
    #     # result = self.mgmt_client.container_services.begin_create_or_update(resource_group_name=RESOURCE_GROUP,
    #     #                                                                     container_service_name=CONTAINER_SERVICE_NAME,
    #     #                                                                     parameters=BODY)
    #     # result = result.result()
    #
    #     # /ContainerServices/get/Get Container Service[get]
    #
    #     # result = self.mgmt_client.container_services.get(resource_group_name=RESOURCE_GROUP,
    #     #                                                  container_service_name=CONTAINER_SERVICE_NAME)
    #
    #     # /ContainerServices/get/List Container Services by Resource Group[get]
    #
    #     result = self.mgmt_client.container_services.list_by_resource_group(resource_group_name=RESOURCE_GROUP)
    #
    #     # /ContainerServices/get/List Container Service Orchestrators[get]
    #
    #     result = self.mgmt_client.container_services.list_orchestrators(location=AZURE_LOCATION)
    #
    #     # /ContainerServices/get/List Container Services[get]
    #
    #     result = self.mgmt_client.container_services.list()
    #
    #     # /ContainerServices/delete/Delete Container Service[delete]
    #
    #     # result = self.mgmt_client.container_services.begin_delete(resource_group_name=RESOURCE_GROUP, container_service_name=CONTAINER_SERVICE_NAME)
    #     # result = result.result()
    #
    # @ResourceGroupPreparer(location=AZURE_LOCATION)
    # def test_OpenShiftManagedClusters(self, resource_group):
    #     SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
    #     TENANT_ID = self.settings.TENANT_ID
    #     CLIENT_ID = self.settings.CLIENT_ID or "123"
    #     CLIENT_SECRET = self.settings.CLIENT_SECRET or "123"
    #     RESOURCE_GROUP = resource_group.name
    #     RESOURCE_NAME = 't'
    #
    #     # /OpenShiftManagedClusters/put/Create/Update OpenShift Managed Cluster[put]
    #
    #     BODY = {
    #         "location": AZURE_LOCATION,
    #         "tags": {
    #             "tier": "production",
    #             "archv2": ""
    #         },
    #         "open_shift_version": "v3.11",
    #         "network_profile": {
    #             "vnet_cidr": "10.0.0.0/8"
    #         },
    #         "master_pool_profile": {
    #             "name": "master",
    #             "count": "3",
    #             "vm_size": "Standard_D4s_v3",
    #             "os_type": "Linux",
    #             "subnet_cidr": "10.0.0.0/24"
    #         },
    #         "agent_pool_profiles": [
    #             {
    #                 "name": "infra",
    #                 "role": "infra",
    #                 "count": 1,
    #                 "vm_size": "Standard_D4s_v3",
    #                 "os_type": "Linux",
    #                 "subnet_cidr": "10.0.0.0/24"
    #             },
    #             {
    #                 "name": "compute",
    #                 "role": "compute",
    #                 "count": 1,
    #                 "vm_size": "Standard_D4s_v3",
    #                 "os_type": "Linux",
    #                 "subnet_cidr": "10.0.0.0/24"
    #             }
    #         ],
    #         "router_profiles": [
    #             {
    #                 "name": "default"
    #             }
    #         ],
    #         "auth_profile": {
    #             "identity_providers": [
    #                 {
    #                     "name": "Azure AD",
    #                     "provider": {
    #                         "kind": "AADIdentityProvider",
    #                         "client_id": CLIENT_ID,
    #                         "secret": CLIENT_SECRET,
    #                         "tenant_id": TENANT_ID,
    #                         #   "customer_admin_group_id": "customerAdminGroupId"
    #                         #   "customer_admin_group_id": RESOURCE_GROUP
    #                     }
    #                 }
    #             ]
    #         }
    #     }
    #     result = self.mgmt_client.open_shift_managed_clusters.begin_create_or_update(resource_group_name=RESOURCE_GROUP,
    #                                                                                  resource_name=RESOURCE_NAME,
    #                                                                                  parameters=BODY)
    #     result = result.result()
    #
    #     # /OpenShiftManagedClusters/get/Get OpenShift Managed Cluster[get]
    #
    #     # result = self.mgmt_client.open_shift_managed_clusters.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
    #
    #     # /OpenShiftManagedClusters/get/Get Managed Clusters by Resource Group[get]
    #
    #     # result = self.mgmt_client.open_shift_managed_clusters.list_by_resource_group(resource_group_name=RESOURCE_GROUP)
    #
    #     # /OpenShiftManagedClusters/get/List Managed Clusters[get]
    #
    #     # result = self.mgmt_client.open_shift_managed_clusters.list()
    #
    #     # /OpenShiftManagedClusters/patch/Update OpenShift Managed Cluster Tags[patch]
    #
    #     BODY = {
    #         "tags": {
    #             "tier": "testing",
    #             "archv3": ""
    #         }
    #     }
    #     # result = self.mgmt_client.open_shift_managed_clusters.begin_update_tags(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
    #     # result = result.result()
    #
    #     # /OpenShiftManagedClusters/delete/Delete OpenShift Managed Cluster[delete]
    #
    #     # result = self.mgmt_client.open_shift_managed_clusters.begin_delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
    #     # result = result.result()


if __name__ == '__main__':
    unittest.main()
