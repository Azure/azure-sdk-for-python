# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import json
import logging
import pytest
from datetime import datetime, timedelta

from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import (
    ServiceBusMessage,
    ServiceBusMessageBatch,
)
from azure.servicebus._common.utils import utc_now
from devtools_testutils import AzureMgmtRecordedTestCase, AzureRecordedTestCase, get_credential
from tests.servicebus_preparer import (
    SERVICEBUS_ENDPOINT_SUFFIX,
    CachedServiceBusNamespacePreparer,
    CachedServiceBusQueuePreparer,
    ServiceBusQueuePreparer,
    CachedServiceBusResourceGroupPreparer,
)
from tests.utilities import (
    get_logger,
    print_message,
    sleep_until_expired,
    uamqp_transport as get_uamqp_transport,
    ArgPasserAsync,
)

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()

_logger = get_logger(logging.DEBUG)


class TestServiceBusMgmtOperationClientAsync(AzureMgmtRecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(
        name_prefix="servicebustest", dead_lettering_on_message_expiration=True, lock_duration="PT10S"
    )
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_async_get_sessions(
        self,
        uamqp_transport,
        *,
        servicebus_namespace_connection_string=None,
        servicebus_namespace=None,
        servicebus_queue=None,
        **kwargs,
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        async with ServiceBusClient(
            fully_qualified_namespace, credential, logging_enable=False, uamqp_transport=uamqp_transport
        ) as sb_client:

            sender = sb_client.get_queue_sender(servicebus_queue.name)
            async with sender:
                for i in range(5):
                    message = ServiceBusMessage("Handler message no. {}".format(i), session_id=str(i))
                    await sender.send_messages(message, timeout=5)

            async with sb_client.get_management_operation_client(servicebus_queue.name) as operator:
                batch = await operator.get_sessions()

                assert len(batch) == 5
                
                for session in batch:
                    assert session in ["0", "1", "2", "3", "4"]

                    async with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session) as receiver:
                        messages = await receiver.receive_messages(max_wait_time=5)
                        assert len(messages) == 1
                        assert messages[0].session_id == session
