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

from azure.servicebus.aio import ServiceBusClient, QueueClient, Message, DeferredMessage, AutoLockRenew
from azure.servicebus.common.message import PeekMessage
from azure.servicebus.common.constants import ReceiveSettleMode, NEXT_AVAILABLE
from azure.servicebus.common.errors import (
    ServiceBusError,
    NoActiveSession,
    SessionLockExpired,
    MessageLockExpired,
    InvalidHandlerState,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSettleFailed)
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer, CachedResourceGroupPreparer
from servicebus_preparer import ServiceBusNamespacePreparer, ServiceBusTopicPreparer, ServiceBusQueuePreparer, CachedServiceBusNamespacePreparer


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
    _logger.debug("Enqueue Sequence numger: {}".format(message.enqueue_sequence_number))
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


class ServiceBusAsyncSessionTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_peeklock(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)
        queue_client.get_properties()

        session_id = str(uuid.uuid4())
        async with queue_client.get_sender(session=session_id) as sender:
            for i in range(3):
                message = Message("Handler message no. {}".format(i))
                await sender.send(message)

        with pytest.raises(ValueError):
            session = queue_client.get_receiver(idle_timeout=5)

        session = queue_client.get_receiver(session=session_id, idle_timeout=5)
        count = 0
        async for message in session:
            print_message(message)
            assert message.session_id == session_id
            count += 1
            await message.complete()

        assert count == 3


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)
        queue_client.get_properties()

        session_id = str(uuid.uuid4())
        async with queue_client.get_sender(session=session_id) as sender:
            for i in range(10):
                message = Message("Handler message no. {}".format(i))
                await sender.send(message)

        messages = []
        session = queue_client.get_receiver(session=session_id, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
        async for message in session:
            messages.append(message)
            assert session_id == session.session_id
            assert session_id == message.session_id
            with pytest.raises(MessageAlreadySettled):
                await message.complete()

        assert not session.running
        assert len(messages) == 10
        time.sleep(30)

        messages = []
        session = queue_client.get_receiver(session=session_id, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
        async for message in session:
            messages.append(message)
        assert len(messages) == 0


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_with_stop(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)

        session_id = str(uuid.uuid4())
        async with queue_client.get_sender(session=session_id) as sender:
            for i in range(10):
                message = Message("Stop message no. {}".format(i))
                await sender.send(message)

        messages = []
        session = queue_client.get_receiver(session=session_id, idle_timeout=5)
        async for message in session:
            assert session_id == session.session_id
            assert session_id == message.session_id
            messages.append(message)
            await message.complete()
            if len(messages) >= 5:
                break

        assert session.running
        assert len(messages) == 5

        async with session:
            async for message in session:
                assert session_id == session.session_id
                assert session_id == message.session_id
                messages.append(message)
                await message.complete()
                if len(messages) >= 5:
                    break

        assert not session.running
        assert len(messages) == 6


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_with_no_session(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)

        session = queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5)
        with pytest.raises(NoActiveSession):
            await session.open()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_with_inactive_session(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)

        session_id = str(uuid.uuid4())
        messages = []
        session = queue_client.get_receiver(session=session_id, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
        async for message in session:
            messages.append(message)

        assert not session.running
        assert len(messages) == 0


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        session_id = str(uuid.uuid4())
        messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
        results = await queue_client.send(messages, session=session_id)
        assert all(result[0] for result in results)

        count = 0
        session = queue_client.get_receiver(session=session_id, idle_timeout=5)
        async for message in session:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            await message.defer()

        assert count == 10

        async with queue_client.get_receiver(session=session_id, idle_timeout=5) as session:
            deferred = await session.receive_deferred_messages(deferred_messages)
            assert len(deferred) == 10
            for message in deferred:
                assert isinstance(message, DeferredMessage)
                assert message.lock_token
                assert not message.locked_until
                assert message._receiver
                with pytest.raises(TypeError):
                    await message.renew_lock()
                await message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        session_id = str(uuid.uuid4())
        messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
        results = await queue_client.send(messages, session=session_id)
        assert all(result[0] for result in results)

        count = 0
        session = queue_client.get_receiver(session=session_id, idle_timeout=5)
        async for message in session:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            await message.defer()

        assert count == 10

        async with queue_client.get_receiver(session=session_id, idle_timeout=5) as session:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        session_id = str(uuid.uuid4())
        messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
        results = await queue_client.send(messages, session=session_id)
        assert all(result[0] for result in results)

        count = 0
        session = queue_client.get_receiver(session=session_id, idle_timeout=5)
        async for message in session:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            await message.defer()

        assert count == 10
        async with queue_client.get_receiver(session=session_id, idle_timeout=5) as session:
            deferred = await session.receive_deferred_messages(deferred_messages, mode=ReceiveSettleMode.ReceiveAndDelete)
            assert len(deferred) == 10
            for message in deferred:
                assert isinstance(message, DeferredMessage)
                with pytest.raises(MessageAlreadySettled):
                    await message.complete()
            with pytest.raises(ServiceBusError):
                deferred = await session.receive_deferred_messages(deferred_messages)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        deferred_messages = []
        session_id = str(uuid.uuid4())
        async with queue_client.get_sender(session=session_id) as sender:
            for i in range(10):
                message = Message("Deferred message no. {}".format(i))
                await sender.send(message)

        session = queue_client.get_receiver(session=session_id, idle_timeout=5)
        count = 0
        async for message in session:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            await message.defer()

        assert count == 10

        with pytest.raises(ValueError):
            deferred = await queue_client.receive_deferred_messages(deferred_messages, session=session_id)

        with pytest.raises(ValueError):
            await queue_client.settle_deferred_messages("completed", [message], session=session_id)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_fetch_next_with_retrieve_deadletter(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        session_id = str(uuid.uuid4())
        async with queue_client.get_receiver(session=session_id, idle_timeout=5, prefetch=10) as receiver:

            async with queue_client.get_sender(session=session_id) as sender:
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
        assert count == 10

        async with queue_client.get_deadletter_receiver(idle_timeout=5) as session:
            count = 0
            async for message in session:
                print_message(message)
                #assert message.user_properties[b'DeadLetterReason'] == b'something'  # TODO
                #assert message.user_properties[b'DeadLetterErrorDescription'] == b'something'  # TODO
                await message.complete()
                count += 1
        assert count == 10


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_browse_messages_client(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        session_id = str(uuid.uuid4())
        async with queue_client.get_sender(session=session_id) as sender:
            for i in range(5):
                message = Message("Test message no. {}".format(i))
                await sender.send(message)

        with pytest.raises(ValueError):
            messages = await queue_client.peek(5)

        messages = await queue_client.peek(5, session=session_id)
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        session_id = str(uuid.uuid4())
        async with queue_client.get_receiver(idle_timeout=5, session=session_id) as receiver:
            async with queue_client.get_sender(session=session_id) as sender:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_renew_client_locks(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        session_id = str(uuid.uuid4())
        messages = []
        locks = 3
        async with queue_client.get_receiver(session=session_id, prefetch=10) as receiver:
            async with queue_client.get_sender(session=session_id) as sender:
                for i in range(locks):
                    message = Message("Test message no. {}".format(i))
                    await sender.send(message)

            messages.extend(await receiver.fetch_next())
            recv = True
            while recv:
                recv = await receiver.fetch_next(timeout=5)
                messages.extend(recv)

            try:
                for m in messages:
                    with pytest.raises(TypeError):
                        expired = m.expired
                    assert m.locked_until is None
                    assert m.lock_token is None
                time.sleep(5)
                initial_expiry = receiver.locked_until
                await receiver.renew_lock()
                assert (receiver.locked_until - initial_expiry) >= timedelta(seconds=5)
            finally:
                await messages[0].complete()
                await messages[1].complete()
                time.sleep(40)
                with pytest.raises(SessionLockExpired):
                    await messages[2].complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        session_id = str(uuid.uuid4())
        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)

        async with queue_client.get_sender(session=session_id) as sender:
            for i in range(10):
                message = Message("{}".format(i))
                await sender.send(message)

        renewer = AutoLockRenew()
        messages = []
        async with queue_client.get_receiver(session=session_id, idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=20) as session:
            renewer.register(session, timeout=60)
            print("Registered lock renew thread", session.locked_until, datetime.now())
            with pytest.raises(SessionLockExpired):
                async for message in session:
                    if not messages:
                        await asyncio.sleep(45)
                        print("First sleep {}".format(session.locked_until - datetime.now()))
                        assert not session.expired
                        with pytest.raises(TypeError):
                            message.expired
                        assert message.locked_until is None
                        with pytest.raises(TypeError):
                            await message.renew_lock()
                        assert message.lock_token is None
                        await message.complete()
                        messages.append(message)

                    elif len(messages) == 1:
                        await asyncio.sleep(45)
                        print("Second sleep {}".format(session.locked_until - datetime.now()))
                        assert session.expired
                        assert isinstance(session.auto_renew_error, AutoLockRenewTimeout)
                        try:
                            await message.complete()
                            raise AssertionError("Didn't raise SessionLockExpired")
                        except SessionLockExpired as e:
                            assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                        messages.append(message)

        await renewer.shutdown()
        assert len(messages) == 2


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_message_connection_closed(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        session_id = str(uuid.uuid4())
        queue_client = client.get_queue(servicebus_queue.name)

        async with queue_client.get_sender() as sender:
            message = Message("test")
            message.session_id = session_id
            await sender.send(message)

        async with queue_client.get_receiver(session=session_id) as receiver:
            messages = await receiver.fetch_next(timeout=10)
            assert len(messages) == 1

        with pytest.raises(MessageSettleFailed):
            await messages[0].complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_message_expiry(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        session_id = str(uuid.uuid4())
        queue_client = client.get_queue(servicebus_queue.name)

        async with queue_client.get_sender() as sender:
            message = Message("Testing expired messages")
            message.session_id = session_id
            await sender.send(message)

        async with queue_client.get_receiver(session=session_id) as receiver:
            messages = await receiver.fetch_next(timeout=10)
            assert len(messages) == 1
            print_message(messages[0])
            await asyncio.sleep(30)
            with pytest.raises(TypeError):
                messages[0].expired
            with pytest.raises(TypeError):
                await messages[0].renew_lock()
            assert receiver.expired
            with pytest.raises(SessionLockExpired):
                await messages[0].complete()
            with pytest.raises(SessionLockExpired):
                await receiver.renew_lock()

        async with queue_client.get_receiver(session=session_id) as receiver:
            messages = await receiver.fetch_next(timeout=30)
            assert len(messages) == 1
            print_message(messages[0])
            #assert messages[0].header.delivery_count  # TODO confirm this with service
            await messages[0].complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_schedule_message(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        session_id = str(uuid.uuid4())
        queue_client = client.get_queue(servicebus_queue.name)
        enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
        async with queue_client.get_sender(session=session_id) as sender:
            content = str(uuid.uuid4())
            message_id = uuid.uuid4()
            message = Message(content)
            message.properties.message_id = message_id
            message.schedule(enqueue_time)
            await sender.send(message)

        messages = []
        renewer = AutoLockRenew()
        async with queue_client.get_receiver(session=session_id) as receiver:
            renewer.register(receiver, timeout=140)
            messages.extend(await receiver.fetch_next(timeout=120))
            messages.extend(await receiver.fetch_next(timeout=5))
            if messages:
                data = str(messages[0])
                assert data == content
                assert messages[0].properties.message_id == message_id
                assert messages[0].scheduled_enqueue_time == enqueue_time
                assert messages[0].scheduled_enqueue_time == messages[0].enqueued_time.replace(microsecond=0)
                assert len(messages) == 1
            else:
                raise Exception("Failed to receive schdeduled message.")
        await renewer.shutdown()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_schedule_multiple_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)
        import uuid
        session_id = str(uuid.uuid4())
        queue_client = client.get_queue(servicebus_queue.name)
        enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
        messages = []
        async with queue_client.get_sender(session=session_id) as sender:
            content = str(uuid.uuid4())
            message_id_a = uuid.uuid4()
            message_a = Message(content)
            message_a.properties.message_id = message_id_a
            message_id_b = uuid.uuid4()
            message_b = Message(content)
            message_b.properties.message_id = message_id_b
            tokens = await sender.schedule(enqueue_time, message_a, message_b)
            assert len(tokens) == 2

        renewer = AutoLockRenew()
        async with queue_client.get_receiver(session=session_id, prefetch=20) as receiver:
            renewer.register(receiver, timeout=140)
            messages.extend(await receiver.fetch_next(timeout=120))
            messages.extend(await receiver.fetch_next(timeout=5))
            if messages:
                data = str(messages[0])
                assert data == content
                assert messages[0].properties.message_id in (message_id_a, message_id_b)
                assert messages[0].scheduled_enqueue_time == enqueue_time
                assert messages[0].scheduled_enqueue_time == messages[0].enqueued_time.replace(microsecond=0)
                assert len(messages) == 2
            else:
                raise Exception("Failed to receive schdeduled message.")
        await renewer.shutdown()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_cancel_scheduled_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        session_id = str(uuid.uuid4())
        queue_client = client.get_queue(servicebus_queue.name)
        enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
        async with queue_client.get_sender(session=session_id) as sender:
            message_a = Message("Test scheduled message")
            message_b = Message("Test scheduled message")
            tokens = await sender.schedule(enqueue_time, message_a, message_b)
            assert len(tokens) == 2
            await sender.cancel_scheduled_messages(*tokens)

        renewer = AutoLockRenew()
        messages = []
        async with queue_client.get_receiver(session=session_id) as receiver:
            renewer.register(receiver, timeout=140)
            messages.extend(await receiver.fetch_next(timeout=120))
            messages.extend(await receiver.fetch_next(timeout=5))
            try:
                assert len(messages) == 0
            except AssertionError:
                for m in messages:
                    print(str(m))
                    await m.complete()
                raise
        await renewer.shutdown()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_get_set_state_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        queue_client = QueueClient.from_connection_string(
            servicebus_namespace_connection_string,
            name=servicebus_queue.name,
            debug=False)

        session_id = str(uuid.uuid4())
        queue_client.get_properties()
        async with queue_client.get_sender(session=session_id) as sender:
            for i in range(3):
                message = Message("Handler message no. {}".format(i))
                await sender.send(message)

        async with queue_client.get_receiver(session=session_id, idle_timeout=5) as session:
            assert await session.get_session_state() == None
            await session.set_session_state("first_state")
            count = 0
            async for m in session:
                assert m.properties.group_id == session_id.encode('utf-8')
                count += 1
            with pytest.raises(InvalidHandlerState):
                await session.get_session_state()
        assert count == 3


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_list_sessions_with_receiver(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        sessions = []
        start_time = datetime.now()
        for i in range(5):
            sessions.append(str(uuid.uuid4()))

        for session in sessions:
            async with queue_client.get_sender(session=session) as sender:
                for i in range(5):
                    message = Message("Test message no. {}".format(i))
                    await sender.send(message)
        for session in sessions:
            async with queue_client.get_receiver(session=session) as receiver:
                await receiver.set_session_state("SESSION {}".format(session))

        async with queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            current_sessions = await receiver.list_sessions(updated_since=start_time)
            assert len(current_sessions) == 5
            assert current_sessions == sessions


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_list_sessions_with_client(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        sessions = []
        start_time = datetime.now()
        for i in range(5):
            sessions.append(str(uuid.uuid4()))

        for session in sessions:
            async with queue_client.get_sender(session=session) as sender:
                for i in range(5):
                    message = Message("Test message no. {}".format(i))
                    await sender.send(message)
        for session in sessions:
            async with queue_client.get_receiver(session=session) as receiver:
                await receiver.set_session_state("SESSION {}".format(session))

        current_sessions = await queue_client.list_sessions(updated_since=start_time)
        assert len(current_sessions) == 5
        assert current_sessions == sessions


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_session_pool(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        
        messages = []
        errors = []
        async def message_processing(queue_client):
            while True:
                try:
                    async with queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5) as session:
                        async for message in session:
                            print("Message: {}".format(message))
                            messages.append(message)
                            await message.complete()
                except NoActiveSession:
                    return
                except Exception as e:
                    errors.append(e)
                    raise

        concurrent_receivers = 5
        sessions = [str(uuid.uuid4()) for i in range(concurrent_receivers)]
        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        queue_client = client.get_queue(servicebus_queue.name)
        for session_id in sessions:
            async with queue_client.get_sender(session=session_id) as sender:
                await asyncio.gather(*[sender.send(Message("Sample message no. {}".format(i))) for i in range(20)])

        receive_sessions = [message_processing(queue_client) for _ in range(concurrent_receivers)]
        await asyncio.gather(*receive_sessions, return_exceptions=True)

        assert not errors
        assert len(messages) == 100