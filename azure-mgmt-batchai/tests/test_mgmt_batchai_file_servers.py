# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
import azure.mgmt.batchai.models as models
from azure.mgmt.batchai import BatchAIManagementClient
from devtools_testutils import AzureMgmtTestCase
from devtools_testutils import ResourceGroupPreparer
from devtools_testutils import StorageAccountPreparer
from helpers import Helpers

_FILE_SERVER_CREATION_TIMEOUT_SEC = Helpers.MINUTE * 10


class FileServerTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(FileServerTestCase, self).setUp()
        self.client = Helpers.create_batchai_client(self)  # type: BatchAIManagementClient
        self.file_server_name = self.get_resource_name('fileserver')

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    def test_file_server(self, resource_group, location, storage_account, storage_account_key):
        """Tests file server functionality

        1. Create file server
        2. Create two clusters with this file server
        3. Check that the file server is mounted:
            a. submit tasks (one from host and another from container) on the first cluster to write data to nfs
            b. submit a task on the second cluster to read the data from nfs
        """
        server = Helpers.create_file_server(self.client, location, resource_group.name,
                                            self.file_server_name)  # type: models.FileServer

        cluster1 = Helpers.create_cluster(self.client, location, resource_group.name, 'cluster1',
                                          'STANDARD_D1', 1,
                                          storage_account.name, storage_account_key,
                                          file_servers=[models.FileServerReference(
                                              file_server=models.ResourceId(id=server.id),
                                              relative_mount_path='nfs',
                                              mount_options="rw")])
        cluster2 = Helpers.create_cluster(self.client, location, resource_group.name, 'cluster2',
                                          'STANDARD_D1', 1,
                                          storage_account.name, storage_account_key,
                                          file_servers=[models.FileServerReference(
                                              file_server=models.ResourceId(id=server.id),
                                              relative_mount_path='nfs',
                                              mount_options="rw")])
        # Verify the file server is reported.
        Helpers.assert_existing_file_servers_are(self, self.client, resource_group.name, [self.file_server_name])

        # Verify the file server become available in a reasonable time
        self.assertTrue(
            Helpers.wait_for_file_server(self.is_live, self.client, resource_group.name, self.file_server_name,
                                         _FILE_SERVER_CREATION_TIMEOUT_SEC))

        # Verify the remote login information and private ip are reported
        server = self.client.file_servers.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, self.file_server_name)
        self.assertRegexpMatches(server.mount_settings.file_server_public_ip, Helpers.RE_ID_ADDRESS)
        self.assertRegexpMatches(server.mount_settings.file_server_internal_ip, Helpers.RE_ID_ADDRESS)

        # Verify the clusters allocated nodes successfully
        self.assertEqual(
            Helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, 'cluster1', 1,
                                   Helpers.NODE_STARTUP_TIMEOUT_SEC), 1)
        self.assertEqual(
            Helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, 'cluster2', 1,
                                   Helpers.NODE_STARTUP_TIMEOUT_SEC), 1)

        # Execute publishing tasks on the first cluster
        job1 = Helpers.create_custom_job(self.client, resource_group.name, cluster1.id, 'host_publisher', 1,
                                         'echo hi from host > $AZ_BATCHAI_MOUNT_ROOT/nfs/host.txt')
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job1.name, Helpers.MINUTE),
            models.ExecutionState.succeeded)
        job2 = Helpers.create_custom_job(self.client, resource_group.name, cluster1.id, 'container_publisher', 1,
                                         'echo hi from container >> $AZ_BATCHAI_MOUNT_ROOT/nfs/container.txt',
                                         container=models.ContainerSettings(
                                             image_source_registry=models.ImageSourceRegistry(image="ubuntu")))
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job2.name, Helpers.MINUTE),
            models.ExecutionState.succeeded)

        # Execute consumer task on the second cluster
        job3 = Helpers.create_custom_job(self.client, resource_group.name, cluster2.id, 'consumer', 1,
                                         'cat $AZ_BATCHAI_MOUNT_ROOT/nfs/host.txt; '
                                         'cat $AZ_BATCHAI_MOUNT_ROOT/nfs/container.txt')
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job3.name, Helpers.MINUTE),
            models.ExecutionState.succeeded)

        # Verify the data
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job3.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'hi from host\nhi from container\n', u'stderr.txt': ''})

        # Delete clusters
        self.client.clusters.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, 'cluster1').result()
        self.client.clusters.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, 'cluster2').result()

        # Test deletion
        self.client.file_servers.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, self.file_server_name).result()
        Helpers.assert_existing_file_servers_are(self, self.client, resource_group.name, [])
