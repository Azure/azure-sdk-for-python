#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import random
import functools

from azure.core.exceptions import HttpResponseError, ServiceRequestError, ResourceNotFoundError
from azure.servicebus.management import ServiceBusManagementClient
from azure.servicebus import ServiceBusSharedKeyCredential

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer
)

from utilities import (
    MgmtQueueListTestHelper,
    MgmtQueueListRuntimeInfoTestHelper,
    run_test_mgmt_list_with_parameters,
    run_test_mgmt_list_with_negative_parameters
)


class ServiceBusManagementClientQueueTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_basic(self, servicebus_namespace_connection_string, servicebus_namespace,
                                    servicebus_namespace_key_name, servicebus_namespace_primary_key):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0
        sb_mgmt_client.create_queue("test_queue")
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == "test_queue"
        sb_mgmt_client.delete_queue("test_queue")
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0

        fully_qualified_namespace = servicebus_namespace.name + '.servicebus.windows.net'
        sb_mgmt_client = ServiceBusManagementClient(
            fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        )
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0
        sb_mgmt_client.create_queue("test_queue")
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == "test_queue"
        sb_mgmt_client.delete_queue("test_queue")
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_with_special_chars(self, servicebus_namespace_connection_string):
        # Queue names can contain letters, numbers, periods (.), hyphens (-), underscores (_), and slashes (/), up to 260 characters. Queue names are also case-insensitive.
        queue_name = 'txt/.-_123'
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0
        sb_mgmt_client.create_queue(queue_name)
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == queue_name
        sb_mgmt_client.delete_queue(queue_name)
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_with_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        run_test_mgmt_list_with_parameters(MgmtQueueListTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_with_negative_credential(self, servicebus_namespace, servicebus_namespace_key_name,
                                                             servicebus_namespace_primary_key):
        invalid_conn_str = 'Endpoint=sb://invalid.servicebus.windows.net/;SharedAccessKeyName=invalid;SharedAccessKey=invalid'
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(invalid_conn_str)
        with pytest.raises(ServiceRequestError):
            sb_mgmt_client.list_queues()

        invalid_conn_str = 'Endpoint=sb://{}.servicebus.windows.net/;SharedAccessKeyName=invalid;SharedAccessKey=invalid'.format(servicebus_namespace.name)
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(invalid_conn_str)
        with pytest.raises(HttpResponseError):
            sb_mgmt_client.list_queues()

        fully_qualified_namespace = 'invalid.servicebus.windows.net'
        sb_mgmt_client = ServiceBusManagementClient(
            fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        )
        with pytest.raises(ServiceRequestError):
            sb_mgmt_client.list_queues()

        fully_qualified_namespace = servicebus_namespace.name + '.servicebus.windows.net'
        sb_mgmt_client = ServiceBusManagementClient(
            fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential("invalid", "invalid")
        )
        with pytest.raises(HttpResponseError):
            sb_mgmt_client.list_queues()

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_with_negative_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        run_test_mgmt_list_with_negative_parameters(MgmtQueueListTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_delete_basic(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        sb_mgmt_client.create_queue("test_queue")
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 1

        sb_mgmt_client.create_queue('txt/.-_123')
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 2

        sb_mgmt_client.delete_queue("test_queue")

        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 1 and queues[0].queue_name == 'txt/.-_123'

        sb_mgmt_client.delete_queue('txt/.-_123')

        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_delete_one_and_check_not_existing(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        for i in range(10):
            sb_mgmt_client.create_queue("queue{}".format(i))

        random_delete_idx = random.randint(0, 9)
        to_delete_queue_name = "queue{}".format(random_delete_idx)
        sb_mgmt_client.delete_queue(to_delete_queue_name)
        queue_names = [queue.queue_name for queue in sb_mgmt_client.list_queues()]
        assert len(queue_names) == 9 and to_delete_queue_name not in queue_names

        for name in queue_names:
            sb_mgmt_client.delete_queue(name)

        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_delete_negtive(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        sb_mgmt_client.create_queue("test_queue")
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 1

        sb_mgmt_client.delete_queue("test_queue")
        queues = sb_mgmt_client.list_queues()
        assert len(queues) == 0

        with pytest.raises(ResourceNotFoundError):
            sb_mgmt_client.delete_queue("test_queue")

        with pytest.raises(ResourceNotFoundError):
            sb_mgmt_client.delete_queue("non_existing_queue")

        with pytest.raises(ValueError):
            sb_mgmt_client.delete_queue("")

        with pytest.raises(ValueError):
            sb_mgmt_client.delete_queue(queue_name=None)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_runtime_info_basic(self, servicebus_namespace_connection_string):
        pytest.skip("pending swagger fix for message_count_details")
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        queues = sb_mgmt_client.list_queues()
        queues_infos = sb_mgmt_client.list_queues_runtime_info()

        assert len(queues) == len(queues_infos) == 0

        sb_mgmt_client.create_queue("test_queue")

        queues = sb_mgmt_client.list_queues()
        queues_infos = sb_mgmt_client.list_queues_runtime_info()

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

        sb_mgmt_client.delete_queue("test_queue")
        queues_infos = sb_mgmt_client.list_queues_runtime_info()
        assert len(queues_infos) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_runtime_info_with_negative_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        run_test_mgmt_list_with_negative_parameters(MgmtQueueListRuntimeInfoTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_runtime_info_with_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        run_test_mgmt_list_with_parameters(MgmtQueueListRuntimeInfoTestHelper(sb_mgmt_client))
