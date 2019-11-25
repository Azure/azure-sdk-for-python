#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

from azure.servicebus import ServiceBusClient, QueueClient, AutoLockRenew
from azure.servicebus.common.message import Message, PeekMessage, BatchMessage, DeferredMessage
from azure.servicebus.common.constants import ReceiveSettleMode
from azure.servicebus.common.errors import (
    ServiceBusError,
    MessageLockExpired,
    InvalidHandlerState,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSendFailed,
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

@pytest.mark.liveTest
def test_pqueue_by_queue_client_conn_str_receive_handler_peeklock(live_servicebus_config, partitioned_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_queue,
        debug=False)

    with queue_client.get_sender() as sender:
        for i in range(10):
            message = Message("Handler message no. {}".format(i))
            message.enqueue_sequence_number = i
            sender.send(message)

    receiver = queue_client.get_receiver(idle_timeout=5)
    count = 0
    for message in receiver:
        print_message(message)
        count += 1
        message.complete()

    assert count == 10

@pytest.mark.liveTest
def test_pqueue_by_queue_client_conn_str_receive_handler_receiveanddelete(live_servicebus_config, partitioned_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_queue,
        debug=False)

    with queue_client.get_sender() as sender:
        for i in range(10):
            message = Message("Handler message no. {}".format(i))
            message.enqueue_sequence_number = i
            sender.send(message)

    messages = []
    receiver = queue_client.get_receiver(mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
    for message in receiver:
        messages.append(message)
        with pytest.raises(MessageAlreadySettled):
            message.complete()

    assert not receiver.running
    assert len(messages) == 10
    time.sleep(30)

    messages = []
    receiver = queue_client.get_receiver(mode=ReceiveSettleMode.ReceiveAndDelete, idle_timeout=5)
    for message in receiver:
        messages.append(message)
    assert len(messages) == 0

@pytest.mark.liveTest
def test_pqueue_by_queue_client_conn_str_receive_handler_with_stop(live_servicebus_config, partitioned_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_queue,
        debug=False)

    with queue_client.get_sender() as sender:
        for i in range(10):
            message = Message("Stop message no. {}".format(i))
            sender.send(message)

    messages = []
    receiver = queue_client.get_receiver(idle_timeout=5)
    for message in receiver:
        messages.append(message)
        message.complete()
        if len(messages) >= 5:
            break

    assert receiver.running
    assert len(messages) == 5

    with receiver:
        for message in receiver:
            messages.append(message)
            message.complete()
            if len(messages) >= 5:
                break

    assert not receiver.running
    assert len(messages) == 6

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_iter_messages_simple(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

        with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("Iter message no. {}".format(i))
                sender.send(message)

        count = 0
        for message in receiver:
            print_message(message)
            message.complete()
            with pytest.raises(MessageAlreadySettled):
                message.complete()
            with pytest.raises(MessageAlreadySettled):
                message.renew_lock()
            count += 1

        with pytest.raises(InvalidHandlerState):
            next(receiver)
    assert count == 10

@pytest.mark.liveTest
def test_pqueue_by_servicebus_conn_str_client_iter_messages_with_abandon(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient.from_connection_string(live_servicebus_config['conn_str'], debug=False)
    queue_client = client.get_queue(partitioned_queue)
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

        with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("Abandoned message no. {}".format(i))
                sender.send(message)

        count = 0
        for message in receiver:
            print_message(message)
            if not message.header.delivery_count:
                count += 1
                message.abandon()
            else:
                assert message.header.delivery_count == 1
                message.complete()

    assert count == 10

    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        count = 0
        for message in receiver:
            print_message(message)
            message.complete()
            count += 1
    assert count == 0

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_iter_messages_with_defer(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    deferred_messages = []
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

        with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("Deferred message no. {}".format(i))
                sender.send(message)

        count = 0
        for message in receiver:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            message.defer()

    assert count == 10
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        count = 0
        for message in receiver:
            print_message(message)
            message.complete()
            count += 1
    assert count == 0

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_iter_messages_with_retrieve_deferred_client(live_servicebus_config, partitioned_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    deferred_messages = []
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

        with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("Deferred message no. {}".format(i))
                message.partition_key = "MyPartitionKey"
                sender.send(message)

        count = 0
        for message in receiver:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            message.defer()

    assert count == 10

    deferred = queue_client.receive_deferred_messages(deferred_messages, mode=ReceiveSettleMode.PeekLock)
    assert len(deferred) == 10

    for message in deferred:
        assert isinstance(message, DeferredMessage)
        with pytest.raises(ValueError):
            message.complete()

    with pytest.raises(ValueError):
        queue_client.settle_deferred_messages('foo', message)
    queue_client.settle_deferred_messages('completed', message)

    with pytest.raises(ServiceBusError):
        queue_client.receive_deferred_messages(deferred_messages)

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(live_servicebus_config, partitioned_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    deferred_messages = []
    messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
    for m in messages:
        m.partition_key = "MyPartitionKey"
    results = queue_client.send(messages, session="test_session")
    assert all(result[0] for result in results)

    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        count = 0
        for message in receiver:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            message.defer()

    assert count == 10

    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        deferred = receiver.receive_deferred_messages(deferred_messages)
        assert len(deferred) == 10
        for message in deferred:
            assert isinstance(message, DeferredMessage)
            assert message.lock_token
            assert message.locked_until
            assert message._receiver
            message.renew_lock()
            message.complete()

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    deferred_messages = []
    messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
    for m in messages:
        m.partition_key = "MyPartitionKey"
    results = queue_client.send(messages)
    assert all(result[0] for result in results)

    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        count = 0
        for message in receiver:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            message.defer()

    assert count == 10

    with queue_client.get_receiver(idle_timeout=5) as session:
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
def test_pqueue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    deferred_messages = []
    messages = [Message("Deferred message no. {}".format(i)) for i in range(10)]
    for m in messages:
        m.partition_key = "MyPartitionKey"
    results = queue_client.send(messages)
    assert all(result[0] for result in results)

    count = 0
    receiver = queue_client.get_receiver(idle_timeout=5)
    for message in receiver:
        deferred_messages.append(message.sequence_number)
        print_message(message)
        count += 1
        message.defer()

    assert count == 10
    with queue_client.get_receiver(idle_timeout=5) as receiver:
        deferred = receiver.receive_deferred_messages(deferred_messages, mode=ReceiveSettleMode.ReceiveAndDelete)
        assert len(deferred) == 10
        for message in deferred:
            assert isinstance(message, DeferredMessage)
            with pytest.raises(MessageAlreadySettled):
                message.complete()
        with pytest.raises(ServiceBusError):
            deferred = receiver.receive_deferred_messages(deferred_messages)

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_iter_messages_with_retrieve_deferred_not_found(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    deferred_messages = []
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:

        with queue_client.get_sender() as sender:
            for i in range(3):
                message = Message("Deferred message no. {}".format(i))
                message.partition_key = "MyPartitionKey"
                sender.send(message)

        count = 0
        for message in receiver:
            deferred_messages.append(message.sequence_number)
            print_message(message)
            count += 1
            message.defer()

    assert count == 3

    with pytest.raises(ServiceBusError):
        deferred = queue_client.receive_deferred_messages([3, 4], mode=ReceiveSettleMode.PeekLock)

    with pytest.raises(ServiceBusError):
        deferred = queue_client.receive_deferred_messages([5, 6, 7], mode=ReceiveSettleMode.PeekLock)

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_receive_batch_with_deadletter(live_servicebus_config, partitioned_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

        with queue_client.get_sender() as sender:
            for i in range(10):
                message = Message("Dead lettered message no. {}".format(i))
                sender.send(message)

        count = 0
        messages = receiver.fetch_next()
        while messages:
            for message in messages:
                print_message(message)
                count += 1
                message.dead_letter(description="Testing")
            messages = receiver.fetch_next()

    assert count == 10

    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        count = 0
        for message in receiver:
            print_message(message)
            message.complete()
            count += 1
    assert count == 0

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_receive_batch_with_retrieve_deadletter(live_servicebus_config, partitioned_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

        with queue_client.get_sender() as sender:
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

        with pytest.raises(InvalidHandlerState):
            receiver.fetch_next()

    assert count == 10

    with queue_client.get_deadletter_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        count = 0
        for message in receiver:
            print_message(message)
            message.complete()
            count += 1
    assert count == 10

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_session_fail(live_servicebus_config, partitioned_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    with pytest.raises(ValueError):
        queue_client.get_receiver(session="test")

    with queue_client.get_sender(session="test") as sender:
        sender.send(Message("test session sender"))


def test_pqueue_by_servicebus_client_browse_messages_client(live_servicebus_config, partitioned_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    with queue_client.get_sender() as sender:
        for i in range(5):
            message = Message("Test message no. {}".format(i))
            message.partition_key = "MyPartitionKey"
            sender.send(message)

    messages = queue_client.peek(5)
    assert len(messages) == 5
    assert all(isinstance(m, PeekMessage) for m in messages)
    for message in messages:
        print_message(message)
        with pytest.raises(TypeError):
            message.complete()

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_browse_messages_with_receiver(live_servicebus_config, partitioned_queue):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        with queue_client.get_sender() as sender:
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
def test_pqueue_by_servicebus_client_browse_empty_messages(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
        messages = receiver.peek(10)
        assert len(messages) == 0

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_fail_send_messages(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    too_large = "A" * 1024 * 512
    try:
        results = queue_client.send(Message(too_large))
    except MessageSendFailed:
        pytest.skip("Open issue for uAMQP on OSX")

    assert len(results) == 1
    assert not results[0][0]
    assert isinstance(results[0][1], MessageSendFailed)

    with queue_client.get_sender() as sender:
        with pytest.raises(MessageSendFailed):
            sender.send(Message(too_large))

    with queue_client.get_sender() as sender:
        sender.queue_message(Message(too_large))
        results = sender.send_pending_messages()
        assert len(results) == 1
        assert not results[0][0]
        assert isinstance(results[0][1], MessageSendFailed)

@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_fail_send_batch_messages(live_servicebus_config, partitioned_queue):
    pytest.skip("TODO: Pending bugfix in uAMQP")
    def batch_data():
        for i in range(3):
            yield str(i) * 1024 * 256

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    results = queue_client.send(BatchMessage(batch_data()))
    assert len(results) == 4
    assert not results[0][0]
    assert isinstance(results[0][1], MessageSendFailed)

    with queue_client.get_sender() as sender:
        with pytest.raises(MessageSendFailed):
            sender.send(BatchMessage(batch_data()))

    with queue_client.get_sender() as sender:
        sender.queue_message(BatchMessage(batch_data()))
        results = sender.send_pending_messages()
        assert len(results) == 4
        assert not results[0][0]
        assert isinstance(results[0][1], MessageSendFailed)


@pytest.mark.liveTest
def test_pqueue_by_servicebus_client_renew_message_locks(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    messages = []
    locks = 3
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
        with queue_client.get_sender() as sender:
            for i in range(locks):
                message = Message("Test message no. {}".format(i))
                message.partition_key = "MyPartitionKey"
                sender.send(message)

        messages.extend(receiver.fetch_next())
        recv = True
        while recv:
            recv = receiver.fetch_next()
            messages.extend(recv)

        try:
            assert not message.expired
            for m in messages:
                time.sleep(5)
                initial_expiry = m.locked_until
                m.renew_lock()
                assert (m.locked_until - initial_expiry) >= timedelta(seconds=5)
        finally:
            messages[0].complete()
            messages[1].complete()
            time.sleep(30)
            with pytest.raises(MessageLockExpired):
                messages[2].complete()

@pytest.mark.liveTest
def test_pqueue_by_queue_client_conn_str_receive_handler_with_autolockrenew(live_servicebus_config, partitioned_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=partitioned_queue,
        debug=False)

    with queue_client.get_sender() as sender:
        for i in range(10):
            message = Message("{}".format(i))
            sender.send(message)

    renewer = AutoLockRenew()
    messages = []
    with queue_client.get_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
        for message in receiver:
            if not messages:
                messages.append(message)
                assert not message.expired
                renewer.register(message, timeout=60)
                print("Registered lock renew thread", message.locked_until, datetime.now())
                time.sleep(50)
                print("Finished first sleep", message.locked_until)
                assert not message.expired
                time.sleep(25)
                print("Finished second sleep", message.locked_until, datetime.now())
                assert message.expired
                try:
                    message.complete()
                    raise AssertionError("Didn't raise MessageLockExpired")
                except MessageLockExpired as e:
                    assert isinstance(e.inner_exception, AutoLockRenewTimeout)
            else:
                if message.expired:
                    print("Remaining messages", message.locked_until, datetime.now())
                    assert message.expired
                    with pytest.raises(MessageLockExpired):
                        message.complete()
                else:
                    assert message.header.delivery_count >= 1
                    print("Remaining messages", message.locked_until, datetime.now())
                    messages.append(message)
                    message.complete()
    renewer.shutdown()
    assert len(messages) == 11

@pytest.mark.liveTest
def test_pqueue_message_time_to_live(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    import uuid
    queue_client = client.get_queue(partitioned_queue)
    
    with queue_client.get_sender() as sender:
        content = str(uuid.uuid4())
        message_id = uuid.uuid4()
        message = Message(content)
        message.time_to_live = timedelta(seconds=30)
        sender.send(message)

    time.sleep(30)
    with queue_client.get_receiver() as receiver:
        messages = receiver.fetch_next(timeout=10)
    assert not messages

    with queue_client.get_deadletter_receiver(idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
        count = 0
        for message in receiver:
            print_message(message)
            message.complete()
            count += 1
        assert count == 1

@pytest.mark.liveTest
def test_pqueue_message_connection_closed(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    import uuid
    queue_client = client.get_queue(partitioned_queue)
    
    with queue_client.get_sender() as sender:
        content = str(uuid.uuid4())
        message = Message(content)
        message.partition_key = "MyPartitionKey"
        sender.send(message)

    with queue_client.get_receiver() as receiver:
        messages = receiver.fetch_next(timeout=10)
        assert len(messages) == 1

    with pytest.raises(MessageSettleFailed):
        messages[0].complete()

@pytest.mark.liveTest
def test_pqueue_message_expiry(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    import uuid
    queue_client = client.get_queue(partitioned_queue)
    
    with queue_client.get_sender() as sender:
        content = str(uuid.uuid4())
        message = Message(content)
        sender.send(message)

    with queue_client.get_receiver() as receiver:
        messages = receiver.fetch_next(timeout=10)
        assert len(messages) == 1
        time.sleep(30)
        assert messages[0].expired
        with pytest.raises(MessageLockExpired):
            messages[0].complete()
        with pytest.raises(MessageLockExpired):
            messages[0].renew_lock()

    with queue_client.get_receiver() as receiver:
        messages = receiver.fetch_next(timeout=30)
        assert len(messages) == 1
        print_message(messages[0])
        assert messages[0].header.delivery_count > 0
        messages[0].complete()

@pytest.mark.liveTest
def test_pqueue_message_lock_renew(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    import uuid
    queue_client = client.get_queue(partitioned_queue)
    
    with queue_client.get_sender() as sender:
        content = str(uuid.uuid4())
        message = Message(content)
        sender.send(message)

    with queue_client.get_receiver() as receiver:
        messages = receiver.fetch_next(timeout=10)
        assert len(messages) == 1
        time.sleep(15)
        messages[0].renew_lock()
        time.sleep(15)
        messages[0].renew_lock()
        time.sleep(15)
        assert not messages[0].expired
        messages[0].complete()

    with queue_client.get_receiver() as receiver:
        messages = receiver.fetch_next(timeout=10)
        assert len(messages) == 0

@pytest.mark.liveTest
def test_pqueue_message_receive_and_delete(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    queue_client = client.get_queue(partitioned_queue)
    
    with queue_client.get_sender() as sender:
        message = Message("Receive and delete test")
        sender.send(message)

    with queue_client.get_receiver(mode=ReceiveSettleMode.ReceiveAndDelete) as receiver:
        messages = receiver.fetch_next(timeout=10)
        assert len(messages) == 1
        received = messages[0]
        print_message(received)
        with pytest.raises(MessageAlreadySettled):
            received.complete()
        with pytest.raises(MessageAlreadySettled):
            received.abandon()
        with pytest.raises(MessageAlreadySettled):
            received.defer()
        with pytest.raises(MessageAlreadySettled):
            received.dead_letter()
        with pytest.raises(MessageAlreadySettled):
            received.renew_lock()

    time.sleep(30)

    with queue_client.get_receiver() as receiver:
        messages = receiver.fetch_next(timeout=10)
        for m in messages:
            print_message(m)
        assert len(messages) == 0

@pytest.mark.liveTest
def test_pqueue_message_batch(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    queue_client = client.get_queue(partitioned_queue)
    
    def message_content():
        for i in range(5):
            yield "Message no. {}".format(i)


    with queue_client.get_sender() as sender:
        message = BatchMessage(message_content())
        sender.send(message)

    with queue_client.get_receiver() as receiver:
        messages =receiver.fetch_next(timeout=10)
        recv = True
        while recv:
            recv = receiver.fetch_next(timeout=10)
            messages.extend(recv)

        assert len(messages) == 5
        for m in messages:
            print_message(m)
            m.complete()

@pytest.mark.liveTest
def test_pqueue_schedule_message(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    import uuid
    queue_client = client.get_queue(partitioned_queue)
    enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
    with queue_client.get_receiver() as receiver:
        with queue_client.get_sender() as sender:
            content = str(uuid.uuid4())
            message_id = uuid.uuid4()
            message = Message(content)
            message.properties.message_id = message_id
            message.schedule(enqueue_time)
            sender.send(message)

        messages = receiver.fetch_next(timeout=120)
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
                    m.complete()
        else:
            raise Exception("Failed to receive schdeduled message.")

@pytest.mark.liveTest
def test_pqueue_schedule_multiple_messages(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)
    import uuid
    queue_client = client.get_queue(partitioned_queue)
    enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
    with queue_client.get_receiver(prefetch=20) as receiver:
        with queue_client.get_sender() as sender:
            content = str(uuid.uuid4())
            message_id_a = uuid.uuid4()
            message_a = Message(content)
            message_a.properties.message_id = message_id_a
            message_id_b = uuid.uuid4()
            message_b = Message(content)
            message_b.properties.message_id = message_id_b
            tokens = sender.schedule(enqueue_time, message_a, message_b)
            assert len(tokens) == 2

        messages = receiver.fetch_next(timeout=120)
        messages.extend(receiver.fetch_next(timeout=5))
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
                    m.complete()
        else:
            raise Exception("Failed to receive schdeduled message.")

@pytest.mark.liveTest
def test_pqueue_cancel_scheduled_messages(live_servicebus_config, partitioned_queue):
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=False)

    queue_client = client.get_queue(partitioned_queue)
    enqueue_time = (datetime.utcnow() + timedelta(minutes=2)).replace(microsecond=0)
    with queue_client.get_receiver() as receiver:
        with queue_client.get_sender() as sender:
            message_a = Message("Test scheduled message")
            message_b = Message("Test scheduled message")
            tokens = sender.schedule(enqueue_time, message_a, message_b)
            assert len(tokens) == 2

            sender.cancel_scheduled_messages(*tokens)

        messages = receiver.fetch_next(timeout=120)
        try:
            assert len(messages) == 0
        except AssertionError:
            for m in messages:
                print(str(m))
                m.complete()
            raise
