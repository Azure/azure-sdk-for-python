
import json
from devtools_testutils import AzureTestCase, CachedResourceGroupPreparer

from azure_devtools.scenario_tests import ReplayableTest
from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from azure.eventgrid import EventGridPublisherClient
from cloudevents.http import CloudEvent

from eventgrid_preparer import (
    CachedEventGridTopicPreparer,
)

class EventGridPublisherClientTests(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['aeg-sas-key', 'aeg-sas-token']

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_send_cloud_event_data_dict(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
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

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_send_cloud_event_data_base64_using_data(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
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

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_send_cloud_event_data_none(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
        }
        data = None
        cloud_event = CloudEvent(attributes, data)
        client.send(cloud_event)

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_send_cloud_event_data_str(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
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

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_send_cloud_event_data_as_list(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
        }
        data = "hello world"
        cloud_event = CloudEvent(attributes, data)
        client.send([cloud_event])

    @CachedResourceGroupPreparer(name_prefix='eventgridtest')
    @CachedEventGridTopicPreparer(name_prefix='cloudeventgridtest')
    def test_send_cloud_event_data_with_extensions(self, resource_group, eventgrid_topic, eventgrid_topic_primary_key, eventgrid_topic_endpoint):
        akc_credential = AzureKeyCredential(eventgrid_topic_primary_key)
        client = EventGridPublisherClient(eventgrid_topic_endpoint, akc_credential)
        attributes = {
            "type": "com.example.sampletype1",
            "source": "https://example.com/event-producer",
            "ext1": "extension"
        }
        data = "hello world"
        cloud_event = CloudEvent(attributes, data)
        client.send([cloud_event])