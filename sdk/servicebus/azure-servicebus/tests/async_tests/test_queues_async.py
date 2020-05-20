#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

from azure.servicebus.aio import (
    ServiceBusClient,
    QueueClient,
    Message,
    BatchMessage,
    DeferredMessage,
    AutoLockRenew)
from azure.servicebus.common.message import PeekMessage
from azure.servicebus.common.constants import ReceiveSettleMode
from azure.servicebus.common.errors import (
    ServiceBusError,
    MessageLockExpired,
    InvalidHandlerState,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSendFailed,
    MessageSettleFailed)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, CachedServiceBusQueuePreparer, ServiceBusQueuePreparer


def get_logger(level):
    azure_logger = logging.getLogger("azure")
    if not azure_logger.handlers:
        azure_logger.setLevel(level)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
        azure_logger.addHandler(handler)

    uamqp_logger = logging.getLogger("uamqp")
    if not uamqp_logger.handlers:
        uamqp_logger.setLevel(logging.INFO)
        uamqp_logger.addHandler(handler)
    return azure_logger

_logger = get_logger(logging.DEBUG)


def print_message(message):
    _logger.info("Receiving: {}".format(message))
    _logger.debug("Time to live: {}".format(message.time_to_live))
    _logger.debug("Sequence number: {}".format(message.sequence_number))
    _logger.debug("Enqueue Sequence number: {}".format(message.enqueue_sequence_number))
    _logger.debug("Partition ID: {}".format(message.partition_id))
    _logger.debug("Partition Key: {}".format(message.partition_key))
    _logger.debug("User Properties: {}".format(message.user_properties))
    _logger.debug("Annotations: {}".format(message.annotations))
    _logger.debug("Delivery count: {}".format(message.header.delivery_count))
    try:
        _logger.debug("Locked until: {}".format(message.locked_until))
        _logger.debug("Lock Token: {}".format(message.lock_token))
    except TypeError:
        pass
    _logger.debug("Enqueued time: {}".format(message.enqueued_time))


class ServiceBusQueueTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_conn_str_receive_handler_peeklock(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)
        queue_client.get_properties()

        async with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("Handler message no. {}".format(i))
                message.enqueue_sequence_number = i
                await sender.send(message)

        with pytest.raises(ValueError):
            queue_client.get_receiver(session="test", idle_timeout=5)

        receiver = queue_client.get_receiver(idle_timeout=5)
        count = 0
        async for message in receiver:
            print_message(message)
            count += 1
            await message.complete()

        assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_github_issue_7079_async(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)
        queue = sb_client.get_queue(servicebus_queue.name)
    
        async with queue.get_sender() as sender:
            for i in range(5):
                await sender.send(Message("Message {}".format(i)))
        messages = queue.get_receiver(mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
        batch = await messages.fetch_next()
        count = len(batch)
        await messages.reconnect()
        async for message in messages:
           _logger.debug(message)
           count += 1
        assert count == 5
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_github_issue_6178_async(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)
        queue = sb_client.get_queue(servicebus_queue.name)
    
        for i in range(3):
            await queue.send(Message("Message {}".format(i)))
    
        messages = queue.get_receiver(idle_timeout=60)
        async for message in messages:
            _logger.debug(message)
            _logger.debug(message.sequence_number)
            _logger.debug(message.enqueued_time)
            _logger.debug(message.expired)
            await message.complete()
            await asyncio.sleep(40)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)
        queue_client.get_properties()

        async with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("Handler message no. {}".format(i))
                message.enqueue_sequence_number = i
                await sender.send(message)

        messages = []
        receiver = queue_client.get_receiver(mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
        async for message in receiver:
            messages.append(message)
            with pytest.raises(MessageAlreadySettled):
                await message.complete()

        assert not receiver.running
        assert len(messages) == 10
        time.sleep(30)

        messages = []
        receiver = queue_client.get_receiver(mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
        async for message in receiver:
            messages.append(message)
        assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_conn_str_receive_handler_with_stop(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)

        async with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("Stop message no. {}".format(i))
                await sender.send(message)

        messages = []
        receiver = queue_client.get_receiver(idle_timeout=5)
        async for message in receiver:
            messages.append(message)
            await message.complete()
            if len(messages) >= 5:
                break

        assert receiver.running
        assert len(messages) == 5

        async with receiver:
            async for message in receiver:
                messages.append(message)
                await message.complete()
                if len(messages) >= 5:
                    break

        assert not receiver.running
        assert len(messages) == 6

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_simple(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

            async with queue_client.get_sender() as sender:
                for i in range(10):
                    message = Message("Iter message no. {}".format(i))
                    await sender.send(message)

            count = 0
            async for message in receiver:
                print_message(message)
                await message.complete()
                with pytest.raises(MessageAlreadySettled):
                    await message.complete()
                with pytest.raises(MessageAlreadySettled):
                    await message.renew_lock()
                count += 1

            with pytest.raises(InvalidHandlerState):
                await receiver.__anext__()

        assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_conn_str_client_iter_messages_with_abandon(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string, debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

            async with queue_client.get_sender() as sender:
                for i in range(10):
                    message = Message("Abandoned message no. {}".format(i))
                    await sender.send(message)

            count = 0
            async for message in receiver:
                print_message(message)
                if not message.header.delivery_count:
                    count += 1
                    await message.abandon()
                else:
                    assert message.header.delivery_count == 1
                    await message.complete()

        assert count == 10

        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            count = 0
            async for message in receiver:
                print_message(message)
                await message.complete()
                count += 1
        assert count == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_defer(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

            async with queue_client.get_sender() as sender:
                for i in range(10):
                    message = Message("Deferred message no. {}".format(i))
                    await sender.send(message)

            count = 0
            async for message in receiver:
                deferred_messages.append(message.sequence_number)
                print_message(message)
                count += 1
                await message.defer()

        assert count == 10
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            count = 0
            async for message in receiver:
                print_message(message)
                await message.complete()
                count += 1
        assert count == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

            async with queue_client.get_sender() as sender:
                for i in range(10):
                    message = Message("Deferred message no. {}".format(i))
                    await sender.send(message)

            count = 0
            async for message in receiver:
                deferred_messages.append(message.sequence_number)
                print_message(message)
                count += 1
                await message.defer()

        assert count == 10

        deferred = await queue_client.receive_deferred_messages(deferred_messages, mode=ReceiveSettleMode.PeekLock)
        assert len(deferred) == 10
        for message in deferred:
            assert isinstance(message, DeferredMessage)
            with pytest.raises(ValueError):
                await message.complete()
        with pytest.raises(ValueError):
            await queue_client.settle_deferred_messages('foo', deferred)

        await queue_client.settle_deferred_messages('completed', deferred)
        with pytest.raises(ServiceBusError):
            await queue_client.receive_deferred_messages(deferred_messages)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
        results = await queue_client.send(messages)
        assert all(result[0] for result in results)

        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            count = 0
            async for message in receiver:
                deferred_messages.append(message.sequence_number)
                print_message(message)
                count += 1
                await message.defer()
        assert count == 10

        async with queue_client.get_receiver(idle_timeout=5) as session:
            deferred = await session.receive_deferred_messages(deferred_messages)
            assert len(deferred) == 10
            for message in deferred:
                assert isinstance(message, DeferredMessage)
                assert message.lock_token
                assert message.locked_until
                assert message._receiver
                await message.renew_lock()
                await message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
        results = await queue_client.send(messages)
        assert all(result[0] for result in results)

        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            count = 0
            async for message in receiver:
                deferred_messages.append(message.sequence_number)
                print_message(message)
                count += 1
                await message.defer()

        assert count == 10

        async with queue_client.get_receiver(idle_timeout=5) as session:
            deferred = await session.receive_deferred_messages(deferred_messages)
            assert len(deferred) == 10
            for message in deferred:
                assert isinstance(message, DeferredMessage)
                await message.dead_letter("something")

        count = 0
        async with queue_client.get_deadletter_receiver(idle_timeout=5) as receiver:
            async for message in receiver:
                count += 1
                print_message(message)
                assert message.user_properties[b'DeadLetterReason'] == b'something'
                assert message.user_properties[b'DeadLetterErrorDescription'] == b'something'
                await message.complete()
        assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
        results = await queue_client.send(messages)
        assert all(result[0] for result in results)

        count = 0
        receiver = queue_client.get_receiver(idle_timeout=5)
        async for message in receiver:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            await message.defer()

        assert count == 10
        async with queue_client.get_receiver(idle_timeout=5) as receiver:
            deferred = await receiver.receive_deferred_messages(deferred_messages, mode=ReceiveSettleMode.ReceiveAndDelete)
            assert len(deferred) == 10
            for message in deferred:
                assert isinstance(message, DeferredMessage)
                with pytest.raises(MessageAlreadySettled):
                    await message.complete()
            with pytest.raises(ServiceBusError):
                deferred = await receiver.receive_deferred_messages(deferred_messages)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_not_found(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

            async with queue_client.get_sender() as sender:
                for i in range(3):
                    message = Message("Deferred message no. {}".format(i))
                    await sender.send(message)

            count = 0
            async for message in receiver:
                deferred_messages.append(message.sequence_number)
                print_message(message)
                count += 1
                await message.defer()

        assert count == 3

        with pytest.raises(ServiceBusError):
            deferred = await queue_client.receive_deferred_messages([3, 4], mode=ReceiveSettleMode.PeekLock)

        with pytest.raises(ServiceBusError):
            deferred = await queue_client.receive_deferred_messages([5, 6, 7], mode=ReceiveSettleMode.PeekLock)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_receive_batch_with_deadletter(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

            async with queue_client.get_sender() as sender:
                for i in range(10):
                    message = Message("Dead lettered message no. {}".format(i))
                    await sender.send(message)

            count = 0
            messages = await receiver.fetch_next()
            while messages:
                for message in messages:
                    print_message(message)
                    count += 1
                    await message.dead_letter(description="Testing")
                messages = await receiver.fetch_next()

        assert count == 10

        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            count = 0
            async for message in receiver:
                print_message(message)
                await message.complete()
                count += 1
        assert count == 0

        async with queue_client.get_deadletter_receiver(idle_timeout=5) as receiver:
            async for message in receiver:
                count += 1
                print_message(message)
                assert message.user_properties[b'DeadLetterReason'] == b'Testing'
                assert message.user_properties[b'DeadLetterErrorDescription'] == b'Testing'
                await message.complete()
        assert count == 10

        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

            async with queue_client.get_sender() as sender:
                for i in range(5):
                    message = Message("Dead lettered message no. {}".format(i))
                    await sender.send(message)

            count = 0
            messages = await receiver.fetch_next()
            while messages:
                for message in messages:
                    print_message(message)
                    count += 1
                    await message.dead_letter(description="Testing description", reason="Testing reason")
                messages = await receiver.fetch_next()

        assert count == 5

        async with queue_client.get_deadletter_receiver(idle_timeout=5) as receiver:
            count = 0
            async for message in receiver:
                count += 1
                print_message(message)
                assert message.user_properties[b'DeadLetterReason'] == b'Testing reason'
                assert message.user_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                await message.complete()
        assert count == 5

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_receive_batch_with_retrieve_deadletter(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

            async with queue_client.get_sender() as sender:
                for i in range(10):
                    message = Message("Dead lettered message no. {}".format(i))
                    await sender.send(message)

            count = 0
            messages = await receiver.fetch_next()
            while messages:
                for message in messages:
                    print_message(message)
                    await message.dead_letter(description="Testing queue deadletter")
                    count += 1
                messages = await receiver.fetch_next()

            with pytest.raises(InvalidHandlerState):
                await receiver.fetch_next()

        assert count == 10

        async with queue_client.get_deadletter_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            count = 0
            async for message in receiver:
                print_message(message)
                await message.complete()
                assert message.user_properties[b'DeadLetterReason'] == b'Testing queue deadletter'
                assert message.user_properties[b'DeadLetterErrorDescription'] == b'Testing queue deadletter'
                count += 1
        assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_session_fail(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        with pytest.raises(ValueError):
            queue_client.get_receiver(session="test")

        async with queue_client.get_sender(session="test") as sender:
            await sender.send(Message("test session sender"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_browse_messages_client(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        async with queue_client.get_sender() as sender:
            for i in range(5):
                message = Message("Test message no. {}".format(i))
                await sender.send(message)

        messages = await queue_client.peek(5)
        assert len(messages) == 5
        assert all(isinstance(m, PeekMessage) for m in messages)
        for message in messages:
            print_message(message)
            with pytest.raises(TypeError):
                message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            async with queue_client.get_sender() as sender:
                for i in range(5):
                    message = Message("Test message no. {}".format(i))
                    await sender.send(message)

            messages = await receiver.peek(5)
            assert len(messages) > 0
            assert all(isinstance(m, PeekMessage) for m in messages)
            for message in messages:
                print_message(message)
                with pytest.raises(TypeError):
                    message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_browse_empty_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
            messages = await receiver.peek(10)
            assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_renew_message_locks(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        messages = []
        locks = 3
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
            async with queue_client.get_sender() as sender:
                for i in range(locks):
                    message = Message("Test message no. {}".format(i))
                    await sender.send(message)

            messages.extend(await receiver.fetch_next())
            recv = True
            while recv:
                recv = await receiver.fetch_next()
                messages.extend(recv)

            try:
                assert not message.expired
                for m in messages:
                    time.sleep(5)
                    initial_expiry = m.locked_until
                    await m.renew_lock()
                    assert (m.locked_until - initial_expiry) >= timedelta(seconds=5)
            finally:
                await messages[0].complete()
                await messages[1].complete()
                time.sleep(30)
                with pytest.raises(MessageLockExpired):
                    await messages[2].complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)

        async with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("{}".format(i))
                await sender.send(message)

        renewer = AutoLockRenew()
        messages = []
        async with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
            async for message in receiver:
                if not messages:
                    messages.append(message)
                    assert not message.expired
                    renewer.register(message, timeout=60)
                    print("Registered lock renew thread", message.locked_until, datetime.now())
                    await asyncio.sleep(50)
                    print("Finished first sleep", message.locked_until)
                    assert not message.expired
                    await asyncio.sleep(25)
                    print("Finished second sleep", message.locked_until, datetime.now())
                    assert message.expired
                    try:
                        await message.complete()
                        raise AssertionError("Didn't raise MessageLockExpired")
                    except MessageLockExpired as e:
                        assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                else:
                    if message.expired:
                        print("Remaining messages", message.locked_until, datetime.now())
                        assert message.expired
                        with pytest.raises(MessageLockExpired):
                            await message.complete()
                    else:
                        assert message.header.delivery_count >= 1
                        print("Remaining messages", message.locked_until, datetime.now())
                        messages.append(message)
                        await message.complete()
        await renewer.shutdown()
        assert len(messages) == 11

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_fail_send_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        try:
            queue_client = client.get_queue(servicebus_queue.name)
        except MessageSendFailed:
            pytest.skip("Open issue for uAMQP on OSX")

        too_large = "A" * 1024 * 512
        results = await queue_client.send(Message(too_large))
        assert len(results) == 1
        assert not results[0][0]
        assert isinstance(results[0][1], MessageSendFailed)

        async with queue_client.get_sender() as sender:
            with pytest.raises(MessageSendFailed):
                await sender.send(Message(too_large))

        async with queue_client.get_sender() as sender:
            sender.queue_message(Message(too_large))
            results = await sender.send_pending_messages()
            assert len(results) == 1
            assert not results[0][0]
            assert isinstance(results[0][1], MessageSendFailed)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_fail_send_batch_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        pytest.skip("TODO: Pending bugfix in uAMQP")
        def batch_data():
            for i in range(3):
                yield str(i) * 1024 * 256

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        results = await queue_client.send(BatchMessage(batch_data()))
        assert len(results) == 4
        assert not results[0][0]
        assert isinstance(results[0][1], MessageSendFailed)

        async with queue_client.get_sender() as sender:
            with pytest.raises(MessageSendFailed):
                await sender.send(BatchMessage(batch_data()))

        async with queue_client.get_sender() as sender:
            sender.queue_message(BatchMessage(batch_data()))
            results = await sender.send_pending_messages()
            assert len(results) == 4
            assert not results[0][0]
            assert isinstance(results[0][1], MessageSendFailed)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_time_to_live(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        queue_client = client.get_queue(servicebus_queue.name)

        async with queue_client.get_sender() as sender:
            content = str(uuid.uuid4())
            message_id = uuid.uuid4()
            message = Message(content)
            message.time_to_live = timedelta(seconds=30)
            await sender.send(message)

        time.sleep(30)
        async with queue_client.get_receiver() as receiver:
            messages = await receiver.fetch_next(timeout=10)
        assert not messages

        async with queue_client.get_deadletter_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            count = 0
            async for message in receiver:
                print_message(message)
                await message.complete()
                count += 1
            assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_duplicate_detection=True, dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_duplicate_detection(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        message_id = uuid.uuid4()
        queue_client = client.get_queue(servicebus_queue.name)

        async with queue_client.get_sender() as sender:
            for i in range(5):
                message = Message(str(i))
                message.properties.message_id = message_id
                await sender.send(message)

        async with queue_client.get_receiver(idle_timeout=5) as receiver:
            count = 0
            async for message in receiver:
                print_message(message)
                assert message.properties.message_id == message_id
                await message.complete()
                count += 1
            assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_connection_closed(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        queue_client = client.get_queue(servicebus_queue.name)

        async with queue_client.get_sender() as sender:
            content = str(uuid.uuid4())
            message = Message(content)
            await sender.send(message)

        async with queue_client.get_receiver() as receiver:
            messages = await receiver.fetch_next(timeout=10)
            assert len(messages) == 1

        with pytest.raises(MessageSettleFailed):
            await messages[0].complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_expiry(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        queue_client = client.get_queue(servicebus_queue.name)

        async with queue_client.get_sender() as sender:
            content = str(uuid.uuid4())
            message = Message(content)
            await sender.send(message)

        async with queue_client.get_receiver() as receiver:
            messages = await receiver.fetch_next(timeout=10)
            assert len(messages) == 1
            time.sleep(30)
            assert messages[0].expired
            with pytest.raises(MessageLockExpired):
                await messages[0].complete()
            with pytest.raises(MessageLockExpired):
                await messages[0].renew_lock()

        async with queue_client.get_receiver() as receiver:
            messages = await receiver.fetch_next(timeout=30)
            assert len(messages) == 1
            print_message(messages[0])
            assert messages[0].header.delivery_count > 0
            await messages[0].complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_lock_renew(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        queue_client = client.get_queue(servicebus_queue.name)

        async with queue_client.get_sender() as sender:
            content = str(uuid.uuid4())
            message = Message(content)
            await sender.send(message)

        async with queue_client.get_receiver() as receiver:
            messages = await receiver.fetch_next(timeout=10)
            assert len(messages) == 1
            time.sleep(15)
            await messages[0].renew_lock()
            time.sleep(15)
            await messages[0].renew_lock()
            time.sleep(15)
            assert not messages[0].expired
            await messages[0].complete()

        async with queue_client.get_receiver() as receiver:
            messages = await receiver.fetch_next(timeout=10)
            assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_receive_and_delete(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        queue_client = client.get_queue(servicebus_queue.name)

        async with queue_client.get_sender() as sender:
            message = Message("Receive and delete test")
            await sender.send(message)

        async with queue_client.get_receiver(mode=ReceiveSettleMode.ReceiveAndDelete) as receiver:
            messages = await receiver.fetch_next(timeout=10)
            assert len(messages) == 1
            received = messages[0]
            print_message(received)
            with pytest.raises(MessageAlreadySettled):
                await received.complete()
            with pytest.raises(MessageAlreadySettled):
                await received.abandon()
            with pytest.raises(MessageAlreadySettled):
                await received.defer()
            with pytest.raises(MessageAlreadySettled):
                await received.dead_letter()
            with pytest.raises(MessageAlreadySettled):
                await received.renew_lock()

        time.sleep(30)
        async with queue_client.get_receiver() as receiver:
            messages = await receiver.fetch_next(timeout=10)
            for m in messages:
                print_message(m)
            assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_batch(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        queue_client = client.get_queue(servicebus_queue.name)

        def message_content():
            for i in range(5):
                yield "Message no. {}".format(i)


        async with queue_client.get_sender() as sender:
            message = BatchMessage(message_content())
            await sender.send(message)

        async with queue_client.get_receiver() as receiver:
            messages = await receiver.fetch_next(timeout=10)
            recv = True
            while recv:
                recv = await receiver.fetch_next(timeout=10)
                messages.extend(recv)

            assert len(messages) == 5
            for m in messages:
                print_message(m)
                await m.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_schedule_message(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        queue_client = client.get_queue(servicebus_queue.name)
        enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
        async with queue_client.get_receiver() as receiver:
            async with queue_client.get_sender() as sender:
                content = str(uuid.uuid4())
                message_id = uuid.uuid4()
                message = Message(content)
                message.properties.message_id = message_id
                message.schedule(enqueue_time)
                await sender.send(message)

            messages = await receiver.fetch_next(timeout=120)
            if messages:
                try:
                    data = str(messages[0])
                    assert data == content
                    assert messages[0].properties.message_id == message_id
                    assert messages[0].scheduled_enqueue_time == enqueue_time
                    assert messages[0].scheduled_enqueue_time == messages[0].enqueued_time.replace(microsecond=0)
                    assert len(messages) == 1
                finally:
                    for m in messages:
                        await m.complete()
            else:
                raise Exception("Failed to receive scheduled message.")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_schedule_multiple_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        queue_client = client.get_queue(servicebus_queue.name)
        enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
        messages = []
        async with queue_client.get_receiver(prefetch=20) as receiver:
            async with queue_client.get_sender() as sender:
                content = str(uuid.uuid4())
                message_id_a = uuid.uuid4()
                message_a = Message(content)
                message_a.properties.message_id = message_id_a
                message_id_b = uuid.uuid4()
                message_b = Message(content)
                message_b.properties.message_id = message_id_b
                tokens = await sender.schedule(enqueue_time, message_a, message_b)
                assert len(tokens) == 2

            recv = await receiver.fetch_next(timeout=120)
            messages.extend(recv)
            recv = await receiver.fetch_next(timeout=5)
            messages.extend(recv)
            if messages:
                try:
                    data = str(messages[0])
                    assert data == content
                    assert messages[0].properties.message_id in (message_id_a, message_id_b)
                    assert messages[0].scheduled_enqueue_time == enqueue_time
                    assert messages[0].scheduled_enqueue_time == messages[0].enqueued_time.replace(microsecond=0)
                    assert len(messages) == 2
                finally:
                    for m in messages:
                        await m.complete()
            else:
                raise Exception("Failed to receive scheduled message.")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_cancel_scheduled_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
        async with queue_client.get_receiver() as receiver:
            async with queue_client.get_sender() as sender:
                message_a = Message("Test scheduled message")
                message_b = Message("Test scheduled message")
                tokens = await sender.schedule(enqueue_time, message_a, message_b)
                assert len(tokens) == 2

                await sender.cancel_scheduled_messages(*tokens)

            messages = await receiver.fetch_next(timeout=120)
            assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_reconnect_send_after_long_wait(self, servicebus_namespace, servicebus_namespace_key_name,
                                    servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        # https://github.com/Azure/azure-uamqp-python/issues/135
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        queue_client = client.get_queue(servicebus_queue.name)
        async with queue_client.get_sender() as sender:
            await sender.send(Message("Test message"))
            time.sleep(620)
            await sender.send(Message("Test message"))

        async with queue_client.get_receiver(prefetch=20) as receiver:
            messages = await receiver.fetch_next(timeout=10)
            assert len(messages) == 2
            await messages[0].complete()
            await messages[1].complete()
