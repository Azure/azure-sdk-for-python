#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, CloudEvent, EventGridEvent

from eventgrid_preparer import (
    EventGridTopicPreparer
)


class EventGridPublisherClientTests(AzureMgmtTestCase):
    @pytest.mark.liveTest
    @ResourceGroupPreparer(name_prefix='eventgridtest')
    @EventGridTopicPreparer(name_prefix='eventgridtest')
    def test_eg_publisher_client_publish_event_grid_event_data_dict(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, **kwargs):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        hostname = eventgrid_topic.endpoint
        client = EventGridPublisherClient(hostname, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        client.send([eg_event])

    @pytest.mark.liveTest
    @ResourceGroupPreparer(name_prefix='eventgridtest')
    @EventGridTopicPreparer(name_prefix='eventgridtest')
    def test_eg_publisher_client_publish_event_grid_event_data_str(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, **kwargs):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        hostname = eventgrid_topic.endpoint
        client = EventGridPublisherClient(hostname, akc_credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data="eventgridevent", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        client.send([eg_event])

    @pytest.mark.liveTest
    @ResourceGroupPreparer(name_prefix='eventgridtest')
    @EventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_eg_publisher_client_publish_cloud_event_data_dict(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, **kwargs):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        hostname = eventgrid_topic.endpoint
        client = EventGridPublisherClient(hostname, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = {"sample": "cloudevent"},
                type="Sample.Cloud.Event"
                )
        client.send([cloud_event])

    @pytest.mark.liveTest
    @ResourceGroupPreparer(name_prefix='eventgridtest')
    @EventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_eg_publisher_client_publish_cloud_event_data_str(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, **kwargs):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        hostname = eventgrid_topic.endpoint
        client = EventGridPublisherClient(hostname, akc_credential)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        client.send([cloud_event])
    
    # add test with signature credential
    