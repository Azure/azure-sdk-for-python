# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import datetime
import io
import hashlib
import logging
import time
import binascii
import json
import pytest
import requests
import six
import os


from wsgiref.handlers import format_date_time
from time import mktime

import azure.core.exceptions
import azure.batch
from azure.batch import models
from typing import Any, Callable, Dict, Iterable, Optional, TypeVar

from batch_preparers import (
    AccountPreparer,
    PoolPreparer,
    JobPreparer
)

from devtools_testutils import (
    AzureMgmtRecordedTestCase, recorded_by_proxy,
    ResourceGroupPreparer,
    StorageAccountPreparer,
    CachedResourceGroupPreparer,
    set_custom_default_matcher
)
from devtools_testutils.fake_credentials import BATCH_TEST_PASSWORD
from azure_devtools.scenario_tests.recording_processors import GeneralNameReplacer, RecordingProcessor


AZURE_LOCATION = 'eastus'
BATCH_ENVIRONMENT = None  # Set this to None if testing against prod
BATCH_RESOURCE = 'https://batch.core.windows.net/'
DEFAULT_VM_SIZE = 'standard_d2_v2'
SECRET_FIELDS = ["primary", "secondary"]

def get_redacted_key(key):
    redacted_value = "redacted"
    digest = hashlib.sha256(six.ensure_binary(key)).digest()
    redacted_value += six.ensure_str(binascii.hexlify(digest))[:6]
    return redacted_value


class RecordingRedactor(RecordingProcessor):
    """Removes keys from test recordings"""

    def process_response(self, response):
        try:
            body = json.loads(response["body"]["string"])
        except (KeyError, ValueError):
            return response

        for field in body:
            if field in SECRET_FIELDS:
                body[field] = get_redacted_key(body[field])

        response["body"]["string"] = json.dumps(body)
        return response



