#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import pytest
import uuid
import datetime

from azure.servicebus.management import ServiceBusManagementClient, QueueDescription
from azure.servicebus._common.utils import utc_now
from azure.core.exceptions import ResourceExistsError

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, ServiceBusQueuePreparer, CachedServiceBusQueuePreparer
from utilities import get_logger

_logger = get_logger(logging.DEBUG)

class ServiceBusMgmtQueueTests(AzureMgmtTestCase):

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
        assert queue.status == 'Available'
        assert created_at < queue.created_at < utc_now() + datetime.timedelta(minutes=10) # TODO: Should be created_at_utc for consistency with dataplane.

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_create_with_invalid_name(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        with pytest.raises(TypeError):
            mgmt_service.create_queue(Exception())

        with pytest.raises(TypeError):
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
                                                    lock_duration=datetime.timedelta(minutes=13),
                                                    max_delivery_count=14,
                                                    max_size_in_megabytes=15,
                                                    requires_duplicate_detection=True, 
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
        assert queue.lock_duration == datetime.timedelta(minutes=13)
        assert queue.max_delivery_count == 14
        assert queue.max_size_in_megabytes == 15
        assert queue.requires_duplicate_detection == True
        assert queue.requires_session == True
        assert queue.support_ordering == True

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_queue_create_duplicate(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)

        queue_name = str(uuid.uuid4())
        created_at = utc_now()
        mgmt_service.create_queue(queue_name)
        with pytest.raises(ResourceExistsError):
            mgmt_service.create_queue(queue_name)

