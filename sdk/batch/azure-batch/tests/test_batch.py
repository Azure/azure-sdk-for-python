# pylint: disable=too-many-lines
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import datetime
import io
import hashlib
import time
import binascii
import pytest
import six

import azure.core.exceptions
from azure.batch import models
from azure.batch.aio import BatchClient as AsyncBatchClient
from azure.batch import BatchClient as SyncBatchClient
from typing import Iterable, Union

from batch_preparers import AccountPreparer, PoolPreparer, JobPreparer
from async_wrapper import wrap_list_result, wrap_result, wrap_file_result
from decorators import recorded_by_proxy_async, client_setup

from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    StorageAccountPreparer,
    CachedResourceGroupPreparer,
    set_custom_default_matcher,
)

# toggle to test sync or async client
TEST_SYNC_CLIENT = False
BatchClient = Union[SyncBatchClient, AsyncBatchClient]

AZURE_LOCATION = "eastus2"
BATCH_ENVIRONMENT = None  # Set this to None if testing against prod
BATCH_RESOURCE = "https://batch.core.windows.net/"
DEFAULT_VM_SIZE = "standard_d2_v2"
SECRET_FIELDS = ["primary", "secondary"]


import platform
import asyncio

# Workaround to disable "Asyncio Event Loop is Closed" errors on Windows
# From: https://stackoverflow.com/questions/45600579/
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def get_redacted_key(key):
    redacted_value = "redacted"
    digest = hashlib.sha256(six.ensure_binary(key)).digest()
    redacted_value += six.ensure_str(binascii.hexlify(digest))[:6]
    return redacted_value


