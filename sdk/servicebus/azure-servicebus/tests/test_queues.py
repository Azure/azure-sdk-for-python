#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor
import types
import pytest
import time
import uuid
from datetime import datetime, timedelta
import calendar
import unittest
import pickle

try:
    import uamqp
    from azure.servicebus._transport._uamqp_transport import UamqpTransport
except ImportError:
    uamqp = None

from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus._pyamqp.message import Message
from azure.servicebus._pyamqp import error, client, management_operation
from azure.servicebus import (
    ServiceBusClient,
    AutoLockRenewer,
    TransportType,
    ServiceBusMessage,
    ServiceBusMessageBatch,
    ServiceBusReceivedMessage,
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
from azure.servicebus._common.constants import (
    _X_OPT_LOCK_TOKEN,
    _X_OPT_PARTITION_KEY,
    _X_OPT_VIA_PARTITION_KEY,
    _X_OPT_SCHEDULED_ENQUEUE_TIME,
    ServiceBusMessageState
)
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

from devtools_testutils import AzureMgmtRecordedTestCase
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusQueuePreparer,
    CachedServiceBusQueuePreparer,
    CachedServiceBusResourceGroupPreparer
)
from utilities import get_logger, print_message, sleep_until_expired
from mocks import MockReceivedMessage, MockReceiver
from utilities import uamqp_transport as get_uamqp_transport, ArgPasser

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()

_logger = get_logger(logging.DEBUG)


