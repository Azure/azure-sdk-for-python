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


class TestEGClientExceptions(AzureRecordedTestCase):
    def create_eg_client(self, endpoint, key):
        client = EventGridClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        return client
    

    @pytest.mark.live_test_only()
    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_binary_mode_xml(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)
        
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

        client.publish_cloud_events(
            eventgrid_topic_name, body=event, binary_mode=True
        )

        time.sleep(5)

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name,max_events=1)
        my_returned_event = events.value[0].event
        assert my_returned_event.data == xml_string
        assert my_returned_event.datacontenttype == 'text/xml'
        assert my_returned_event.type == "Contoso.Items.ItemReceived"

        tokens = []
        for detail in events.value:
            token = detail.broker_properties.lock_token
            tokens.append(token)
        rejected_result = client.reject_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, reject_options=RejectOptions(lock_tokens=tokens))



    @pytest.mark.live_test_only()
    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_binary_mode_cloud_event(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b'this is binary data',
            datacontenttype='text/plain'
        )

        client.publish_cloud_events(
            eventgrid_topic_name, body=event, binary_mode=True
        )

        time.sleep(5)

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name,max_events=1)
        my_returned_event = events.value[0].event
        assert my_returned_event.data == 'this is binary data'
        assert my_returned_event.datacontenttype == 'text/plain'
        assert my_returned_event.type == "Contoso.Items.ItemReceived"

        tokens = []
        for detail in events.value:
            token = detail.broker_properties.lock_token
            tokens.append(token)
        rejected_result = client.reject_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, reject_options=RejectOptions(lock_tokens=tokens))


    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_binary_mode_incorrect_cloud_event(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data={"key": "value"},
            datacontenttype='text/plain'
        )

        with pytest.raises(TypeError):
            client.publish_cloud_events(
                eventgrid_topic_name, body=event, binary_mode=True
            )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_binary_mode_list_cloud_event(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data={"key": "value"},
            datacontenttype='text/plain'
        )

        with pytest.raises(TypeError):
            client.publish_cloud_events(
                eventgrid_topic_name, body=[event], binary_mode=True
            )

    @pytest.mark.live_test_only()
    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_binary_mode_combinations(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b"hello",
            datacontenttype='text/plain'
        )

        dict_event = {"type": "Contoso.Items.ItemReceived", "source": "source", "subject": "MySubject", "data": b"hello", "datacontenttype": "text/plain"}

        
        client.publish_cloud_events(
            eventgrid_topic_name, body=event, binary_mode=True
        )

        client.publish_cloud_events(
            eventgrid_topic_name, body=dict_event, binary_mode=True
        )

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name,max_events=1)
        tokens = []
        for detail in events.value:
            token = detail.broker_properties.lock_token
            tokens.append(token)
        rejected_result = client.reject_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, reject_options=RejectOptions(lock_tokens=tokens))


    @pytest.mark.skip("need to update conftest")
    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_receive_cloud_event(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b'this is binary data',
        )

        client.publish_cloud_events(
            eventgrid_topic_name, body=[event]
        )

        time.sleep(5)

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name,max_events=1)
        lock_token = events.value[0].broker_properties.lock_token

        ack = client.acknowledge_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, lock_tokens=AcknowledgeOptions(lock_tokens=[lock_token]))
        assert len(ack.succeeded_lock_tokens) == 1
        assert len(ack.failed_lock_tokens) == 0

    @pytest.mark.skip("need to update conftest")
    @EventGridPreparer()
    @recorded_by_proxy
    def test_publish_release_cloud_event(self, eventgrid_endpoint, eventgrid_key, eventgrid_topic_name, eventgrid_event_subscription_name):
        client = self.create_eg_client(eventgrid_endpoint, eventgrid_key)

        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b'this is binary data',
        )

        client.publish_cloud_events(
            eventgrid_topic_name, body=[event]
        )

        time.sleep(5)

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, max_events=1)
        lock_token = events.value[0].broker_properties.lock_token

        ack = client.release_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, lock_tokens=ReleaseOptions(lock_tokens=[lock_token]))
        assert len(ack.succeeded_lock_tokens) == 1
        assert len(ack.failed_lock_tokens) == 0

        events = client.receive_cloud_events(eventgrid_topic_name, eventgrid_event_subscription_name, max_events=1)
        assert events.value[0].broker_properties.delivery_count > 1