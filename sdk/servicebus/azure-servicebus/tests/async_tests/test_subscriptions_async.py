#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#-------------------------------------------------------------------------

import logging
import sys
import os
import asyncio
import pytest
import time
from datetime import datetime, timedelta

from azure.servicebus import ServiceBusMessage, ServiceBusReceiveMode
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.aio._base_handler_async import ServiceBusSharedKeyCredential
from azure.servicebus.exceptions import ServiceBusError, MessageLockLostError
from azure.servicebus._common.constants import ServiceBusSubQueue

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from tests.servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    CachedServiceBusTopicPreparer,
    CachedServiceBusSubscriptionPreparer,
    ServiceBusTopicPreparer,
    ServiceBusSubscriptionPreparer,
    CachedServiceBusResourceGroupPreparer,
    SERVICEBUS_ENDPOINT_SUFFIX
)
from tests.utilities import get_logger, print_message, uamqp_transport as get_uamqp_transport, ArgPasserAsync

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()

_logger = get_logger(logging.DEBUG)


class TestServiceBusSubscriptionAsync(AzureMgmtRecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_subscription_by_subscription_client_conn_str_receive_basic(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_topic=None, servicebus_subscription=None, **kwargs):

        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False,
                uamqp_transport=uamqp_transport
        ) as sb_client:
            async with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                await sender.send_messages(message)

            with pytest.raises(ValueError):
                sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name,
                    subscription_name=servicebus_subscription.name,
                    max_wait_time=0
                )

            async with sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name,
                    subscription_name=servicebus_subscription.name,
                    max_wait_time=10
            ) as receiver:

                with pytest.raises(ValueError):
                    await receiver.receive_messages(max_wait_time=-1)

                count = 0
                async for message in receiver:
                    count += 1
                    await receiver.complete_message(message)
            assert count == 1

    
    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_subscription_by_sas_token_credential_conn_str_send_basic(self, uamqp_transport, *, servicebus_namespace=None, servicebus_namespace_key_name=None, servicebus_namespace_primary_key=None, servicebus_topic=None, servicebus_subscription=None, **kwargs):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_namespace_key_name,
                key=servicebus_namespace_primary_key
            ),
            logging_enable=False,
            uamqp_transport=uamqp_transport
        ) as sb_client:

            async with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                await sender.send_messages(message)

            async with sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name,
                    subscription_name=servicebus_subscription.name,
                    max_wait_time=5
            ) as receiver:
                count = 0
                async for message in receiver:
                    count += 1
                    await receiver.complete_message(message)
            assert count == 1

    
    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_topic_by_servicebus_client_receive_batch_with_deadletter(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_topic=None, servicebus_subscription=None, **kwargs):
        async with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False,
                uamqp_transport=uamqp_transport
        ) as sb_client:

            async with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                max_wait_time=5,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                prefetch_count=10
            ) as receiver:

                async with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Dead lettered message no. {}".format(i))
                        await sender.send_messages(message)

                count = 0
                messages = await receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        count += 1
                        await receiver.dead_letter_message(message, reason="Testing reason", error_description="Testing description")
                    messages = await receiver.receive_messages()

                assert count == 10

            async with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                max_wait_time=5,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK
            ) as receiver:
                count = 0
                async for message in receiver:
                    print_message(_logger, message)
                    await receiver.complete_message(message)
                    count += 1
            assert count == 0

            async with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                sub_queue = ServiceBusSubQueue.DEAD_LETTER,
                max_wait_time=5,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK
            ) as dl_receiver:
                count = 0
                async for message in dl_receiver:
                    await dl_receiver.complete_message(message)
                    count += 1
                    assert message.dead_letter_reason == 'Testing reason'
                    assert message.dead_letter_error_description == 'Testing description'
                    assert message.application_properties[b'DeadLetterReason'] == b'Testing reason'
                    assert message.application_properties[b'DeadLetterErrorDescription'] == b'Testing description'
                assert count == 10

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest', lock_duration='PT5S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_subscription_message_expiry(self, uamqp_transport, *, servicebus_namespace=None, servicebus_namespace_key_name=None, servicebus_namespace_primary_key=None, servicebus_topic=None, servicebus_subscription=None, **kwargs):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_namespace_key_name,
                key=servicebus_namespace_primary_key
            ),
            logging_enable=False,
            uamqp_transport=uamqp_transport
        ) as sb_client:

            async with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Testing topic message expiry")
                await sender.send_messages(message)

            async with sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name,
                    subscription_name=servicebus_subscription.name
            ) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep(10)
                assert messages[0]._lock_expired
                with pytest.raises(MessageLockLostError):
                    await receiver.complete_message(messages[0])
                with pytest.raises(MessageLockLostError):
                    await receiver.renew_message_lock(messages[0])
            async with sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name,
                    subscription_name=servicebus_subscription.name
            ) as receiver:
                messages = await receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                assert messages[0].delivery_count > 0
                await receiver.complete_message(messages[0])
    
    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest', lock_duration='PT5S')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_subscription_receive_and_delete_with_send_and_wait(self, uamqp_transport, *, servicebus_namespace=None, servicebus_namespace_key_name=None, servicebus_namespace_primary_key=None, servicebus_topic=None, servicebus_subscription=None, **kwargs):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_namespace_key_name,
                key=servicebus_namespace_primary_key
            ),
            logging_enable=False,
            uamqp_transport=uamqp_transport
        ) as sb_client:

            sender = sb_client.get_topic_sender(topic_name=servicebus_topic.name)
            receiver = sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name,
                    subscription_name=servicebus_subscription.name,
                    receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
            )
            async with sender, receiver:
                # queue should be empty
                received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=10)
                assert len(received_msgs) == 0

                messages = [ServiceBusMessage("Message") for _ in range(10)]
                await sender.send_messages(messages)
                # wait for all messages to be sent to queue
                await asyncio.sleep(10)

                # receive messages + add to internal buffer should have messages now
                received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=10)
                assert len(received_msgs) == 10
