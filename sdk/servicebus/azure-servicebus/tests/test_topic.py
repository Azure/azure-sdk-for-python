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

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer, CachedResourceGroupPreparer

from azure.servicebus import ServiceBusClient
from azure.servicebus._base_handler import ServiceBusSharedKeyCredential
from azure.servicebus._common.message import ServiceBusMessage
from utilities import get_logger, print_message
from sb_env_loader import ServiceBusPreparer

_logger = get_logger(logging.DEBUG)


class ServiceBusTopicsTests(AzureMgmtTestCase):
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @ServiceBusPreparer()
    def test_topic_by_servicebus_client_conn_str_send_basic(self, servicebus_connection_str, servicebus_topic_name, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_connection_str,
            logging_enable=False
        ) as sb_client:
            with sb_client.get_topic_sender(servicebus_topic_name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                sender.send_messages(message)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @ServiceBusPreparer()
    def test_topic_by_sas_token_credential_conn_str_send_basic(self, servicebus_fully_qualified_namespace, servicebus_sas_policy, servicebus_sas_key, servicebus_topic_name, **kwargs):
        with ServiceBusClient(
            fully_qualified_namespace=servicebus_fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_sas_policy,
                key=servicebus_sas_key
            ),
            logging_enable=False
        ) as sb_client:
            with sb_client.get_topic_sender(servicebus_topic_name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                sender.send_messages(message)

    @pytest.mark.skip(reason="Pending management apis")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @ServiceBusPreparer()
    def test_topic_by_servicebus_client_list_topics(self, servicebus_fully_qualified_namespace, servicebus_sas_key, servicebus_sas_policy, servicebus_topic_name, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_fully_qualified_namespace,
            shared_access_key_name=servicebus_sas_policy,
            shared_access_key_value=servicebus_sas_key,
            debug=False)

        topics = client.list_topics()
        assert len(topics) >= 1
        # assert all(isinstance(t, TopicClient) for t in topics)
