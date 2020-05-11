# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 5
# Methods Covered : 5
# Examples Total  : 5
# Examples Tested : 5
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.kubernetesconfiguration
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSourceControlConfigurationClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSourceControlConfigurationClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.kubernetesconfiguration.SourceControlConfigurationClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_kubernetesconfiguration(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        CLUSTER_RP = "Microsoft.ContainerService"
        CLUSTER_RESOURCE_NAME = "managedClusters"
        CLUSTER_NAME = "zimscluster"
        SOURCE_CONTROL_CONFIGURATION_NAME = "mySourceControlConfiguration"

        # /SourceControlConfigurations/put/Create Source Control Configuration[put]
        BODY = {
          "repository_url": "git@github.com:k8sdeveloper425/flux-get-started",
          "operator_namespace": "SRS_Namespace",
          "operator_instance_name": "SRSGitHubFluxOp-01",
          "operator_type": "Flux",
          "operator_scope": "namespace",
          "operator_params": "--git-email=xyzgituser@users.srs.github.com",
          "enable_helm_operator": "true",
          "helm_operator_properties": {
            "chart_version": "0.3.0",
            "chart_values": "--set git.ssh.secretName=flux-git-deploy --set tillerNamespace=kube-system"
          }
        }
        result = self.mgmt_client.source_control_configurations.create_or_update(resource_group_name=RESOURCE_GROUP, cluster_rp=CLUSTER_RP, cluster_resource_name=CLUSTER_RESOURCE_NAME, cluster_name=CLUSTER_NAME, source_control_configuration_name=SOURCE_CONTROL_CONFIGURATION_NAME, api_version="2019-11-01-preview", source_control_configuration=BODY)

        # /SourceControlConfigurations/get/Get Source Control Configuration[get]
        result = self.mgmt_client.source_control_configurations.get(resource_group_name=RESOURCE_GROUP, cluster_name=CLUSTER_NAME, source_control_configuration_name=SOURCE_CONTROL_CONFIGURATION_NAME)

        # /SourceControlConfigurations/get/List Source Control Configuration[get]
        result = self.mgmt_client.source_control_configurations.list(resource_group_name=RESOURCE_GROUP, cluster_name=CLUSTER_NAME)

        # /Operations/get/BatchAccountDelete[get]
        result = self.mgmt_client.operations.list()

        # /SourceControlConfigurations/delete/Delete Source Control Configuration[delete]
        result = self.mgmt_client.source_control_configurations.delete(resource_group_name=RESOURCE_GROUP, cluster_name=CLUSTER_NAME, source_control_configuration_name=SOURCE_CONTROL_CONFIGURATION_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
