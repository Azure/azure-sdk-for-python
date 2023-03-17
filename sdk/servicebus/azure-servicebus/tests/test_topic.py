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

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, CachedResourceGroupPreparer

from azure.servicebus import ServiceBusClient
from azure.servicebus._base_handler import ServiceBusSharedKeyCredential
from azure.servicebus._common.message import ServiceBusMessage
from servicebus_preparer import (
    ServiceBusNamespacePreparer,
    ServiceBusTopicPreparer,
    CachedServiceBusNamespacePreparer,
    CachedServiceBusTopicPreparer
)
from utilities import get_logger, print_message, uamqp_transport as get_uamqp_transport, ArgPasser
uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()


_logger = get_logger(logging.DEBUG)


class TestServiceBusTopics(AzureMgmtRecordedTestCase):
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusTopicPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_topic_by_servicebus_client_conn_str_send_basic(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_topic=None, **kwargs):

        with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string,
            logging_enable=False,
            uamqp_transport=uamqp_transport
        ) as sb_client:
            with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                sender.send_messages(message)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusTopicPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_topic_by_sas_token_credential_conn_str_send_basic(self, uamqp_transport, *, servicebus_namespace=None, servicebus_namespace_key_name=None, servicebus_namespace_primary_key=None, servicebus_topic=None, **kwargs):
        fully_qualified_namespace = servicebus_namespace.name + '.servicebus.windows.net'
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=ServiceBusSharedKeyCredential(
                policy=servicebus_namespace_key_name,
                key=servicebus_namespace_primary_key
            ),
            logging_enable=False,
            uamqp_transport=uamqp_transport
        ) as sb_client:
            with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                sender.send_messages(message)

    @pytest.mark.skip(reason="Pending management apis")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer()
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusTopicPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_topic_by_servicebus_client_list_topics(self, uamqp_transport, *, servicebus_namespace=None, servicebus_namespace_key_name=None, servicebus_namespace_primary_key=None, servicebus_topic=None, **kwargs):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            logging_enable=False,
            uamqp_transport=uamqp_transport
            )

        topics = client.list_topics()
        assert len(topics) >= 1
        # assert all(isinstance(t, TopicClient) for t in topics)
