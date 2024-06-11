# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import sys
import os
import json
import pytest
import uuid
from msrest.serialization import UTC
import datetime as dt

from devtools_testutils import AzureRecordedTestCase
from azure.core.messaging import CloudEvent
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridConsumerClient, EventGridPublisherClient
from eventgrid_preparer import (
    EventGridPreparer,
)


class TestEventGridConsumerClient(AzureRecordedTestCase):
    def create_eg_publisher_client(self, endpoint, topic=None):
        credential = self.get_credential(EventGridPublisherClient)
        client = self.create_client_from_credential(
            EventGridPublisherClient, credential=credential, endpoint=endpoint, namespace_topic=topic
        )
        return client

    def create_eg_consumer_client(self, endpoint, topic, subscription):
        credential = self.get_credential(EventGridConsumerClient)
        client = self.create_client_from_credential(
            EventGridConsumerClient,
            credential=credential,
            endpoint=endpoint,
            namespace_topic=topic,
            subscription=subscription,
        )
        return client

    @pytest.mark.live_test_only
    @EventGridPreparer()
    def test_receive_data(self, **kwargs):
        eventgrid_endpoint = kwargs["eventgrid_endpoint"]
        eventgrid_key = kwargs["eventgrid_key"]
        eventgrid_topic_name = kwargs["eventgrid_topic_name"]
        eventgrid_event_subscription_name = kwargs["eventgrid_event_subscription_name"]
        publisher = self.create_eg_publisher_client(eventgrid_endpoint, eventgrid_topic_name)
        consumer = self.create_eg_consumer_client(
            eventgrid_endpoint, eventgrid_topic_name, eventgrid_event_subscription_name
        )
        cloud_event = CloudEvent(
            source="http://samplesource.dev",
            data={"sample": "cloudevent"},
            type="Sample.Cloud.Event",
        )
        publisher.send(cloud_event)

        received_event = consumer.receive(max_events=1)
        assert len(received_event) == 1

        for event in received_event:
            ack_result = consumer.acknowledge(lock_tokens=[event.broker_properties.lock_token])
            assert ack_result.succeeded_lock_tokens == [event.broker_properties.lock_token]

    @pytest.mark.live_test_only
    @EventGridPreparer()
    def test_receive_renew_data(self, **kwargs):
        eventgrid_endpoint = kwargs["eventgrid_endpoint"]
        eventgrid_key = kwargs["eventgrid_key"]
        eventgrid_topic_name = kwargs["eventgrid_topic_name"]
        eventgrid_event_subscription_name = kwargs["eventgrid_event_subscription_name"]
        publisher = self.create_eg_publisher_client(eventgrid_endpoint, eventgrid_topic_name)
        consumer = self.create_eg_consumer_client(
            eventgrid_endpoint, eventgrid_topic_name, eventgrid_event_subscription_name
        )

        cloud_event = CloudEvent(
            source="http://samplesource.dev",
            data={"sample": "cloudevent"},
            type="Sample.Cloud.Event",
        )
        publisher.send(cloud_event)

        received_event = consumer.receive(max_events=1)
        assert len(received_event) == 1

        for event in received_event:
            renew_lock = consumer.renew_locks(lock_tokens=[event.broker_properties.lock_token])
            ack_result = consumer.acknowledge(lock_tokens=[event.broker_properties.lock_token])
            assert ack_result.succeeded_lock_tokens == [event.broker_properties.lock_token]

    @pytest.mark.live_test_only
    @EventGridPreparer()
    def test_receive_release_data(self, **kwargs):
        eventgrid_endpoint = kwargs["eventgrid_endpoint"]
        eventgrid_key = kwargs["eventgrid_key"]
        eventgrid_topic_name = kwargs["eventgrid_topic_name"]
        eventgrid_event_subscription_name = kwargs["eventgrid_event_subscription_name"]
        publisher = self.create_eg_publisher_client(eventgrid_endpoint, eventgrid_topic_name)
        consumer = self.create_eg_consumer_client(
            eventgrid_endpoint, eventgrid_topic_name, eventgrid_event_subscription_name
        )

        cloud_event = CloudEvent(
            source="http://samplesource.dev",
            data={"sample": "cloudevent"},
            type="Sample.Cloud.Event",
        )
        publisher.send(cloud_event)

        received_event = consumer.receive(max_events=1)
        assert len(received_event) == 1

        for event in received_event:
            release = consumer.release(lock_tokens=[event.broker_properties.lock_token])
            assert release.succeeded_lock_tokens == [event.broker_properties.lock_token]

    @pytest.mark.live_test_only
    @EventGridPreparer()
    def test_receive_reject_data(self, **kwargs):
        eventgrid_endpoint = kwargs["eventgrid_endpoint"]
        eventgrid_key = kwargs["eventgrid_key"]
        eventgrid_topic_name = kwargs["eventgrid_topic_name"]
        eventgrid_event_subscription_name = kwargs["eventgrid_event_subscription_name"]
        publisher = self.create_eg_publisher_client(eventgrid_endpoint, eventgrid_topic_name)
        consumer = self.create_eg_consumer_client(
            eventgrid_endpoint, eventgrid_topic_name, eventgrid_event_subscription_name
        )

        cloud_event = CloudEvent(
            source="http://samplesource.dev",
            data={"sample": "cloudevent"},
            type="Sample.Cloud.Event",
        )
        publisher.send(cloud_event)

        received_event = consumer.receive(max_events=1)
        assert len(received_event) == 1

        for event in received_event:
            reject = consumer.reject(lock_tokens=[event.broker_properties.lock_token])
            assert reject.succeeded_lock_tokens == [event.broker_properties.lock_token]
