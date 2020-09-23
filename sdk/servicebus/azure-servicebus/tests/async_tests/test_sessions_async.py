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

from uamqp.errors import VendorLinkDetach
from azure.servicebus.aio import ServiceBusClient, ReceivedMessage, AutoLockRenew
from azure.servicebus._common.message import Message, PeekedMessage
from azure.servicebus._common.constants import ReceiveMode, NEXT_AVAILABLE, SubQueue
from azure.servicebus._common.utils import utc_now
from azure.servicebus.exceptions import (
    ServiceBusConnectionError,
    ServiceBusAuthenticationError,
    ServiceBusError,
    NoActiveSession,
    SessionLockExpired,
    MessageLockExpired,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSettleFailed)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusTopicPreparer,
    ServiceBusQueuePreparer,
    ServiceBusSubscriptionPreparer
)
from utilities import get_logger, print_message

_logger = get_logger(logging.DEBUG)


class ServiceBusAsyncSessionTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_peeklock(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = Message("Handler message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            with pytest.raises(ServiceBusConnectionError):
                await sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)._open_with_retry()

            session = sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5)
            count = 0
            async for message in session:
                print_message(_logger, message)
                assert message.session_id == session_id
                count += 1
                await message.complete()

            await session.close()

            assert count == 3


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Handler message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            messages = []
            session = sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, receive_mode=ReceiveMode.ReceiveAndDelete, max_wait_time=5)
            async for message in session:
                messages.append(message)
                assert session_id == session.session.session_id
                assert session_id == message.session_id
                with pytest.raises(MessageAlreadySettled):
                    await message.complete()

            assert session._running
            await session.close()

            assert not session._running
            assert len(messages) == 10
            time.sleep(30)

            messages = []
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, receive_mode=ReceiveMode.ReceiveAndDelete, max_wait_time=5) as session:
                async for message in session:
                    messages.append(message)
            assert len(messages) == 0


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_with_stop(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Stop message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            messages = []
            session = sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5)
            async with session:
                async for message in session:
                    assert session_id == session.session.session_id
                    assert session_id == message.session_id
                    messages.append(message)
                    await message.complete()
                    if len(messages) >= 5:
                        break

                assert session._running
                assert len(messages) == 5

            async with session:
                async for message in session:
                    assert session_id == session.session.session_id
                    assert session_id == message.session_id
                    messages.append(message)
                    await message.complete()
                    if len(messages) >= 5:
                        break

            assert not session._running
            assert len(messages) == 6


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_with_no_session(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session = sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE, max_wait_time=5)
            with pytest.raises(NoActiveSession):
                await session._open_with_retry()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_with_inactive_session(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            messages = []
            session = sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, receive_mode=ReceiveMode.ReceiveAndDelete, max_wait_time=5)
            async with session:
                async for message in session:
                    messages.append(message)

            assert not session._running
            assert len(messages) == 0


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for message in [Message("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]:
                    await sender.send_messages(message)

            count = 0
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as session:
                async for message in session:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()

            assert count == 10

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as session:
                deferred = await session.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    assert message.lock_token
                    assert not message.locked_until_utc
                    assert message._receiver
                    with pytest.raises(TypeError):
                        await message.renew_lock()
                    await message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for message in [Message("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]:
                    await sender.send_messages(message)

            count = 0
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as session:
                async for message in session:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()

            assert count == 10

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as session:
                deferred = await session.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    await message.dead_letter(reason="Testing reason", error_description="Testing description")

            count = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                    sub_queue = SubQueue.DeadLetter,
                                                    max_wait_time=5) as receiver:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for message in [Message("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]:
                    await sender.send_messages(message)

            count = 0
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as session:
                async for message in session:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await message.defer()

            assert count == 10
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5, receive_mode=ReceiveMode.ReceiveAndDelete) as session:
                deferred = await session.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    with pytest.raises(MessageAlreadySettled):
                        await message.complete()
                with pytest.raises(ServiceBusError):
                    deferred = await session.receive_deferred_messages(deferred_messages)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Deferred message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            session = sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5)
            count = 0
            async for message in session:
                deferred_messages.append(message.sequence_number)
                print_message(_logger, message)
                count += 1
                await message.defer()
            await session.close()

            assert count == 10

            with pytest.raises(MessageSettleFailed):
                await message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_fetch_next_with_retrieve_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5, prefetch_count=10) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Dead lettered message no. {}".format(i), session_id=session_id)
                        await sender.send_messages(message)

                count = 0
                messages = await receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        await message.dead_letter(reason="Testing reason", error_description="Testing description")
                        count += 1
                    messages = await receiver.receive_messages()
            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                    sub_queue = SubQueue.DeadLetter,
                                                    max_wait_time=5) as session:
                count = 0
                async for message in session:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_browse_messages_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = Message("Test message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)
            session_id_2 = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = Message("Test message no. {}".format(i), session_id=session_id_2)
                    await sender.send_messages(message)

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = await receiver.peek_messages(5)
                assert len(messages) == 5
                assert all(isinstance(m, PeekedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(AttributeError):
                        message.complete()

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id_2) as receiver:
                messages = await receiver.peek_messages(5)
                assert len(messages) == 3

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, max_wait_time=5, session_id=session_id) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = Message("Test message no. {}".format(i), session_id=session_id)
                        await sender.send_messages(message)

                messages = await receiver.peek_messages(5)
                assert len(messages) > 0
                assert all(isinstance(m, PeekedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(AttributeError):
                        message.complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_renew_client_locks(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            messages = []
            locks = 3
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, prefetch_count=10) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(locks):
                        message = Message("Test message no. {}".format(i), session_id=session_id)
                        await sender.send_messages(message)

                messages.extend(await receiver.receive_messages())
                recv = True
                while recv:
                    recv = await receiver.receive_messages(max_wait_time=5)
                    messages.extend(recv)

                try:
                    for m in messages:
                        with pytest.raises(TypeError):
                            expired = m._lock_expired
                        assert m.locked_until_utc is None
                        assert m.lock_token is not None
                    time.sleep(5)
                    initial_expiry = receiver.session.locked_until_utc
                    await receiver.session.renew_lock()
                    assert (receiver.session.locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    await messages[0].complete()
                    await messages[1].complete()
                    time.sleep(70) #TODO: BUG: Was 40
                    with pytest.raises(SessionLockExpired):
                        await messages[2].complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            session_id = str(uuid.uuid4())

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("{}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            results = []
            async def lock_lost_callback(renewable, error):
                results.append(renewable)

            renewer = AutoLockRenew()
            messages = []
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5, receive_mode=ReceiveMode.PeekLock, prefetch_count=20) as session:
                renewer.register(session.session, timeout=60)
                print("Registered lock renew thread", session.session.locked_until_utc, utc_now())
                with pytest.raises(SessionLockExpired):
                    async for message in session:
                        if not messages:
                            await asyncio.sleep(45)
                            print("First sleep {}".format(session.session.locked_until_utc - utc_now()))
                            assert not session.session._lock_expired
                            with pytest.raises(TypeError):
                                message._lock_expired
                            assert message.locked_until_utc is None
                            with pytest.raises(TypeError):
                                await message.renew_lock()
                            assert message.lock_token is not None
                            await message.complete()
                            messages.append(message)

                        elif len(messages) == 1:
                            assert not results
                            await asyncio.sleep(45)
                            print("Second sleep {}".format(session.session.locked_until_utc - utc_now()))
                            assert session.session._lock_expired
                            assert isinstance(session.session.auto_renew_error, AutoLockRenewTimeout)
                            try:
                                await message.complete()
                                raise AssertionError("Didn't raise SessionLockExpired")
                            except SessionLockExpired as e:
                                assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                            messages.append(message)

            # While we're testing autolockrenew and sessions, let's make sure we don't call the lock-lost callback when a session exits.
            renewer._renew_period = 1
            session = None

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5, receive_mode=ReceiveMode.PeekLock, prefetch_count=10) as receiver:
                session = receiver.session
                renewer.register(session, timeout=5, on_lock_renew_failure=lock_lost_callback)
            await asyncio.sleep(max(0,(session.locked_until_utc - utc_now()).total_seconds()+1)) # If this pattern repeats make sleep_until_expired_async
            assert not results

            await renewer.close()
            assert len(messages) == 2


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_message_connection_closed(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = Message("test")
                message.session_id = session_id
                await sender.send_messages(message)

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1

            with pytest.raises(MessageSettleFailed):
                await messages[0].complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_message_expiry(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = Message("Testing expired messages")
                message.session_id = session_id
                await sender.send_messages(message)

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                await asyncio.sleep(60) #TODO: Was 30, but then lock isn't expired.
                with pytest.raises(TypeError):
                    messages[0]._lock_expired
                with pytest.raises(TypeError):
                    await messages[0].renew_lock()
                assert receiver.session._lock_expired
                with pytest.raises(SessionLockExpired):
                    await messages[0].complete()
                with pytest.raises(SessionLockExpired):
                    await receiver.session.renew_lock()

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = await receiver.receive_messages(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                assert messages[0].delivery_count
                await messages[0].complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_schedule_message(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            import uuid
            session_id = str(uuid.uuid4())
            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message_id = uuid.uuid4()
                message = Message(content, session_id=session_id)
                message.message_id = message_id
                message.scheduled_enqueue_time_utc = enqueue_time
                await sender.send_messages(message)

            messages = []
            renewer = AutoLockRenew()
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                renewer.register(receiver.session, timeout=140)
                messages.extend(await receiver.receive_messages(max_wait_time=120))
                messages.extend(await receiver.receive_messages(max_wait_time=5))
                if messages:
                    data = str(messages[0])
                    assert data == content
                    assert messages[0].message_id == message_id
                    assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                    assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                    assert len(messages) == 1
                else:
                    raise Exception("Failed to receive schdeduled message.")
            await renewer.close()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_schedule_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            import uuid
            session_id = str(uuid.uuid4())
            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            messages = []
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message_id_a = uuid.uuid4()
                message_a = Message(content, session_id=session_id)
                message_a.message_id = message_id_a
                message_id_b = uuid.uuid4()
                message_b = Message(content, session_id=session_id)
                message_b.message_id = message_id_b
                tokens = await sender.schedule_messages([message_a, message_b], enqueue_time)
                assert len(tokens) == 2

            renewer = AutoLockRenew()
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, prefetch_count=20) as receiver:
                renewer.register(receiver.session, timeout=140)
                messages.extend(await receiver.receive_messages(max_wait_time=120))
                messages.extend(await receiver.receive_messages(max_wait_time=5))
                if messages:
                    data = str(messages[0])
                    assert data == content
                    assert messages[0].message_id in (message_id_a, message_id_b)
                    assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                    assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                    assert len(messages) == 2
                else:
                    raise Exception("Failed to receive schdeduled message.")
            await renewer.close()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_cancel_scheduled_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message_a = Message("Test scheduled message", session_id=session_id)
                message_b = Message("Test scheduled message", session_id=session_id)
                tokens = await sender.schedule_messages([message_a, message_b], enqueue_time)
                assert len(tokens) == 2
                await sender.cancel_scheduled_messages(tokens)

            renewer = AutoLockRenew()
            messages = []
            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                renewer.register(receiver.session, timeout=140)
                messages.extend(await receiver.receive_messages(max_wait_time=120))
                messages.extend(await receiver.receive_messages(max_wait_time=5))
                try:
                    assert len(messages) == 0
                except AssertionError:
                    for m in messages:
                        print(str(m))
                        await m.complete()
                    raise
            await renewer.close()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_get_set_state_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = Message("Handler message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as session:
                assert await session.session.get_state() == None
                await session.session.set_state("first_state")
                count = 0
                async for m in session:
                    assert m.session_id == session_id
                    count += 1
                await session.session.get_state()
            assert count == 3


    @pytest.mark.skip(reason='Requires list sessions')
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_list_sessions_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            sessions = []
            start_time = utc_now()
            for i in range(5):
                sessions.append(str(uuid.uuid4()))

            for session in sessions:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = Message("Test message no. {}".format(i), session_id=session)
                        await sender.send_messages(message)
            for session in sessions:
                async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session) as receiver:
                    await receiver.session.set_state("SESSION {}".format(session))

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE, max_wait_time=5, receive_mode=ReceiveMode.PeekLock) as receiver:
                current_sessions = await receiver.list_sessions(updated_since=start_time)
                assert len(current_sessions) == 5
                assert current_sessions == sessions


    @pytest.mark.skip(reason="requires list_session")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_list_sessions_with_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            sessions = []
            start_time = utc_now()
            for i in range(5):
                sessions.append(str(uuid.uuid4()))

            for session in sessions:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = Message("Test message no. {}".format(i), session_id=session)
                        await sender.send_messages(message)
            for session in sessions:
                async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=session) as receiver:
                    await receiver.session.set_state("SESSION {}".format(session))

            current_sessions = await sb_client.list_sessions(updated_since=start_time)
            assert len(current_sessions) == 5
            assert current_sessions == sessions


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_session_pool(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        messages = []
        errors = []
        async def message_processing(sb_client):
            while True:
                try:
                    async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE, max_wait_time=5) as session:
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
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            for session_id in sessions:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    await asyncio.gather(*[sender.send_messages(Message("Sample message no. {}".format(i), session_id=session_id)) for i in range(20)])

            receive_sessions = [message_processing(sb_client) for _ in range(concurrent_receivers)]
            await asyncio.gather(*receive_sessions, return_exceptions=True)

            assert not errors
            assert len(messages) == 100

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_basic_topic_subscription_send_and_receive(self, servicebus_namespace_connection_string, servicebus_topic, servicebus_subscription, **kwargs):
        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False
        ) as sb_client:
            async with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = Message(b"Sample topic message", session_id='test_session')
                await sender.send_messages(message)

            async with sb_client.get_subscription_session_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                session_id='test_session',
                max_wait_time=5
            ) as receiver:
                count = 0
                async for message in receiver:
                    count += 1
                    await message.complete()
            assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_connection_failure_is_idempotent(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        #Technically this validates for all senders/receivers, not just session, but since it uses session to generate a recoverable failure, putting it in here.
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            # First let's just try the naive failure cases.
            receiver = sb_client.get_queue_receiver("THIS_IS_WRONG_ON_PURPOSE")
            with pytest.raises(ServiceBusAuthenticationError):
                await receiver._open_with_retry()
            assert not receiver._running
            assert not receiver._handler
    
            sender = sb_client.get_queue_sender("THIS_IS_WRONG_ON_PURPOSE")
            with pytest.raises(ServiceBusAuthenticationError):
                await sender._open_with_retry()
            assert not receiver._running
            assert not receiver._handler

            # Then let's try a case we can recover from to make sure everything works on reestablishment.
            receiver = sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE)
            with pytest.raises(NoActiveSession):
                await receiver._open_with_retry()

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(Message("test session sender", session_id=session_id))

            async with sb_client.get_queue_session_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE, max_wait_time=5) as receiver:
                messages = []
                async for message in receiver:
                    messages.append(message)
                assert len(messages) == 1