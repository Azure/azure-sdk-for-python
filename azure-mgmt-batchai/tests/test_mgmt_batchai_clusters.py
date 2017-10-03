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

from . import helpers


class ClusterTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(ClusterTestCase, self).setUp()
        self.client = self.create_mgmt_client(BatchAIManagementClient)  # type: BatchAIManagementClient
        self.cluster_name = self.get_resource_name('cluster')

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    def test_creation_and_deletion(self, resource_group, location, storage_account, storage_account_key):
        """Tests basic use-case scenario.

        1. Create cluster
        2. Execute a task on the host
        3. Execute a task in a docker container
        4. Delete cluster
        """
        cluster = helpers.create_cluster(
            self.client, location, resource_group.name, self.cluster_name, 'STANDARD_D1', 1,
            storage_account.name, storage_account_key)

        self.assertEqual(cluster.name, self.cluster_name)
        self.assertIsNone(cluster.errors)
        self.assertEqual(cluster.vm_size, 'STANDARD_D1')

        # Verify that the cluster is reported in the list of clusters
        helpers.assert_existing_clusters_are(self, self.client, resource_group.name, [self.cluster_name])

        # Verify that one node is allocated and become available
        self.assertEqual(
            helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, 1,
                                   helpers.NODE_STARTUP_TIMEOUT_SEC), 1)
        helpers.assert_remote_login_info_reported_for_nodes(self, self.client, resource_group.name,
                                                            self.cluster_name, 1)

        # Verify that the cluster able to run tasks.
        self.assertCanRunJobOnHost(resource_group, location, cluster.id)
        self.assertCanRunJobInContainer(resource_group, location, cluster.id)

        # Test cluster deletion
        self.client.clusters.delete(resource_group.name, self.cluster_name).result()
        helpers.assert_existing_clusters_are(self, self.client, resource_group.name, [])

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    def test_setup_task_execution(self, resource_group, location, storage_account, storage_account_key):
        """Tests setup task execution.
        """
        helpers.create_cluster(
            self.client, location, resource_group.name, self.cluster_name, 'STANDARD_D1', 1,
            storage_account.name, storage_account_key,
            setup_task_cmd='echo $GREETING',
            setup_task_env={"GREETING": "setup task"})

        # Verify that the cluster is reported in the list of clusters
        helpers.assert_existing_clusters_are(self, self.client, resource_group.name, [self.cluster_name])

        # Verify that one node is allocated and become available
        self.assertEqual(
            helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, 1,
                                   helpers.NODE_STARTUP_TIMEOUT_SEC), 1)

        # Verify that the setup task is completed by checking generated output
        setup_task_output_path = '{0}/{1}/clusters/{2}'.format(self.client.config.subscription_id,
                                                               resource_group.name, self.cluster_name)
        nodes = helpers.get_node_ids(self.client, resource_group.name, self.cluster_name)
        self.assertEqual(len(nodes), 1)
        node_id = nodes[0]
        helpers.assert_file_in_file_share(self, storage_account.name, storage_account_key,
                                          setup_task_output_path, 'stdout-{0}.txt'.format(node_id), u'setup task\n')
        helpers.assert_file_in_file_share(self, storage_account.name, storage_account_key,
                                          setup_task_output_path, 'stderr-{0}.txt'.format(node_id), u'')
        self.client.clusters.delete(resource_group.name, self.cluster_name).result()

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    def test_cluster_resizing(self, resource_group, location, storage_account, storage_account_key):
        """Tests manual cluster resizing"""
        cluster = helpers.create_cluster(
            self.client, location, resource_group.name, self.cluster_name, 'STANDARD_D1', 1,
            storage_account.name, storage_account_key)

        # Verify that one node is allocated and become available
        self.assertEqual(
            helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, 1,
                                   helpers.NODE_STARTUP_TIMEOUT_SEC), 1)
        helpers.assert_remote_login_info_reported_for_nodes(self, self.client, resource_group.name,
                                                            self.cluster_name, 1)

        self.assertCanResizeCluster(resource_group, 0)
        self.assertCanResizeCluster(resource_group, 1)

        # Verify that cluster able to run tasks after resizing.
        self.assertCanRunJobOnHost(resource_group, location, cluster.id)
        self.client.clusters.delete(resource_group.name, self.cluster_name).result()

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    def test_auto_scaling(self, resource_group, location, storage_account, storage_account_key):
        """Tests auto-scaling"""
        # Create the cluster with no nodes.
        cluster = helpers.create_cluster(
            self.client, location, resource_group.name, self.cluster_name, 'STANDARD_D1', 0,
            storage_account.name, storage_account_key)

        # Switch the cluster into auto-scale mode
        self.client.clusters.update(resource_group.name, self.cluster_name,
                                    scale_settings=models.ScaleSettings(
                                        auto_scale=models.AutoScaleSettings(
                                            minimum_node_count=0,
                                            maximum_node_count=1)))

        # Submit a task. BatchAI must increase the number of nodes to execute the task.
        self.assertCanRunJobOnHost(resource_group, location, cluster.id, timeout_sec=helpers.AUTO_SCALE_TIMEOUT_SEC)

        # Verify that cluster downsized to zero since there are no more jobs for it
        self.assertEqual(
            helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, 0,
                                   helpers.NODE_STARTUP_TIMEOUT_SEC), 0)
        self.client.clusters.delete(resource_group.name, self.cluster_name).result()

    def assertCanRunJobInContainer(self, resource_group, location, cluster_id, timeout_sec=helpers.MINUTE):
        self.assertCanRunJob(resource_group, location, cluster_id, 'container_job',
                             models.ContainerSettings(models.ImageSourceRegistry(image="ubuntu")), timeout_sec)

    def assertCanRunJobOnHost(self, resource_group, location, cluster_id, timeout_sec=helpers.MINUTE):
        self.assertCanRunJob(resource_group, location, cluster_id, 'host_job', None, timeout_sec)

    def assertCanRunJob(self, resource_group, location, cluster_id, job_name, container_settings, timeout_sec):
        helpers.create_custom_job(self.client, resource_group.name, location, cluster_id, job_name, 1,
                                  'echo hello | tee $AZ_BATCHAI_OUTPUT_OUTPUTS/hi.txt', container=container_settings)

        # Verify if the job finishes reasonably fast.
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job_name, timeout_sec),
            models.ExecutionState.succeeded)

        # Verify if output files and standard output files are available and contain expected greeting.
        helpers.assert_job_files_are(self, self.client, resource_group.name, job_name, 'OUTPUTS',
                                     {u'hi.txt': u'hello\n'})
        helpers.assert_job_files_are(self, self.client, resource_group.name, job_name,
                                     helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'hello\n', u'stderr.txt': ''})

    def assertCanResizeCluster(self, resource_group, target):
        self.client.clusters.update(resource_group.name, self.cluster_name, scale_settings=models.ScaleSettings(
            manual=models.ManualScaleSettings(target_node_count=target)))
        self.assertEqual(
            helpers.wait_for_nodes(self.is_live, self.client, resource_group.name, self.cluster_name, target,
                                   helpers.NODE_STARTUP_TIMEOUT_SEC),
            target)
        helpers.assert_remote_login_info_reported_for_nodes(self, self.client, resource_group.name,
                                                            self.cluster_name, target)
