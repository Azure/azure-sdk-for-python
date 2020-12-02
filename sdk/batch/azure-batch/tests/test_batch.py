# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import datetime
import io
import logging
import time
import unittest
import requests

import azure.batch
from azure.batch import models

from batch_preparers import (
    AccountPreparer,
    PoolPreparer,
    JobPreparer
)

from devtools_testutils import (
    AzureMgmtTestCase,
    ResourceGroupPreparer,
    StorageAccountPreparer,
    CachedResourceGroupPreparer,
    CachedStorageAccountPreparer
)


AZURE_LOCATION = 'westcentralus'
BATCH_RESOURCE = 'https://batch.core.windows.net/'


class BatchTest(AzureMgmtTestCase):

    def _batch_url(self, batch):
        if batch.account_endpoint.startswith('https://'):
            return batch.account_endpoint
        else:
            return 'https://' + batch.account_endpoint

    def create_aad_client(self, batch_account, **kwargs):
        credentials = self.settings.get_credentials(resource=BATCH_RESOURCE)
        client = self.create_basic_client(
            azure.batch.BatchServiceClient,
            credentials=credentials,
            batch_url=self._batch_url(batch_account)
        )
        return client

    def create_sharedkey_client(self, batch_account, credentials, **kwargs):
        client = azure.batch.BatchServiceClient(
            credentials=credentials,
            batch_url=self._batch_url(batch_account)
        )
        return client

    def assertBatchError(self, code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.fail("BatchErrorException expected but not raised")
        except models.BatchErrorException as err:
            self.assertEqual(err.error.code, code)
        except Exception as err:
            self.fail("Expected BatchErrorExcption, instead got: {!r}".format(err))

    def assertCreateTasksError(self, code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.fail("CreateTasksError expected but not raised")
        except models.CreateTasksErrorException as err:
            try:
                batch_error = err.errors.pop()
                if code:
                    self.assertEqual(batch_error.error.code, code)
            except IndexError:
                self.fail("Inner BatchErrorException expected but not exist")
        except Exception as err:
            self.fail("Expected CreateTasksError, instead got: {!r}".format(err))

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @StorageAccountPreparer(name_prefix='batch1', location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    @JobPreparer()
    def test_batch_applications(self, batch_job, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test List Applications
        apps = list(client.application.list())
        self.assertEqual(len(apps), 1)

        # Test Get Application
        app = client.application.get('application_id')
        self.assertIsInstance(app, models.ApplicationSummary)
        self.assertEqual(app.id, 'application_id')
        self.assertEqual(app.versions, ['v1.0'])

        # Test Create Task with Application Package
        task_id = 'python_task_with_app_package'
        task = models.TaskAddParameter(
            id=task_id,
            command_line='cmd /c "echo hello world"',
            application_package_references=[models.ApplicationPackageReference(application_id='application_id', version='v1.0')]
        )
        response = client.task.add(batch_job.id, task)
        self.assertIsNone(response)

        # Test Get Task with Application Package
        task = client.task.get(batch_job.id, task_id)
        self.assertIsInstance(task, models.CloudTask)
        self.assertEqual(task.application_package_references[0].application_id, 'application_id')

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    def test_batch_certificates(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Add Certificate
        certificate = models.CertificateAddParameter(
            thumbprint='cff2ab63c8c955aaf71989efa641b906558d9fb7',
            thumbprint_algorithm='sha1',
            data='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',
            certificate_format=models.CertificateFormat.pfx,
            password='nodesdk')

        response = client.certificate.add(certificate)
        self.assertIsNone(response)

        # Test List Certificates
        certs = client.certificate.list()
        test_cert = [c for c in certs if c.thumbprint == 'cff2ab63c8c955aaf71989efa641b906558d9fb7']
        self.assertEqual(len(test_cert), 1)

        # Test Get Certificate
        cert = client.certificate.get('sha1', 'cff2ab63c8c955aaf71989efa641b906558d9fb7')
        self.assertIsInstance(cert, models.Certificate)
        self.assertEqual(cert.thumbprint, 'cff2ab63c8c955aaf71989efa641b906558d9fb7')
        self.assertEqual(cert.thumbprint_algorithm, 'sha1')
        self.assertIsNone(cert.delete_certificate_error)

        # Test Cancel Certificate Delete
        self.assertBatchError('CertificateStateActive',
                              client.certificate.cancel_deletion,
                              'sha1',
                              'cff2ab63c8c955aaf71989efa641b906558d9fb7')

        # Test Delete Certificate
        response = client.certificate.delete(
            'sha1',
            'cff2ab63c8c955aaf71989efa641b906558d9fb7')
        self.assertIsNone(response)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    def test_batch_create_pools(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test List Node Agent SKUs
        response = client.account.list_supported_images()
        response = list(response)
        self.assertTrue(len(response) > 1)
        self.assertIsNotNone(response[-1].image_reference)

        # Test Create Iaas Pool
        users = [
            models.UserAccount(name='test-user-1', password='kt#_gahr!@aGERDXA'),
            models.UserAccount(name='test-user-2', password='kt#_gahr!@aGERDXA', elevation_level=models.ElevationLevel.admin)
        ]
        test_iaas_pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_iaas_'),
            vm_size='Standard_A1',
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='MicrosoftWindowsServer',
                    offer='WindowsServer',
                    sku='2016-Datacenter-smalldisk'
                ),
                node_agent_sku_id='batch.node.windows amd64',
                windows_configuration=models.WindowsConfiguration(enable_automatic_updates=True)),
            task_scheduling_policy=models.TaskSchedulingPolicy(node_fill_type=models.ComputeNodeFillType.pack),
            user_accounts=users
        )
        response = client.pool.add(test_iaas_pool)
        self.assertIsNone(response)

        # Test list pool node counnt
        counts = list(client.account.list_pool_node_counts())
        self.assertIsNotNone(counts)
        self.assertEqual(len(counts), 1)
        self.assertEqual(counts[0].pool_id, test_iaas_pool.id)
        self.assertIsNotNone(counts[0].dedicated)
        self.assertEqual(counts[0].dedicated.total, 0)
        self.assertEqual(counts[0].dedicated.leaving_pool, 0)
        self.assertEqual(counts[0].low_priority.total, 0)

        # Test Create Pool with Network Configuration
        #TODO Public IP tests
        network_config = models.NetworkConfiguration(subnet_id='/subscriptions/00000000-0000-0000-0000-000000000000'
                                                     '/resourceGroups/test'
                                                     '/providers/Microsoft.Network'
                                                     '/virtualNetworks/vnet1'
                                                     '/subnets/subnet1')
        test_network_pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_network_'),
            vm_size='Standard_A1',
            network_configuration=network_config,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='Canonical',
                    offer='UbuntuServer',
                    sku='16.04-LTS'
                ),
                node_agent_sku_id='batch.node.ubuntu 16.04')
        )
        self.assertBatchError('InvalidPropertyValue', client.pool.add, test_network_pool, models.PoolAddOptions(timeout=45))

        test_image_pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_image_'),
            vm_size='Standard_A1',
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    virtual_machine_image_id="/subscriptions/00000000-0000-0000-0000-000000000000"
                                             "/resourceGroups/test"
                                             "/providers/Microsoft.Compute"
                                             "/gallery/FakeGallery"
                                             "/images/FakeImage"
                                             "/versions/version"
                ),
                node_agent_sku_id='batch.node.ubuntu 16.04'
            )
        )
        self.assertBatchError('InvalidPropertyValue', client.pool.add, test_image_pool, models.PoolAddOptions(timeout=45))

        # Test Create Pool with Data Disk
        data_disk = models.DataDisk(lun=1, disk_size_gb=50)
        test_disk_pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_disk_'),
            vm_size='Standard_A1',
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='Canonical',
                    offer='UbuntuServer',
                    sku='16.04-LTS'
                ),
                node_agent_sku_id='batch.node.ubuntu 16.04',
                data_disks=[data_disk])
        )
        response = client.pool.add(test_disk_pool)
        self.assertIsNone(response)
        disk_pool = client.pool.get(test_disk_pool.id)
        self.assertEqual(disk_pool.virtual_machine_configuration.data_disks[0].lun, 1)
        self.assertEqual(disk_pool.virtual_machine_configuration.data_disks[0].disk_size_gb, 50)

        # Test Create Pool with Application Licenses
        test_app_pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_app_'),
            vm_size='Standard_A1',
            application_licenses=["maya"],
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='Canonical',
                    offer='UbuntuServer',
                    sku='16.04-LTS'
                ),
                node_agent_sku_id='batch.node.ubuntu 16.04',
                data_disks=[data_disk])
        )
        response = client.pool.add(test_app_pool)
        self.assertIsNone(response)
        app_pool = client.pool.get(test_app_pool.id)
        self.assertEqual(app_pool.application_licenses[0], "maya")

        # Test Create Pool with Azure Disk Encryption
        test_ade_pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_ade_'),
            vm_size='Standard_A1',
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='Canonical',
                    offer='UbuntuServer',
                    sku='16.04-LTS'
                ),
                disk_encryption_configuration=models.DiskEncryptionConfiguration(
                    targets=[models.DiskEncryptionTarget.temporary_disk]
                ),
                node_agent_sku_id='batch.node.ubuntu 16.04')
        )
        response = client.pool.add(test_ade_pool)
        self.assertIsNone(response)
        ade_pool = client.pool.get(test_ade_pool.id)
        self.assertEqual(ade_pool.virtual_machine_configuration.disk_encryption_configuration.targets,
                         [models.DiskEncryptionTarget.temporary_disk])

        # Test List Pools without Filters
        pools = list(client.pool.list())
        self.assertTrue(len(pools) > 1)

        # Test List Pools with Maximum
        options = models.PoolListOptions(max_results=1)
        pools = client.pool.list(options)
        pools.next()
        self.assertEqual(len(pools.current_page), 1)

        # Test List Pools with Filter
        options = models.PoolListOptions(
            filter='startswith(id,\'batch_app_\')',
            select='id,state',
            expand='stats')
        pools = list(client.pool.list(options))
        self.assertEqual(len(pools), 1)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    def test_batch_create_pool_with_blobfuse_mount(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Create Iaas Pool
        test_iaas_pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_iaas_'),
            vm_size='Standard_A1',
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='MicrosoftWindowsServer',
                    offer='WindowsServer',
                    sku='2016-Datacenter-smalldisk'
                ),
                node_agent_sku_id='batch.node.windows amd64',
                windows_configuration=models.WindowsConfiguration(enable_automatic_updates=True)),
            task_scheduling_policy=models.TaskSchedulingPolicy(node_fill_type=models.ComputeNodeFillType.pack),
            mount_configuration=[models.MountConfiguration(
                azure_blob_file_system_configuration=models.AzureBlobFileSystemConfiguration(
                    account_name='test',
                    container_name='https://test.blob.core.windows.net:443/test-container',
                    relative_mount_path='foo',
                    account_key='fake_account_key'
                )
            )]
        )
        response = client.pool.add(test_iaas_pool)
        self.assertIsNone(response)

        mount_pool = client.pool.get(test_iaas_pool.id)
        self.assertIsNotNone(mount_pool.mount_configuration)
        self.assertEqual(len(mount_pool.mount_configuration), 1)
        self.assertIsNotNone(mount_pool.mount_configuration[0].azure_blob_file_system_configuration)
        self.assertIsNone(mount_pool.mount_configuration[0].nfs_mount_configuration)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    def test_batch_update_pools(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Create Paas Pool
        test_paas_pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_paas_'),
            vm_size='small',
            cloud_service_configuration=models.CloudServiceConfiguration(
                os_family='5'
            ),
            start_task=models.StartTask(
                command_line="cmd.exe /c \"echo hello world\"",
                resource_files=[models.ResourceFile(http_url='https://blobsource.com', file_path='filename.txt')],
                environment_settings=[models.EnvironmentSetting(name='ENV_VAR', value='env_value')],
                user_identity=models.UserIdentity(
                    auto_user=models.AutoUserSpecification(
                        elevation_level=models.ElevationLevel.admin
                    )
                )
            )
        )
        response = client.pool.add(test_paas_pool)
        self.assertIsNone(response)

        # Test Update Pool Parameters
        params = models.PoolUpdatePropertiesParameter(
            certificate_references=[], 
            application_package_references=[], 
            metadata=[models.MetadataItem(name='foo', value='bar')])
        response = client.pool.update_properties(test_paas_pool.id, params)
        self.assertIsNone(response)

        # Test Patch Pool Parameters
        params = models.PoolPatchParameter(metadata=[models.MetadataItem(name='foo2', value='bar2')])
        response = client.pool.patch(test_paas_pool.id, params)
        self.assertIsNone(response)

        # Test Pool Exists
        response = client.pool.exists(test_paas_pool.id)
        self.assertTrue(response)

        # Test Get Pool
        pool = client.pool.get(test_paas_pool.id)
        self.assertIsInstance(pool, models.CloudPool)
        self.assertEqual(pool.id, test_paas_pool.id)
        self.assertEqual(pool.state, models.PoolState.active)
        self.assertEqual(pool.allocation_state, models.AllocationState.steady)
        self.assertEqual(pool.cloud_service_configuration.os_family, '5')
        self.assertEqual(pool.vm_size, 'small')
        self.assertIsNone(pool.start_task)
        self.assertEqual(pool.metadata[0].name, 'foo2')
        self.assertEqual(pool.metadata[0].value, 'bar2')

        # Test Get Pool with OData Clauses
        options = models.PoolGetOptions(select='id,state', expand='stats')
        pool = client.pool.get(test_paas_pool.id, options)
        self.assertIsInstance(pool, models.CloudPool)
        self.assertEqual(pool.id, test_paas_pool.id)
        self.assertEqual(pool.state, models.PoolState.active)
        self.assertIsNone(pool.allocation_state)
        self.assertIsNone(pool.vm_size)

        # Test Delete Pool
        response = client.pool.delete(test_paas_pool.id)
        self.assertIsNone(response)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    @PoolPreparer(location=AZURE_LOCATION)
    def test_batch_scale_pools(self, batch_pool, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Enable Autoscale
        interval = datetime.timedelta(minutes=6)
        response = client.pool.enable_auto_scale(
            batch_pool.name,
            auto_scale_formula='$TargetDedicatedNodes=2',
            auto_scale_evaluation_interval=interval)

        self.assertIsNone(response)

        # Test Evaluate Autoscale
        result = client.pool.evaluate_auto_scale(batch_pool.name, '$TargetDedicatedNodes=3')
        self.assertIsInstance(result, models.AutoScaleRun)
        self.assertEqual(
            result.results,
            '$TargetDedicatedNodes=3;$TargetLowPriorityNodes=0;$NodeDeallocationOption=requeue')
        
        # Test Disable Autoscale
        response = client.pool.disable_auto_scale(batch_pool.name)
        self.assertIsNone(response)

        # Test Pool Resize
        pool = client.pool.get(batch_pool.name)
        while self.is_live and pool.allocation_state != models.AllocationState.steady:
            time.sleep(5)
            pool = client.pool.get(batch_pool.name)
        params = models.PoolResizeParameter(target_dedicated_nodes=0, target_low_priority_nodes=2)
        response = client.pool.resize(batch_pool.name, params)
        self.assertIsNone(response)

        # Test Stop Pool Resize
        response = client.pool.stop_resize(batch_pool.name)
        self.assertIsNone(response)
        pool = client.pool.get(batch_pool.name)
        while self.is_live and pool.allocation_state != models.AllocationState.steady:
            time.sleep(5)
            pool = client.pool.get(batch_pool.name)

        # Test Get All Pools Lifetime Statistics
        stats = client.pool.get_all_lifetime_statistics()
        self.assertIsInstance(stats, models.PoolStatistics)
        self.assertIsNotNone(stats.resource_stats.avg_cpu_percentage)
        self.assertIsNotNone(stats.resource_stats.network_read_gi_b)
        self.assertIsNotNone(stats.resource_stats.disk_write_gi_b)
        self.assertIsNotNone(stats.resource_stats.peak_disk_gi_b)

        # Test Get Pool Usage Info
        info = list(client.pool.list_usage_metrics())
        self.assertEqual(info, [])

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    def test_batch_job_schedules(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Create Job Schedule
        schedule_id = self.get_resource_name('batch_schedule_')
        job_spec = models.JobSpecification(
            pool_info=models.PoolInformation(pool_id="pool_id"),
            constraints=models.JobConstraints(max_task_retry_count=2),
            on_all_tasks_complete=models.OnAllTasksComplete.terminate_job
        )
        schedule = models.Schedule(
            start_window=datetime.timedelta(hours=1),
            recurrence_interval=datetime.timedelta(days=1)
        )
        params = models.JobScheduleAddParameter(
            id=schedule_id,
            schedule=schedule,
            job_specification=job_spec
        )
        response = client.job_schedule.add(params)
        self.assertIsNone(response)

        # Test List Job Schedules
        schedules = list(client.job_schedule.list())
        self.assertTrue(len(schedules) > 0)

        # Test Get Job Schedule
        schedule = client.job_schedule.get(schedule_id)
        self.assertIsInstance(schedule, models.CloudJobSchedule)
        self.assertEqual(schedule.id, schedule_id)
        self.assertEqual(schedule.state, models.JobScheduleState.active)

        # Test Job Schedule Exists
        exists = client.job_schedule.exists(schedule_id)
        self.assertTrue(exists)

        # Test List Jobs from Schedule
        jobs = list(client.job.list_from_job_schedule(schedule_id))
        self.assertTrue(len(jobs) > 0)

        # Test Disable Job Schedule
        response = client.job_schedule.disable(schedule_id)
        self.assertIsNone(response)

        # Test Enable Job Schedule
        response = client.job_schedule.enable(schedule_id)
        self.assertIsNone(response)

        # Test Update Job Schedule
        job_spec = models.JobSpecification(
            pool_info=models.PoolInformation(pool_id='pool_id')
        )
        schedule = models.Schedule(
            recurrence_interval=datetime.timedelta(hours=10)
        )
        params = models.JobScheduleUpdateParameter(schedule=schedule, job_specification=job_spec)
        response = client.job_schedule.update(schedule_id, params)
        self.assertIsNone(response)

        # Test Patch Job Schedule
        schedule = models.Schedule(
            recurrence_interval=datetime.timedelta(hours=5)
        )
        params = models.JobSchedulePatchParameter(schedule=schedule)
        response = client.job_schedule.patch(schedule_id, params)
        self.assertIsNone(response)

        # Test Terminate Job Schedule
        response = client.job_schedule.terminate(schedule_id)
        self.assertIsNone(response)

        # Test Delete Job Schedule
        response = client.job_schedule.delete(schedule_id)
        self.assertIsNone(response)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    def test_batch_network_configuration(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Create Pool with Network Config
        network_config = models.NetworkConfiguration(
            endpoint_configuration=models.PoolEndpointConfiguration(
                inbound_nat_pools=[
                    models.InboundNATPool(
                        name="TestEndpointConfig",
                        protocol=models.InboundEndpointProtocol.udp,
                        backend_port=64444,
                        frontend_port_range_start=60000,
                        frontend_port_range_end=61000,
                        network_security_group_rules=[
                            models.NetworkSecurityGroupRule(
                                priority=150,
                                access=models.NetworkSecurityGroupRuleAccess.allow,
                                source_address_prefix='*'
                            )
                        ]
                    )
                ]
            )
        )
        virtual_machine_config = models.VirtualMachineConfiguration(
            node_agent_sku_id="batch.node.ubuntu 16.04",
            image_reference=models.ImageReference(
                publisher="Canonical",
                offer="UbuntuServer",
                sku="16.04-LTS")
        )
        pool = models.PoolAddParameter(
            id=self.get_resource_name('batch_network_'),
            target_dedicated_nodes=1,
            vm_size='Standard_A1',
            virtual_machine_configuration=virtual_machine_config,
            network_configuration=network_config
        )

        client.pool.add(pool)
        network_pool = client.pool.get(pool.id)
        while self.is_live and network_pool.allocation_state != models.AllocationState.steady:
            time.sleep(10)
            network_pool = client.pool.get(pool.id)

        # Test Compute Node Config
        nodes = list(client.compute_node.list(pool.id))
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], models.ComputeNode)
        self.assertEqual(len(nodes[0].endpoint_configuration.inbound_endpoints), 2)
        self.assertEqual(nodes[0].endpoint_configuration.inbound_endpoints[0].name, 'TestEndpointConfig.0')
        self.assertEqual(nodes[0].endpoint_configuration.inbound_endpoints[0].protocol.value, 'udp')

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    @PoolPreparer(location=AZURE_LOCATION, size=2, config='iaas')
    def test_batch_compute_nodes(self, batch_pool, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test List Compute Nodes
        nodes = list(client.compute_node.list(batch_pool.name))
        self.assertEqual(len(nodes), 2)
        while self.is_live and any([n for n in nodes if n.state != models.ComputeNodeState.idle]):
            time.sleep(10)
            nodes = list(client.compute_node.list(batch_pool.name))

        # Test Get Compute Node
        node = client.compute_node.get(batch_pool.name, nodes[0].id)
        self.assertIsInstance(node, models.ComputeNode)
        self.assertEqual(node.scheduling_state, models.SchedulingState.enabled)
        self.assertTrue(node.is_dedicated)
        self.assertIsNotNone(node.node_agent_info)
        self.assertIsNotNone(node.node_agent_info.version)

        # Test Upload Log
        config = models.UploadBatchServiceLogsConfiguration(
            container_url = "https://test.blob.core.windows.net:443/test-container", 
            start_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=6))
        result = client.compute_node.upload_batch_service_logs(batch_pool.name, nodes[0].id, config)
        self.assertIsNotNone(result)
        self.assertTrue(result.number_of_files_uploaded > 0)
        self.assertIsNotNone(result.virtual_directory_name)

        # Test Disable Scheduling
        response = client.compute_node.disable_scheduling(batch_pool.name, nodes[0].id)
        self.assertIsNone(response)

        # Test Enable Scheduling
        response = client.compute_node.enable_scheduling(batch_pool.name, nodes[0].id)
        self.assertIsNone(response)

        # Test Reboot Node
        response = client.compute_node.reboot(
            batch_pool.name, nodes[0].id, node_reboot_option=models.ComputeNodeRebootOption.terminate)
        self.assertIsNone(response)

        # Test Reimage Node
        self.assertBatchError('OperationNotValidOnNode',
                              client.compute_node.reimage,
                              batch_pool.name,
                              nodes[1].id,
                              node_reimage_option=models.ComputeNodeReimageOption.terminate)

        # Test Remove Nodes
        options = models.NodeRemoveParameter(node_list=[n.id for n in nodes])
        response = client.pool.remove_nodes(batch_pool.name, options)
        self.assertIsNone(response)

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    @PoolPreparer(location=AZURE_LOCATION, size=1, config='paas')
    def test_batch_compute_node_user(self, batch_pool, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        nodes = list(client.compute_node.list(batch_pool.name))
        while self.is_live and any([n for n in nodes if n.state != models.ComputeNodeState.idle]):
            time.sleep(10)
            nodes = list(client.compute_node.list(batch_pool.name))

        # Test Add User
        user_name = 'BatchPythonSDKUser'
        nodes = list(client.compute_node.list(batch_pool.name))
        user = models.ComputeNodeUser(name=user_name, password='kt#_gahr!@aGERDXA', is_admin=False)
        response = client.compute_node.add_user(batch_pool.name, nodes[0].id, user)
        self.assertIsNone(response)

        # Test Update User
        user = models.NodeUpdateUserParameter(password='liilef#$DdRGSa_ewkjh')
        response = client.compute_node.update_user(batch_pool.name, nodes[0].id, user_name, user)
        self.assertIsNone(response)

        # Test Get RDP File
        file_length = 0
        with io.BytesIO() as file_handle:
            response = client.compute_node.get_remote_desktop(batch_pool.name, nodes[0].id)
            if response:
                for data in response:
                    file_length += len(data)
        self.assertTrue(file_length > 0)

        # Test Delete User
        response = client.compute_node.delete_user(batch_pool.name, nodes[0].id, user_name)
        self.assertIsNone(response)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @StorageAccountPreparer(name_prefix='batch4', location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, name_prefix='batch4')
    @PoolPreparer(size=1)
    @JobPreparer()
    def test_batch_files(self, batch_pool, batch_job, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        nodes = list(client.compute_node.list(batch_pool.name))
        while self.is_live and any([n for n in nodes if n.state != models.ComputeNodeState.idle]):
            time.sleep(10)
            nodes = list(client.compute_node.list(batch_pool.name))
        node = nodes[0].id
        task_id = 'test_task'
        task_param = models.TaskAddParameter(id=task_id, command_line='cmd /c "echo hello world"')
        response = client.task.add(batch_job.id, task_param)
        self.assertIsNone(response)
        task = client.task.get(batch_job.id, task_id)
        while self.is_live and task.state != models.TaskState.completed:
            time.sleep(5)
            task = client.task.get(batch_job.id, task_id)

        # Test List Files from Compute Node
        all_files = client.file.list_from_compute_node(batch_pool.name, node, recursive=True)
        only_files = [f for f in all_files if not f.is_directory]
        self.assertTrue(len(only_files) >= 2)

        # Test File Properties from Compute Node
        props = client.file.get_properties_from_compute_node(
            batch_pool.name, node, only_files[0].name, raw=True)
        self.assertTrue('Content-Length' in props.headers)
        self.assertTrue('Content-Type' in props.headers)

        # Test Get File from Compute Node
        file_length = 0
        with io.BytesIO() as file_handle:
            response = client.file.get_from_compute_node(batch_pool.name, node, only_files[0].name)
            for data in response:
                file_length += len(data)
        self.assertEqual(file_length, props.headers['Content-Length'])

        # Test Delete File from Compute Node
        response = client.file.delete_from_compute_node(batch_pool.name, node, only_files[0].name)
        self.assertIsNone(response)

        # Test List Files from Task
        all_files = client.file.list_from_task(batch_job.id, task_id)
        only_files = [f for f in all_files if not f.is_directory]
        self.assertTrue(len(only_files) >= 1)

        # Test File Properties from Task
        props = client.file.get_properties_from_task(
            batch_job.id, task_id, only_files[0].name, raw=True)
        self.assertTrue('Content-Length' in props.headers)
        self.assertTrue('Content-Type' in props.headers)

        # Test Get File from Task
        file_length = 0
        with io.BytesIO() as file_handle:
            response = client.file.get_from_task(batch_job.id, task_id, only_files[0].name)
            for data in response:
                file_length += len(data)
        self.assertEqual(file_length, props.headers['Content-Length'])

        # Test Delete File from Task
        response = client.file.delete_from_task(batch_job.id, task_id, only_files[0].name)
        self.assertIsNone(response)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    @JobPreparer(on_task_failure=models.OnTaskFailure.perform_exit_options_job_action)
    def test_batch_tasks(self, batch_job, **kwargs):
        client = self.create_sharedkey_client(**kwargs)

        # Test Create Task with Auto Complete
        exit_conditions = models.ExitConditions(
            exit_codes=[models.ExitCodeMapping(code=1, exit_options=models.ExitOptions(job_action=models.JobAction.terminate))],
            exit_code_ranges=[models.ExitCodeRangeMapping(start=2, end=4, exit_options=models.ExitOptions(job_action=models.JobAction.disable))],
            default=models.ExitOptions(job_action=models.JobAction.none))
        task_param = models.TaskAddParameter(
            id=self.get_resource_name('batch_task1_'),
            command_line='cmd /c "echo hello world"',
            exit_conditions=exit_conditions
        )
        try:
            client.task.add(batch_job.id, task_param)
        except models.BatchErrorException as e:
            message = "{}: ".format(e.error.code, e.error.message)
            for v in e.error.values:
                message += "\n{}: {}".format(v.key, v.value)
            raise Exception(message)
        task = client.task.get(batch_job.id, task_param.id)
        self.assertIsInstance(task, models.CloudTask)
        self.assertEqual(task.exit_conditions.default.job_action, models.JobAction.none)
        self.assertEqual(task.exit_conditions.exit_codes[0].code, 1)
        self.assertEqual(task.exit_conditions.exit_codes[0].exit_options.job_action, models.JobAction.terminate)

        # Test Create Task with Output Files
        container_url = "https://test.blob.core.windows.net:443/test-container"
        outputs = [
            models.OutputFile(
                file_pattern="../stdout.txt",
                destination=models.OutputFileDestination(
                    container=models.OutputFileBlobContainerDestination(
                        container_url=container_url, path="taskLogs/output.txt")),
                upload_options=models.OutputFileUploadOptions(
                    upload_condition=models.OutputFileUploadCondition.task_completion)),
            models.OutputFile(
                file_pattern="../stderr.txt",
                destination=models.OutputFileDestination(
                    container=models.OutputFileBlobContainerDestination(
                        container_url=container_url, path="taskLogs/error.txt")),
                upload_options=models.OutputFileUploadOptions(
                    upload_condition=models.OutputFileUploadCondition.task_failure)),
        ]
        task_param = models.TaskAddParameter(
            id=self.get_resource_name('batch_task2_'),
            command_line='cmd /c "echo hello world"',
            output_files=outputs
        )
        client.task.add(batch_job.id, task_param)
        task = client.task.get(batch_job.id, task_param.id)
        self.assertIsInstance(task, models.CloudTask)
        self.assertEqual(len(task.output_files), 2)

        # Test Create Task with Auto User
        auto_user = models.AutoUserSpecification(
            scope=models.AutoUserScope.task,
            elevation_level=models.ElevationLevel.admin)
        task_param = models.TaskAddParameter(
            id=self.get_resource_name('batch_task3_'),
            command_line='cmd /c "echo hello world"',
            user_identity=models.UserIdentity(auto_user=auto_user)
        )
        client.task.add(batch_job.id, task_param)
        task = client.task.get(batch_job.id, task_param.id)
        self.assertIsInstance(task, models.CloudTask)
        self.assertEqual(task.user_identity.auto_user.scope, models.AutoUserScope.task)
        self.assertEqual(task.user_identity.auto_user.elevation_level, models.ElevationLevel.admin)

        # Test Create Task with Token Settings
        task_param = models.TaskAddParameter(
            id=self.get_resource_name('batch_task4_'),
            command_line='cmd /c "echo hello world"',
            authentication_token_settings=models.AuthenticationTokenSettings(
                access=[models.AccessScope.job])
        )
        client.task.add(batch_job.id, task_param)
        task = client.task.get(batch_job.id, task_param.id)
        self.assertIsInstance(task, models.CloudTask)
        self.assertEqual(task.authentication_token_settings.access[0], models.AccessScope.job)

        # Test Create Task with Container Settings
        task_param = models.TaskAddParameter(
            id=self.get_resource_name('batch_task5_'),
            command_line='cmd /c "echo hello world"',
            container_settings=models.TaskContainerSettings(
                image_name='windows_container:latest',
                registry=models.ContainerRegistry(user_name='username', password='password'))
        )
        client.task.add(batch_job.id, task_param)
        task = client.task.get(batch_job.id, task_param.id)
        self.assertIsInstance(task, models.CloudTask)
        self.assertEqual(task.container_settings.image_name, 'windows_container:latest')
        self.assertEqual(task.container_settings.registry.user_name, 'username')

        # Test Create Task with Run-As-User
        task_param = models.TaskAddParameter(
            id=self.get_resource_name('batch_task6_'),
            command_line='cmd /c "echo hello world"',
            user_identity=models.UserIdentity(user_name='task-user')
        )
        client.task.add(batch_job.id, task_param)
        task = client.task.get(batch_job.id, task_param.id)
        self.assertIsInstance(task, models.CloudTask)
        self.assertEqual(task.user_identity.user_name, 'task-user')

        # Test Add Task Collection
        tasks = []
        for i in range(7, 10):
            tasks.append(models.TaskAddParameter(
                id=self.get_resource_name('batch_task{}_'.format(i)),
                command_line='cmd /c "echo hello world"'))
        result = client.task.add_collection(batch_job.id, tasks)
        self.assertIsInstance(result, models.TaskAddCollectionResult)
        self.assertEqual(len(result.value), 3)
        self.assertEqual(result.value[0].status, models.TaskAddStatus.success)

        # Test List Tasks
        tasks = list(client.task.list(batch_job.id))
        self.assertEqual(len(tasks), 9)

        # Test Count Tasks
        task_results = client.job.get_task_counts(batch_job.id)
        self.assertIsInstance(task_results, models.TaskCountsResult)
        self.assertEqual(task_results.task_counts.completed, 0)
        self.assertEqual(task_results.task_counts.succeeded, 0)

        # Test Terminate Task
        response = client.task.terminate(batch_job.id, task_param.id)
        self.assertIsNone(response)
        task = client.task.get(batch_job.id, task_param.id)
        self.assertEqual(task.state, models.TaskState.completed)

        # Test Reactivate Task
        response = client.task.reactivate(batch_job.id, task_param.id)
        self.assertIsNone(response)
        task = client.task.get(batch_job.id, task_param.id)
        self.assertEqual(task.state, models.TaskState.active)

        # Test Update Task
        response = client.task.update(
            batch_job.id, task_param.id,
            constraints=models.TaskConstraints(max_task_retry_count=1))
        self.assertIsNone(response)

        # Test Get Subtasks
        # TODO: Test with actual subtasks
        subtasks = client.task.list_subtasks(batch_job.id, task_param.id)
        self.assertIsInstance(subtasks, models.CloudTaskListSubtasksResult)
        self.assertEqual(subtasks.value, [])

        # Test Delete Task
        response = client.task.delete(batch_job.id, task_param.id)
        self.assertIsNone(response)

        # Test Bulk Add Task Failure
        task_id = "mytask"
        tasks_to_add = []
        resource_files = []
        for i in range(10000):
            resource_file = models.ResourceFile(
                http_url="https://mystorageaccount.blob.core.windows.net/files/resourceFile{}".format(str(i)),
                file_path="resourceFile{}".format(str(i)))
            resource_files.append(resource_file)
        task = models.TaskAddParameter(
            id=task_id,
            command_line="sleep 1",
            resource_files=resource_files)
        tasks_to_add.append(task)
        self.assertCreateTasksError(
            "RequestBodyTooLarge",
            client.task.add_collection,
            batch_job.id,
            tasks_to_add)
        self.assertCreateTasksError(
            "RequestBodyTooLarge",
            client.task.add_collection,
            batch_job.id,
            tasks_to_add,
            threads=3)

        # Test Bulk Add Task Success
        task_id = "mytask"
        tasks_to_add = []
        resource_files = []
        for i in range(100):
            resource_file = models.ResourceFile(
                http_url="https://mystorageaccount.blob.core.windows.net/files/resourceFile" + str(i),
                file_path="resourceFile"+str(i))
            resource_files.append(resource_file)
        for i in range(733):
            task = models.TaskAddParameter(
                id=task_id + str(i),
                command_line="sleep 1",
                resource_files=resource_files)
            tasks_to_add.append(task)
        result = client.task.add_collection(batch_job.id, tasks_to_add)
        self.assertIsInstance(result, models.TaskAddCollectionResult)
        self.assertEqual(len(result.value), 733)
        self.assertEqual(result.value[0].status, models.TaskAddStatus.success)
        self.assertTrue(
            all(t.status == models.TaskAddStatus.success for t in result.value))

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION)
    def test_batch_jobs(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Create Job
        auto_pool = models.AutoPoolSpecification(
            pool_lifetime_option=models.PoolLifetimeOption.job,
            pool=models.PoolSpecification(
                vm_size='small',
                cloud_service_configuration=models.CloudServiceConfiguration(
                    os_family='5'
                )
            )
        )
        job_prep = models.JobPreparationTask(command_line="cmd /c \"echo hello world\"")
        job_release = models.JobReleaseTask(command_line="cmd /c \"echo goodbye world\"")
        job_param = models.JobAddParameter(
            id=self.get_resource_name('batch_job1_'),
            pool_info=models.PoolInformation(
                auto_pool_specification=auto_pool
            ),
            job_preparation_task=job_prep,
            job_release_task=job_release
        )
        response = client.job.add(job_param)
        self.assertIsNone(response)

        # Test Update Job
        constraints = models.JobConstraints(max_task_retry_count=3)
        options = models.JobUpdateParameter(
            priority=500,
            constraints=constraints,
            pool_info=models.PoolInformation(
                auto_pool_specification=auto_pool
            )
        )
        response = client.job.update(job_param.id, options)
        self.assertIsNone(response)

        # Test Patch Job
        options = models.JobPatchParameter(priority=900)
        response = client.job.patch(job_param.id, options)
        self.assertIsNone(response)

        job = client.job.get(job_param.id)
        self.assertIsInstance(job, models.CloudJob)
        self.assertEqual(job.id, job_param.id)
        self.assertEqual(job.constraints.max_task_retry_count, 3)
        self.assertEqual(job.priority, 900)

        # Test Create Job with Auto Complete
        job_auto_param = models.JobAddParameter(
            id=self.get_resource_name('batch_job2_'),
            on_all_tasks_complete=models.OnAllTasksComplete.terminate_job,
            on_task_failure=models.OnTaskFailure.perform_exit_options_job_action,
            pool_info=models.PoolInformation(
                auto_pool_specification=auto_pool
            )
        )
        response = client.job.add(job_auto_param)
        self.assertIsNone(response)
        job = client.job.get(job_auto_param.id)
        self.assertIsInstance(job, models.CloudJob)
        self.assertEqual(job.on_all_tasks_complete, models.OnAllTasksComplete.terminate_job)
        self.assertEqual(job.on_task_failure, models.OnTaskFailure.perform_exit_options_job_action)

        # Test List Jobs
        jobs = client.job.list()
        self.assertIsInstance(jobs, models.CloudJobPaged)
        self.assertEqual(len(list(jobs)), 2)

        # Test Disable Job
        response = client.job.disable(job_param.id, models.DisableJobOption.requeue)
        self.assertIsNone(response)

        # Test Enable Job
        response = client.job.enable(job_param.id)
        self.assertIsNone(response)

        # Prep and release task status
        task_status = client.job.list_preparation_and_release_task_status(job_param.id)
        self.assertIsInstance(task_status, models.JobPreparationAndReleaseTaskExecutionInformationPaged)
        self.assertEqual(list(task_status), [])

        # Test Terminate Job
        response = client.job.terminate(job_param.id)
        self.assertIsNone(response)

        # Test Delete Job
        response = client.job.delete(job_auto_param.id)
        self.assertIsNone(response)

        # Test Job Lifetime Statistics
        stats = client.job.get_all_lifetime_statistics()
        self.assertIsInstance(stats, models.JobStatistics)
        self.assertEqual(stats.num_succeeded_tasks, 0)
        self.assertEqual(stats.num_failed_tasks, 0)
