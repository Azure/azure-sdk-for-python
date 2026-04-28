# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import uuid
from datetime import datetime, timedelta, timezone

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

from devtools_testutils import AzureMgmtRecordedTestCase, get_credential
from servicebus_preparer import (
    SERVICEBUS_ENDPOINT_SUFFIX,
    CachedServiceBusNamespacePreparer,
    CachedServiceBusResourceGroupPreparer,
    ServiceBusQueuePreparer,
    ServiceBusTopicPreparer,
    ServiceBusSubscriptionPreparer,
)
from utilities import uamqp_transport as get_uamqp_transport, ArgPasserAsync

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()


class TestServiceBusListSessionsAsync(AzureMgmtRecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_list_queue_sessions_with_active_messages_async(
        self, uamqp_transport, *, servicebus_namespace=None, servicebus_queue=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            session_ids = [str(uuid.uuid4()) for _ in range(3)]
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for sid in session_ids:
                    await sender.send_messages(ServiceBusMessage(
                        f"test message for {sid}", session_id=sid))

            result = await sb_client.list_queue_sessions(servicebus_queue.name)

            assert isinstance(result, list)
            for sid in session_ids:
                assert sid in result

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_list_queue_sessions_empty_async(
        self, uamqp_transport, *, servicebus_namespace=None, servicebus_queue=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # No messages sent; should return empty list
            result = await sb_client.list_queue_sessions(servicebus_queue.name)

            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_list_queue_sessions_updated_since_async(
        self, uamqp_transport, *, servicebus_namespace=None, servicebus_queue=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # Use a 1-minute buffer to absorb client/server clock skew.
            before_send = datetime.now(timezone.utc) - timedelta(minutes=1)

            session_id = str(uuid.uuid4())
            async with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage(
                    "test updated_since", session_id=session_id))

            # updated_since mode: sessions whose state was updated after before_send
            result = await sb_client.list_queue_sessions(
                servicebus_queue.name, updated_since=before_send)

            assert isinstance(result, list)
            assert session_id in result

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_list_subscription_sessions_with_active_messages_async(
        self, uamqp_transport, *, servicebus_namespace=None,
        servicebus_topic=None, servicebus_subscription=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            session_ids = [str(uuid.uuid4()) for _ in range(2)]
            async with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                for sid in session_ids:
                    await sender.send_messages(ServiceBusMessage(
                        f"test message for {sid}", session_id=sid))

            result = await sb_client.list_subscription_sessions(
                servicebus_topic.name, servicebus_subscription.name)

            assert isinstance(result, list)
            for sid in session_ids:
                assert sid in result

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_list_subscription_sessions_empty_async(
        self, uamqp_transport, *, servicebus_namespace=None,
        servicebus_topic=None, servicebus_subscription=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # No messages sent; should return empty list
            result = await sb_client.list_subscription_sessions(
                servicebus_topic.name, servicebus_subscription.name)

            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_list_subscription_sessions_updated_since_async(
        self, uamqp_transport, *, servicebus_namespace=None,
        servicebus_topic=None, servicebus_subscription=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # Use a 1-minute buffer to absorb client/server clock skew.
            before_send = datetime.now(timezone.utc) - timedelta(minutes=1)

            session_id = str(uuid.uuid4())
            async with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                await sender.send_messages(ServiceBusMessage(
                    "test updated_since", session_id=session_id))

            # updated_since mode: sessions whose state was updated after before_send
            result = await sb_client.list_subscription_sessions(
                servicebus_topic.name, servicebus_subscription.name,
                updated_since=before_send)

            assert isinstance(result, list)
            assert session_id in result
