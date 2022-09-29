#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import logging
import sys
import os
import types
import pytest
import time
import uuid
from datetime import datetime, timedelta

from azure.servicebus.aio import (
    ServiceBusClient,
    AutoLockRenewer
)
from azure.servicebus import (
    ServiceBusMessage,
    ServiceBusMessageBatch,
    ServiceBusReceivedMessage,
    TransportType,
    ServiceBusReceiveMode,
    ServiceBusSubQueue,
    ServiceBusMessageState
)
from azure.servicebus.amqp import (
    AmqpMessageHeader,
    AmqpMessageBodyType,
    AmqpAnnotatedMessage,
    AmqpMessageProperties,
)
from azure.servicebus._pyamqp.message import Message
from azure.servicebus._pyamqp import error, management_operation
from azure.servicebus._pyamqp.aio import AMQPClientAsync, ReceiveClientAsync, _management_operation_async
from azure.servicebus._common.constants import ServiceBusReceiveMode, ServiceBusSubQueue
from azure.servicebus._common.utils import utc_now
from azure.servicebus.management._models import DictMixin
from azure.servicebus.exceptions import (
    ServiceBusConnectionError,
    ServiceBusError,
    MessageLockLostError,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSizeExceededError,
    OperationTimeoutError
)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer, AzureTestCase
from servicebus_preparer import CachedServiceBusNamespacePreparer, CachedServiceBusQueuePreparer, ServiceBusQueuePreparer
from utilities import get_logger, print_message, sleep_until_expired
from mocks_async import MockReceivedMessage, MockReceiver

_logger = get_logger(logging.DEBUG)


