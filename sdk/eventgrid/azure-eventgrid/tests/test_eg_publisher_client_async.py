#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import asyncio
import sys
import os
import pytest
from datetime import timedelta
from msrest.serialization import UTC
import datetime as dt

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer

from azure_devtools.scenario_tests import ReplayableTest
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import CloudEvent, EventGridEvent, CustomEvent ,EventGridSharedAccessSignatureCredential, generate_shared_access_signature
from azure.eventgrid.aio import EventGridPublisherClient

from eventgrid_preparer import (
    CachedEventGridTopicPreparer
)

class EventGridPublisherClientTests(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['aeg-sas-key']

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    @pytest.mark.asyncio
    async def test_send_event_grid_event_data_dict(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        await client.send(eg_event)


    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    @pytest.mark.asyncio
    async def test_send_event_grid_event_data_as_list(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
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


    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    @pytest.mark.asyncio
    async def test_send_event_grid_event_data_str(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data="eventgridevent", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        await client.send(eg_event)

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    @pytest.mark.asyncio
    async def test_send_event_grid_event_data_bytes(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data=b"eventgridevent", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        with pytest.raises(TypeError, match="Data in EventGridEvent cannot be bytes*"):
            await client.send(eg_event)

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    @pytest.mark.asyncio
    async def test_send_event_grid_event_dict_data_bytes(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        eg_event = {
                "subject":"sample", 
                "data":b"eventgridevent", 
                "event_type":"Sample.EventGrid.Event",
                "data_version":"2.0"
        }
        with pytest.raises(TypeError, match="Data in EventGridEvent cannot be bytes*"):
            await client.send(eg_event)

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_dict(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = {"sample": "cloudevent"},
                type="Sample.Cloud.Event"
                )
        await client.send(cloud_event)


    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_str(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        await client.send(cloud_event)

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_bytes(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = b"cloudevent",
                type="Sample.Cloud.Event"
                )
        await client.send(cloud_event)

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_as_list(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        await client.send([cloud_event])


    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    @pytest.mark.asyncio
    async def test_send_cloud_event_data_with_extensions(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event",
                extensions={
                    'reason_code':204,
                    'extension':'hello'
                    }
                )
        await client.send([cloud_event])
        internal = cloud_event._to_generated().serialize()
        assert 'reason_code' in internal
        assert 'extension' in internal
        assert internal['reason_code'] == 204


    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    @pytest.mark.asyncio
    async def test_send_cloud_event_dict(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        cloud_event1 = {
                "id": "1234",
                "source": "http://samplesource.dev",
                "specversion": "1.0",
                "data": "cloudevent",
                "type": "Sample.Cloud.Event"
        }
        await client.send(cloud_event1)


    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    @pytest.mark.asyncio
    async def test_send_signature_credential(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        expiration_date_utc = dt.datetime.now(UTC()) + timedelta(hours=1)
        signature = generate_shared_access_signature(eventgrid_topic_endpoint, eventgrid_topic_primary_key, expiration_date_utc)
        credential = EventGridSharedAccessSignatureCredential(signature)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        await client.send(eg_event)


    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='customeventgridtest')
    @pytest.mark.asyncio
    async def test_send_custom_schema_event(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        custom_event = CustomEvent(
                    {
                    "customSubject": "sample",
                    "customEventType": "sample.event",
                    "customDataVersion": "2.0",
                    "customId": "1234",
                    "customEventTime": dt.datetime.now(UTC()).isoformat(),
                    "customData": "sample data"
                    }
                )
        await client.send(custom_event)


    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='customeventgridtest')
    @pytest.mark.asyncio
    async def test_send_custom_schema_event_as_list(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        custom_event1 = CustomEvent(
                    {
                    "customSubject": "sample",
                    "customEventType": "sample.event",
                    "customDataVersion": "2.0",
                    "customId": "1234",
                    "customEventTime": dt.datetime.now(UTC()).isoformat(),
                    "customData": "sample data"
                    }
                )
        custom_event2 = CustomEvent(
                    {
                    "customSubject": "sample2",
                    "customEventType": "sample.event",
                    "customDataVersion": "2.0",
                    "customId": "12345",
                    "customEventTime": dt.datetime.now(UTC()).isoformat(),
                    "customData": "sample data 2"
                    }
                )
        await client.send([custom_event1, custom_event2])
