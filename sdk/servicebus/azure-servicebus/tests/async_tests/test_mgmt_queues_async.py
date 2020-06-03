#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.servicebus.management.aio import ServiceBusManagementClient
from azure.servicebus.aio import ServiceBusSharedKeyCredential

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer
)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, CachedServiceBusQueuePreparer, ServiceBusQueuePreparer


class ServiceBusManagementClientQueueAsyncTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_list_queues_by_conn_string(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
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
    async def test_list_queue_by_credential(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key):
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
    async def test_list_queues_with_special_chars(self, servicebus_namespace_connection_string):
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
    async def test_list_queues_with_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        queues = await sb_mgmt_client.list_queues(skip=5, max_count=10)
        assert len(queues) == 0

        for i in range(20):
            await sb_mgmt_client.create_queue("queue{}".format(i))

        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 20

        all_queues = sorted(["queue{}".format(i) for i in range(20)])

        queues = await sb_mgmt_client.list_queues(skip=5, max_count=10)
        correct_set = all_queues[5:15]
        assert len(queues) == 10
        for queue in queues:
            correct_set.remove(queue.queue_name)
        assert len(correct_set) == 0

        correct_set = all_queues[15:20]
        queues = await sb_mgmt_client.list_queues(skip=15, max_count=100)
        assert len(queues) == 5
        for queue in queues:
            correct_set.remove(queue.queue_name)
        assert len(correct_set) == 0

        queues = await sb_mgmt_client.list_queues(max_count=0)
        assert len(queues) == 0

        queues = await sb_mgmt_client.list_queues(skip=0, max_count=0)
        assert len(queues) == 0

        cnt = 20
        for i in range(20):
            await sb_mgmt_client.delete_queue(all_queues[i])
            cnt -= 1
            assert len(await sb_mgmt_client.list_queues()) == cnt

        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_list_queues_with_negative_conn_str(self, servicebus_namespace):
        invalid_conn_str = 'Endpoint=sb://invalid.servicebus.windows.net/;SharedAccessKeyName=invalid;SharedAccessKey=invalid'
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(invalid_conn_str)
        with pytest.raises(ServiceRequestError):
            await sb_mgmt_client.list_queues()

        invalid_conn_str = 'Endpoint=sb://{}.servicebus.windows.net/;SharedAccessKeyName=invalid;SharedAccessKey=invalid'.format(servicebus_namespace.name)
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(invalid_conn_str)
        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues()

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_list_queues_with_negative_credential(self, servicebus_namespace, servicebus_namespace_key_name,
                                                        servicebus_namespace_primary_key):
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
    async def test_list_queues_with_negative_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0

        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues(skip=-1)

        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues(max_count=-1)

        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues(skip=-1, max_count=-1)

        await sb_mgmt_client.create_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == "test_queue"

        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues(skip=-1)

        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues(max_count=-1)

        with pytest.raises(HttpResponseError):
            await sb_mgmt_client.list_queues(skip=-1, max_count=-1)

        await sb_mgmt_client.delete_queue("test_queue")
        queues = await sb_mgmt_client.list_queues()
        assert len(queues) == 0
