# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
import re
from devtools_testutils import AzureMgmtTestCase, StorageAccountPreparer
from devtools_testutils import ResourceGroupPreparer
from msrestazure.azure_exceptions import CloudError

import azure.mgmt.batchai.models as models
from azure.mgmt.batchai import BatchAIManagementClient
from . import helpers


class JobTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(JobTestCase, self).setUp()
        self.client = self.create_mgmt_client(BatchAIManagementClient)  # type: BatchAIManagementClient

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_job_creation_and_deletion(self, resource_group, location, cluster):
        """Tests simple scenario for a job - submit, check results, delete."""
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'job', 1,
                                        'echo hi | tee {0}/hi.txt'.format(helpers.JOB_OUTPUT_DIRECTORY_PATH_ENV),
                                        container=models.ContainerSettings(models.ImageSourceRegistry('ubuntu')))
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, helpers.MINUTE),
            models.ExecutionState.succeeded)
        # Check standard job output
        helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'hi\n', u'stderr.txt': u''})
        # Check job's output
        helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     helpers.JOB_OUTPUT_DIRECTORY_ID,
                                     {u'hi.txt': u'hi\n'})
        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_running_job_deletion(self, resource_group, location, cluster):
        """Tests deletion of a running job."""
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'job', 1,
                                        'sleep 600')
        self.assertEqual(
            helpers.wait_for_job_start_running(self.is_live, self.client, resource_group.name, job.name,
                                               helpers.MINUTE),
            models.ExecutionState.running)

        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_running_job_termination(self, resource_group, location, cluster):
        """Tests termination of a running job."""
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'longrunning', 1,
                                        'sleep 600')
        self.assertEqual(
            helpers.wait_for_job_start_running(self.is_live, self.client, resource_group.name, job.name,
                                               helpers.MINUTE),
            models.ExecutionState.running)

        self.client.jobs.terminate(resource_group.name, job.name).result()
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, helpers.MINUTE),
            models.ExecutionState.failed)

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer(target_nodes=0, wait=False)
    def test_queued_job_termination(self, resource_group, location, cluster):
        """Tests termination of a job in queued state."""
        # Create a job which will be in queued state because the cluster has no compute nodes.
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'job', 1, 'true')

        self.client.jobs.terminate(resource_group.name, job.name).result()
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, helpers.MINUTE),
            models.ExecutionState.failed)

        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_completed_job_termination(self, resource_group, location, cluster):
        """Tests termination of completed job."""
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'job', 1, 'true')
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, helpers.MINUTE),
            models.ExecutionState.succeeded)

        # termination of completed job is NOP and must not change the execution state.
        self.client.jobs.terminate(resource_group.name, job.name).result()
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, helpers.MINUTE),
            models.ExecutionState.succeeded)

        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_failed_job_reporting(self, resource_group, location, cluster):
        """Tests if job failure is reported correctly."""
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'job', 1,
                                        'false')
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            helpers.MINUTE),
            models.ExecutionState.failed)

        job = self.client.jobs.get(resource_group.name, job.name)
        self.assertEqual(job.execution_info.exit_code, 1)
        self.assertEqual(len(job.execution_info.errors), 1)
        self.assertEqual(job.execution_info.errors[0].code, 'JobFailed')
        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_job_preparation_host(self, resource_group, location, cluster):
        """Tests job preparation execution for a job running on a host."""
        # create a job with job preparation which populates input data in $AZ_BATCHAI_INPUT_INPUT/hi.txt
        job = helpers.create_custom_job(
            self.client, resource_group.name, location, cluster.id, 'job', 1,
            'cat $AZ_BATCHAI_INPUT_INPUT/hi.txt',
            'mkdir -p $AZ_BATCHAI_INPUT_INPUT && echo hello | tee $AZ_BATCHAI_INPUT_INPUT/hi.txt')
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            helpers.MINUTE),
            models.ExecutionState.succeeded)

        helpers.assert_job_files_are(self, self.client, resource_group.name, job.name, 'stdouterr',
                                     {u'stdout.txt': u'hello\n',
                                      u'stderr.txt': u'',
                                      u'stdout-job_prep.txt': u'hello\n',
                                      u'stderr-job_prep.txt': u''})
        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_job_preparation_container(self, resource_group, location, cluster):
        """Tests job preparation execution for a job running in a container."""
        # create a job with job preparation which populates input data in $AZ_BATCHAI_INPUT_INPUT/hi.txt
        job = helpers.create_custom_job(
            self.client, resource_group.name, location, cluster.id, 'job', 1,
            'cat $AZ_BATCHAI_INPUT_INPUT/hi.txt',
            'mkdir -p $AZ_BATCHAI_INPUT_INPUT && echo hello | tee $AZ_BATCHAI_INPUT_INPUT/hi.txt',
            container=models.ContainerSettings(models.ImageSourceRegistry('ubuntu')))
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            helpers.MINUTE),
            models.ExecutionState.succeeded)

        helpers.assert_job_files_are(self, self.client, resource_group.name, job.name, 'stdouterr',
                                     {u'stdout.txt': u'hello\n',
                                      u'stderr.txt': u'',
                                      u'stdout-job_prep.txt': u'hello\n',
                                      u'stderr-job_prep.txt': u''})
        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_job_host_preparation_failure_reporting(self, resource_group, location, cluster):
        """Tests if job preparation failure is reported correctly."""
        # create a job with failing job preparation
        job = helpers.create_custom_job(
            self.client, resource_group.name, location, cluster.id, 'job', 1, 'true', 'false')
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            helpers.MINUTE),
            models.ExecutionState.failed)

        job = self.client.jobs.get(resource_group.name, job.name)
        self.assertEqual(job.execution_info.exit_code, 1)
        self.assertEqual(len(job.execution_info.errors), 1)
        self.assertEqual(job.execution_info.errors[0].code, 'JobNodePreparationFailed')
        print(job.serialize())
        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer()
    def test_job_container_preparation_failure_reporting(self, resource_group, location, cluster):
        """Tests if job preparation failure is reported correctly."""
        # create a job with failing job preparation
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'job', 1, 'true',
                                        'false',
                                        container=models.ContainerSettings(models.ImageSourceRegistry('ubuntu')))
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            helpers.MINUTE),
            models.ExecutionState.failed)

        job = self.client.jobs.get(resource_group.name, job.name)
        self.assertEqual(job.execution_info.exit_code, 1)
        self.assertEqual(len(job.execution_info.errors), 1)
        self.assertEqual(job.execution_info.errors[0].code, 'JobNodePreparationFailed')
        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer(target_nodes=2)
    def test_password_less_ssh(self, resource_group, location, cluster):
        """Tests if password-less ssh is configured on hosts."""
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'job', 2,
                                        'ssh 10.0.0.4 echo done && ssh 10.0.0.5 echo done')
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            helpers.MINUTE),
            models.ExecutionState.succeeded)

        job = self.client.jobs.get(resource_group.name, job.name)

        helpers.assert_job_files_are(self, self.client, resource_group.name, job.name, 'stdouterr',
                                     {u'stdout.txt': u'done\ndone\n',
                                      u'stderr.txt': re.compile('Permanently added.*')})
        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

    @ResourceGroupPreparer(location=helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=helpers.LOCATION, playback_fake_resource=helpers.FAKE_STORAGE)
    @helpers.ClusterPreparer(target_nodes=2)
    def test_password_less_ssh_in_container(self, resource_group, location, cluster):
        """Tests if password-less ssh is configured in containers."""
        job = helpers.create_custom_job(self.client, resource_group.name, location, cluster.id, 'job', 2,
                                        'ssh 10.0.0.5 echo done && ssh 10.0.0.5 echo done',
                                        container=models.ContainerSettings(models.ImageSourceRegistry('ubuntu')))
        self.assertEqual(
            helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            helpers.MINUTE),
            models.ExecutionState.succeeded)

        job = self.client.jobs.get(resource_group.name, job.name)
        helpers.assert_job_files_are(self, self.client, resource_group.name, job.name, 'stdouterr',
                                     {u'stdout.txt': u'done\ndone\n',
                                      u'stderr.txt': re.compile('Permanently added.*')})
        self.client.jobs.delete(resource_group.name, job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, job.name))