# A note regarding live_test_only.
# Old servicebus tests were not written to work on both stubs and live entities.
# This disables those tests for non-live scenarios, and should be removed as tests
# are ported to offline-compatible code.
class TestServiceBusQueue(AzureMgmtRecordedTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_receive_and_delete_reconnect_interaction(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        # Note: This test was to guard against github issue 7079
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport)

        with sb_client.get_queue_sender(servicebus_queue.name) as sender:
            for i in range(5):
                sender.send_messages(ServiceBusMessage("ServiceBusMessage {}".format(i)))

        with sb_client.get_queue_receiver(servicebus_queue.name,
                                          receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                          max_wait_time=10) as receiver:
            batch = receiver.receive_messages()
            count = len(batch)

            for message in receiver:
               _logger.debug(message)
               count += 1
            assert count == 5

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT5S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_github_issue_6178(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    sender.send_messages(ServiceBusMessage("ServiceBusMessage {}".format(i)))

                    with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=60) as receiver:
                        for message in receiver:
                            _logger.debug(message)
                            _logger.debug(message.sequence_number)
                            _logger.debug(message.enqueued_time_utc)
                            _logger.debug(message._lock_expired)
                            receiver.complete_message(message)
                            time.sleep(10)

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_queue_client_conn_str_receive_handler_peeklock(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            for i in range(10):
                message = ServiceBusMessage("Handler message no. {}".format(i))
                message.application_properties = {'key': 'value'}
                message.subject = 'label'
                message.content_type = 'application/text'
                message.correlation_id = 'cid'
                message.message_id = str(i)
                message.partition_key = 'pk'
                message.to = 'to'
                message.reply_to = 'reply_to'
                sender.send_messages(message)

            # Test that noop empty send works properly.
            sender.send_messages([])
            sender.send_messages(ServiceBusMessageBatch())
            assert len(sender.schedule_messages([], utc_now())) == 0
            sender.cancel_scheduled_messages([])
            sender.close()

            # Then test expected failure modes.
            with pytest.raises(ValueError):
                with sender:
                    raise AssertionError("Should raise ValueError")
            with pytest.raises(ValueError):
                sender.send_messages(ServiceBusMessage('msg'))
            with pytest.raises(ValueError):
                sender.schedule_messages(ServiceBusMessage('msg'), utc_now())
            with pytest.raises(ValueError):
                sender.cancel_scheduled_messages([1, 2, 3])

            with pytest.raises(ValueError):
                sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=0)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10)

            assert len(receiver.receive_deferred_messages([])) == 0
            with pytest.raises(ValueError):
                receiver.receive_messages(max_wait_time=0)

            count = 0
            for message in receiver:
                print_message(_logger, message)
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
                assert message.message.delivery_tag is not None
                assert message.lock_token == message.message.delivery_annotations.get(_X_OPT_LOCK_TOKEN)
                assert message.lock_token == uuid.UUID(bytes_le=message.message.delivery_tag)
                assert not message.scheduled_enqueue_time_utc
                assert not message.time_to_live
                assert not message.session_id
                assert not message.reply_to_session_id
                count += 1
                receiver.complete_message(message)
            receiver.close()

            with pytest.raises(ValueError):
                receiver.receive_messages()
            with pytest.raises(ValueError):
                with receiver:
                    raise AssertionError("Should raise ValueError")
            with pytest.raises(ValueError):
                receiver.receive_deferred_messages([1, 2, 3])
            with pytest.raises(ValueError):
                receiver.peek_messages()

            assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_queue_client_conn_str_receive_handler_release_messages(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            def sub_test_releasing_messages():
                # test releasing messages when prefetch is 1 and link credits are issue dynamically
                receiver = sb_client.get_queue_receiver(servicebus_queue.name)
                sender = sb_client.get_queue_sender(servicebus_queue.name)
                with sender, receiver:
                    # send 10 msgs to queue first
                    sender.send_messages([ServiceBusMessage('test') for _ in range(5)])

                    received_msgs = []
                    # the amount of messages returned by receive call is not stable, especially in live tests
                    # of different os platforms, this is why a while loop is used here to receive the specific
                    # amount of message we want to receive
                    while len(received_msgs) < 5:
                        # issue link credits more than 5, client should consume 5 msgs from the service in total,
                        # leaving the extra credits on the wire
                        for msg in receiver.receive_messages(max_message_count=10, max_wait_time=5):
                            receiver.complete_message(msg)
                            received_msgs.append(received_msgs)
                    assert len(received_msgs) == 5

                    # send 5 more messages, those messages would arrive at the client while the program is sleeping
                    sender.send_messages([ServiceBusMessage('test') for _ in range(5)])
                    time.sleep(15)  # sleep > message expiration time

                    target_msgs_count = 5
                    received_msgs = []
                    while len(received_msgs) < target_msgs_count:
                        # issue 10 link credits, client should consume 5 msgs from the service, leaving no link credits
                        for msg in receiver.receive_messages(max_message_count=target_msgs_count - len(received_msgs),
                                                             max_wait_time=5):
                            assert msg.delivery_count == 0  # release would not increase delivery count
                            receiver.complete_message(msg)
                            received_msgs.append(msg)
                    assert len(received_msgs) == 5

            def sub_test_releasing_messages_iterator():
                # test nested iterator scenario
                receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10)
                sender = sb_client.get_queue_sender(servicebus_queue.name)
                with sender, receiver:
                    # send 5 msgs to queue first
                    sender.send_messages([ServiceBusMessage('test') for _ in range(5)])
                    first_time = True
                    iterator_recv_cnt = 0

                    # case: iterator + receive batch
                    for msg in receiver:
                        assert msg.delivery_count == 0  # release would not increase delivery count
                        receiver.complete_message(msg)
                        iterator_recv_cnt += 1
                        if first_time:  # for the first time, we call nested receive message call
                            received_msgs = []

                            while len(received_msgs) < 4:  # there supposed to be 5 msgs in the queue
                                # we issue 10 link credits, leaving more credits on the wire
                                for sub_msg in receiver.receive_messages(max_message_count=10, max_wait_time=5):
                                    assert sub_msg.delivery_count == 0
                                    receiver.complete_message(sub_msg)
                                    received_msgs.append(sub_msg)
                            assert len(received_msgs) == 4
                            sender.send_messages([ServiceBusMessage('test') for _ in range(10)])
                            time.sleep(15)  # sleep > message expiration time

                            received_msgs = []
                            target_msgs_count = 5  # we want to receive 5 with the receive message call
                            while len(received_msgs) < target_msgs_count:
                                for sub_msg in receiver.receive_messages(
                                        max_message_count=target_msgs_count - len(received_msgs), max_wait_time=5):
                                    assert sub_msg.delivery_count == 0  # release would not increase delivery count
                                    receiver.complete_message(sub_msg)
                                    received_msgs.append(sub_msg)
                            assert len(received_msgs) == target_msgs_count
                            first_time = False
                    assert iterator_recv_cnt == 6  # 1 before nested receive message call + 5 after nested receive message call

                    # case: iterator + iterator case
                    sender.send_messages([ServiceBusMessage('test') for _ in range(10)])
                    outter_recv_cnt = 0
                    inner_recv_cnt = 0
                    for msg in receiver:
                        assert msg.delivery_count == 0
                        outter_recv_cnt += 1
                        receiver.complete_message(msg)
                        for sub_msg in receiver:
                            assert sub_msg.delivery_count == 0
                            inner_recv_cnt += 1
                            receiver.complete_message(sub_msg)
                            if inner_recv_cnt == 5:
                                time.sleep(15)  # innner finish receiving first 5 messages then sleep until lock expiration
                                break
                    assert outter_recv_cnt == 1
                    outter_recv_cnt = 0
                    for msg in receiver:
                        assert msg.delivery_count == 0
                        outter_recv_cnt += 1
                        receiver.complete_message(msg)
                    assert outter_recv_cnt == 4


            def sub_test_non_releasing_messages():
                # test not releasing messages when prefetch is not 1
                receiver = sb_client.get_queue_receiver(servicebus_queue.name)
                sender = sb_client.get_queue_sender(servicebus_queue.name)

                if uamqp_transport:
                    def _hack_disable_receive_context_message_received(self, message):
                        # pylint: disable=protected-access
                        self._handler._was_message_received = True
                        self._handler._received_messages.put(message)
                else:
                    def _hack_disable_receive_context_message_received(self, frame, message):
                        # pylint: disable=protected-access
                        self._handler._last_activity_timestamp = time.time()
                        self._handler._received_messages.put((frame, message))

                with sender, receiver:
                    # send 5 msgs to queue first
                    sender.send_messages([ServiceBusMessage('test') for _ in range(5)])
                    if uamqp_transport:
                        receiver._handler.message_handler.on_message_received = types.MethodType(
                            _hack_disable_receive_context_message_received, receiver)
                    else:
                        receiver._handler._link._on_transfer = types.MethodType(
                            _hack_disable_receive_context_message_received, receiver)
                    received_msgs = []
                    while len(received_msgs) < 5:
                        # issue 10 link credits, client should consume 5 msgs from the service
                        # leaving 5 credits on the wire
                        for msg in receiver.receive_messages(max_message_count=10, max_wait_time=5):
                            receiver.complete_message(msg)
                            received_msgs.append(msg)
                    assert len(received_msgs) == 5

                    # send 5 more messages, those messages would arrive at the client while the program is sleeping
                    sender.send_messages([ServiceBusMessage('test') for _ in range(5)])
                    time.sleep(15)  # sleep > message expiration time

                    # issue 5 link credits, client should consume 5 msgs from the internal buffer which is already lock expired
                    target_msgs_count = 5
                    received_msgs = []
                    while len(received_msgs) < target_msgs_count:
                        received_msgs.extend(receiver.receive_messages(max_message_count=5, max_wait_time=5))
                    assert len(received_msgs) == 5
                    for msg in received_msgs:
                        # queue ordering I think
                        assert msg.delivery_count == 0
                        with pytest.raises(ServiceBusError):
                            receiver.complete_message(msg)

                    # re-received message with delivery count increased
                    target_msgs_count = 5
                    received_msgs = []
                    while len(received_msgs) < target_msgs_count:
                        received_msgs.extend(receiver.receive_messages(max_message_count=5, max_wait_time=5))
                    assert len(received_msgs) == 5
                    for msg in received_msgs:
                        assert msg.delivery_count > 0
                        receiver.complete_message(msg)

            sub_test_releasing_messages()
            sub_test_releasing_messages_iterator()
            sub_test_non_releasing_messages()

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_queue_client_send_multiple_messages(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            with sender:
                messages = []
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i))
                    message.partition_key = 'pkey'
                    message.time_to_live = timedelta(seconds=60)
                    message.scheduled_enqueue_time_utc = utc_now() + timedelta(seconds=60)
                    message.partition_key = None
                    message.time_to_live = None
                    message.scheduled_enqueue_time_utc = None
                    message.session_id = None
                    messages.append(message)
                sender.send_messages(messages)

            with pytest.raises(ValueError):
                with sender:
                    raise AssertionError("Should raise ValueError")
            with pytest.raises(ValueError):
                sender.send_messages(ServiceBusMessage('msg'))
            with pytest.raises(ValueError):
                sender.schedule_messages(ServiceBusMessage('msg'), utc_now())
            with pytest.raises(ValueError):
                sender.cancel_scheduled_messages([1, 2, 3])

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)
            with receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    assert message.delivery_count == 0
                    assert not message.application_properties
                    assert not message.subject
                    assert not message.content_type
                    assert not message.correlation_id
                    assert not message.to
                    assert not message.reply_to
                    assert not message.scheduled_enqueue_time_utc
                    assert not message.time_to_live
                    assert not message.session_id
                    assert not message.reply_to_session_id
                    count += 1
                    receiver.complete_message(message)
                assert count == 10

            with pytest.raises(ValueError):
                receiver.receive_messages()
            with pytest.raises(ValueError):
                with receiver:
                    raise AssertionError("Should raise ValueError")
            with pytest.raises(ValueError):
                receiver.receive_deferred_messages([1, 2, 3])
            with pytest.raises(ValueError):
                receiver.peek_messages()

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)
            with sender, receiver:
                # send previously unpicklable message
                msg = {
                    "body":"W1tdLCB7ImlucHV0X2lkIjogNH0sIHsiY2FsbGJhY2tzIjogbnVsbCwgImVycmJhY2tzIjogbnVsbCwgImNoYWluIjogbnVsbCwgImNob3JkIjogbnVsbH1d",
                    "content-encoding":"utf-8",
                    "content-type":"application/json",
                    "headers":{
                        "lang":"py",
                        "task":"tasks.example_task",
                        "id":"7c66557d-e4bc-437f-b021-b66dcc39dfdf",
                        "shadow":None,
                        "eta":"2021-10-07T02:30:23.764066+00:00",
                        "expires":None,
                        "group":None,
                        "group_index":None,
                        "retries":1,
                        "timelimit":[
                            None,
                            None
                        ],
                        "root_id":"7c66557d-e4bc-437f-b021-b66dcc39dfdf",
                        "parent_id":"7c66557d-e4bc-437f-b021-b66dcc39dfdf",
                        "argsrepr":"()",
                        "kwargsrepr":"{'input_id': 4}",
                        "origin":"gen36@94713e01a9c0",
                        "ignore_result":1,
                        "x_correlator":"44a1978d-c869-4173-afe4-da741f0edfb9"
                    },
                    "properties":{
                        "correlation_id":"7c66557d-e4bc-437f-b021-b66dcc39dfdf",
                        "reply_to":"7b9a3672-2fed-3e9b-8bfd-23ae2397d9ad",
                        "origin":"gen68@c33d4eef123a",
                        "delivery_mode":2,
                        "delivery_info":{
                            "exchange":"",
                            "routing_key":"celery_task_queue"
                        },
                        "priority":0,
                        "body_encoding":"base64",
                        "delivery_tag":"dc83ddb6-8cdc-4413-b88a-06c56cbde90d"
                    }
                }
                sender.send_messages(ServiceBusMessage(json.dumps(msg)))
                messages = receiver.receive_messages(max_wait_time=10, max_message_count=1)
                # complete first then pickle
                receiver.complete_message(messages[0])
                if not uamqp_transport:
                    pickled = pickle.loads(pickle.dumps(messages[0]))
                    assert json.loads(str(pickled)) == json.loads(str(messages[0]))
                else:
                    with pytest.raises(TypeError):
                        pickled = pickle.loads(pickle.dumps(messages[0]))

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_queue_client_conn_str_receive_handler_receiveanddelete(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i))
                    sender.send_messages(message)
    
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, 
                                              max_wait_time=8) as receiver:
                for message in receiver:
                    assert not message.application_properties
                    assert not message.subject
                    assert not message.content_type
                    assert not message.correlation_id
                    assert not message.partition_key
                    assert not message.to
                    assert not message.reply_to
                    assert not message.scheduled_enqueue_time_utc
                    assert not message.time_to_live
                    assert not message.session_id
                    assert not message.reply_to_session_id
                    messages.append(message)
                    with pytest.raises(ValueError):
                        receiver.complete_message(message)
                    with pytest.raises(ValueError): # RECEIVE_AND_DELETE messages cannot be lock renewed.
                        renewer = AutoLockRenewer()
                        renewer.register(receiver, message)
    
            assert len(messages) == 10
            assert not receiver._running
            time.sleep(10)
    
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, 
                                              max_wait_time=5) as receiver:
                for message in receiver:
                    messages.append(message)
                assert len(messages) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_queue_client_conn_str_receive_handler_receiveanddelete_prefetch(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            # send 10 messages
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i))
                    sender.send_messages(message)

            # check peek_messages returns correctly, with default prefetch_count = 0
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                            receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                            max_wait_time=10) as receiver:
                # peek messages checks current state of queue, which should return 10
                # since none were prefetched, added to internal queue, and deleted
                peeked_msgs = receiver.peek_messages(max_message_count=10, timeout=10)
                assert len(peeked_msgs) == 10

                # iterator receives and deletes each message from SB queue
                for msg in receiver:
                    messages.append(msg)
                assert len(messages) == 10

                # queue should be empty now
                peeked_msgs = receiver.peek_messages(max_message_count=10, timeout=10)
                assert len(peeked_msgs) == 0

            # send 10 messages
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i))
                    sender.send_messages(message)

            # check peek_messages returns correctly, with default prefetch_count > 0
            messages = []
            # prefetch 2 messages from SB queue when receive is called and not on open
            with sb_client.get_queue_receiver(
                servicebus_queue.name,
                receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                prefetch_count=2,
                max_wait_time=30
            ) as receiver:
                # peek messages checks current state of SB queue, and returns 10
                peeked_msgs = receiver.peek_messages(max_message_count=10, timeout=10)
                assert len(peeked_msgs) == 10

                # receive 3 messages
                recvd_msgs = receiver.receive_messages(max_message_count=3, max_wait_time=10)
                assert len(recvd_msgs) == 3

                # receive rest of messages in queue
                for msg in receiver:
                    messages.append(msg)
                assert len(messages) == 7

                # queue should be empty now
                peeked_msgs = receiver.peek_messages(max_message_count=10, timeout=10)
                assert len(peeked_msgs) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_queue_client_conn_str_receive_handler_with_stop(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("Stop message no. {}".format(i))
                    sender.send_messages(message)
    
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10) as receiver:
                for message in receiver:
                    messages.append(message)
                    receiver.complete_message(message)
                    if len(messages) >= 5:
                        break
                    
                assert receiver._running
                assert len(messages) == 5

                for message in receiver:
                    messages.append(message)
                    receiver.complete_message(message)
                    if len(messages) >= 5:
                        break

            assert not receiver._running
            assert len(messages) == 6

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_iter_messages_simple(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              max_wait_time=10,
                                              receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Iter message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    receiver.complete_message(message)
                    with pytest.raises(MessageAlreadySettled):
                        receiver.complete_message(message)
                    with pytest.raises(MessageAlreadySettled):
                        receiver.renew_message_lock(message)
                    count += 1

                with pytest.raises(StopIteration):
                    next(receiver)
            assert count == 10
    
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_conn_str_client_iter_messages_with_abandon(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Abandoned message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    if not message.delivery_count:
                        count += 1
                        receiver.abandon_message(message)
                    else:
                        assert message.delivery_count == 1
                        receiver.complete_message(message)
    
            assert count == 10
    
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=20, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    receiver.complete_message(message)
                    count += 1
            assert count == 0

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_iter_messages_with_defer(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            deferred_messages = []
            with sb_client.get_queue_receiver(
                servicebus_queue.name, 
                max_wait_time=5, 
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Deferred message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)
    
            assert count == 10
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    receiver.complete_message(message)
                    count += 1
            assert count == 0
    
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            deferred_messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                 max_wait_time=5, 
                                                 receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Deferred message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)
    
                assert count == 10
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    receiver.complete_message(message)
                
                with pytest.raises(ServiceBusError):
                    receiver.receive_deferred_messages(deferred_messages)

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                deferred_messages = []
                for i in range(10):
                    message = ServiceBusMessage("Deferred message no. {}".format(i), session_id="test_session")
                    sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                        max_wait_time=5, 
                                        receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)
    
            assert count == 10
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                           max_wait_time=5, 
                                           receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    assert message.lock_token
                    assert message.locked_until_utc
                    assert message._receiver
                    receiver.renew_message_lock(message)
                    receiver.complete_message(message)

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                deferred_messages = []
                for i in range(10):
                    message = ServiceBusMessage("Deferred message no. {}".format(i))
                    sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              max_wait_time=10,
                                              receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)
    
            assert count == 10
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                        max_wait_time=10) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    receiver.dead_letter_message(message, reason="Testing reason", error_description="Testing description")
    
            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                                              max_wait_time=10) as receiver:
                for message in receiver:
                    count += 1
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    receiver.complete_message(message)
            assert count == 10

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    sender.send_messages(ServiceBusMessage("Deferred message no. {}".format(i)))

            deferred_messages = []
            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)
    
            assert count == 10
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE.value, 
                                              max_wait_time=5) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    with pytest.raises(ValueError):
                        receiver.complete_message(message)
                with pytest.raises(ServiceBusError):
                    deferred = receiver.receive_deferred_messages(deferred_messages)

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_not_found(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            deferred_messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                 max_wait_time=5, 
                                                 receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(3):
                        message = ServiceBusMessage("Deferred message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)
    
                assert count == 3
    
                with pytest.raises(ServiceBusError):
                    deferred = receiver.receive_deferred_messages([3, 4])
    
                with pytest.raises(ServiceBusError):
                    deferred = receiver.receive_deferred_messages([5, 6, 7])

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_receive_batch_with_deadletter(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                           max_wait_time=5, 
                                           receive_mode=ServiceBusReceiveMode.PEEK_LOCK, 
                                           prefetch_count=10) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Dead lettered message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                messages = receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        count += 1
                        receiver.dead_letter_message(message, reason="Testing reason",
                                                     error_description="Testing description")
                    messages = receiver.receive_messages()
    
            assert count == 10
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              max_wait_time=5, 
                                              receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    receiver.complete_message(message)
                    count += 1
            assert count == 0

            with sb_client.get_queue_receiver(
                    servicebus_queue.name,
                    sub_queue = ServiceBusSubQueue.DEAD_LETTER.value,
                    max_wait_time=5,
                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as dl_receiver:
                count = 0
                for message in dl_receiver:
                    dl_receiver.complete_message(message)
                    count += 1
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                assert count == 10

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_receive_batch_with_retrieve_deadletter(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                           max_wait_time=5,
                                           receive_mode=ServiceBusReceiveMode.PEEK_LOCK, 
                                           prefetch_count=10) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Dead lettered message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                messages = receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        receiver.dead_letter_message(message, reason="Testing reason",
                                                     error_description="Testing description")
                        count += 1
                    messages = receiver.receive_messages()
    
                receiver.receive_messages(1,5)
    
            assert count == 10

            with sb_client.get_queue_receiver(
                    servicebus_queue.name,
                    sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                    max_wait_time=5,
                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as dl_receiver:
                count = 0
                for message in dl_receiver:
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    dl_receiver.complete_message(message)
                    count += 1
            assert count == 10
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_session_fail(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with pytest.raises(ServiceBusError):
                sb_client.get_queue_receiver(servicebus_queue.name, session_id="test")._open_with_retry()
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("test session sender", session_id="test"))
            
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages()
                for message in messages:
                    receiver.complete_message(message)
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_browse_messages_client(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = ServiceBusMessage("Test message no. {}".format(i))
                    sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.peek_messages(5)
                assert len(messages) == 5
                assert all(isinstance(m, ServiceBusReceivedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(ValueError):
                        receiver.complete_message(message)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_browse_messages_with_receiver(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            receiver = sb_client.get_queue_receiver(servicebus_queue.name,
                                           max_wait_time=5,
                                           receive_mode=ServiceBusReceiveMode.PEEK_LOCK)
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            with receiver, sender:
                for i in range(5):
                    message = ServiceBusMessage(
                        body="Test message",
                        application_properties={'key': 'value'},
                        subject='label',
                        content_type='application/text',
                        correlation_id='cid',
                        message_id='mid',
                        to='to',
                        reply_to='reply_to',
                        time_to_live=timedelta(seconds=60)
                    )
                    sender.send_messages(message)
    
                messages = receiver.peek_messages(5)
                assert len(messages) > 0
                assert all(isinstance(m, ServiceBusReceivedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    assert b''.join(message.body) == b'Test message'
                    assert message.application_properties[b'key'] == b'value'
                    assert message.subject == 'label'
                    assert message.content_type == 'application/text'
                    assert message.correlation_id == 'cid'
                    assert message.message_id == 'mid'
                    assert message.to == 'to'
                    assert message.reply_to == 'reply_to'
                    assert message.time_to_live == timedelta(seconds=60)
                    with pytest.raises(ValueError):
                        receiver.complete_message(message)

                    sender.send_messages(message)

                cnt = 0
                for message in receiver:
                    assert b''.join(message.body) == b'Test message'
                    assert message.application_properties[b'key'] == b'value'
                    assert message.subject == 'label'
                    assert message.content_type == 'application/text'
                    assert message.correlation_id == 'cid'
                    assert message.message_id == 'mid'
                    assert message.to == 'to'
                    assert message.reply_to == 'reply_to'
                    assert message.time_to_live == timedelta(seconds=60)
                    receiver.complete_message(message)
                    cnt += 1
                assert cnt == 10
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_browse_empty_messages(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 max_wait_time=5, 
                                                 receive_mode=ServiceBusReceiveMode.PEEK_LOCK, 
                                                 prefetch_count=10) as receiver:
                messages = receiver.peek_messages(10)
                assert len(messages) == 0
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_fail_send_messages(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            too_large = "A" * 256 * 1024
    
            with sb_client.get_queue_sender(servicebus_queue.name, socket_timeout=0.5) as sender:
                with pytest.raises(MessageSizeExceededError):
                    sender.send_messages(ServiceBusMessage(too_large))

                half_too_large = "A" * int((1024 * 256) / 2)
                with pytest.raises(MessageSizeExceededError):
                    sender.send_messages([ServiceBusMessage(half_too_large), ServiceBusMessage(half_too_large)])

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_renew_message_locks(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            messages = []
            locks = 3
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              max_wait_time=5, 
                                              receive_mode=ServiceBusReceiveMode.PEEK_LOCK, 
                                              prefetch_count=10) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(locks):
                        message = ServiceBusMessage("Test message no. {}".format(i))
                        sender.send_messages(message)
    
                messages.extend(receiver.receive_messages())
                recv = True
                while recv:
                    recv = receiver.receive_messages()
                    messages.extend(recv)
    
                try:
                    for message in messages:
                        assert not message._lock_expired
                        time.sleep(5)
                        initial_expiry = message.locked_until_utc
                        receiver.renew_message_lock(message)
                        assert (message.locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    receiver.complete_message(messages[0])
                    receiver.complete_message(messages[1])
                    assert (messages[2].locked_until_utc - utc_now()) <= timedelta(seconds=60)
                    sleep_until_expired(messages[2])
                    with pytest.raises(MessageLockLostError):
                        receiver.complete_message(messages[2])

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_queue_client_conn_str_receive_handler_with_autolockrenew(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i))
                    sender.send_messages(message)
    
            renewer = AutoLockRenewer()
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 max_wait_time=10,
                                                 receive_mode=ServiceBusReceiveMode.PEEK_LOCK, 
                                                 prefetch_count=10) as receiver:
                for message in receiver:
                    if not messages:
                        messages.append(message)
                        assert not message._lock_expired
                        renewer.register(receiver, message, max_lock_renewal_duration=10)
                        print("Registered lock renew thread", message.locked_until_utc, utc_now())
                        time.sleep(10)
                        print("Finished first sleep", message.locked_until_utc)
                        assert not message._lock_expired
                        time.sleep(15) #generate autolockrenewtimeout error by going one iteration past.
                        sleep_until_expired(message)
                        print("Finished second sleep", message.locked_until_utc, utc_now())
                        assert message._lock_expired
                        try:
                            receiver.complete_message(message)
                            raise AssertionError("Didn't raise MessageLockLostError")
                        except MessageLockLostError as e:
                            assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                    else:
                        if message._lock_expired:
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            assert message._lock_expired
                            with pytest.raises(MessageLockLostError):
                                receiver.complete_message(message)
                        else:
                            assert message.delivery_count >= 1
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            messages.append(message)
                            receiver.complete_message(message)
            renewer.close()
            assert len(messages) == 11

            renewer = AutoLockRenewer(max_workers=8)
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i))
                    sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 max_wait_time=10,
                                                 receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                                 prefetch_count=10) as receiver:
                received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                for msg in received_msgs:
                    renewer.register(receiver, msg, max_lock_renewal_duration=30)
                time.sleep(10)

                for msg in received_msgs:
                    receiver.complete_message(msg)
            assert len(received_msgs) == 10
            renewer.close()

            executor = ThreadPoolExecutor(max_workers=1)
            renewer = AutoLockRenewer(executor=executor)
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(2):
                    message = ServiceBusMessage("{}".format(i))
                    sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 max_wait_time=10,
                                                 receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                                 prefetch_count=3) as receiver:
                received_msgs = receiver.receive_messages(max_message_count=3, max_wait_time=10)
                for msg in received_msgs:
                    renewer.register(receiver, msg, max_lock_renewal_duration=30)
                time.sleep(10)

                for msg in received_msgs:
                    receiver.complete_message(msg)
            assert len(received_msgs) == 2
            assert not renewer._is_max_workers_greater_than_one
            renewer.close()

            executor = ThreadPoolExecutor(max_workers=2)
            renewer = AutoLockRenewer(executor=executor)
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = ServiceBusMessage("{}".format(i))
                    sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 max_wait_time=10,
                                                 receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                                 prefetch_count=3) as receiver:
                received_msgs = receiver.receive_messages(max_message_count=3, max_wait_time=10)
                for msg in received_msgs:
                    renewer.register(receiver, msg, max_lock_renewal_duration=30)
                time.sleep(10)

                for msg in received_msgs:
                    receiver.complete_message(msg)
            assert len(received_msgs) == 3
            assert renewer._is_max_workers_greater_than_one
            renewer.close()

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_queue_client_conn_str_receive_handler_with_auto_autolockrenew(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                # The 10 iterations is "important" because it gives time for the timed out message to be received again.
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i))
                    sender.send_messages(message)
    
            renewer = AutoLockRenewer(max_lock_renewal_duration=10)
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 max_wait_time=10,
                                                 receive_mode=ServiceBusReceiveMode.PEEK_LOCK, 
                                                 prefetch_count=10,
                                                 auto_lock_renewer=renewer) as receiver:
                for message in receiver:
                    if not messages:
                        messages.append(message)
                        assert not message._lock_expired
                        print("Registered lock renew thread", message.locked_until_utc, utc_now())
                        time.sleep(10)
                        print("Finished first sleep", message.locked_until_utc)
                        assert not message._lock_expired
                        time.sleep(15) #generate autolockrenewtimeout error by going one iteration past.
                        sleep_until_expired(message)
                        print("Finished second sleep", message.locked_until_utc, utc_now())
                        assert message._lock_expired
                        try:
                            receiver.complete_message(message)
                            raise AssertionError("Didn't raise MessageLockLostError")
                        except MessageLockLostError as e:
                            assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                    else:
                        if message._lock_expired:
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            assert message._lock_expired
                            with pytest.raises(MessageLockLostError):
                                receiver.complete_message(message)
                        else:
                            assert message.delivery_count >= 1
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            messages.append(message)
                            receiver.complete_message(message)
            renewer.close()
            assert len(messages) == 11

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_time_to_live(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
               
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message_id = uuid.uuid4()
                message = ServiceBusMessage(content)
                message.time_to_live = timedelta(seconds=15)
                sender.send_messages(message)
    
            time.sleep(15)
            with sb_client.get_queue_receiver(servicebus_queue.name, prefetch_count=5) as receiver:
                messages = receiver.receive_messages(5, max_wait_time=10)
            assert not messages

            with sb_client.get_queue_receiver(
                    servicebus_queue.name,
                    sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                    max_wait_time=5,
                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as dl_receiver:
                count = 0
                for message in dl_receiver:
                    print_message(_logger, message)
                    dl_receiver.complete_message(message)
                    count += 1
            assert count == 1

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_duplicate_detection=True, dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_duplicate_detection(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
    
            message_id = uuid.uuid4()
            
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = ServiceBusMessage(str(i))
                    message.message_id = message_id
                    sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                 max_wait_time=5) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    assert message.message_id == message_id
                    receiver.complete_message(message)
                    count += 1
                assert count == 1
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_connection_closed(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
                
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = ServiceBusMessage(content)
                sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
    
            with pytest.raises(ValueError):
                receiver.complete_message(messages[0])
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_expiry(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
                       
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = ServiceBusMessage(content)
                sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep((messages[0].locked_until_utc - utc_now()).total_seconds()+1)
                assert messages[0]._lock_expired
                with pytest.raises(MessageLockLostError):
                    receiver.complete_message(messages[0])
                with pytest.raises(MessageLockLostError):
                    receiver.renew_message_lock(messages[0])
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                assert messages[0].delivery_count > 0
                receiver.complete_message(messages[0])
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_lock_renew(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = ServiceBusMessage(content)
                sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep(15)
                receiver.renew_message_lock(messages[0])
                time.sleep(15)
                receiver.renew_message_lock(messages[0])
                time.sleep(15)
                assert not messages[0]._lock_expired
                receiver.complete_message(messages[0])
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 0
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT10S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_receive_and_delete(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        if uamqp:
            transport_type = uamqp.constants.TransportType.Amqp
        else:
            transport_type = TransportType.Amqp
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string,
            logging_enable=False,
            transport_time=transport_type,
            uamqp_transport=uamqp_transport
        ) as sb_client:
                
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("Receive and delete test")
                sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                message = messages[0]
                print_message(_logger, message)
                with pytest.raises(ValueError):
                    receiver.complete_message(message)
                with pytest.raises(ValueError):
                    receiver.abandon_message(message)
                with pytest.raises(ValueError):
                    receiver.defer_message(message)
                with pytest.raises(ValueError):
                    receiver.dead_letter_message(message)
                with pytest.raises(ValueError):
                    receiver.renew_message_lock(message)
    
            time.sleep(10)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                for m in messages:
                    print_message(_logger, m)
                assert len(messages) == 0
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_batch(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
                            
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

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                # sending manually created message batch (with default pyamqp) should work for both uamqp/pyamqp
                message = ServiceBusMessageBatch()
                for each in message_content():
                    message.add_message(each)
                sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages =receiver.receive_messages(max_wait_time=10)
                recv = True
                while recv:
                    recv = receiver.receive_messages(max_wait_time=10)
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
                    receiver.complete_message(message)
                    count += 1
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_schedule_message(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            scheduled_enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    content = str(uuid.uuid4())
                    message_id = uuid.uuid4()
                    message = ServiceBusMessage(content)
                    message.message_id = message_id
                    message.scheduled_enqueue_time_utc = scheduled_enqueue_time
                    sender.send_messages(message)
    
                messages = receiver.receive_messages(max_wait_time=120)
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
                            receiver.complete_message(message)
                else:
                    raise Exception("Failed to receive schdeduled message.")
            
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_schedule_multiple_messages(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            scheduled_enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, prefetch_count=20, max_wait_time=5)

            with sender, receiver:
                content = str(uuid.uuid4())
                message_id_a = uuid.uuid4()
                message_a = ServiceBusMessage(content)
                message_a.message_id = message_id_a
                message_id_b = uuid.uuid4()
                message_b = ServiceBusMessage(content)
                message_b.message_id = message_id_b
                message_arry = [message_a, message_b]
                for message in message_arry:
                    message.application_properties = {'key': 'value'}
                    message.subject = 'label'
                    message.content_type = 'application/text'
                    message.correlation_id = 'cid'
                    message.to = 'to'
                    message.reply_to = 'reply_to'

                sender.send_messages(message_arry)

                received_messages = []
                for message in receiver:
                    received_messages.append(message)
                    receiver.complete_message(message)

                tokens = sender.schedule_messages(received_messages, scheduled_enqueue_time)
                assert len(tokens) == 2
    
                messages = receiver.receive_messages(max_wait_time=120)
                messages.extend(receiver.receive_messages(max_wait_time=5))
                if messages:
                    try:
                        data = str(messages[0])
                        assert data == content
                        assert messages[0].message_id in (message_id_a, message_id_b)
                        assert messages[0].scheduled_enqueue_time_utc == scheduled_enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc <= messages[0].enqueued_time_utc.replace(microsecond=0)
                        assert messages[0].delivery_count == 0
                        assert messages[0].application_properties
                        assert messages[0].application_properties[b'key'] == b'value'
                        assert messages[0].subject == 'label'
                        assert messages[0].content_type == 'application/text'
                        assert messages[0].correlation_id == 'cid'
                        assert messages[0].to == 'to'
                        assert messages[0].reply_to == 'reply_to'
                        assert messages[0].sequence_number
                        assert messages[0].enqueued_time_utc
                        assert messages[0].message.delivery_tag is not None
                        assert len(messages) == 2

                        if not uamqp_transport:
                            pickled = pickle.loads(pickle.dumps(messages[0]))
                            assert pickled.message_id == messages[0].message_id
                            assert pickled.scheduled_enqueue_time_utc == messages[0].scheduled_enqueue_time_utc
                            assert pickled.scheduled_enqueue_time_utc <= pickled.enqueued_time_utc.replace(microsecond=0)
                            assert pickled.delivery_count == messages[0].delivery_count
                            assert pickled.application_properties == messages[0].application_properties
                            assert pickled.application_properties[b'key'] == messages[0].application_properties[b'key']
                            assert pickled.subject == messages[0].subject
                            assert pickled.content_type == messages[0].content_type
                            assert pickled.correlation_id == messages[0].correlation_id
                            assert pickled.to == messages[0].to
                            assert pickled.reply_to == messages[0].reply_to
                            assert pickled.sequence_number
                            assert pickled.enqueued_time_utc
                    finally:
                        for message in messages:
                            receiver.complete_message(message)
                else:
                    raise Exception("Failed to receive schdeduled message.")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_cancel_scheduled_messages(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    message_a = ServiceBusMessage("Test scheduled message")
                    message_b = ServiceBusMessage("Test scheduled message")
                    tokens = sender.schedule_messages([message_a, message_b], enqueue_time)
                    assert len(tokens) == 2
    
                    sender.cancel_scheduled_messages(tokens)
    
                messages = receiver.receive_messages(max_wait_time=120)
                try:
                    assert len(messages) == 0
                except AssertionError:
                    for message in messages:
                        print(str(message))
                        receiver.complete_message(message)
                    raise


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_amqp_over_websocket(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                transport_type=TransportType.AmqpOverWebsocket,
                logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                assert sender._config.transport_type == TransportType.AmqpOverWebsocket
                message = ServiceBusMessage("Test")
                sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE) as receiver:
                assert receiver._config.transport_type == TransportType.AmqpOverWebsocket
                messages = receiver.receive_messages(max_wait_time=5)
                assert len(messages) == 1

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_queue_message_http_proxy_setting(self, uamqp_transport):
        mock_conn_str = "Endpoint=sb://mock.servicebus.windows.net/;SharedAccessKeyName=mock;SharedAccessKey=mock"
        http_proxy = {
            'proxy_hostname': '127.0.0.1',
            'proxy_port': 8899,
            'username': 'admin',
            'password': '123456'
        }

        sb_client = ServiceBusClient.from_connection_string(mock_conn_str, http_proxy=http_proxy, uamqp_transport=uamqp_transport)
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
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_message_settle_through_mgmt_link_due_to_broken_receiver_link(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("Test")
                sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=5)
                # destroy the underlying receiver link
                if uamqp_transport:
                    receiver._handler.message_handler.destroy()
                else:
                    receiver._handler._link.detach()
                assert len(messages) == 1
                receiver.complete_message(messages[0])

    @unittest.skip('hard to test')
    def test_queue_mock_auto_lock_renew_callback(self):
        # A warning to future devs: If the renew period override heuristic in registration
        # ever changes, it may break this (since it adjusts renew period if it is not short enough)

        results = []
        errors = []
        def callback_mock(renewable, error):
            results.append(renewable)
            if error:
                errors.append(error)

        receiver = MockReceiver()
        auto_lock_renew = AutoLockRenewer()
        with pytest.raises(TypeError):
            auto_lock_renew.register(Exception())  # an arbitrary invalid type.

        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1 # So we can run the test fast.
        with auto_lock_renew: # Check that it is called when the object expires for any reason (silent renew failure)
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            time.sleep(3)
            assert len(results) == 1 and results[-1]._lock_expired is True
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that in normal operation it does not get called
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage(lock_duration=5), on_lock_renew_failure=callback_mock)
            time.sleep(6)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that when a message is settled, it will not get called even after expiry
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            message._settled = True
            time.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that it is called when there is an overt renew failure
            message = MockReceivedMessage(exception_on_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            time.sleep(3)
            assert len(results) == 1 and results[-1]._lock_expired == True
            assert errors[-1]

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that it is not called when the renewer is shutdown
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            auto_lock_renew.close()
            time.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that it is not called when the receiver is shutdown
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(receiver, renewable=message, on_lock_renew_failure=callback_mock)
            message._receiver._running = False
            time.sleep(3)
            assert not results
            assert not errors

    def test_queue_mock_no_reusing_auto_lock_renew(self):

        receiver = MockReceiver()
        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1 # So we can run the test fast.
        with auto_lock_renew:
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage())
            time.sleep(3)

        with pytest.raises(ServiceBusError):
            with auto_lock_renew:
                pass

        with pytest.raises(ServiceBusError):
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage())

        auto_lock_renew = AutoLockRenewer()
        auto_lock_renew._renew_period = 1

        with auto_lock_renew:
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage())
            time.sleep(3)

        auto_lock_renew.close()

        with pytest.raises(ServiceBusError):
            with auto_lock_renew:
                pass

        with pytest.raises(ServiceBusError):
            auto_lock_renew.register(receiver, renewable=MockReceivedMessage())

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_queue_message_properties(self, uamqp_transport):

        scheduled_enqueue_time = (utc_now() + timedelta(seconds=20)).replace(microsecond=0)
        message = ServiceBusMessage(
            body='data',
            application_properties={'key': 'value'},
            session_id='sid',
            subject='label',
            content_type='application/text',
            correlation_id='cid',
            message_id='mid',
            to='to',
            reply_to='reply_to',
            reply_to_session_id='reply_to_sid',
            scheduled_enqueue_time_utc=scheduled_enqueue_time
        )

        assert message.application_properties
        assert message.application_properties['key'] == 'value'
        assert message.subject == 'label'
        assert message.content_type == 'application/text'
        assert message.correlation_id == 'cid'
        assert message.message_id == 'mid'
        assert message.to == 'to'
        assert message.reply_to == 'reply_to'
        assert message.session_id == 'sid'
        assert message.reply_to_session_id == 'reply_to_sid'
        assert message.scheduled_enqueue_time_utc == scheduled_enqueue_time

        message.partition_key = 'sid'
        new_scheduled_time = (utc_now() + timedelta(hours=5)).replace(microsecond=0)
        message.scheduled_enqueue_time_utc = new_scheduled_time
        assert message.scheduled_enqueue_time_utc == new_scheduled_time

        message.via_partition_key = None
        message.scheduled_enqueue_time_utc = None

        assert message.scheduled_enqueue_time_utc is None

        try:
            timestamp = new_scheduled_time.timestamp() * 1000
        except AttributeError:
            timestamp = calendar.timegm(new_scheduled_time.timetuple()) * 1000

        my_frame = [0,0,0]
        if uamqp_transport:
            amqp_transport = UamqpTransport
            amqp_received_message = uamqp.message.Message(
                body=[b'data'],
                annotations={
                    _X_OPT_PARTITION_KEY: b'r_key',
                    _X_OPT_VIA_PARTITION_KEY: b'r_via_key',
                    _X_OPT_SCHEDULED_ENQUEUE_TIME: timestamp,
                },
                properties={}
            )
        else:
            amqp_transport = PyamqpTransport
            amqp_received_message = Message(
                data=[b'data'],
                message_annotations={
                    _X_OPT_PARTITION_KEY: b'r_key',
                    _X_OPT_VIA_PARTITION_KEY: b'r_via_key',
                    _X_OPT_SCHEDULED_ENQUEUE_TIME: timestamp,
                },
                properties={}
            )
        received_message = ServiceBusReceivedMessage(amqp_received_message, receiver=None, frame=my_frame, amqp_transport=amqp_transport)
        assert received_message.scheduled_enqueue_time_utc == new_scheduled_time

        new_scheduled_time = utc_now() + timedelta(hours=1, minutes=49, seconds=32)

        received_message.scheduled_enqueue_time_utc = new_scheduled_time

        assert received_message.scheduled_enqueue_time_utc == new_scheduled_time

        received_message.scheduled_enqueue_time_utc = None

        assert message.scheduled_enqueue_time_utc is None

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_receive_batch_without_setting_prefetch(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            def message_content():
                for i in range(20):
                    yield ServiceBusMessage(
                        body="Test message",
                        # application_properties={'key': 'value'},
                        subject='1st',
                        # content_type='application/text',
                        # correlation_id='cid',
                        # message_id='mid',
                        # to='to',
                        # reply_to='reply_to',
                        # time_to_live=timedelta(seconds=60)
                    )

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10)

            with sender, receiver:
                message = ServiceBusMessageBatch()
                for each in message_content():
                    message.add_message(each)
                sender.send_messages(message)

                receive_counter = 0
                message_1st_received_cnt = 0
                message_2nd_received_cnt = 0
                while message_1st_received_cnt < 20 or message_2nd_received_cnt < 20:
                    messages = []
                    for message in receiver:
                        messages.append(message)
                    if not messages:
                        break
                    receive_counter += 1
                    for message in messages:
                        print_message(_logger, message)
                        # assert b''.join(message.body) == b'Test message'
                        # assert message.application_properties[b'key'] == b'value'
                        # assert message.content_type == 'application/text'
                        # assert message.correlation_id == 'cid'
                        # assert message.message_id == 'mid'
                        # assert message.to == 'to'
                        # assert message.reply_to == 'reply_to'
                        # assert message.time_to_live == timedelta(seconds=60)

                        if message.subject == '1st':
                            message_1st_received_cnt += 1
                            receiver.complete_message(message)
                            message.subject = '2nd'
                            sender.send_messages(message)  # resending received message
                        elif message.subject == '2nd':
                            message_2nd_received_cnt += 1
                            receiver.complete_message(message)

                assert message_1st_received_cnt == 20 and message_2nd_received_cnt == 20
                # Network/server might be unstable making flow control ineffective in the leading rounds of connection iteration
                assert receive_counter < 10  # Dynamic link credit issuing come info effect

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_receiver_alive_after_timeout(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("0")
                message_1 = ServiceBusMessage("1")
                sender.send_messages([message, message_1])

                messages = []
                with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                    
                    for message in receiver:
                        messages.append(message)
                        break

                    for message in receiver:
                        messages.append(message)

                    for message in messages:
                        receiver.complete_message(message)

                    assert len(messages) == 2
                    assert str(messages[0]) == "0"
                    assert str(messages[1]) == "1"

                    message_2 = ServiceBusMessage("2")
                    message_3 = ServiceBusMessage("3")
                    sender.send_messages([message_2, message_3])

                    for message in receiver:
                        messages.append(message)
                        for message in receiver:
                            messages.append(message)

                    assert len(messages) == 4
                    assert str(messages[2]) == "2"
                    assert str(messages[3]) == "3"

                    for message in messages[2:]:
                        receiver.complete_message(message)

                    messages = receiver.receive_messages()
                    assert not messages

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True, lock_duration='PT5M')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_receive_keep_conn_alive(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10)

            with sender, receiver:
                sender.send_messages([ServiceBusMessage("message1"), ServiceBusMessage("message2")])

                messages = []
                for message in receiver:
                    messages.append(message)

                receiver_handler = receiver._handler
                assert len(messages) == 2
                time.sleep(4 * 60 + 5)  # 240s is the service defined connection idle timeout
                receiver.renew_message_lock(messages[0])  # check mgmt link operation
                receiver.complete_message(messages[0])
                receiver.complete_message(messages[1])  # check receiver link operation

                time.sleep(60)  # sleep another one minute to ensure we pass the lock_duration time

                messages = []
                for message in receiver:
                    messages.append(message)

                assert len(messages) == 0  # make sure messages are removed from the queue
                assert receiver_handler == receiver._handler  # make sure no reconnection happened

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_receiver_sender_resume_after_link_timeout(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("0")
                sender.send_messages(message)

                time.sleep(60 * 5)

                message_1 = ServiceBusMessage("1")
                sender.send_messages(message_1)

                messages = []
                with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                    
                    for message in receiver:
                        messages.append(message)
                assert len(messages) == 2
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_twice(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        if uamqp:
            transport_type = uamqp.constants.TransportType.AmqpOverWebsocket
        else:
            transport_type = TransportType.AmqpOverWebsocket

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False,
            transport_type=transport_type, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("ServiceBusMessage")
                message2 = ServiceBusMessage("Message2")
                # first test batch message resending.
                batch_message = sender.create_message_batch()
                batch_message._from_list([message, message2])  # pylint: disable=protected-access
                sender.send_messages(batch_message)
                sender.send_messages(batch_message)
                messages = []
                with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=20) as receiver:
                    for message in receiver:
                        messages.append(message)
                        receiver.complete_message(message)
                    assert len(messages) == 4
                # then normal message resending
                sender.send_messages(message)
                sender.send_messages(message)
                expected_count = 2
                if not uamqp_transport:
                    pickled_recvd = pickle.loads(pickle.dumps(messages[0]))
                    sender.send_messages(pickled_recvd)
                    expected_count = 3
                messages = []
                with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=20) as receiver:
                    for message in receiver:
                        messages.append(message)
                        receiver.complete_message(message)
                    assert len(messages) == expected_count


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_receiver_invalid_mode(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            with pytest.raises(ValueError):
                with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  receive_mode=2) as receiver:
                
                    raise Exception("Should not get here, should fail fast.")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_receiver_invalid_autolockrenew_mode(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            with pytest.raises(ValueError):
                with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                                  auto_lock_renewer=AutoLockRenewer()) as receiver:
                
                    raise Exception("Should not get here, should fail fast because RECEIVE_AND_DELETE messages cannot be autorenewed.")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_message_inner_amqp_properties(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        message = ServiceBusMessage("body")

        message.raw_amqp_message.properties.subject = "subject"
        message.raw_amqp_message.application_properties = {b"application_properties":1}
        message.raw_amqp_message.annotations = {b"annotations":2}
        message.raw_amqp_message.delivery_annotations = {b"delivery_annotations":3}
        message.raw_amqp_message.header.priority = 5
        message.raw_amqp_message.footer = {b"footer":6}

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(message)
                with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                    message = receiver.receive_messages()[0]
                    assert message.raw_amqp_message.application_properties != None \
                        and message.raw_amqp_message.annotations != None \
                        and message.raw_amqp_message.delivery_annotations != None \
                        and message.raw_amqp_message.footer != None \
                        and message.raw_amqp_message.properties != None \
                        and message.raw_amqp_message.header != None

                    assert message.raw_amqp_message.properties.subject == b"subject"
                    assert message.raw_amqp_message.application_properties[b"application_properties"] == 1
                    assert message.raw_amqp_message.annotations[b"annotations"] == 2
                    assert message.raw_amqp_message.delivery_annotations[b"delivery_annotations"] == 3
                    assert message.raw_amqp_message.header.priority == 5
                    assert message.raw_amqp_message.footer[b"footer"] == 6

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_timeout(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        def _hack_amqp_sender_run(self, **kwargs):
            time.sleep(6)  # sleep until timeout
            if uamqp_transport:
                self.message_handler.work()
                self._waiting_messages = 0
                self._pending_messages = self._filter_pending()
                if self._backoff and not self._waiting_messages:
                    _logger.info("Client told to backoff - sleeping for %r seconds", self._backoff)
                    self._connection.sleep(self._backoff)
                    self._backoff = 0
                self._connection.work()
            else:
                try:
                    self._link.update_pending_deliveries()
                    self._connection.listen(wait=self._socket_timeout, **kwargs)
                except ValueError:
                    self._shutdown = True
                    return False
            return True

        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                # this one doesn't need to reset the method, as it's hacking the method on the instance
                sender._handler._client_run = types.MethodType(_hack_amqp_sender_run, sender._handler)
                with pytest.raises(OperationTimeoutError):
                    sender.send_messages(ServiceBusMessage("body"), timeout=5)

        if not uamqp_transport:
            # Amqp
            with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                uamqp_transport=uamqp_transport
            ) as sb_client:
                with sb_client.get_queue_sender(servicebus_queue.name, socket_timeout=0.6) as sender:
                    payload = "A" * 250 * 1024
                    sender.send_messages(ServiceBusMessage(payload))

            if uamqp:
                transport_type = uamqp.constants.TransportType.AmqpOverWebsocket
            else:
                transport_type = TransportType.AmqpOverWebsocket
            # AmqpOverWebsocket
            with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                transport_type=transport_type,
                uamqp_transport=uamqp_transport
            ) as sb_client:
                with sb_client.get_queue_sender(servicebus_queue.name, socket_timeout=0.8) as sender:
                    payload = "A" * 250 * 1024
                    sender.send_messages(ServiceBusMessage(payload))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_large_message_receive(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        # Amqp
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string,
            uamqp_transport=uamqp_transport
        ) as sb_client:
            with sb_client.get_queue_sender(servicebus_queue.name, socket_timeout=0.6) as sender:
                payload = "A" * 250 * 1024
                sender.send_messages(ServiceBusMessage(payload))

        if uamqp:
            transport_type = uamqp.constants.TransportType.AmqpOverWebsocket
        else:
            transport_type = TransportType.AmqpOverWebsocket
        # AmqpOverWebsocket
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string,
            transport_type=transport_type,
            uamqp_transport=uamqp_transport
        ) as sb_client:
            with sb_client.get_queue_sender(servicebus_queue.name, socket_timeout=0.8) as sender:
                payload = "A" * 250 * 1024
                sender.send_messages(ServiceBusMessage(payload))

        # ReceiveMessages
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                messages = receiver.receive_messages(max_message_count=5, max_wait_time=5)
                for message in messages:
                    if not uamqp_transport:
                        assert message._delivery_id is not None
                        assert message._message.data[0].decode("utf-8")  == "A" * 250 * 1024
                    receiver.complete_message(message)  # complete messages             

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_mgmt_operation_timeout(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        if uamqp_transport:
            def hack_mgmt_execute(self, operation, op_type, message, timeout=0):
                start_time = self._counter.get_current_ms()
                operation_id = str(uuid.uuid4())
                self._responses[operation_id] = None

                time.sleep(6)  # sleep until timeout
                while not self._responses[operation_id] and not self.mgmt_error:
                    if timeout > 0:
                        now = self._counter.get_current_ms()
                        if (now - start_time) >= timeout:
                            raise uamqp.compat.TimeoutException("Failed to receive mgmt response in {}ms".format(timeout))
                    self.connection.work()
                if self.mgmt_error:
                    raise self.mgmt_error
                response = self._responses.pop(operation_id)
                return response

            original_execute_method = uamqp.mgmt_operation.MgmtOperation.execute
            # hack the mgmt method on the class, not on an instance, so it needs reset
        else:
            def hack_mgmt_execute(self, message, operation=None, operation_type=None, timeout=0):
                start_time = time.time()
                operation_id = str(uuid.uuid4())
                self._responses[operation_id] = None

                time.sleep(6)  # sleep until timeout
                while not self._responses[operation_id] and not self._mgmt_error:
                    if timeout and timeout > 0:
                        now = time.time()
                        if (now - start_time) >= timeout:
                            raise TimeoutError("Failed to receive mgmt response in {}ms".format(timeout))
                    self._connection.listen()
                if self._mgmt_error:
                    self._responses.pop(operation_id)
                    raise self._mgmt_error

                response = self._responses.pop(operation_id)
                return response

            original_execute_method = management_operation.ManagementOperation.execute
            # hack the mgmt method on the class, not on an instance, so it needs reset

        try:
            if uamqp_transport:
                uamqp.mgmt_operation.MgmtOperation.execute = hack_mgmt_execute
            else:
                management_operation.ManagementOperation.execute = hack_mgmt_execute
            with ServiceBusClient.from_connection_string(
                    servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    with pytest.raises(OperationTimeoutError):
                        scheduled_time_utc = utc_now() + timedelta(seconds=30)
                        sender.schedule_messages(ServiceBusMessage("ServiceBusMessage to be scheduled"), scheduled_time_utc, timeout=5)
        finally:
            # must reset the mgmt execute method, otherwise other test cases would use the hacked execute method, leading to timeout error
            if uamqp_transport:
                uamqp.mgmt_operation.MgmtOperation.execute = original_execute_method
            else:
                management_operation.ManagementOperation.execute = original_execute_method

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', lock_duration='PT5S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_operation_negative(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        if uamqp_transport:
            def _hack_amqp_message_complete(cls):
                raise RuntimeError()

            def _hack_amqp_mgmt_request(cls, message, operation, op_type=None, node=None, callback=None, **kwargs):
                raise uamqp.errors.AMQPConnectionError()

            def _hack_sb_receiver_settle_message(self, message, settle_operation, dead_letter_reason=None, dead_letter_error_description=None):
                raise uamqp.errors.AMQPError()
        else:
            def _hack_amqp_message_complete(cls, _, settlement):
                    if settlement == 'completed':
                        raise RuntimeError()

            def _hack_amqp_mgmt_request(cls, message, operation, op_type=None, node=None, callback=None, **kwargs):
                raise error.AMQPConnectionError(error.ErrorCondition.ConnectionCloseForced)

            def _hack_sb_receiver_settle_message(self, message, settle_operation, dead_letter_reason=None, dead_letter_error_description=None):
                raise error.AMQPException(error.ErrorCondition.ClientError)

        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)
            if not uamqp_transport:
                original_settlement = client.ReceiveClient.settle_messages
            try:
                with sender, receiver:
                    # negative settlement via receiver link
                    sender.send_messages(ServiceBusMessage("body"), timeout=10)
                    message = receiver.receive_messages()[0]
                    if uamqp_transport:
                        message._message.accept = types.MethodType(_hack_amqp_message_complete, message._message)
                    else:
                        client.ReceiveClient.settle_messages = types.MethodType(_hack_amqp_message_complete, receiver._handler)
                    receiver.complete_message(message)  # settle via mgmt link

                    if uamqp_transport:
                        origin_amqp_client_mgmt_request_method = uamqp.AMQPClient.mgmt_request
                        try:
                            uamqp.AMQPClient.mgmt_request = _hack_amqp_mgmt_request
                            with pytest.raises(ServiceBusConnectionError):
                                receiver.peek_messages()
                        finally:
                            uamqp.AMQPClient.mgmt_request = origin_amqp_client_mgmt_request_method
                    else:
                        origin_amqp_client_mgmt_request_method = client.AMQPClient.mgmt_request
                        try:
                            client.AMQPClient.mgmt_request = _hack_amqp_mgmt_request
                            with pytest.raises(ServiceBusConnectionError):
                                receiver.peek_messages()
                        finally:
                            client.AMQPClient.mgmt_request = origin_amqp_client_mgmt_request_method

                    sender.send_messages(ServiceBusMessage("body"), timeout=10)

                    message = receiver.receive_messages()[0]

                    origin_sb_receiver_settle_message_method = receiver._settle_message
                    receiver._settle_message = types.MethodType(_hack_sb_receiver_settle_message, receiver)
                    with pytest.raises(ServiceBusError):
                        receiver.complete_message(message)

                    receiver._settle_message = origin_sb_receiver_settle_message_method
                    message = receiver.receive_messages(max_wait_time=6)[0]
                    receiver.complete_message(message)
            finally:
                if not uamqp_transport:
                    client.ReceiveClient.settle_messages = original_settlement

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_send_message_no_body(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, uamqp_transport=uamqp_transport)

        with sb_client.get_queue_sender(servicebus_queue.name) as sender:
            sender.send_messages(ServiceBusMessage(body=None))

        with sb_client.get_queue_receiver(servicebus_queue.name,  
                                          max_wait_time=10) as receiver:
            message = receiver.next()
            assert message.body is None
            receiver.complete_message(message)

    def test_send_message_alternate_body_types(self, **kwargs):
        with pytest.raises(TypeError):
            message = ServiceBusMessage(body=['1','2'])
        with pytest.raises(TypeError):
            message = ServiceBusMessage(body=[None, None])
        with pytest.raises(TypeError):
            message = ServiceBusMessage(body=['1', None])
        with pytest.raises(TypeError):
            message = ServiceBusMessage(body=[Exception()])
        with pytest.raises(TypeError):
            message = ServiceBusMessage(body={})
        with pytest.raises(TypeError):
            message = ServiceBusMessage(body=Exception())

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_by_servicebus_client_enum_case_sensitivity(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        # Note: This test is currently intended to enforce case-sensitivity.  If we eventually upgrade to the Fancy Enums being used with new autorest,
        # we may want to tweak this.
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE.value, 
                                              max_wait_time=5) as receiver:
                pass
            with pytest.raises(ValueError):
                with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  receive_mode=str.upper(ServiceBusReceiveMode.RECEIVE_AND_DELETE.value),
                                                  max_wait_time=5) as receiver:
                    raise Exception("Should not get here, should be case sensitive.")
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              sub_queue=ServiceBusSubQueue.DEAD_LETTER.value,
                                              max_wait_time=5) as receiver:
                pass
            with pytest.raises(ValueError):
                with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  sub_queue=str.upper(ServiceBusSubQueue.DEAD_LETTER.value),
                                                  max_wait_time=5) as receiver:
                    raise Exception("Should not get here, should be case sensitive.")

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_dict_messages(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:

                message_dict = {"body": "Message"}
                message2_dict = {"body": "Message2"}
                list_message_dicts = [message_dict, message2_dict]

                # send single dict
                sender.send_messages(message_dict)

                # send list of dicts
                sender.send_messages(list_message_dicts)

                # create and send BatchMessage with dicts
                batch_message = sender.create_message_batch()
                batch_message._from_list(list_message_dicts)  # pylint: disable=protected-access
                batch_message.add_message(message_dict)
                sender.send_messages(batch_message)

                received_messages = []
                with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                    for message in receiver:
                        received_messages.append(message)
                assert len(received_messages) == 6

                batch_message = sender.create_message_batch(max_size_in_bytes=73)
                for _ in range(2):
                    try:
                        batch_message.add_message(message_dict)
                    except ValueError:
                        break
                sender.send_messages(batch_message)
                received_messages = []
                with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                    for message in receiver:
                        received_messages.append(message)
                assert len(received_messages) == 1
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_mapping_messages(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        class MappingMessage(DictMixin):
            def __init__(self, content):
                self.body = content
                self.message_id = 'foo'
        
        class BadMappingMessage(DictMixin):
            def __init__(self):
                self.message_id = 'foo'

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:

                message_dict = MappingMessage("Message")
                message2_dict = MappingMessage("Message2")
                message3_dict = BadMappingMessage()
                list_message_dicts = [message_dict, message2_dict]

                # send single dict
                sender.send_messages(message_dict)

                # send list of dicts
                sender.send_messages(list_message_dicts)

                # send bad dict
                with pytest.raises(TypeError):
                    sender.send_messages(message3_dict)

                # create and send BatchMessage with dicts
                batch_message = sender.create_message_batch()
                batch_message._from_list(list_message_dicts)  # pylint: disable=protected-access
                batch_message.add_message(message_dict)
                sender.send_messages(batch_message)

                received_messages = []
                with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5) as receiver:
                    for message in receiver:
                        received_messages.append(message)
                assert len(received_messages) == 6

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_dict_messages_error_badly_formatted_dicts(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:

                message_dict = {"bad_key": "Message"}
                message2_dict = {"bad_key": "Message2"}
                list_message_dicts = [message_dict, message2_dict]

                # send single dict
                with pytest.raises(TypeError):
                    sender.send_messages(message_dict)

                # send list of dicts
                with pytest.raises(TypeError):
                    sender.send_messages(list_message_dicts)

                # create and send BatchMessage with dicts
                batch_message = sender.create_message_batch()
                with pytest.raises(TypeError):
                    batch_message._from_list(list_message_dicts)  # pylint: disable=protected-access

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_dict_messages_scheduled(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            content = "Test scheduled message"
            message_id = uuid.uuid4()
            message_id2 = uuid.uuid4()
            scheduled_enqueue_time = (utc_now() + timedelta(minutes=0.05)).replace(microsecond=0)
            message_dict = {"message_id": message_id, "body": content}
            message2_dict = {"message_id": message_id2, "body": content}
            list_message_dicts = [message_dict, message2_dict]
            
            # send single dict
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    tokens = sender.schedule_messages(message_dict, scheduled_enqueue_time)
                    assert len(tokens) == 1
    
                messages = receiver.receive_messages(max_wait_time=20)
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
                            receiver.complete_message(m)
                else:
                    raise Exception("Failed to receive schdeduled message.")

            # send list of dicts
            with sb_client.get_queue_receiver(servicebus_queue.name, prefetch_count=20) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    tokens = sender.schedule_messages(list_message_dicts, scheduled_enqueue_time)
                    assert len(tokens) == 2
    
                messages = receiver.receive_messages(max_wait_time=20)
                messages.extend(receiver.receive_messages(max_wait_time=5))
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
                            receiver.complete_message(m)
                else:
                    raise Exception("Failed to receive schdeduled message.")                    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_dict_messages_scheduled_error_badly_formatted_dicts(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            content = "Test scheduled message"
            message_id = uuid.uuid4()
            message_id2 = uuid.uuid4()
            scheduled_enqueue_time = (utc_now() + timedelta(minutes=0.1)).replace(microsecond=0)
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    message_dict = {"message_id": message_id, "bad_key": content}
                    message2_dict = {"message_id": message_id2, "bad_key": content}
                    list_message_dicts = [message_dict, message2_dict]
                    with pytest.raises(TypeError):
                        sender.schedule_messages(message_dict, scheduled_enqueue_time)
                    with pytest.raises(TypeError):
                        sender.schedule_messages(list_message_dicts, scheduled_enqueue_time)

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_receive_iterator_resume_after_link_detach(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):

        def hack_iter_next_mock_error(self, wait_time=None):
            try:
                self._receive_context.set()
                self._open()
                # when trying to receive the second message (execution_times is 1), raising LinkDetach error to mock 10 mins idle timeout
                if self.execution_times == 1:
                    # TODO: update uamqp errors to pyamqp
                    if uamqp_transport:
                        from uamqp.errors import LinkDetach
                        from uamqp.constants import ErrorCodes
                        error = LinkDetach
                        error_condition = ErrorCodes
                    else:
                        from azure.servicebus._pyamqp.error import ErrorCondition, AMQPLinkError
                        error = AMQPLinkError
                        error_condition = ErrorCondition

                    self.execution_times += 1
                    self.error_raised = True
                    raise error(error_condition.LinkDetachForced)
                else:
                    self.execution_times += 1
                if not self._message_iter:
                    if uamqp_transport:
                        self._message_iter = self._handler.receive_messages_iter()
                    else:
                        self._message_iter = self._handler.receive_messages_iter(timeout=wait_time)
                amqp_message = next(self._message_iter)
                message = self._build_received_message(amqp_message)
                return message
            finally:
                self._receive_context.clear()

        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(
                    [ServiceBusMessage("test1"), ServiceBusMessage("test2"), ServiceBusMessage("test3")]
                )
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10) as receiver:
                receiver.execution_times = 0
                receiver.error_raised = False
                receiver._iter_next = types.MethodType(hack_iter_next_mock_error, receiver)
                res = []
                for msg in receiver:
                    receiver.complete_message(msg)
                    res.append(msg)
                assert len(res) == 3
                assert receiver.error_raised
                assert receiver.execution_times >= 4  # at least 1 failure and 3 successful receiving iterator

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_queue_send_amqp_annotated_message(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):

        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False, uamqp_transport=uamqp_transport) as sb_client:
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

            with pytest.raises(ValueError):
                AmqpAnnotatedMessage(data_body=data_body, value_body=value_body)
            with pytest.raises(ValueError):
                AmqpAnnotatedMessage()

            content = "normalmessage"
            dict_message = {"body": content}
            sb_message = ServiceBusMessage(body=content)
            message_with_ttl = AmqpAnnotatedMessage(data_body=data_body, header=AmqpMessageHeader(time_to_live=60000))
            if uamqp_transport:
                amqp_transport = UamqpTransport
            else:
                amqp_transport = PyamqpTransport
            amqp_with_ttl = amqp_transport.to_outgoing_amqp_message(message_with_ttl)
            assert amqp_with_ttl.properties.absolute_expiry_time == amqp_with_ttl.properties.creation_time + amqp_with_ttl.header.ttl

            recv_data_msg = recv_sequence_msg = recv_value_msg = normal_msg = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=10) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    batch = sender.create_message_batch()
                    batch.add_message(data_message)
                    batch.add_message(value_message)
                    batch.add_message(sequence_message)
                    batch.add_message(dict_message)
                    batch.add_message(sb_message)

                    sender.send_messages(batch)
                    sender.send_messages([data_message, value_message, sequence_message, dict_message, sb_message])
                    sender.send_messages(data_message)
                    sender.send_messages(value_message)
                    sender.send_messages(sequence_message)

                    for message in receiver:
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

                    assert recv_sequence_msg == 3
                    assert recv_data_msg == 3
                    assert recv_value_msg == 3
                    assert normal_msg == 4


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_state_scheduled(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, uamqp_transport=uamqp_transport) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            for i in range(10):
                message = ServiceBusMessage("message no. {}".format(i))
                scheduled_time_utc = datetime.utcnow() + timedelta(seconds=30)
                sequence_number = sender.schedule_messages(message, scheduled_time_utc)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name)
            with receiver:
                for msg in receiver.peek_messages():
                    assert msg.state == ServiceBusMessageState.SCHEDULED


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_state_deferred(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, uamqp_transport=uamqp_transport) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            for i in range(10):
                message = ServiceBusMessage("message no. {}".format(i))
                sender.send_messages(message)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name)
            deferred_messages = []
            with receiver:
                received_msgs = receiver.receive_messages()
                for message in received_msgs:
                    assert message.state == ServiceBusMessageState.ACTIVE
                    deferred_messages.append(message.sequence_number)
                    receiver.defer_message(message)
                if deferred_messages:
                    received_deferred_msg = receiver.receive_deferred_messages(
                        sequence_numbers=deferred_messages
                        )
                for message in received_deferred_msg:
                    assert message.state == ServiceBusMessageState.DEFERRED
