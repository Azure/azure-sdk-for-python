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
import uuid
from datetime import datetime, timedelta
import calendar

import uamqp
from azure.servicebus import ServiceBusClient, AutoLockRenew, TransportType
from azure.servicebus._common.message import Message, PeekMessage, ReceivedMessage, BatchMessage
from azure.servicebus._common.constants import (
    ReceiveSettleMode,
    _X_OPT_LOCK_TOKEN,
    _X_OPT_PARTITION_KEY,
    _X_OPT_VIA_PARTITION_KEY,
    _X_OPT_SCHEDULED_ENQUEUE_TIME
)
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
from servicebus_preparer import CachedServiceBusNamespacePreparer, ServiceBusQueuePreparer, CachedServiceBusQueuePreparer
from utilities import get_logger, print_message, sleep_until_expired
from mocks import MockReceivedMessage

_logger = get_logger(logging.DEBUG)


# A note regarding live_test_only.
# Old servicebus tests were not written to work on both stubs and live entities.
# This disables those tests for non-live scenarios, and should be removed as tests
# are ported to offline-compatible code.
class ServiceBusQueueTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_receive_and_delete_reconnect_interaction(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        # Note: This test was to guard against github issue 7079
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False)

        with sb_client.get_queue_sender(servicebus_queue.name) as sender:
            for i in range(5):
                sender.send_messages(Message("Message {}".format(i)))

        with sb_client.get_queue_receiver(servicebus_queue.name, 
                                          mode=ReceiveSettleMode.ReceiveAndDelete, 
                                          idle_timeout=10) as receiver:
            batch = receiver.receive_messages()
            count = len(batch)

            for message in receiver:
               _logger.debug(message)
               count += 1
            assert count == 5

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_github_issue_6178(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    sender.send_messages(Message("Message {}".format(i)))

                    with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=60) as receiver:
                        for message in receiver:
                            _logger.debug(message)
                            _logger.debug(message.sequence_number)
                            _logger.debug(message.enqueued_time_utc)
                            _logger.debug(message._lock_expired)
                            message.complete()
                            time.sleep(40)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_queue_client_conn_str_receive_handler_peeklock(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Handler message no. {}".format(i))
                    message.properties = {'key': 'value'}
                    message.label = 'label'
                    message.content_type = 'application/text'
                    message.correlation_id = 'cid'
                    message.message_id = str(i)
                    message.partition_key = 'pk'
                    message.via_partition_key = 'via_pk'
                    message.to = 'to'
                    message.reply_to = 'reply_to'
                    sender.send_messages(message)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5)
            count = 0
            for message in receiver:
                print_message(_logger, message)
                assert message.delivery_count == 0
                assert message.properties
                assert message.properties[b'key'] == b'value'
                assert message.label == 'label'
                assert message.content_type == 'application/text'
                assert message.correlation_id == 'cid'
                assert message.message_id == str(count)
                assert message.partition_key == 'pk'
                assert message.via_partition_key == 'via_pk'
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
                message.complete()

            assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_queue_client_send_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                messages = []
                for i in range(10):
                    message = Message("Handler message no. {}".format(i))
                    message.partition_key = 'pkey'
                    message.via_partition_key = 'vpkey'
                    message.time_to_live = timedelta(seconds=60)
                    message.scheduled_enqueue_time_utc = utc_now() + timedelta(seconds=60)
                    message.partition_key = None
                    message.via_partition_key = None
                    message.time_to_live = None
                    message.scheduled_enqueue_time_utc = None
                    message.session_id = None
                    messages.append(message)
                sender.send_messages(messages)

            with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    assert message.delivery_count == 0
                    assert not message.properties
                    assert not message.label
                    assert not message.content_type
                    assert not message.correlation_id
                    assert not message.partition_key
                    assert not message.via_partition_key
                    assert not message.to
                    assert not message.reply_to
                    assert not message.scheduled_enqueue_time_utc
                    assert not message.time_to_live
                    assert not message.session_id
                    assert not message.reply_to_session_id
                    count += 1
                    message.complete()

                assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Handler message no. {}".format(i))
                    sender.send_messages(message)
    
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              mode=ReceiveSettleMode.ReceiveAndDelete, 
                                              idle_timeout=8) as receiver:
                for message in receiver:
                    assert not message.properties
                    assert not message.label
                    assert not message.content_type
                    assert not message.correlation_id
                    assert not message.partition_key
                    assert not message.via_partition_key
                    assert not message.to
                    assert not message.reply_to
                    assert not message.scheduled_enqueue_time_utc
                    assert not message.time_to_live
                    assert not message.session_id
                    assert not message.reply_to_session_id
                    messages.append(message)
                    with pytest.raises(MessageAlreadySettled):
                        message.complete()
    
            assert len(messages) == 10
            assert not receiver._running
            time.sleep(30)
    
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              mode=ReceiveSettleMode.ReceiveAndDelete, 
                                              idle_timeout=5) as receiver:
                for message in receiver:
                    messages.append(message)
                assert len(messages) == 0
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_queue_client_conn_str_receive_handler_with_stop(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("Stop message no. {}".format(i))
                    sender.send_messages(message)
    
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                for message in receiver:
                    messages.append(message)
                    message.complete()
                    if len(messages) >= 5:
                        break
                    
                assert receiver._running
                assert len(messages) == 5

                with receiver:
                    for message in receiver:
                        messages.append(message)
                        message.complete()
                        if len(messages) >= 5:
                            break
                        
                assert not receiver._running
                assert len(messages) == 6
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_simple(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              idle_timeout=5, 
                                              mode=ReceiveSettleMode.PeekLock) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Iter message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    message.complete()
                    with pytest.raises(MessageAlreadySettled):
                        message.complete()
                    with pytest.raises(MessageAlreadySettled):
                        message.renew_lock()
                    count += 1

                with pytest.raises(StopIteration):
                    next(receiver)
            assert count == 10
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_conn_str_client_iter_messages_with_abandon(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Abandoned message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    if not message.delivery_count:
                        count += 1
                        message.abandon() 
                    else:
                        assert message.delivery_count == 1
                        message.complete()
    
            assert count == 10
    
            with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=20, mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    message.complete()
                    count += 1
            assert count == 0

    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_with_defer(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            deferred_messages = []
            with sb_client.get_queue_receiver(
                servicebus_queue.name, 
                idle_timeout=5, 
                mode=ReceiveSettleMode.PeekLock) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Deferred message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()
    
            assert count == 10
            with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5, mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    message.complete()
                    count += 1
            assert count == 0
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                 idle_timeout=5, 
                                                 mode=ReceiveSettleMode.PeekLock) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Deferred message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()
    
                assert count == 10
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    message.complete()
                
                with pytest.raises(ServiceBusError):
                    receiver.receive_deferred_messages(deferred_messages)
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_complete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                deferred_messages = []
                for i in range(10):
                    message = Message("Deferred message no. {}".format(i), session_id="test_session")
                    sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                        idle_timeout=5, 
                                        mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()
    
            assert count == 10
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                           idle_timeout=5, 
                                           mode=ReceiveSettleMode.PeekLock) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    assert message.lock_token
                    assert message.locked_until_utc
                    assert message._receiver
                    message.renew_lock()
                    message.complete()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                deferred_messages = []
                for i in range(10):
                    message = Message("Deferred message no. {}".format(i))
                    sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              idle_timeout=5, 
                                              mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()
    
            assert count == 10
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                        idle_timeout=5) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    message.dead_letter(reason="Testing reason", description="Testing description")
    
            count = 0
            with sb_client.get_queue_deadletter_receiver(servicebus_queue.name,
                                                   idle_timeout=5) as receiver:
                for message in receiver:
                    count += 1
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    message.complete()
            assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    sender.send_messages(Message("Deferred message no. {}".format(i)))

            deferred_messages = []
            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5) as receiver:
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()
    
            assert count == 10
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              mode=ReceiveSettleMode.ReceiveAndDelete, 
                                              idle_timeout=5) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ReceivedMessage)
                    with pytest.raises(MessageAlreadySettled):
                        message.complete()
                with pytest.raises(ServiceBusError):
                    deferred = receiver.receive_deferred_messages(deferred_messages)
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_not_found(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            deferred_messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                 idle_timeout=5, 
                                                 mode=ReceiveSettleMode.PeekLock) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(3):
                        message = Message("Deferred message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    message.defer()
    
                assert count == 3
    
                with pytest.raises(ServiceBusError):
                    deferred = receiver.receive_deferred_messages([3, 4])
    
                with pytest.raises(ServiceBusError):
                    deferred = receiver.receive_deferred_messages([5, 6, 7])

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_receive_batch_with_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                           idle_timeout=5, 
                                           mode=ReceiveSettleMode.PeekLock, 
                                           prefetch=10) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Dead lettered message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                messages = receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        count += 1
                        message.dead_letter(reason="Testing reason", description="Testing description")
                    messages = receiver.receive_messages()
    
            assert count == 10
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              idle_timeout=5, 
                                              mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    message.complete()
                    count += 1
            assert count == 0

            with sb_client.get_queue_deadletter_receiver(
                    servicebus_queue.name,
                    idle_timeout=5,
                    mode=ReceiveSettleMode.PeekLock) as dl_receiver:
                count = 0
                for message in dl_receiver:
                    message.complete()
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
    def test_queue_by_servicebus_client_receive_batch_with_retrieve_deadletter(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                           idle_timeout=5,
                                           mode=ReceiveSettleMode.PeekLock, 
                                           prefetch=10) as receiver:
            
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = Message("Dead lettered message no. {}".format(i))
                        sender.send_messages(message)
    
                count = 0
                messages = receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        message.dead_letter(reason="Testing reason", description="Testing description")
                        count += 1
                    messages = receiver.receive_messages()
    
                receiver.receive_messages(1,5)
    
            assert count == 10

            with sb_client.get_queue_deadletter_receiver(
                    servicebus_queue.name,
                    idle_timeout=5,
                    mode=ReceiveSettleMode.PeekLock) as dl_receiver:
                count = 0
                for message in dl_receiver:
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    message.complete()
                    count += 1
            assert count == 10
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_session_fail(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with pytest.raises(ServiceBusConnectionError):
                sb_client.get_queue_session_receiver(servicebus_queue.name, session_id="test")._open_with_retry()
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(Message("test session sender", session_id="test"))
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_browse_messages_client(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = Message("Test message no. {}".format(i))
                    sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.peek_messages(5)
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
    def test_queue_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            receiver = sb_client.get_queue_receiver(servicebus_queue.name,
                                           idle_timeout=5,
                                           mode=ReceiveSettleMode.PeekLock)
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            with receiver, sender:
                for i in range(5):
                    message = Message(
                        body="Test message",
                        properties={'key': 'value'},
                        label='label',
                        content_type='application/text',
                        correlation_id='cid',
                        message_id='mid',
                        partition_key='pk',
                        via_partition_key='via_pk',
                        to='to',
                        reply_to='reply_to',
                        time_to_live=timedelta(seconds=60)
                    )
                    sender.send_messages(message)
    
                messages = receiver.peek_messages(5)
                assert len(messages) > 0
                assert all(isinstance(m, PeekMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    assert b''.join(message.body) == b'Test message'
                    assert message.properties[b'key'] == b'value'
                    assert message.label == 'label'
                    assert message.content_type == 'application/text'
                    assert message.correlation_id == 'cid'
                    assert message.message_id == 'mid'
                    assert message.partition_key == 'pk'
                    assert message.via_partition_key == 'via_pk'
                    assert message.to == 'to'
                    assert message.reply_to == 'reply_to'
                    assert message.time_to_live == timedelta(seconds=60)
                    with pytest.raises(AttributeError):
                        message.complete()

                    sender.send_messages(message)

                cnt = 0
                for message in receiver:
                    assert b''.join(message.body) == b'Test message'
                    assert message.properties[b'key'] == b'value'
                    assert message.label == 'label'
                    assert message.content_type == 'application/text'
                    assert message.correlation_id == 'cid'
                    assert message.message_id == 'mid'
                    assert message.partition_key == 'pk'
                    assert message.via_partition_key == 'via_pk'
                    assert message.to == 'to'
                    assert message.reply_to == 'reply_to'
                    assert message.time_to_live == timedelta(seconds=60)
                    message.complete()
                    cnt += 1
                assert cnt == 10
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_browse_empty_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 idle_timeout=5, 
                                                 mode=ReceiveSettleMode.PeekLock, 
                                                 prefetch=10) as receiver:
                messages = receiver.peek_messages(10)
                assert len(messages) == 0
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_fail_send_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            too_large = "A" * 256 * 1024
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                with pytest.raises(MessageContentTooLarge):
                    sender.send_messages(Message(too_large))

                half_too_large = "A" * int((1024 * 256) / 2)
                with pytest.raises(MessageContentTooLarge):
                    sender.send_messages([Message(half_too_large), Message(half_too_large)])

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_renew_message_locks(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            messages = []
            locks = 3
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              idle_timeout=5, 
                                              mode=ReceiveSettleMode.PeekLock, 
                                              prefetch=10) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(locks):
                        message = Message("Test message no. {}".format(i))
                        sender.send_messages(message)
    
                messages.extend(receiver.receive_messages())
                recv = True
                while recv:
                    recv = receiver.receive_messages()
                    messages.extend(recv)
    
                try:
                    for m in messages:
                        assert not m._lock_expired
                        time.sleep(5)
                        initial_expiry = m.locked_until_utc
                        m.renew_lock()
                        assert (m.locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    messages[0].complete()
                    messages[1].complete()
                    assert (messages[2].locked_until_utc - utc_now()) <= timedelta(seconds=60)
                    sleep_until_expired(messages[2])
                    with pytest.raises(MessageLockExpired):
                        messages[2].complete()
    
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_queue_client_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = Message("{}".format(i))
                    sender.send_messages(message)
    
            renewer = AutoLockRenew()
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 idle_timeout=5, 
                                                 mode=ReceiveSettleMode.PeekLock, 
                                                 prefetch=10) as receiver:
                for message in receiver:
                    if not messages:
                        messages.append(message)
                        assert not message._lock_expired
                        renewer.register(message, timeout=60)
                        print("Registered lock renew thread", message.locked_until_utc, utc_now())
                        time.sleep(60)
                        print("Finished first sleep", message.locked_until_utc)
                        assert not message._lock_expired
                        time.sleep(15) #generate autolockrenewtimeout error by going one iteration past.
                        sleep_until_expired(message)
                        print("Finished second sleep", message.locked_until_utc, utc_now())
                        assert message._lock_expired
                        try:
                            message.complete()
                            raise AssertionError("Didn't raise MessageLockExpired")
                        except MessageLockExpired as e:
                            assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                    else:
                        if message._lock_expired:
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            assert message._lock_expired
                            with pytest.raises(MessageLockExpired):
                                message.complete()
                        else:
                            assert message.delivery_count >= 1
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            messages.append(message)
                            message.complete()
            renewer.close()
            assert len(messages) == 11

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_message_time_to_live(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
               
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message_id = uuid.uuid4()
                message = Message(content)
                message.time_to_live = timedelta(seconds=30)
                sender.send_messages(message)
    
            time.sleep(30)
            with sb_client.get_queue_receiver(servicebus_queue.name, prefetch=5) as receiver:
                messages = receiver.receive_messages(5, max_wait_time=10)
            assert not messages

            with sb_client.get_queue_deadletter_receiver(
                    servicebus_queue.name,
                    idle_timeout=5,
                    mode=ReceiveSettleMode.PeekLock) as dl_receiver:
                count = 0
                for message in dl_receiver:
                    print_message(_logger, message)
                    message.complete()
                    count += 1
            assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_duplicate_detection=True, dead_lettering_on_message_expiration=True)
    def test_queue_message_duplicate_detection(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            message_id = uuid.uuid4()
            
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(5):
                    message = Message(str(i))
                    message.message_id = message_id
                    sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                 idle_timeout=5) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    assert message.message_id == message_id
                    message.complete()
                    count += 1
                assert count == 1
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_message_connection_closed(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
                
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = Message(content)
                sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
    
            with pytest.raises(MessageSettleFailed):
                messages[0].complete()
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_message_expiry(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
                       
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = Message(content)
                sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep((messages[0].locked_until_utc - utc_now()).total_seconds()+1)
                assert messages[0]._lock_expired
                with pytest.raises(MessageLockExpired):
                    messages[0].complete()
                with pytest.raises(MessageLockExpired):
                    messages[0].renew_lock()
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                assert messages[0].delivery_count > 0
                messages[0].complete()
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_message_lock_renew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                content = str(uuid.uuid4())
                message = Message(content)
                sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep(15)
                messages[0].renew_lock()
                time.sleep(15)
                messages[0].renew_lock()
                time.sleep(15)
                assert not messages[0]._lock_expired
                messages[0].complete()
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 0
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_message_receive_and_delete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
                
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = Message("Receive and delete test")
                sender.send_messages(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 mode=ReceiveSettleMode.ReceiveAndDelete) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                received = messages[0]
                print_message(_logger, received)
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
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                for m in messages:
                    print_message(_logger, m)
                assert len(messages) == 0
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_message_batch(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
                            
            def message_content():
                for i in range(5):
                    message = Message("Message no. {}".format(i))
                    message.properties = {'key': 'value'}
                    message.label = 'label'
                    message.content_type = 'application/text'
                    message.correlation_id = 'cid'
                    message.message_id = str(i)
                    message.partition_key = 'pk'
                    message.via_partition_key = 'via_pk'
                    message.to = 'to'
                    message.reply_to = 'reply_to'
                    message.time_to_live = timedelta(seconds=60)

                    yield message

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = BatchMessage()
                for each in message_content():
                    message.add(each)
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
                    assert message.properties
                    assert message.properties[b'key'] == b'value'
                    assert message.label == 'label'
                    assert message.content_type == 'application/text'
                    assert message.correlation_id == 'cid'
                    assert message.message_id == str(count)
                    assert message.partition_key == 'pk'
                    assert message.via_partition_key == 'via_pk'
                    assert message.to == 'to'
                    assert message.reply_to == 'reply_to'
                    assert message.sequence_number
                    assert message.enqueued_time_utc
                    assert message.expires_at_utc == (message.enqueued_time_utc + timedelta(seconds=60))
                    print_message(_logger, message)
                    message.complete()
                    count += 1
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_schedule_message(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    content = str(uuid.uuid4())
                    message_id = uuid.uuid4()
                    message = Message(content)
                    message.message_id = message_id
                    message.scheduled_enqueue_time_utc = enqueue_time
                    sender.send_messages(message)
    
                messages = receiver.receive_messages(max_wait_time=120)
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
                            m.complete()
                else:
                    raise Exception("Failed to receive schdeduled message.")
            

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_schedule_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, prefetch=20)

            with sender, receiver:
                content = str(uuid.uuid4())
                message_id_a = uuid.uuid4()
                message_a = Message(content)
                message_a.message_id = message_id_a
                message_id_b = uuid.uuid4()
                message_b = Message(content)
                message_b.message_id = message_id_b
                message_arry = [message_a, message_b]
                for message in message_arry:
                    message.properties = {'key': 'value'}
                    message.label = 'label'
                    message.content_type = 'application/text'
                    message.correlation_id = 'cid'
                    message.partition_key = 'pk'
                    message.via_partition_key = 'via_pk'
                    message.to = 'to'
                    message.reply_to = 'reply_to'

                sender.send_messages(message_arry)

                received_messages = receiver.receive_messages(max_batch_size=2, max_wait_time=5)
                for message in received_messages:
                    message.complete()

                tokens = sender.schedule_messages(received_messages, enqueue_time)
                assert len(tokens) == 2
    
                messages = receiver.receive_messages(max_wait_time=120)
                messages.extend(receiver.receive_messages(max_wait_time=5))
                if messages:
                    try:
                        data = str(messages[0])
                        assert data == content
                        assert messages[0].message_id in (message_id_a, message_id_b)
                        assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                        assert messages[0].delivery_count == 0
                        assert messages[0].properties
                        assert messages[0].properties[b'key'] == b'value'
                        assert messages[0].label == 'label'
                        assert messages[0].content_type == 'application/text'
                        assert messages[0].correlation_id == 'cid'
                        assert messages[0].partition_key == 'pk'
                        assert messages[0].via_partition_key == 'via_pk'
                        assert messages[0].to == 'to'
                        assert messages[0].reply_to == 'reply_to'
                        assert messages[0].sequence_number
                        assert messages[0].enqueued_time_utc
                        assert messages[0].message.delivery_tag is not None
                        assert len(messages) == 2
                    finally:
                        for m in messages:
                            m.complete()
                else:
                    raise Exception("Failed to receive schdeduled message.")
            

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_cancel_scheduled_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    message_a = Message("Test scheduled message")
                    message_b = Message("Test scheduled message")
                    tokens = sender.schedule_messages([message_a, message_b], enqueue_time)
                    assert len(tokens) == 2
    
                    sender.cancel_scheduled_messages(tokens)
    
                messages = receiver.receive_messages(max_wait_time=120)
                try:
                    assert len(messages) == 0
                except AssertionError:
                    for m in messages:
                        print(str(m))
                        m.complete()
                    raise


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_message_amqp_over_websocket(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                transport_type=TransportType.AmqpOverWebsocket,
                logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                assert sender._config.transport_type == TransportType.AmqpOverWebsocket
                message = Message("Test")
                sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, mode=ReceiveSettleMode.ReceiveAndDelete) as receiver:
                assert receiver._config.transport_type == TransportType.AmqpOverWebsocket
                messages = receiver.receive_messages(max_wait_time=5)
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
    def test_queue_message_settle_through_mgmt_link_due_to_broken_receiver_link(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = Message("Test")
                sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_wait_time=5)
                receiver._handler.message_handler.destroy()  # destroy the underlying receiver link
                assert len(messages) == 1
                messages[0].complete()


    def test_queue_mock_auto_lock_renew_callback(self):
        results = []
        errors = []
        def callback_mock(renewable, error):
            results.append(renewable)
            if error:
                errors.append(error)

        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1 # So we can run the test fast.
        with auto_lock_renew: # Check that it is called when the object expires for any reason (silent renew failure)
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            time.sleep(3)
            assert len(results) == 1 and results[-1]._lock_expired == True
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that in normal operation it does not get called
            auto_lock_renew.register(renewable=MockReceivedMessage(), on_lock_renew_failure=callback_mock)
            time.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that when a message is settled, it will not get called even after expiry
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            message._settled = True
            time.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that it is called when there is an overt renew failure
            message = MockReceivedMessage(exception_on_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            time.sleep(3)
            assert len(results) == 1 and results[-1]._lock_expired == True
            assert errors[-1]

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that it is not called when the renewer is shutdown
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            auto_lock_renew.close()
            time.sleep(3)
            assert not results
            assert not errors

        del results[:]
        del errors[:]
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1
        with auto_lock_renew: # Check that it is not called when the receiver is shutdown
            message = MockReceivedMessage(prevent_renew_lock=True)
            auto_lock_renew.register(renewable=message, on_lock_renew_failure=callback_mock)
            message._receiver._running = False
            time.sleep(3)
            assert not results
            assert not errors


    def test_queue_mock_no_reusing_auto_lock_renew(self):
        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1 # So we can run the test fast.
        with auto_lock_renew:
            auto_lock_renew.register(renewable=MockReceivedMessage())
            time.sleep(3)

        with pytest.raises(ServiceBusError):
            with auto_lock_renew:
                pass

        with pytest.raises(ServiceBusError):
            auto_lock_renew.register(renewable=MockReceivedMessage())

        auto_lock_renew = AutoLockRenew()
        auto_lock_renew._renew_period = 1

        with auto_lock_renew:
            auto_lock_renew.register(renewable=MockReceivedMessage())
            time.sleep(3)

        auto_lock_renew.close()

        with pytest.raises(ServiceBusError):
            with auto_lock_renew:
                pass

        with pytest.raises(ServiceBusError):
            auto_lock_renew.register(renewable=MockReceivedMessage())

    def test_queue_message_properties(self):
        scheduled_enqueue_time = (utc_now() + timedelta(seconds=20)).replace(microsecond=0)
        message = Message(
            body='data',
            properties={'key': 'value'},
            session_id='sid',
            label='label',
            content_type='application/text',
            correlation_id='cid',
            message_id='mid',
            partition_key='pk',
            via_partition_key='via_pk',
            to='to',
            reply_to='reply_to',
            reply_to_session_id='reply_to_sid',
            scheduled_enqueue_time_utc=scheduled_enqueue_time
        )

        assert message.properties
        assert message.properties['key'] == 'value'
        assert message.label == 'label'
        assert message.content_type == 'application/text'
        assert message.correlation_id == 'cid'
        assert message.message_id == 'mid'
        assert message.partition_key == 'pk'
        assert message.via_partition_key == 'via_pk'
        assert message.to == 'to'
        assert message.reply_to == 'reply_to'
        assert message.session_id == 'sid'
        assert message.reply_to_session_id == 'reply_to_sid'
        assert message.scheduled_enqueue_time_utc == scheduled_enqueue_time

        message.partition_key = 'updated'
        message.via_partition_key = 'updated'
        new_scheduled_time = (utc_now() + timedelta(hours=5)).replace(microsecond=0)
        message.scheduled_enqueue_time_utc = new_scheduled_time
        assert message.partition_key == 'updated'
        assert message.via_partition_key == 'updated'
        assert message.scheduled_enqueue_time_utc == new_scheduled_time

        message.partition_key = None
        message.via_partition_key = None
        message.scheduled_enqueue_time_utc = None

        assert message.partition_key is None
        assert message.via_partition_key is None
        assert message.scheduled_enqueue_time_utc is None

        try:
            timestamp = new_scheduled_time.timestamp() * 1000
        except AttributeError:
            timestamp = calendar.timegm(new_scheduled_time.timetuple()) * 1000

        uamqp_received_message = uamqp.message.Message(
            body=b'data',
            annotations={
                _X_OPT_PARTITION_KEY: b'r_key',
                _X_OPT_VIA_PARTITION_KEY: b'r_via_key',
                _X_OPT_SCHEDULED_ENQUEUE_TIME: timestamp,
            },
            properties=uamqp.message.MessageProperties()
        )
        received_message = ReceivedMessage(uamqp_received_message)
        assert received_message.partition_key == 'r_key'
        assert received_message.via_partition_key == 'r_via_key'
        assert received_message.scheduled_enqueue_time_utc == new_scheduled_time

        new_scheduled_time = utc_now() + timedelta(hours=1, minutes=49, seconds=32)

        received_message.partition_key = 'new_r_key'
        received_message.via_partition_key = 'new_r_via_key'
        received_message.scheduled_enqueue_time_utc = new_scheduled_time

        assert received_message.partition_key == 'new_r_key'
        assert received_message.via_partition_key == 'new_r_via_key'
        assert received_message.scheduled_enqueue_time_utc == new_scheduled_time

        received_message.partition_key = None
        received_message.via_partition_key = None
        received_message.scheduled_enqueue_time_utc = None

        assert message.partition_key is None
        assert message.via_partition_key is None
        assert message.scheduled_enqueue_time_utc is None

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_receive_batch_without_setting_prefetch(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            def message_content():
                for i in range(20):
                    yield Message(
                        body="Test message",
                        properties={'key': 'value'},
                        label='1st',
                        content_type='application/text',
                        correlation_id='cid',
                        message_id='mid',
                        partition_key='pk',
                        via_partition_key='via_pk',
                        to='to',
                        reply_to='reply_to',
                        time_to_live=timedelta(seconds=60)
                    )

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name)

            with sender, receiver:
                message = BatchMessage()
                for each in message_content():
                    message.add(each)
                sender.send_messages(message)

                receive_counter = 0
                message_1st_received_cnt = 0
                message_2nd_received_cnt = 0
                while message_1st_received_cnt < 20 or message_2nd_received_cnt < 20:
                    messages = receiver.receive_messages(max_batch_size=20, max_wait_time=5)
                    if not messages:
                        break
                    receive_counter += 1
                    for message in messages:
                        print_message(_logger, message)
                        assert b''.join(message.body) == b'Test message'
                        assert message.properties[b'key'] == b'value'
                        assert message.content_type == 'application/text'
                        assert message.correlation_id == 'cid'
                        assert message.message_id == 'mid'
                        assert message.partition_key == 'pk'
                        assert message.via_partition_key == 'via_pk'
                        assert message.to == 'to'
                        assert message.reply_to == 'reply_to'
                        assert message.time_to_live == timedelta(seconds=60)

                        if message.label == '1st':
                            message_1st_received_cnt += 1
                            message.complete()
                            message.label = '2nd'
                            sender.send_messages(message)  # resending received message
                        elif message.label == '2nd':
                            message_2nd_received_cnt += 1
                            message.complete()

                assert message_1st_received_cnt == 20 and message_2nd_received_cnt == 20
                # Network/server might be unstable making flow control ineffective in the leading rounds of connection iteration
                assert receive_counter < 10  # Dynamic link credit issuing come info effect
