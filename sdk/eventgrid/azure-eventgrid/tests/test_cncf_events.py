
import json
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.eventgrid import EventGridPublisherClient
from cloudevents.http import CloudEvent

from eventgrid_preparer import (
    EventGridPreparer,
)

class TestEventGridPublisherClientCncf(AzureRecordedTestCase):
    def create_eg_publisher_client(self, endpoint):
        credential = self.get_credential(EventGridPublisherClient)
        client = self.create_client_from_credential(EventGridPublisherClient, credential=credential, endpoint=endpoint)
        return client

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_dict(self, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
        }
        data = {"message": "Hello World!"}
        cloud_event = CloudEvent(attributes, data)
        def callback(request):
            req = json.loads(request.http_request.body)
            assert req[0].get("data") is not None
            assert isinstance(req[0], dict)
            assert req[0].get("type") == "com.example.sampletype1"
            assert req[0].get("source") == "https://example.com/event-producer"
    
        client.send(cloud_event, raw_request_hook=callback)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_base64_using_data(self, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
        }
        data = b'hello world'
        cloud_event = CloudEvent(attributes, data)
        def callback(request):
            req = json.loads(request.http_request.body)
            assert req[0].get("data_base64") is not None
            assert req[0].get("data") is None
    
        client.send(cloud_event, raw_request_hook=callback)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_none(self, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
        }
        data = None
        cloud_event = CloudEvent(attributes, data)
        client.send(cloud_event)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_str(self, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
        }
        data = "hello world"
        def callback(request):
            req = json.loads(request.http_request.body)
            assert req[0].get("data_base64") is None
            assert req[0].get("data") is not None
        cloud_event = CloudEvent(attributes, data)
        client.send(cloud_event, raw_request_hook=callback)

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_as_list(self, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
        }
        data = "hello world"
        cloud_event = CloudEvent(attributes, data)
        client.send([cloud_event])

    @EventGridPreparer()
    @recorded_by_proxy
    def test_send_cloud_event_data_with_extensions(self, eventgrid_cloud_event_topic_endpoint):
        client = self.create_eg_publisher_client(eventgrid_cloud_event_topic_endpoint)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
            "ext1": "extension"
        }
        data = "hello world"
        cloud_event = CloudEvent(attributes, data)
        client.send([cloud_event])