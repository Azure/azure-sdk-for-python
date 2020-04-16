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

import azure.mgmt.hybridkubernetes
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtKubernetesConnectRPClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtKubernetesConnectRPClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.hybridkubernetes.KubernetesConnectRPClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_hybridkubernetes(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        CLUSTER_NAME = "myCluster"

        # /ConnectedCluster/put/CreateClusterExample[put]
        BODY = {
          "location": "East US",
          "identity": {
            "type": "SystemAssigned"
          },
          "agent_public_key_certificate": "MIICYzCCAcygAwIBAgIBADANBgkqhkiG9w0BAQUFADAuMQswCQYDVQQGEwJVUzEMMAoGA1UEChMDSUJNMREwDwYDVQQLEwhMb2NhbCBDQTAeFw05OTEyMjIwNTAwMDBaFw0wMDEyMjMwNDU5NTlaMC4xCzAJBgNVBAYTAlVTMQwwCgYDVQQKEwNJQk0xETAPBgNVBAsTCExvY2FsIENBMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD2bZEo7xGaX2/0GHkrNFZvlxBou9v1Jmt/PDiTMPve8r9FeJAQ0QdvFST/0JPQYD20rH0bimdDLgNdNynmyRoS2S/IInfpmf69iyc2G0TPyRvmHIiOZbdCd+YBHQi1adkj17NDcWj6S14tVurFX73zx0sNoMS79q3tuXKrDsxeuwIDAQABo4GQMIGNMEsGCVUdDwGG+EIBDQQ+EzxHZW5lcmF0ZWQgYnkgdGhlIFNlY3VyZVdheSBTZWN1cml0eSBTZXJ2ZXIgZm9yIE9TLzM5MCAoUkFDRikwDgYDVR0PAQH/BAQDAgAGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFJ3+ocRyCTJw067dLSwr/nalx6YMMA0GCSqGSIb3DQEBBQUAA4GBAMaQzt+zaj1GU77yzlr8iiMBXgdQrwsZZWJo5exnAucJAEYQZmOfyLiM D6oYq+ZnfvM0n8G/Y79q8nhwvuxpYOnRSAXFp6xSkrIOeZtJMY1h00LKp/JX3Ng1svZ2agE126JHsQ0bhzN5TKsYfbwfTwfjdWAGy6Vf1nYi/rO+ryMO",
          "aad_profile": {
            "tenant_id": "72f988bf-86f1-41af-91ab-2d7cd011db47",
            "client_app_id": "f8cd1fd9-154f-4da7-b348-595f283c13a3",
            "server_app_id": "45c27b16-e262-4c55-b572-b3b8f7788eb8"
          }
        }
        result = self.mgmt_client.connected_cluster.create(resource_group_name=RESOURCE_GROUP, cluster_name=CLUSTER_NAME, connected_cluster=BODY)
        result = result.result()

        # /ConnectedCluster/get/GetClusterExample[get]
        result = self.mgmt_client.connected_cluster.get(resource_group_name=RESOURCE_GROUP, cluster_name=CLUSTER_NAME)

        # /ConnectedCluster/get/GetClustersExample[get]
        result = self.mgmt_client.connected_cluster.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /ConnectedCluster/get/GetClustersExample[get]
        result = self.mgmt_client.connected_cluster.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /Operations/get/ListConnectedClusterOperationsExample[get]
        result = self.mgmt_client.operations.get()

        # /ConnectedCluster/post/ListClusterUserCredentialsExample[post]
        result = self.mgmt_client.connected_cluster.list_cluster_user_credentials(resource_group_name=RESOURCE_GROUP, cluster_name=CLUSTER_NAME)

        # /ConnectedCluster/patch/UpdateClusterExample[patch]
        TAGS = {
          "tag1": "value1",
          "tag2": "value2"
        }
        result = self.mgmt_client.connected_cluster.update(resource_group_name=RESOURCE_GROUP, cluster_name=CLUSTER_NAME, tags= TAGS, agent_public_key_certificate="MIICYzCCAcygAwIBAgIBADANBgkqhkiG9w0BAQUFADAuMQswCQYDVQQGEwJVUzEMMAoGA1UEChMDSUJNMREwDwYDVQQLEwhMb2NhbCBDQTAeFw05OTEyMjIwNTAwMDBaFw0wMDEyMjMwNDU5NTlaMC4xCzAJBgNVBAYTAlVTMQwwCgYDVQQKEwNJQk0xETAPBgNVBAsTCExvY2FsIENBMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD2bZEo7xGaX2/0GHkrNFZvlxBou9v1Jmt/PDiTMPve8r9FeJAQ0QdvFST/0JPQYD20rH0bimdDLgNdNynmyRoS2S/IInfpmf69iyc2G0TPyRvmHIiOZbdCd+YBHQi1adkj17NDcWj6S14tVurFX73zx0sNoMS79q3tuXKrDsxeuwIDAQABo4GQMIGNMEsGCVUdDwGG+EIBDQQ+EzxHZW5lcmF0ZWQgYnkgdGhlIFNlY3VyZVdheSBTZWN1cml0eSBTZXJ2ZXIgZm9yIE9TLzM5MCAoUkFDRikwDgYDVR0PAQH/BAQDAgAGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFJ3+ocRyCTJw067dLSwr/nalx6YMMA0GCSqGSIb3DQEBBQUAA4GBAMaQzt+zaj1GU77yzlr8iiMBXgdQrwsZZWJo5exnAucJAEYQZmOfyLiM D6oYq+ZnfvM0n8G/Y79q8nhwvuxpYOnRSAXFp6xSkrIOeZtJMY1h00LKp/JX3Ng1svZ2agE126JHsQ0bhzN5TKsYfbwfTwfjdWAGy6Vf1nYi/rO+ryMO")

        # /ConnectedCluster/delete/DeleteClusterExample[delete]
        result = self.mgmt_client.connected_cluster.delete(resource_group_name=RESOURCE_GROUP, cluster_name=CLUSTER_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
