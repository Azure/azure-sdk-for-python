# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
import time
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.eventgrid import EventGridClient
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.credentials import AzureKeyCredential

from eventgrid_preparer import EventGridPreparer


def _clean_up(client, eventgrid_topic_name, eventgrid_event_subscription_name):
    events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, max_events=100)
    tokens = []
    for detail in events.value:
        token = detail.broker_properties.lock_token
        tokens.append(token)
    ack = client.acknowledge_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, lock_tokens=tokens)


class TestEGClientExceptions(AzureRecordedTestCase):
    def create_eg_client(self, endpoint, key):
        client = EventGridClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        return client

    @pytest.mark.live_test_only()
    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_receive_cloud_event(
        self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name
    ):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b"this is binary data",
        )

        client.send(topic_name=eventgrid_topic_name, events=[event])

        time.sleep(5)

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, max_events=1)
        lock_token = events.value[0].broker_properties.lock_token

        ack = client.acknowledge_cloud_events(
            eventgrid_topic_name, eventgrid_event_subscription_name, lock_tokens=[lock_token]
        )
        assert len(ack.succeeded_lock_tokens) == 1
        assert len(ack.failed_lock_tokens) == 0

    @pytest.mark.live_test_only()
    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_release_cloud_event(
        self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name
    ):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b"this is binary data",
        )

        client.send(topic_name=eventgrid_topic_name, events=[event])

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, max_events=1)
        lock_token = events.value[0].broker_properties.lock_token

        ack = client.release_cloud_events(
            eventgrid_topic_name, eventgrid_event_subscription_name, lock_tokens=[lock_token]
        )
        assert len(ack.succeeded_lock_tokens) == 1
        assert len(ack.failed_lock_tokens) == 0

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, max_events=1)
        assert events.value[0].broker_properties.delivery_count > 1

        client.reject_cloud_events(
            eventgrid_topic_name,
            eventgrid_event_subscription_name,
            lock_tokens=[events.value[0].broker_properties.lock_token],
        )

        _clean_up(client, eventgrid_topic_name, eventgrid_event_subscription_name)

    @pytest.mark.live_test_only()
    @EventGridPreparer()
    @recorded_by_proxy
    def test_receive_type(
        self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name
    ):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data={"key": "value"},
        )

        client.send(topic_name=eventgrid_topic_name, events=event)

        time.sleep(5)

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, max_events=1)
        data = events.value[0].event.data

        assert isinstance(data, dict)

        _clean_up(client, eventgrid_topic_name, eventgrid_event_subscription_name)
