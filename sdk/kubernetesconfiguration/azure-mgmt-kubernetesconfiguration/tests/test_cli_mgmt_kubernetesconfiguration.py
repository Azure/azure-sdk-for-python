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
# from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

# AZURE_LOCATION = 'eastus'

# class MgmtSourceControlConfigurationClientTest(AzureMgmtTestCase):

#     def setUp(self):
#         super(MgmtSourceControlConfigurationClientTest, self).setUp()
#         self.mgmt_client = self.create_mgmt_client(
#             azure.mgmt.kubernetesconfiguration.SourceControlConfigurationClient
#         )
#         if self.is_live:
#             from azure.mgmt.hybridkubernetes import KubernetesConnectRPClient
#             self.kubernetes_client = self.create_mgmt_client(
#                 azure.mgmt.hybridkubernetes.KubernetesConnectRPClient
#             )

#     def create_kubernetes_cluster(self, group_name, cluster_name):
#         BODY = {
#           "location": AZURE_LOCATION,
#           "identity": {
#             "type": "SystemAssigned"
#           },
#           "agent_public_key_certificate": "MIICYzCCAcygAwIBAgIBADANBgkqhkiG9w0BAQUFADAuMQswCQYDVQQGEwJVUzEMMAoGA1UEChMDSUJNMREwDwYDVQQLEwhMb2NhbCBDQTAeFw05OTEyMjIwNTAwMDBaFw0wMDEyMjMwNDU5NTlaMC4xCzAJBgNVBAYTAlVTMQwwCgYDVQQKEwNJQk0xETAPBgNVBAsTCExvY2FsIENBMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD2bZEo7xGaX2/0GHkrNFZvlxBou9v1Jmt/PDiTMPve8r9FeJAQ0QdvFST/0JPQYD20rH0bimdDLgNdNynmyRoS2S/IInfpmf69iyc2G0TPyRvmHIiOZbdCd+YBHQi1adkj17NDcWj6S14tVurFX73zx0sNoMS79q3tuXKrDsxeuwIDAQABo4GQMIGNMEsGCVUdDwGG+EIBDQQ+EzxHZW5lcmF0ZWQgYnkgdGhlIFNlY3VyZVdheSBTZWN1cml0eSBTZXJ2ZXIgZm9yIE9TLzM5MCAoUkFDRikwDgYDVR0PAQH/BAQDAgAGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFJ3+ocRyCTJw067dLSwr/nalx6YMMA0GCSqGSIb3DQEBBQUAA4GBAMaQzt+zaj1GU77yzlr8iiMBXgdQrwsZZWJo5exnAucJAEYQZmOfyLiM D6oYq+ZnfvM0n8G/Y79q8nhwvuxpYOnRSAXFp6xSkrIOeZtJMY1h00LKp/JX3Ng1svZ2agE126JHsQ0bhzN5TKsYfbwfTwfjdWAGy6Vf1nYi/rO+ryMO",
#           "aad_profile": {
#             "tenant_id": "72f988bf-86f1-41af-91ab-2d7cd011db47",
#             "client_app_id": "f8cd1fd9-154f-4da7-b348-595f283c13a3",
#             "server_app_id": "45c27b16-e262-4c55-b572-b3b8f7788eb8"
#           }
#         }
#         result = self.kubernetes_client.connected_cluster.create(resource_group_name=group_name, cluster_name=cluster_name, connected_cluster=BODY)
#         result = result.result()

#     @unittest.skip("skip test")
#     @ResourceGroupPreparer(location=AZURE_LOCATION)
#     def test_kubernetesconfiguration(self, resource_group):

#         SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
#         RESOURCE_GROUP = resource_group.name
#         CLUSTER_RP = "Microsoft.Kubernetes"
#         CLUSTER_RESOURCE_NAME = "connectedClusters"
#         CLUSTER_NAME = "myConnectedCluster"
#         SOURCE_CONTROL_CONFIGURATION_NAME = "mySourceControlConfiguration"

#         if self.is_live:
#             self.create_kubernetes_cluster(RESOURCE_GROUP, CLUSTER_NAME)

#         # /SourceControlConfigurations/put/Create Source Control Configuration[put]
#         BODY = {
#           "repository_url": "git@github.com:k8sdeveloper425/flux-get-started",
#           "operator_namespace": "SRS_Namespace",
#           "operator_instance_name": "SRSGitHubFluxOp-01",
#           "operator_type": "Flux",
#           "operator_scope": "namespace",
#           "operator_params": "--git-email=xyzgituser@users.srs.github.com",
#           "enable_helm_operator": "true",
#           "helm_operator_properties": {
#             "chart_version": "0.3.0",
#             "chart_values": "--set git.ssh.secretName=flux-git-deploy --set tillerNamespace=kube-system"
#           }
#         }
#         result = self.mgmt_client.source_control_configurations.create_or_update(resource_group_name=RESOURCE_GROUP, cluster_rp=CLUSTER_RP, cluster_resource_name=CLUSTER_RESOURCE_NAME, cluster_name=CLUSTER_NAME, source_control_configuration_name=SOURCE_CONTROL_CONFIGURATION_NAME, source_control_configuration=BODY)

#         # /SourceControlConfigurations/get/Get Source Control Configuration[get]
#         result = self.mgmt_client.source_control_configurations.get(resource_group_name=RESOURCE_GROUP, cluster_rp=CLUSTER_RP, cluster_resource_name=CLUSTER_RESOURCE_NAME, cluster_name=CLUSTER_NAME, source_control_configuration_name=SOURCE_CONTROL_CONFIGURATION_NAME)

#         # /SourceControlConfigurations/get/List Source Control Configuration[get]
#         result = self.mgmt_client.source_control_configurations.list(resource_group_name=RESOURCE_GROUP, cluster_rp=CLUSTER_RP, cluster_resource_name=CLUSTER_RESOURCE_NAME, cluster_name=CLUSTER_NAME)

#         # /Operations/get/BatchAccountDelete[get]
#         result = self.mgmt_client.operations.list(api_version="2019-11-01-preview")

#         # /SourceControlConfigurations/delete/Delete Source Control Configuration[delete]
#         result = self.mgmt_client.source_control_configurations.delete(resource_group_name=RESOURCE_GROUP, cluster_rp=CLUSTER_RP, cluster_resource_name=CLUSTER_RESOURCE_NAME, cluster_name=CLUSTER_NAME, source_control_configuration_name=SOURCE_CONTROL_CONFIGURATION_NAME)
#         result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
