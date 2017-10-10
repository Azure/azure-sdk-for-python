# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
import time

import requests
import six
from azure.mgmt.batchai import BatchAIManagementClient
from azure.mgmt.batchai import models
from azure.storage.file import FileService
from azure_devtools.scenario_tests import AzureTestError
from devtools_testutils import AzureMgmtTestCase, FakeStorageAccount, AzureMgmtPreparer, StorageAccountPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM, ResourceGroupPreparer

MINUTE = 60
# Node allocation should not take longer than 15 minutes.
NODE_STARTUP_TIMEOUT_SEC = 15 * MINUTE

# Auto scaling should not take longer than 30 minutes.
AUTO_SCALE_TIMEOUT_SEC = 30 * MINUTE

# User name and password for admin user configured on compute cluster and file servers.
ADMIN_USER_NAME = 'demoUser'
ADMIN_USER_PASSWORD = 'Dem0Pa$$w0rd'

# Name of the Azure Files which will be create for each cluster.
AZURE_FILES_NAME = 'share'
# Name of the directory for mounting Azure Files on cluster.
AZURE_FILES_MOUNTING_PATH = 'azfiles'

# Job's output directory configuration.
JOB_OUTPUT_DIRECTORY_PATH = '$AZ_BATCHAI_MOUNT_ROOT/{0}/'.format(AZURE_FILES_MOUNTING_PATH)
JOB_OUTPUT_DIRECTORY_ID = 'OUTPUTS'
# Environment variable used by jobs to access the output directory.
JOB_OUTPUT_DIRECTORY_PATH_ENV = '$AZ_BATCHAI_OUTPUT_{0}'.format(JOB_OUTPUT_DIRECTORY_ID)

# Polling interval for checking nodes allocation, jobs completion and so on.
_POLL_INTERVAL_SEC = 20

# Fake storage account returned during running tests against recorded session.
FAKE_STORAGE = FakeStorageAccount(name='psdk', id='fakeid')

# ID of output directory containing job's standard output
STANDARD_OUTPUT_DIRECTORY_ID = 'stdouterr'

# Location to run tests.
LOCATION = 'eastus'

# Regular expression to validate IP address (we don't need strict validation, just a smoke test enough).
RE_ID_ADDRESS = '\d+(?:\.\d+){3}'


def sleep_before_next_poll(is_live):
    """Sleep for polling interval

    :param int is_live: True if running in live mode.
    :return: Slept time in sec.
    """
    if is_live:
        time.sleep(_POLL_INTERVAL_SEC)
    return _POLL_INTERVAL_SEC


def _create_file_share(storage_account, storage_account_key):
    """Creates Azure Files in the storage account to be mounted into a cluster

    :param str storage_account: name of the storage account.
    :param str storage_account_key: storage account key.
    """
    if storage_account == FAKE_STORAGE.name:
        return
    service = FileService(storage_account, storage_account_key)
    service.create_share(AZURE_FILES_NAME)


def create_file_server(client, location, resource_group, nfs_name, subnet_id=None):
    """Creates NFS

    :param BatchAIManagementClient client: client instance.
    :param str location: location.
    :param str resource_group: resource group name.
    :param str nfs_name: file server name.
    :param models.ResourceId subnet_id: id of the subnet.
    :return models.FileServer: created file server.
    """
    return client.file_servers.create(resource_group, nfs_name, models.FileServerCreateParameters(
        location=location,
        vm_size='STANDARD_D1',
        ssh_configuration=models.SshConfiguration(
            user_account_settings=models.UserAccountSettings(
                admin_user_name=ADMIN_USER_NAME,
                admin_user_password=ADMIN_USER_PASSWORD,
            )
        ),
        data_disks=models.DataDisks(
            disk_size_in_gb=10,
            disk_count=2,
            storage_account_type='Standard_LRS'),
        subnet=subnet_id)).result()


