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

from azure.servicebus import ServiceBusClient, AutoLockRenew
from azure.servicebus._common.message import Message, PeekMessage, ReceivedMessage, BatchMessage
from azure.servicebus._common.constants import ReceiveSettleMode, _X_OPT_LOCK_TOKEN
from azure.servicebus._common.utils import utc_now
from azure.servicebus.exceptions import (
    ServiceBusConnectionError,
    ServiceBusError,
    MessageLockExpired,
    InvalidHandlerState,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSendFailed,
    MessageSettleFailed)

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, ServiceBusQueuePreparer, CachedServiceBusQueuePreparer
from utilities import get_logger, print_message

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
                sender.send(Message("Message {}".format(i)))

        with sb_client.get_queue_receiver(servicebus_queue.name, 
                                          mode=ReceiveSettleMode.ReceiveAndDelete, 
                                          idle_timeout=10) as receiver:
            batch = receiver.receive()
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
                    sender.send(Message("Message {}".format(i)))

                    with sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=60) as receiver:
                        for message in receiver:
                            _logger.debug(message)
                            _logger.debug(message.sequence_number)
                            _logger.debug(message.enqueued_time_utc)
                            _logger.debug(message.expired)
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
                    message.enqueue_sequence_number = i
                    sender.send(message)

            receiver = sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5)
            count = 0
            for message in receiver:
                print_message(_logger, message)
                assert message.message.delivery_tag is not None
                assert message.lock_token == message.message.delivery_annotations.get(_X_OPT_LOCK_TOKEN)
                assert message.lock_token == uuid.UUID(bytes_le=message.message.delivery_tag)
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
                    message.enqueue_sequence_number = i
                    sender.send(message)
    
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              mode=ReceiveSettleMode.ReceiveAndDelete, 
                                              idle_timeout=5) as receiver:
                for message in receiver:
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
                    sender.send(message)
    
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
                        sender.send(message)
    
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
                        sender.send(message)
    
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    if not message.header.delivery_count:
                        count += 1
                        message.abandon() 
                    else:
                        assert message.header.delivery_count == 1
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
                        sender.send(message)
    
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
                        sender.send(message)
    
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
                    sender.send(message)
    
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
    

    @pytest.mark.skip(reason="Pending dead letter receiver")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deadletter(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                deferred_messages = []
                for i in range(10):
                    message = Message("Deferred message no. {}".format(i))
                    sender.send(message)
    
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
            with sb_client.get_deadletter_receiver(servicebus_queue.name,
                                                   idle_timeout=5) as receiver:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_iter_messages_with_retrieve_deferred_receiver_deletemode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    sender.send(Message("Deferred message no. {}".format(i)))

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
                        sender.send(message)
    
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
                        sender.send(message)
    
                count = 0
                messages = receiver.receive()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        count += 1
                        message.dead_letter(reason="Testing reason", description="Testing description")
                    messages = receiver.receive()
    
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
    

    @pytest.mark.skip(reason="Pending dead letter receiver")
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
                        sender.send(message)
    
                count = 0
                messages = receiver.receive()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        message.dead_letter(reason="Testing reason", description="Testing description")
                        count += 1
                    messages = receiver.receive()
    
                receiver.receive(1,5)
    
            assert count == 10
    
            with sb_client.get_deadletter_receiver(idle_timeout=5) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
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
                sb_client.get_queue_receiver(servicebus_queue.name, session_id="test")._open_with_retry()
    
            with sb_client.get_queue_sender(servicebus_queue.name, session_id="test") as sender:
                sender.send(Message("test session sender"))
    

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
                    sender.send(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                           idle_timeout=5, 
                                           mode=ReceiveSettleMode.PeekLock) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = Message("Test message no. {}".format(i))
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
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_browse_empty_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 idle_timeout=5, 
                                                 mode=ReceiveSettleMode.PeekLock, 
                                                 prefetch=10) as receiver:
                messages = receiver.peek(10)
                assert len(messages) == 0
    

    @pytest.mark.skip(reason="Pending queue message")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_fail_send_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            too_large = "A" * 1024 * 512
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                try:
                    results = sender.send(Message(too_large))
                except MessageSendFailed:
                    pytest.skip("Open issue for uAMQP on OSX")
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                with pytest.raises(MessageSendFailed):
                    sender.send(Message(too_large))
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.queue_message(Message(too_large))
                results = sender.send_pending_messages()
                assert len(results) == 1
                assert not results[0][0]
                assert isinstance(results[0][1], MessageSendFailed)
    

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_by_servicebus_client_fail_send_batch_messages(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_queue, **kwargs):
        
        pytest.skip("TODO: Pending bugfix in uAMQP")
        def batch_data(batch):
            for i in range(3):
                batch.add(Message(str(i) * 1024 * 256))
        return batch
    
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                with pytest.raises(MessageSendFailed):
                    batch = BatchMessage()
                    sender.send(batch_data(batch))
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.queue_message(BatchMessage(batch_data()))
                results = sender.send_pending_messages()
                assert len(results) == 4
                assert not results[0][0]
                assert isinstance(results[0][1], MessageSendFailed)
    

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
                        sender.send(message)
    
                messages.extend(receiver.receive())
                recv = True
                while recv:
                    recv = receiver.receive()
                    messages.extend(recv)
    
                try:
                    for m in messages:
                        assert not m.expired
                        time.sleep(5)
                        initial_expiry = m.locked_until_utc
                        m.renew_lock()
                        assert (m.locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    messages[0].complete()
                    messages[1].complete()
                    assert (messages[2].locked_until_utc - utc_now()) <= timedelta(seconds=60)
                    time.sleep((messages[2].locked_until_utc - utc_now()).total_seconds())
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
                    sender.send(message)
    
            renewer = AutoLockRenew()
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 idle_timeout=5, 
                                                 mode=ReceiveSettleMode.PeekLock, 
                                                 prefetch=10) as receiver:
                for message in receiver:
                    if not messages:
                        messages.append(message)
                        assert not message.expired
                        renewer.register(message, timeout=60)
                        print("Registered lock renew thread", message.locked_until_utc, utc_now())
                        time.sleep(50)
                        print("Finished first sleep", message.locked_until_utc)
                        assert not message.expired
                        time.sleep((message.locked_until_utc - utc_now()).total_seconds()+1)
                        print("Finished second sleep", message.locked_until_utc, utc_now())
                        assert message.expired
                        try:
                            message.complete()
                            raise AssertionError("Didn't raise MessageLockExpired")
                        except MessageLockExpired as e:
                            assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                    else:
                        if message.expired:
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            assert message.expired
                            with pytest.raises(MessageLockExpired):
                                message.complete()
                        else:
                            assert message.header.delivery_count >= 1
                            print("Remaining messages", message.locked_until_utc, utc_now())
                            messages.append(message)
                            message.complete()
            renewer.shutdown()
            assert len(messages) == 11
    

    @pytest.mark.skip(reason="Pending dead letter queue receiver")
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
                sender.send(message)
    
            time.sleep(30)
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive(5, timeout=10)
            assert not messages
    
            with sb_client.get_deadletter_receiver(servicebus_queue.name,
                                                      idle_timeout=5, 
                                                      mode=ReceiveSettleMode.PeekLock) as receiver:
                count = 0
                for message in receiver:
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
                    message.properties.message_id = message_id
                    sender.send(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                 idle_timeout=5) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    assert message.properties.message_id == message_id
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
                sender.send(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive(max_wait_time=10)
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
                sender.send(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive(max_wait_time=10)
                assert len(messages) == 1
                time.sleep((messages[0].locked_until_utc - utc_now()).total_seconds()+1)
                assert messages[0].expired
                with pytest.raises(MessageLockExpired):
                    messages[0].complete()
                with pytest.raises(MessageLockExpired):
                    messages[0].renew_lock()
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                assert messages[0].header.delivery_count > 0
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
                sender.send(message)

            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive(max_wait_time=10)
                assert len(messages) == 1
                time.sleep(15)
                messages[0].renew_lock()
                time.sleep(15)
                messages[0].renew_lock()
                time.sleep(15)
                assert not messages[0].expired
                messages[0].complete()
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive(max_wait_time=10)
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
                sender.send(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                                 mode=ReceiveSettleMode.ReceiveAndDelete) as receiver:
                messages = receiver.receive(max_wait_time=10)
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
                messages = receiver.receive(max_wait_time=10)
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
                    yield Message("Message no. {}".format(i))
    
    
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = BatchMessage()
                for each in message_content():
                    message.add(each)
                sender.send(message)
    
            with sb_client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages =receiver.receive(max_wait_time=10)
                recv = True
                while recv:
                    recv = receiver.receive(max_wait_time=10)
                    messages.extend(recv)
    
                assert len(messages) == 5
                for m in messages:
                    print_message(_logger, m)
                    m.complete()
    

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
                    message.properties.message_id = message_id
                    message.schedule(enqueue_time)
                    sender.send(message)
    
                messages = receiver.receive(max_wait_time=120)
                if messages:
                    try:
                        data = str(messages[0])
                        assert data == content
                        assert messages[0].properties.message_id == message_id
                        assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                        assert len(messages) == 1
                    finally:
                        for m in messages:
                            m.complete()
                else:
                    raise Exception("Failed to receive schdeduled message.")
            

    @pytest.mark.skip("Pending message scheduling functionality")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_queue_schedule_multiple_messages(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            enqueue_time = (utc_now() + timedelta(minutes=2)).replace(microsecond=0)
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              prefetch=20) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
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
                        assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                        assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                        assert len(messages) == 2
                    finally:
                        for m in messages:
                            m.complete()
                else:
                    raise Exception("Failed to receive schdeduled message.")
            

    @pytest.mark.skip(reason="Pending message scheduling functionality")
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
                    tokens = sender.schedule(enqueue_time, message_a, message_b)
                    assert len(tokens) == 2
    
                    sender.cancel_scheduled_messages(*tokens)
    
                messages = receiver.receive(max_wait_time=120)
                try:
                    assert len(messages) == 0
                except AssertionError:
                    for m in messages:
                        print(str(m))
                        m.complete()
                    raise
