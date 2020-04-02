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

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

from azure.servicebus import ServiceBusClient, TopicClient
from azure.servicebus.common.message import Message, PeekMessage
from azure.servicebus.common.constants import ReceiveSettleMode
from azure.servicebus.common.errors import ServiceBusError
from servicebus_preparer import ServiceBusNamespacePreparer, ServiceBusTopicPreparer

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


class ServiceBusTopicsTests(AzureMgmtTestCase):
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer()
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    def test_topic_by_topic_client_conn_str_send_basic(self, servicebus_namespace_connection_string, servicebus_topic, **kwargs):

        topic_client = TopicClient.from_connection_string(servicebus_namespace_connection_string, name=servicebus_topic.name, debug=False)
        with topic_client.get_sender() as sender:
            message = Message(b"Sample topic message")
            sender.send(message)
        message = Message(b"Another sample topic message")
        topic_client.send(message)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer()
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    def test_topic_by_servicebus_client_conn_str_send_basic(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_topic, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        topic_client = client.get_topic(servicebus_topic.name)
        with topic_client.get_sender() as sender:
            message = Message(b"Sample topic message")
            sender.send(message)
        message = Message(b"Another sample topic message")
        topic_client.send(message)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer()
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    def test_topic_by_servicebus_client_list_topics(self, servicebus_namespace, servicebus_namespace_key_name, servicebus_namespace_primary_key, servicebus_topic, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            debug=False)

        topics = client.list_topics()
        assert len(topics) >= 1
        assert all(isinstance(t, TopicClient) for t in topics)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer()
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    def test_topic_by_topic_client_conn_str_receive_fail(self, servicebus_namespace_connection_string, servicebus_topic, **kwargs):
        topic_client = TopicClient.from_connection_string(servicebus_namespace_connection_string, name=servicebus_topic.name, debug=False)
        with pytest.raises(AttributeError):
            topic_client.get_receiver()
