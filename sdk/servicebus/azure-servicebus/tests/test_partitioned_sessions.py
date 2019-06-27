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

from azure.servicebus import ServiceBusClient, QueueClient, AutoLockRenew
from azure.servicebus.common.message import Message, PeekMessage, BatchMessage, DeferredMessage
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
    _logger.debug("Time to live: {}".format(message.header.time_to_live))
    _logger.debug("Sequence number: {}".format(message.sequence_number))
    _logger.debug("Enqueue Sequence numger: {}".format(message.enqueue_sequence_number))
    _logger.debug("Partition ID: {}".format(message.partition_id))
    _logger.debug("Partition Key: {}".format(message.partition_key))
    _logger.debug("Enqueued time: {}".format(message.enqueued_time))

@pytest.mark.liveTest
def test_qsession_by_session_client_conn_str_receive_handler_peeklock(live_servicebus_config, partitioned_session_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_session_queue,
        debug=False)
    queue_client.get_properties()

    session_id = str(uuid.uuid4())
    with queue_client.get_sender(session=session_id) as sender:
        for i in range(3):
            message = Message("Handler message no. {}".format(i))
            sender.send(message)

    with pytest.raises(ValueError):
        session = queue_client.get_receiver(idle_timeout=5)

    session = queue_client.get_receiver(session=session_id, idle_timeout=5)
    count = 0
    for message in session:
        print_message(message)
        assert message.session_id == session_id
        count += 1
        message.complete()

    assert count == 3

