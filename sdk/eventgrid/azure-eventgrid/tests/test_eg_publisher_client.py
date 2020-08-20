#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import pytest
from datetime import timedelta
from msrest.serialization import UTC
import datetime as dt

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, CloudEvent, EventGridEvent, CustomEvent ,EventGridSharedAccessSignatureCredential, generate_shared_access_signature

from eventgrid_preparer import (
    CachedEventGridTopicPreparer
)

class EventGridPublisherClientTests(AzureMgmtTestCase):
    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    def test_eg_publisher_client_publish_event_grid_event_data_dict(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        client.send([eg_event])

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    def test_eg_publisher_client_publish_event_grid_event_data_str(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data="eventgridevent", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        client.send([eg_event])

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_eg_publisher_client_publish_cloud_event_data_dict(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = {"sample": "cloudevent"},
                type="Sample.Cloud.Event"
                )
        client.send([cloud_event])

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_eg_publisher_client_publish_cloud_event_data_str(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        client.send([cloud_event])
    
    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='eventgridtest')
    def test_eg_publisher_client_publish_signature_credential(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
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
        client.send([eg_event])

    @pytest.mark.liveTest
    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='customeventgridtest')
    def test_eg_publisher_client_publish_custom_schema_event(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
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
        client.send([custom_event])