# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from azure.mgmt.hdinsight import HDInsightManagementClient
from azure.mgmt.hdinsight.models import *
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer, StorageAccountPreparer, FakeStorageAccount


class HDInsightTestConfig:
    # Non-sensitive test configs
    location = "North Central US"
    cluster_username = "admin"
    cluster_password = "Password1!"
    ssh_username = "sshuser"
    ssh_password = "Password1!"
    storage_account_suffix = ".blob.core.windows.net"

    FAKE_STORAGE = FakeStorageAccount(
        name='pyhdi',
        id='',
    )

class MgmtHDInsightTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtHDInsightTest, self).setUp()
        self.hdinsight_client = self.create_mgmt_client(
            HDInsightManagementClient
        )

    @ResourceGroupPreparer(location=HDInsightTestConfig.location)
    @StorageAccountPreparer(name_prefix='hdipy', location=HDInsightTestConfig.location, playback_fake_resource=HDInsightTestConfig.FAKE_STORAGE)
    def test_cluster_create(self, resource_group, location, storage_account, storage_account_key):
        cluster_name = self.get_resource_name('hdisdk-py-humboldt')
        create_params = self.get_extended_create_params(location, cluster_name, storage_account.name, storage_account_key)
        create_poller = self.hdinsight_client.clusters.create(resource_group.name, cluster_name, create_params)
        cluster = create_poller.result()
        self.validate_cluster(create_params, cluster)

        scale_poller = self.hdinsight_client.clusters.resize(resource_group.name, cluster_name, target_instance_count=2)
        scale_poller.wait()

        delete_poller = self.hdinsight_client.clusters.delete(resource_group.name, cluster_name)
        delete_poller.wait()

    def get_extended_create_params(self, location, cluster_name, storage_account_name, storage_account_key):
        return ClusterCreateParametersExtended(
            location=location,
            tags={},
            properties=ClusterCreateProperties(
                cluster_version="3.6",
                os_type=OSType.linux,
                tier=Tier.standard,
                cluster_definition=ClusterDefinition(
                    kind="hadoop",
                    configurations={
                        "gateway": {
                            "restAuthCredential.enabled_credential": "True",
                            "restAuthCredential.username": HDInsightTestConfig.cluster_username,
                            "restAuthCredential.password": HDInsightTestConfig.cluster_password
                        }
                    }
                ),
                compute_profile=ComputeProfile(
                    roles=[
                        Role(
                            name="headnode",
                            target_instance_count=2,
                            hardware_profile=HardwareProfile(vm_size="Large"),
                            os_profile=OsProfile(
                                linux_operating_system_profile=LinuxOperatingSystemProfile(
                                    username=HDInsightTestConfig.ssh_username,
                                    password=HDInsightTestConfig.ssh_password
                                )
                            )
                        ),
                        Role(
                            name="workernode",
                            target_instance_count=1,
                            hardware_profile=HardwareProfile(vm_size="Large"),
                            os_profile=OsProfile(
                                linux_operating_system_profile=LinuxOperatingSystemProfile(
                                    username=HDInsightTestConfig.ssh_username,
                                    password=HDInsightTestConfig.ssh_password
                                )
                            )
                        )
                    ]
                ),
                storage_profile=StorageProfile(
                    storageaccounts=[StorageAccount(
                        name=storage_account_name + HDInsightTestConfig.storage_account_suffix,
                        key=storage_account_key,
                        container=cluster_name.lower(),
                        is_default=True
                    )]
                )
            )
        )

    def validate_cluster(self, create_parameters, cluster_response):
        self.assertEqual(create_parameters.properties.tier, cluster_response.properties.tier)
        self.assertEqual("Running", cluster_response.properties.cluster_state)
        self.assertIsNotNone(cluster_response.etag)
        self.assertEqual("Microsoft.HDInsight/clusters", cluster_response.type)
        self.assertEqual(create_parameters.location, cluster_response.location)
        self.assertEqual(create_parameters.tags, cluster_response.tags)
        self.assertEqual(1, len([endpoint for endpoint in cluster_response.properties.connectivity_endpoints
                                 if endpoint.name == "HTTPS"]))
        self.assertEqual(1, len([endpoint for endpoint in cluster_response.properties.connectivity_endpoints
                                 if endpoint.name == "SSH"]))
        self.assertEqual(create_parameters.properties.os_type, cluster_response.properties.os_type)
        self.assertIsNone(cluster_response.properties.errors)
        self.assertEqual(HDInsightClusterProvisioningState.succeeded, cluster_response.properties.provisioning_state)
        self.assertEqual(create_parameters.properties.cluster_definition.kind, cluster_response.properties.cluster_definition.kind)
        self.assertEqual(create_parameters.properties.cluster_version, cluster_response.properties.cluster_version[0:3])


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
