# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 8
# Methods Covered : 8
# Examples Total  : 8
# Examples Tested : 8
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.redhatopenshift
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAzureRedHatOpenShiftClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAzureRedHatOpenShiftClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.redhatopenshift.AzureRedHatOpenShiftClient
        )
        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )
            from azure.mgmt.authorization import AuthorizationManagementClient
            self.authorization_client = self.create_mgmt_client(
                AuthorizationManagementClient
            )
            from azure.mgmt.containerregistry import ContainerRegistryManagementClient
            self.acr_client = self.create_mgmt_client(
                ContainerRegistryManagementClient
            )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):
      
      azure_operation_poller = self.network_client.virtual_networks.create_or_update(
          group_name,
          network_name,
          {
              'location': location,
              'address_space': {
                  'address_prefixes': ['10.0.0.0/16']
              }
          },
      )
      result_create = azure_operation_poller.result()

      async_subnet_creation = self.network_client.subnets.create_or_update(
          group_name,
          network_name,
          subnet_name,
          subnet_parameters={'address_prefix': '10.0.0.0/24', "private_link_service_network_policies": "Disabled", "private_endpoint_network_policies": "Disabled", "service_endpoints": [ { "service": "Microsoft.ContainerRegistry" } ] }
      )
      subnet_info = async_subnet_creation.result()
      
      return subnet_info

    def create_subnet(self, group_name, location, network_name, subnet_name):
        async_subnet_creation = self.network_client.subnets.create_or_update(
            group_name,
            network_name,
            subnet_name,
            subnet_parameters={'address_prefix': '10.0.1.0/24', "private_link_service_network_policies": "Disabled", "private_endpoint_network_policies": "Disabled", "service_endpoints": [ { "service": "Microsoft.ContainerRegistry" } ] }
        )
        subnet_info = async_subnet_creation.result()

        subnet_info = self.network_client.subnets.get(group_name,
                            network_name,
                            subnet_name)

        print(str(subnet_info))

        return subnet_info

    def assign_role(self,
                    service_principal_id,
                    scope,
                    name,
                    full_id):
        BODY = {
            "role_definition_id": full_id,
            "principal_id": service_principal_id,
            "principal_type": "ServicePrincipal"
        }
        result = self.authorization_client.role_assignments.create(scope, role_assignment_name=name, parameters=BODY)

    def create_private_endpoint(self, subscription_id, group_name, name, vnet_name, subnet_name, registry_name):

        # Create load balancer
        LOAD_BALANCER = "testlb"
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "Standard"
          },
            "frontend_ip_configurations": [
              {
                "name": "fipconfig",
                  "subnet": {
                    "id": "/subscriptions/" + subscription_id + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + subnet_name
                  }
              }
            ],
        }

        result = self.network_client.load_balancers.create_or_update(group_name, LOAD_BALANCER, BODY)
        result.result()

        
        # Create private link services
        PRIVATE_LINK_SERVICES = "privatelinkservice"
        BODY = {
          "location": AZURE_LOCATION,
          "visibility": {
            "subscriptions": [
              subscription_id
            ]
          },
          "auto_approval": {
            "subscriptions": [
              subscription_id
            ]
          },
          "fqdns": [
            # "fqdn1",
            # "fqdn2",
            # "fqdn3"
          ],
          "load_balancer_frontend_ip_configurations": [
             {
               "id": "/subscriptions/" + subscription_id + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER + "/frontendIPConfigurations/" + "fipconfig",
             }
           ],
          "ip_configurations": [
            {
              "name": "configname",
              "properties": {
                "private_ip_address": "10.0.0.5",
                "private_ip_allocation_method": "Static",
                "private_ip_address_version": "IPv4",
                "subnet": {
                  "id": "/subscriptions/" + subscription_id + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + subnet_name
                }
              }
            }
          ]
        }
        result = self.network_client.private_link_services.create_or_update(group_name, PRIVATE_LINK_SERVICES, BODY)

        
        BODY = {
          "location": AZURE_LOCATION,
          # "private_link_service_connections": [
          #  #{
          #  #  "name": "privatelinkservices",
          #  #  # TODO: This is needed, but was not showed in swagger.
          #  #  "private_link_service_id": "/subscriptions/" + subscription_id + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/privateLinkServices/" + PRIVATE_LINK_SERVICES,
          #  #},
          #  {
          #    "name": "acrconnection",
          #    "private_link_service_id": "/subscriptions/" + subscription_id + "/resourceGroups/" + group_name + "/providers/Microsoft.ContainerRegistry/registries/" + registry_name + "",
          #    "group_ids": [ "xxxxxxxxxxx" ]
          #  }
          #],
          "subnet": {
            "id": "/subscriptions/" + subscription_id + "/resourceGroups/" + group_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + subnet_name
          }
        }

        endpoint = self.network_client.private_endpoints.create_or_update(
                resource_group_name=group_name,
                private_endpoint_name=name,
                parameters=BODY
        )

        return endpoint.id

        
    def create_acr(self, group_name, registry_name, location, private_endpoint_id):
        registry = self.acr_client.registries.create(
            resource_group_name=group_name,
            registry_name=registry_name,
            registry={
              "location": location,
              "sku": {
                "name": "Premium"
              }
            }
        )

        #private_endpoint = self.acr_client.private_endpoint_connections.create_or_update(
        #        group_name,
        #        registry_name,
        #        endpoint_name,
        #        { "id": private_endpoint_id }
        #)


    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_redhatopenshift(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "myResource"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mySubnet"
        SUBNET_NAME_2 = "mySubnet2"

        SUBNET = self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)
        SUBNET_2 = self.create_subnet(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME_2)
        
        self.assign_role(self.settings.SERVICE_PRINCIPAL_ID, # SP Object ID
                         "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME,
                         "1fa638dc-b769-420d-b822-340abb216e78",
                         "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Authorization/roleDefinitions/" + "b24988ac-6180-42a0-ab88-20f7382dd24c")
        self.assign_role(self.settings.ARO_SERVICE_PRINCIPAL_ID,
                         "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME,
                         "1fa638dc-b769-420d-b822-340abb216e77",
                         "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Authorization/roleDefinitions/" + "b24988ac-6180-42a0-ab88-20f7382dd24c")

        self.create_acr(RESOURCE_GROUP, "acdr27837", "westus", None) #endpoint_id)
        #endpoint_id = self.create_private_endpoint(SUBSCRIPTION_ID,
        #                                           RESOURCE_GROUP,
        #                                           "endpoint123",
        #                                           VIRTUAL_NETWORK_NAME,
        #                                           SUBNET_NAME_2,
        #                                           "acdr27837")
        # self.create_acr(RESOURCE_GROUP, "acdr27837", "westus", endpoint_id)
        
        # /OpenShiftClusters/put/Creates or updates a OpenShift cluster with the specified subscription, resource group and resource name.[put]
        BODY = {
          "location": "australiaeast",
          "tags": {
            "key": "value"
          },
          "cluster_profile": {
            "pull_secret": "{\"auths\":{\"registry.connect.redhat.com\":{\"auth\":\"\"},\"registry.redhat.io\":{\"auth\":\"\"}}}",
            "domain": "cluster.australiaeast.aroapp.io",
            "resource_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + ""
          },
          "service_principal_profile": {
            "client_id": self.settings.CLIENT_ID,
            "client_secret": self.settings.CLIENT_SECRET
          },
          "network_profile": {
            "pod_cidr": "10.128.0.0/14",
            "service_cidr": "172.30.0.0/16"
          },
          "master_profile": {
            "vm_size": "Standard_D8s_v3",
            "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
          },
          "worker_profiles": [
            {
              "name": "worker",
              "vm_size": "Standard_D8s_v3",
              "disk_size_gb": "128",
              "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME_2 + "",
              "count": "3"
            }
          ],
          "apiserver_profile": {
            "visibility": "Public"
          },
          "ingress_profiles": [
            {
              "name": "default",
              "visibility": "Public"
            }
          ]
        }
        result = self.mgmt_client.open_shift_clusters.create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        result = result.result()

        # /OpenShiftClusters/get/Gets a OpenShift cluster with the specified subscription, resource group and resource name.[get]
        result = self.mgmt_client.open_shift_clusters.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

        # /OpenShiftClusters/get/Lists OpenShift clusters in the specified subscription and resource group.[get]
        result = self.mgmt_client.open_shift_clusters.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /OpenShiftClusters/get/Lists OpenShift clusters in the specified subscription.[get]
        result = self.mgmt_client.open_shift_clusters.list()

        # /Operations/get/Lists all of the available RP operations.[get]
        result = self.mgmt_client.operations.list()

        # /OpenShiftClusters/post/Lists credentials of an OpenShift cluster with the specified subscription, resource group and resource name.[post]
        result = self.mgmt_client.open_shift_clusters.list_credentials(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

        # /OpenShiftClusters/patch/Creates or updates a OpenShift cluster with the specified subscription, resource group and resource name.[patch]
        BODY = {
          "tags": {
            "key": "value"
          },
          "cluster_profile": {
            "pull_secret": "{\"auths\":{\"registry.connect.redhat.com\":{\"auth\":\"\"},\"registry.redhat.io\":{\"auth\":\"\"}}}",
            "domain": "cluster.location.aroapp.io",
            "resource_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + ""
          },
          "service_principal_profile": {
            "client_id": "clientId",
            "client_secret": "clientSecret"
          },
          "network_profile": {
            "pod_cidr": "10.128.0.0/14",
            "service_cidr": "172.30.0.0/16"
          },
          "master_profile": {
            "vm_size": "Standard_D8s_v3",
            "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
          },
          "worker_profiles": [
            {
              "name": "worker",
              "vm_size": "Standard_D2s_v3",
              "disk_size_gb": "128",
              "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + "",
              "count": "3"
            }
          ],
          "apiserver_profile": {
            "visibility": "Public"
          },
          "ingress_profiles": [
            {
              "name": "default",
              "visibility": "Public"
            }
          ]
        }
        result = self.mgmt_client.open_shift_clusters.update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        result = result.result()

        # /OpenShiftClusters/delete/Deletes a OpenShift cluster with the specified subscription, resource group and resource name.[delete]
        result = self.mgmt_client.open_shift_clusters.delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
