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

AZURE_LOCATION = 'australiaeast'

@unittest.skip("skip test")
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


    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_redhatopenshift(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "zimsclusterxx"
        VIRTUAL_NETWORK_NAME = "myvirtualnetwork"
        SUBNET_NAME = "mysubnet"
        SUBNET_NAME_2 = "mysubnet2"

        if self.is_live:
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
          CLIENT_ID = self.settings.CLIENT_ID
          CLIENT_SECRET = self.settings.CLIENT_SECRET
          self.be_careful_with_service_principal
        else:
          CLIENT_ID = "00000000-0000-0000-0000-000000000000"
          CLIENT_SECRET = "xxxxxxxx"

        # /OpenShiftClusters/put/Creates or updates a OpenShift cluster with the specified subscription, resource group and resource name.[put]
        BODY = {
          "location": "australiaeast",
          "tags": {
            "key": "value"
          },
          "cluster_profile": {
            "pull_secret": "",
            "domain": "ab0176mx",
            "resource_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + "aro-ab0176mx"
          },
          "service_principal_profile": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
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
              "vm_size": "Standard_D4s_v3",
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
            "pull_secret": "",
            "domain": "ab0176mx",
            "resource_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + "aro-ab0176mx"
          },
          "service_principal_profile": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
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
              # "name": "worker",
              "vm_size": "Standard_D4s_v3",
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
        result = self.mgmt_client.open_shift_clusters.update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, parameters=BODY)
        result = result.result()

        # /OpenShiftClusters/delete/Deletes a OpenShift cluster with the specified subscription, resource group and resource name.[delete]
        result = self.mgmt_client.open_shift_clusters.delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
