# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
import time
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.eventgrid import EventGridClient, EventGridEvent
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from eventgrid_preparer import EventGridPreparer

class ArgPasser:
    def __call__(self, fn):
        def _preparer(test_class, level, **kwargs):
            fn(test_class, level, **kwargs)
        return _preparer

class TestEGDualClient(AzureRecordedTestCase):
    def create_eg_client(self, endpoint, key, level):
        client = EventGridClient(
            endpoint=endpoint, credential=AzureKeyCredential(key), level=level
        )
        return client
    

    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_create_client_publish(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key, level=level)
        
        from xml.etree import ElementTree as ET
        xml_string = """<?xml version="1.0" encoding="UTF-8"?><Data><test>test</test></Data>"""
        tree = xml_string.encode('utf-8')
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=tree,
            datacontenttype="text/xml",
            extensions={"extension1": "value1", "extension2": "value2"}
        )

        if level=="Basic":
            with pytest.raises(ValueError):
                client.send(
                    topic_name=eventgrid_topic_name, events=event, binary_mode=True
                )
        else:
            client.send(
                topic_name=eventgrid_topic_name, events=event, binary_mode=True
            )

    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_create_client_receive(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key, level=level)
        
        from xml.etree import ElementTree as ET
        xml_string = """<?xml version="1.0" encoding="UTF-8"?><Data><test>test</test></Data>"""
        tree = xml_string.encode('utf-8')
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=tree,
            datacontenttype="text/xml",
            extensions={"extension1": "value1", "extension2": "value2"}
        )

        if level=="Basic":
            with pytest.raises(AttributeError):
                client.receive_cloud_events(
                    topic_name=eventgrid_topic_name, event_subscription_name=eventgrid_event_subscription_name
                )
        else:
            client.receive_cloud_events(
                topic_name=eventgrid_topic_name, event_subscription_name=eventgrid_event_subscription_name
            )

    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_create_client_publish_event(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name,
                                   eventgrid_topic_key, eventgrid_topic_endpoint):
        if level=="Basic":
            client = self.create_eg_client(eventgrid_topic_endpoint, eventgrid_topic_key, level=level)
        else:
            client = self.create_eg_client(eventgrid_endpoint, eventgrid_key, level=level)
        
        event = EventGridEvent(
            id="7f7d",
            subject="MySubject",
            data={
                "test": "data"
            },
            event_type="Contoso.Items.ItemReceived",
            data_version="1.0"
        )

        if level=="Basic":
            client.send(
                events=event
                )
        else:
            with pytest.raises(HttpResponseError):
                client.send(
                    topic_name=eventgrid_topic_name, events=event
                )