class ServiceBusQueueAsyncTests(AzureMgmtTestCase):
    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    async def test_async_queue_by_queue_client_conn_str_receive_handler_peeklock(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            async with sender:
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i))
                    await sender.send_messages(message, timeout=5)

                # Test that noop empty send works properly.
                await sender.send_messages([])
                await sender.send_messages(ServiceBusMessageBatch())
                assert len(await sender.schedule_messages([], utc_now())) == 0
                await sender.cancel_scheduled_messages([])

            # Then test expected failure modes.
            with pytest.raises(ValueError):
                async with sender:
                    raise AssertionError("Should raise ValueError")
            with pytest.raises(ValueError):
                await sender.send_messages(ServiceBusMessage('msg'))
            with pytest.raises(ValueError):
                await sender.schedule_messages(ServiceBusMessage('msg'), utc_now())
            with pytest.raises(ValueError):
                await sender.cancel_scheduled_messages([1, 2, 3])

            with pytest.raises(ServiceBusError):
                await (sb_client.get_queue_receiver(servicebus_queue.name, session_id="test", max_wait_time=5))._open_with_retry()

            with pytest.raises(ValueError):
                sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=0)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)
            async with receiver:
                assert len(await receiver.receive_deferred_messages([])) == 0
                with pytest.raises(ValueError):
                    await receiver.receive_messages(max_wait_time=0)

                with pytest.raises(ValueError):
                    await receiver._get_streaming_message_iter(max_wait_time=0)

                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    count += 1
                    await receiver.complete_message(message)

            assert count == 10

            with pytest.raises(ValueError):
                await receiver.receive_messages()
            with pytest.raises(ValueError):
                async with receiver:
                    raise AssertionError("Should raise ValueError")
            with pytest.raises(ValueError):
                await receiver.receive_deferred_messages([1, 2, 3])
            with pytest.raises(ValueError):
                await receiver.peek_messages()

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    async def test_async_queue_by_queue_client_conn_str_receive_handler_release_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async def sub_test_releasing_messages():
                # test releasing messages when prefetch is 1 and link credits are issue dynamically
                receiver = sb_client.get_queue_receiver(servicebus_queue.name)
                sender = sb_client.get_queue_sender(servicebus_queue.name)
                async with sender, receiver:
                    # send 10 msgs to queue first
                    await sender.send_messages([ServiceBusMessage('test') for _ in range(5)])

                    received_msgs = []
                    # the amount of messages returned by receive call is not stable, especially in live tests
                    # of different os platforms, this is why a while loop is used here to receive the specific
                    # amount of message we want to receive
                    while len(received_msgs) < 5:
                        # issue link credits more than 5, client should consume 5 msgs from the service in total,
                        # leaving the extra credits on the wire
                        for msg in (await receiver.receive_messages(max_message_count=10, max_wait_time=10)):
                            await receiver.complete_message(msg)
                            received_msgs.append(received_msgs)
                    assert len(received_msgs) == 5

                    # send 5 more messages, those messages would arrive at the client while the program is sleeping
                    await sender.send_messages([ServiceBusMessage('test') for _ in range(5)])
                    await asyncio.sleep(15)  # sleep > message expiration time

                    target_msgs_count = 5
                    received_msgs = []
                    while len(received_msgs) < target_msgs_count:
                        # issue 10 link credits, client should consume 5 msgs from the service, leaving no link credits
                        for msg in (await receiver.receive_messages(max_message_count=target_msgs_count - len(received_msgs),
                                                             max_wait_time=10)):
                            assert msg.delivery_count == 0  # release would not increase delivery count
                            await receiver.complete_message(msg)
                            received_msgs.append(msg)
                    assert len(received_msgs) == 5

            async def sub_test_releasing_messages_iterator():
                # test nested iterator scenario
                receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10)
                sender = sb_client.get_queue_sender(servicebus_queue.name)
                async with sender, receiver:
                    # send 5 msgs to queue first
                    await sender.send_messages([ServiceBusMessage('test') for _ in range(5)])
                    first_time = True
                    iterator_recv_cnt = 0

                    # case: iterator + receive batch
                    async for msg in receiver:
                        assert msg.delivery_count == 0  # release would not increase delivery count
                        await receiver.complete_message(msg)
                        iterator_recv_cnt += 1
                        if first_time:  # for the first time, we call nested receive message call
                            received_msgs = []

                            while len(received_msgs) < 4:  # there supposed to be 5 msgs in the queue
                                # we issue 10 link credits, leaving more credits on the wire
                                for sub_msg in (await receiver.receive_messages(max_message_count=10, max_wait_time=10)):
                                    assert sub_msg.delivery_count == 0
                                    await receiver.complete_message(sub_msg)
                                    received_msgs.append(sub_msg)
                            assert len(received_msgs) == 4
                            await sender.send_messages([ServiceBusMessage('test') for _ in range(10)])
                            await asyncio.sleep(15)  # sleep > message expiration time

                            received_msgs = []
                            target_msgs_count = 5  # we want to receive 5 with the receive message call
                            while len(received_msgs) < target_msgs_count:
                                for sub_msg in (await receiver.receive_messages(
                                        max_message_count=target_msgs_count - len(received_msgs), max_wait_time=5)):
                                    assert sub_msg.delivery_count == 0  # release would not increase delivery count
                                    await receiver.complete_message(sub_msg)
                                    received_msgs.append(sub_msg)
                            assert len(received_msgs) == target_msgs_count
                            first_time = False
                    assert iterator_recv_cnt == 6  # 1 before nested receive message call + 5 after nested receive message call

                    # case: iterator + iterator case
                    await sender.send_messages([ServiceBusMessage('test') for _ in range(10)])
                    outter_recv_cnt = 0
                    inner_recv_cnt = 0
                    async for msg in receiver:
                        assert msg.delivery_count == 0
                        outter_recv_cnt += 1
                        await receiver.complete_message(msg)
                        async for sub_msg in receiver:
                            assert sub_msg.delivery_count == 0
                            inner_recv_cnt += 1
                            await receiver.complete_message(sub_msg)
                            if inner_recv_cnt == 5:
                                await asyncio.sleep(15)  # innner finish receiving first 5 messages then sleep until lock expiration
                                break
                    assert outter_recv_cnt == 1
                    outter_recv_cnt = 0
                    async for msg in receiver:
                        assert msg.delivery_count == 0
                        outter_recv_cnt += 1
                        await receiver.complete_message(msg)
                    assert outter_recv_cnt == 4

            async def sub_test_non_releasing_messages():
                # test not releasing messages when prefetch is not 1
                receiver = sb_client.get_queue_receiver(servicebus_queue.name)
                sender = sb_client.get_queue_sender(servicebus_queue.name)

                def _hack_disable_receive_context_message_received(self, message):
                    # pylint: disable=protected-access
                    self._handler._was_message_received = True
                    self._handler._received_messages.put(message)

                async with sender, receiver:
                    # send 5 msgs to queue first
                    await sender.send_messages([ServiceBusMessage('test') for _ in range(5)])
                    receiver._handler.message_handler.on_message_received = types.MethodType(
                        _hack_disable_receive_context_message_received, receiver)
                    received_msgs = []
                    while len(received_msgs) < 5:
                        # issue 10 link credits, client should consume 5 msgs from the service
                        # leaving 5 credits on the wire
                        for msg in (await receiver.receive_messages(max_message_count=10, max_wait_time=10)):
                            await receiver.complete_message(msg)
                            received_msgs.append(msg)
                    assert len(received_msgs) == 5

                    # send 5 more messages, those messages would arrive at the client while the program is sleeping
                    await sender.send_messages([ServiceBusMessage('test') for _ in range(5)])
                    await asyncio.sleep(15)  # sleep > message expiration time

                    # issue 5 link credits, client should consume 5 msgs from the internal buffer which is already lock expired
                    target_msgs_count = 5
                    received_msgs = []
                    while len(received_msgs) < target_msgs_count:
                        received_msgs.extend((await receiver.receive_messages(max_message_count=5, max_wait_time=10)))
                    assert len(received_msgs) == 5
                    for msg in received_msgs:
                        assert msg.delivery_count == 0
                        with pytest.raises(ServiceBusError):
                            await receiver.complete_message(msg)

                    # re-received message with delivery count increased
                    target_msgs_count = 5
                    received_msgs = []
                    while len(received_msgs) < target_msgs_count:
                        received_msgs.extend((await receiver.receive_messages(max_message_count=5, max_wait_time=10)))
                    assert len(received_msgs) == 5
                    for msg in received_msgs:
                        assert msg.delivery_count > 0
                        await receiver.complete_message(msg)

            await sub_test_releasing_messages()
            await sub_test_releasing_messages_iterator()
            await sub_test_non_releasing_messages()

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_queue_client_send_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            async with sender:
                messages = []
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i))
                    messages.append(message)
                await sender.send_messages(messages)

            with pytest.raises(ValueError):
                async with sender:
                    raise AssertionError("Should raise ValueError")
            with pytest.raises(ValueError):
                await sender.send_messages(ServiceBusMessage('msg'))
            with pytest.raises(ValueError):
                await sender.schedule_messages(ServiceBusMessage('msg'), utc_now())
            with pytest.raises(ValueError):
                await sender.cancel_scheduled_messages([1, 2, 3])

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)
            count = 0
            async for message in receiver:
                print_message(_logger, message)
                count += 1
                await receiver.complete_message(message)

            assert count == 10

            await receiver.close()

            with pytest.raises(ValueError):
                await receiver.receive_messages()
            with pytest.raises(ValueError):
                async with receiver:
                    raise AssertionError("Should raise ValueError")
            with pytest.raises(ValueError):
                await receiver.receive_deferred_messages([1, 2, 3])
            with pytest.raises(ValueError):
                await receiver.peek_messages()

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    await sender.send_messages(ServiceBusMessage("ServiceBusMessage {}".format(i)))
            async with sb_client.get_queue_receiver(servicebus_queue.name, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, max_wait_time=5) as messages:
                batch = await messages.receive_messages()
                count = len(batch)
                async for message in messages:
                   _logger.debug(message)
                   count += 1
                assert count == 5

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    await sender.send_messages(ServiceBusMessage("Message {}".format(i)))
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=60) as receiver:
                async for message in receiver:
                    _logger.debug(message)
                    _logger.debug(message.sequence_number)
                    _logger.debug(message.enqueued_time_utc)
                    _logger.debug(message._lock_expired)
                    await receiver.complete_message(message)
                    await asyncio.sleep(40)

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    async def test_async_queue_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i))
                    await sender.send_messages(message)

            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, max_wait_time=8) as receiver:
                async for message in receiver:
                    messages.append(message)
                    with pytest.raises(ValueError):
                        await receiver.complete_message(message)
                    with pytest.raises(ValueError): # RECEIVE_AND_DELETE messages cannot be lock renewed.
                        renewer = AutoLockRenewer()
                        renewer.register(receiver, message)

            assert not receiver._running
            assert len(messages) == 10
            time.sleep(10)

            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, max_wait_time=5) as receiver:
                async for message in receiver:
                    messages.append(message)
                assert len(messages) == 0

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage("Stop message no. {}".format(i))
                    await sender.send_messages(message)

            messages = []
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, prefetch_count=0) 
            async with receiver:
                async for message in receiver:
                    messages.append(message)
                    await receiver.complete_message(message)
                    if len(messages) >= 5:
                        break

                assert receiver._running
                assert len(messages) == 5

                async for message in receiver:
                    messages.append(message)
                    await receiver.complete_message(message)
                    if len(messages) >= 5:
                        break

            assert not receiver._running
            assert len(messages) == 6

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_simple(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Iter message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await receiver.complete_message(message)
                    with pytest.raises(MessageAlreadySettled):
                        await receiver.complete_message(message)
                    with pytest.raises(MessageAlreadySettled):
                        await receiver.renew_message_lock(message)
                    count += 1

                with pytest.raises(StopAsyncIteration):
                    await receiver.__anext__()

            assert count == 10

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_conn_str_client_iter_messages_with_abandon(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Abandoned message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    if not message.delivery_count:
                        count += 1
                        await receiver.abandon_message(message)
                    else:
                        assert message.delivery_count == 1
                        await receiver.complete_message(message)

            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await receiver.complete_message(message)
                    count += 1
            assert count == 0

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_defer(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Deferred message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)

            assert count == 10
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await receiver.complete_message(message)
                    count += 1
            assert count == 0

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Deferred message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)

                assert count == 10

                deferred = await receiver.receive_deferred_messages(deferred_messages, timeout=10)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    await receiver.complete_message(message)

                with pytest.raises(ServiceBusError):
                    await receiver.receive_deferred_messages(deferred_messages)

    @pytest.mark.skip(reason="TODO: iterator support")
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
                for message in [ServiceBusMessage("Deferred message no. {}".format(i)) for i in range(10)]:
                    results = await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)
            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                with pytest.raises(ValueError):
                    await receiver.receive_deferred_messages(deferred_messages, timeout=0)
                deferred = await receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    assert message.lock_token
                    assert message.locked_until_utc
                    assert message._receiver
                    await receiver.renew_message_lock(message)
                    await receiver.complete_message(message)

    @pytest.mark.skip(reason="TODO: iterator support")
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
                for message in [ServiceBusMessage("Deferred message no. {}".format(i)) for i in range(10)]:
                    results = await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)

            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10) as receiver:
                deferred = await receiver.receive_deferred_messages(deferred_messages, timeout=None)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    await receiver.dead_letter_message(message, reason="Testing reason", error_description="Testing description")

            count = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                    sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                                                    max_wait_time=10) as receiver:
                async for message in receiver:
                    count += 1
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    await receiver.complete_message(message)
            assert count == 10

    @pytest.mark.skip(reason="TODO: iterator support")
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
                for message in [ServiceBusMessage("Deferred message no. {}".format(i)) for i in range(10)]:
                    results = await sender.send_messages(message)

            count = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10) as receiver:
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)

            assert count == 10
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE.value) as receiver:
                deferred = await receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    with pytest.raises(ValueError):
                        await receiver.complete_message(message)
                with pytest.raises(ServiceBusError):
                    deferred = await receiver.receive_deferred_messages(deferred_messages)

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_not_found(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(3):
                        message = ServiceBusMessage("Deferred message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)

            assert count == 3

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                with pytest.raises(ServiceBusError):
                    deferred = await receiver.receive_deferred_messages([3, 4])

                with pytest.raises(ServiceBusError):
                    deferred = await receiver.receive_deferred_messages([5, 6, 7])

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_receive_batch_with_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=10) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Dead lettered message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                messages = await receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        count += 1
                        await receiver.dead_letter_message(message, reason="Testing reason", error_description="Testing description")
                    messages = await receiver.receive_messages()

            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await receiver.complete_message(message)
                    count += 1
            assert count == 0

            async with sb_client.get_queue_receiver(
                    servicebus_queue.name,
                    sub_queue = ServiceBusSubQueue.DEAD_LETTER.value,
                    max_wait_time=10,
                    mode=ServiceBusReceiveMode.PEEK_LOCK) as dl_receiver:
                count = 0
                async for message in dl_receiver:
                    await dl_receiver.complete_message(message)
                    count += 1
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                assert count == 10

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_receive_batch_with_retrieve_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=10) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Dead lettered message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                messages = await receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        await receiver.dead_letter_message(message, reason="Testing reason", error_description="Testing description")
                        count += 1
                    messages = await receiver.receive_messages()

            assert count == 10

            async with sb_client.get_queue_receiver(
                servicebus_queue.name,
                sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                max_wait_time=5,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK
            ) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    await receiver.complete_message(message)
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

            with pytest.raises(ServiceBusError):
                await sb_client.get_queue_receiver(servicebus_queue.name, session_id="test")._open_with_retry()

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("test session sender", session_id="test"))

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
                    message = ServiceBusMessage("Test message no. {}".format(i))
                    await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.peek_messages(5)
                assert len(messages) == 5
                assert all(isinstance(m, ServiceBusReceivedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(ValueError):
                        await receiver.complete_message(message)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = ServiceBusMessage("Test message no. {}".format(i))
                        await sender.send_messages(message)

                messages = await receiver.peek_messages(5, timeout=5)
                assert len(messages) > 0
                assert all(isinstance(m, ServiceBusReceivedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(ValueError):
                        await receiver.complete_message(message)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_by_servicebus_client_browse_empty_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=10) as receiver:
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
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=10) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(locks):
                        message = ServiceBusMessage("Test message no. {}".format(i))
                        await sender.send_messages(message)

                messages.extend(await receiver.receive_messages())
                recv = True
                while recv:
                    recv = await receiver.receive_messages()
                    messages.extend(recv)

                try:
                    with pytest.raises(AttributeError):
                        assert not message._lock_expired
                    for message in messages:
                        time.sleep(5)
                        initial_expiry = message.locked_until_utc
                        await receiver.renew_message_lock(message)
                        assert (message.locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    await receiver.complete_message(messages[0])
                    await receiver.complete_message(messages[1])
                    sleep_until_expired(messages[2])
                    with pytest.raises(ServiceBusError):
                        await receiver.complete_message(messages[2])

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT5S')
    async def test_async_queue_by_queue_client_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i))
                    await sender.send_messages(message)

            # issue https://github.com/Azure/azure-sdk-for-python/issues/19642
            empty_renewer = AutoLockRenewer()
            async with empty_renewer:
                pass

            renewer = AutoLockRenewer()
            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=10) as receiver:
                async for message in receiver:
                    if not messages:
                        messages.append(message)
                        assert not message._lock_expired
                        renewer.register(receiver, message, max_lock_renewal_duration=10)
                        print("Registered lock renew thread", message.locked_until_utc, utc_now())
                        await asyncio.sleep(10)
                        print("Finished first sleep", message.locked_until_utc)
                        assert not message._lock_expired
                        await asyncio.sleep(15) #generate autolockrenewtimeout error by going one iteration past.
                        sleep_until_expired(message)
                        print("Finished second sleep", message.locked_until_utc, utc_now())
                        assert message._lock_expired
                        try:
                            await receiver.complete_message(message)
                            raise AssertionError("Didn't raise ServiceBusError")
                        except ServiceBusError as e:
                            assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                    else:
                        if message._lock_expired:
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            assert message._lock_expired
                            with pytest.raises(ServiceBusError):
                                await receiver.complete_message(message)
                        else:
                            assert message.delivery_count >= 1
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            messages.append(message)
                            await receiver.complete_message(message)
            await renewer.close()
            assert len(messages) == 11

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT5S')
    async def test_async_queue_by_queue_client_conn_str_receive_handler_with_auto_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                # The 10 iterations is "important" because it gives time for the timed out message to be received again.
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i))
                    await sender.send_messages(message)

            renewer = AutoLockRenewer(max_lock_renewal_duration=10)
            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name,
                                                    max_wait_time=5,
                                                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                                    prefetch_count=10,
                                                    auto_lock_renewer=renewer) as receiver:
                async for message in receiver:
                    if not messages:
                        messages.append(message)
                        assert not message._lock_expired
                        print("Registered lock renew thread", message.locked_until_utc, utc_now())
                        await asyncio.sleep(10)
                        print("Finished first sleep", message.locked_until_utc)
                        assert not message._lock_expired
                        await asyncio.sleep(15) #generate autolockrenewtimeout error by going one iteration past.
                        sleep_until_expired(message)
                        print("Finished second sleep", message.locked_until_utc, utc_now())
                        assert message._lock_expired
                        try:
                            await receiver.complete_message(message)
                            raise AssertionError("Didn't raise ServiceBusError")
                        except ServiceBusError as e:
                            assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                    else:
                        if message._lock_expired:
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            assert message._lock_expired
                            with pytest.raises(ServiceBusError):
                                await receiver.complete_message(message)
                        else:
                            assert message.delivery_count >= 1
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            messages.append(message)
                            await receiver.complete_message(message)
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
                with pytest.raises(MessageSizeExceededError):
                    await sender.send_messages(ServiceBusMessage(too_large))
                    
                half_too_large = "A" * int((1024 * 256) / 2)
                with pytest.raises(MessageSizeExceededError):
                    await sender.send_messages([ServiceBusMessage(half_too_large), ServiceBusMessage(half_too_large)])

    @pytest.mark.skip(reason="TODO: iterator support")
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
                message = ServiceBusMessage(content)
                message.time_to_live = timedelta(seconds=15)
                await sender.send_messages(message)

            time.sleep(15)
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
            assert not messages

            async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                    sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                                                    max_wait_time=5, 
                                                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await receiver.complete_message(message)
                    count += 1
                assert count == 1

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage(str(i))
                    message.message_id = message_id
                    await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    assert message.message_id == message_id
                    await receiver.complete_message(message)
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
                message = ServiceBusMessage(content)
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1

            with pytest.raises(ValueError):
                await receiver.complete_message(messages[0])

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
                message = ServiceBusMessage(content)
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep(60)
                assert messages[0]._lock_expired
                with pytest.raises(ServiceBusError):
                    await receiver.complete_message(messages[0])
                with pytest.raises(MessageLockLostError):
                    await receiver.renew_message_lock(messages[0])

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                assert messages[0].delivery_count > 0
                await receiver.complete_message(messages[0])

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
                message = ServiceBusMessage(content)
                await sender.send_messages(message)
            
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep(15)
                await receiver.renew_message_lock(messages[0], timeout=5)
                time.sleep(15)
                await receiver.renew_message_lock(messages[0])
                time.sleep(15)
                assert not messages[0]._lock_expired
                await receiver.complete_message(messages[0])
            
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    async def test_async_queue_message_receive_and_delete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("Receive and delete test")
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                message = messages[0]
                print_message(_logger, message)
                with pytest.raises(ValueError):
                    await receiver.complete_message(message)
                with pytest.raises(ValueError):
                    await receiver.abandon_message(message)
                with pytest.raises(ValueError):
                    await receiver.defer_message(message)
                with pytest.raises(ValueError):
                    await receiver.dead_letter_message(message)
                with pytest.raises(ValueError):
                    await receiver.renew_message_lock(message)

            time.sleep(10)
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

            def message_content():
                for i in range(5):
                    message = ServiceBusMessage("ServiceBusMessage no. {}".format(i))
                    message.application_properties = {'key': 'value'}
                    message.subject = 'label'
                    message.content_type = 'application/text'
                    message.correlation_id = 'cid'
                    message.message_id = str(i)
                    message.to = 'to'
                    message.reply_to = 'reply_to'
                    message.time_to_live = timedelta(seconds=60)
                    assert message.raw_amqp_message.properties.absolute_expiry_time == message.raw_amqp_message.properties.creation_time + message.raw_amqp_message.header.time_to_live

                    yield message

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessageBatch()
                for each in message_content():
                    message.add_message(each)
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                recv = True
                while recv:
                    recv = await receiver.receive_messages(max_wait_time=10)
                    messages.extend(recv)

                assert len(messages) == 5
                count = 0
                for message in messages:
                    assert message.delivery_count == 0
                    assert message.application_properties
                    assert message.application_properties[b'key'] == b'value'
                    assert message.subject == 'label'
                    assert message.content_type == 'application/text'
                    assert message.correlation_id == 'cid'
                    assert message.message_id == str(count)
                    assert message.to == 'to'
                    assert message.reply_to == 'reply_to'
                    assert message.sequence_number
                    assert message.enqueued_time_utc
                    assert message.expires_at_utc == (message.enqueued_time_utc + timedelta(seconds=60))
                    print_message(_logger, message)
                    await receiver.complete_message(message)
                    count += 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_schedule_message(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            scheduled_enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    content = str(uuid.uuid4())
                    message_id = uuid.uuid4()
                    message = ServiceBusMessage(content)
                    message.message_id = message_id
                    message.scheduled_enqueue_time_utc = scheduled_enqueue_time
                    await sender.send_messages(message)

                messages = await receiver.receive_messages(max_wait_time=120)
                if messages:
                    try:
                        data = str(messages[0])
                        assert data == content
                        assert messages[0].message_id == message_id
                        assert messages[0].scheduled_enqueue_time_utc == scheduled_enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc <= messages[0].enqueued_time_utc.replace(microsecond=0)
                        assert len(messages) == 1
                    finally:
                        for message in messages:
                            await receiver.complete_message(message)
                else:
                    raise Exception("Failed to receive scheduled message.")

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_schedule_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            scheduled_enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            messages = []
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, prefetch_count=20)
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            async with sender, receiver:
                content = str(uuid.uuid4())
                message_id_a = uuid.uuid4()
                message_a = ServiceBusMessage(content)
                message_a.message_id = message_id_a
                message_id_b = uuid.uuid4()
                message_b = ServiceBusMessage(content)
                message_b.message_id = message_id_b

                await sender.send_messages([message_a, message_b])

                received_messages = []
                async for message in receiver._get_streaming_message_iter(max_wait_time=5):
                    received_messages.append(message)
                    await receiver.complete_message(message)

                tokens = await sender.schedule_messages(received_messages, scheduled_enqueue_time, timeout=5)
                assert len(tokens) == 2

                messages = await receiver.receive_messages(max_wait_time=120)
                recv = await receiver.receive_messages(max_wait_time=5)
                messages.extend(recv)
                if messages:
                    try:
                        data = str(messages[0])
                        assert data == content
                        assert messages[0].message_id in (message_id_a, message_id_b)
                        assert messages[0].scheduled_enqueue_time_utc == scheduled_enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc <= messages[0].enqueued_time_utc.replace(microsecond=0)
                        assert len(messages) == 2
                    finally:
                        for message in messages:
                            await receiver.complete_message(message)
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
                    message_a = ServiceBusMessage("Test scheduled message")
                    message_b = ServiceBusMessage("Test scheduled message")
                    tokens = await sender.schedule_messages([message_a, message_b], enqueue_time)
                    assert len(tokens) == 2

                    await sender.cancel_scheduled_messages(tokens, timeout=None)

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
                message = ServiceBusMessage("Test")
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE) as receiver:
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
                message = ServiceBusMessage("Test")
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_wait_time=5)
                await receiver._handler._link.detach()  # destroy the underlying receiver link
                assert len(messages) == 1
                await receiver.complete_message(messages[0])

    @AzureTestCase.await_prepared_test
    async def test_async_queue_mock_auto_lock_renew_callback(self):
        # A warning to future devs: If the renew period override heuristic in registration
        # ever changes, it may break this (since it adjusts renew period if it is not short enough)

        results = []
        errors = []
        async def callback_mock(renewable, error):
            results.append(renewable)
            if error:
                errors.append(error)

        receiver = MockReceiver()
        auto_lock_renew = AutoLockRenewer()
        with pytest.raises(TypeError):
            auto_lock_renew.register(receiver, renewable=Exception())  # an arbitrary invalid type.

        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1  # So we can run the test fast.
        async with auto_lock_renew:  # Check that it is called when the object expires for any reason (silent renew failure)
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            await asyncio.sleep(3)
            assert len(results) == 1 and results[-1]._lock_expired == True
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew:  # Check that in normal operation it does not get called
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage(), on_lock_renew_failure=callback_mock)
            await asyncio.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew:  # Check that when a message is settled, it will not get called even after expiry
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            message._settled = True
            await asyncio.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew: # Check that it is called when there is an overt renew failure
            message = MockReceivedMessage(exception_on_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            await asyncio.sleep(3)
            assert len(results) == 1 and results[-1]._lock_expired == True
            assert errors[-1]

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew:  # Check that it is not called when the renewer is shutdown
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            await auto_lock_renew.close()
            await asyncio.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        async with auto_lock_renew:  # Check that it is not called when the receiver is shutdown
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            message._receiver._running = False
            await asyncio.sleep(3)
            assert not results
            assert not errors

    @AzureTestCase.await_prepared_test
    async def test_async_queue_mock_no_reusing_auto_lock_renew(self):
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1

        receiver = MockReceiver()
        async with auto_lock_renew:
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage())
            await asyncio.sleep(3)

        with pytest.raises(ServiceBusError):
            async with auto_lock_renew:
                pass

        with pytest.raises(ServiceBusError):
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage())

        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1

        auto_lock_renew.register(receiver, renewable=MockReceivedMessage())
        time.sleep(3)

        await auto_lock_renew.close()

        with pytest.raises(ServiceBusError):
            async with auto_lock_renew:
                pass

        with pytest.raises(ServiceBusError):
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage())

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_queue_receiver_invalid_autolockrenew_mode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            with pytest.raises(ValueError):
                async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                                  auto_lock_renewer=AutoLockRenewer()) as receiver:
                
                    raise Exception("Should not get here, should fail fast because RECEIVE_AND_DELETE messages cannot be autorenewed.")

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
                    yield ServiceBusMessage(
                        body="ServiceBusMessage no. {}".format(i),
                        subject='1st'
                    )

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name)

            async with sender, receiver:
                message = ServiceBusMessageBatch()
                for each in message_content():
                    message.add_message(each)
                await sender.send_messages(message)

                receive_counter = 0
                message_1st_received_cnt = 0
                message_2nd_received_cnt = 0
                while message_1st_received_cnt < 20 or message_2nd_received_cnt < 20:
                    messages = []
                    batch = await receiver.receive_messages(max_message_count=20, max_wait_time=5)
                    while batch:
                        messages += batch
                        batch = await receiver.receive_messages(max_message_count=20, max_wait_time=5)
                    if not messages:
                        break
                    receive_counter += 1
                    for message in messages:
                        print_message(_logger, message)
                        if message.subject == '1st':
                            message_1st_received_cnt += 1
                            await receiver.complete_message(message)
                            message.subject = '2nd'
                            await sender.send_messages(message)  # resending received message
                        elif message.subject == '2nd':
                            message_2nd_received_cnt += 1
                            await receiver.complete_message(message)

                assert message_1st_received_cnt == 20 and message_2nd_received_cnt == 20
                # Network/server might be unstable making flow control ineffective in the leading rounds of connection iteration
                assert receive_counter < 10  # Dynamic link credit issuing come info effect

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_receiver_alive_after_timeout(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("0")
                message_1 = ServiceBusMessage("1")
                await sender.send_messages([message, message_1])

                messages = []
                async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10) as receiver:
                    
                    async for message in receiver._get_streaming_message_iter():
                        messages.append(message)
                        break

                    async for message in receiver._get_streaming_message_iter():
                        messages.append(message)

                    for message in messages:
                        await receiver.complete_message(message)

                    assert len(messages) == 2
                    assert str(messages[0]) == "0"
                    assert str(messages[1]) == "1"

                    message_2 = ServiceBusMessage("2")
                    message_3 = ServiceBusMessage("3")
                    await sender.send_messages([message_2, message_3])

                    async for message in receiver._get_streaming_message_iter():
                        messages.append(message)
                        async for message in receiver._get_streaming_message_iter():
                            messages.append(message)

                    assert len(messages) == 4
                    assert str(messages[2]) == "2"
                    assert str(messages[3]) == "3"

                    for message in messages[2:]:
                        await receiver.complete_message(message)

                    messages = await receiver.receive_messages()
                    assert not messages

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT5M')
    async def test_queue_receive_keep_conn_alive_async(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)

            async with sender, receiver:
                await sender.send_messages([ServiceBusMessage("message1"), ServiceBusMessage("message2")])

                messages = []
                async for message in receiver:
                    messages.append(message)

                receiver_handler = receiver._handler
                assert len(messages) == 2
                await asyncio.sleep(4 * 60 + 5)  # 240s is the service defined connection idle timeout
                await receiver.renew_message_lock(messages[0])  # check mgmt link operation
                await receiver.complete_message(messages[0])
                await receiver.complete_message(messages[1])  # check receiver link operation

                await asyncio.sleep(60)  # sleep another one minute to ensure we pass the lock_duration time
                messages = []
                async for message in receiver:
                    messages.append(message)

                assert len(messages) == 0  # make sure messages are removed from the queue
                assert receiver_handler == receiver._handler  # make sure no reconnection happened

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_async_queue_receiver_respects_max_wait_time_overrides(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("0")
                await sender.send_messages(message)

                messages = []
                async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:

                    time_1 = receiver._handler._counter.get_current_ms()
                    async for message in receiver._get_streaming_message_iter(max_wait_time=10):
                        messages.append(message)
                        await receiver.complete_message(message)

                        time_2 = receiver._handler._counter.get_current_ms()
                        async for message in receiver._get_streaming_message_iter(max_wait_time=1):
                            messages.append(message)
                        time_3 = receiver._handler._counter.get_current_ms()
                        assert timedelta(seconds=.5) < timedelta(milliseconds=(time_3 - time_2)) <= timedelta(seconds=2)
                    time_4 = receiver._handler._counter.get_current_ms()
                    assert timedelta(seconds=8) < timedelta(milliseconds=(time_4 - time_3)) <= timedelta(seconds=11)

                    async for message in receiver._get_streaming_message_iter(max_wait_time=3):
                        messages.append(message)
                    time_5 = receiver._handler._counter.get_current_ms()
                    assert timedelta(seconds=1) < timedelta(milliseconds=(time_5 - time_4)) <= timedelta(seconds=4)

                    async for message in receiver:
                        messages.append(message)
                    time_6 = receiver._handler._counter.get_current_ms()
                    assert timedelta(seconds=3) < timedelta(milliseconds=(time_6 - time_5)) <= timedelta(seconds=6)

                    async for message in receiver._get_streaming_message_iter():
                        messages.append(message)
                    time_7 = receiver._handler._counter.get_current_ms()
                    assert timedelta(seconds=3) < timedelta(milliseconds=(time_7 - time_6)) <= timedelta(seconds=6)
                    assert len(messages) == 1

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_async_queue_send_twice(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("ServiceBusMessage")
                message2 = ServiceBusMessage("Message2")
                # first test batch message resending.
                batch_message = await sender.create_message_batch()
                batch_message._from_list([message, message2])  # pylint: disable=protected-access
                await sender.send_messages(batch_message)
                await sender.send_messages(batch_message)
                messages = []
                async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=20) as receiver:
                    async for message in receiver:
                        messages.append(message)
                        await receiver.complete_message(message)
                    assert len(messages) == 4
                # then normal message resending
                await sender.send_messages(message)
                await sender.send_messages(message)
                messages = []
                async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=20) as receiver:
                    async for message in receiver:
                        messages.append(message)
                        await receiver.complete_message(message)
                    assert len(messages) == 2

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_send_timeout(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async def _hack_amqp_sender_run_async(self, **kwargs):
            time.sleep(6)  # sleep until timeout
            try:
                await self._link.update_pending_deliveries()
                await self._connection.listen(wait=self._socket_timeout, **kwargs)
            except ValueError:
                self._shutdown = True
                return False
            return True

        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                # this one doesn't need to reset the method, as it's hacking the method on the instance
                sender._handler._client_run_async = types.MethodType(_hack_amqp_sender_run_async, sender._handler)
                with pytest.raises(OperationTimeoutError):
                    await sender.send_messages(ServiceBusMessage("body"), timeout=5)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_queue_mgmt_operation_timeout(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async def hack_mgmt_execute_async(self, message, operation=None, operation_type=None, timeout=0):
            start_time = time.time()
            operation_id = str(uuid.uuid4())
            self._responses[operation_id] = None
            self._mgmt_error = None

            await asyncio.sleep(6)  # sleep until timeout
            while not self._responses[operation_id] and not self._mgmt_error:
                if timeout and timeout > 0:
                    now = time.time()
                    if (now - start_time) >= timeout:
                        raise TimeoutError("Failed to receive mgmt response in {}ms".format(timeout))
                await self.connection.listen()
            if self._mgmt_error:
                self._responses.pop(operation_id)
                raise self._mgmt_error
            response = self._responses.pop(operation_id)
            return response

        original_execute_method = _management_operation_async.ManagementOperation.execute
        # hack the mgmt method on the class, not on an instance, so it needs reset
        try:
            _management_operation_async.ManagementOperation.execute = hack_mgmt_execute_async
            async with ServiceBusClient.from_connection_string(
                    servicebus_namespace_connection_string, logging_enable=False) as sb_client:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    with pytest.raises(OperationTimeoutError):
                        scheduled_time_utc = utc_now() + timedelta(seconds=30)
                        await sender.schedule_messages(ServiceBusMessage("ServiceBusMessage to be scheduled"), scheduled_time_utc, timeout=5)
        finally:
            # must reset the mgmt execute method, otherwise other test cases would use the hacked execute method, leading to timeout error
            _management_operation_async.ManagementOperation.execute = original_execute_method

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', lock_duration='PT10S')
    async def test_async_queue_operation_negative(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async def _hack_amqp_message_complete(cls, _, settlement):
            if settlement == 'completed':
                raise RuntimeError()

        async def _hack_amqp_mgmt_request(cls, message, operation, op_type=None, node=None, callback=None, **kwargs):
            raise error.AMQPConnectionError(error.ErrorCondition.ConnectionCloseForced)

        async def _hack_sb_receiver_settle_message(self, message, settle_operation, dead_letter_reason=None, dead_letter_error_description=None):
            raise error.AMQPException(error.ErrorCondition.ClientError)

        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10)
            original_settlement = ReceiveClientAsync.settle_messages_async
            try:
                async with sender, receiver:
                    # negative settlement via receiver link
                    await sender.send_messages(ServiceBusMessage("body"), timeout=5)
                    message = (await receiver.receive_messages(max_wait_time=10))[0]
                    ReceiveClientAsync.settle_messages_async = types.MethodType(_hack_amqp_message_complete, receiver._handler)
                    await receiver.complete_message(message)  # settle via mgmt link

                    origin_amqp_client_mgmt_request_method = AMQPClientAsync.mgmt_request_async
                    try:
                        AMQPClientAsync.mgmt_request_async = _hack_amqp_mgmt_request
                        with pytest.raises(ServiceBusConnectionError):
                            receiver._handler.mgmt_request_async = types.MethodType(_hack_amqp_mgmt_request, receiver._handler)
                            await receiver.peek_messages()
                    finally:
                        AMQPClientAsync.mgmt_request_async = origin_amqp_client_mgmt_request_method

                    await sender.send_messages(ServiceBusMessage("body"), timeout=5)

                    message = (await receiver.receive_messages(max_wait_time=10))[0]
                    origin_sb_receiver_settle_message_method = receiver._settle_message
                    receiver._settle_message = types.MethodType(_hack_sb_receiver_settle_message, receiver)
                    with pytest.raises(ServiceBusError):
                        await receiver.complete_message(message)

                    receiver._settle_message = origin_sb_receiver_settle_message_method
                    message = (await receiver.receive_messages(max_wait_time=10))[0]
                    await receiver.complete_message(message)
            finally:
                ReceiveClientAsync.settle_messages_async = original_settlement

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_async_send_message_no_body(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage(body=None))

            async with sb_client.get_queue_receiver(servicebus_queue.name,  
                                            max_wait_time=10) as receiver:
                message = await receiver.__anext__()
                assert message.body is None
                await receiver.complete_message(message)
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_async_queue_by_servicebus_client_enum_case_sensitivity(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        # Note: This test is currently intended to enforce case-sensitivity.  If we eventually upgrade to the Fancy Enums being used with new autorest,
        # we may want to tweak this.
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE.value, 
                                              max_wait_time=5) as receiver:
                pass
            with pytest.raises(ValueError):
                async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  receive_mode=str.upper(ServiceBusReceiveMode.RECEIVE_AND_DELETE.value),
                                                  max_wait_time=5) as receiver:
                    raise Exception("Should not get here, should be case sensitive.")
            async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              sub_queue=ServiceBusSubQueue.DEAD_LETTER.value,
                                              max_wait_time=5) as receiver:
                pass
            with pytest.raises(ValueError):
                async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  sub_queue=str.upper(ServiceBusSubQueue.DEAD_LETTER.value),
                                                  max_wait_time=5) as receiver:
                    raise Exception("Should not get here, should be case sensitive.")

    @pytest.mark.skip(reason="TODO: iterator support")            
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_queue_async_send_dict_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:

                message_dict = {"body": "Message"}
                message2_dict = {"body": "Message2"}
                list_message_dicts = [message_dict, message2_dict]

                # send single dict
                await sender.send_messages(message_dict)

                # send list of dicts
                await sender.send_messages(list_message_dicts)

                # create and send BatchMessage with dicts
                batch_message = await sender.create_message_batch()
                batch_message._from_list(list_message_dicts)  # pylint: disable=protected-access
                batch_message.add_message(message_dict)
                await sender.send_messages(batch_message)

                received_messages = []
                async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                    async for message in receiver:
                        received_messages.append(message)
                assert len(received_messages) == 6

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_queue_async_send_mapping_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        class MappingMessage(DictMixin):
            def __init__(self, content):
                self.body = content
                self.message_id = 'foo'
        
        class BadMappingMessage(DictMixin):
            def __init__(self):
                self.message_id = 'foo'

        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:

                message_dict = MappingMessage("Message")
                message2_dict = MappingMessage("Message2")
                message3_dict = BadMappingMessage()
                list_message_dicts = [message_dict, message2_dict]

                # send single dict
                await sender.send_messages(message_dict)

                # send list of dicts
                await sender.send_messages(list_message_dicts)

                # send bad dict
                with pytest.raises(TypeError):
                    await sender.send_messages(message3_dict)

                # create and send BatchMessage with dicts
                batch_message = await sender.create_message_batch()
                batch_message._from_list(list_message_dicts)  # pylint: disable=protected-access
                batch_message.add_message(message_dict)
                await sender.send_messages(batch_message)

                received_messages = []
                async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                    async for message in receiver:
                        received_messages.append(message)
                assert len(received_messages) == 6

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    async def test_queue_async_send_dict_messages_error_badly_formatted_dicts(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:

                message_dict = {"bad_key": "Message"}
                message2_dict = {"bad_key": "Message2"}
                list_message_dicts = [message_dict, message2_dict]

                # send single dict
                with pytest.raises(TypeError):
                    await sender.send_messages(message_dict)

                # send list of dicts
                with pytest.raises(TypeError):
                    await sender.send_messages(list_message_dicts)

                # create and send BatchMessage with dicts
                batch_message = await sender.create_message_batch()
                with pytest.raises(TypeError):
                    batch_message._from_list(list_message_dicts)  # pylint: disable=protected-access

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_queue_async_send_dict_messages_scheduled(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            content = "Test scheduled message"
            message_id = uuid.uuid4()
            message_id2 = uuid.uuid4()
            scheduled_enqueue_time = (utc_now() + timedelta(minutes=0.05)).replace(microsecond=0)
            message_dict = {"message_id": message_id, "body": content}
            message2_dict = {"message_id": message_id2, "body": content}
            list_message_dicts = [message_dict, message2_dict]
            
            # send single dict
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    tokens = await sender.schedule_messages(message_dict, scheduled_enqueue_time)
                    assert len(tokens) == 1
    
                messages = await receiver.receive_messages(max_wait_time=20)
                if messages:
                    try:
                        data = str(messages[0])
                        assert data == content
                        assert messages[0].message_id == message_id
                        assert messages[0].scheduled_enqueue_time_utc == scheduled_enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc <= messages[0].enqueued_time_utc.replace(microsecond=0)
                        assert len(messages) == 1
                    finally:
                        for m in messages:
                            await receiver.complete_message(m)
                else:
                    raise Exception("Failed to receive schdeduled message.")

            # send list of dicts
            async with sb_client.get_queue_receiver(servicebus_queue.name, prefetch_count=20) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    tokens = await sender.schedule_messages(list_message_dicts, scheduled_enqueue_time)
                    assert len(tokens) == 2
    
                messages = await receiver.receive_messages(max_wait_time=20)
                messages.extend(await receiver.receive_messages(max_wait_time=5))
                if messages:
                    try:
                        data = str(messages[0])
                        print(messages)
                        assert data == content
                        assert messages[0].message_id == message_id
                        assert messages[0].scheduled_enqueue_time_utc == scheduled_enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc <= messages[0].enqueued_time_utc.replace(microsecond=0)
                        assert len(messages) == 2
                    finally:
                        for m in messages:
                            await receiver.complete_message(m)
                else:
                    raise Exception("Failed to receive schdeduled message.")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_queue_async_send_dict_messages_scheduled_error_badly_formatted_dicts(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            content = "Test scheduled message"
            message_id = uuid.uuid4()
            message_id2 = uuid.uuid4()
            scheduled_enqueue_time = (utc_now() + timedelta(minutes=0.1)).replace(microsecond=0)
            async with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    message_dict = {"message_id": message_id, "bad_key": content}
                    message2_dict = {"message_id": message_id2, "bad_key": content}
                    list_message_dicts = [message_dict, message2_dict]
                    with pytest.raises(TypeError):
                        await sender.schedule_messages(message_dict, scheduled_enqueue_time)
                    with pytest.raises(TypeError):
                        await sender.schedule_messages(list_message_dicts, scheduled_enqueue_time)

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_queue_async_receive_iterator_resume_after_link_detach(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        async def hack_iter_next_mock_error(self):
            await self._open()
            # when trying to receive the second message (execution_times is 1), raising LinkDetach error to mock 10 mins idle timeout
            if self.execution_times == 1:
                from uamqp.errors import LinkDetach
                from uamqp.constants import ErrorCodes
                self.execution_times += 1
                self.error_raised = True
                raise LinkDetach(ErrorCodes.LinkDetachForced)
            else:
                self.execution_times += 1
            if not self._message_iter:
                self._message_iter = self._handler.receive_messages_iter_async()
            uamqp_message = await self._message_iter.__anext__()
            message = self._build_message(uamqp_message)
            return message

        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(
                    [ServiceBusMessage("test1"), ServiceBusMessage("test2"), ServiceBusMessage("test3")]
                )
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10) as receiver:
                receiver.execution_times = 0
                receiver.error_raised = False
                receiver._iter_next = types.MethodType(hack_iter_next_mock_error, receiver)
                res = []
                async for msg in receiver:
                    await receiver.complete_message(msg)
                    res.append(msg)
                assert len(res) == 3
                assert receiver.error_raised
                assert receiver.execution_times >= 4  # at least 1 failure and 3 successful receiving iterator

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_queue_async_send_amqp_annotated_message(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            sequence_body = [b'message', 123.456, True]
            footer = {'footer_key': 'footer_value'}
            prop = {"subject": "sequence"}
            seq_app_prop = {"body_type": "sequence"}

            sequence_message = AmqpAnnotatedMessage(
                sequence_body=sequence_body,
                footer=footer,
                properties=prop,
                application_properties=seq_app_prop
            )

            value_body = {b"key": [-123, b'data', False]}
            header = {"priority": 10}
            anno = {"ann_key": "ann_value"}
            value_app_prop = {"body_type": "value"}

            value_message = AmqpAnnotatedMessage(
                value_body=value_body,
                header=header,
                annotations=anno,
                application_properties=value_app_prop
            )

            data_body = [b'aa', b'bb', b'cc']
            data_app_prop = {"body_type": "data"}
            del_anno = {"delann_key": "delann_value"}
            data_message = AmqpAnnotatedMessage(
                data_body=data_body,
                delivery_annotations=del_anno,
                application_properties=data_app_prop
            )

            content = "normalmessage"
            dict_message = {"body": content}
            sb_message = ServiceBusMessage(body=content)
            message_with_ttl = AmqpAnnotatedMessage(data_body=data_body, header=AmqpMessageHeader(time_to_live=60000))
            uamqp_with_ttl = message_with_ttl._to_outgoing_amqp_message()
            assert uamqp_with_ttl.properties.absolute_expiry_time == uamqp_with_ttl.properties.creation_time + uamqp_with_ttl.header.time_to_live

            recv_data_msg = recv_sequence_msg = recv_value_msg = normal_msg = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    batch = await sender.create_message_batch()
                    batch.add_message(data_message)
                    batch.add_message(value_message)
                    batch.add_message(sequence_message)
                    batch.add_message(dict_message)
                    batch.add_message(sb_message)

                    await sender.send_messages(batch)
                    await sender.send_messages([data_message, value_message, sequence_message, dict_message, sb_message])
                    await sender.send_messages(data_message)
                    await sender.send_messages(value_message)
                    await sender.send_messages(sequence_message)

                    async for message in receiver:
                        raw_amqp_message = message.raw_amqp_message
                        if raw_amqp_message.body_type == AmqpMessageBodyType.DATA:
                            if raw_amqp_message.application_properties and raw_amqp_message.application_properties.get(b'body_type') == b'data':
                                body = [data for data in raw_amqp_message.body]
                                assert data_body == body
                                assert raw_amqp_message.delivery_annotations[b'delann_key'] == b'delann_value'
                                assert raw_amqp_message.application_properties[b'body_type'] == b'data'
                                recv_data_msg += 1
                            else:
                                assert str(message) == content
                                normal_msg += 1
                        elif raw_amqp_message.body_type == AmqpMessageBodyType.SEQUENCE:
                            body = [sequence for sequence in raw_amqp_message.body]
                            assert [sequence_body] == body
                            assert raw_amqp_message.footer[b'footer_key'] == b'footer_value'
                            assert raw_amqp_message.properties.subject == b'sequence'
                            assert raw_amqp_message.application_properties[b'body_type'] == b'sequence'
                            recv_sequence_msg += 1
                        elif raw_amqp_message.body_type == AmqpMessageBodyType.VALUE:
                            assert raw_amqp_message.body == value_body
                            assert raw_amqp_message.header.priority == 10
                            assert raw_amqp_message.annotations[b'ann_key'] == b'ann_value'
                            assert raw_amqp_message.application_properties[b'body_type'] == b'value'
                            recv_value_msg += 1
                        receiver.complete_message(message)

                    assert recv_data_msg == 3
                    assert recv_sequence_msg == 3
                    assert recv_value_msg == 3
                    assert normal_msg == 4


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_state_scheduled_async(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            async with sender:
                for i in range(10):
                    message = ServiceBusMessage("message no. {}".format(i))
                    scheduled_time_utc = datetime.utcnow() + timedelta(seconds=30)
                    sequence_number = await sender.schedule_messages(message, scheduled_time_utc)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name)
            async with receiver:
                messages = await receiver.peek_messages()
                for msg in messages:
                    assert msg.state == ServiceBusMessageState.SCHEDULED


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    async def test_state_deferred_async(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            async with sender:
                for i in range(10):
                    message = ServiceBusMessage("message no. {}".format(i))
                    await sender.send_messages(message)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name)
            deferred_messages = []
            async with receiver:
                received_msgs = await receiver.receive_messages()
                for message in received_msgs:
                    assert message.state == ServiceBusMessageState.ACTIVE
                    deferred_messages.append(message.sequence_number)
                    await receiver.defer_message(message)
                await asyncio.sleep(5)
                if deferred_messages:
                    received_deferred_msg = await receiver.receive_deferred_messages(
                        sequence_numbers=deferred_messages
                        )                
                for message in received_deferred_msg:
                    assert message.state == ServiceBusMessageState.DEFERRED
