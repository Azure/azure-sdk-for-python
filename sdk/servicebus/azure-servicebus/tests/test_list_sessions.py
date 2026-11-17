# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from datetime import datetime, timezone
import time

import pytest

from azure.servicebus import (
    ServiceBusClient,
    ServiceBusMessage,
)

from devtools_testutils import AzureMgmtRecordedTestCase, get_credential
from servicebus_preparer import (
    SERVICEBUS_ENDPOINT_SUFFIX,
    CachedServiceBusNamespacePreparer,
    CachedServiceBusResourceGroupPreparer,
    ServiceBusQueuePreparer,
    ServiceBusTopicPreparer,
    ServiceBusSubscriptionPreparer,
)
from utilities import uamqp_transport as get_uamqp_transport, ArgPasser

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()


class TestServiceBusListSessions(AzureMgmtRecordedTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_list_queue_sessions_with_active_messages(
        self, uamqp_transport, *, servicebus_namespace=None, servicebus_queue=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # Send messages to distinct sessions
            session_ids = [str(uuid.uuid4()) for _ in range(3)]
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                for sid in session_ids:
                    sender.send_messages(ServiceBusMessage(
                        f"test message for {sid}", session_id=sid))

            # List sessions — materialize the iterator for assertions
            result = list(sb_client.list_queue_sessions(servicebus_queue.name))

            assert isinstance(result, list)
            for sid in session_ids:
                assert sid in result

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_list_queue_sessions_empty(
        self, uamqp_transport, *, servicebus_namespace=None, servicebus_queue=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # No messages sent; should return empty
            result = list(sb_client.list_queue_sessions(servicebus_queue.name))

            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_list_subscription_sessions_with_active_messages(
        self, uamqp_transport, *, servicebus_namespace=None,
        servicebus_topic=None, servicebus_subscription=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            session_ids = [str(uuid.uuid4()) for _ in range(2)]
            with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                for sid in session_ids:
                    sender.send_messages(ServiceBusMessage(
                        f"test message for {sid}", session_id=sid))

            result = list(sb_client.list_subscription_sessions(
                servicebus_topic.name, servicebus_subscription.name))

            assert isinstance(result, list)
            for sid in session_ids:
                assert sid in result

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_list_queue_sessions_updated_after(
        self, uamqp_transport, *, servicebus_namespace=None, servicebus_queue=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # Session A is updated first; the cutoff is captured AFTER it, so A
            # predates the cutoff and must be EXCLUDED. Asserting only inclusion
            # would pass even if state_updated_after were ignored, so the
            # exclusion assertion is what actually exercises the filter.
            old_session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("old session", session_id=old_session_id))
            with sb_client.get_queue_receiver(
                servicebus_queue.name, session_id=old_session_id, max_wait_time=5,
            ) as receiver:
                receiver.session.set_state("old-state")

            # Cutoff strictly between the two session-state updates. Sleep on
            # each side so the service-side timestamps land on either side of
            # the cutoff even with client/server clock skew.
            time.sleep(10)
            cutoff = datetime.now(timezone.utc)
            time.sleep(10)

            # Session B is updated after the cutoff and must be INCLUDED.
            new_session_id = str(uuid.uuid4())
            with sb_client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("new session", session_id=new_session_id))
            with sb_client.get_queue_receiver(
                servicebus_queue.name, session_id=new_session_id, max_wait_time=5,
            ) as receiver:
                receiver.session.set_state("new-state")

            result = list(sb_client.list_queue_sessions(
                servicebus_queue.name, state_updated_after=cutoff))

            assert isinstance(result, list)
            assert new_session_id in result  # updated after cutoff
            assert old_session_id not in result  # updated before cutoff -> excluded by the filter

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_list_subscription_sessions_empty(
        self, uamqp_transport, *, servicebus_namespace=None,
        servicebus_topic=None, servicebus_subscription=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # No messages sent; should return empty
            result = list(sb_client.list_subscription_sessions(
                servicebus_topic.name, servicebus_subscription.name))

            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusTopicPreparer(name_prefix="servicebustest")
    @ServiceBusSubscriptionPreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_list_subscription_sessions_updated_after(
        self, uamqp_transport, *, servicebus_namespace=None,
        servicebus_topic=None, servicebus_subscription=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        ) as sb_client:
            # Session A is updated first; the cutoff is captured AFTER it, so A
            # predates the cutoff and must be EXCLUDED. Asserting only inclusion
            # would pass even if state_updated_after were ignored, so the
            # exclusion assertion is what actually exercises the filter.
            old_session_id = str(uuid.uuid4())
            with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                sender.send_messages(ServiceBusMessage("old session", session_id=old_session_id))
            with sb_client.get_subscription_receiver(
                servicebus_topic.name, servicebus_subscription.name,
                session_id=old_session_id, max_wait_time=5,
            ) as receiver:
                receiver.session.set_state("old-state")

            # Cutoff strictly between the two session-state updates. Sleep on
            # each side so the service-side timestamps land on either side of
            # the cutoff even with client/server clock skew.
            time.sleep(10)
            cutoff = datetime.now(timezone.utc)
            time.sleep(10)

            # Session B is updated after the cutoff and must be INCLUDED.
            new_session_id = str(uuid.uuid4())
            with sb_client.get_topic_sender(servicebus_topic.name) as sender:
                sender.send_messages(ServiceBusMessage("new session", session_id=new_session_id))
            with sb_client.get_subscription_receiver(
                servicebus_topic.name, servicebus_subscription.name,
                session_id=new_session_id, max_wait_time=5,
            ) as receiver:
                receiver.session.set_state("new-state")

            result = list(sb_client.list_subscription_sessions(
                servicebus_topic.name, servicebus_subscription.name,
                state_updated_after=cutoff))

            assert isinstance(result, list)
            assert new_session_id in result  # updated after cutoff
            assert old_session_id not in result  # updated before cutoff -> excluded by the filter