def create_cluster(client, location, resource_group, cluster_name, vm_size, target_nodes,
                   storage_account, storage_account_key, file_servers=None, file_systems=None,
                   subnet_id=None, setup_task_cmd=None, setup_task_env=None):
    """Creates a cluster with given parameters and mounted Azure Files

    :param BatchAIManagementClient client: client instance.
    :param str location: location.
    :param str resource_group: resource group name.
    :param str cluster_name: name of the cluster.
    :param str vm_size: vm size.
    :param int target_nodes: number of nodes.
    :param str storage_account: name of the storage account.
    :param str storage_account_key: storage account key.
    :param list(models.FileServerReference) file_servers: file servers.
    :param list(models.UnmanagedFileServerReference) file_systems: file systems.
    :param str setup_task_cmd: start task cmd line.
    :param dict[str, str] setup_task_env: environment variables for start task.
    :param str subnet_id: virtual network subnet id.
    :return models.Cluster: the created cluster
    """
    _create_file_share(storage_account, storage_account_key)
    setup_task = None
    if setup_task_cmd:
        setup_task = models.SetupTask(
            command_line=setup_task_cmd,
            environment_variables=[models.EnvironmentSetting(k, v) for k, v in setup_task_env.items()],
            std_out_err_path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(AZURE_FILES_MOUNTING_PATH))
    return client.clusters.create(
        resource_group,
        cluster_name,
        parameters=models.ClusterCreateParameters(
            location=location,
            vm_size=vm_size,
            scale_settings=models.ScaleSettings(
                manual=models.ManualScaleSettings(
                    target_node_count=target_nodes)),
            node_setup=models.NodeSetup(
                mount_volumes=models.MountVolumes(
                    azure_file_shares=[models.AzureFileShareReference(
                        azure_file_url='https://{0}.file.core.windows.net/{1}'.format(storage_account,
                                                                                      AZURE_FILES_NAME),
                        relative_mount_path=AZURE_FILES_MOUNTING_PATH,
                        account_name=storage_account,
                        credentials=models.AzureStorageCredentialsInfo(
                            account_key=storage_account_key
                        ),
                    )],
                    file_servers=file_servers,
                    unmanaged_file_systems=file_systems
                ),
                setup_task=setup_task
            ),
            subnet=subnet_id,
            user_account_settings=models.UserAccountSettings(
                admin_user_name=ADMIN_USER_NAME,
                admin_user_password=ADMIN_USER_PASSWORD
            ))).result()


def create_custom_job(client, resource_group, location, cluster_id, job_name, nodes, cmd, job_preparation_cmd=None,
                      container=None):
    """Creates custom toolkit job

    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param str location: location.
    :param str cluster_id: resource Id of the cluster.
    :param str job_name: job name.
    :param int nodes: number of nodes to execute the job.
    :param str cmd: command line to run.
    :param str or None job_preparation_cmd: Job preparation command line.
    :param models.ContainerSettings or None container: container settings to run the job.
    :return models.Job: the created job.
    """
    job_preparation = None
    if job_preparation_cmd:
        job_preparation = models.JobPreparation(job_preparation_cmd)
    return client.jobs.create(
        resource_group,
        job_name,
        parameters=models.JobCreateParameters(
            location=location,
            cluster=models.ResourceId(cluster_id),
            node_count=nodes,
            std_out_err_path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(AZURE_FILES_MOUNTING_PATH),
            output_directories=[models.OutputDirectory(
                id=JOB_OUTPUT_DIRECTORY_ID,
                path_prefix=JOB_OUTPUT_DIRECTORY_PATH,
                path_suffix="files")],
            input_directories=[models.InputDirectory(
                id='INPUT',
                path='$AZ_BATCHAI_MOUNT_ROOT/{0}/input'.format(AZURE_FILES_MOUNTING_PATH))],
            container_settings=container,
            job_preparation=job_preparation,
            custom_toolkit_settings=models.CustomToolkitSettings(
                command_line=cmd
            )
        )
    ).result()