class TestBatch(AzureMgmtRecordedTestCase):

    scrubber = GeneralNameReplacer()
    redactor = RecordingRedactor()


    def fail(self, err):
        raise RuntimeError(err)

    def _batch_url(self, batch):
        if batch.account_endpoint.startswith('https://'):
            return batch.account_endpoint
        else:
            return 'https://' + batch.account_endpoint

    def create_aad_client(self, batch_account, **kwargs):
        credential = self.settings.get_credentials(resource=BATCH_RESOURCE)
        client = self.create_basic_client(
            azure.batch.BatchClient,
            credential=credential,
            endpoint=self._batch_url(batch_account)
        )
        return client

    def create_sharedkey_client(self, batch_account, credential, **kwargs):
        client = azure.batch.BatchClient(
            credential=credential,
            endpoint=self._batch_url(batch_account)
        )
        return client

    def assertBatchError(self, code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.fail("BatchErrorException expected but not raised")
        except azure.core.exceptions.HttpResponseError as err:
            batcherror = err.model
            #self.assertEqual(err.error.code, code)
            assert err.error.code ==  code
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
                    #self.assertEqual(batch_error.error.code, code)
                    assert batch_error.error.code ==  code
            except IndexError:
                self.fail("Inner BatchErrorException expected but not exist")
        except Exception as err:
            self.fail("Expected CreateTasksError, instead got: {!r}".format(err))

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @StorageAccountPreparer(name_prefix='batch1', location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @JobPreparer()
    @recorded_by_proxy
    def test_batch_applications(self, **kwargs):
        batch_job = kwargs.pop("batch_job")
        client = self.create_sharedkey_client(**kwargs)
        # Test List Applications
        apps = list(client.list_applications())
        assert len(apps) ==  1

        # Test Get Application
        app = client.get_application('application_id')
        assert isinstance(app,  models.BatchApplication)
        assert app.id ==  'application_id'
        assert app.versions ==  ['v1.0']

        # Test Create Task with Application Package
        task_id = 'python_task_with_app_package'
        task = models.BatchTaskCreateOptions(
            id=task_id,
            command_line='cmd /c "echo hello world"',
            application_package_references=[models.ApplicationPackageReference(application_id='application_id', version='v1.0')]
        )
        response = client.create_task(batch_job.id, task)
        assert response is None

        # Test Get Task with Application Package
        task = client.get_task(batch_job.id, task_id)
        assert isinstance(task,  models.BatchTask)
        assert task.application_package_references[0].application_id ==  'application_id'

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @recorded_by_proxy
    def test_batch_certificates(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Add Certificate
        certificate = models.BatchCertificate(
            thumbprint='cff2ab63c8c955aaf71989efa641b906558d9fb7',
            thumbprint_algorithm='sha1',
            data='MIIGMQIBAzCCBe0GCSqGSIb3DQEHAaCCBd4EggXaMIIF1jCCA8AGCSqGSIb3DQEHAaCCA7EEggOtMIIDqTCCA6UGCyqGSIb3DQEMCgECoIICtjCCArIwHAYKKoZIhvcNAQwBAzAOBAhyd3xCtln3iQICB9AEggKQhe5P10V9iV1BsDlwWT561Yu2hVq3JT8ae/ebx1ZR/gMApVereDKkS9Zg4vFyssusHebbK5pDpU8vfAqle0TM4m7wGsRj453ZorSPUfMpHvQnAOn+2pEpWdMThU7xvZ6DVpwhDOQk9166z+KnKdHGuJKh4haMT7Rw/6xZ1rsBt2423cwTrQVMQyACrEkianpuujubKltN99qRoFAxhQcnYE2KlYKw7lRcExq6mDSYAyk5xJZ1ZFdLj6MAryZroQit/0g5eyhoNEKwWbi8px5j71pRTf7yjN+deMGQKwbGl+3OgaL1UZ5fCjypbVL60kpIBxLZwIJ7p3jJ+q9pbq9zSdzshPYor5lxyUfXqaso/0/91ayNoBzg4hQGh618PhFI6RMGjwkzhB9xk74iweJ9HQyIHf8yx2RCSI22JuCMitPMWSGvOszhbNx3AEDLuiiAOHg391mprEtKZguOIr9LrJwem/YmcHbwyz5YAbZmiseKPkllfC7dafFfCFEkj6R2oegIsZo0pEKYisAXBqT0g+6/jGwuhlZcBo0f7UIZm88iA3MrJCjlXEgV5OcQdoWj+hq0lKEdnhtCKr03AIfukN6+4vjjarZeW1bs0swq0l3XFf5RHa11otshMS4mpewshB9iO9MuKWpRxuxeng4PlKZ/zuBqmPeUrjJ9454oK35Pq+dghfemt7AUpBH/KycDNIZgfdEWUZrRKBGnc519C+RTqxyt5hWL18nJk4LvSd3QKlJ1iyJxClhhb/NWEzPqNdyA5cxen+2T9bd/EqJ2KzRv5/BPVwTQkHH9W/TZElFyvFfOFIW2+03RKbVGw72Mr/0xKZ+awAnEfoU+SL/2Gj2m6PHkqFX2sOCi/tN9EA4xgdswEwYJKoZIhvcNAQkVMQYEBAEAAAAwXQYJKwYBBAGCNxEBMVAeTgBNAGkAYwByAG8AcwBvAGYAdAAgAFMAdAByAG8AbgBnACAAQwByAHkAcAB0AG8AZwByAGEAcABoAGkAYwAgAFAAcgBvAHYAaQBkAGUAcjBlBgkqhkiG9w0BCRQxWB5WAFAAdgBrAFQAbQBwADoANABjAGUANgAwADQAZABhAC0AMAA2ADgAMQAtADQANAAxADUALQBhADIAYwBhAC0ANQA3ADcAMwAwADgAZQA2AGQAOQBhAGMwggIOBgkqhkiG9w0BBwGgggH/BIIB+zCCAfcwggHzBgsqhkiG9w0BDAoBA6CCAcswggHHBgoqhkiG9w0BCRYBoIIBtwSCAbMwggGvMIIBXaADAgECAhAdka3aTQsIsUphgIXGUmeRMAkGBSsOAwIdBQAwFjEUMBIGA1UEAxMLUm9vdCBBZ2VuY3kwHhcNMTYwMTAxMDcwMDAwWhcNMTgwMTAxMDcwMDAwWjASMRAwDgYDVQQDEwdub2Rlc2RrMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC5fhcxbJHxxBEIDzVOMc56s04U6k4GPY7yMR1m+rBGVRiAyV4RjY6U936dqXHCVD36ps2Q0Z+OeEgyCInkIyVeB1EwXcToOcyeS2YcUb0vRWZDouC3tuFdHwiK1Ed5iW/LksmXDotyV7kpqzaPhOFiMtBuMEwNJcPge9k17hRgRQIDAQABo0swSTBHBgNVHQEEQDA+gBAS5AktBh0dTwCNYSHcFmRjoRgwFjEUMBIGA1UEAxMLUm9vdCBBZ2VuY3mCEAY3bACqAGSKEc+41KpcNfQwCQYFKw4DAh0FAANBAHl2M97QbpzdnwO5HoRBsiEExOcLTNg+GKCr7HUsbzfvrUivw+JLL7qjHAIc5phnK+F5bQ8HKe0L9YXBSKl+fvwxFTATBgkqhkiG9w0BCRUxBgQEAQAAADA7MB8wBwYFKw4DAhoEFGVtyGMqiBd32fGpzlGZQoRM6UQwBBTI0YHFFqTS4Go8CoLgswn29EiuUQICB9A=',
            certificate_format=models.CertificateFormat.pfx,
            password='nodesdk')

        response = client.create_certificate(certificate)
        assert response is None

        # Test List Certificates
        certs = client.list_certificates()
        test_cert = [c for c in certs if c.thumbprint == 'cff2ab63c8c955aaf71989efa641b906558d9fb7']
        assert len(test_cert) ==  1

        # Test Get Certificate
        cert = client.get_certificate('sha1', 'cff2ab63c8c955aaf71989efa641b906558d9fb7')
        assert isinstance(cert,  models.BatchCertificate)
        assert cert.thumbprint ==  'cff2ab63c8c955aaf71989efa641b906558d9fb7'
        assert cert.thumbprint_algorithm ==  'sha1'
        assert cert.delete_certificate_error is None

        # Test Cancel Certificate Delete
        self.assertBatchError('CertificateStateActive',
                              client.cancel_certificate_deletion,
                              'sha1',
                              'cff2ab63c8c955aaf71989efa641b906558d9fb7')

        # Test Delete Certificate
        response = client.delete_certificate(
            'sha1',
            'cff2ab63c8c955aaf71989efa641b906558d9fb7')
        assert response is None

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @recorded_by_proxy
    def test_batch_create_pools(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test List Node Agent SKUs
        response = client.list_supported_images()
        response = list(response)
        assert (len(response) > 1)
        assert response[-1].image_reference is not None

        # Test Create Iaas Pool
        users = [
            models.UserAccount(name='test-user-1', password=BATCH_TEST_PASSWORD),
            models.UserAccount(name='test-user-2', password=BATCH_TEST_PASSWORD, elevation_level=models.ElevationLevel.admin)
        ]
        test_iaas_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_iaas_'),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='MicrosoftWindowsServer',
                    offer='WindowsServer',
                    sku='2016-Datacenter-smalldisk'
                ),
                node_agent_sku_id='batch.node.windows amd64',
                windows_configuration=models.WindowsConfiguration(enable_automatic_updates=True)),
            task_scheduling_policy=models.TaskSchedulingPolicy(node_fill_type=models.BatchNodeFillType.pack),
            user_accounts=users,
            target_node_communication_mode=models.NodeCommunicationMode.classic
        )
        response = client.create_pool(test_iaas_pool)
        assert response is None

        # Test list pool node counnt
        counts = list(client.list_pool_node_counts())
        assert counts is not None
        assert len(counts) ==  1
        assert counts[0].pool_id ==  test_iaas_pool.id
        assert counts[0].dedicated is not None
        assert counts[0].dedicated.total ==  0
        assert counts[0].dedicated.leaving_pool ==  0
        assert counts[0].low_priority.total ==  0   

        # Test Create Pool with Network Configuration
        #TODO Public IP tests
        network_config = models.NetworkConfiguration(subnet_id='/subscriptions/00000000-0000-0000-0000-000000000000'
                                                     '/resourceGroups/test'
                                                     '/providers/Microsoft.Network'
                                                     '/virtualNetworks/vnet1'
                                                     '/subnets/subnet1')
        test_network_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_network_'),
            vm_size=DEFAULT_VM_SIZE,
            network_configuration=network_config,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='Canonical',
                    offer='UbuntuServer',
                    sku='18.04-LTS'
                ),
                node_agent_sku_id='batch.node.ubuntu 18.04')
        )
        self.assertBatchError('InvalidPropertyValue', client.create_pool, body=test_network_pool, timeout=45)

        test_image_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_image_'),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    virtual_machine_image_id="/subscriptions/00000000-0000-0000-0000-000000000000"
                                             "/resourceGroups/test"
                                             "/providers/Microsoft.Compute"
                                             "/gallery/FakeGallery"
                                             "/images/FakeImage"
                                             "/versions/version"
                ),
                node_agent_sku_id='batch.node.ubuntu 18.04'
            )
        )
        self.assertBatchError('InvalidPropertyValue', client.create_pool, body=test_image_pool, timeout=45)

        # Test Create Pool with Data Disk
        data_disk = models.DataDisk(lun=1, disk_size_gb=50)
        test_disk_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_disk_'),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='Canonical',
                    offer='UbuntuServer',
                    sku='18.04-LTS'
                ),
                node_agent_sku_id='batch.node.ubuntu 18.04',
                data_disks=[data_disk]),
            target_node_communication_mode=models.NodeCommunicationMode.classic
        )
        response = client.create_pool(test_disk_pool)
        assert response is None
        disk_pool = client.get_pool(test_disk_pool.id)
        assert disk_pool.virtual_machine_configuration.data_disks[0].lun ==  1
        assert disk_pool.virtual_machine_configuration.data_disks[0].disk_size_gb ==  50
        assert disk_pool.target_node_communication_mode ==  models.NodeCommunicationMode.classic

        # Test Create Pool with Application Licenses
        test_app_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_app_'),
            vm_size=DEFAULT_VM_SIZE,
            application_licenses=["maya"],
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='Canonical',
                    offer='UbuntuServer',
                    sku='18.04-LTS'
                ),
                node_agent_sku_id='batch.node.ubuntu 18.04',
                data_disks=[data_disk]),
            target_node_communication_mode=models.NodeCommunicationMode.simplified
        )
        response = client.create_pool(test_app_pool)
        assert response is None
        app_pool = client.get_pool(test_app_pool.id)
        assert app_pool.application_licenses[0] ==  "maya"
        assert app_pool.target_node_communication_mode ==  models.NodeCommunicationMode.simplified

        # Test Create Pool with Azure Disk Encryption
        test_ade_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_ade_'),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='Canonical',
                    offer='UbuntuServer',
                    sku='18.04-LTS'
                ),
                disk_encryption_configuration=models.DiskEncryptionConfiguration(
                    targets=[models.DiskEncryptionTarget.temporary_disk]
                ),
                node_agent_sku_id='batch.node.ubuntu 18.04')
        )
        response = client.create_pool(test_ade_pool)
        assert response is None
        ade_pool = client.get_pool(test_ade_pool.id)
        assert ade_pool.virtual_machine_configuration.disk_encryption_configuration.targets == [models.DiskEncryptionTarget.temporary_disk]

        # Test List Pools without Filters
        pools = list(client.list_pools())
        assert (len(pools) > 1)

        # Test List Pools with Maximum
        pools = list(client.list_pools(maxresults=1))
        assert len(pools) == 4

        # Test List Pools with Filter
        pools = list(client.list_pools(filter='startswith(id,\'batch_app_\')',
            select='id,state',
            expand='stats'))
        assert len(pools) ==  1

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @recorded_by_proxy
    def test_batch_create_pool_with_blobfuse_mount(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Create Iaas Pool
        test_iaas_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_iaas_'),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher='MicrosoftWindowsServer',
                    offer='WindowsServer',
                    sku='2016-Datacenter-smalldisk'
                ),
                node_agent_sku_id='batch.node.windows amd64',
                windows_configuration=models.WindowsConfiguration(enable_automatic_updates=True)),
            task_scheduling_policy=models.TaskSchedulingPolicy(node_fill_type=models.BatchNodeFillType.pack),
            mount_configuration=[models.MountConfiguration(
                azure_blob_file_system_configuration=models.AzureBlobFileSystemConfiguration(
                    account_name='test',
                    container_name='https://test.blob.core.windows.net:443/test-container',
                    relative_mount_path='foo',
                    account_key='fake_account_key'
                )
            )]
        )
        response = client.create_pool(test_iaas_pool)
        assert response is None

        mount_pool = client.get_pool(test_iaas_pool.id)
        assert mount_pool.mount_configuration is not None
        assert len(mount_pool.mount_configuration) ==  1
        assert mount_pool.mount_configuration[0].azure_blob_file_system_configuration is not None
        assert mount_pool.mount_configuration[0].nfs_mount_configuration is None

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @recorded_by_proxy
    def test_batch_update_pools(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Create Paas Pool
        test_paas_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_paas_'),
            vm_size=DEFAULT_VM_SIZE,
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
        response = client.create_pool(test_paas_pool)
        assert response is None

        # Test Update Pool Options
        params = models.BatchPoolUpdateOptions(
            certificate_references=[], 
            application_package_references=[], 
            metadata=[models.MetadataItem(name='foo', value='bar')],
            target_node_communication_mode=models.NodeCommunicationMode.classic)
        response = client.update_pool(test_paas_pool.id, params)
        assert response is None

        # Test Patch Pool Options
        params = models.BatchPoolPatchOptions(metadata=[models.MetadataItem(name='foo2', value='bar2')])
        response = client.update_pool(test_paas_pool.id, params)
        assert response is None

        # Test Pool Exists
        response = client.update_pool(test_paas_pool.id)
        assert response

        # Test Get Pool
        pool = client.get_pool(test_paas_pool.id)
        assert isinstance(pool,  models.BatchPool)
        assert pool.id ==  test_paas_pool.id
        assert pool.state ==  models.PoolState.active
        assert pool.allocation_state ==  models.AllocationState.steady
        assert pool.cloud_service_configuration.os_family ==  '5'
        assert pool.vm_size ==  DEFAULT_VM_SIZE
        assert pool.start_task is None
        assert pool.metadata[0].name ==  'foo2'
        assert pool.metadata[0].value ==  'bar2'
        assert pool.target_node_communication_mode ==  models.NodeCommunicationMode.classic

        # Test Get Pool with OData Clauses
        pool = client.get_pool(pool_id=test_paas_pool.id, select='id,state', expand='stats')
        assert isinstance(pool,  models.BatchPool)
        assert pool.id ==  test_paas_pool.id
        assert pool.state ==  models.PoolState.active
        assert pool.allocation_state is None
        assert pool.vm_size is None

        # Test Delete Pool
        response = client.delete_pool(test_paas_pool.id)
        assert response is None

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @PoolPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_batch_scale_pools(self, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        client = self.create_sharedkey_client(**kwargs)
        # Test Enable Autoscale
        interval = datetime.timedelta(minutes=6)
        response = client.enable_pool_auto_scale(
            batch_pool.name,
            models.BatchPoolEnableAutoScaleOptions(
            auto_scale_formula='$TargetDedicatedNodes=2',
            auto_scale_evaluation_interval=interval))

        assert response is None

        # Test Evaluate Autoscale
        result = client.evaluate_pool_auto_scale(batch_pool.name, models.BatchPoolEnableAutoScaleOptions(auto_scale_formula='$TargetDedicatedNodes=3'))
        assert isinstance(result,  models.AutoScaleRun)
        assert result.results == '$TargetDedicatedNodes=3;$TargetLowPriorityNodes=0;$NodeDeallocationOption=requeue'
        
        # Test Disable Autoscale
        pool = client.get_pool(batch_pool.name)
        while self.is_live and pool.allocation_state != models.AllocationState.steady:
            time.sleep(5)
            pool = client.get_pool(batch_pool.name)
        response = client.disable_pool_auto_scale(batch_pool.name)
        assert response is None

        # Test Pool Resize
        pool = client.get_pool(batch_pool.name)
        while self.is_live and pool.allocation_state != models.AllocationState.steady:
            time.sleep(5)
            pool = client.get_pool(batch_pool.name)
        params = models.BatchPoolResizeOptions(target_dedicated_nodes=0, target_low_priority_nodes=2)
        response = client.resize_pool(batch_pool.name, params)
        assert response is None

        # Test Stop Pool Resize
        response = client.stop_pool_resize(batch_pool.name)
        assert response is None
        pool = client.get_pool(batch_pool.name)
        while self.is_live and pool.allocation_state != models.AllocationState.steady:
            time.sleep(5)
            pool = client.get_pool(batch_pool.name)

        # Test Get Pool Usage Info
        info = list(client.list_pool_usage_metrics())
        assert info ==  []

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @recorded_by_proxy
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
        params = models.BatchJobScheduleCreateOptions(
            id=schedule_id,
            schedule=schedule,
            job_specification=job_spec
        )
        response = client.create_job_schedule(params)
        assert response is None

        # Test List Job Schedules
        schedules = list(client.list_job_schedules())
        assert (len(schedules) > 0)

        # Test Get Job Schedule
        schedule = client.get_job_schedule(schedule_id)
        assert isinstance(schedule,  models.BatchJobSchedule)
        assert schedule.id ==  schedule_id
        assert schedule.state ==  models.JobScheduleState.active

        # Test Job Schedule Exists
        exists = client.job_schedule_exists(schedule_id)
        assert exists

        # Test List Jobs from Schedule
        jobs = list(client.list_jobs_from_schedule(schedule_id))
        assert (len(jobs) > 0)

        # Test Disable Job Schedule
        response = client.disable_job_schedule(schedule_id)
        assert response is None

        # Test Enable Job Schedule
        response = client.enable_job_schedule(schedule_id)
        assert response is None

        # Test Update Job Schedule
        job_spec = models.JobSpecification(
            pool_info=models.PoolInformation(pool_id='pool_id')
        )
        schedule = models.Schedule(
            recurrence_interval=datetime.timedelta(hours=10)
        )
        params = models.BatchJobSchedule(schedule=schedule, job_specification=job_spec)
        response = client.update_job_schedule(schedule_id, params)
        assert response is None

        # Test Patch Job Schedule
        schedule = models.Schedule(
            recurrence_interval=datetime.timedelta(hours=5)
        )
        params = models.BatchJobScheduleUpdateOptions(schedule=schedule)
        response = client.patch_job_schedule(schedule_id, params)
        assert response is None

        # Test Terminate Job Schedule
        response = client.terminate_job_schedule(schedule_id)
        assert response is None

        # Test Delete Job Schedule
        response = client.delete_job_schedule(schedule_id)
        assert response is None

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @recorded_by_proxy
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
            node_agent_sku_id="batch.node.ubuntu 18.04",
            image_reference=models.ImageReference(
                publisher="Canonical",
                offer="UbuntuServer",
                sku="18.04-LTS")
        )
        pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_network_'),
            target_dedicated_nodes=1,
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=virtual_machine_config,
            network_configuration=network_config
        )

        client.create_pool(pool)
        network_pool = client.get_pool(pool.id)
        while self.is_live and network_pool.allocation_state != models.AllocationState.steady:
            time.sleep(10)
            network_pool = client.get_pool(pool.id)

        # Test Batch Node Config
        nodes = list(client.list_nodes(pool.id))
        assert len(nodes) ==  1
        assert isinstance(nodes[0],  models.BatchNode)
        assert len(nodes[0].endpoint_configuration.inbound_endpoints) ==  2
        assert nodes[0].endpoint_configuration.inbound_endpoints[0].name ==  'TestEndpointConfig.0'
        assert nodes[0].endpoint_configuration.inbound_endpoints[0].protocol ==  'udp'

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @PoolPreparer(location=AZURE_LOCATION, size=2, config='iaas')
    @recorded_by_proxy
    def test_batch_compute_nodes(self, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        client = self.create_sharedkey_client(**kwargs)
        # Test List Batch Nodes
        nodes = list(client.list_nodes(batch_pool.name))
        assert len(nodes) ==  2
        while self.is_live and any([n for n in nodes if n.state != models.BatchNodeState.IDLE]):
            time.sleep(10)
            nodes = list(client.list_nodes(batch_pool.name))
        assert len(nodes) ==  2

        # Test Get Batch Node
        node = client.get_node(batch_pool.name, nodes[0].id)
        assert isinstance(node,  models.BatchNode)
        assert node.scheduling_state ==  models.SchedulingState.enabled
        assert node.is_dedicated
        assert node.node_agent_info is not None
        assert node.node_agent_info.version is not None


        # Test Upload Log
        config = models.UploadBatchServiceLogsOptions(
            container_url = "https://computecontainer.blob.core.windows.net/", 
            start_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=6))
        set_custom_default_matcher(
            compare_bodies=False,
            ignored_headers="Accept, ocp-date",
            # excluded_headers=" client-request-id"
        )
        result = client.upload_node_logs(batch_pool.name, nodes[0].id, config)
        assert result is not None
        assert result.number_of_files_uploaded > 0
        assert result.virtual_directory_name is not None

        # Test Disable Scheduling
        response = client.disable_node_scheduling(batch_pool.name, nodes[0].id)
        assert response is None

        # Test Enable Scheduling
        response = client.enable_node_scheduling(batch_pool.name, nodes[0].id)
        assert response is None

        # Test Reboot Node
        response = client.reboot_node(
            batch_pool.name, nodes[0].id, models.NodeRebootOptions(node_reboot_option=models.BatchNodeRebootOption.terminate))
        assert response is None

        # Test Reimage Node
        self.assertBatchError('OperationNotValidOnNode',
                              client.reimage_node,
                              batch_pool.name,
                              nodes[1].id,
                              models.NodeReimageOptions(node_reimage_option=models.BatchNodeReimageOption.terminate))

        # Test Remove Nodes
        options = models.NodeRemoveOptions(node_list=[n.id for n in nodes])
        response = client.remove_nodes_pool(batch_pool.name, options)
        assert response is None

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @recorded_by_proxy
    def test_batch_compute_node_extensions(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)


        # Test Create Iaas Pool
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
        extension = models.VMExtension(name="secretext",type="KeyVaultForLinux",publisher="Microsoft.Azure.KeyVault",
        type_handler_version="1.0",auto_upgrade_minor_version=True)
        virtual_machine_config = models.VirtualMachineConfiguration(
            node_agent_sku_id="batch.node.ubuntu 18.04",
            extensions=[extension],
            image_reference=models.ImageReference(
                publisher="Canonical",
                offer="UbuntuServer",
                sku="18.04-LTS")
        )
        batch_pool = models.BatchPoolCreateOptions(
            id=self.get_resource_name('batch_network_'),
            target_dedicated_nodes=1,
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=virtual_machine_config,
            network_configuration=network_config
        )
        response = client.create_pool(batch_pool)
        assert response is None

        batch_pool = client.get_pool(batch_pool.id)
        while self.is_live and batch_pool.allocation_state != models.AllocationState.steady:
            time.sleep(10)
            batch_pool = client.get_pool(batch_pool.id)


        nodes = list(client.list_nodes(batch_pool.id))
        assert len(nodes) == 1


        extensions = list(client.list_node_extensions(batch_pool.id,nodes[0].id))
        assert extensions is not None
        assert len(extensions) == 2
        extension = client.get_node_extension(batch_pool.id,nodes[0].id, extensions[1].vm_extension.name)
        assert extension is not None
        assert extension.vm_extension.name == "secretext"
        assert extension.vm_extension.publisher == "Microsoft.Azure.KeyVault"
        assert extension.vm_extension.type == "KeyVaultForLinux"

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @PoolPreparer(location=AZURE_LOCATION, size=1)
    @recorded_by_proxy
    def test_batch_compute_node_user(self, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        client = self.create_sharedkey_client(**kwargs)
        nodes = list(client.list_nodes(batch_pool.name))
        while self.is_live and any([n for n in nodes if n.state != models.BatchNodeState.idle]):
            time.sleep(10)
            nodes = list(client.list_nodes(batch_pool.name))
        assert len(nodes) ==  1

        # Test Add User
        user_name = 'BatchPythonSDKUser'
        nodes = list(client.list_nodes(batch_pool.name))
        user = models.BatchNodeUserCreateOptions(name=user_name, password=BATCH_TEST_PASSWORD, is_admin=False)
        response = client.create_node_user(batch_pool.name, nodes[0].id, user)
        assert response is None

        # Test Update User
        user = models.BatchNodeUserUpdateOptions(password='liilef#$DdRGSa_ewkjh')
        response = client.replace_node_user(batch_pool.name, nodes[0].id, user_name, user)
        assert response is None

        # Test Get remote login settings
        remote_login_settings = client.get_node_remote_login_settings(batch_pool.name, nodes[0].id)
        assert isinstance(remote_login_settings,  models.BatchNodeRemoteLoginSettingsResult)
        assert remote_login_settings.remote_login_ip_address is not None
        assert remote_login_settings.remote_login_port is not None

        # Test Delete User
        response = client.delete_node_user(batch_pool.name, nodes[0].id, user_name)
        assert response is None

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @PoolPreparer(location=AZURE_LOCATION, size=1, config="paas")
    @recorded_by_proxy
    def test_batch_compute_node_remote_desktop(self, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        client = self.create_sharedkey_client(**kwargs)
        nodes = list(client.list_nodes(batch_pool.name))
        while self.is_live and any([n for n in nodes if n.state != models.BatchNodeState.idle]):
            time.sleep(10)
            nodes = list(client.list_nodes(batch_pool.name))
        assert len(nodes) ==  1


        # Test Get remote desktop 
        file_length = 0
        with io.BytesIO() as file_handle:
            remote_desktop = client.get_node_remote_desktop_file(batch_pool.name, nodes[0].id)
            assert remote_desktop is not None
            for data in remote_desktop:
                file_length += len(data)
        assert 'full address' in str(data)


    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @StorageAccountPreparer(name_prefix='batch4', location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT, name_prefix='batch4')
    @PoolPreparer(os="Windows",size=1)
    @JobPreparer()
    @recorded_by_proxy
    def test_batch_files(self, **kwargs):

        batch_pool = kwargs.pop("batch_pool")
        batch_job = kwargs.pop("batch_job")
        client = self.create_sharedkey_client(**kwargs)
        nodes = list(client.list_nodes(batch_pool.name))
        while self.is_live and any([n for n in nodes if n.state != models.BatchNodeState.idle]):
            time.sleep(10)
            nodes = list(client.list_nodes(batch_pool.name))
        assert len(nodes) ==  1
        node = nodes[0].id
        task_id = 'test_task'
        task_param = models.BatchTaskCreateOptions(id=task_id, command_line='cmd /c "echo hello world"')
        response = client.create_task(batch_job.id, task_param)
        assert response is None
        task = client.get_task(batch_job.id, task_id)
        while self.is_live and task.state != models.TaskState.completed:
            time.sleep(5)
            task = client.get_task(batch_job.id, task_id)

        # Test List Files from Batch Node
        all_files = client.list_node_files(batch_pool.name, node, recursive=True)
        only_files = [f for f in all_files if not f.is_directory]
        assert (len(only_files) >= 2)

        # Test File Properties from Batch Node
        props = client.get_node_file_properties(
            batch_pool.name, node, only_files[0].name)
        assert ('Content-Length' in props.headers)
        assert ('Content-Type' in props.headers)

        # Test Get File from Batch Node
        file_length = 0
        with io.BytesIO() as file_handle:
            response = client.get_node_file(batch_pool.name, node, only_files[0].name)
            #lenght = len(response)
            for data in response:
                file_length += len(data)
        assert file_length ==  int(props.headers['Content-Length'])

        # Test Delete File from Batch Node
        response = client.delete_node_file(batch_pool.name, node, only_files[0].name)
        assert response is None

        # Test List Files from Task
        all_files = client.list_task_files(batch_job.id, task_id)
        only_files = [f for f in all_files if not f.is_directory]
        assert (len(only_files) >= 1)

        # Test File Properties from Task
        props = client.get_task_file_properties(
            job_id=batch_job.id, task_id=task_id, file_path=only_files[0].name)
        assert ('Content-Length' in props.headers)
        assert ('Content-Type' in props.headers)

        # Test Get File from Task
        file_length = 0
        with io.BytesIO() as file_handle:
            response = client.get_task_file(batch_job.id, task_id, only_files[0].name)
            for data in response:
                file_length += len(data)
        assert file_length ==  int(props.headers['Content-Length'])
        assert 'hello world' in str(data)

        # Test Delete File from Task
        response = client.delete_task_file(batch_job.id, task_id, only_files[0].name)
        assert response is None

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @JobPreparer(on_task_failure=models.OnTaskFailure.perform_exit_options_job_action)
    @recorded_by_proxy
    def test_batch_tasks(self, **kwargs):
        batch_job = kwargs.pop("batch_job")
        client = self.create_sharedkey_client(**kwargs)

        # Test Create Task with Auto Complete
        exit_conditions = models.ExitConditions(
            exit_codes=[models.ExitCodeMapping(code=1, exit_options=models.ExitOptions(job_action=models.JobAction.terminate))],
            exit_code_ranges=[models.ExitCodeRangeMapping(start=2, end=4, exit_options=models.ExitOptions(job_action=models.JobAction.disable))],
            default=models.ExitOptions(job_action=models.JobAction.none))
        task_param = models.BatchTaskCreateOptions(
            id=self.get_resource_name('batch_task1_'),
            command_line='cmd /c "echo hello world"',
            exit_conditions=exit_conditions
        )
        try:
            client.create_task(batch_job.id, task_param)
        except azure.core.exceptions.HttpResponseError as e:
            message = "{}: ".format(e.error.code, e.error.message)
            for v in e.model.values:
                message += "\n{}: {}".format(v.key, v.value)
            raise Exception(message)
        task = client.get_task(batch_job.id, task_param.id)
        assert isinstance(task,  models.BatchTask)
        assert task.exit_conditions.default.job_action ==  models.JobAction.none
        assert task.exit_conditions.exit_codes[0].code ==  1
        assert task.exit_conditions.exit_codes[0].exit_options.job_action ==  models.JobAction.terminate

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
        task_param = models.BatchTaskCreateOptions(
            id=self.get_resource_name('batch_task2_'),
            command_line='cmd /c "echo hello world"',
            output_files=outputs
        )
        client.create_task(batch_job.id, task_param)
        task = client.get_task(batch_job.id, task_param.id)
        assert isinstance(task,  models.BatchTask)
        assert len(task.output_files) ==  2

        # Test Create Task with Auto User
        auto_user = models.AutoUserSpecification(
            scope=models.AutoUserScope.task,
            elevation_level=models.ElevationLevel.admin)
        task_param = models.BatchTaskCreateOptions(
            id=self.get_resource_name('batch_task3_'),
            command_line='cmd /c "echo hello world"',
            user_identity=models.UserIdentity(auto_user=auto_user)
        )
        client.create_task(batch_job.id, task_param)
        task = client.get_task(batch_job.id, task_param.id)
        assert isinstance(task,  models.BatchTask)
        assert task.user_identity.auto_user.scope ==  models.AutoUserScope.task
        assert task.user_identity.auto_user.elevation_level ==  models.ElevationLevel.admin

        # Test Create Task with Token Settings
        task_param = models.BatchTaskCreateOptions(
            id=self.get_resource_name('batch_task4_'),
            command_line='cmd /c "echo hello world"',
            authentication_token_settings=models.AuthenticationTokenSettings(
                access=[models.AccessScope.job])
        )
        client.create_task(batch_job.id, task_param)
        task = client.get_task(batch_job.id, task_param.id)
        assert isinstance(task,  models.BatchTask)
        assert task.authentication_token_settings.access[0] ==  models.AccessScope.job

        # Test Create Task with Container Settings
        task_param = models.BatchTaskCreateOptions(
            id=self.get_resource_name('batch_task5_'),
            command_line='cmd /c "echo hello world"',
            container_settings=models.TaskContainerSettings(
                image_name='windows_container:latest',
                registry=models.ContainerRegistry(username='username', password='password'))
        )
        client.create_task(batch_job.id, task_param)
        task = client.get_task(batch_job.id, task_param.id)
        assert isinstance(task,  models.BatchTask)
        assert task.container_settings.image_name ==  'windows_container:latest'
        assert task.container_settings.registry.username ==  'username'

        # Test Create Task with Run-As-User
        task_param = models.BatchTaskCreateOptions(
            id=self.get_resource_name('batch_task6_'),
            command_line='cmd /c "echo hello world"',
            user_identity=models.UserIdentity(username='task-user')
        )
        client.create_task(batch_job.id, task_param)
        task = client.get_task(batch_job.id, task_param.id)
        assert isinstance(task,  models.BatchTask)
        assert task.user_identity.username ==  'task-user'

        # Test Add Task Collection
        tasks = []
        for i in range(7, 10):
            tasks.append(models.BatchTaskCreateOptions(
                id=self.get_resource_name('batch_task{}_'.format(i)),
                command_line='cmd /c "echo hello world"'))
        result = client.create_task_collection(batch_job.id, collection=tasks)
        assert isinstance(result,  models.TaskAddCollectionResult)
        assert len(result.value) ==  3
        assert result.value[0].status ==  models.TaskAddStatus.success

        # Test List Tasks
        tasks = list(client.list_tasks(batch_job.id))
        assert len(tasks) ==  9

        # Test Count Tasks
        task_results = client.get_job_task_counts(batch_job.id)
        assert isinstance(task_results,  models.TaskCountsResult)
        assert task_results.task_counts.completed ==  0
        assert task_results.task_counts.succeeded ==  0

        # Test Terminate Task
        response = client.terminate_task(batch_job.id, task_param.id)
        assert response is None
        task = client.get_task(batch_job.id, task_param.id)
        assert task.state ==  models.TaskState.completed

        # Test Reactivate Task
        response = client.reactivate_task(batch_job.id, task_param.id)
        assert response is None
        task = client.get_task(batch_job.id, task_param.id)
        assert task.state ==  models.TaskState.active

        # Test Update Task
        response = client.replace_task(
            job_id=batch_job.id, task_id=task_param.id,
            body=models.BatchTask(constraints=models.TaskConstraints(max_task_retry_count=1)))
        assert response is None

        # Test Get Subtasks
        # TODO: Test with actual subtasks
        subtasks = client.list_sub_tasks(batch_job.id, task_param.id)
        assert isinstance(subtasks,  models.BatchTaskListSubtasksResult)
        assert subtasks.value ==  []

        # Test Delete Task
        response = client.delete_task(batch_job.id, task_param.id)
        assert response is None

        # Test Bulk Add Task Failure
        task_id = "mytask"
        tasks_to_add = []
        resource_files = []
        for i in range(10000):
            resource_file = models.ResourceFile(
                http_url="https://mystorageaccount.blob.core.windows.net/files/resourceFile{}".format(str(i)),
                file_path="resourceFile{}".format(str(i)))
            resource_files.append(resource_file)
        task = models.BatchTaskCreateOptions(
            id=task_id,
            command_line="sleep 1",
            resource_files=resource_files)
        tasks_to_add.append(task)
        self.assertCreateTasksError(
            "RequestBodyTooLarge",
            client.create_task_collection,
            batch_job.id,
            tasks_to_add)
        self.assertCreateTasksError(
            "RequestBodyTooLarge",
            client.create_task_collection,
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
            task = models.BatchTaskCreateOptions(
                id=task_id + str(i),
                command_line="sleep 1",
                resource_files=resource_files)
            tasks_to_add.append(task)
        result = client.create_task_collection(batch_job.id, tasks_to_add)
        assert isinstance(result,  models.TaskAddCollectionResult)
        assert len(result.value) ==  733
        assert result.value[0].status ==  models.TaskAddStatus.success
        assert (
            all(t.status == models.TaskAddStatus.success for t in result.value))

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @recorded_by_proxy
    def test_batch_jobs(self, **kwargs):
        client = self.create_sharedkey_client(**kwargs)
        # Test Create Job
        auto_pool = models.AutoPoolSpecification(
            pool_lifetime_option=models.PoolLifetimeOption.job,
            pool=models.PoolSpecification(
                vm_size=DEFAULT_VM_SIZE,
                cloud_service_configuration=models.CloudServiceConfiguration(
                    os_family='5'
                )
            )
        )
        job_prep = models.JobPreparationTask(command_line="cmd /c \"echo hello world\"")
        job_release = models.JobReleaseTask(command_line="cmd /c \"echo goodbye world\"")
        job_param = models.BatchJobCreateOptions(
            id=self.get_resource_name('batch_job1_'),
            pool_info=models.PoolInformation(
                auto_pool_specification=auto_pool
            ),
            job_preparation_task=job_prep,
            job_release_task=job_release
        )
        
        now = datetime.datetime.now()
        # stamp = mktime(now.timetuple())
        # currenttime =  format_date_time(stamp) #--> Wed, 22 Oct 2008 10:52:40 GMT
        
        response = client.create_job(body=job_param,ocp_date=now)
        
        #response = client.create_job(body=job_param,ocp_date="Wed, 3 May 2023 21:49:13 GMT")
        #response = client.create_job(body=job_param,ocp_date=datetime.datetime.utcnow())
        assert response is None

        # Test Update Job
        constraints = models.JobConstraints(max_task_retry_count=3)
        options = models.BatchJob(
            priority=500,
            constraints=constraints,
            pool_info=models.PoolInformation(
                auto_pool_specification=auto_pool
            )
        )
        response = client.update_job(job_param.id, options)
        assert response is None

        # Test Patch Job
        options = models.BatchJobUpdateOptions(priority=900)
        response = client.patch_job(job_param.id, options)
        assert response is None

        job = client.get_job(job_param.id)
        assert isinstance(job,  models.BatchJob)
        assert job.id ==  job_param.id
        assert job.constraints.max_task_retry_count ==  3
        assert job.priority ==  900


        # Test Create Job with Auto Complete
        job_auto_param = models.BatchJobCreateOptions(
            id=self.get_resource_name('batch_job2_'),
            on_all_tasks_complete=models.OnAllTasksComplete.terminate_job,
            on_task_failure=models.OnTaskFailure.perform_exit_options_job_action,
            pool_info=models.PoolInformation(
                auto_pool_specification=auto_pool
            )
        )
        response = client.create_job(job_auto_param)
        assert response is None
        job = client.get_job(job_auto_param.id)
        assert isinstance(job,  models.BatchJob)
        assert job.on_all_tasks_complete ==  models.OnAllTasksComplete.terminate_job
        assert job.on_task_failure ==  models.OnTaskFailure.perform_exit_options_job_action

        # Test List Jobs
        jobs = client.list_job()
        assert isinstance(jobs, Iterable)
        assert len(list(jobs)) ==  2

        # Test Disable Job
        response = client.disable_job(job_id=job_param.id,body=models.BatchJobDisableOptions(disable_tasks="requeue"))
        assert response is None

        # Test Enable Job
        response = client.enable_job(job_param.id)
        assert response is None

        # Prep and release task status
        task_status = client.list_preparation_and_release_task_status_job(job_param.id)
        assert isinstance(task_status,  Iterable)
        assert list(task_status) ==  []

        # Test Terminate Job
        response = client.terminate_job(job_param.id)
        assert response is None

        # Test Delete Job
        response = client.delete_job(job_auto_param.id)
        assert response is None

        
