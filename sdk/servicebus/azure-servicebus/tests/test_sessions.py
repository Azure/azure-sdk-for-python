#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import concurrent
import sys
import os
import pytest
import time
import uuid
from datetime import datetime, timedelta

from azure.servicebus import ServiceBusClient, AutoLockRenew
from azure.servicebus._common.message import Message, PeekMessage, ReceivedMessage
from azure.servicebus._common.constants import ReceiveSettleMode, NEXT_AVAILABLE
from azure.servicebus._common.utils import utc_now
from azure.servicebus.exceptions import (
    ServiceBusConnectionError,
    ServiceBusError,
    NoActiveSession,
    SessionLockExpired,
    MessageLockExpired,
    InvalidHandlerState,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSettleFailed)

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, ServiceBusTopicPreparer, ServiceBusQueuePreparer
from utilities import get_logger, print_message

_logger = get_logger(logging.DEBUG)


class ServiceBusSessionTests(AzureMgmtTestCase):
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_session_client_conn_str_receive_handler_peeklock(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = Message("Handler message no. {}".format(i), session_id=session_id)
                    sender.send(message)

            with pytest.raises(ServiceBusConnectionError):
                session = sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5)._open_with_retry()

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, idle_timeout=5) as session:
                count = 0
                for message in session:
                    print_message(_logger, message)
                    assert message.session_id == session_id
                    count += 1
                    message.complete()

                assert count == 3

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Handler message no. {}".format(i), session_id=session_id)
                    sender.send(message)

            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              mode=ReceiveSettleMode.ReceiveAndDelete, 
                                              idle_timeout=5) as session:
                for message in session:
                    messages.append(message)
                    assert session_id == session._session_id
                    assert session_id == message.session_id
                    with pytest.raises(MessageAlreadySettled):
                        message.complete()

            assert not session._running
            assert len(messages) == 10
            time.sleep(30)

            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5) as session:
                for message in session:
                    messages.append(message)
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_session_client_conn_str_receive_handler_with_stop(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Stop message no. {}".format(i), session_id=session_id)
                    sender.send(message)

            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, idle_timeout=5) as session:
                for message in session:
                    assert session_id == session._session_id 
                    assert session_id == message.session_id
                    messages.append(message)
                    message.complete()
                    if len(messages) >= 5:
                        break

                assert session._running
                assert len(messages) == 5

                with session:
                    for message in session:
                        assert session_id == session._session_id
                        assert session_id == message.session_id
                        messages.append(message)
                        message.complete()
                        if len(messages) >= 5:
                            break

                assert not session._running
                assert len(messages) == 6

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_session_client_conn_str_receive_handler_with_no_session(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            with pytest.raises(NoActiveSession):
                with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  session_id=NEXT_AVAILABLE, 
                                                  idle_timeout=5) as session:
                        session.open()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_session_client_conn_str_receive_handler_with_inactive_session(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              mode=ReceiveSettleMode.ReceiveAndDelete, 
                                              idle_timeout=5) as session:
                for message in session:
                    messages.append(message)

                assert not session._running
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                deferred_messages = []
                session_id = str(uuid.uuid4())
                for i in range(10):
                    message = Message("Deferred message no. {}".format(i), session_id=session_id)
                    sender.send(message)

            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              idle_timeout=5) as session:
                for message in session:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()

            assert count == 10

            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              idle_timeout=5) as session:
                deferred = session.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    assert message.lock_token
                    assert not message.locked_until_utc
                    assert message._receiver
                    with pytest.raises(TypeError):
                        message.renew_lock()
                    message.complete()

    @pytest.mark.skip(reason='Requires deadletter receiver')
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                deferred_messages = []
                session_id = str(uuid.uuid4())
                messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
                results = sender.send(messages, session_id=session_id)
                assert all(result[0] for result in results)

            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              idle_timeout=5) as session:
                for message in session:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()

                assert count == 10

            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              idle_timeout=5) as session:
                deferred = session.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    message.dead_letter(reason="Testing reason", description="Testing description")

            count = 0
            with sb_client.get_deadletter_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                for message in receiver:
                    count += 1
                    print_message(_logger, message)
                    assert message.user_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.user_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    message.complete()
            assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                deferred_messages = []
                session_id = str(uuid.uuid4())
                messages = [Message("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]
                for message in messages:
                    sender.send(message)

            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, idle_timeout=5) as session:
                for message in session:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()

            assert count == 10
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              idle_timeout=5,
                                              mode=ReceiveSettleMode.ReceiveAndDelete) as session:
                deferred = session.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    with pytest.raises(MessageAlreadySettled):
                        message.complete()
                with pytest.raises(ServiceBusError):
                    deferred = session.receive_deferred_messages(deferred_messages)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Deferred message no. {}".format(i), session_id=session_id)
                    sender.send(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, idle_timeout=5) as session:
                count = 0
                for message in session:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()

                assert count == 10

                deferred = session.receive_deferred_messages(deferred_messages)

                with pytest.raises(MessageAlreadySettled):
                    message.complete()


    @pytest.mark.skip(reason='Requires deadletter receiver')
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_receive_with_retrieve_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              idle_timeout=5, 
                                              prefetch=10) as receiver:

                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Dead lettered message no. {}".format(i), session_id=session_id)
                        sender.send(message)

                count = 0
                messages = receiver.receive()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        message.dead_letter(reason="Testing reason", description="Testing description")
                        count += 1
                    messages = receiver.receive()
            assert count == 10

            with sb_client.get_deadletter_receiver(servicebus_queue.name, 
                                                      idle_timeout=5) as session:
                count = 0
                for message in session:
                    print_message(_logger, message)
                    message.complete()
                    #assert message.user_properties[b'DeadLetterReason'] == b'something'  # TODO
                    #assert message.user_properties[b'DeadLetterErrorDescription'] == b'something'  # TODO
                    count += 1
            assert count == 10


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_browse_messages_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = Message("Test message no. {}".format(i), session_id=session_id)
                    sender.send(message)

            with pytest.raises(ServiceBusConnectionError):
                with sb_client.get_queue_receiver(servicebus_queue.name):
                    messages = sb_client.peek(5)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = receiver.peek(5)
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, session_id=session_id) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = Message("Test message no. {}".format(i), session_id=session_id)
                        sender.send(message)

                messages = receiver.peek(5)
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_renew_client_locks(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            messages = []
            locks = 3
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, prefetch=10) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(locks):
                        message = Message("Test message no. {}".format(i), session_id=session_id)
                        sender.send(message)

                messages.extend(receiver.receive())
                recv = True
                while recv:
                    recv = receiver.receive(max_wait_time=5)
                    messages.extend(recv)

                try:
                    for m in messages:
                        with pytest.raises(TypeError):
                            expired = m.expired
                        assert m.locked_until_utc is None
                        assert m.lock_token is not None
                    time.sleep(5)
                    initial_expiry = receiver.session._locked_until_utc
                    receiver.session.renew_lock()
                    assert (receiver.session._locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    messages[0].complete()
                    messages[1].complete()

                    # This magic number is because of a 30 second lock renewal window.  Chose 31 seconds because at 30, you'll see "off by .05 seconds" flaky failures
                    # potentially as a side effect of network delays/sleeps/"typical distributed systems nonsense."  In a perfect world we wouldn't have a magic number/network hop but this allows
                    # a slightly more robust test in absence of that.
                    assert (receiver.session._locked_until_utc - utc_now()) <= timedelta(seconds=60)
                    time.sleep((receiver.session._locked_until_utc - utc_now()).total_seconds())
                    with pytest.raises(SessionLockExpired):
                        messages[2].complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        session_id = str(uuid.uuid4())
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("{}".format(i), session_id=session_id)
                    sender.send(message)

            renewer = AutoLockRenew()
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
                renewer.register(receiver.session, timeout=60)
                print("Registered lock renew thread", receiver.session._locked_until_utc, utc_now())
                with pytest.raises(SessionLockExpired):
                    for message in receiver:
                        if not messages:
                            print("Starting first sleep")
                            time.sleep(40)
                            print("First sleep {}".format(receiver.session._locked_until_utc - utc_now()))
                            assert not receiver.session.expired
                            with pytest.raises(TypeError):
                                message.expired
                            assert message.locked_until_utc is None
                            with pytest.raises(TypeError):
                                message.renew_lock()
                            assert message.lock_token is not None
                            message.complete()
                            messages.append(message)

                        elif len(messages) == 1:
                            print("Starting second sleep")
                            time.sleep(40)
                            print("Second sleep {}".format(receiver.session._locked_until_utc - utc_now()))
                            assert receiver.session.expired
                            assert isinstance(receiver.session.auto_renew_error, AutoLockRenewTimeout)
                            try:
                                message.complete()
                                raise AssertionError("Didn't raise SessionLockExpired")
                            except SessionLockExpired as e:
                                assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                            messages.append(message)

            renewer.shutdown()
            assert len(messages) == 2


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_message_connection_closed(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = Message("test")
                message.session_id = session_id
                sender.send(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = receiver.receive(max_wait_time=10)
                assert len(messages) == 1

            with pytest.raises(MessageSettleFailed):
                messages[0].complete()


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_message_expiry(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            session_id = str(uuid.uuid4())

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = Message("Testing expired messages")
                message.session_id = session_id
                sender.send(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = receiver.receive(max_wait_time=10)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                time.sleep(60)
                with pytest.raises(TypeError):
                    messages[0].expired
                with pytest.raises(TypeError):
                    messages[0].renew_lock()
                    #TODO: Bug: Why was this 30s sleep before?  compare with T1.
                assert receiver.session.expired
                with pytest.raises(SessionLockExpired):
                    messages[0].complete()
                with pytest.raises(SessionLockExpired):
                    receiver.session.renew_lock()

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = receiver.receive(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                #assert messages[0].header.delivery_count  # TODO confirm this with service
                messages[0].complete()


    @pytest.mark.skip(reason='Requires schedule functionality')
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_schedule_message(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    content = str(uuid.uuid4())
                    message_id = uuid.uuid4()
                    message = Message(content, session_id=session_id)
                    message.properties.message_id = message_id
                    message.schedule(enqueue_time)
                    sender.send(message)

                messages = []
                count = 0
                while not messages and count < 12:
                    messages = receiver.receive(max_wait_time=10)
                    receiver.session.renew_lock()
                    count += 1

                data = str(messages[0])
                assert data == content
                assert messages[0].properties.message_id == message_id
                assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                assert len(messages) == 1


    @pytest.mark.skip(reason='Requires schedule functionality')
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_schedule_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, prefetch=20) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    content = str(uuid.uuid4())
                    message_id_a = uuid.uuid4()
                    message_a = Message(content, session_id=session_id)
                    message_a.properties.message_id = message_id_a
                    message_id_b = uuid.uuid4()
                    message_b = Message(content, session_id=session_id)
                    message_b.properties.message_id = message_id_b
                    tokens = sender.schedule(enqueue_time, message_a, message_b)
                    assert len(tokens) == 2

                messages = []
                count = 0
                while len(messages) < 2 and count < 12:
                    receiver.session.renew_lock()
                    messages = receiver.receive(max_wait_time=15)
                    time.sleep(5)
                    count += 1

                data = str(messages[0])
                assert data == content
                assert messages[0].properties.message_id in (message_id_a, message_id_b)
                assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                assert len(messages) == 2


    @pytest.mark.skip(reason='Requires schedule functionality')
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_cancel_scheduled_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message_a = Message("Test scheduled message", session_id=session_id)
                message_b = Message("Test scheduled message", session_id=session_id)
                tokens = sender.schedule(enqueue_time, message_a, message_b)
                assert len(tokens) == 2
                sender.cancel_scheduled_messages(*tokens)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = []
                count = 0
                while not messages and count < 13:
                    messages = receiver.receive(max_wait_time=10)
                    receiver.session.renew_lock()
                    count += 1
                assert len(messages) == 0


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_get_set_state_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = Message("Handler message no. {}".format(i), session_id=session_id)
                    sender.send(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, idle_timeout=5) as session:
                assert session.session.get_session_state() == None
                session.session.set_session_state("first_state")
                count = 0
                for m in session:
                    assert m.properties.group_id == session_id.encode('utf-8')
                    count += 1
                session.session.get_session_state()
            assert count == 3


    @pytest.mark.skip(reasion="Needs list sessions")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_list_sessions_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            sessions = []
            start_time = utc_now()
            for i in range(5):
                sessions.append(str(uuid.uuid4()))

            for session_id in sessions:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = Message("Test message no. {}".format(i), session_id=session_id)
                        sender.send(message)
            for session_id in sessions:
                with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                    receiver.set_session_state("SESSION {}".format(session_id))

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                current_sessions = receiver.list_sessions(updated_since=start_time)
                assert len(current_sessions) == 5
                assert current_sessions == sessions


    @pytest.mark.skip("Requires list sessions")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_list_sessions_with_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            sessions = []
            start_time = utc_now()
            for i in range(5):
                sessions.append(str(uuid.uuid4()))

            for session in sessions:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = Message("Test message no. {}".format(i), session_id=session)
                        sender.send(message)
            for session in sessions:
                with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session) as receiver:
                    receiver.set_session_state("SESSION {}".format(session))

                    current_sessions = receiver.list_sessions(updated_since=start_time)
                    assert len(current_sessions) == 5
                    assert current_sessions == sessions


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_session_pool(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        messages = []
        errors = []
        concurrent_receivers = 5
    
        def message_processing(sb_client):
            while True:
                try:
                    with sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE, idle_timeout=5) as session:
                        for message in session:
                            print("Message: {}".format(message))
                            messages.append(message)
                            message.complete()
                except NoActiveSession:
                    return
                except Exception as e:
                    errors.append(e)
                    raise
                
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            sessions = [str(uuid.uuid4()) for i in range(concurrent_receivers)]
    
            for session_id in sessions:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(20):
                        message = Message("Test message no. {}".format(i), session_id=session_id)
                        sender.send(message)
    
            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_receivers) as thread_pool:
                for _ in range(concurrent_receivers):
                    futures.append(thread_pool.submit(message_processing, sb_client))
                concurrent.futures.wait(futures)
    
            assert not errors
            assert len(messages) == 100

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_session_client_conn_str_receive_handler_peeklock_abandon(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = Message("Handler message no. {}".format(i), session_id=session_id)
                    sender.send(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, prefetch=0) as receiver:
                message = receiver.next()
                assert message.sequence_number == 1
                message.abandon()
                second_message = receiver.next()
                assert second_message.sequence_number == 1



