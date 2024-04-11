# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.eventgrid import EventGridClient, EventGridEvent, ClientLevel
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from cloudevents.http import CloudEvent as CNCFCloudEvent

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
            with pytest.raises(ValueError):
                client.receive_cloud_events(
                    topic_name=eventgrid_topic_name, subscription_name=eventgrid_event_subscription_name
                )
        else:
            client.receive_cloud_events(
                topic_name=eventgrid_topic_name, subscription_name=eventgrid_event_subscription_name
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
            with pytest.raises(TypeError):
                client.send(
                    topic_name=eventgrid_topic_name, events=event
                )

    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_create_client_cloud_event(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name,
                                   eventgrid_cloud_event_topic_key, eventgrid_cloud_event_topic_endpoint):
        if level=="Basic":
            client = self.create_eg_client(eventgrid_cloud_event_topic_endpoint, eventgrid_cloud_event_topic_key, level=level)
        else:
            client = self.create_eg_client(eventgrid_endpoint, eventgrid_key, level=level)
        
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data={"test": "data"},
            datacontenttype="application/json",
            extensions={"extension1": "value1", "extension2": "value2"}
        )

        client.send(
            topic_name=eventgrid_topic_name, events=event
        )

    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_create_client_channel_name(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name,
                                   eventgrid_partner_namespace_topic_key, eventgrid_partner_namespace_topic_endpoint, eventgrid_partner_channel_name):
        
        client = self.create_eg_client(eventgrid_partner_namespace_topic_endpoint, eventgrid_partner_namespace_topic_key, level=level)
        
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data={"test": "data"},
            datacontenttype="application/json",
            extensions={"extension1": "value1", "extension2": "value2"}
        )

        if level=="Standard":
            with pytest.raises(ValueError):
                client.send(
                    topic_name=eventgrid_topic_name, events=event, channel_name=eventgrid_partner_channel_name
                )
        else:
            client.send(
                topic_name=eventgrid_topic_name, events=event, channel_name=eventgrid_partner_channel_name
            )

    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_publish_endpoint(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key, level=level)
        
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data={"test": "data"},
            datacontenttype="application/json",
            extensions={"extension1": "value1", "extension2": "value2"}
        )

        if level=="Basic":
            with pytest.raises(ResourceNotFoundError):
                client.send(
                    topic_name=eventgrid_topic_name, events=event
                )
        else:
            client.send(
                topic_name=eventgrid_topic_name, events=event
            )

    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_publish_cncf_events(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name,
                                   eventgrid_cloud_event_topic_key, eventgrid_cloud_event_topic_endpoint):
        if level=="Basic":
            client = self.create_eg_client(eventgrid_cloud_event_topic_endpoint, eventgrid_cloud_event_topic_key, level=level)
        else:
            client = self.create_eg_client(eventgrid_endpoint, eventgrid_key, level=level)
        
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
        }
        data = {"message": "Hello World!"}
        cloud_event = CNCFCloudEvent(attributes, data)

        if level==ClientLevel.STANDARD:
            with pytest.raises(HttpResponseError):
                client.send(
                    topic_name=eventgrid_topic_name, events=cloud_event
                )
        else:
            client.send(
                    topic_name=eventgrid_topic_name, events=cloud_event
                )
            
    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_create_client_cloud_event_dict(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name,
                                   eventgrid_cloud_event_topic_key, eventgrid_cloud_event_topic_endpoint):
        if level=="Basic":
            client = self.create_eg_client(eventgrid_cloud_event_topic_endpoint, eventgrid_cloud_event_topic_key, level=level)
        else:
            client = self.create_eg_client(eventgrid_endpoint, eventgrid_key, level=level)
        
        event = {"type": "Contoso.Items.ItemReceived",
            "source": "source",
            "subject": "MySubject",
            "data": {"test": "data"},
            "datacontenttype": "application/json",
            "extensions": {"extension1": "value1", "extension2": "value2"}}

        client.send(
            topic_name=eventgrid_topic_name, events=event
        )

    @pytest.mark.live_test_only()
    @pytest.mark.parametrize("level", ["Standard", "Basic"])
    @EventGridPreparer()
    @ArgPasser()
    @recorded_by_proxy
    def test_create_client_publish_event_dict(self, level, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name,
                                   eventgrid_topic_key, eventgrid_topic_endpoint):
        if level=="Basic":
            client = self.create_eg_client(eventgrid_topic_endpoint, eventgrid_topic_key, level=level)
        else:
            client = self.create_eg_client(eventgrid_endpoint, eventgrid_key, level=level)
        
        event = {
            "eventType": "Contoso.Items.ItemReceived",
            "data": {"itemSku": "Contoso Item SKU #1"},
            "subject": "Door1",
            "dataVersion": "2.0",
            "id": "randomuuid11",
            "eventTime": datetime.now(),
        }

        if level==ClientLevel.STANDARD:
            with pytest.raises(TypeError):
                client.send(
                    topic_name=eventgrid_topic_name, events=event
                )
        else:
            client.send(
                topic_name=eventgrid_topic_name, events=event
            )