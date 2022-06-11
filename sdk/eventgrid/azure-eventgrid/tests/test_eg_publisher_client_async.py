#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import asyncio
import sys
import os
import json
import pytest
from datetime import timedelta
from msrest.serialization import UTC
from urllib.parse import urlparse
import datetime as dt

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from azure.core.messaging import CloudEvent
from azure.core.serialization import NULL
from azure.eventgrid import EventGridEvent, generate_sas
from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid._helpers import _cloud_event_to_generated

from eventgrid_preparer import (
    EventGridPreparer
)


class TestEventGridPublisherClient(AzureRecordedTestCase):
    def create_eg_publisher_client(self, endpoint):
        credential = self.get_credential(EventGridPublisherClient, is_async=True)
        client = self.create_client_from_credential(EventGridPublisherClient, credential=credential, endpoint=endpoint)
        return client

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_event_grid_event_data_dict(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_topic_endpoint = kwargs.pop("eventgrid_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        await client.send(eg_event)


    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_event_grid_event_data_as_list(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_topic_endpoint = kwargs.pop("eventgrid_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event1 = EventGridEvent(
                subject="sample", 
                data="eventgridevent", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        eg_event2 = EventGridEvent(
                subject="sample2", 
                data="eventgridevent2", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        await client.send([eg_event1, eg_event2])

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_event_grid_event_fails_without_full_url(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_topic_key = kwargs.pop("eventgrid_topic_key")
        eventgrid_topic_endpoint = kwargs.pop("eventgrid_topic_endpoint")
        akc_credential = AzureKeyCredential(eventgrid_topic_key)
        parsed_url = urlparse(eventgrid_topic_endpoint)
        client = EventGridPublisherClient(parsed_url.netloc, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        with pytest.raises(ValueError):
            await client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_event_grid_event_data_str(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_topic_endpoint = kwargs.pop("eventgrid_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = EventGridEvent(
                subject="sample", 
                data="eventgridevent", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        await client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_event_grid_event_data_bytes(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_topic_endpoint = kwargs.pop("eventgrid_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = EventGridEvent(
                subject="sample", 
                data=b"eventgridevent", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        with pytest.raises(TypeError, match="Data in EventGridEvent cannot be bytes*"):
            await client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_event_grid_event_dict_data_bytes(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_topic_endpoint = kwargs.pop("eventgrid_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = {
                "subject":"sample", 
                "data":b"eventgridevent", 
                "eventType":"Sample.EventGrid.Event",
                "dataVersion":"2.0",
                "id": "123-ddf-133-324255ffd",
                "eventTime": dt.datetime.utcnow()
        }
        with pytest.raises(TypeError, match="Data in EventGridEvent cannot be bytes*"):
            await client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_dict(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = {"sample": "cloudevent"},
                type="Sample.Cloud.Event"
                )
        await client.send(cloud_event)


    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_str(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        await client.send(cloud_event)

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_bytes(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = b"cloudevent",
                type="Sample.Cloud.Event"
                )
        await client.send(cloud_event)

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_as_list(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        await client.send([cloud_event])


    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_with_extensions(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event",
                extensions={
                    'reasoncode':204,
                    'extension':'hello'
                    }
                )
        await client.send([cloud_event])
        internal = _cloud_event_to_generated(cloud_event).serialize()
        assert 'reasoncode' in internal
        assert 'extension' in internal
        assert internal['reasoncode'] == 204


    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_cloud_event_dict(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event1 = {
                "id": "1234",
                "source": "http://samplesource.dev",
                "specversion": "1.0",
                "data": "cloudevent",
                "type": "Sample.Cloud.Event"
        }
        await client.send(cloud_event1)

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_none(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = None,
                type="Sample.Cloud.Event"
                )
        await client.send(cloud_event)

    @pytest.mark.skip("https://github.com/Azure/azure-sdk-for-python/issues/16993")
    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_NULL(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = NULL,
                type="Sample.Cloud.Event"
                )
        def callback(request):
            req = json.loads(request.http_request.body)
            assert req[0].get("data") is None

        await client.send(cloud_event, raw_request_hook=callback)

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_signature_credential(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_topic_key = kwargs.pop("eventgrid_topic_key")
        eventgrid_topic_endpoint = kwargs.pop("eventgrid_topic_endpoint")
        expiration_date_utc = dt.datetime.now(UTC()) + timedelta(hours=1)
        signature = generate_sas(eventgrid_topic_endpoint, eventgrid_topic_key, expiration_date_utc)
        credential = AzureSasCredential(signature)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        await client.send(eg_event)


    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_custom_schema_event(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_custom_event_topic_endpoint = kwargs.pop("eventgrid_custom_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_custom_event_topic_endpoint)
        custom_event = {
                    "customSubject": "sample",
                    "customEventType": "sample.event",
                    "customDataVersion": "2.0",
                    "customId": "1234",
                    "customEventTime": dt.datetime.now(UTC()).isoformat(),
                    "customData": "sample data"
                    }
        await client.send(custom_event)


    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_custom_schema_event_as_list(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_custom_event_topic_endpoint = kwargs.pop("eventgrid_custom_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_custom_event_topic_endpoint)
        custom_event1 = {
                    "customSubject": "sample",
                    "customEventType": "sample.event",
                    "customDataVersion": "2.0",
                    "customId": "1234",
                    "customEventTime": dt.datetime.now(UTC()).isoformat(),
                    "customData": "sample data"
                    }
        custom_event2 = {
                    "customSubject": "sample2",
                    "customEventType": "sample.event",
                    "customDataVersion": "2.0",
                    "customId": "12345",
                    "customEventTime": dt.datetime.now(UTC()).isoformat(),
                    "customData": "sample data 2"
                    }
        await client.send([custom_event1, custom_event2])

    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_and_close_async_session(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_cloud_event_topic_endpoint = kwargs.pop("eventgrid_cloud_event_topic_endpoint")
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        async with client: # this throws if client can't close
            cloud_event = CloudEvent(
                    source = "http://samplesource.dev",
                    data = "cloudevent",
                    type="Sample.Cloud.Event"
                    )
            await client.send(cloud_event)

    @pytest.mark.skip()
    @EventGridPreparer()
    @recorded_by_proxy_async
    def test_send_NONE_credential_async(self, variables, eventgrid_topic_endpoint):
        with pytest.raises(ValueError, match="Parameter 'self._credential' must not be None."):
            client = EventGridPublisherClient(eventgrid_topic_endpoint, None)

    @pytest.mark.live_test_only
    @EventGridPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_send_token_credential(self, **kwargs):
        variables = kwargs.pop("variables")
        eventgrid_topic_endpoint = kwargs.pop("eventgrid_topic_endpoint")
        credential = self.get_credential(EventGridPublisherClient)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        await client.send(eg_event)