def wait_for_nodes(is_live, client, resource_group, cluster_name, target, timeout_sec):
    """Wait for target number of nodes in a cluster become idle.

    :param bool is_live: True if running in live mode.
    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param str cluster_name: cluster name.
    :param int target: target number of node.
    :param int timeout_sec: Timeout in seconds.
    :return int: Number of idle nodes.
    """
    wait_time = 0
    while True:
        cluster = client.clusters.get(resource_group, cluster_name)
        counts = cluster.node_state_counts  # type: models.NodeStateCounts
        if counts.idle_node_count == target and cluster.allocation_state != models.AllocationState.resizing:
            return counts.idle_node_count
        if wait_time < timeout_sec:
            wait_time += sleep_before_next_poll(is_live)
        else:
            print("Cluster:")
            print(cluster.serialize())
            return counts.idle_node_count


def wait_for_job_completion(is_live, client, resource_group, job_name, timeout_sec):
    """Wait for job completion.

    :param bool is_live: True if running in live mode.
    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param str job_name: job name.
    :param int timeout_sec: Timeout in seconds.
    :return models.ExecutionState: The job's execution state.
    """
    wait_time = 0
    while True:
        job = client.jobs.get(resource_group, job_name)
        if job.execution_state in [models.ExecutionState.succeeded, models.ExecutionState.failed]:
            return job.execution_state
        if wait_time < timeout_sec:
            wait_time += sleep_before_next_poll(is_live)
        else:
            print("Job:")
            print(job.serialize())
            return job.execution_state


def wait_for_job_start_running(is_live, client, resource_group, job_name, timeout_sec):
    """Wait for job start running.

    :param bool is_live: True if running in live mode.
    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param str job_name: job name.
    :param int timeout_sec: Timeout in seconds.
    :return models.ExecutionState: The job's execution state.
    """
    wait_time = 0
    while True:
        job = client.jobs.get(resource_group, job_name)
        if job.execution_state != models.ExecutionState.queued:
            return job.execution_state
        if wait_time < timeout_sec:
            wait_time += sleep_before_next_poll(is_live)
        else:
            print("Job:")
            print(job.serialize())
            return job.execution_state


def print_file_server(file_server):
    """Output information about file server
    
    :param models.FileServer file_server: file server.
    """
    print("File server:")
    print(file_server.serialize())


def wait_for_file_server(is_live, client, resource_group, file_server_name, timeout_sec):
    """Wait for file server to become available.

    :param bool is_live: True if running in live mode.
    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param str file_server_name: cluster name.
    :param int timeout_sec: Timeout in seconds.
    :return bool: True is the file server become available.
    """
    wait_time = 0
    while True:
        server = client.file_servers.get(resource_group, file_server_name)  # type: models.FileServer
        if server.provisioning_state == models.FileServerProvisioningState.succeeded:
            return True
        if wait_time < timeout_sec:
            wait_time += sleep_before_next_poll(is_live)
        else:
            print_file_server(server)
            return False


def assert_remote_login_info_reported_for_nodes(test, client, resource_group, cluster_name, expected):
    """Checks that given number of nodes are reported for the cluster

    :param AzureMgmtTestCase test: test instance.
    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param str cluster_name: cluster
    :param int expected: expected number of nodes.
    """
    nodes = list(client.clusters.list_remote_login_information(resource_group, cluster_name))
    test.assertEqual(len(nodes), expected)
    # Check if there is a reasonable information about nodes.
    for n in nodes:  # type: models.RemoteLoginInformation
        test.assertIsNotNone(n.ip_address)
        test.assertIsNotNone(n.node_id)
        test.assertRegexpMatches(n.ip_address, RE_ID_ADDRESS)
        test.assertGreater(len(n.node_id), 0)
        test.assertGreater(n.port, 0)


def get_node_ids(client, resource_group, cluster_name):
    """Checks that given number of nodes are reported for the cluster

    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param str cluster_name: cluster
    :return list(str): list of node Ids
    """
    return [n.node_id for n in list(client.clusters.list_remote_login_information(resource_group, cluster_name))]


