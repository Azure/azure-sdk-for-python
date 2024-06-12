# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import sys
import os
import json
import asyncio
import pytest
import uuid
from msrest.serialization import UTC
import datetime as dt

from devtools_testutils import AzureRecordedTestCase
from azure.core.messaging import CloudEvent
from azure.core.exceptions import HttpResponseError
from azure.eventgrid.aio import EventGridConsumerClient, EventGridPublisherClient
from eventgrid_preparer import (
    EventGridPreparer,
)


class TestEventGridDualClientAsync(AzureRecordedTestCase):
    def create_eg_publisher_client(self, endpoint, topic=None):
        credential = self.get_credential(EventGridPublisherClient, is_async=True)
        client = self.create_client_from_credential(
            EventGridPublisherClient, credential=credential, endpoint=endpoint, namespace_topic=topic
        )
        return client

    def create_eg_consumer_client(self, endpoint, topic=None, subscription=None):
        credential = self.get_credential(EventGridConsumerClient, is_async=True)
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
    @pytest.mark.asyncio
    async def test_eg_dual_client_send_eventgrid_event(self, **kwargs):
        eventgrid_endpoint = kwargs["eventgrid_endpoint"]
        eventgrid_topic_name = kwargs["eventgrid_topic_name"]
        event_endpoint = kwargs["eventgrid_topic_endpoint"]
        namespace_client = self.create_eg_publisher_client(eventgrid_endpoint, eventgrid_topic_name)
        basic_client = self.create_eg_publisher_client(event_endpoint)

        event = {
            "id": uuid.uuid4(),
            "data": {
                "team": "azure-sdk",
                "project": "azure-eventgrid",
            },
            "subject": "Door1",
            "eventType": "Azure.SDK.TestEvent",
            "eventTime": dt.datetime.now(UTC()),
            "dataVersion": "2.0",
        }

        await basic_client.send(event)

        with pytest.raises(TypeError):
            await namespace_client.send(event)

    @pytest.mark.live_test_only
    @EventGridPreparer()
    @pytest.mark.asyncio
    async def test_eg_dual_client_send_custom_event(self, **kwargs):
        eventgrid_endpoint = kwargs["eventgrid_endpoint"]
        eventgrid_topic_name = kwargs["eventgrid_topic_name"]
        custom_event_endpoint = kwargs["eventgrid_custom_event_topic_endpoint"]
        namespace_client = self.create_eg_publisher_client(eventgrid_endpoint, eventgrid_topic_name)
        basic_client = self.create_eg_publisher_client(custom_event_endpoint)

        custom_event = {
            "customSubject": "sample",
            "customEventType": "sample.event",
            "customDataVersion": "2.0",
            "customId": "1234",
            "customEventTime": dt.datetime.now(UTC()).isoformat(),
            "customData": "sample data",
        }

        await basic_client.send(custom_event)

        with pytest.raises(HttpResponseError):
            await namespace_client.send(custom_event)

    @pytest.mark.live_test_only
    @EventGridPreparer()
    @pytest.mark.asyncio
    async def test_eg_dual_client_send_channel_name(self, **kwargs):
        eventgrid_endpoint = kwargs["eventgrid_endpoint"]
        eventgrid_topic_name = kwargs["eventgrid_topic_name"]
        cloud_event_endpoint = kwargs["eventgrid_partner_namespace_topic_endpoint"]
        channel_name = kwargs["eventgrid_partner_channel_name"]
        namespace_client = self.create_eg_publisher_client(eventgrid_endpoint, eventgrid_topic_name)
        basic_client = self.create_eg_publisher_client(cloud_event_endpoint)

        cloud_event = CloudEvent(
            source="http://samplesource.dev",
            data={"sample": "cloudevent"},
            type="Sample.Cloud.Event",
        )

        await basic_client.send(cloud_event, channel_name=channel_name)

        with pytest.raises(ValueError):
            await namespace_client.send(cloud_event, channel_name=channel_name)

    @pytest.mark.live_test_only
    @EventGridPreparer()
    @pytest.mark.asyncio
    async def test_eg_dual_client_consumer(self, **kwargs):
        eventgrid_endpoint = kwargs["eventgrid_endpoint"]
        eventgrid_topic_name = kwargs["eventgrid_topic_name"]
        eventgrid_subscription = kwargs["eventgrid_event_subscription_name"]
        cloud_event_endpoint = kwargs["eventgrid_cloud_event_topic_endpoint"]
        namespace_client = self.create_eg_consumer_client(
            eventgrid_endpoint, eventgrid_topic_name, eventgrid_subscription
        )

        await namespace_client.receive()

        with pytest.raises(ValueError):
            basic_client = self.create_eg_consumer_client(cloud_event_endpoint)
            await basic_client.receive()
