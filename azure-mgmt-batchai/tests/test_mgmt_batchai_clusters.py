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


class ClusterTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(ClusterTestCase, self).setUp()
        self.client = Helpers.create_batchai_client(self)  # type: BatchAIManagementClient
        self.cluster_name = self.get_resource_name('cluster')

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    def test_creation_and_deletion(self, resource_group, location, storage_account, storage_account_key):
        """Tests basic use-case scenario.

        1. Create cluster
        2. Execute a task on the host
        3. Execute a task in a docker container
        4. Delete cluster
        """
        cluster = Helpers.create_cluster(
            self.client, location, resource_group.name, self.cluster_name, 'STANDARD_D1', 1,
            storage_account.name, storage_account_key)

        self.assertEqual(cluster.name, self.cluster_name)
        self.assertIsNone(cluster.errors)
        self.assertEqual(cluster.vm_size, 'STANDARD_D1')

        # Verify that the cluster is reported in the list of clusters
        Helpers.assert_existing_clusters_are(self, self.client, resource_group.name, [self.cluster_name])

        # Verify that one node is allocated and become available
        self.assertEqual(
            Helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, 1,
                                   Helpers.NODE_STARTUP_TIMEOUT_SEC), 1)
        Helpers.assert_remote_login_info_reported_for_nodes(self, self.client, resource_group.name,
                                                            self.cluster_name, 1)

        # Verify that the cluster able to run tasks.
        self.assertCanRunJobOnHost(resource_group, location, cluster.id)
        self.assertCanRunJobInContainer(resource_group, location, cluster.id)

        # Test cluster deletion
        self.client.clusters.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, self.cluster_name).result()
        Helpers.assert_existing_clusters_are(self, self.client, resource_group.name, [])

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    def test_setup_task_execution(self, resource_group, location, storage_account, storage_account_key):
        """Tests setup task execution.
        """
        cluster = Helpers.create_cluster(
            self.client, location, resource_group.name, self.cluster_name, 'STANDARD_D1', 1,
            storage_account.name, storage_account_key,
            setup_task_cmd='echo $GREETING $SECRET_GREETING',
            setup_task_env={'GREETING': 'setup task'},
            setup_task_secrets={'SECRET_GREETING': 'has a secret'})  # type: models.Cluster

        # Verify that the cluster is reported in the list of clusters
        Helpers.assert_existing_clusters_are(self, self.client, resource_group.name, [self.cluster_name])

        # Verify that one node is allocated and become available
        self.assertEqual(
            Helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, 1,
                                   Helpers.NODE_STARTUP_TIMEOUT_SEC), 1)

        # Check that server doesn't return values for secrets
        self.assertEqual(len(cluster.node_setup.setup_task.secrets), 1)
        self.assertEqual(cluster.node_setup.setup_task.secrets[0].name, 'SECRET_GREETING')
        self.assertIsNone(cluster.node_setup.setup_task.secrets[0].value)
        # Verify that the setup task is completed by checking generated output. BatchAI reports a path which was auto-
        # generated for storing setup output logs.
        setup_task_output_path = cluster.node_setup.setup_task.std_out_err_path_suffix
        nodes = Helpers.get_node_ids(self.client, resource_group.name, self.cluster_name)
        self.assertEqual(len(nodes), 1)
        node_id = nodes[0]
        Helpers.assert_file_in_file_share(self, storage_account.name, storage_account_key,
                                          setup_task_output_path,
                                          'stdout-{0}.txt'.format(node_id),
                                          u'setup task has a secret\n')
        Helpers.assert_file_in_file_share(self, storage_account.name, storage_account_key,
                                          setup_task_output_path, 'stderr-{0}.txt'.format(node_id), u'')
        self.client.clusters.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, self.cluster_name).result()

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    def test_cluster_resizing(self, resource_group, location, storage_account, storage_account_key):
        """Tests manual cluster resizing"""
        cluster = Helpers.create_cluster(
            self.client, location, resource_group.name, self.cluster_name, 'STANDARD_D1', 1,
            storage_account.name, storage_account_key)

        # Verify that one node is allocated and become available
        self.assertEqual(
            Helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, 1,
                                   Helpers.NODE_STARTUP_TIMEOUT_SEC), 1)
        Helpers.assert_remote_login_info_reported_for_nodes(self, self.client, resource_group.name,
                                                            self.cluster_name, 1)

        self.assertCanResizeCluster(resource_group, 0)
        self.assertCanResizeCluster(resource_group, 1)

        # Verify that cluster able to run tasks after resizing.
        self.assertCanRunJobOnHost(resource_group, location, cluster.id)
        self.client.clusters.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, self.cluster_name).result()

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    def test_auto_scaling(self, resource_group, location, storage_account, storage_account_key):
        """Tests auto-scaling"""
        # Create the cluster with no nodes.
        cluster = Helpers.create_cluster(
            self.client, location, resource_group.name, self.cluster_name, 'STANDARD_D1', 0,
            storage_account.name, storage_account_key)

        # Switch the cluster into auto-scale mode
        self.client.clusters.update(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, self.cluster_name,
                                    scale_settings=models.ScaleSettings(
                                        auto_scale=models.AutoScaleSettings(
                                            minimum_node_count=0,
                                            maximum_node_count=1)))

        # Submit a task. BatchAI must increase the number of nodes to execute the task.
        self.assertCanRunJobOnHost(resource_group, location, cluster.id, timeout_sec=Helpers.AUTO_SCALE_TIMEOUT_SEC)

        # Verify that cluster downsized to zero since there are no more jobs for it
        self.assertEqual(
            Helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, 0,
                                   Helpers.NODE_STARTUP_TIMEOUT_SEC), 0)
        self.client.clusters.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, self.cluster_name).result()

    def assertCanRunJobInContainer(self, resource_group, location, cluster_id, timeout_sec=Helpers.MINUTE):
        self.assertCanRunJob(resource_group, location, cluster_id, 'container_job',
                             models.ContainerSettings(image_source_registry=models.ImageSourceRegistry(image="ubuntu")),
                             timeout_sec)

    def assertCanRunJobOnHost(self, resource_group, location, cluster_id, timeout_sec=Helpers.MINUTE):
        self.assertCanRunJob(resource_group, location, cluster_id, 'host_job', None, timeout_sec)

    def assertCanRunJob(self, resource_group, location, cluster_id, job_name, container_settings, timeout_sec):
        Helpers.create_custom_job(self.client, resource_group.name, cluster_id, job_name, 1,
                                  'echo hello | tee $AZ_BATCHAI_OUTPUT_OUTPUTS/hi.txt', container=container_settings)

        # Verify if the job finishes reasonably fast.
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job_name, timeout_sec),
            models.ExecutionState.succeeded)

        # Verify if output files and standard output files are available and contain expected greeting.
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job_name, 'OUTPUTS',
                                     {u'hi.txt': u'hello\n'})
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job_name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'hello\n', u'stderr.txt': ''})

    def assertCanResizeCluster(self, resource_group, target):
        self.client.clusters.update(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, self.cluster_name,
                                    scale_settings=models.ScaleSettings(
                                        manual=models.ManualScaleSettings(target_node_count=target)))
        self.assertEqual(
            Helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, target,
                                   Helpers.NODE_STARTUP_TIMEOUT_SEC),
            target)
        Helpers.assert_remote_login_info_reported_for_nodes(self, self.client, resource_group.name,
                                                            self.cluster_name, target)
