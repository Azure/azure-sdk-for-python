# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import pytest
import time
import json
import sys

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, get_credential

from azure.servicebus import ServiceBusClient
from azure.servicebus._base_handler import ServiceBusSharedKeyCredential
from azure.servicebus._common.message import ServiceBusMessage
from servicebus_preparer import (
    ServiceBusNamespacePreparer,
    ServiceBusTopicPreparer,
    CachedServiceBusNamespacePreparer,
    CachedServiceBusTopicPreparer,
    CachedServiceBusResourceGroupPreparer,
    SERVICEBUS_ENDPOINT_SUFFIX,
)
from utilities import get_logger, uamqp_transport as get_uamqp_transport, ArgPasser

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()


_logger = get_logger(logging.DEBUG)


class TestServiceBusTopics(AzureMgmtRecordedTestCase):
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusTopicPreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_topic_by_servicebus_client_send_basic(
        self, uamqp_transport, *, servicebus_namespace=None, servicebus_topic=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                sender.send_messages(message)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusTopicPreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_topic_by_sas_token_credential_send_basic(
      self,
      uamqp_transport,
      *,
      servicebus_namespace=None,
      servicebus_namespace_key_name=None,
      servicebus_namespace_primary_key=None,
      servicebus_topic=None,
      **kwargs
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
            with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                sender.send_messages(message)

    @pytest.mark.skip(reason="Pending management apis")
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer()
    @ServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_topic_by_servicebus_client_list_topics(
        self,
        uamqp_transport,
        *,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_topic=None,
        **kwargs,
    ):

        client = ServiceBusClient(
            service_namespace=servicebus_namespace.name,
            shared_access_key_name=servicebus_namespace_key_name,
            shared_access_key_value=servicebus_namespace_primary_key,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        )

        topics = client.list_topics()
        assert len(topics) >= 1
        # assert all(isinstance(t, TopicClient) for t in topics)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusTopicPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_topic_by_servicebus_client_send_large_messages_w_sleep(self, uamqp_transport, *, servicebus_namespace=None, servicebus_topic=None, **kwargs):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        
        # message of 100 kb - requires multiple transfer frames
        size = 100
        large_dict = {
            "key": "A" * 1024
        }
        for i in range(size):
            large_dict[f"key_{i}"] = "A" * 1024
        body = json.dumps(large_dict)

        sb_client = ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=True,
            uamqp_transport=uamqp_transport
        )

        # This issue doesn't repro unless logging is added here w/ this socket timeout,
        # seemingly due to slowing down and some threading behavior.
        # Adding in the logging here to make sure this bug is being hit and tested.
        sender = sb_client.get_topic_sender(servicebus_topic.name, socket_timeout=60)
        for i in range(10):
            try:
                time.sleep(10)
                logging.info("sender created for %d", i)
                size_in_bytes = sys.getsizeof(body)

                # Convert bytes to kilobytes (KB)
                size_in_kb = size_in_bytes / 1024
                logging.info(f"size of body: {size_in_kb:.2f} KB")
                sender.send_messages(ServiceBusMessage(body))
                logging.info(f"Message sent %d successfully", i)
            except Exception as e:
                logging.error(f"Error sending message %d: %s", i, str(e))
                raise
