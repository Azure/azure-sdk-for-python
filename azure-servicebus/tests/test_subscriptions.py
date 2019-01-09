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

from azure.servicebus import ServiceBusClient, TopicClient, SubscriptionClient
from azure.servicebus.common.message import Message, PeekMessage
from azure.servicebus.common.constants import ReceiveSettleMode
from azure.servicebus.common.errors import ServiceBusError


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


def test_subscription_by_subscription_client_conn_str_receive_basic(live_servicebus_config, standard_subscription):
    topic_name, subscription_name = standard_subscription
    topic_client = TopicClient.from_connection_string(live_servicebus_config['conn_str'], name=topic_name, debug=True)
    with topic_client.get_sender() as sender:
        message = Message(b"Sample topic message")
        sender.send(message)

    sub_client = SubscriptionClient.from_connection_string(live_servicebus_config['conn_str'], subscription_name, topic=topic_name, debug=True)
    with sub_client.get_receiver(idle_timeout=5) as receiver:
        count = 0
        for message in receiver:
            count += 1
            message.complete()
    assert count == 1


def test_subscription_by_servicebus_client_conn_str_send_basic(live_servicebus_config, standard_subscription):
    topic_name, subscription_name = standard_subscription
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=True)

    topic_client = client.get_topic(topic_name)
    sub_client = client.get_subscription(topic_name, subscription_name)

    with topic_client.get_sender() as sender:
        message = Message(b"Sample topic message")
        sender.send(message)

    with sub_client.get_receiver(idle_timeout=5) as receiver:
        count = 0
        for message in receiver:
            count += 1
            message.complete()
    assert count == 1


def test_subscription_by_servicebus_client_list_subscriptions(live_servicebus_config, standard_subscription):
    topic_name, subscription_name = standard_subscription
    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=True)

    subs = client.list_subscriptions(topic_name)
    assert len(subs) >= 1
    assert all(isinstance(s, SubscriptionClient) for s in subs)
    assert subs[0].name == subscription_name
    assert subs[0].topic_name == topic_name


def test_subscription_by_subscription_client_conn_str_send_fail(live_servicebus_config, standard_subscription):
    topic_name, subscription_name = standard_subscription

    sub_client = SubscriptionClient.from_connection_string(live_servicebus_config['conn_str'], subscription_name, topic=topic_name, debug=True)
    with pytest.raises(AttributeError):
        sub_client.get_sender()
