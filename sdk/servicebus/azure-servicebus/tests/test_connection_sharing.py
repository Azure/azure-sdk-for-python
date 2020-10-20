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
import random
import uuid
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from uamqp import c_uamqp, errors

from azure.servicebus import ServiceBusClient, AutoLockRenew, TransportType
from azure.servicebus._common.message import Message, PeekedMessage, ReceivedMessage, BatchMessage
from azure.servicebus._common.constants import ReceiveMode, _X_OPT_LOCK_TOKEN
from azure.servicebus._common.utils import utc_now
from azure.servicebus.exceptions import (
    ConnectionError,
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

_logger = get_logger(logging.DEBUG)

class ServiceBusQueueTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def ddd_test_send_and_receive_concurrent(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False
        ) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            receiver = sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=5)

            def send():
                for _ in range(5):
                    sender.send([Message("test message") for _ in range(10)])
                    time.sleep(0.5)

            def receive():
                msg_count = 0
                for msg in receiver:
                    msg_count += 1
                    msg.complete()
                return msg_count

            with sender, receiver:
                assert sender._connection._conn and receiver._connection._conn
                assert sender._connection._conn == receiver._connection._conn

                with ThreadPoolExecutor(max_workers=2) as executor:
                    executor.submit(send)
                    future = executor.submit(receive)
                    assert future.result() == 50

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_duplicate_detection=True, dead_lettering_on_message_expiration=True)
    # When sharing connection, duplication detection needs to be turned on in connection error case, see doc:
    # https://docs.microsoft.com/en-us/azure/service-bus-messaging/duplicate-detection
    # message_id needs to be set for duplication detection
    def ddd_test_send_and_receive_concurrent_error(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=True
        ) as sb_client:

            sender_1 = sb_client.get_queue_sender(servicebus_queue.name)
            sender_2 = sb_client.get_queue_sender(servicebus_queue.name)
            receiver_1 = sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=60)
            receiver_2 = sb_client.get_queue_receiver(servicebus_queue.name, idle_timeout=60)

            random_interruption = random.randint(4, 11)

            def send(sender):
                for i in range(50):
                    msg = Message("test message")
                    msg.properties.message_id = str(i)
                    sender.send(msg)

                    if i % random_interruption:
                        # manually destroy uamqp connection and set error state
                        sb_client._connection._conn._conn.destroy()
                        sb_client._connection._conn._error = errors.ConnectionClose(b"amqp:internal-error")
                        sb_client._connection._conn._state = c_uamqp.ConnectionState.ERROR

            def receive(receiver):
                msg_count = 0
                for msg in receiver:
                    msg.complete()
                    msg_count += 1
                return msg_count

            with sender_1, sender_2, receiver_1, receiver_2:
                assert sender_1._connection._conn and sender_2._connection._conn and receiver_1._connection._conn and receiver_2._connection._conn
                assert sender_1._connection._conn == receiver_1._connection._conn == sender_2._connection._conn == receiver_2._connection._conn

                with ThreadPoolExecutor(max_workers=4) as executor:
                    executor.submit(send, sender_1)
                    executor.submit(send, sender_2)
                    future_1 = executor.submit(receive, receiver_1)
                    future_2 = executor.submit(receive, receiver_2)

                    assert future_1.result() and future_2.result()
                    assert (future_1.result() + future_2.result()) == 100

