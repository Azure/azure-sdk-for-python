#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import random

from azure.core.exceptions import HttpResponseError, ServiceRequestError, ResourceNotFoundError
from azure.servicebus.management.aio import ServiceBusManagementClient
from azure.servicebus.aio import ServiceBusSharedKeyCredential

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer
)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, CachedServiceBusQueuePreparer, ServiceBusQueuePreparer

from utilities import (
    AsyncMgmtQueueListTestHelper,
    AsyncMgmtQueueListRuntimeInfoTestHelper,
    run_test_async_mgmt_list_with_parameters,
    run_test_async_mgmt_list_with_negative_parameters
)

class ServiceBusManagementClientQueueAsyncTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_basic(self, servicebus_namespace_connection_string,
                                                        servicebus_namespace, servicebus_namespace_key_name,
                                                        servicebus_namespace_primary_key):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0
        await sb_mgmt_client.create_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == "test_queue"
        await sb_mgmt_client.delete_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0

        fully_qualified_namespace = servicebus_namespace.name + '.servicebus.windows.net'
        sb_mgmt_client = ServiceBusManagementClient(
            fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        )
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0
        await sb_mgmt_client.create_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == "test_queue"
        await sb_mgmt_client.delete_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_with_special_chars(self, servicebus_namespace_connection_string):
        # Queue names can contain letters, numbers, periods (.), hyphens (-), underscores (_), and slashes (/), up to 260 characters. Queue names are also case-insensitive.
        queue_name = 'txt/.-_123'
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0
        await sb_mgmt_client.create_queue(queue_name)
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == queue_name
        await sb_mgmt_client.delete_queue(queue_name)
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_with_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        await run_test_async_mgmt_list_with_parameters(AsyncMgmtQueueListTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_with_negative_credential(self, servicebus_namespace, servicebus_namespace_key_name,
                                                        servicebus_namespace_primary_key):
        invalid_conn_str = 'Endpoint=sb://invalid.servicebus.windows.net/;SharedAccessKeyName=invalid;SharedAccessKey=invalid'
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(invalid_conn_str)
        with pytest.raises(ServiceRequestError):
            await sb_mgmt_client.list_queues()

        invalid_conn_str = 'Endpoint=sb://{}.servicebus.windows.net/;SharedAccessKeyName=invalid;SharedAccessKey=invalid'.format(servicebus_namespace.name)
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(invalid_conn_str)
        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues()

        fully_qualified_namespace = 'invalid.servicebus.windows.net'
        sb_mgmt_client = ServiceBusManagementClient(
            fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        )
        with pytest.raises(ServiceRequestError):
            await sb_mgmt_client.list_queues()

        fully_qualified_namespace = servicebus_namespace.name + '.servicebus.windows.net'
        sb_mgmt_client = ServiceBusManagementClient(
            fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential("invalid", "invalid")
        )
        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues()

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_with_negative_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        await run_test_async_mgmt_list_with_negative_parameters(AsyncMgmtQueueListTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_delete_basic(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        await sb_mgmt_client.create_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 1

        await sb_mgmt_client.create_queue('txt/.-_123')
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 2

        await sb_mgmt_client.delete_queue("test_queue")

        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == 'txt/.-_123'

        await sb_mgmt_client.delete_queue('txt/.-_123')

        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_delete_one_and_check_not_existing(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        for i in range(10):
            await sb_mgmt_client.create_queue("queue{}".format(i))

        random_delete_idx = random.randint(0, 9)
        to_delete_queue_name = "queue{}".format(random_delete_idx)
        await sb_mgmt_client.delete_queue(to_delete_queue_name)
        queue_names = [queue.queue_name for queue in (await sb_mgmt_client.list_queues())]
        assert len(queue_names) == 9 and to_delete_queue_name not in queue_names

        for name in queue_names:
            await sb_mgmt_client.delete_queue(name)

        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_delete_negtive(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        await sb_mgmt_client.create_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 1

        await sb_mgmt_client.delete_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0

        with pytest.raises(ResourceNotFoundError):
            await sb_mgmt_client.delete_queue("test_queue")

        with pytest.raises(ResourceNotFoundError):
            await sb_mgmt_client.delete_queue("non_existing_queue")

        with pytest.raises(ValueError):
            await sb_mgmt_client.delete_queue("")

        with pytest.raises(ValueError):
            await sb_mgmt_client.delete_queue(queue_name=None)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_runtime_info_basic(self, servicebus_namespace_connection_string):
        pytest.skip("pending swagger fix for message_count_details")
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        queues = await sb_mgmt_client.list_queues()
        queues_infos = await sb_mgmt_client.list_queues_runtime_info()

        assert len(queues) == len(queues_infos) == 0

        await sb_mgmt_client.create_queue("test_queue")

        queues = await sb_mgmt_client.list_queues()
        queues_infos = await sb_mgmt_client.list_queues_runtime_info()

        assert len(queues) == 1 and len(queues_infos) == 1

        assert queues[0].queue_name == queues_infos[0].queue_name == "test_queue"
        assert queues_infos[0].created_at and queues_infos[0].created_at == queues[0].created_at

        info = queues_infos[0]

        assert info.size_in_bytes == 0
        assert info.accessed_at is not None
        assert info.updated_at is not None
        assert info.message_count == 0

        assert info.message_count_details
        assert info.message_count_details.active_message_count == 0
        assert info.message_count_details.dead_letter_message_count == 0
        assert info.message_count_details.transfer_dead_letter_message_count == 0
        assert info.message_count_details.transfer_message_count == 0
        assert info.message_count_details.scheduled_message_count == 0

        await sb_mgmt_client.delete_queue("test_queue")
        queues_infos = await sb_mgmt_client.list_queues_runtime_info()
        assert len(queues_infos) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_runtime_info_with_negative_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        await run_test_async_mgmt_list_with_negative_parameters(AsyncMgmtQueueListRuntimeInfoTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_runtime_info_with_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        await run_test_async_mgmt_list_with_parameters(AsyncMgmtQueueListRuntimeInfoTestHelper(sb_mgmt_client))
