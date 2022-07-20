#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import json
import pytest
import uuid
from datetime import datetime, timedelta
from msrest.serialization import UTC
import datetime as dt

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from devtools_testutils import  AzureRecordedTestCase, recorded_by_proxy

from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from azure.core.messaging import CloudEvent
from azure.core.serialization import NULL
from azure.eventgrid import EventGridPublisherClient, EventGridEvent, generate_sas
from azure.eventgrid._helpers import _cloud_event_to_generated

from eventgrid_preparer import (
    EventGridPreparer,
)

class TestEventGridPublisherClient(AzureRecordedTestCase):
    def create_eg_publisher_client(self, endpoint):
        credential = self.get_credential(EventGridPublisherClient)
        client = self.create_client_from_credential(EventGridPublisherClient, credential=credential, endpoint=endpoint)
        return client

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_event_grid_event_data_dict(self, variables, eventgrid_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_event_grid_event_fails_without_full_url(self, variables, eventgrid_topic_key, eventgrid_topic_endpoint):
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
            client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_event_grid_event_data_as_list(self, variables, eventgrid_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event1 = EventGridEvent(
                subject="sample", 
                data=u"eventgridevent",
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        eg_event2 = EventGridEvent(
                subject="sample2", 
                data=u"eventgridevent2",
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        client.send([eg_event1, eg_event2])

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_event_grid_event_data_str(self, variables, eventgrid_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = EventGridEvent(
                subject="sample", 
                data=u"eventgridevent",
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_event_grid_event_data_bytes(self, variables, eventgrid_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = EventGridEvent(
                subject="sample", 
                data=b"eventgridevent", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        with pytest.raises(TypeError, match="Data in EventGridEvent cannot be bytes*"):
            client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_event_grid_event_dict_data_bytes(self, variables, eventgrid_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = {
                "subject":"sample", 
                "data":b"eventgridevent", 
                "eventType":"Sample.EventGrid.Event",
                "dataVersion":"2.0",
                "id": uuid.uuid4(),
                "eventTime": datetime.now()
        }
        with pytest.raises(TypeError, match="Data in EventGridEvent cannot be bytes*"):
            client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_event_grid_event_dict_data_dict(self, variables, eventgrid_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_topic_endpoint)
        eg_event = {
                "subject":"sample", 
                "data":{"key1": "Sample.EventGrid.Event"}, 
                "eventType":"Sample.EventGrid.Event",
                "dataVersion":"2.0",
                "id": uuid.uuid4(),
                "eventTime": datetime.now()
        }
        client.send(eg_event)


    ### CLOUD EVENT TESTS

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_dict(self, variables, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = {"sample": "cloudevent"},
                type="Sample.Cloud.Event"
                )
        client.send(cloud_event)

    @pytest.mark.skip("https://github.com/Azure/azure-sdk-for-python/issues/16993")
    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_NULL(self, variables, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = NULL,
                type="Sample.Cloud.Event"
                )
        
        def callback(request):
            req = json.loads(request.http_request.body)
            assert req[0].get("data") is None

        client.send(cloud_event, raw_request_hook=callback)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_base64_using_data(self, variables, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = b'cloudevent',
                type="Sample.Cloud.Event"
                )

        def callback(request):
            req = json.loads(request.http_request.body)
            assert req[0].get("data_base64") is not None
            assert req[0].get("data") is None

        client.send(cloud_event, raw_response_hook=callback)

    def test_send_cloud_event_fails_on_providing_data_and_b64(self):
        with pytest.raises(ValueError, match="Unexpected keyword arguments data_base64.*"):
            cloud_event = CloudEvent(
                    source = "http://samplesource.dev",
                    data_base64 = b'cloudevent',
                    data = "random data",
                    type="Sample.Cloud.Event"
                    )

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_none(self, variables, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = None,
                type="Sample.Cloud.Event"
                )
        client.send(cloud_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_str(self, variables, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        client.send(cloud_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_bytes(self, variables, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = b"cloudevent",
                type="Sample.Cloud.Event"
                )
        client.send(cloud_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_as_list(self, variables, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        client.send([cloud_event])

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_with_extensions(self, variables, eventgrid_cloud_event_topic_endpoint):
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
        client.send([cloud_event])
        internal = _cloud_event_to_generated(cloud_event).serialize()
        assert 'reasoncode' in internal
        assert 'extension' in internal
        assert internal['reasoncode'] == 204

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_dict(self, variables, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        cloud_event1 = {
                "id": "1234",
                "source": "http://samplesource.dev",
                "specversion": "1.0",
                "data": "cloudevent",
                "type": "Sample.Cloud.Event"
        }
        client.send(cloud_event1)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_signature_credential(self, variables, eventgrid_topic_key, eventgrid_topic_endpoint):
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
        client.send(eg_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_NONE_credential(self, variables, eventgrid_topic_endpoint):
        with pytest.raises(ValueError, match="Parameter 'self._credential' must not be None."):
            client = EventGridPublisherClient(eventgrid_topic_endpoint, None)
        
    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_custom_schema_event(self, variables, eventgrid_custom_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_custom_event_topic_endpoint)
        custom_event = {
                    "customSubject": "sample",
                    "customEventType": "sample.event",
                    "customDataVersion": "2.0",
                    "customId": "1234",
                    "customEventTime": dt.datetime.now(UTC()).isoformat(),
                    "customData": "sample data"
                    }
        client.send(custom_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_custom_schema_event_as_list(self, variables, eventgrid_custom_event_topic_endpoint):
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
        client.send([custom_event1, custom_event2])

    def test_send_throws_with_bad_credential(self):
        bad_credential = "I am a bad credential"
        with pytest.raises(ValueError, match="The provided credential should be an instance of a TokenCredential, AzureSasCredential or AzureKeyCredential"):
            client = EventGridPublisherClient("eventgrid_endpoint", bad_credential)

    @pytest.mark.live_test_only
    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_token_credential(self, variables, eventgrid_topic_endpoint):
        credential = self.get_credential(EventGridPublisherClient)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, credential)
        eg_event = EventGridEvent(
                subject="sample", 
                data={"sample": "eventgridevent"}, 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
                )
        client.send(eg_event)

    @pytest.mark.live_test_only
    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_partner_namespace(self, variables):
        eventgrid_partner_namespace_endpoint = os.environ['EVENTGRID_PARTNER_NAMESPACE_TOPIC_ENDPOINT']
        eventgrid_partner_namespace_key = os.environ['EVENTGRID_PARTNER_NAMESPACE_TOPIC_KEY']
        channel_name = os.environ['EVENTGRID_PARTNER_CHANNEL_NAME']
        credential = AzureKeyCredential(eventgrid_partner_namespace_key)
        client = EventGridPublisherClient(eventgrid_partner_namespace_endpoint, eventgrid_partner_namespace_key)
        cloud_event = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event"
                )
        
        def callback(request):
            req = json.loads(request.http_request.headers)
            assert req.get("aeg-channel-name") == channel_name

        client.send(cloud_event, channel_name=channel_name, raw_request_hook=callback)
