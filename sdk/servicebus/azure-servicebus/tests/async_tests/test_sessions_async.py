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
from azure.servicebus import (
    ServiceBusMessage,
    ServiceBusReceivedMessage,
    ServiceBusReceiveMode,
    NEXT_AVAILABLE_SESSION,
    ServiceBusSubQueue
)
from azure.servicebus.aio import ServiceBusClient, AutoLockRenewer
from azure.servicebus._common.utils import utc_now
from azure.servicebus.exceptions import (
    ServiceBusConnectionError,
    ServiceBusAuthenticationError,
    ServiceBusError,
    OperationTimeoutError,
    SessionLockLostError,
    MessageLockLostError,
    MessageAlreadySettled,
    AutoLockRenewTimeout
)
from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    CachedServiceBusQueuePreparer,
    ServiceBusTopicPreparer,
    ServiceBusQueuePreparer,
    ServiceBusSubscriptionPreparer
)
from utilities import get_logger, print_message

_logger = get_logger(logging.DEBUG)


class ServiceBusAsyncSessionTests(AzureMgmtTestCase):
    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage("Handler message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            with pytest.raises(ServiceBusError):
                await sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10)._open_with_retry()

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=10)
            count = 0
            async for message in receiver:
                print_message(_logger, message)
                assert message.session_id == session_id
                count += 1
                await receiver.complete_message(message)

            await receiver.close()

            assert count == 3

            session_id = ""
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = ServiceBusMessage("Handler message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            with pytest.raises(ServiceBusError):
                await sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10)._open_with_retry()

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=10)
            count = 0
            async for message in receiver:
                print_message(_logger, message)
                assert message.session_id == session_id
                count += 1
                await receiver.complete_message(message)

            await receiver.close()

            assert count == 3

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True, lock_duration='PT10S')
    async def test_async_session_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            messages = []
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, max_wait_time=10)
            async for message in receiver:
                messages.append(message)
                assert session_id == receiver.session.session_id
                assert session_id == message.session_id
                with pytest.raises(ValueError):
                    await receiver.complete_message(message)

            assert receiver._running
            await receiver.close()

            assert not receiver._running
            assert len(messages) == 10
            time.sleep(10)

            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, max_wait_time=10) as receiver:
                async for message in receiver:
                    messages.append(message)
            assert len(messages) == 0

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage("Stop message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            messages = []
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5)
            async with receiver:
                async for message in receiver:
                    assert session_id == receiver.session.session_id
                    assert session_id == message.session_id
                    messages.append(message)
                    await receiver.complete_message(message)
                    if len(messages) >= 5:
                        break

                assert receiver._running
                assert len(messages) == 5

                async for message in receiver:
                    assert session_id == receiver.session.session_id
                    assert session_id == message.session_id
                    messages.append(message)
                    await receiver.complete_message(message)
                    if len(messages) >= 5:
                        break

            assert not receiver._running
            assert len(messages) == 6

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @pytest.mark.xfail(reason="'Cannot open log' error, potential service bug", raises=ServiceBusError)
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_session_client_conn_str_receive_handler_with_no_session(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION, max_wait_time=10)
            with pytest.raises(OperationTimeoutError):
                await receiver._open_with_retry()

    @pytest.mark.skip(reason="TODO: iterator support")
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
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, max_wait_time=5)
            async with receiver:
                async for message in receiver:
                    messages.append(message)

            assert not receiver._running
            assert len(messages) == 0

    @pytest.mark.skip(reason="TODO: iterator support")
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
                for message in [ServiceBusMessage("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]:
                    await sender.send_messages(message)

            count = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as receiver:
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)

            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as receiver:
                deferred = await receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    assert message.lock_token
                    assert not message.locked_until_utc
                    assert message._receiver
                    with pytest.raises(TypeError):
                        await receiver.renew_message_lock(message)
                    await receiver.complete_message(message)

    @pytest.mark.skip(reason="TODO: iterator support")
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
                for message in [ServiceBusMessage("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]:
                    await sender.send_messages(message)

            count = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as receiver:
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)

            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as receiver:
                deferred = await receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    await receiver.dead_letter_message(message, reason="Testing reason", error_description="Testing description")

            count = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                    sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                                                    max_wait_time=5) as receiver:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for message in [ServiceBusMessage("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]:
                    await sender.send_messages(message)

            count = 0
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as receiver:
                async for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    await receiver.defer_message(message)

            assert count == 10
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE) as receiver:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("Deferred message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5)
            count = 0
            async for message in receiver:
                deferred_messages.append(message.sequence_number)
                print_message(_logger, message)
                count += 1
                await receiver.defer_message(message)
            await receiver.close()

            assert count == 10

            with pytest.raises(ValueError):
                await receiver.complete_message(message)

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_fetch_next_with_retrieve_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5, prefetch_count=10) as receiver:

                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Dead lettered message no. {}".format(i), session_id=session_id)
                        await sender.send_messages(message)

                count = 0
                messages = await receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        await receiver.dead_letter_message(message, reason="Testing reason",
                                                           error_description="Testing description")
                        count += 1
                    messages = await receiver.receive_messages()
            assert count == 10

            async with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                    sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                                                    max_wait_time=5) as receiver:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_browse_messages_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)
            session_id_2 = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id_2)
                    await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = await receiver.peek_messages(5)
                assert len(messages) == 5
                assert all(isinstance(m, ServiceBusReceivedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(ValueError):
                        await receiver.complete_message(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id_2) as receiver:
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
            async with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, session_id=session_id) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id)
                        await sender.send_messages(message)

                messages = await receiver.peek_messages(5)
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_renew_client_locks(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            messages = []
            locks = 3
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, prefetch_count=10) as receiver:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(locks):
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id)
                        await sender.send_messages(message)

                messages.extend(await receiver.receive_messages())
                recv = True
                while recv:
                    recv = await receiver.receive_messages(max_wait_time=10)
                    messages.extend(recv)

                try:
                    for m in messages:
                        with pytest.raises(TypeError):
                            expired = m._lock_expired
                        assert m.locked_until_utc is None
                        assert m.lock_token is not None
                    time.sleep(5)
                    initial_expiry = receiver.session.locked_until_utc
                    await receiver.session.renew_lock(timeout=5)
                    assert (receiver.session.locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    await receiver.complete_message(messages[0])
                    await receiver.complete_message(messages[1])
                    time.sleep(40)
                    with pytest.raises(SessionLockLostError):
                        await receiver.complete_message(messages[2])

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True, lock_duration='PT5S')
    async def test_async_session_by_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            session_id = str(uuid.uuid4())

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            results = []
            async def lock_lost_callback(renewable, error):
                results.append(renewable)

            renewer = AutoLockRenewer()
            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=20) as receiver:
                renewer.register(receiver, receiver.session, max_lock_renewal_duration=10)
                print("Registered lock renew thread", receiver.session.locked_until_utc, utc_now())
                with pytest.raises(SessionLockLostError):
                    async for message in receiver:
                        if not messages:
                            await asyncio.sleep(10)
                            print("First sleep {}".format(receiver.session.locked_until_utc - utc_now()))
                            assert not receiver.session._lock_expired
                            with pytest.raises(TypeError):
                                message._lock_expired
                            assert message.locked_until_utc is None
                            with pytest.raises(TypeError):
                                await receiver.renew_message_lock(message)
                            assert message.lock_token is not None
                            await receiver.complete_message(message)
                            messages.append(message)

                        elif len(messages) == 1:
                            assert not results
                            await asyncio.sleep(10)
                            print("Second sleep {}".format(receiver.session.locked_until_utc - utc_now()))
                            assert receiver.session._lock_expired
                            assert isinstance(receiver.session.auto_renew_error, AutoLockRenewTimeout)
                            try:
                                await receiver.complete_message(message)
                                raise AssertionError("Didn't raise SessionLockExpired")
                            except SessionLockLostError as e:
                                assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                            messages.append(message)

            # While we're testing autolockrenew and sessions, let's make sure we don't call the lock-lost callback when a session exits.
            renewer._renew_period = 1
            session = None

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=10) as receiver:
                session = receiver.session
                renewer.register(receiver, session, max_lock_renewal_duration=5, on_lock_renew_failure=lock_lost_callback)
            await asyncio.sleep(max(0,(session.locked_until_utc - utc_now()).total_seconds()+1)) # If this pattern repeats make sleep_until_expired_async
            assert not results

            await renewer.close()
            assert len(messages) == 2

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True, lock_duration='PT10S')
    async def test_async_session_by_conn_str_receive_handler_with_auto_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            session_id = str(uuid.uuid4())

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            results = []
            async def lock_lost_callback(renewable, error):
                results.append(renewable)

            renewer = AutoLockRenewer(max_lock_renewal_duration=10)
            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name,
                                                    session_id=session_id,
                                                    max_wait_time=10,
                                                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                                    prefetch_count=20,
                                                    auto_lock_renewer=renewer) as session:
                print("Registered lock renew thread", session.session.locked_until_utc, utc_now())
                with pytest.raises(SessionLockLostError):
                    async for message in session:
                        if not messages:
                            await asyncio.sleep(10)
                            print("First sleep {}".format(session.session.locked_until_utc - utc_now()))
                            assert not session.session._lock_expired
                            with pytest.raises(TypeError):
                                message._lock_expired
                            assert message.locked_until_utc is None
                            with pytest.raises(TypeError):
                                await session.renew_message_lock(message)
                            assert message.lock_token is not None
                            await session.complete_message(message)
                            messages.append(message)

                        elif len(messages) == 1:
                            assert not results
                            await asyncio.sleep(10)
                            print("Second sleep {}".format(session.session.locked_until_utc - utc_now()))
                            assert session.session._lock_expired
                            assert isinstance(session.session.auto_renew_error, AutoLockRenewTimeout)
                            try:
                                await session.complete_message(message)
                                raise AssertionError("Didn't raise SessionLockExpired")
                            except SessionLockLostError as e:
                                assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                            messages.append(message)

            # While we're testing autolockrenew and sessions, let's make sure we don't call the lock-lost callback when a session exits.
            renewer._renew_period = 1
            session = None

            async with sb_client.get_queue_receiver(servicebus_queue.name,
                                                    session_id=session_id,
                                                    max_wait_time=10,
                                                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                                    prefetch_count=10,
                                                    auto_lock_renewer=renewer) as receiver:
                session = receiver.session
            await asyncio.sleep(max(0,(session.locked_until_utc - utc_now()).total_seconds()+1)) # If this pattern repeats make sleep_until_expired_async
            assert not results

            await renewer.close()
            assert len(messages) == 2

        session_id = str(uuid.uuid4())
        async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
            messages = [ServiceBusMessage("{}".format(i), session_id=session_id) for i in range(10)]
            await sender.send_messages(messages)

        renewer = AutoLockRenewer(max_lock_renewal_duration=100)
        receiver = sb_client.get_queue_receiver(servicebus_queue.name,
                                            session_id=session_id,
                                            max_wait_time=10,
                                            prefetch_count=10,
                                            auto_lock_renewer=renewer)

        async with receiver:
            received_msgs = await receiver.receive_messages(max_wait_time=10)
            for msg in received_msgs:
                await receiver.complete_message(msg)

        await receiver.close()
        assert not renewer._renewable(receiver._session)


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
                message = ServiceBusMessage("test")
                message.session_id = session_id
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1

            with pytest.raises(ValueError):
                await receiver.complete_message(messages[0])


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
                message = ServiceBusMessage("Testing expired messages")
                message.session_id = session_id
                await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                await asyncio.sleep(60) #TODO: Was 30, but then lock isn't expired.
                with pytest.raises(TypeError):
                    messages[0]._lock_expired
                with pytest.raises(TypeError):
                    await receiver.renew_message_lock(messages[0])
                assert receiver.session._lock_expired
                with pytest.raises(SessionLockLostError):
                    await receiver.complete_message(messages[0])
                with pytest.raises(SessionLockLostError):
                    await receiver.session.renew_lock()

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = await receiver.receive_messages(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                assert messages[0].delivery_count
                await receiver.complete_message(messages[0])

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
                message = ServiceBusMessage(content, session_id=session_id)
                message.message_id = message_id
                message.scheduled_enqueue_time_utc = enqueue_time
                await sender.send_messages(message)

            messages = []
            renewer = AutoLockRenewer()
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                renewer.register(receiver, receiver.session, max_lock_renewal_duration=140)
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
                message_a = ServiceBusMessage(content, session_id=session_id)
                message_a.message_id = message_id_a
                message_id_b = uuid.uuid4()
                message_b = ServiceBusMessage(content, session_id=session_id)
                message_b.message_id = message_id_b
                tokens = await sender.schedule_messages([message_a, message_b], enqueue_time)
                assert len(tokens) == 2

            renewer = AutoLockRenewer()
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, prefetch_count=20) as receiver:
                renewer.register(receiver, receiver.session, max_lock_renewal_duration=140)
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
                message_a = ServiceBusMessage("Test scheduled message", session_id=session_id)
                message_b = ServiceBusMessage("Test scheduled message", session_id=session_id)
                tokens = await sender.schedule_messages([message_a, message_b], enqueue_time)
                assert len(tokens) == 2
                await sender.cancel_scheduled_messages(tokens)

            renewer = AutoLockRenewer()
            messages = []
            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                renewer.register(receiver, receiver.session, max_lock_renewal_duration=140)
                messages.extend(await receiver.receive_messages(max_wait_time=115))
                messages.extend(await receiver.receive_messages(max_wait_time=10))
                try:
                    assert len(messages) == 0
                except AssertionError:
                    for message in messages:
                        print(str(message))
                        await receiver.complete_message(message)
                    raise
            await renewer.close()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_session_receiver_partially_invalid_autolockrenew_mode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        session_id = str(uuid.uuid4())
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("test_message", session_id=session_id))

            failures = 0
            async def should_not_run(*args, **kwargs):
                failures += 1

            async with sb_client.get_queue_receiver(servicebus_queue.name,
                                              session_id=session_id,
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                              auto_lock_renewer=AutoLockRenewer()) as receiver:
                assert receiver.receive_messages()
                assert not failures

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage("Handler message no. {}".format(i), session_id=session_id)
                    await sender.send_messages(message)

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=10) as receiver:
                assert await receiver.session.get_state(timeout=5) == None
                await receiver.session.set_state("first_state", timeout=5)
                count = 0
                async for m in receiver:
                    assert m.session_id == session_id
                    count += 1
                state = await receiver.session.get_state()
                assert state == b'first_state'
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
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session)
                        await sender.send_messages(message)
            for session in sessions:
                async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session) as receiver:
                    await receiver.session.set_state("SESSION {}".format(session))

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
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
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session)
                        await sender.send_messages(message)
            for session in sessions:
                async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session) as receiver:
                    await receiver.session.set_state("SESSION {}".format(session))

            current_sessions = await sb_client.list_sessions(updated_since=start_time)
            assert len(current_sessions) == 5
            assert current_sessions == sessions

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @pytest.mark.xfail(reason="'Cannot open log' error, potential service bug")
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_by_servicebus_client_session_pool(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        messages = []
        errors = []
        async def message_processing(sb_client):
            while True:
                try:
                    async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION, max_wait_time=5) as receiver:
                        async for message in receiver:
                            print("ServiceBusMessage: {}".format(message))
                            messages.append(message)
                            await receiver.complete_message(message)
                except OperationTimeoutError:
                    return
                except Exception as e:
                    errors.append(e)
                    raise

        concurrent_receivers = 5
        sessions = [str(uuid.uuid4()) for i in range(concurrent_receivers)]
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, retry_total=1) as sb_client:

            for session_id in sessions:
                async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    await asyncio.gather(*[sender.send_messages(ServiceBusMessage("Sample message no. {}".format(i), session_id=session_id)) for i in range(20)])

            receive_sessions = [message_processing(sb_client) for _ in range(concurrent_receivers)]
            await asyncio.gather(*receive_sessions, return_exceptions=True)

            assert not errors
            assert len(messages) == 100

    @pytest.mark.skip(reason="TODO: iterator support")
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
                message = ServiceBusMessage(b"Sample topic message", session_id='test_session')
                await sender.send_messages(message)

            async with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                session_id='test_session',
                max_wait_time=5
            ) as receiver:
                count = 0
                async for message in receiver:
                    count += 1
                    await receiver.complete_message(message)
            assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @pytest.mark.xfail(reason="'Cannot open log' error, potential service bug", raises=ServiceBusError)
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_connection_failure_is_idempotent(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        #Technically this validates for all senders/receivers, not just session, but since it uses session to generate a recoverable failure, putting it in here.
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, retry_total=1) as sb_client:
    
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
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION)
            with pytest.raises(OperationTimeoutError):
                await receiver._open_with_retry()

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("test session sender", session_id=session_id))

            async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION, max_wait_time=5) as receiver:
                messages = []
                async for message in receiver:
                    messages.append(message)
                assert len(messages) == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    async def test_async_session_non_session_send_to_session_queue_should_fail(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                with pytest.raises(ServiceBusError):
                    message = ServiceBusMessage("Handler message")
                    await sender.send_messages(message)