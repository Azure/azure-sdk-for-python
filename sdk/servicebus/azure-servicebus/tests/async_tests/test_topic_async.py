#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer

from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.aio._base_handler_async import ServiceBusSharedKeyCredential
from azure.servicebus._common.message import ServiceBusMessage
from servicebus_preparer import (
    ServiceBusNamespacePreparer,
    ServiceBusTopicPreparer,
    CachedServiceBusNamespacePreparer,
    CachedServiceBusTopicPreparer,
    CachedServiceBusResourceGroupPreparer,
    SERVICEBUS_ENDPOINT_SUFFIX
)
from utilities import get_logger, print_message, uamqp_transport as get_uamqp_transport, ArgPasserAsync

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()

_logger = get_logger(logging.DEBUG)


class TestServiceBusTopicsAsync(AzureMgmtRecordedTestCase):
    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusTopicPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_topic_by_servicebus_client_conn_str_send_basic(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_topic=None, **kwargs):

        async with ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string,
            logging_enable=False,
            uamqp_transport=uamqp_transport
        ) as sb_client:
            async with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                await sender.send_messages(message)

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusTopicPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_topic_by_sas_token_credential_conn_str_send_basic(self, uamqp_transport, *, servicebus_namespace=None, servicebus_namespace_key_name=None, servicebus_namespace_primary_key=None, servicebus_topic=None, **kwargs):
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
            async with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                message = ServiceBusMessage(b"Sample topic message")
                await sender.send_messages(message)
