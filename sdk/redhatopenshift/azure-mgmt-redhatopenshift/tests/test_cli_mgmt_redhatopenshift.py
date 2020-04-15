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
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_v2020_04_30(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "myResource"

        # /OpenShiftClusters/put/Creates or updates a OpenShift cluster with the specified subscription, resource group and resource name.[put]
        BODY = {
          "location": "location",
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
            "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworksvnet/subnetsmaster"
          },
          "worker_profiles": [
            {
              "name": "worker",
              "vm_size": "Standard_D2s_v3",
              "disk_size_gb": "128",
              "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworksvnet/subnetsworker",
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
            "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworksvnet/subnetsmaster"
          },
          "worker_profiles": [
            {
              "name": "worker",
              "vm_size": "Standard_D2s_v3",
              "disk_size_gb": "128",
              "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworksvnet/subnetsworker",
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
