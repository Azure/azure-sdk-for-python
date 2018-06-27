# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
import re
from azure.storage.blob import BlockBlobService
from azure.storage.file import FileService
from devtools_testutils import AzureMgmtTestCase, StorageAccountPreparer
from devtools_testutils import ResourceGroupPreparer
from msrestazure.azure_exceptions import CloudError

import azure.mgmt.batchai.models as models
from azure.mgmt.batchai import BatchAIManagementClient
from helpers import Helpers, ClusterPreparer


class JobTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(JobTestCase, self).setUp()
        self.client = Helpers.create_batchai_client(self)  # type: BatchAIManagementClient

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_job_creation_and_deletion(self, resource_group, location, cluster, storage_account, storage_account_key):
        """Tests simple scenario for a job - submit, check results, delete."""
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 1,
                                        'echo hi | tee {0}/hi.txt'.format(Helpers.JOB_OUTPUT_DIRECTORY_PATH_ENV),
                                        container=models.ContainerSettings(
                                            image_source_registry=models.ImageSourceRegistry(image='ubuntu'))
                                        )  # type: models.Job
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, Helpers.MINUTE),
            models.ExecutionState.succeeded)
        # Check standard job output
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'hi\n', u'stderr.txt': u''})
        # Check job's output
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     Helpers.JOB_OUTPUT_DIRECTORY_ID,
                                     {u'hi.txt': u'hi\n'})
        # Check that we can access the output files directly in storage using path segment returned by the server
        Helpers.assert_file_in_file_share(self, storage_account.name, storage_account_key,
                                          job.job_output_directory_path_segment + '/' + Helpers.STDOUTERR_FOLDER_NAME,
                                          'stdout.txt', u'hi\n')
        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_running_job_deletion(self, resource_group, location, cluster):
        """Tests deletion of a running job."""
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 1, 'sleep 600')
        self.assertEqual(
            Helpers.wait_for_job_start_running(self.is_live, self.client, resource_group.name, job.name,
                                               Helpers.MINUTE),
            models.ExecutionState.running)

        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_running_job_termination(self, resource_group, location, cluster):
        """Tests termination of a running job."""
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'longrunning', 1, 'sleep 600')
        self.assertEqual(
            Helpers.wait_for_job_start_running(self.is_live, self.client, resource_group.name, job.name,
                                               Helpers.MINUTE),
            models.ExecutionState.running)

        self.client.jobs.terminate(
            resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME, job.name).result()
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, Helpers.MINUTE),
            models.ExecutionState.failed)

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer(target_nodes=0, wait=False)
    def test_queued_job_termination(self, resource_group, location, cluster):
        """Tests termination of a job in queued state."""
        # Create a job which will be in queued state because the cluster has no compute nodes.
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 1, 'true')

        self.client.jobs.terminate(
            resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME, job.name).result()
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, Helpers.MINUTE),
            models.ExecutionState.failed)

        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_completed_job_termination(self, resource_group, location, cluster):
        """Tests termination of completed job."""
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 1, 'true')
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, Helpers.MINUTE),
            models.ExecutionState.succeeded)

        # termination of completed job is NOP and must not change the execution state.
        self.client.jobs.terminate(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                   job.name).result()
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, Helpers.MINUTE),
            models.ExecutionState.succeeded)

        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_failed_job_reporting(self, resource_group, location, cluster):
        """Tests if job failure is reported correctly."""
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 1, 'false')
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            Helpers.MINUTE),
            models.ExecutionState.failed)

        job = self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                   job.name)
        self.assertEqual(job.execution_info.exit_code, 1)
        self.assertEqual(len(job.execution_info.errors), 1)
        self.assertEqual(job.execution_info.errors[0].code, 'JobFailed')
        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_job_preparation_host(self, resource_group, location, cluster):
        """Tests job preparation execution for a job running on a host."""
        # create a job with job preparation which populates input data in $AZ_BATCHAI_INPUT_INPUT/hi.txt
        job = Helpers.create_custom_job(
            self.client, resource_group.name, cluster.id, 'job', 1,
            'cat $AZ_BATCHAI_INPUT_INPUT/hi.txt',
            'mkdir -p $AZ_BATCHAI_INPUT_INPUT && echo hello | tee $AZ_BATCHAI_INPUT_INPUT/hi.txt')
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            Helpers.MINUTE),
            models.ExecutionState.succeeded)

        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'hello\n',
                                      u'stderr.txt': u'',
                                      u'stdout-job_prep.txt': u'hello\n',
                                      u'stderr-job_prep.txt': u''})
        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_job_preparation_container(self, resource_group, location, cluster):
        """Tests job preparation execution for a job running in a container."""
        # create a job with job preparation which populates input data in $AZ_BATCHAI_INPUT_INPUT/hi.txt
        job = Helpers.create_custom_job(
            self.client, resource_group.name, cluster.id, 'job', 1,
            'cat $AZ_BATCHAI_INPUT_INPUT/hi.txt',
            'mkdir -p $AZ_BATCHAI_INPUT_INPUT && echo hello | tee $AZ_BATCHAI_INPUT_INPUT/hi.txt',
            container=models.ContainerSettings(
                image_source_registry=models.ImageSourceRegistry(image='ubuntu')))
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            Helpers.MINUTE),
            models.ExecutionState.succeeded)

        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'hello\n',
                                      u'stderr.txt': u'',
                                      u'stdout-job_prep.txt': u'hello\n',
                                      u'stderr-job_prep.txt': u''})
        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_job_host_preparation_failure_reporting(self, resource_group, location, cluster):
        """Tests if job preparation failure is reported correctly."""
        # create a job with failing job preparation
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 1, 'true', 'false')
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            Helpers.MINUTE),
            models.ExecutionState.failed)

        job = self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                   job.name)
        self.assertEqual(job.execution_info.exit_code, 1)
        self.assertEqual(len(job.execution_info.errors), 1)
        self.assertEqual(job.execution_info.errors[0].code, 'JobPreparationFailed')
        print(job.serialize())
        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer()
    def test_job_container_preparation_failure_reporting(self, resource_group, location, cluster):
        """Tests if job preparation failure is reported correctly."""
        # create a job with failing job preparation
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 1, 'true', 'false',
                                        container=models.ContainerSettings(
                                            image_source_registry=models.ImageSourceRegistry(image='ubuntu')))
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            Helpers.MINUTE),
            models.ExecutionState.failed)

        job = self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                   job.name)
        self.assertEqual(job.execution_info.exit_code, 1)
        self.assertEqual(len(job.execution_info.errors), 1)
        self.assertEqual(job.execution_info.errors[0].code, 'JobPreparationFailed')
        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer(target_nodes=2)
    def test_password_less_ssh(self, resource_group, location, cluster):
        """Tests if password-less ssh is configured on hosts."""
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 2,
                                        'ssh 10.0.0.4 echo done && ssh 10.0.0.5 echo done')
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            Helpers.MINUTE),
            models.ExecutionState.succeeded)

        job = self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                   job.name)

        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'done\ndone\n',
                                      u'stderr.txt': re.compile('Permanently added.*')})
        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer(target_nodes=2)
    def test_password_less_ssh_in_container(self, resource_group, location, cluster):
        """Tests if password-less ssh is configured in containers."""
        job = Helpers.create_custom_job(self.client, resource_group.name, cluster.id, 'job', 2,
                                        'ssh 10.0.0.5 echo done && ssh 10.0.0.5 echo done',
                                        container=models.ContainerSettings(
                                            image_source_registry=models.ImageSourceRegistry(image='ubuntu')))
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name,
                                            Helpers.MINUTE),
            models.ExecutionState.succeeded)

        job = self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                   job.name)
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'done\ndone\n',
                                      u'stderr.txt': re.compile('Permanently added.*')})
        self.client.jobs.delete(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                job.name).result()
        self.assertRaises(CloudError, lambda: self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME,
                                                                   Helpers.DEFAULT_EXPERIMENT_NAME, job.name))

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer(target_nodes=1)
    def test_job_level_mounting(self, resource_group, location, cluster, storage_account, storage_account_key):
        """Tests if it's possible to mount external file systems for a job."""
        job_name = 'job'

        # Create file share and container to mount on the job level
        if storage_account.name != Helpers.FAKE_STORAGE.name:
            files = FileService(storage_account.name, storage_account_key)
            files.create_share('jobshare', fail_on_exist=False)
            blobs = BlockBlobService(storage_account.name, storage_account_key)
            blobs.create_container('jobcontainer', fail_on_exist=False)

        job = self.client.jobs.create(
            resource_group.name,
            Helpers.DEFAULT_WORKSPACE_NAME,
            Helpers.DEFAULT_EXPERIMENT_NAME,
            job_name,
            parameters=models.JobCreateParameters(
                cluster=models.ResourceId(id=cluster.id),
                node_count=1,
                mount_volumes=models.MountVolumes(
                    azure_file_shares=[
                        models.AzureFileShareReference(
                            account_name=storage_account.name,
                            azure_file_url='https://{0}.file.core.windows.net/{1}'.format(
                                storage_account.name, 'jobshare'),
                            relative_mount_path='job_afs',
                            credentials=models.AzureStorageCredentialsInfo(
                                account_key=storage_account_key
                            ),
                        )
                    ],
                    azure_blob_file_systems=[
                        models.AzureBlobFileSystemReference(
                            account_name=storage_account.name,
                            container_name='jobcontainer',
                            relative_mount_path='job_bfs',
                            credentials=models.AzureStorageCredentialsInfo(
                                account_key=storage_account_key
                            ),
                        )
                    ]
                ),
                # Put standard output on cluster level AFS to check that the job has access to it.
                std_out_err_path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(Helpers.AZURE_FILES_MOUNTING_PATH),
                # Create two output directories on job level AFS and blobfuse.
                output_directories=[
                    models.OutputDirectory(id='OUTPUT1', path_prefix='$AZ_BATCHAI_JOB_MOUNT_ROOT/job_afs'),
                    models.OutputDirectory(id='OUTPUT2', path_prefix='$AZ_BATCHAI_JOB_MOUNT_ROOT/job_bfs')
                ],
                # Check that the job preparation has access to job level file systems.
                job_preparation=models.JobPreparation(
                    command_line='echo afs > $AZ_BATCHAI_OUTPUT_OUTPUT1/prep_afs.txt; '
                                 'echo bfs > $AZ_BATCHAI_OUTPUT_OUTPUT2/prep_bfs.txt; '
                                 'echo done'
                ),
                # Check that the job has access to job
                custom_toolkit_settings=models.CustomToolkitSettings(
                    command_line='echo afs > $AZ_BATCHAI_OUTPUT_OUTPUT1/job_afs.txt; '
                                 'echo bfs > $AZ_BATCHAI_OUTPUT_OUTPUT2/job_bfs.txt; '
                                 'mkdir $AZ_BATCHAI_OUTPUT_OUTPUT1/afs; '
                                 'echo afs > $AZ_BATCHAI_OUTPUT_OUTPUT1/afs/job_afs.txt; '
                                 'mkdir $AZ_BATCHAI_OUTPUT_OUTPUT2/bfs; '
                                 'echo bfs > $AZ_BATCHAI_OUTPUT_OUTPUT2/bfs/job_bfs.txt; '
                                 'echo done'
                )
            )
        ).result()
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, Helpers.MINUTE),
            models.ExecutionState.succeeded)

        job = self.client.jobs.get(resource_group.name, Helpers.DEFAULT_WORKSPACE_NAME, Helpers.DEFAULT_EXPERIMENT_NAME,
                                   job.name)
        # Assert job and job prep standard output is populated on cluster level filesystem
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'done\n', u'stderr.txt': u'',
                                      u'stdout-job_prep.txt': u'done\n', u'stderr-job_prep.txt': u''})
        # Assert files are generated on job level AFS
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name, 'OUTPUT1',
                                     {u'job_afs.txt': u'afs\n', u'prep_afs.txt': u'afs\n', u'afs': None})
        # Assert files are generated on job level blobfuse
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name, 'OUTPUT2',
                                     {u'job_bfs.txt': u'bfs\n', u'prep_bfs.txt': u'bfs\n', u'bfs': None})
        # Assert subfolders are available via API
        Helpers.assert_job_files_in_path_are(self, self.client, resource_group.name, job.name, 'OUTPUT1',
                                             'afs', {u'job_afs.txt': u'afs\n'})
        Helpers.assert_job_files_in_path_are(self, self.client, resource_group.name, job.name, 'OUTPUT2',
                                             'bfs', {u'job_bfs.txt': u'bfs\n'})

        # Assert that we can access the output files created on job level mount volumes directly in storage using path
        # segment returned by the server.
        if storage_account.name != Helpers.FAKE_STORAGE.name:
            files = FileService(storage_account.name, storage_account_key)
            self.assertTrue(
                files.exists('jobshare', job.job_output_directory_path_segment +
                             '/' + Helpers.OUTPUT_DIRECTORIES_FOLDER_NAME, 'job_afs.txt'))
            blobs = BlockBlobService(storage_account.name, storage_account_key)
            self.assertTrue(
                blobs.exists('jobcontainer', job.job_output_directory_path_segment +
                             '/' + Helpers.OUTPUT_DIRECTORIES_FOLDER_NAME + '/job_bfs.txt'))
        # After the job is done the filesystems should be unmounted automatically, check this by submitting a new job.
        checker = self.client.jobs.create(
            resource_group.name,
            Helpers.DEFAULT_WORKSPACE_NAME,
            Helpers.DEFAULT_EXPERIMENT_NAME,
            'checker',
            parameters=models.JobCreateParameters(
                location=location,
                cluster=models.ResourceId(id=cluster.id),
                node_count=1,
                std_out_err_path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(Helpers.AZURE_FILES_MOUNTING_PATH),
                custom_toolkit_settings=models.CustomToolkitSettings(
                    command_line='echo job; df | grep -E "job_bfs|job_afs"'
                )
            )
        ).result()
        # Check the job failed because there are not job level mount volumes anymore
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, checker.name,
                                            Helpers.MINUTE),
            models.ExecutionState.failed)
        # Check that the cluster level AFS was still mounted
        Helpers.assert_job_files_are(self, self.client, resource_group.name, checker.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'job\n', u'stderr.txt': u''})

    @ResourceGroupPreparer(location=Helpers.LOCATION)
    @StorageAccountPreparer(name_prefix='psdk', location=Helpers.LOCATION, playback_fake_resource=Helpers.FAKE_STORAGE)
    @ClusterPreparer(target_nodes=1)
    def test_job_environment_variables_and_secrets(self, resource_group, location, cluster):
        """Tests if it's possible to mount external file systems for a job."""
        job_name = 'job'
        job = self.client.jobs.create(
            resource_group.name,
            Helpers.DEFAULT_WORKSPACE_NAME,
            Helpers.DEFAULT_EXPERIMENT_NAME,
            job_name,
            parameters=models.JobCreateParameters(
                cluster=models.ResourceId(id=cluster.id),
                node_count=1,
                std_out_err_path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(Helpers.AZURE_FILES_MOUNTING_PATH),
                environment_variables=[
                    models.EnvironmentVariable(name='VARIABLE', value='VALUE')
                ],
                secrets=[
                    models.EnvironmentVariableWithSecretValue(name='SECRET_VARIABLE', value='SECRET')
                ],
                # Check that the job preparation has access to env variables and secrets.
                job_preparation=models.JobPreparation(
                    command_line='echo $VARIABLE $SECRET_VARIABLE'
                ),
                # Check that the job has access to env variables and secrets.
                custom_toolkit_settings=models.CustomToolkitSettings(
                    command_line='echo $VARIABLE $SECRET_VARIABLE'
                )
            )
        ).result()  # type: models.Job
        self.assertEqual(
            Helpers.wait_for_job_completion(self.is_live, self.client, resource_group.name, job.name, Helpers.MINUTE),
            models.ExecutionState.succeeded)
        # Check that environment variables are reported by the server.
        self.assertEqual(len(job.environment_variables), 1)
        self.assertEqual(job.environment_variables[0].name, 'VARIABLE')
        self.assertEqual(job.environment_variables[0].value, 'VALUE')
        # Check that secrets are reported back by server, but value is not reported.
        self.assertEqual(len(job.secrets), 1)
        self.assertEqual(job.secrets[0].name, 'SECRET_VARIABLE')
        self.assertIsNone(job.secrets[0].value)
        # Check that job and job prep had access to the env variables and secrets.
        Helpers.assert_job_files_are(self, self.client, resource_group.name, job.name,
                                     Helpers.STANDARD_OUTPUT_DIRECTORY_ID,
                                     {u'stdout.txt': u'VALUE SECRET\n', u'stderr.txt': u'',
                                      u'stdout-job_prep.txt': u'VALUE SECRET\n', u'stderr-job_prep.txt': u''})