@pytest.mark.liveTest
def test_qsession_by_queue_client_conn_str_receive_handler_receiveanddelete(live_servicebus_config, partitioned_session_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_session_queue,
        debug=False)
    queue_client.get_properties()

    session_id = str(uuid.uuid4())
    with queue_client.get_sender(session=session_id) as sender:
        for i in range(10):
            message = Message("Handler message no. {}".format(i))
            sender.send(message)

    messages = []
    session = queue_client.get_receiver(session=session_id, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
    for message in session:
        messages.append(message)
        assert session_id == session.session_id
        assert session_id == message.session_id
        with pytest.raises(MessageAlreadySettled):
            message.complete()

    assert not session.running
    assert len(messages) == 10
    time.sleep(30)

    messages = []
    session = queue_client.get_receiver(session=session_id, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
    for message in session:
        messages.append(message)
    assert len(messages) == 0

@pytest.mark.liveTest
def test_qsession_by_session_client_conn_str_receive_handler_with_stop(live_servicebus_config, partitioned_session_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_session_queue,
        debug=False)

    session_id = str(uuid.uuid4())
    with queue_client.get_sender(session=session_id) as sender:
        for i in range(10):
            message = Message("Stop message no. {}".format(i))
            sender.send(message)

    messages = []
    session = queue_client.get_receiver(session=session_id, idle_timeout=5)
    for message in session:
        assert session_id == session.session_id
        assert session_id == message.session_id
        messages.append(message)
        message.complete()
        if len(messages) >= 5:
            break

    assert session.running
    assert len(messages) == 5

    with session:
        for message in session:
            assert session_id == session.session_id
            assert session_id == message.session_id
            messages.append(message)
            message.complete()
            if len(messages) >= 5:
                break

    assert not session.running
    assert len(messages) == 6

@pytest.mark.liveTest
def test_qsession_by_session_client_conn_str_receive_handler_with_no_session(live_servicebus_config, partitioned_session_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_session_queue,
        debug=False)

    session = queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5)
    with pytest.raises(NoActiveSession):
        session.open()

@pytest.mark.liveTest
def test_qsession_by_session_client_conn_str_receive_handler_with_inactive_session(live_servicebus_config, partitioned_session_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_session_queue,
        debug=False)

    session_id = str(uuid.uuid4())
    messages = []
    session = queue_client.get_receiver(session=session_id, mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
    for message in session:
        messages.append(message)

    assert not session.running
    assert len(messages) == 0

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    deferred_messages = []
    session_id = str(uuid.uuid4())
    messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
    for m in messages:
        m.partition_key = "MyPartitionKey"
    results = queue_client.send(messages, session=session_id)
    assert all(result[0] for result in results)

    count = 0
    session = queue_client.get_receiver(session=session_id, idle_timeout=5)
    for message in session:
        deferred_messages.append(message.sequence_number)
        print_message(message)
        count += 1
        message.defer()

    assert count == 10

    with queue_client.get_receiver(session=session_id, idle_timeout=5) as session:
        deferred = session.receive_deferred_messages(deferred_messages)
        assert len(deferred) == 10
        for message in deferred:
            assert isinstance(message, DeferredMessage)
            assert message.lock_token
            assert not message.locked_until
            assert message._receiver
            with pytest.raises(TypeError):
                message.renew_lock()
            message.complete()

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    deferred_messages = []
    session_id = str(uuid.uuid4())
    messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
    for m in messages:
        m.partition_key = "MyPartitionKey"
    results = queue_client.send(messages, session=session_id)
    assert all(result[0] for result in results)

    count = 0
    session = queue_client.get_receiver(session=session_id, idle_timeout=5)
    for message in session:
        deferred_messages.append(message.sequence_number)
        print_message(message)
        count += 1
        message.defer()

    assert count == 10

    with queue_client.get_receiver(session=session_id, idle_timeout=5) as session:
        deferred = session.receive_deferred_messages(deferred_messages)
        assert len(deferred) == 10
        for message in deferred:
            assert isinstance(message, DeferredMessage)
            message.dead_letter("something")
    
    count = 0
    with queue_client.get_deadletter_receiver(idle_timeout=5) as receiver:
        for message in receiver:
            count += 1
            print_message(message)
            assert message.user_properties[b'DeadLetterReason'] == b'something'
            assert message.user_properties[b'DeadLetterErrorDescription'] == b'something'
            message.complete()
    assert count == 10

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    deferred_messages = []
    session_id = str(uuid.uuid4())
    messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
    for m in messages:
        m.partition_key = "MyPartitionKey"
    results = queue_client.send(messages, session=session_id)
    assert all(result[0] for result in results)

    count = 0
    session = queue_client.get_receiver(session=session_id, idle_timeout=5)
    for message in session:
        deferred_messages.append(message.sequence_number)
        print_message(message)
        count += 1
        message.defer()

    assert count == 10
    with queue_client.get_receiver(session=session_id, idle_timeout=5) as session:
        deferred = session.receive_deferred_messages(deferred_messages, mode=ReceiveSettleMode.ReceiveAndDelete)
        assert len(deferred) == 10
        for message in deferred:
            assert isinstance(message, DeferredMessage)
            with pytest.raises(MessageAlreadySettled):
                message.complete()
        with pytest.raises(ServiceBusError):
            deferred = session.receive_deferred_messages(deferred_messages)

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_iter_messages_with_retrieve_deferred_client(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    deferred_messages = []
    session_id = str(uuid.uuid4())
    with queue_client.get_sender(session=session_id) as sender:
        for i in range(10):
            message = Message("Deferred message no. {}".format(i))
            sender.send(message)

    session = queue_client.get_receiver(session=session_id, idle_timeout=5)
    count = 0
    for message in session:
        deferred_messages.append(message.sequence_number)
        print_message(message)
        count += 1
        message.defer()

    assert count == 10

    with pytest.raises(ValueError):
        deferred = queue_client.receive_deferred_messages(deferred_messages, session=session_id)

    with pytest.raises(ValueError):
        queue_client.settle_deferred_messages('completed', [message], session=session_id)

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_fetch_next_with_retrieve_deadletter(live_servicebus_config, partitioned_session_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    session_id = str(uuid.uuid4())
    with queue_client.get_receiver(session=session_id, idle_timeout=5, prefetch=10) as receiver:

        with queue_client.get_sender(session=session_id) as sender:
            for i in range(10):
                message = Message("Dead lettered message no. {}".format(i))
                sender.send(message)

        count = 0
        messages = receiver.fetch_next()
        while messages:
            for message in messages:
                print_message(message)
                message.dead_letter(description="Testing queue deadletter")
                count += 1
            messages = receiver.fetch_next()
    assert count == 10

    with queue_client.get_deadletter_receiver(idle_timeout=5) as session:
        count = 0
        for message in session:
            print_message(message)
            message.complete()
            #assert message.user_properties[b'DeadLetterReason'] == b'something'  # TODO
            #assert message.user_properties[b'DeadLetterErrorDescription'] == b'something'  # TODO
            count += 1
    assert count == 10

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_browse_messages_client(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    session_id = str(uuid.uuid4())
    with queue_client.get_sender(session=session_id) as sender:
        for i in range(5):
            message = Message("Test message no. {}".format(i))
            message.partition_key = "MyPartitionKey"
            sender.send(message)

    with pytest.raises(ValueError):
        messages = queue_client.peek(5)

    messages = queue_client.peek(5, session=session_id)
    assert len(messages) == 5
    assert all(isinstance(m, PeekMessage) for m in messages)
    for message in messages:
        print_message(message)
        with pytest.raises(TypeError):
            message.complete()

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_browse_messages_with_receiver(live_servicebus_config, partitioned_session_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    session_id = str(uuid.uuid4())
    with queue_client.get_receiver(idle_timeout=5, session=session_id) as receiver:
        with queue_client.get_sender(session=session_id) as sender:
            for i in range(5):
                message = Message("Test message no. {}".format(i))
                message.partition_key = "MyPartitionKey"
                sender.send(message)

        messages = receiver.peek(5)
        assert len(messages) > 0
        assert all(isinstance(m, PeekMessage) for m in messages)
        for message in messages:
            print_message(message)
            with pytest.raises(TypeError):
                message.complete()

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_renew_client_locks(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    session_id = str(uuid.uuid4())
    messages = []
    locks = 3
    with queue_client.get_receiver(session=session_id, prefetch=10) as receiver:
        with queue_client.get_sender(session=session_id) as sender:
            for i in range(locks):
                message = Message("Test message no. {}".format(i))
                sender.send(message)

        messages.extend(receiver.fetch_next())
        recv = True
        while recv:
            recv = receiver.fetch_next(timeout=5)
            messages.extend(recv)

        try:
            for m in messages:
                with pytest.raises(TypeError):
                    expired = m.expired
                assert m.locked_until is None
                assert m.lock_token is None
            time.sleep(5)
            initial_expiry = receiver.locked_until
            receiver.renew_lock()
            assert (receiver.locked_until - initial_expiry) >= timedelta(seconds=5)
        finally:
            messages[0].complete()
            messages[1].complete()
            time.sleep(30)
            with pytest.raises(SessionLockExpired):
                messages[2].complete()

@pytest.mark.liveTest
def test_qsession_by_conn_str_receive_handler_with_autolockrenew(live_servicebus_config, partitioned_session_queue):
    session_id = str(uuid.uuid4())
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_session_queue,
        debug=False)

    with queue_client.get_sender(session=session_id) as sender:
        for i in range(10):
            message = Message("{}".format(i))
            sender.send(message)

    renewer = AutoLockRenew()
    messages = []
    with queue_client.get_receiver(session=session_id, idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as session:
        renewer.register(session, timeout=60)
        print("Registered lock renew thread", session.locked_until, datetime.now())
        with pytest.raises(SessionLockExpired):
            for message in session:
                if not messages:
                    print("Starting first sleep")
                    time.sleep(40)
                    print("First sleep {}".format(session.locked_until - datetime.now()))
                    assert not session.expired
                    with pytest.raises(TypeError):
                        message.expired
                    assert message.locked_until is None
                    with pytest.raises(TypeError):
                        message.renew_lock()
                    assert message.lock_token is None
                    message.complete()
                    messages.append(message)

                elif len(messages) == 1:
                    print("Starting second sleep")
                    time.sleep(40)
                    print("Second sleep {}".format(session.locked_until - datetime.now()))
                    assert session.expired
                    assert isinstance(session.auto_renew_error, AutoLockRenewTimeout)
                    try:
                        message.complete()
                        raise AssertionError("Didn't raise SessionLockExpired")
                    except SessionLockExpired as e:
                        assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                    messages.append(message)

    renewer.shutdown()
    assert len(messages) == 2

@pytest.mark.liveTest
def test_qsession_message_connection_closed(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    session_id = str(uuid.uuid4())
    queue_client = client.get_queue(partitioned_session_queue)
    
    with queue_client.get_sender() as sender:
        message = Message("test")
        message.session_id = session_id
        sender.send(message)

    with queue_client.get_receiver(session=session_id) as receiver:
        messages = receiver.fetch_next(timeout=10)
        assert len(messages) == 1

    with pytest.raises(MessageSettleFailed):
        messages[0].complete()

@pytest.mark.liveTest
def test_qsession_message_expiry(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    session_id = str(uuid.uuid4())
    queue_client = client.get_queue(partitioned_session_queue)
    
    with queue_client.get_sender() as sender:
        message = Message("Testing expired messages")
        message.session_id = session_id
        sender.send(message)

    with queue_client.get_receiver(session=session_id) as receiver:
        messages = receiver.fetch_next(timeout=10)
        assert len(messages) == 1
        print_message(messages[0])
        time.sleep(30)
        with pytest.raises(TypeError):
            messages[0].expired
        with pytest.raises(TypeError):
            messages[0].renew_lock()
        assert receiver.expired
        with pytest.raises(SessionLockExpired):
            messages[0].complete()
        with pytest.raises(SessionLockExpired):
            receiver.renew_lock()

    with queue_client.get_receiver(session=session_id) as receiver:
        messages = receiver.fetch_next(timeout=30)
        assert len(messages) == 1
        print_message(messages[0])
        #assert messages[0].header.delivery_count  # TODO confirm this with service
        messages[0].complete()

@pytest.mark.liveTest
def test_qsession_schedule_message(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    import uuid
    session_id = str(uuid.uuid4())
    queue_client = client.get_queue(partitioned_session_queue)
    enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
    with queue_client.get_receiver(session=session_id) as receiver:
        with queue_client.get_sender(session=session_id) as sender:
            content = str(uuid.uuid4())
            message_id = uuid.uuid4()
            message = Message(content)
            message.properties.message_id = message_id
            message.schedule(enqueue_time)
            sender.send(message)

        messages = []
        count = 0
        while not messages and count < 12:
            messages = receiver.fetch_next(timeout=10)
            receiver.renew_lock()
            count += 1

        data = str(messages[0])
        assert data == content
        assert messages[0].properties.message_id == message_id
        assert messages[0].scheduled_enqueue_time == enqueue_time
        assert messages[0].scheduled_enqueue_time == messages[0].enqueued_time.replace(microsecond=0)
        assert len(messages) == 1

@pytest.mark.liveTest
def test_qsession_schedule_multiple_messages(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    import uuid
    session_id = str(uuid.uuid4())
    queue_client = client.get_queue(partitioned_session_queue)
    enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)

    with queue_client.get_receiver(session=session_id, prefetch=20) as receiver:
        with queue_client.get_sender(session=session_id) as sender:
            content = str(uuid.uuid4())
            message_id = uuid.uuid4()
            message_a = Message(content)
            message_a.properties.message_id = message_id
            message_b = Message(content)
            message_b.properties.message_id = message_id
            sender.schedule(enqueue_time, message_a, message_b)
            assert len(tokens) == 2

        messages = []
        count = 0
        while len(messages) < 2 and count < 12:
            messages = receiver.fetch_next(timeout=10)
            receiver.renew_lock()
            count += 1

        data = str(messages[0])
        assert data == content
        assert messages[0].scheduled_enqueue_time == enqueue_time
        assert messages[0].scheduled_enqueue_time == messages[0].enqueued_time.replace(microsecond=0)
        assert len(messages) == 2

@pytest.mark.liveTest
def test_qsession_cancel_scheduled_messages(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    session_id = str(uuid.uuid4())
    queue_client = client.get_queue(partitioned_session_queue)
    enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)

    with queue_client.get_sender(session=session_id) as sender:
        message_id = uuid.uuid4()
        message_a = Message("Test scheduled message")
        message_a.properties.message_id = message_id
        message_b = Message("Test scheduled message")
        message_b.properties.message_id = message_id
        tokens = sender.schedule(enqueue_time, message_a, message_b)
        assert len(tokens) == 2
        sender.cancel_scheduled_messages(*tokens)

    with queue_client.get_receiver(session=session_id) as receiver:
        messages = []
        count = 0
        while not messages and count < 13:
            messages = receiver.fetch_next(timeout=10)
            receiver.renew_lock()
            count += 1
        assert len(messages) == 0

@pytest.mark.liveTest
def test_qsession_get_set_state_with_receiver(live_servicebus_config, partitioned_session_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_session_queue,
        debug=False)
    queue_client.get_properties()
    session_id = str(uuid.uuid4())
    with queue_client.get_sender(session=session_id) as sender:
        for i in range(3):
            message = Message("Handler message no. {}".format(i))
            sender.send(message)

    with queue_client.get_receiver(session=session_id, idle_timeout=5) as session:
        assert session.get_session_state() == None
        session.set_session_state("first_state")
        count = 0
        for m in session:
            assert m.properties.group_id == session_id.encode('utf-8')
            count += 1
        with pytest.raises(InvalidHandlerState):
            session.get_session_state()
    assert count == 3

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_list_sessions_with_receiver(live_servicebus_config, partitioned_session_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    sessions = []
    start_time = datetime.now()
    for i in range(5):
        sessions.append(str(uuid.uuid4()))

    for session in sessions:
        with queue_client.get_sender(session=session) as sender:
            for i in range(5):
                message = Message("Test message no. {}".format(i))
                sender.send(message)
    for session in sessions:
        with queue_client.get_receiver(session=session) as receiver:
            receiver.set_session_state("SESSION {}".format(session))

    with queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        current_sessions = receiver.list_sessions(updated_since=start_time)
        assert len(current_sessions) == 5
        assert current_sessions == sessions

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_list_sessions_with_client(live_servicebus_config, partitioned_session_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    sessions = []
    start_time = datetime.now()
    for i in range(5):
        sessions.append(str(uuid.uuid4()))

    for session in sessions:
        with queue_client.get_sender(session=session) as sender:
            for i in range(5):
                message = Message("Test message no. {}".format(i))
                sender.send(message)
    for session in sessions:
        with queue_client.get_receiver(session=session) as receiver:
            receiver.set_session_state("SESSION {}".format(session))

    current_sessions = queue_client.list_sessions(updated_since=start_time)
    assert len(current_sessions) == 5
    assert current_sessions == sessions

@pytest.mark.liveTest
def test_qsession_by_servicebus_client_session_pool(live_servicebus_config, partitioned_session_queue):
    messages = []
    errors = []
    concurrent_receivers = 5

    def message_processing(queue_client):
        while True:
            try:
                with queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5) as session:
                    for message in session:
                        print("Message: {}".format(message))
                        messages.append(message)
                        message.complete()
            except NoActiveSession:
                return
            except Exception as e:
                errors.append(e)
                raise

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_session_queue)
    sessions = [str(uuid.uuid4()) for i in range(concurrent_receivers)]

    for session in sessions:
        with queue_client.get_sender(session=session) as sender:
            for i in range(20):
                message = Message("Test message no. {}".format(i))
                sender.send(message)

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_receivers) as thread_pool:
        for _ in range(concurrent_receivers):
            futures.append(thread_pool.submit(message_processing, queue_client))
        concurrent.futures.wait(futures)

    assert not errors
    assert len(messages) == 100