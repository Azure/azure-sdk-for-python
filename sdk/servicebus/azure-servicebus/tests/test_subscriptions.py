#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#-------------------------------------------------------------------------

import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

from azure.servicebus import ServiceBusClient, Message, PeekMessage, ReceiveSettleMode, ServiceBusSharedKeyCredential
from azure.servicebus.exceptions import ServiceBusError

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    CachedServiceBusTopicPreparer,
    CachedServiceBusSubscriptionPreparer,
    ServiceBusTopicPreparer,
    ServiceBusSubscriptionPreparer
)
from utilities import get_logger, print_message

_logger = get_logger(logging.DEBUG)


class ServiceBusSubscriptionTests(AzureMgmtTestCase):
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest')
    def test_subscription_by_subscription_client_conn_str_receive_basic(self, servicebus_namespace_connection_string, servicebus_topic, servicebus_subscription, **kwargs):

        with ServiceBusClient.from_connection_string(
                servicebus_namespace_connection_string,
                logging_enable=False
        ) as sb_client:
            with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = Message(b"Sample topic message")
                sender.send(message)

            with sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name,
                    subscription_name=servicebus_subscription.name,
                    idle_timeout=5
            ) as receiver:
                count = 0
                for message in receiver:
                    count += 1
                    message.complete()
            assert count == 1

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest')
    def test_subscription_by_sas_token_credential_conn_str_send_basic(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_topic, servicebus_subscription, **kwargs):
        fully_qualified_namespace = servicebus_namespace.name + '.servicebus.windows.net'
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_namespace_key_name,
                key=servicebus_namespace_primary_key
            ),
            logging_enable=False
        ) as sb_client:

            with sb_client.get_topic_sender(topic_name=servicebus_topic.name) as sender:
                message = Message(b"Sample topic message")
                sender.send(message)

            with sb_client.get_subscription_receiver(
                    topic_name=servicebus_topic.name,
                    subscription_name=servicebus_subscription.name,
                    idle_timeout=5
            ) as receiver:
                count = 0
                for message in receiver:
                    count += 1
                    message.complete()
            assert count == 1

    @pytest.mark.skip(reason="Pending management apis")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @ServiceBusSubscriptionPreparer(name_prefix='servicebustest')
    def test_subscription_by_servicebus_client_list_subscriptions(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_topic, servicebus_subscription, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        subs = client.list_subscriptions(servicebus_topic.name)
        assert len(subs) >= 1
        # assert all(isinstance(s, SubscriptionClient) for s in subs)
        assert subs[0].name == servicebus_subscription.name
        assert subs[0].topic_name == servicebus_topic.name
