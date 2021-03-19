#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import datetime

import msrest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError, ResourceExistsError
from azure.servicebus.aio.management import ServiceBusAdministrationClient
from azure.servicebus.management import QueueProperties
from azure.servicebus.aio._base_handler_async import ServiceBusSharedKeyCredential
from azure.servicebus._common.utils import utc_now

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusNamespacePreparer
)

from mgmt_test_utilities_async import (
    AsyncMgmtQueueListTestHelper,
    AsyncMgmtQueueListRuntimeInfoTestHelper,
    run_test_async_mgmt_list_with_parameters,
    run_test_async_mgmt_list_with_negative_parameters,
    async_pageable_to_list,
    clear_queues
)


class ServiceBusAdministrationClientQueueAsyncTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_basic(self, servicebus_namespace_connection_string,
                                                        servicebus_namespace, servicebus_namespace_key_name,
                                                        servicebus_namespace_primary_key):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0
        await mgmt_service.create_queue("test_queue")
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 1 and queues[0].name == "test_queue"
        await mgmt_service.delete_queue("test_queue")
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0

        fully_qualified_namespace = servicebus_namespace.name + '.servicebus.windows.net'
        mgmt_service = ServiceBusAdministrationClient(
            fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        )
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0
        await mgmt_service.create_queue("test_queue")
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 1 and queues[0].name == "test_queue"
        await mgmt_service.delete_queue("test_queue")
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_with_special_chars(self, servicebus_namespace_connection_string):
        # Queue names can contain letters, numbers, periods (.), hyphens (-), underscores (_), and slashes (/), up to 260 characters. Queue names are also case-insensitive.
        queue_name = 'txt/.-_123'
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0
        await mgmt_service.create_queue(queue_name)
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 1 and queues[0].name == queue_name
        await mgmt_service.delete_queue(queue_name)
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_with_parameters(self, servicebus_namespace_connection_string):
        pytest.skip("start_idx and max_count are currently removed, they might come back in the future.")
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await run_test_async_mgmt_list_with_parameters(AsyncMgmtQueueListTestHelper(mgmt_service))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_with_negative_credential(self, servicebus_namespace, servicebus_namespace_key_name,
                                                        servicebus_namespace_primary_key):
        # invalid_conn_str = 'Endpoint=sb://invalid.servicebus.windows.net/;SharedAccessKeyName=invalid;SharedAccessKey=invalid'
        # mgmt_service = ServiceBusAdministrationClient.from_connection_string(invalid_conn_str)
        # with pytest.raises(ServiceRequestError):
        #     await async_pageable_to_list(mgmt_service.list_queues())

        invalid_conn_str = 'Endpoint=sb://{}.servicebus.windows.net/;SharedAccessKeyName=invalid;SharedAccessKey=invalid'.format(servicebus_namespace.name)
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(invalid_conn_str)
        with pytest.raises(HttpResponseError):
            await async_pageable_to_list(mgmt_service.list_queues())

        # fully_qualified_namespace = 'invalid.servicebus.windows.net'
        # mgmt_service = ServiceBusAdministrationClient(
        #     fully_qualified_namespace,
        #     credential=ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        # )
        # with pytest.raises(ServiceRequestError):
        #     await async_pageable_to_list(mgmt_service.list_queues())

        fully_qualified_namespace = servicebus_namespace.name + '.servicebus.windows.net'
        mgmt_service = ServiceBusAdministrationClient(
            fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential("invalid", "invalid")
        )
        with pytest.raises(HttpResponseError):
            await async_pageable_to_list(mgmt_service.list_queues())

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_with_negative_parameters(self, servicebus_namespace_connection_string):
        pytest.skip("start_idx and max_count are currently removed, they might come back in the future.")
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await run_test_async_mgmt_list_with_negative_parameters(AsyncMgmtQueueListTestHelper(mgmt_service))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_delete_basic(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        await mgmt_service.create_queue("test_queue")
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 1

        await mgmt_service.create_queue('txt/.-_123')
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 2

        await mgmt_service.delete_queue("test_queue")

        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 1 and queues[0].name == 'txt/.-_123'

        await mgmt_service.delete_queue('txt/.-_123')

        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_delete_one_and_check_not_existing(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        for i in range(10):
            await mgmt_service.create_queue("queue{}".format(i))

        random_delete_idx = 0
        to_delete_queue_name = "queue{}".format(random_delete_idx)
        await mgmt_service.delete_queue(to_delete_queue_name)
        queue_names = [queue.name for queue in (await async_pageable_to_list(mgmt_service.list_queues()))]
        assert len(queue_names) == 9 and to_delete_queue_name not in queue_names

        for name in queue_names:
            await mgmt_service.delete_queue(name)

        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_delete_negtive(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        await mgmt_service.create_queue("test_queue")
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 1

        await mgmt_service.delete_queue("test_queue")
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        assert len(queues) == 0

        with pytest.raises(ResourceNotFoundError):
            await mgmt_service.delete_queue("test_queue")

        with pytest.raises(ResourceNotFoundError):
            await mgmt_service.delete_queue("non_existing_queue")

        with pytest.raises(ValueError):
            await mgmt_service.delete_queue("")

        with pytest.raises(TypeError):
            await mgmt_service.delete_queue(queue_name=None)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_create_by_name(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queue_name = "eidk"
        created_at_utc = utc_now()
        await mgmt_service.create_queue(queue_name)
        try:
            queue = await mgmt_service.get_queue(queue_name)
            assert queue.name == queue_name
            assert queue.availability_status == 'Available'
            assert queue.status == 'Active'
            # assert created_at_utc < queue.created_at_utc < utc_now() + datetime.timedelta(minutes=10)
        finally:
            await mgmt_service.delete_queue(queue_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_create_with_invalid_name(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)

        with pytest.raises(msrest.exceptions.ValidationError):
            await mgmt_service.create_queue(Exception())

        with pytest.raises(msrest.exceptions.ValidationError):
            await mgmt_service.create_queue('')


    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_create_with_queue_description(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queue_name = "dkldf"
        await mgmt_service.create_queue(queue_name,
                                                    auto_delete_on_idle=datetime.timedelta(minutes=10),
                                                    dead_lettering_on_message_expiration=True, 
                                                    default_message_time_to_live=datetime.timedelta(minutes=11),
                                                    duplicate_detection_history_time_window=datetime.timedelta(minutes=12),
                                                    enable_batched_operations=True,
                                                    enable_express=True,
                                                    enable_partitioning=True,
                                                    lock_duration=datetime.timedelta(seconds=13),
                                                    max_delivery_count=14,
                                                    max_size_in_megabytes=3072,
                                                    #requires_duplicate_detection=True, 
                                                    requires_session=True
                                                    )
        try:
            queue = await mgmt_service.get_queue(queue_name)
            assert queue.name == queue_name
            assert queue.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert queue.dead_lettering_on_message_expiration == True
            assert queue.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert queue.duplicate_detection_history_time_window == datetime.timedelta(minutes=12)
            assert queue.enable_batched_operations == True
            assert queue.enable_express == True
            assert queue.enable_partitioning == True
            assert queue.lock_duration == datetime.timedelta(seconds=13)
            assert queue.max_delivery_count == 14
            assert queue.max_size_in_megabytes % 3072 == 0
            #assert queue.requires_duplicate_detection == True
            assert queue.requires_session == True
        finally:
            await mgmt_service.delete_queue(queue_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_create_duplicate(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queue_name = "eriodk"
        await mgmt_service.create_queue(queue_name)
        try:
            with pytest.raises(ResourceExistsError):
                await mgmt_service.create_queue(queue_name)
        finally:
            await mgmt_service.delete_queue(queue_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_update_success(self, servicebus_namespace_connection_string, servicebus_namespace, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queue_name = "ewuidfj"
        queue_description = await mgmt_service.create_queue(queue_name)

        try:
            # Try updating one setting.
            queue_description.lock_duration = datetime.timedelta(minutes=2)
            await mgmt_service.update_queue(queue_description)
            queue_description = await mgmt_service.get_queue(queue_name)
            assert queue_description.lock_duration == datetime.timedelta(minutes=2)

            # Now try updating all settings.
            queue_description.auto_delete_on_idle = datetime.timedelta(minutes=10)
            queue_description.dead_lettering_on_message_expiration = True
            queue_description.default_message_time_to_live = datetime.timedelta(minutes=11)
            queue_description.duplicate_detection_history_time_window = datetime.timedelta(minutes=12)
            queue_description.enable_batched_operations = True
            queue_description.enable_express = True
            #queue_description.enable_partitioning = True # Cannot be changed after creation
            queue_description.lock_duration = datetime.timedelta(seconds=13)
            queue_description.max_delivery_count = 14
            queue_description.max_size_in_megabytes = 3072
            queue_description.forward_to = "sb://{}.servicebus.windows.net/{}".format(servicebus_namespace.name, queue_name)
            queue_description.forward_dead_lettered_messages_to = "sb://{}.servicebus.windows.net/{}".format(servicebus_namespace.name, queue_name)
            #queue_description.requires_duplicate_detection = True # Read only
            #queue_description.requires_session = True # Cannot be changed after creation

            await mgmt_service.update_queue(queue_description)
            queue_description = await mgmt_service.get_queue(queue_name)

            assert queue_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert queue_description.dead_lettering_on_message_expiration == True
            assert queue_description.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert queue_description.duplicate_detection_history_time_window == datetime.timedelta(minutes=12)
            assert queue_description.enable_batched_operations == True
            assert queue_description.enable_express == True
            #assert queue_description.enable_partitioning == True
            assert queue_description.lock_duration == datetime.timedelta(seconds=13)
            assert queue_description.max_delivery_count == 14
            assert queue_description.max_size_in_megabytes == 3072
            assert queue_description.forward_to.endswith(".servicebus.windows.net/{}".format(queue_name))
            # Note: We endswith to avoid the fact that the servicebus_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert queue_description.forward_dead_lettered_messages_to.endswith(".servicebus.windows.net/{}".format(queue_name))
            #assert queue_description.requires_duplicate_detection == True
            #assert queue_description.requires_session == True
        finally:
            await mgmt_service.delete_queue(queue_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_update_invalid(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queue_name = "vbmfm"
        queue_description = await mgmt_service.create_queue(queue_name)
        try:
            # handle a null update properly.
            with pytest.raises(TypeError):
                await mgmt_service.update_queue(None)

            # handle an invalid type update properly.
            with pytest.raises(TypeError):
                await mgmt_service.update_queue(Exception("test"))

            # change a setting we can't change; should fail.
            queue_description.requires_session = True
            with pytest.raises(HttpResponseError):
                await mgmt_service.update_queue(queue_description)
            queue_description.requires_session = False

            #change the name to a queue that doesn't exist; should fail.
            queue_description.name = "dkfrgx"
            with pytest.raises(HttpResponseError):
                await mgmt_service.update_queue(queue_description)
            queue_description.name = queue_name

            #change the name to a queue with an invalid name exist; should fail.
            queue_description.name = ''
            with pytest.raises(msrest.exceptions.ValidationError):
                await mgmt_service.update_queue(queue_description)
            queue_description.name = queue_name

            #change to a setting with an invalid value; should still fail.
            queue_description.lock_duration = datetime.timedelta(days=25)
            with pytest.raises(HttpResponseError):
                await mgmt_service.update_queue(queue_description)
            queue_description.lock_duration = datetime.timedelta(minutes=5)
        finally:
            await mgmt_service.delete_queue(queue_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_runtime_properties_basic(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queues = await async_pageable_to_list(mgmt_service.list_queues())
        queues_infos = await async_pageable_to_list(mgmt_service.list_queues_runtime_properties())

        assert len(queues) == len(queues_infos) == 0

        await mgmt_service.create_queue("test_queue")

        queues = await async_pageable_to_list(mgmt_service.list_queues())
        queues_infos = await async_pageable_to_list(mgmt_service.list_queues_runtime_properties())

        assert len(queues) == 1 and len(queues_infos) == 1

        assert queues[0].name == queues_infos[0].name == "test_queue"

        info = queues_infos[0]

        assert info.size_in_bytes == 0
        assert info.created_at_utc is not None
        assert info.accessed_at_utc is not None
        assert info.updated_at_utc is not None
        assert info.total_message_count == 0
        assert info.active_message_count == 0
        assert info.dead_letter_message_count == 0
        assert info.transfer_dead_letter_message_count == 0
        assert info.transfer_message_count == 0
        assert info.scheduled_message_count == 0

        await mgmt_service.delete_queue("test_queue")
        queues_infos = await async_pageable_to_list(mgmt_service.list_queues_runtime_properties())
        assert len(queues_infos) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_runtime_properties_with_negative_parameters(self, servicebus_namespace_connection_string):
        pytest.skip("start_idx and max_count are currently removed, they might come back in the future.")
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await run_test_async_mgmt_list_with_negative_parameters(AsyncMgmtQueueListRuntimeInfoTestHelper(mgmt_service))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_list_runtime_properties_with_parameters(self, servicebus_namespace_connection_string):
        pytest.skip("start_idx and max_count are currently removed, they might come back in the future.")
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await run_test_async_mgmt_list_with_parameters(AsyncMgmtQueueListRuntimeInfoTestHelper(mgmt_service))

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_get_runtime_properties_basic(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        await mgmt_service.create_queue("test_queue")
        queue_runtime_properties = await mgmt_service.get_queue_runtime_properties("test_queue")

        assert queue_runtime_properties
        assert queue_runtime_properties.name == "test_queue"
        assert queue_runtime_properties.size_in_bytes == 0
        assert queue_runtime_properties.created_at_utc is not None
        assert queue_runtime_properties.accessed_at_utc is not None
        assert queue_runtime_properties.updated_at_utc is not None
        assert queue_runtime_properties.total_message_count == 0
        assert queue_runtime_properties.active_message_count == 0
        assert queue_runtime_properties.dead_letter_message_count == 0
        assert queue_runtime_properties.transfer_dead_letter_message_count == 0
        assert queue_runtime_properties.transfer_message_count == 0
        assert queue_runtime_properties.scheduled_message_count == 0
        await mgmt_service.delete_queue("test_queue")

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_async_mgmt_queue_get_runtime_properties_negative(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        with pytest.raises(TypeError):
            await mgmt_service.get_queue_runtime_properties(None)

        with pytest.raises(msrest.exceptions.ValidationError):
            await mgmt_service.get_queue_runtime_properties("")

        with pytest.raises(ResourceNotFoundError):
            await mgmt_service.get_queue_runtime_properties("non_existing_queue")

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_mgmt_queue_async_update_dict_success(self, servicebus_namespace_connection_string, servicebus_namespace, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queue_name = "fjruid"
        queue_description = await mgmt_service.create_queue(queue_name)
        queue_description_dict = dict(queue_description)
        try:
            # Try updating one setting.
            queue_description_dict["lock_duration"] = datetime.timedelta(minutes=2)
            await mgmt_service.update_queue(queue_description_dict)

            queue_description = await mgmt_service.get_queue(queue_name)
            assert queue_description.lock_duration == datetime.timedelta(minutes=2)

            # Now try updating all settings.
            queue_description_dict = dict(queue_description)
            queue_description_dict["auto_delete_on_idle"] = datetime.timedelta(minutes=10)
            queue_description_dict["dead_lettering_on_message_expiration"] = True
            queue_description_dict["default_message_time_to_live"] = datetime.timedelta(minutes=11)
            queue_description_dict["duplicate_detection_history_time_window"] = datetime.timedelta(minutes=12)
            queue_description_dict["enable_batched_operations"] = True
            queue_description_dict["enable_express"] = True
            #queue_description_dict["enable_partitioning"] = True # Cannot be changed after creation
            queue_description_dict["lock_duration"] = datetime.timedelta(seconds=13)
            queue_description_dict["max_delivery_count"] = 14
            queue_description_dict["max_size_in_megabytes"] = 3072
            queue_description_dict["forward_to"] = "sb://{}.servicebus.windows.net/{}".format(servicebus_namespace.name, queue_name)
            queue_description_dict["forward_dead_lettered_messages_to"] = "sb://{}.servicebus.windows.net/{}".format(servicebus_namespace.name, queue_name)
            #queue_description_dict["requires_duplicate_detection"] = True # Read only
            #queue_description_dict["requires_session"] = True # Cannot be changed after creation

            await mgmt_service.update_queue(queue_description_dict)
            queue_description = await mgmt_service.get_queue(queue_name)

            assert queue_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert queue_description.dead_lettering_on_message_expiration == True
            assert queue_description.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert queue_description.duplicate_detection_history_time_window == datetime.timedelta(minutes=12)
            assert queue_description.enable_batched_operations == True
            assert queue_description.enable_express == True
            #assert queue_description.enable_partitioning == True
            assert queue_description.lock_duration == datetime.timedelta(seconds=13)
            assert queue_description.max_delivery_count == 14
            assert queue_description.max_size_in_megabytes == 3072
            assert queue_description.forward_to.endswith(".servicebus.windows.net/{}".format(queue_name))
            # Note: We endswith to avoid the fact that the servicebus_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert queue_description.forward_dead_lettered_messages_to.endswith(".servicebus.windows.net/{}".format(queue_name))
            #assert queue_description.requires_duplicate_detection == True
            #assert queue_description.requires_session == True
        finally:
            await mgmt_service.delete_queue(queue_name)
    
    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    async def test_mgmt_queue_async_update_dict_error(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        await clear_queues(mgmt_service)
        queue_name = "fjruid"
        queue_description = await mgmt_service.create_queue(queue_name)
        try:
            # send in queue dict without non-name keyword args
            queue_description_only_name = {"name": queue_name}
            with pytest.raises(TypeError):
                await mgmt_service.update_queue(queue_description_only_name)
        finally:
            await mgmt_service.delete_queue(queue_name)
