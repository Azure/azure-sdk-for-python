#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import random
import logging
import pytest
import uuid
import datetime
import functools

from azure.servicebus.management import ServiceBusManagementClient, QueueDescription
from azure.servicebus._common.utils import utc_now
from utilities import get_logger
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ResourceNotFoundError, ResourceExistsError
from azure.servicebus import ServiceBusSharedKeyCredential

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusNamespacePreparer
)

from mgmt_test_utilities import (
    MgmtQueueListTestHelper,
    MgmtQueueListRuntimeInfoTestHelper,
    run_test_mgmt_list_with_parameters,
    run_test_mgmt_list_with_negative_parameters
)
_logger = get_logger(logging.DEBUG)


class ServiceBusManagementClientQueueTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
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
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
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
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_with_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        run_test_mgmt_list_with_parameters(MgmtQueueListTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
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
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_with_negative_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        run_test_mgmt_list_with_negative_parameters(MgmtQueueListTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
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
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
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
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
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


    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_create_by_name(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        queue_name = str(uuid.uuid4())
        created_at = utc_now()
        mgmt_service.create_queue(queue_name)

        queue = mgmt_service.get_queue(queue_name)
        assert queue.queue_name == queue_name
        assert queue.entity_availability_status == 'Available'
        assert queue.status == 'Active'
        assert created_at < queue.created_at < utc_now() + datetime.timedelta(minutes=10) # TODO: Should be created_at_utc for consistency with dataplane.

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_create_with_invalid_name(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        with pytest.raises(TypeError):
            mgmt_service.create_queue(Exception())

        with pytest.raises(ValueError):
            mgmt_service.create_queue(QueueDescription(queue_name=Exception()))

        with pytest.raises(ValueError):
            mgmt_service.create_queue('')

        with pytest.raises(ValueError):
            mgmt_service.create_queue(QueueDescription(queue_name=''))

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_create_with_queue_description(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        queue_name = str(uuid.uuid4())
        #TODO: Why don't we have an input model (queueOptions? as superclass of QueueDescription?) and output model to not show these params?
        #TODO: This fails with the following: E           msrest.exceptions.DeserializationError: Find several XML 'prefix:DeadLetteringOnMessageExpiration' where it was not expected .tox\whl\lib\site-packages\msrest\serialization.py:1262: DeserializationError
        mgmt_service.create_queue(QueueDescription(queue_name=queue_name,
                                                    auto_delete_on_idle=datetime.timedelta(minutes=10),
                                                    dead_lettering_on_message_expiration=True, 
                                                    default_message_time_to_live=datetime.timedelta(minutes=11),
                                                    duplicate_detection_history_time_window=datetime.timedelta(minutes=12),
                                                    enable_batched_operations=True,
                                                    enable_express=True,
                                                    enable_partitioning=True,
                                                    is_anonymous_accessible=True,
                                                    lock_duration=datetime.timedelta(seconds=13),
                                                    max_delivery_count=14,
                                                    max_size_in_megabytes=3072,
                                                    #requires_duplicate_detection=True, 
                                                    requires_session=True,
                                                    support_ordering=True
                                                    ))

        queue = mgmt_service.get_queue(queue_name)
        assert queue.queue_name == queue_name
        assert queue.auto_delete_on_idle == datetime.timedelta(minutes=10)
        assert queue.dead_lettering_on_message_expiration == True
        assert queue.default_message_time_to_live == datetime.timedelta(minutes=11)
        assert queue.duplicate_detection_history_time_window == datetime.timedelta(minutes=12)
        assert queue.enable_batched_operations == True
        assert queue.enable_express == True
        assert queue.enable_partitioning == True
        assert queue.is_anonymous_accessible == True
        assert queue.lock_duration == datetime.timedelta(seconds=13)
        assert queue.max_delivery_count == 14
        assert queue.max_size_in_megabytes % 3072 == 0  # TODO: In my local test, I don't see a multiple of the input number. To confirm
        #assert queue.requires_duplicate_detection == True
        assert queue.requires_session == True
        assert queue.support_ordering == True

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_create_duplicate(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        queue_name = str(uuid.uuid4())
        mgmt_service.create_queue(queue_name)
        with pytest.raises(ResourceExistsError):
            mgmt_service.create_queue(queue_name)

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_update_success(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        queue_name = str(uuid.uuid4())
        queue_description = mgmt_service.create_queue(queue_name)
        
        # Try updating one setting.
        queue_description.lock_duration = datetime.timedelta(minutes=2)
        queue_description = mgmt_service.update_queue(queue_description)
        assert queue_description.lock_duration == datetime.timedelta(minutes=2)

        # Now try updating all settings.
        queue_description.auto_delete_on_idle = datetime.timedelta(minutes=10)
        queue_description.dead_lettering_on_message_expiration = True
        queue_description.default_message_time_to_live = datetime.timedelta(minutes=11)
        queue_description.duplicate_detection_history_time_window = datetime.timedelta(minutes=12)
        queue_description.enable_batched_operations = True
        queue_description.enable_express = True
        #queue_description.enable_partitioning = True # Cannot be changed after creation
        queue_description.is_anonymous_accessible = True
        queue_description.lock_duration = datetime.timedelta(seconds=13)
        queue_description.max_delivery_count = 14
        queue_description.max_size_in_megabytes = 3072
        #queue_description.requires_duplicate_detection = True # Read only
        #queue_description.requires_session = True # Cannot be changed after creation
        queue_description.support_ordering = True        
        
        queue_description = mgmt_service.update_queue(queue_description)

        assert queue_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
        assert queue_description.dead_lettering_on_message_expiration == True
        assert queue_description.default_message_time_to_live == datetime.timedelta(minutes=11)
        assert queue_description.duplicate_detection_history_time_window == datetime.timedelta(minutes=12)
        assert queue_description.enable_batched_operations == True
        assert queue_description.enable_express == True
        #assert queue_description.enable_partitioning == True
        assert queue_description.is_anonymous_accessible == True
        assert queue_description.lock_duration == datetime.timedelta(seconds=13)
        assert queue_description.max_delivery_count == 14
        assert queue_description.max_size_in_megabytes == 3072
        #assert queue_description.requires_duplicate_detection == True
        #assert queue_description.requires_session == True
        assert queue_description.support_ordering == True   

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_update_invalid(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        queue_name = str(uuid.uuid4())
        queue_description = mgmt_service.create_queue(queue_name)
        
        # handle a null update properly.
        with pytest.raises(TypeError):
            mgmt_service.update_queue(None)

        # handle an invalid type update properly.
        with pytest.raises(TypeError):
            mgmt_service.update_queue(Exception("test"))

        # change a setting we can't change; should fail.
        queue_description.requires_session = True
        with pytest.raises(HttpResponseError):
            mgmt_service.update_queue(queue_description)
        queue_description.requires_session = False

        #change the name to a queue that doesn't exist; should fail.
        queue_description.queue_name = str(uuid.uuid4())
        with pytest.raises(HttpResponseError):
            mgmt_service.update_queue(queue_description)
        queue_description.queue_name = queue_name
    
        #change the name to a queue with an invalid name exist; should fail.
        queue_description.queue_name = ''
        with pytest.raises(ValueError):
            mgmt_service.update_queue(queue_description)
        queue_description.queue_name = queue_name

        #change to a setting with an invalid value; should still fail.
        queue_description.lock_duration = datetime.timedelta(days=25)
        with pytest.raises(HttpResponseError):
            mgmt_service.update_queue(queue_description)
        queue_description.lock_duration = datetime.timedelta(minutes=5)  

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_runtime_info_basic(self, servicebus_namespace_connection_string):
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
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_runtime_info_with_negative_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        run_test_mgmt_list_with_negative_parameters(MgmtQueueListRuntimeInfoTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_list_runtime_info_with_parameters(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        run_test_mgmt_list_with_parameters(MgmtQueueListRuntimeInfoTestHelper(sb_mgmt_client))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_get_runtime_info_basic(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        sb_mgmt_client.create_queue("test_queue")
        queue_runtime_info = sb_mgmt_client.get_queue_runtime_info("test_queue")

        assert queue_runtime_info
        assert queue_runtime_info.queue_name == "test_queue"
        assert queue_runtime_info.size_in_bytes == 0
        assert queue_runtime_info.created_at is not None
        assert queue_runtime_info.accessed_at is not None
        assert queue_runtime_info.updated_at is not None
        assert queue_runtime_info.message_count == 0

        assert queue_runtime_info.message_count_details
        assert queue_runtime_info.message_count_details.active_message_count == 0
        assert queue_runtime_info.message_count_details.dead_letter_message_count == 0
        assert queue_runtime_info.message_count_details.transfer_dead_letter_message_count == 0
        assert queue_runtime_info.message_count_details.transfer_message_count == 0
        assert queue_runtime_info.message_count_details.scheduled_message_count == 0
        sb_mgmt_client.delete_queue("test_queue")

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_get_runtime_info_negative(self, servicebus_namespace_connection_string):
        sb_mgmt_client = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        with pytest.raises(ValueError):
            sb_mgmt_client.get_queue_runtime_info(None)

        with pytest.raises(ValueError):
            sb_mgmt_client.get_queue_runtime_info("")

        with pytest.raises(ResourceNotFoundError):
            sb_mgmt_client.get_queue_runtime_info("non_existing_queue")