class TestBatch(AzureMgmtRecordedTestCase):
    def fail(self, err):
        raise RuntimeError(err)

    async def assertBatchError(self, code, func, *args, **kwargs):
        try:
            await wrap_result(func(*args, **kwargs))
            self.fail("BatchErrorException expected but not raised")
        except azure.core.exceptions.HttpResponseError as err:
            assert err.error.code == code
        except Exception as err:
            self.fail("Expected BatchErrorException, instead got: {!r}".format(err))

    async def assertCreateTasksError(self, code, func, *args, **kwargs):
        try:
            await wrap_result(func(*args, **kwargs))
            self.fail("CreateTasksError expected but not raised")
        except models.CreateTasksError as err:
            try:
                batch_error = err.errors.pop()
                if code:
                    # self.assertEqual(batch_error.error.code, code)
                    assert batch_error.error.code == code
            except IndexError:
                pytest.fail("Inner BatchErrorException expected but not exist")
        except Exception as err:
            pytest.fail("Expected CreateTasksError, instead got: {!r}".format(err))
    
    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_certificates(self, client: BatchClient, **kwargs):
        # Test Add Certificate
        certificate = models.BatchCertificate(
            thumbprint="cff2ab63c8c955aaf71989efa641b906558d9fb7",
            thumbprint_algorithm="sha1",
            data="MIIGMQIBAzCCBe0GCSqGSIb3DQEHAaCCBd4EggXaMIIF1jCCA8AGCSqGSIb3DQEHAaCCA7EEggOtMIIDqTCCA6UGCyqGSIb3DQEMCgECoIICtjCCArIwHAYKKoZIhvcNAQwBAzAOBAhyd3xCtln3iQICB9AEggKQhe5P10V9iV1BsDlwWT561Yu2hVq3JT8ae/ebx1ZR/gMApVereDKkS9Zg4vFyssusHebbK5pDpU8vfAqle0TM4m7wGsRj453ZorSPUfMpHvQnAOn+2pEpWdMThU7xvZ6DVpwhDOQk9166z+KnKdHGuJKh4haMT7Rw/6xZ1rsBt2423cwTrQVMQyACrEkianpuujubKltN99qRoFAxhQcnYE2KlYKw7lRcExq6mDSYAyk5xJZ1ZFdLj6MAryZroQit/0g5eyhoNEKwWbi8px5j71pRTf7yjN+deMGQKwbGl+3OgaL1UZ5fCjypbVL60kpIBxLZwIJ7p3jJ+q9pbq9zSdzshPYor5lxyUfXqaso/0/91ayNoBzg4hQGh618PhFI6RMGjwkzhB9xk74iweJ9HQyIHf8yx2RCSI22JuCMitPMWSGvOszhbNx3AEDLuiiAOHg391mprEtKZguOIr9LrJwem/YmcHbwyz5YAbZmiseKPkllfC7dafFfCFEkj6R2oegIsZo0pEKYisAXBqT0g+6/jGwuhlZcBo0f7UIZm88iA3MrJCjlXEgV5OcQdoWj+hq0lKEdnhtCKr03AIfukN6+4vjjarZeW1bs0swq0l3XFf5RHa11otshMS4mpewshB9iO9MuKWpRxuxeng4PlKZ/zuBqmPeUrjJ9454oK35Pq+dghfemt7AUpBH/KycDNIZgfdEWUZrRKBGnc519C+RTqxyt5hWL18nJk4LvSd3QKlJ1iyJxClhhb/NWEzPqNdyA5cxen+2T9bd/EqJ2KzRv5/BPVwTQkHH9W/TZElFyvFfOFIW2+03RKbVGw72Mr/0xKZ+awAnEfoU+SL/2Gj2m6PHkqFX2sOCi/tN9EA4xgdswEwYJKoZIhvcNAQkVMQYEBAEAAAAwXQYJKwYBBAGCNxEBMVAeTgBNAGkAYwByAG8AcwBvAGYAdAAgAFMAdAByAG8AbgBnACAAQwByAHkAcAB0AG8AZwByAGEAcABoAGkAYwAgAFAAcgBvAHYAaQBkAGUAcjBlBgkqhkiG9w0BCRQxWB5WAFAAdgBrAFQAbQBwADoANABjAGUANgAwADQAZABhAC0AMAA2ADgAMQAtADQANAAxADUALQBhADIAYwBhAC0ANQA3ADcAMwAwADgAZQA2AGQAOQBhAGMwggIOBgkqhkiG9w0BBwGgggH/BIIB+zCCAfcwggHzBgsqhkiG9w0BDAoBA6CCAcswggHHBgoqhkiG9w0BCRYBoIIBtwSCAbMwggGvMIIBXaADAgECAhAdka3aTQsIsUphgIXGUmeRMAkGBSsOAwIdBQAwFjEUMBIGA1UEAxMLUm9vdCBBZ2VuY3kwHhcNMTYwMTAxMDcwMDAwWhcNMTgwMTAxMDcwMDAwWjASMRAwDgYDVQQDEwdub2Rlc2RrMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC5fhcxbJHxxBEIDzVOMc56s04U6k4GPY7yMR1m+rBGVRiAyV4RjY6U936dqXHCVD36ps2Q0Z+OeEgyCInkIyVeB1EwXcToOcyeS2YcUb0vRWZDouC3tuFdHwiK1Ed5iW/LksmXDotyV7kpqzaPhOFiMtBuMEwNJcPge9k17hRgRQIDAQABo0swSTBHBgNVHQEEQDA+gBAS5AktBh0dTwCNYSHcFmRjoRgwFjEUMBIGA1UEAxMLUm9vdCBBZ2VuY3mCEAY3bACqAGSKEc+41KpcNfQwCQYFKw4DAh0FAANBAHl2M97QbpzdnwO5HoRBsiEExOcLTNg+GKCr7HUsbzfvrUivw+JLL7qjHAIc5phnK+F5bQ8HKe0L9YXBSKl+fvwxFTATBgkqhkiG9w0BCRUxBgQEAQAAADA7MB8wBwYFKw4DAhoEFGVtyGMqiBd32fGpzlGZQoRM6UQwBBTI0YHFFqTS4Go8CoLgswn29EiuUQICB9A=",
            certificate_format=models.BatchCertificateFormat.PFX,
            password="nodesdk",
        )

        response = await wrap_result(client.create_certificate(certificate))
        assert response is None

        # Test List Certificates
        certs = await wrap_list_result(client.list_certificates())
        test_cert = [c for c in certs if c.thumbprint == "cff2ab63c8c955aaf71989efa641b906558d9fb7"]
        assert len(test_cert) == 1

        # Test Get Certificate
        cert = await wrap_result(client.get_certificate("sha1", "cff2ab63c8c955aaf71989efa641b906558d9fb7"))
        assert cert.thumbprint == "cff2ab63c8c955aaf71989efa641b906558d9fb7"
        assert cert.thumbprint_algorithm == "sha1"
        assert cert.delete_certificate_error is None

        # Test Cancel Certificate Delete
        await self.assertBatchError(
            "CertificateStateActive",
            client.cancel_certificate_deletion,
            "sha1",
            "cff2ab63c8c955aaf71989efa641b906558d9fb7",
        )

        # Test Delete Certificate
        response = await wrap_result(client.delete_certificate("sha1", "cff2ab63c8c955aaf71989efa641b906558d9fb7"))
        assert response is None

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_create_pools(self, client: BatchClient, **kwargs):
        # Test Create Iaas Pool
        users = [
            models.UserAccount(name="test-user-1", password="secret"),
            models.UserAccount(
                name="test-user-2",
                password="secret",
                elevation_level=models.ElevationLevel.ADMIN,
            ),
        ]
        test_iaas_pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_iaas_"),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher="MicrosoftWindowsServer",
                    offer="WindowsServer",
                    sku="2016-Datacenter-smalldisk",
                ),
                node_agent_sku_id="batch.node.windows amd64",
                windows_configuration=models.WindowsConfiguration(enable_automatic_updates=True),
            ),
            task_scheduling_policy=models.BatchTaskSchedulingPolicy(node_fill_type=models.BatchNodeFillType.PACK),
            user_accounts=users,
            target_node_communication_mode=models.BatchNodeCommunicationMode.CLASSIC,
        )
        response = await wrap_result(client.create_pool(test_iaas_pool))
        assert response is None

        # Test list pool node counnt
        counts = list(await wrap_list_result(client.list_pool_node_counts()))
        assert counts is not None
        assert len(counts) == 1
        assert counts[0].pool_id == test_iaas_pool.id
        assert counts[0].dedicated is not None
        assert counts[0].dedicated.total == 0
        assert counts[0].dedicated.leaving_pool == 0
        assert counts[0].low_priority is not None
        assert counts[0].low_priority.total == 0

        # Test Create Pool with Network Configuration
        # TODO Public IP tests
        network_config = models.NetworkConfiguration(
            subnet_id="/subscriptions/00000000-0000-0000-0000-000000000000"
            "/resourceGroups/test"
            "/providers/Microsoft.Network"
            "/virtualNetworks/vnet1"
            "/subnets/subnet1"
        )
        test_network_pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_network_"),
            vm_size=DEFAULT_VM_SIZE,
            network_configuration=network_config,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(publisher="Canonical", offer="UbuntuServer", sku="18.04-LTS"),
                node_agent_sku_id="batch.node.ubuntu 18.04",
            ),
        )
        await self.assertBatchError(
            "InvalidPropertyValue",
            client.create_pool,
            pool=test_network_pool,
            timeout=45,
        )

        test_image_pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_image_"),
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
                node_agent_sku_id="batch.node.ubuntu 18.04",
            ),
        )
        await self.assertBatchError("InvalidPropertyValue", client.create_pool, pool=test_image_pool, timeout=45)

        # Test Create Pool with Data Disk
        data_disk = models.DataDisk(logical_unit_number=1, disk_size_gb=50)
        test_disk_pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_disk_"),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(publisher="Canonical", offer="UbuntuServer", sku="18.04-LTS"),
                node_agent_sku_id="batch.node.ubuntu 18.04",
                data_disks=[data_disk],
            ),
            target_node_communication_mode=models.BatchNodeCommunicationMode.CLASSIC,
        )
        response = await wrap_result(client.create_pool(test_disk_pool))
        assert response is None
        disk_pool = await wrap_result(client.get_pool(test_disk_pool.id))
        assert disk_pool.virtual_machine_configuration is not None
        assert disk_pool.virtual_machine_configuration.data_disks is not None
        assert disk_pool.virtual_machine_configuration.data_disks[0].logical_unit_number == 1
        assert disk_pool.virtual_machine_configuration.data_disks[0].disk_size_gb == 50
        assert disk_pool.target_node_communication_mode == models.BatchNodeCommunicationMode.CLASSIC

        # Test Create Pool with Azure Disk Encryption
        test_ade_pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_ade_"),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(publisher="Canonical", offer="UbuntuServer", sku="18.04-LTS"),
                disk_encryption_configuration=models.DiskEncryptionConfiguration(
                    targets=[models.DiskEncryptionTarget.TEMPORARY_DISK]
                ),
                node_agent_sku_id="batch.node.ubuntu 18.04",
            ),
        )
        response = await wrap_result(client.create_pool(test_ade_pool))
        # assert response is None
        ade_pool = await wrap_result(client.get_pool(test_ade_pool.id))
        assert ade_pool.virtual_machine_configuration is not None
        assert ade_pool.virtual_machine_configuration.disk_encryption_configuration is not None
        assert ade_pool.virtual_machine_configuration.disk_encryption_configuration.targets == [
            models.DiskEncryptionTarget.TEMPORARY_DISK
        ]

        # Test List Pools without Filters
        pools = list(await wrap_list_result(client.list_pools()))
        assert len(pools) > 1

        # Test List Pools with Maximum
        pools = list(await wrap_list_result(client.list_pools(max_results=1)))
        assert len(pools) == 3

        # Test List Pools with Filter
        pools = list(
            await wrap_list_result(
                client.list_pools(
                    filter="startswith(id,'batch_ade_')",
                    select=["id,state"],
                    expand=["stats"],
                )
            ),
        )
        assert len(pools) == 1

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_create_pool_with_blobfuse_mount(self, client: BatchClient, **kwargs):
        # Test Create Iaas Pool
        test_iaas_pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_iaas_"),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.ImageReference(
                    publisher="MicrosoftWindowsServer",
                    offer="WindowsServer",
                    sku="2016-Datacenter-smalldisk",
                ),
                node_agent_sku_id="batch.node.windows amd64",
                windows_configuration=models.WindowsConfiguration(enable_automatic_updates=True),
            ),
            task_scheduling_policy=models.BatchTaskSchedulingPolicy(node_fill_type=models.BatchNodeFillType.PACK),
            mount_configuration=[
                models.MountConfiguration(
                    azure_blob_file_system_configuration=models.AzureBlobFileSystemConfiguration(
                        account_name="test",
                        container_name="https://test.blob.core.windows.net:443/test-container",
                        relative_mount_path="foo",
                        account_key="fake_account_key",
                    )
                )
            ],
        )
        response = await wrap_result(client.create_pool(test_iaas_pool))
        assert response is None

        mount_pool = await wrap_result(client.get_pool(test_iaas_pool.id))
        assert mount_pool.mount_configuration is not None
        assert len(mount_pool.mount_configuration) == 1
        assert mount_pool.mount_configuration[0].azure_blob_file_system_configuration is not None
        assert mount_pool.mount_configuration[0].nfs_mount_configuration is None

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_update_pools(self, client: BatchClient, **kwargs):
        test_paas_pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_paas_"),
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                node_agent_sku_id="batch.node.ubuntu 18.04",
                image_reference=models.ImageReference(publisher="Canonical", offer="UbuntuServer", sku="18.04-LTS"),
            ),
            start_task=models.BatchStartTask(
                command_line='cmd.exe /c "echo hello world"',
                resource_files=[models.ResourceFile(http_url="https://contoso.com", file_path="filename.txt")],
                environment_settings=[models.EnvironmentSetting(name="ENV_VAR", value="env_value")],
                user_identity=models.UserIdentity(
                    auto_user=models.AutoUserSpecification(elevation_level=models.ElevationLevel.ADMIN)
                ),
            ),
        )
        response = await wrap_result(client.create_pool(test_paas_pool))
        assert response is None

        # Test Update Pool Options
        params = models.BatchPoolReplaceContent(
            certificate_references=[],
            application_package_references=[],
            metadata=[models.MetadataItem(name="foo", value="bar")],
            target_node_communication_mode=models.BatchNodeCommunicationMode.CLASSIC,
        )
        response = await wrap_result(client.replace_pool_properties(test_paas_pool.id, params))
        assert response is None

        # Test Patch Pool Options
        params = models.BatchPoolUpdateContent(metadata=[models.MetadataItem(name="foo2", value="bar2")])
        response = await wrap_result(client.update_pool(test_paas_pool.id, params))
        assert response is None

        # Test Pool Exists
        response = await wrap_result(client.pool_exists(test_paas_pool.id))
        assert response

        # Test Get Pool
        pool = await wrap_result(client.get_pool(test_paas_pool.id))
        assert isinstance(pool, models.BatchPool)
        assert pool.id == test_paas_pool.id
        assert pool.state == models.BatchPoolState.ACTIVE
        assert pool.allocation_state == models.AllocationState.STEADY
        # assert pool.vm_configuration.node_agent_sku_id == "batch.node.ubuntu 18.04"
        assert pool.vm_size == DEFAULT_VM_SIZE
        assert pool.start_task is None
        assert pool.metadata is not None
        assert pool.metadata[0].name == "foo2"
        assert pool.metadata[0].value == "bar2"
        assert pool.target_node_communication_mode == models.BatchNodeCommunicationMode.CLASSIC

        # Test Get Pool with OData Clauses
        pool = await wrap_result(client.get_pool(pool_id=test_paas_pool.id, select=["id,state"], expand=["stats"]))
        assert isinstance(pool, models.BatchPool)
        assert pool.id == test_paas_pool.id
        assert pool.state == models.BatchPoolState.ACTIVE
        assert pool.allocation_state is None
        assert pool.vm_size is None

        # Test Delete Pool
        response = await wrap_result(client.delete_pool(test_paas_pool.id))
        assert response is None

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @PoolPreparer(location=AZURE_LOCATION)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_scale_pools(self, client: BatchClient, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        # Test Enable Autoscale
        interval = datetime.timedelta(minutes=6)
        response = await wrap_result(
            client.enable_pool_auto_scale(
                batch_pool.name,
                models.BatchPoolEnableAutoScaleContent(
                    auto_scale_formula="$TargetDedicatedNodes=2",
                    auto_scale_evaluation_interval=interval,
                ),
            )
        )

        assert response is None

        # Test Evaluate Autoscale
        result = await wrap_result(
            client.evaluate_pool_auto_scale(
                batch_pool.name,
                models.BatchPoolEvaluateAutoScaleContent(auto_scale_formula="$TargetDedicatedNodes=3"),
            )
        )
        assert isinstance(result, models.AutoScaleRun)
        assert result.results == "$TargetDedicatedNodes=3;$TargetLowPriorityNodes=0;$NodeDeallocationOption=requeue"

        # Test Disable Autoscale
        pool = await wrap_result(client.get_pool(batch_pool.name))
        while self.is_live and pool.allocation_state != models.AllocationState.STEADY:
            time.sleep(5)
            pool = await wrap_result(client.get_pool(batch_pool.name))
        response = await wrap_result(client.disable_pool_auto_scale(batch_pool.name))
        assert response is None

        # Test Pool Resize
        pool = await wrap_result(client.get_pool(batch_pool.name))
        while self.is_live and pool.allocation_state != models.AllocationState.STEADY:
            time.sleep(5)
            pool = await wrap_result(client.get_pool(batch_pool.name))
        params = models.BatchPoolResizeContent(target_dedicated_nodes=0, target_low_priority_nodes=2)
        response = await wrap_result(client.resize_pool(batch_pool.name, params))
        assert response is None

        # Test Stop Pool Resize
        response = await wrap_result(client.stop_pool_resize(batch_pool.name))
        assert response is None
        pool = await wrap_result(client.get_pool(batch_pool.name))
        while self.is_live and pool.allocation_state != models.AllocationState.STEADY:
            time.sleep(5)
            pool = await wrap_result(client.get_pool(batch_pool.name))

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_job_schedules(self, client: BatchClient, **kwargs):
        # Test Create Job Schedule
        schedule_id = self.get_resource_name("batch_schedule_")
        job_spec = models.BatchJobSpecification(
            pool_info=models.BatchPoolInfo(pool_id="pool_id"),
            constraints=models.BatchJobConstraints(max_task_retry_count=2),
            on_all_tasks_complete=models.OnAllBatchTasksComplete.TERMINATE_JOB,
        )
        schedule = models.BatchJobScheduleConfiguration(
            start_window=datetime.timedelta(hours=1),
            recurrence_interval=datetime.timedelta(days=1),
        )
        params = models.BatchJobScheduleCreateContent(id=schedule_id, schedule=schedule, job_specification=job_spec)
        response = await wrap_result(client.create_job_schedule(params))
        assert response is None

        # Test List Job Schedules
        schedules = list(await wrap_list_result(client.list_job_schedules()))
        assert len(schedules) > 0

        # Test Get Job Schedule
        schedule = await wrap_result(client.get_job_schedule(schedule_id))
        assert isinstance(schedule, models.BatchJobSchedule)
        assert schedule.id == schedule_id
        assert schedule.state == models.BatchJobScheduleState.ACTIVE

        # Test Job Schedule Exists
        exists = await wrap_result(client.job_schedule_exists(schedule_id))
        assert exists

        # Test List Jobs from Schedule
        jobs = list(await wrap_list_result(client.list_jobs_from_schedule(schedule_id)))
        assert len(jobs) > 0

        # Test Disable Job Schedule
        response = await wrap_result(client.disable_job_schedule(schedule_id))
        assert response is None

        # Test Enable Job Schedule
        response = await wrap_result(client.enable_job_schedule(schedule_id))
        assert response is None

        # Test Update Job Schedule
        job_spec = models.BatchJobSpecification(pool_info=models.BatchPoolInfo(pool_id="pool_id"))
        schedule = models.BatchJobScheduleConfiguration(recurrence_interval=datetime.timedelta(hours=10))
        params = models.BatchJobSchedule(schedule=schedule, job_specification=job_spec)
        response = await wrap_result(client.replace_job_schedule(schedule_id, params))
        assert response is None

        # Test Patch Job Schedule
        schedule = models.BatchJobScheduleConfiguration(recurrence_interval=datetime.timedelta(hours=5))
        params = models.BatchJobScheduleUpdateContent(schedule=schedule)
        response = await wrap_result(client.update_job_schedule(schedule_id, params))
        assert response is None

        # Test Terminate Job Schedule
        response = await wrap_result(client.terminate_job_schedule(schedule_id))
        assert response is None

        # Test Delete Job Schedule
        response = await wrap_result(client.delete_job_schedule(schedule_id))
        assert response is None

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_network_configuration(self, client: BatchClient, **kwargs):
        # Test Create Pool with Network Config
        network_config = models.NetworkConfiguration(
            endpoint_configuration=models.BatchPoolEndpointConfiguration(
                inbound_nat_pools=[
                    models.InboundNatPool(
                        name="TestEndpointConfig",
                        protocol=models.InboundEndpointProtocol.UDP,
                        backend_port=64444,
                        frontend_port_range_start=60000,
                        frontend_port_range_end=61000,
                        network_security_group_rules=[
                            models.NetworkSecurityGroupRule(
                                priority=150,
                                access=models.NetworkSecurityGroupRuleAccess.ALLOW,
                                source_address_prefix="*",
                            )
                        ],
                    )
                ]
            )
        )
        virtual_machine_config = models.VirtualMachineConfiguration(
            node_agent_sku_id="batch.node.ubuntu 18.04",
            image_reference=models.ImageReference(publisher="Canonical", offer="UbuntuServer", sku="18.04-LTS"),
        )
        pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_network_"),
            target_dedicated_nodes=1,
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=virtual_machine_config,
            network_configuration=network_config,
        )

        await wrap_result(client.create_pool(pool))
        network_pool: models.BatchPool = await wrap_result(client.get_pool(pool.id))
        while self.is_live and network_pool.allocation_state != models.AllocationState.STEADY:
            time.sleep(10)
            network_pool = await wrap_result(client.get_pool(pool.id))

        # Test Batch Node Config
        nodes = list(await wrap_list_result(client.list_nodes(pool.id)))
        assert len(nodes) == 1
        assert isinstance(nodes[0], models.BatchNode)
        assert nodes[0].endpoint_configuration is not None
        assert len(nodes[0].endpoint_configuration.inbound_endpoints) == 1
        assert nodes[0].endpoint_configuration.inbound_endpoints[0].name == "TestEndpointConfig.0"
        assert nodes[0].endpoint_configuration.inbound_endpoints[0].protocol == "udp"

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @PoolPreparer(location=AZURE_LOCATION, size=2, config="iaas")
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_compute_nodes(self, client: BatchClient, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        # Test List Batch Nodes
        nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        assert len(nodes) == 2
        while self.is_live and any([n for n in nodes if n.state != models.BatchNodeState.IDLE]):
            time.sleep(10)
            nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        assert len(nodes) == 2

        # Test Get Batch Node
        node = await wrap_result(client.get_node(batch_pool.name, nodes[0].id))
        assert isinstance(node, models.BatchNode)
        assert node.scheduling_state == models.SchedulingState.ENABLED
        assert node.is_dedicated
        assert node.node_agent_info is not None
        assert node.node_agent_info.version is not None

        # Test Upload Log
        config = models.UploadBatchServiceLogsContent(
            container_url="https://computecontainer.blob.core.windows.net/",
            start_time=datetime.datetime.utcnow() - datetime.timedelta(minutes=6),
        )
        set_custom_default_matcher(
            compare_bodies=False,
            ignored_headers="Accept, ocp-date, client-request-id",
            excluded_headers="Connection",
        )
        result = await wrap_result(client.upload_node_logs(batch_pool.name, nodes[0].id, config))
        assert result is not None
        assert result.number_of_files_uploaded > 0
        assert result.virtual_directory_name is not None

        # Test Disable Scheduling
        response = await wrap_result(
            client.disable_node_scheduling(
                batch_pool.name,
                nodes[0].id,
                models.BatchNodeDisableSchedulingContent(
                    node_disable_scheduling_option=models.BatchNodeDisableSchedulingOption.terminate
                ),
            )
        )
        assert response is None

        # Test Enable Scheduling
        response = await wrap_result(client.enable_node_scheduling(batch_pool.name, nodes[0].id))
        assert response is None

        # Test Reboot Node
        response = await wrap_result(
            client.reboot_node(
                batch_pool.name,
                nodes[0].id,
                models.BatchNodeRebootContent(node_reboot_option=models.BatchNodeRebootOption.TERMINATE),
            )
        )
        assert response is None

        # Test Reimage Node
        # TODO: check to see if reimage is removed from service
        # await self.assertBatchError(
        #     "OperationNotValidOnNode",
        #     client.reimage_node,
        #     batch_pool.name,
        #     nodes[1].id,
        #     models.BatchNodeReimageParameters(node_reimage_option=models.BatchNodeReimageOption.terminate),
        # )

        # Test Remove Nodes
        options = models.BatchNodeRemoveContent(node_list=[n.id for n in nodes])
        response = await wrap_result(client.remove_nodes(batch_pool.name, options))
        assert response is None

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_compute_node_extensions(self, client: BatchClient, **kwargs):
        # Test Create Iaas Pool
        network_config = models.NetworkConfiguration(
            endpoint_configuration=models.BatchPoolEndpointConfiguration(
                inbound_nat_pools=[
                    models.InboundNatPool(
                        name="TestEndpointConfig",
                        protocol=models.InboundEndpointProtocol.UDP,
                        backend_port=64444,
                        frontend_port_range_start=60000,
                        frontend_port_range_end=61000,
                        network_security_group_rules=[
                            models.NetworkSecurityGroupRule(
                                priority=150,
                                access=models.NetworkSecurityGroupRuleAccess.ALLOW,
                                source_address_prefix="*",
                            )
                        ],
                    )
                ]
            )
        )
        extension = models.VMExtension(
            name="secretext",
            type="KeyVaultForLinux",
            publisher="Microsoft.Azure.KeyVault",
            type_handler_version="1.0",
            auto_upgrade_minor_version=True,
        )
        virtual_machine_config = models.VirtualMachineConfiguration(
            node_agent_sku_id="batch.node.ubuntu 18.04",
            extensions=[extension],
            image_reference=models.ImageReference(publisher="Canonical", offer="UbuntuServer", sku="18.04-LTS"),
        )
        batch_pool = models.BatchPoolCreateContent(
            id=self.get_resource_name("batch_network_"),
            target_dedicated_nodes=1,
            vm_size=DEFAULT_VM_SIZE,
            virtual_machine_configuration=virtual_machine_config,
            network_configuration=network_config,
        )
        response = await wrap_result(client.create_pool(batch_pool))
        assert response is None

        batch_pool = await wrap_result(client.get_pool(batch_pool.id))
        while self.is_live and batch_pool.allocation_state != models.AllocationState.STEADY:
            time.sleep(10)
            batch_pool = await wrap_result(client.get_pool(batch_pool.id))

        nodes = list(await wrap_list_result(client.list_nodes(batch_pool.id)))
        assert len(nodes) == 1

        extensions = list(await wrap_list_result(client.list_node_extensions(batch_pool.id, nodes[0].id)))
        assert extensions is not None
        assert len(extensions) == 2
        extension = await wrap_result(
            client.get_node_extension(batch_pool.id, nodes[0].id, extensions[1].vm_extension.name)
        )
        assert extension is not None
        assert extension.vm_extension is not None
        assert extension.vm_extension.name == "batchNodeExtension"
        assert extension.vm_extension.publisher == "Microsoft.Azure.Extensions"
        assert extension.vm_extension.type == "CustomScript"

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @PoolPreparer(location=AZURE_LOCATION, size=1)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_compute_node_user(self, client: BatchClient, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        while self.is_live and any([n for n in nodes if n.state != models.BatchNodeState.IDLE]):
            time.sleep(10)
            nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        assert len(nodes) == 1

        # Test Add User
        user_name = "BatchPythonSDKUser"
        nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        user = models.BatchNodeUserCreateContent(name=user_name, password="secret", is_admin=False)
        response = await wrap_result(client.create_node_user(batch_pool.name, nodes[0].id, user))
        assert response is None

        # Test Update User
        user = models.BatchNodeUserUpdateContent(password="liilef#$DdRGSa_ewkjh")
        response = await wrap_result(client.replace_node_user(batch_pool.name, nodes[0].id, user_name, user))
        assert response is None

        # Test Get remote login settings
        remote_login_settings = await wrap_result(client.get_node_remote_login_settings(batch_pool.name, nodes[0].id))
        assert isinstance(remote_login_settings, models.BatchNodeRemoteLoginSettings)
        assert remote_login_settings.remote_login_ip_address is not None
        assert remote_login_settings.remote_login_port is not None

        # Test Delete User
        response = await wrap_result(client.delete_node_user(batch_pool.name, nodes[0].id, user_name))
        assert response is None

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @PoolPreparer(location=AZURE_LOCATION, size=1, config="paas")
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_compute_node_remote_desktop(self, client: BatchClient, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        while self.is_live and any([n for n in nodes if n.state != models.BatchNodeState.IDLE]):
            time.sleep(10)
            nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        assert len(nodes) == 1

        # Test Get remote desktop
        with io.BytesIO() as file_handle:
            remote_desktop_bytes = await wrap_result(
                client.get_node_remote_login_settings(batch_pool.name, nodes[0].id)
            )
            assert remote_desktop_bytes is not None
        assert "remoteLoginIPAddress" in remote_desktop_bytes

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @StorageAccountPreparer(name_prefix="batch4", location=AZURE_LOCATION)
    @AccountPreparer(
        location=AZURE_LOCATION,
        batch_environment=BATCH_ENVIRONMENT,
        name_prefix="batch4",
    )
    @PoolPreparer(os="Windows", size=1)
    @JobPreparer()
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_files(self, client: BatchClient, **kwargs):
        batch_pool = kwargs.pop("batch_pool")
        batch_job = kwargs.pop("batch_job")
        nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        while self.is_live and any([n for n in nodes if n.state != models.BatchNodeState.IDLE]):
            time.sleep(10)
            nodes = list(await wrap_list_result(client.list_nodes(batch_pool.name)))
        assert len(nodes) == 1
        node = nodes[0].id
        assert node is not None
        task_id = "test_task"
        task_param = models.BatchTaskCreateContent(id=task_id, command_line='cmd /c "echo hello world"')
        response = await wrap_result(client.create_task(batch_job.id, task_param))
        assert response is None
        task = await wrap_result(client.get_task(batch_job.id, task_id))
        while self.is_live and task.state != models.BatchTaskState.COMPLETED:
            time.sleep(5)
            task = await wrap_result(client.get_task(batch_job.id, task_id))

        # Test List Files from Batch Node
        all_files = await wrap_list_result(client.list_node_files(batch_pool.name, node, recursive=True))
        only_files = [f for f in all_files if not f.is_directory]
        assert len(only_files) >= 2

        # Test File Properties from Batch Node
        if only_files[1].name is not None:
            props = await wrap_result(client.get_node_file_properties(batch_pool.name, node, only_files[1].name))
        else:
            raise ValueError("File path is None")
        assert props.content_length is not None
        # assert props.content_type is not None # add content-type to typespec

        # Test Get File from Batch Node
        file_length = 0
        with io.BytesIO() as file_handle:
            response = await wrap_file_result(client.get_node_file(batch_pool.name, node, only_files[1].name))
            for data in response:
                file_length += len(data)
        assert file_length == props.content_length

        # Test Delete File from Batch Node
        response = await wrap_result(
            client.delete_node_file(batch_pool.name, node, only_files[1].name)
        )  # TODO: maybe delete stderr to use in the next test for content_length (against "hello world")
        assert response is None

        # Test List Files from Task
        all_files = await wrap_list_result(client.list_task_files(batch_job.id, task_id))
        only_files = [f for f in all_files if not f.is_directory]
        assert len(only_files) >= 1

        # Test File Properties from Task
        if only_files[0].name is not None:
            props = await wrap_result(
                client.get_task_file_properties(job_id=batch_job.id, task_id=task_id, file_path=only_files[0].name)
            )
        else:
            raise ValueError("File path is None")
        assert props.content_length is not None
        # assert props.content_type is not None # add content-type to typespec

        # Test Get File from Task
        file_length = 0
        with io.BytesIO() as file_handle:
            response = await wrap_file_result(client.get_task_file(batch_job.id, task_id, only_files[0].name))
            for data in response:
                file_length += len(data)
        assert file_length == props.content_length

        # Test Delete File from Task
        response = await wrap_result(client.delete_task_file(batch_job.id, task_id, only_files[0].name))
        assert response is None

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @JobPreparer(on_task_failure=models.OnBatchTaskFailure.PERFORM_EXIT_OPTIONS_JOB_ACTION)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_tasks(self, client: BatchClient, **kwargs):
        batch_job = kwargs.pop("batch_job")
        # Test Create Task with Auto Complete
        exit_conditions = models.ExitConditions(
            exit_codes=[
                models.ExitCodeMapping(
                    code=1,
                    exit_options=models.ExitOptions(job_action=models.BatchJobAction.TERMINATE),
                )
            ],
            exit_code_ranges=[
                models.ExitCodeRangeMapping(
                    start=2,
                    end=4,
                    exit_options=models.ExitOptions(job_action=models.BatchJobAction.DISABLE),
                )
            ],
            default=models.ExitOptions(job_action=models.BatchJobAction.NONE),
        )
        task_param = models.BatchTaskCreateContent(
            id=self.get_resource_name("batch_task1_"),
            command_line='cmd /c "echo hello world"',
            exit_conditions=exit_conditions,
        )
        try:
            await wrap_result(client.create_task(batch_job.id, task_param))
        except azure.core.exceptions.HttpResponseError as e:
            message = "{}: ".format(e.error.code, e.error.message)
            for v in e.model.values:
                message += "\n{}: {}".format(v.key, v.value)
            raise Exception(message)
        task = await wrap_result(client.get_task(batch_job.id, task_param.id))
        assert isinstance(task, models.BatchTask)
        assert task.exit_conditions is not None
        assert task.exit_conditions.default is not None
        assert task.exit_conditions.default.job_action == models.BatchJobAction.NONE
        assert task.exit_conditions.exit_codes is not None
        assert task.exit_conditions.exit_codes[0].code == 1
        assert task.exit_conditions.exit_codes[0].exit_options.job_action == models.BatchJobAction.TERMINATE

        # Test Create Task with Output Files
        container_url = "https://test.blob.core.windows.net:443/test-container"
        outputs = [
            models.OutputFile(
                file_pattern="../stdout.txt",
                destination=models.OutputFileDestination(
                    container=models.OutputFileBlobContainerDestination(
                        container_url=container_url, path="taskLogs/output.txt"
                    )
                ),
                upload_options=models.OutputFileUploadConfig(
                    upload_condition=models.OutputFileUploadCondition.TASK_COMPLETION
                ),
            ),
            models.OutputFile(
                file_pattern="../stderr.txt",
                destination=models.OutputFileDestination(
                    container=models.OutputFileBlobContainerDestination(
                        container_url=container_url, path="taskLogs/error.txt"
                    )
                ),
                upload_options=models.OutputFileUploadConfig(
                    upload_condition=models.OutputFileUploadCondition.TASK_FAILURE
                ),
            ),
        ]
        task_param = models.BatchTaskCreateContent(
            id=self.get_resource_name("batch_task2_"),
            command_line='cmd /c "echo hello world"',
            output_files=outputs,
        )
        await wrap_result(client.create_task(batch_job.id, task_param))
        task = await wrap_result(client.get_task(batch_job.id, task_param.id))
        assert isinstance(task, models.BatchTask)
        assert len(task.output_files) == 2

        # Test Create Task with Auto User
        auto_user = models.AutoUserSpecification(
            scope=models.AutoUserScope.TASK, elevation_level=models.ElevationLevel.ADMIN
        )
        task_param = models.BatchTaskCreateContent(
            id=self.get_resource_name("batch_task3_"),
            command_line='cmd /c "echo hello world"',
            user_identity=models.UserIdentity(auto_user=auto_user),
        )
        await wrap_result(client.create_task(batch_job.id, task_param))
        task = await wrap_result(client.get_task(batch_job.id, task_param.id))
        assert isinstance(task, models.BatchTask)
        assert task.user_identity.auto_user.scope == models.AutoUserScope.TASK
        assert task.user_identity.auto_user.elevation_level == models.ElevationLevel.ADMIN

        # Test Create Task with Container Settings
        task_param = models.BatchTaskCreateContent(
            id=self.get_resource_name("batch_task5_"),
            command_line='cmd /c "echo hello world"',
            container_settings=models.BatchTaskContainerSettings(
                image_name="windows_container:latest",
                registry=models.ContainerRegistryReference(username="username", password="password"),
            ),
        )
        await wrap_result(client.create_task(batch_job.id, task_param))
        task = await wrap_result(client.get_task(batch_job.id, task_param.id))
        assert isinstance(task, models.BatchTask)
        assert task.container_settings.image_name == "windows_container:latest"
        assert task.container_settings.registry.username == "username"

        # Test Create Task with Run-As-User
        task_param = models.BatchTaskCreateContent(
            id=self.get_resource_name("batch_task6_"),
            command_line='cmd /c "echo hello world"',
            user_identity=models.UserIdentity(username="task-user"),
        )
        await wrap_result(client.create_task(batch_job.id, task_param))
        task = await wrap_result(client.get_task(batch_job.id, task_param.id))
        assert isinstance(task, models.BatchTask)
        assert task.user_identity.username == "task-user"

        # Test Add Task Collection
        tasks = []
        for i in range(7, 10):
            tasks.append(
                models.BatchTaskCreateContent(
                    id=self.get_resource_name("batch_task{}_".format(i)),
                    command_line='cmd /c "echo hello world"',
                )
            )
        result = await wrap_result(client.create_tasks(batch_job.id, task_collection=tasks))
        assert isinstance(result, models.BatchTaskAddCollectionResult)
        assert len(result.value) == 3
        assert result.value[0].status.lower() == models.BatchTaskAddStatus.SUCCESS

        # Test List Tasks
        tasks = list(await wrap_list_result(client.list_tasks(batch_job.id)))
        assert len(tasks) == 8

        # Test Count Tasks
        task_results = await wrap_result(client.get_job_task_counts(batch_job.id))
        assert isinstance(task_results, models.BatchTaskCountsResult)
        assert task_results.task_counts.completed == 0
        assert task_results.task_counts.succeeded == 0

        # Test Terminate Task
        response = await wrap_result(client.terminate_task(batch_job.id, task_param.id))
        assert response is None
        task = await wrap_result(client.get_task(batch_job.id, task_param.id))
        assert task.state == models.BatchTaskState.COMPLETED

        # Test Reactivate Task
        response = await wrap_result(client.reactivate_task(batch_job.id, task_param.id))
        assert response is None
        task = await wrap_result(client.get_task(batch_job.id, task_param.id))
        assert task.state == models.BatchTaskState.ACTIVE

        # Test Update Task
        response = await wrap_result(
            client.replace_task(
                job_id=batch_job.id,
                task_id=task_param.id,
                task=models.BatchTask(constraints=models.BatchTaskConstraints(max_task_retry_count=1)),
            )
        )
        assert response is None

        # Test Get Subtasks
        # TODO: Test with actual subtasks
        subtasks = list(await wrap_list_result(client.list_sub_tasks(batch_job.id, task_param.id)))
        assert isinstance(subtasks, Iterable)

        # Test Delete Task
        response = await wrap_result(client.delete_task(batch_job.id, task_param.id))
        assert response is None

        # Test Bulk Add Task Failure
        task_id = "mytask"
        tasks_to_add = []
        resource_files = []
        for i in range(10000):
            resource_file = models.ResourceFile(
                http_url="https://mystorageaccount.blob.core.windows.net/files/resourceFile{}".format(str(i)),
                file_path="resourceFile{}".format(str(i)),
            )
            resource_files.append(resource_file)
        task = models.BatchTaskCreateContent(id=task_id, command_line="sleep 1", resource_files=resource_files)
        tasks_to_add.append(task)
        await self.assertCreateTasksError(
            "RequestBodyTooLarge",
            client.create_tasks,
            batch_job.id,
            tasks_to_add,
        )
        await self.assertCreateTasksError(
            "RequestBodyTooLarge",
            client.create_tasks,
            batch_job.id,
            tasks_to_add,
            concurrencies=3,
        )

        # Test Bulk Add Task Success
        task_id = "mytask"
        tasks_to_add = []
        resource_files = []
        for i in range(100):
            resource_file = models.ResourceFile(
                http_url="https://mystorageaccount.blob.core.windows.net/files/resourceFile" + str(i),
                file_path="resourceFile" + str(i),
            )
            resource_files.append(resource_file)
        for i in range(733):
            task = models.BatchTaskCreateContent(
                id=task_id + str(i),
                command_line="sleep 1",
                resource_files=resource_files,
            )
            tasks_to_add.append(task)
        result = await wrap_result(client.create_tasks(batch_job.id, tasks_to_add))
        assert isinstance(result, models.BatchTaskAddCollectionResult)
        assert len(result.value) == 733
        assert result.value[0].status.lower() == models.BatchTaskAddStatus.SUCCESS
        assert all(t.status.lower() == models.BatchTaskAddStatus.SUCCESS for t in result.value)

    @CachedResourceGroupPreparer(location=AZURE_LOCATION)
    @AccountPreparer(location=AZURE_LOCATION, batch_environment=BATCH_ENVIRONMENT)
    @pytest.mark.parametrize("BatchClient", [SyncBatchClient, AsyncBatchClient], ids=["sync", "async"])
    @client_setup
    @recorded_by_proxy_async
    async def test_batch_jobs(self, client: BatchClient, **kwargs):
        # Test Create Job
        auto_pool = models.BatchAutoPoolSpecification(
            pool_lifetime_option=models.BatchPoolLifetimeOption.JOB,
            pool=models.BatchPoolSpecification(
                vm_size=DEFAULT_VM_SIZE,
                virtual_machine_configuration=models.VirtualMachineConfiguration(
                    image_reference=models.ImageReference(
                        publisher="Canonical",
                        offer="UbuntuServer",
                        sku="18.04-LTS",
                        version="latest",
                    ),
                    node_agent_sku_id="batch.node.ubuntu 18.04",
                ),
            ),
        )
        job_prep = models.BatchJobPreparationTask(command_line='cmd /c "echo hello world"')
        job_release = models.BatchJobReleaseTask(command_line='cmd /c "echo goodbye world"')
        job_param = models.BatchJobCreateContent(
            id=self.get_resource_name("batch_job1_"),
            pool_info=models.BatchPoolInfo(auto_pool_specification=auto_pool),
            job_preparation_task=job_prep,
            job_release_task=job_release,
        )

        now = datetime.datetime.now(datetime.timezone.utc)

        response = await wrap_result(client.create_job(job=job_param, ocpdate=now))
        assert response is None

        # Test Update Job
        constraints = models.BatchJobConstraints(max_task_retry_count=3)
        options = models.BatchJob(
            priority=500,
            constraints=constraints,
            pool_info=models.BatchPoolInfo(auto_pool_specification=auto_pool),
        )
        response = await wrap_result(client.replace_job(job_param.id, options))
        assert response is None

        # Test Patch Job
        options = models.BatchJobUpdateContent(priority=900)
        response = await wrap_result(client.update_job(job_param.id, options))
        assert response is None

        job = await wrap_result(client.get_job(job_param.id))
        assert isinstance(job, models.BatchJob)
        assert job.id == job_param.id
        assert job.constraints.max_task_retry_count == 3
        assert job.priority == 900

        # Test Create Job with Auto Complete
        job_auto_param = models.BatchJobCreateContent(
            id=self.get_resource_name("batch_job2_"),
            on_all_tasks_complete=models.OnAllBatchTasksComplete.TERMINATE_JOB,
            on_task_failure=models.OnBatchTaskFailure.PERFORM_EXIT_OPTIONS_JOB_ACTION,
            pool_info=models.BatchPoolInfo(auto_pool_specification=auto_pool),
        )
        response = await wrap_result(client.create_job(job_auto_param))
        assert response is None
        job = await wrap_result(client.get_job(job_auto_param.id))
        assert isinstance(job, models.BatchJob)
        assert job.on_all_tasks_complete == models.OnAllBatchTasksComplete.TERMINATE_JOB
        assert job.on_task_failure == models.OnBatchTaskFailure.PERFORM_EXIT_OPTIONS_JOB_ACTION

        # Test List Jobs
        jobs = await wrap_list_result(client.list_jobs())
        assert isinstance(jobs, Iterable)
        assert len(list(jobs)) == 2

        # Test Disable Job
        response = await wrap_result(
            client.disable_job(
                job_id=job_param.id,
                content=models.BatchJobDisableContent(disable_tasks="requeue"),
            )
        )
        assert response is None

        # Test Enable Job
        response = await wrap_result(client.enable_job(job_param.id))
        assert response is None

        # Prep and release task status
        task_status = await wrap_list_result(client.list_job_preparation_and_release_task_status(job_param.id))
        assert isinstance(task_status, Iterable)
        assert list(task_status) == []

        # Test Terminate Job
        response = await wrap_result(client.terminate_job(job_param.id))
        assert response is None

        # Test Delete Job
        response = await wrap_result(client.delete_job(job_auto_param.id))
        assert response is None