def assert_job_files_are(test, client, resource_group, job_name, output_directory_id, expected):
    """Checks that the given task has expected output

    :param AzureMgmtTestCase test: test instance.
    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param str job_name: job name.
    :param str output_directory_id: output directory id.
    :param dict(str, str) expected: expected content.
    """
    paged = client.jobs.list_output_files(resource_group, job_name, models.JobsListOutputFilesOptions(
        output_directory_id))
    files = paged.get(paged.current_page)
    actual = dict()
    for f in files:
        v = requests.get(f.download_url).content
        actual[f.name] = v if isinstance(v, six.string_types) else v.decode()
    test.assertEquals(sorted(actual.keys()), sorted(expected.keys()))
    for k, v in expected.items():
        a = actual[k]
        if isinstance(v, six.string_types):
            test.assertEquals(a, v, k)
        else:
            test.assertRegexpMatches(actual.get(k), v, k)


def assert_existing_clusters_are(test, client, resource_group, expected):
    """Checks if there are expected set of clusters in the given resource group reported

    :param AzureMgmtTestCase test: test instance.
    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param list[str] expected: list of cluster names.
    """
    actual = [c.name for c in list(client.clusters.list_by_resource_group(resource_group))]
    test.assertListEqual(sorted(expected), sorted(actual))


def assert_existing_file_servers_are(test, client, resource_group, expected):
    """Checks if there are expected set of file servers in the given resource group reported

    :param AzureMgmtTestCase test: test instance.
    :param BatchAIManagementClient client: client instance.
    :param str resource_group: resource group name.
    :param list[str] expected: list of file servers names.
    """
    actual = [s.name for s in list(client.file_servers.list_by_resource_group(resource_group))]
    test.assertListEqual(sorted(expected), sorted(actual))


def assert_file_in_file_share(test, storage_account, storage_account_key, directory, filename, expected_content):
    """Checks if there is a file with given name and content exists in the Azure File share.

    :param AzureMgmtTestCase test: test instance.
    :param str storage_account: storage account name.
    :param str storage_account_key: storage account key.
    :param str directory: folder.
    :param str filename: filename.
    :param unicode expected_content: expected content.
    """
    if not test.is_live:
        return
    service = FileService(storage_account, storage_account_key)
    actual = service.get_file_to_text(AZURE_FILES_NAME, directory, filename).content
    test.assertEqual(expected_content, actual)


class ClusterPreparer(AzureMgmtPreparer):
    """Batch AI cluster preparer"""
    def __init__(self,
                 location='eastus',
                 vm_size='STANDARD_D1',
                 target_nodes=1,
                 wait=True,
                 name_prefix='cluster',
                 parameter_name='cluster',
                 storage_account_parameter='storage_account',
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM):
        super(ClusterPreparer, self).__init__(name_prefix, 24)
        self.client = None  # type: BatchAIManagementClient or None
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.storage_key = ''
        self.vm_size = vm_size
        self.target_nodes = target_nodes
        self.storage_account_param = storage_account_parameter
        self.wait = wait

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(BatchAIManagementClient)
            group = self._get_resource_group(**kwargs)
            self.resource = create_cluster(self.client, self.location, group.name, name, self.vm_size,
                                           self.target_nodes, self._get_storage_account(**kwargs).name,
                                           self._get_storage_account_key(**kwargs))
            if self.wait:
                wait_for_nodes(self.is_live, self.client, group.name, name, self.target_nodes, NODE_STARTUP_TIMEOUT_SEC)
        else:
            self.resource = models.Cluster()
            self.resource.id = models.ResourceId('fake')
        return {self.parameter_name: self.resource}

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.clusters.delete(group.name, name).result()

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a cluster a resource group is required. Please add ' \
                       'decorator @{} in front of this cluster preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_storage_account(self, **kwargs):
        try:
            return kwargs.get(self.storage_account_param)
        except KeyError:
            template = 'To create a cluster a storage account is required. Please add ' \
                       'decorator @{} in front of this cluster preparer.'
            raise AzureTestError(template.format(StorageAccountPreparer.__name__))

    def _get_storage_account_key(self, **kwargs):
        try:
            return kwargs.get(self.storage_account_param + '_key')
        except KeyError:
            template = 'To create a cluster a storage account is required. Please add ' \
                       'decorator @{} in front of this cluster preparer.'
            raise AzureTestError(template.format(StorageAccountPreparer.__name__))
