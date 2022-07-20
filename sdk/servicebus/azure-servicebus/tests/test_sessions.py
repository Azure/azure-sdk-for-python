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
from datetime import timedelta

from azure.servicebus import (
    ServiceBusClient,
    AutoLockRenewer,
    ServiceBusMessage,
    ServiceBusReceivedMessage,
    ServiceBusReceiveMode,
    NEXT_AVAILABLE_SESSION,
    ServiceBusSubQueue
)
from azure.servicebus._common.utils import utc_now
from azure.servicebus.exceptions import (
    ServiceBusConnectionError,
    ServiceBusAuthenticationError,
    ServiceBusError,
    SessionLockLostError,
    MessageAlreadySettled,
    OperationTimeoutError,
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
from utilities import get_logger, print_message, sleep_until_expired

_logger = get_logger(logging.DEBUG)


class ServiceBusSessionTests(AzureMgmtTestCase):
    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_session_client_conn_str_receive_handler_peeklock(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5)

            with sender, receiver:
                for i in range(3):
                    message = ServiceBusMessage("Handler message no. {}".format(i))

                    message.partition_key = 'pkey'

                    message.session_id = session_id
                    message.partition_key = session_id
                    message.application_properties = {'key': 'value'}
                    message.subject = 'label'
                    message.content_type = 'application/text'
                    message.correlation_id = 'cid'
                    message.message_id = str(i)
                    message.to = 'to'
                    message.reply_to = 'reply_to'
                    message.reply_to_session_id = 'reply_to_session_id'

                    with pytest.raises(ValueError):
                        message.partition_key = 'pkey'

                    sender.send_messages(message)

                with pytest.raises(ServiceBusError):
                    receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)._open_with_retry()

                count = 0
                received_cnt_dic = {}
                for message in receiver:
                    print_message(_logger, message)
                    assert message.delivery_count == 0
                    assert message.application_properties
                    assert message.application_properties[b'key'] == b'value'
                    assert message.subject == 'label'
                    assert message.content_type == 'application/text'
                    assert message.correlation_id == 'cid'
                    assert message.partition_key == session_id
                    assert message.to == 'to'
                    assert message.reply_to == 'reply_to'
                    assert message.sequence_number
                    assert message.enqueued_time_utc
                    assert message.session_id == session_id
                    assert message.reply_to_session_id == 'reply_to_session_id'
                    count += 1
                    receiver.complete_message(message)
                    if message.message_id not in received_cnt_dic:
                        received_cnt_dic[message.message_id] = 1
                        sender.send_messages(message)
                    else:
                        received_cnt_dic[message.message_id] += 1

                assert received_cnt_dic['0'] == 2 and received_cnt_dic['1'] == 2 and received_cnt_dic['2'] == 2
                assert count == 6

            session_id = ""
            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5)

            with sender, receiver:
                for i in range(3):
                    message = ServiceBusMessage("Handler message no. {}".format(i))

                    message.partition_key = 'pkey'

                    message.session_id = session_id
                    message.partition_key = session_id
                    message.application_properties = {'key': 'value'}
                    message.subject = 'label'
                    message.content_type = 'application/text'
                    message.correlation_id = 'cid'
                    message.message_id = str(i)
                    message.to = 'to'
                    message.reply_to = 'reply_to'
                    message.reply_to_session_id = 'reply_to_session_id'

                    with pytest.raises(ValueError):
                        message.partition_key = 'pkey'

                    sender.send_messages(message)

                with pytest.raises(ServiceBusError):
                    receiver = sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5)._open_with_retry()

                count = 0
                received_cnt_dic = {}
                for message in receiver:
                    print_message(_logger, message)
                    assert message.delivery_count == 0
                    assert message.application_properties
                    assert message.application_properties[b'key'] == b'value'
                    assert message.subject == 'label'
                    assert message.content_type == 'application/text'
                    assert message.correlation_id == 'cid'
                    assert message.partition_key == session_id
                    assert message.to == 'to'
                    assert message.reply_to == 'reply_to'
                    assert message.sequence_number
                    assert message.enqueued_time_utc
                    assert message.session_id == session_id
                    assert message.reply_to_session_id == 'reply_to_session_id'
                    count += 1
                    receiver.complete_message(message)
                    if message.message_id not in received_cnt_dic:
                        received_cnt_dic[message.message_id] = 1
                        sender.send_messages(message)
                    else:
                        received_cnt_dic[message.message_id] += 1

                assert received_cnt_dic['0'] == 2 and received_cnt_dic['1'] == 2 and received_cnt_dic['2'] == 2
                assert count == 6

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True, lock_duration='PT5S')
    def test_session_by_queue_client_conn_str_receive_handler_receiveanddelete(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("Handler message no. {}".format(i), session_id=session_id)
                    sender.send_messages(message)

            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, 
                                              max_wait_time=5) as receiver:
                for message in receiver:
                    messages.append(message)
                    assert session_id == receiver._session_id
                    assert session_id == message.session_id
                    with pytest.raises(ValueError):
                        receiver.complete_message(message)

            assert not receiver._running
            assert len(messages) == 10
            time.sleep(5)

            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, max_wait_time=5) as session:
                for message in session:
                    messages.append(message)
                assert len(messages) == 0

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage("Stop message no. {}".format(i), session_id=session_id)
                    sender.send_messages(message)

            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as receiver:
                for message in receiver:
                    assert session_id == receiver.session.session_id
                    assert session_id == message.session_id
                    messages.append(message)
                    receiver.complete_message(message)
                    if len(messages) >= 5:
                        break

                assert receiver._running
                assert len(messages) == 5


                for message in receiver:
                    assert session_id == receiver.session.session_id
                    assert session_id == message.session_id
                    messages.append(message)
                    receiver.complete_message(message)
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
    def test_session_by_session_client_conn_str_receive_handler_with_no_session(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False, retry_total=1) as sb_client:
            with pytest.raises(OperationTimeoutError):
                with sb_client.get_queue_receiver(servicebus_queue.name, 
                                                  session_id=NEXT_AVAILABLE_SESSION, 
                                                  max_wait_time=10,) as session:
                    pass

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @pytest.mark.xfail(reason="'Cannot open log' error, potential service bug", raises=ServiceBusError)
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_connection_failure_is_idempotent(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        #Technically this validates for all senders/receivers, not just session, but since it uses session to generate a recoverable failure, putting it in here.
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
    
            # First let's just try the naive failure cases.
            receiver = sb_client.get_queue_receiver("THIS_IS_WRONG_ON_PURPOSE")
            with pytest.raises(ServiceBusAuthenticationError):
                receiver._open_with_retry()
            assert not receiver._running
            assert not receiver._handler
    
            sender = sb_client.get_queue_sender("THIS_IS_WRONG_ON_PURPOSE")
            with pytest.raises(ServiceBusAuthenticationError):
                sender._open_with_retry()
            assert not receiver._running
            assert not receiver._handler

            # Then let's try a case we can recover from to make sure everything works on reestablishment.
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION)
            with pytest.raises(OperationTimeoutError):
                receiver._open_with_retry()

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("test session sender", session_id=session_id))

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION, max_wait_time=5) as receiver:
                messages = []
                for message in receiver:
                    messages.append(message)
                assert len(messages) == 1

    @pytest.mark.skip(reason="TODO: iterator support")
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
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE, 
                                              max_wait_time=5) as session:
                for message in session:
                    messages.append(message)

                assert session._running
                assert len(messages) == 0

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage("Deferred message no. {}".format(i), session_id=session_id)
                    sender.send_messages(message)

            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              max_wait_time=5) as receiver:
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)

            assert count == 10

            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              max_wait_time=5) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    assert message.lock_token
                    assert not message.locked_until_utc
                    assert message._receiver
                    with pytest.raises(TypeError):
                        receiver.renew_message_lock(message)
                    receiver.complete_message(message)

    @pytest.mark.skip(reason="TODO: iterator support")
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
                messages = [ServiceBusMessage("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]
                sender.send_messages(messages)

            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              max_wait_time=5) as receiver:
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)

                assert count == 10

            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              max_wait_time=5) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    receiver.dead_letter_message(message, reason="Testing reason",
                                                 error_description="Testing description")

            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              sub_queue=ServiceBusSubQueue.DEAD_LETTER,
                                              max_wait_time=5) as receiver:
                for message in receiver:
                    count += 1
                    print_message(_logger, message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                    receiver.complete_message(message)
            assert count == 10

    @pytest.mark.skip(reason="TODO: iterator support")
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
                messages = [ServiceBusMessage("Deferred message no. {}".format(i), session_id=session_id) for i in range(10)]
                for message in messages:
                    sender.send_messages(message)

            count = 0
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as receiver:
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)

            assert count == 10
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id, 
                                              max_wait_time=5,
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE) as receiver:
                deferred = receiver.receive_deferred_messages(deferred_messages)
                assert len(deferred) == 10
                for message in deferred:
                    assert isinstance(message, ServiceBusReceivedMessage)
                    with pytest.raises(ValueError):
                        receiver.complete_message(message)
                with pytest.raises(ServiceBusError):
                    deferred = receiver.receive_deferred_messages(deferred_messages)

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage("Deferred message no. {}".format(i), session_id=session_id)
                    sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as receiver:
                count = 0
                for message in receiver:
                    deferred_messages.append(message.sequence_number)
                    print_message(_logger, message)
                    count += 1
                    receiver.defer_message(message)

                assert count == 10

                deferred = receiver.receive_deferred_messages(deferred_messages)

                with pytest.raises(MessageAlreadySettled):
                    receiver.complete_message(message)

    @pytest.mark.skip(reason="TODO: iterator support")
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
                                              max_wait_time=5, 
                                              prefetch_count=10) as receiver:

                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Dead lettered message no. {}".format(i), session_id=session_id)
                        sender.send_messages(message)

                count = 0
                messages = receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        receiver.dead_letter_message(message, reason="Testing reason", error_description="Testing description")
                        count += 1
                    messages = receiver.receive_messages()
            assert count == 10

            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                                              max_wait_time=5) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    receiver.complete_message(message)
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
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
                    message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id)
                    sender.send_messages(message)
            session_id_2 = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(3):
                    message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id_2)
                    sender.send_messages(message)

            with pytest.raises(ServiceBusError):
                with sb_client.get_queue_receiver(servicebus_queue.name):
                    messages = sb_client.peek_messages(5)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = receiver.peek_messages(5)
                assert len(messages) == 5
                assert all(isinstance(m, ServiceBusReceivedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(ValueError):
                        receiver.complete_message(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id_2) as receiver:
                messages = receiver.peek_messages(5)
                assert len(messages) == 3


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_by_servicebus_client_browse_messages_with_receiver(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            session_id = str(uuid.uuid4())
            with sb_client.get_queue_receiver(servicebus_queue.name, max_wait_time=5, session_id=session_id) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(5):
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id)
                        sender.send_messages(message)

                messages = receiver.peek_messages(5)
                assert len(messages) > 0
                assert all(isinstance(m, ServiceBusReceivedMessage) for m in messages)
                for message in messages:
                    print_message(_logger, message)
                    with pytest.raises(ValueError):
                        receiver.complete_message(message)

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
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, prefetch_count=10) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    for i in range(locks):
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id)
                        sender.send_messages(message)

                messages.extend(receiver.receive_messages())
                recv = True
                while recv:
                    recv = receiver.receive_messages(max_wait_time=5)
                    messages.extend(recv)

                try:
                    for m in messages:
                        with pytest.raises(TypeError):
                            expired = m._lock_expired
                        assert m.locked_until_utc is None
                        assert m.lock_token is not None
                    time.sleep(5)
                    initial_expiry = receiver.session._locked_until_utc
                    receiver.session.renew_lock(timeout=5)
                    assert (receiver.session._locked_until_utc - initial_expiry) >= timedelta(seconds=5)
                finally:
                    receiver.complete_message(messages[0])
                    receiver.complete_message(messages[1])

                    # This magic number is because of a 30 second lock renewal window.  Chose 31 seconds because at 30, you'll see "off by .05 seconds" flaky failures
                    # potentially as a side effect of network delays/sleeps/"typical distributed systems nonsense."  In a perfect world we wouldn't have a magic number/network hop but this allows
                    # a slightly more robust test in absence of that.
                    assert (receiver.session._locked_until_utc - utc_now()) <= timedelta(seconds=60)
                    sleep_until_expired(receiver.session)
                    with pytest.raises(SessionLockLostError):
                        receiver.complete_message(messages[2])

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True, lock_duration='PT10S')
    def test_session_by_conn_str_receive_handler_with_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        session_id = str(uuid.uuid4())
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i), session_id=session_id)
                    sender.send_messages(message)

            results = []
            def lock_lost_callback(renewable, error):
                results.append(renewable)

            renewer = AutoLockRenewer()
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=10) as receiver:
                renewer.register(receiver,
                                 receiver.session,
                                 max_lock_renewal_duration=10,
                                 on_lock_renew_failure=lock_lost_callback)
                print("Registered lock renew thread", receiver.session._locked_until_utc, utc_now())
                with pytest.raises(SessionLockLostError):
                    for message in receiver:
                        if not messages:
                            print("Starting first sleep")
                            time.sleep(10)
                            print("First sleep {}".format(receiver.session._locked_until_utc - utc_now()))
                            assert not receiver.session._lock_expired
                            with pytest.raises(TypeError):
                                message._lock_expired
                            assert message.locked_until_utc is None
                            with pytest.raises(TypeError):
                                receiver.renew_message_lock(message)
                            assert message.lock_token is not None
                            receiver.complete_message(message)
                            messages.append(message)

                        elif len(messages) == 1:
                            print("Starting second sleep")
                            time.sleep(10) # ensure renewer expires
                            print("Second sleep {}".format(receiver.session._locked_until_utc - utc_now()))
                            assert not results
                            sleep_until_expired(receiver.session) # and then ensure it didn't slip a renew under the wire.
                            assert receiver.session._lock_expired
                            assert isinstance(receiver.session.auto_renew_error, AutoLockRenewTimeout)
                            try:
                                receiver.complete_message(message)
                                raise AssertionError("Didn't raise SessionLockLostError")
                            except SessionLockLostError as e:
                                assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                            messages.append(message)

            # While we're testing autolockrenew and sessions, let's make sure we don't call the lock-lost callback when a session exits.
            renewer._renew_period = 1
            session = None

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=10, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, prefetch_count=10) as receiver:
                session = receiver.session
                renewer.register(receiver,
                                 session,
                                 max_lock_renewal_duration=10,
                                 on_lock_renew_failure=lock_lost_callback)
            sleep_until_expired(receiver.session)
            assert not results

            renewer.close()
            assert len(messages) == 2

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True, lock_duration='PT10S')
    def test_session_by_conn_str_receive_handler_with_auto_autolockrenew(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        session_id = str(uuid.uuid4())
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=True) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for i in range(10):
                    message = ServiceBusMessage("{}".format(i), session_id=session_id)
                    sender.send_messages(message)

            results = []
            def lock_lost_callback(renewable, error):
                results.append(renewable)

            renewer = AutoLockRenewer(max_lock_renewal_duration=10, on_lock_renew_failure = lock_lost_callback)
            messages = []
            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              session_id=session_id,
                                              max_wait_time=10,
                                              receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                              prefetch_count=10,
                                              auto_lock_renewer=renewer) as receiver:
                print("Registered lock renew thread", receiver.session._locked_until_utc, utc_now())
                with pytest.raises(SessionLockLostError):
                    for message in receiver:
                        if not messages:
                            print("Starting first sleep")
                            time.sleep(10)
                            print("First sleep {}".format(receiver.session._locked_until_utc - utc_now()))
                            assert not receiver.session._lock_expired
                            with pytest.raises(TypeError):
                                message._lock_expired
                            assert message.locked_until_utc is None
                            with pytest.raises(TypeError):
                                receiver.renew_message_lock(message)
                            assert message.lock_token is not None
                            receiver.complete_message(message)
                            messages.append(message)

                        elif len(messages) == 1:
                            print("Starting second sleep")
                            time.sleep(10) # ensure renewer expires
                            print("Second sleep {}".format(receiver.session._locked_until_utc - utc_now()))
                            assert not results
                            sleep_until_expired(receiver.session) # and then ensure it didn't slip a renew under the wire.
                            assert receiver.session._lock_expired
                            assert isinstance(receiver.session.auto_renew_error, AutoLockRenewTimeout)
                            try:
                                receiver.complete_message(message)
                                raise AssertionError("Didn't raise SessionLockLostError")
                            except SessionLockLostError as e:
                                assert isinstance(e.inner_exception, AutoLockRenewTimeout)
                            messages.append(message)

            # While we're testing autolockrenew and sessions, let's make sure we don't call the lock-lost callback when a session exits.
            renewer._renew_period = 1
            session = None

            with sb_client.get_queue_receiver(servicebus_queue.name,
                                              session_id=session_id,
                                              max_wait_time=10,
                                              receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                              prefetch_count=10,
                                              auto_lock_renewer=renewer) as receiver:
                session = receiver.session
            sleep_until_expired(receiver.session)
            assert not results

            renewer.close()
            assert len(messages) == 2

        # test voluntary halt of auto lock renewer when session is closed
        session_id = str(uuid.uuid4())
        with sb_client.get_queue_sender(servicebus_queue.name) as sender:
            messages = [ServiceBusMessage("{}".format(i), session_id=session_id) for i in range(10)]
            sender.send_messages(messages)

        renewer = AutoLockRenewer(max_lock_renewal_duration=100)
        receiver = sb_client.get_queue_receiver(servicebus_queue.name,
                                            session_id=session_id,
                                            max_wait_time=10,
                                            prefetch_count=10,
                                            auto_lock_renewer=renewer)

        with receiver:
            received_msgs = receiver.receive_messages(max_wait_time=5)
            for msg in received_msgs:
                receiver.complete_message(msg)

        receiver.close()
        assert not renewer._renewable(receiver._session)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_receiver_partially_invalid_autolockrenew_mode(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        session_id = str(uuid.uuid4())
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("test_message", session_id=session_id))

            failures = 0
            def should_not_run(*args, **kwargs):
                failures += 1

            auto_lock_renewer = AutoLockRenewer(on_lock_renew_failure=should_not_run)
            with sb_client.get_queue_receiver(servicebus_queue.name, 
                                              session_id=session_id,
                                              receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                              auto_lock_renewer=auto_lock_renewer) as receiver:
            
                assert receiver.receive_messages()
                assert not failures

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
                message = ServiceBusMessage("test")
                message.session_id = session_id
                sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1

            with pytest.raises(ValueError):
                receiver.complete_message(messages[0])

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True, lock_duration='PT5S')
    def test_session_message_expiry(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:
            session_id = str(uuid.uuid4())

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("Testing expired messages")
                message.session_id = session_id
                sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                time.sleep(10)
                with pytest.raises(TypeError):
                    messages[0]._lock_expired
                with pytest.raises(TypeError):
                    receiver.renew_message_lock(messages[0])
                    #TODO: Bug: Why was this 30s sleep before?  compare with T1.
                assert receiver.session._lock_expired
                with pytest.raises(SessionLockLostError):
                    receiver.complete_message(messages[0])
                with pytest.raises(SessionLockLostError):
                    receiver.session.renew_lock()

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = receiver.receive_messages(max_wait_time=30)
                assert len(messages) == 1
                print_message(_logger, messages[0])
                assert messages[0].delivery_count
                receiver.complete_message(messages[0])

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
                    message = ServiceBusMessage(content, session_id=session_id)
                    message.message_id = message_id
                    message.scheduled_enqueue_time_utc = enqueue_time
                    sender.send_messages(message)

                messages = []
                count = 0
                while not messages and count < 12:
                    messages = receiver.receive_messages(max_wait_time=10)
                    receiver.session.renew_lock(timeout=None)
                    count += 1

                data = str(messages[0])
                assert data == content
                assert messages[0].message_id == message_id
                assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                assert len(messages) == 1


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

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, prefetch_count=20) as receiver:
                with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                    content = str(uuid.uuid4())
                    message_id_a = uuid.uuid4()
                    message_a = ServiceBusMessage(content, session_id=session_id)
                    message_a.message_id = message_id_a
                    message_id_b = uuid.uuid4()
                    message_b = ServiceBusMessage(content, session_id=session_id)
                    message_b.message_id = message_id_b
                    tokens = sender.schedule_messages([message_a, message_b], enqueue_time)
                    assert len(tokens) == 2

                messages = []
                count = 0
                while len(messages) < 2 and count < 12:
                    receiver.session.renew_lock(timeout=None)
                    messages.extend(receiver.receive_messages(max_wait_time=15))
                    time.sleep(5)
                    count += 1

                data = str(messages[0])
                assert data == content
                assert messages[0].message_id in (message_id_a, message_id_b)
                assert messages[0].scheduled_enqueue_time_utc == enqueue_time
                assert messages[0].scheduled_enqueue_time_utc == messages[0].enqueued_time_utc.replace(microsecond=0)
                assert len(messages) == 2


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
                message_a = ServiceBusMessage("Test scheduled message", session_id=session_id)
                message_b = ServiceBusMessage("Test scheduled message", session_id=session_id)
                tokens = sender.schedule_messages([message_a, message_b], enqueue_time)
                assert len(tokens) == 2
                sender.cancel_scheduled_messages(tokens)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                messages = []
                count = 0
                while not messages and count < 13:
                    messages = receiver.receive_messages(max_wait_time=20)
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
                    message = ServiceBusMessage("Handler message no. {}".format(i), session_id=session_id)
                    sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, max_wait_time=5) as session:
                assert session.session.get_state(timeout=5) == None
                session.session.set_state("first_state", timeout=5)
                count = 0
                for m in session:
                    assert m.session_id == session_id
                    count += 1
                state = session.session.get_state()
                assert state == b'first_state'
            assert count == 3


    @pytest.mark.skip(reason="Needs list sessions")
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
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id)
                        sender.send_messages(message)
            for session_id in sessions:
                with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id) as receiver:
                    receiver.set_state("SESSION {}".format(session_id))

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION, max_wait_time=5, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as receiver:
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
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session)
                        sender.send_messages(message)
            for session in sessions:
                with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session) as receiver:
                    receiver.set_state("SESSION {}".format(session))

                    current_sessions = receiver.list_sessions(updated_since=start_time)
                    assert len(current_sessions) == 5
                    assert current_sessions == sessions


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @pytest.mark.xfail(reason="'Cannot open log' error, potential service bug")
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
                    with sb_client.get_queue_receiver(servicebus_queue.name, session_id=NEXT_AVAILABLE_SESSION, max_wait_time=10) as receiver:
                        for message in receiver:
                            print("ServiceBusReceivedMessage: {}".format(message))
                            messages.append(message)
                            receiver.complete_message(message)
                except OperationTimeoutError:
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
                        message = ServiceBusMessage("Test message no. {}".format(i), session_id=session_id)
                        sender.send_messages(message)
    
            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_receivers) as thread_pool:
                for _ in range(concurrent_receivers):
                    futures.append(thread_pool.submit(message_processing, sb_client))
                concurrent.futures.wait(futures)
    
            assert not errors
            assert len(messages) == 100

    @pytest.mark.skip(reason="TODO: iterator support")
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
                    message = ServiceBusMessage("Handler message no. {}".format(i), session_id=session_id)
                    sender.send_messages(message)

            with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id, prefetch_count=0, max_wait_time=5) as receiver:
                message = receiver.next()
                assert message.sequence_number == 1
                receiver.abandon_message(message)
                for next_message in receiver: # we can't be sure there won't be a service delay, so we may not get the message back _immediately_, even if in most cases it shows right back up.
                    if not next_message:
                        raise Exception("Did not successfully re-receive abandoned message, sequence_number 1 was not observed.")
                    if next_message.sequence_number == 1:
                        return

    @pytest.mark.skip(reason="TODO: iterator support")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_basic_topic_subscription_send_and_receive(self, servicebus_namespace_connection_string, servicebus_topic, servicebus_subscription, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False
        ) as sb_client:
            with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message", session_id='test_session')
                sender.send_messages(message)

            with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                session_id='test_session',
                max_wait_time=5
            ) as receiver:
                count = 0
                for message in receiver:
                    count += 1
                    receiver.complete_message(message)
            assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_session_non_session_send_to_session_queue_should_fail(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=False) as sb_client:

            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                message = ServiceBusMessage("This should be an invalid non session message")
                with pytest.raises(ServiceBusError):
                    sender.send_messages(message)
