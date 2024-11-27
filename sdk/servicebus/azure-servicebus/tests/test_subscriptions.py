# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

from azure.servicebus._common.utils import utc_now
from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusReceiveMode
from azure.servicebus._base_handler import ServiceBusSharedKeyCredential
from azure.servicebus.exceptions import ServiceBusError, MessageLockLostError
from azure.servicebus._common.constants import ServiceBusSubQueue

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, get_credential
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    CachedServiceBusTopicPreparer,
    CachedServiceBusSubscriptionPreparer,
    ServiceBusTopicPreparer,
    ServiceBusSubscriptionPreparer,
    CachedServiceBusResourceGroupPreparer,
    SERVICEBUS_ENDPOINT_SUFFIX,
)
from utilities import get_logger, print_message, uamqp_transport as get_uamqp_transport, ArgPasser

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()


_logger = get_logger(logging.DEBUG)


class TestServiceBusSubscription(AzureMgmtRecordedTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_subscription_by_subscription_client_conn_str_receive_basic(
        self,
        uamqp_transport,
        *,
        servicebus_namespace=None,
        servicebus_topic=None,
        servicebus_subscription=None,
        **kwargs,
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                sender.send_messages(message)

            with pytest.raises(ValueError):
                sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name, subscription_name=servicebus_subscription.name, max_wait_time=0
                )

            with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name, subscription_name=servicebus_subscription.name, max_wait_time=5
            ) as receiver:

                with pytest.raises(ValueError):
                    receiver.receive_messages(max_wait_time=-1)

                count = 0
                for message in receiver:
                    count += 1
                    receiver.complete_message(message)
            assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_subscription_by_sas_token_credential_conn_str_send_basic(
        self,
        uamqp_transport,
        *,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_topic=None,
        servicebus_subscription=None,
        **kwargs,
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_namespace_key_name, key=servicebus_namespace_primary_key
            ),
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:

            with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                sender.send_messages(message)

            with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name, subscription_name=servicebus_subscription.name, max_wait_time=5
            ) as receiver:
                count = 0
                for message in receiver:
                    count += 1
                    receiver.complete_message(message)
            assert count == 1

    @pytest.mark.skip(reason="Pending management apis")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_subscription_by_servicebus_client_list_subscriptions(
        self,
        uamqp_transport,
        *,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_topic=None,
        servicebus_subscription=None,
        **kwargs,
    ):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        )

        subs = client.list_subscriptions(servicebus_topic.name)
        assert len(subs) >= 1
        # assert all(isinstance(s, SubscriptionClient) for s in subs)
        assert subs[0].name == servicebus_subscription.name
        assert subs[0].topic_name == servicebus_topic.name

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_subscription_by_servicebus_client_receive_batch_with_deadletter(
        self,
        uamqp_transport,
        *,
        servicebus_namespace=None,
        servicebus_topic=None,
        servicebus_subscription=None,
        **kwargs,
    ):

        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:

            with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                max_wait_time=5,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                prefetch_count=10,
            ) as receiver:

                with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                    for i in range(10):
                        message = ServiceBusMessage("Dead lettered message no. {}".format(i))
                        sender.send_messages(message)

                count = 0
                messages = receiver.receive_messages()
                while messages:
                    for message in messages:
                        print_message(_logger, message)
                        count += 1
                        receiver.dead_letter_message(
                            message, reason="Testing reason", error_description="Testing description"
                        )
                    messages = receiver.receive_messages()

            assert count == 10

            with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                max_wait_time=5,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
            ) as receiver:
                count = 0
                for message in receiver:
                    print_message(_logger, message)
                    receiver.complete_message(message)
                    count += 1
            assert count == 0

            with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                sub_queue=ServiceBusSubQueue.DEAD_LETTER,
                max_wait_time=5,
                receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
            ) as dl_receiver:
                count = 0
                for message in dl_receiver:
                    dl_receiver.complete_message(message)
                    count += 1
                    assert message.dead_letter_reason == "Testing reason"
                    assert message.dead_letter_error_description == "Testing description"
                    assert message.application_properties[b"DeadLetterReason"] == b"Testing reason"
                    assert message.application_properties[b"DeadLetterErrorDescription"] == b"Testing description"
                assert count == 10

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest", lock_duration="PT5S")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_subscription_message_expiry(
        self,
        uamqp_transport,
        *,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_topic=None,
        servicebus_subscription=None,
        **kwargs,
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_namespace_key_name, key=servicebus_namespace_primary_key
            ),
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:

            with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Testing topic message expiry")
                sender.send_messages(message)

            with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name, subscription_name=servicebus_subscription.name
            ) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                time.sleep((messages[0].locked_until_utc - utc_now()).total_seconds() + 1)
                assert messages[0]._lock_expired
                with pytest.raises(MessageLockLostError):
                    receiver.complete_message(messages[0])
                with pytest.raises(MessageLockLostError):
                    receiver.renew_message_lock(messages[0])
            with sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name, subscription_name=servicebus_subscription.name
            ) as receiver:
                messages = receiver.receive_messages(max_wait_time=10)
                assert len(messages) == 1
                assert messages[0].delivery_count > 0
                receiver.complete_message(messages[0])

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest", lock_duration="PT5S")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_subscription_receive_and_delete_with_send_and_wait(
        self,
        uamqp_transport,
        *,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_topic=None,
        servicebus_subscription=None,
        **kwargs,
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_namespace_key_name, key=servicebus_namespace_primary_key
            ),
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:

            sender = sb_client.get_topic_sender(topic_name=servicebus_topic.name)
            receiver = sb_client.get_subscription_receiver(
                topic_name=servicebus_topic.name,
                subscription_name=servicebus_subscription.name,
                receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
            )
            with sender, receiver:
                # queue should be empty
                received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=10)
                assert len(received_msgs) == 0

                messages = [ServiceBusMessage("Message") for _ in range(10)]
                sender.send_messages(messages)
                # wait for all messages to be sent to queue
                time.sleep(10)

                # receive messages + add to internal buffer should have messages now
                received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=10)
                assert len(received_msgs) == 10
