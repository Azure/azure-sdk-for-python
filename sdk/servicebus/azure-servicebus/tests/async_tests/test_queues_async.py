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
import uuid
from datetime import datetime, timedelta

from azure.servicebus.aio import (
    ServiceBusClient,
    ReceivedMessage,
    AutoLockRenew)
from azure.servicebus import TransportType
from azure.servicebus._common.message import Message, BatchMessage, PeekMessage
from azure.servicebus._common.constants import ReceiveSettleMode
from azure.servicebus._common.utils import utc_now
from azure.servicebus.exceptions import (
    ServiceBusConnectionError,
    ServiceBusError,
    MessageLockExpired,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSendFailed,
    MessageSettleFailed,
    MessageContentTooLarge)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, CachedServiceBusQueuePreparer, ServiceBusQueuePreparer
from utilities import get_logger, print_message, sleep_until_expired
from mocks_async import MockReceivedMessage

_logger = get_logger(logging.DEBUG)


class ServiceBusQueueAsyncTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_conn_str_receive_handler_peeklock(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Handler message no. {}".format(i))
                    await sender.send_messages(message)

            with pytest.raises(ServiceBusConnectionError):
                await (sb_client.get_queue_session_receiver(servicebus_queue.name, session_id="test", idle_timeout=5))._open_with_retry()

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    count += 1
                    await message.complete()

            assert count == 10


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_send_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                messages = []
                for i in range(10):
                    message = Message("Handler message no. {}".format(i))
                    messages.append(message)
                await sender.send_messages(messages)

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    count += 1
                    await message.complete()

                assert count == 10


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_github_issue_7079_async(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    await sender.send_messages(Message("Message {}".format(i)))
            async with sb_client.get_queue_receiver(servicebus_queue.name, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5) as messages:
                batch = await messages.receive_messages()
                count = len(batch)
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
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    await sender.send_messages(Message("Message {}".format(i)))
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=60) as messages:
                async for message in messages:
                    _logger.debug(message)
                    _logger.debug(message.sequence_number)
                    _logger.debug(message.enqueued_time_utc)
                    _logger.debug(message._lock_expired)
                    await message.complete()
                    await asyncio.sleep(40)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Handler message no. {}".format(i))
                    await sender.send_messages(message)

            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=8) as receiver:
                async for message in receiver:
                    messages.append(message)
                    with pytest.raises(MessageAlreadySettled):
                        await message.complete()

            assert not receiver._running
            assert len(messages) == 10
            time.sleep(30)

            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5) as receiver:
                async for message in receiver:
                    messages.append(message)
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_conn_str_receive_handler_with_stop(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Stop message no. {}".format(i))
                    await sender.send_messages(message)

            messages = []
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, prefetch=0) 
            async with receiver:
                async for message in receiver:
                    messages.append(message)
                    await message.complete()
                    if len(messages) >= 5:
                        break

                assert receiver._running
                assert len(messages) == 5

            async with receiver:
                async for message in receiver:
                    messages.append(message)
                    await message.complete()
                    if len(messages) >= 5:
                        break

            assert not receiver._running
            assert len(messages) == 6

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_simple(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Iter message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await message.complete()
                    with pytest.raises(MessageAlreadySettled):
                        await message.complete()
                    with pytest.raises(MessageAlreadySettled):
                        await message.renew_lock()
                    count += 1

                with pytest.raises(StopAsyncIteration):
                    await receiver.__anext__()

            assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_conn_str_client_iter_messages_with_abandon(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Abandoned message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    if not message.delivery_count:
                        count += 1
                        await message.abandon()
                    else:
                        assert message.delivery_count == 1
                        await message.complete()

            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await message.complete()
                    count += 1
            assert count == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_defer(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Deferred message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()

            assert count == 10
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await message.complete()
                    count += 1
            assert count == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Deferred message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()

                assert count == 10

                deferred = await receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    await message.complete()

                with pytest.raises(ServiceBusError):
                    await receiver.receive_deferred_messages(deferred_messages)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for message in [Message("Deferred message no. {}".format(i)) for i in range(10)]:
                    results = await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()
            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as session:
                deferred = await session.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    assert message.lock_token
                    assert message.locked_until_utc
                    assert message._receiver
                    await message.renew_lock()
                    await message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for message in [Message("Deferred message no. {}".format(i)) for i in range(10)]:
                    results = await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()

            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as session:
                deferred = await session.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    await message.dead_letter(reason="Testing reason", description="Testing description")

            count = 0
            async with sb_client.get_queue_deadletter_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                async for message in receiver:
                    count += 1
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    await message.complete()
            assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for message in [Message("Deferred message no. {}".format(i)) for i in range(10)]:
                    results = await sender.send_messages(message)

            count = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()

            assert count == 10
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.ReceiveAndDelete) as receiver:
                deferred = await receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    with pytest.raises(MessageAlreadySettled):
                        await message.complete()
                with pytest.raises(ServiceBusError):
                    deferred = await receiver.receive_deferred_messages(deferred_messages)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_not_found(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(3):
                        message = Message("Deferred message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()

            assert count == 3

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                with pytest.raises(ServiceBusError):
                    deferred = await receiver.receive_deferred_messages([3, 4])

                with pytest.raises(ServiceBusError):
                    deferred = await receiver.receive_deferred_messages([5, 6, 7])

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_receive_batch_with_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Dead lettered message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                messages = await receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        count += 1
                        await message.dead_letter(reason="Testing reason", description="Testing description")
                    messages = await receiver.receive_messages()

            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await message.complete()
                    count += 1
            assert count == 0

            async with sb_client.get_queue_deadletter_receiver(
                    servicebus_queue.name,
                    idle_timeout=5,
                    mode=ReceiveSettleMode.PeekLock) as dl_receiver:
                count = 0
                async for message in dl_receiver:
                    await message.complete()
                    count += 1
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.properties[b'DeadLetterErrorDescription'] == b'Testing description'
                assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_receive_batch_with_retrieve_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Dead lettered message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                messages = await receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        await message.dead_letter(reason="Testing reason", description="Testing description")
                        count += 1
                    messages = await receiver.receive_messages()

            assert count == 10

            async with sb_client.get_queue_deadletter_receiver(
                servicebus_queue.name,
                idle_timeout=5,
                mode=ReceiveSettleMode.PeekLock
            ) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    await message.complete()
                    count += 1
            assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_session_fail(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with pytest.raises(ServiceBusConnectionError):
                await sb_client.get_queue_session_receiver(servicebus_queue.name, session_id="test")._open_with_retry()

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(Message("test session sender", session_id="test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_browse_messages_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = Message("Test message no. {}".format(i))
                    await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.peek_messages(5)
                assert len(messages) == 5
                assert all(isinstance(m, PeekMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(AttributeError):
                        message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = Message("Test message no. {}".format(i))
                        await sender.send_messages(message)

                messages = await receiver.peek_messages(5)
                assert len(messages) > 0
                assert all(isinstance(m, PeekMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(AttributeError):
                        message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_browse_empty_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
                messages = await receiver.peek_messages(10)
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_renew_message_locks(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            messages = []
            locks = 3
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(locks):
                        message = Message("Test message no. {}".format(i))
                        await sender.send_messages(message)

                messages.extend(await receiver.receive_messages())
                recv = True
                while recv:
                    recv = await receiver.receive_messages()
                    messages.extend(recv)

                try:
                    with pytest.raises(AttributeError):
                        assert not message._lock_expired
                    for m in messages:
                        time.sleep(5)
                        initial_expiry = m.locked_until_utc
                        await m.renew_lock()
                        assert (m.locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    await messages[0].complete()
                    await messages[1].complete()
                    sleep_until_expired(messages[2])
                    with pytest.raises(MessageLockExpired):
                        await messages[2].complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("{}".format(i))
                    await sender.send_messages(message)

            renewer = AutoLockRenew()
            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
                async for message in receiver:
                    if not messages:
                        messages.append(message)
                        assert not message._lock_expired
                        renewer.register(message, timeout=60)
                        print("Registered lock renew thread", message.locked_until_utc, utc_now())
                        await asyncio.sleep(60)
                        print("Finished first sleep", message.locked_until_utc)
                        assert not message._lock_expired
                        await asyncio.sleep(15) #generate autolockrenewtimeout error by going one iteration past.
                        sleep_until_expired(message)
                        print("Finished second sleep", message.locked_until_utc, utc_now())
                        assert message._lock_expired
                        try:
                            await message.complete()
                            raise AssertionError("Didn't raise MessageLockExpired")
                        except MessageLockExpired as e:
                            assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                    else:
                        if message._lock_expired:
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            assert message._lock_expired
                            with pytest.raises(MessageLockExpired):
                                await message.complete()
                        else:
                            assert message.delivery_count >= 1
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            messages.append(message)
                            await message.complete()
            await renewer.close()
            assert len(messages) == 11

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_fail_send_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            too_large = "A" * 1024 * 256
            
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                with pytest.raises(MessageContentTooLarge):
                    await sender.send_messages(Message(too_large))
                    
                half_too_large = "A" * int((1024 * 256) / 2)
                with pytest.raises(MessageContentTooLarge):
                    await sender.send_messages([Message(half_too_large), Message(half_too_large)])

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_time_to_live(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message_id = uuid.uuid4()
                message = Message(content)
                message.time_to_live = timedelta(seconds=30)
                await sender.send_messages(message)

            time.sleep(30)
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
            assert not messages

            async with sb_client.get_queue_deadletter_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await message.complete()
                    count += 1
                assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_duplicate_detection=True, dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_duplicate_detection(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            message_id = uuid.uuid4()

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = Message(str(i))
                    message.message_id = message_id
                    await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    assert message.message_id == message_id
                    await message.complete()
                    count += 1
                assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_connection_closed(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = Message(content)
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1

            with pytest.raises(MessageSettleFailed):
                await messages[0].complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_expiry(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = Message(content)
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep(60)
                assert messages[0]._lock_expired
                with pytest.raises(MessageLockExpired):
                    await messages[0].complete()
                with pytest.raises(MessageLockExpired):
                    await messages[0].renew_lock()

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                assert messages[0].delivery_count > 0
                await messages[0].complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_lock_renew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = Message(content)
                await sender.send_messages(message)
            
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep(15)
                await messages[0].renew_lock()
                time.sleep(15)
                await messages[0].renew_lock()
                time.sleep(15)
                assert not messages[0]._lock_expired
                await messages[0].complete()
            
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_receive_and_delete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = Message("Receive and delete test")
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, mode=ReceiveSettleMode.ReceiveAndDelete) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                received = messages[0]
                print_message(_logger, received)
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
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                for m in messages:
                    print_message(_logger, m)
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_message_batch(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = BatchMessage()
                for i in range(5):
                    message.add(Message("Message no. {}".format(i)))
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                recv = True
                while recv:
                    recv = await receiver.receive_messages(max_wait_time=10)
                    messages.extend(recv)

                assert len(messages) == 5
                for m in messages:
                    print_message(_logger, m)
                    await m.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_schedule_message(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    content = str(uuid.uuid4())
                    message_id = uuid.uuid4()
                    message = Message(content)
                    message.message_id = message_id
                    message.scheduled_enqueue_time_utc = enqueue_time
                    await sender.send_messages(message)

                messages = await receiver.receive_messages(max_wait_time=120)
                if messages:
                    try:
                        data = str(messages[0])
                        assert data == content
                        assert messages[0].message_id == message_id
                        assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
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
    async def test_async_queue_schedule_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            messages = []
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, prefetch=20)
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            async with sender, receiver:
                content = str(uuid.uuid4())
                message_id_a = uuid.uuid4()
                message_a = Message(content)
                message_a.message_id = message_id_a
                message_id_b = uuid.uuid4()
                message_b = Message(content)
                message_b.message_id = message_id_b

                await sender.send_messages([message_a, message_b])

                received_messages = await receiver.receive_messages(max_batch_size=2, max_wait_time=5)
                for message in received_messages:
                    await message.complete()

                tokens = await sender.schedule_messages(received_messages, enqueue_time)
                assert len(tokens) == 2

                messages = await receiver.receive_messages(max_wait_time=120)
                recv = await receiver.receive_messages(max_wait_time=5)
                messages.extend(recv)
                if messages:
                    try:
                        data = str(messages[0])
                        assert data == content
                        assert messages[0].message_id in (message_id_a, message_id_b)
                        assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
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
    async def test_async_queue_cancel_scheduled_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    message_a = Message("Test scheduled message")
                    message_b = Message("Test scheduled message")
                    tokens = await sender.schedule_messages([message_a, message_b], enqueue_time)
                    assert len(tokens) == 2

                    await sender.cancel_scheduled_messages(tokens)

                messages = await receiver.receive_messages(max_wait_time=120)
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_queue_message_amqp_over_websocket(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                transport_type=TransportType.AmqpOverWebsocket,
                logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                assert sender._config.transport_type == TransportType.AmqpOverWebsocket
                message = Message("Test")
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, mode=ReceiveSettleMode.ReceiveAndDelete) as receiver:
                assert receiver._config.transport_type == TransportType.AmqpOverWebsocket
                messages = await receiver.receive_messages(max_wait_time=5)
                assert len(messages) == 1

    def test_queue_message_http_proxy_setting(self):
        mock_conn_str = "Endpoint=sb://mock.servicebus.windows.net/;SharedAccessKeyName=mock;SharedAccessKey=mock"
        http_proxy = {
            'proxy_hostname': '127.0.0.1',
            'proxy_port': 8899,
            'username': 'admin',
            'password': '123456'
        }

        sb_client = ServiceBusClient.from_connection_string(mock_conn_str, http_proxy=http_proxy)
        assert sb_client._config.http_proxy == http_proxy
        assert sb_client._config.transport_type == TransportType.AmqpOverWebsocket

        sender = sb_client.get_queue_sender(queue_name="mock")
        assert sender._config.http_proxy == http_proxy
        assert sender._config.transport_type == TransportType.AmqpOverWebsocket

        receiver = sb_client.get_queue_receiver(queue_name="mock")
        assert receiver._config.http_proxy == http_proxy
        assert receiver._config.transport_type == TransportType.AmqpOverWebsocket

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_queue_message_settle_through_mgmt_link_due_to_broken_receiver_link(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = Message("Test")
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=5)
                await receiver._handler.message_handler.destroy_async()  # destroy the underlying receiver link
                assert len(messages) == 1
                await messages[0].complete()


    @pytest.mark.asyncio
    async def test_async_queue_mock_auto_lock_renew_callback(self):
        results = []
        errors = []
        async def callback_mock(renewable, error):
            results.append(renewable)
            if error:
                errors.append(error)

        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1 # So we can run the test fast.
        async with auto_lock_renew: # Check that it is called when the object expires for any reason (silent renew failure)
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            await asyncio.sleep(3)
            assert len(results) == 1 and results[-1]._lock_expired == True
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew: # Check that in normal operation it does not get called
            auto_lock_renew.register(renewable=MockReceivedMessage(), on_lock_renew_failure=callback_mock)
            await asyncio.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew: # Check that when a message is settled, it will not get called even after expiry
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            message._settled = True
            await asyncio.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew: # Check that it is called when there is an overt renew failure
            message = MockReceivedMessage(exception_on_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            await asyncio.sleep(3)
            assert len(results) == 1 and results[-1]._lock_expired == True
            assert errors[-1]

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew: # Check that it is not called when the renewer is shutdown
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            await auto_lock_renew.close()
            await asyncio.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew: # Check that it is not called when the receiver is shutdown
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            message._receiver._running = False
            await asyncio.sleep(3)
            assert not results
            assert not errors


    @pytest.mark.asyncio
    async def test_async_queue_mock_no_reusing_auto_lock_renew(self):
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1

        async with auto_lock_renew:
            auto_lock_renew.register(renewable=MockReceivedMessage())
            await asyncio.sleep(3)

        with pytest.raises(ServiceBusError):
            async with auto_lock_renew:
                pass

        with pytest.raises(ServiceBusError):
            auto_lock_renew.register(renewable=MockReceivedMessage())

        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1

        auto_lock_renew.register(renewable=MockReceivedMessage())
        time.sleep(3)

        await auto_lock_renew.close()

        with pytest.raises(ServiceBusError):
            async with auto_lock_renew:
                pass

        with pytest.raises(ServiceBusError):
            auto_lock_renew.register(renewable=MockReceivedMessage())

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_receive_batch_without_setting_prefetch(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            def message_content():
                for i in range(20):
                    yield Message(
                        body="Message no. {}".format(i),
                        label='1st'
                    )

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name)

            async with sender, receiver:
                message = BatchMessage()
                for each in message_content():
                    message.add(each)
                await sender.send_messages(message)

                receive_counter = 0
                message_1st_received_cnt = 0
                message_2nd_received_cnt = 0
                while message_1st_received_cnt < 20 or message_2nd_received_cnt < 20:
                    messages = await receiver.receive_messages(max_batch_size=20, max_wait_time=5)
                    if not messages:
                        break
                    receive_counter += 1
                    for message in messages:
                        print_message(_logger, message)
                        if message.label == '1st':
                            message_1st_received_cnt += 1
                            await message.complete()
                            message.label = '2nd'
                            await sender.send_messages(message)  # resending received message
                        elif message.label == '2nd':
                            message_2nd_received_cnt += 1
                            await message.complete()

                assert message_1st_received_cnt == 20 and message_2nd_received_cnt == 20
                # Network/server might be unstable making flow control ineffective in the leading rounds of connection iteration
                assert receive_counter < 10  # Dynamic link credit issuing come info effect
