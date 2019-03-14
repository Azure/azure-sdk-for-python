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

from azure.servicebus import ServiceBusClient, TopicClient
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

@pytest.mark.liveTest
def test_topic_by_topic_client_conn_str_send_basic(live_servicebus_config, standard_topic):

    topic_client = TopicClient.from_connection_string(live_servicebus_config['conn_str'], name=standard_topic, debug=True)
    with topic_client.get_sender() as sender:
        message = Message(b"Sample topic message")
        sender.send(message)
    message = Message(b"Another sample topic message")
    topic_client.send(message)

@pytest.mark.liveTest
def test_topic_by_servicebus_client_conn_str_send_basic(live_servicebus_config, standard_topic):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=True)

    topic_client = client.get_topic(standard_topic)
    with topic_client.get_sender() as sender:
        message = Message(b"Sample topic message")
        sender.send(message)
    message = Message(b"Another sample topic message")
    topic_client.send(message)

@pytest.mark.liveTest
def test_topic_by_servicebus_client_list_topics(live_servicebus_config, standard_topic):

    client = ServiceBusClient(
        service_namespace=live_servicebus_config['hostname'],
        shared_access_key_name=live_servicebus_config['key_name'],
        shared_access_key_value=live_servicebus_config['access_key'],
        debug=True)

    topics = client.list_topics()
    assert len(topics) >= 1
    assert all(isinstance(t, TopicClient) for t in topics)

@pytest.mark.liveTest
def test_topic_by_topic_client_conn_str_receive_fail(live_servicebus_config, standard_topic):
    topic_client = TopicClient.from_connection_string(live_servicebus_config['conn_str'], name=standard_topic, debug=True)
    with pytest.raises(AttributeError):
        topic_client.get_receiver()
