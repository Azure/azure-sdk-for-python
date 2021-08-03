# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
import pytest
import uuid
from msrest.serialization import UTC
from azure.eventgrid._messaging_shared import _get_json_content
from azure.eventgrid import EventGridEvent

class MockQueueMessage(object):
    def __init__(self, content=None):
        self.id = uuid.uuid4()
        self.inserted_on = datetime.datetime.now()
        self.expires_on = datetime.datetime.now() + datetime.timedelta(days=100)
        self.dequeue_count = 1
        self.content = content
        self.pop_receipt = None
        self.next_visible_on = None

class MockServiceBusReceivedMessage(object):
    def __init__(self, body=None, **kwargs):
        self.body=body
        self.application_properties=None
        self.session_id=None
        self.message_id='3f6c5441-5be5-4f33-80c3-3ffeb6a090ce'
        self.content_type='application/cloudevents+json; charset=utf-8'
        self.correlation_id=None
        self.to=None
        self.reply_to=None
        self.reply_to_session_id=None
        self.subject=None
        self.time_to_live=datetime.timedelta(days=14)
        self.partition_key=None
        self.scheduled_enqueue_time_utc=None
        self.auto_renew_error=None,
        self.dead_letter_error_description=None
        self.dead_letter_reason=None
        self.dead_letter_source=None
        self.delivery_count=13
        self.enqueued_sequence_number=0
        self.enqueued_time_utc=datetime.datetime(2021, 7, 22, 22, 27, 41, 236000)
        self.expires_at_utc=datetime.datetime(2021, 8, 5, 22, 27, 41, 236000)
        self.sequence_number=11219
        self.lock_token='233146e3-d5a6-45eb-826f-691d82fb8b13'

class MockEventhubData(object):
    def __init__(self, body=None):
        self._last_enqueued_event_properties = {}
        self._sys_properties = None
        if body is None:
            raise ValueError("EventData cannot be None.")

        # Internal usage only for transforming AmqpAnnotatedMessage to outgoing EventData
        self.body=body
        self._raw_amqp_message = "some amqp data"
        self.message_id = None
        self.content_type = None
        self.correlation_id = None


class MockBody(object):
    def __init__(self, data=None):
        self.data = data

    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.data:
            return """{"id":"f208feff-099b-4bda-a341-4afd0fa02fef","subject":"https://egsample.dev/sampleevent","data":"ServiceBus","event_type":"Azure.Sdk.Sample","event_time":"2021-07-22T22:27:38.960209Z","data_version":"1.0"}"""
        return self.data

    next = __next__


class MockEhBody(object):
    def __init__(self, data=None):
        self.data = data

    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.data:
            return b'[{"id":"f208feff-099b-4bda-a341-4afd0fa02fef","subject":"https://egsample.dev/sampleevent","data":"Eventhub","event_type":"Azure.Sdk.Sample","event_time":"2021-07-22T22:27:38.960209Z","data_version":"1.0"}]'
        return self.data
    
    next = __next__

def test_get_bytes_storage_queue():
    cloud_storage_dict = """{
        "id":"a0517898-9fa4-4e70-b4a3-afda1dd68672",
        "subject":"/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}",
        "data":{
            "api":"PutBlockList",
            "client_request_id":"6d79dbfb-0e37-4fc4-981f-442c9ca65760",
            "request_id":"831e1650-001e-001b-66ab-eeb76e000000",
            "e_tag":"0x8D4BCC2E4835CD0",
            "content_type":"application/octet-stream",
            "content_length":524288,
            "blob_type":"BlockBlob",
            "url":"https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
            "sequencer":"00000000000004420000000000028963",
            "storage_diagnostics":{"batchId":"b68529f3-68cd-4744-baa4-3c0498ec19f0"}
        },
        "event_type":"Microsoft.Storage.BlobCreated",
        "event_time":"2021-02-18T20:18:10.581147898Z",
        "data_version":"1.0"
    }"""
    obj = MockQueueMessage(content=cloud_storage_dict)

    dict = _get_json_content(obj)
    assert dict.get('data') == {
            "api":"PutBlockList",
            "client_request_id":"6d79dbfb-0e37-4fc4-981f-442c9ca65760",
            "request_id":"831e1650-001e-001b-66ab-eeb76e000000",
            "e_tag":"0x8D4BCC2E4835CD0",
            "content_type":"application/octet-stream",
            "content_length":524288,
            "blob_type":"BlockBlob",
            "url":"https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
            "sequencer":"00000000000004420000000000028963",
            "storage_diagnostics":{"batchId":"b68529f3-68cd-4744-baa4-3c0498ec19f0"}
        }
    assert dict.get('data_version') == "1.0"

def test_get_bytes_storage_queue_wrong_content():
    string = u'This is a random string which must fail'
    obj = MockQueueMessage(content=string)

    with pytest.raises(ValueError, match="Failed to load JSON content from the object."):
        _get_json_content(obj)

def test_get_bytes_servicebus():
    obj = MockServiceBusReceivedMessage(
        body=MockBody(),
        message_id='3f6c5441-5be5-4f33-80c3-3ffeb6a090ce',
        content_type='application/cloudevents+json; charset=utf-8',
        time_to_live=datetime.timedelta(days=14),
        delivery_count=13,
        enqueued_sequence_number=0,
        enqueued_time_utc=datetime.datetime(2021, 7, 22, 22, 27, 41, 236000),
        expires_at_utc=datetime.datetime(2021, 8, 5, 22, 27, 41, 236000),
        sequence_number=11219,
        lock_token='233146e3-d5a6-45eb-826f-691d82fb8b13'
    )
    dict = _get_json_content(obj)
    assert dict.get('data') == "ServiceBus"
    assert dict.get('data_version') == '1.0'

def test_get_bytes_servicebus_wrong_content():
    obj = MockServiceBusReceivedMessage(
        body=MockBody(data='random'),
        message_id='3f6c5441-5be5-4f33-80c3-3ffeb6a090ce',
        content_type='application/json; charset=utf-8',
        time_to_live=datetime.timedelta(days=14),
        delivery_count=13,
        enqueued_sequence_number=0,
        enqueued_time_utc=datetime.datetime(2021, 7, 22, 22, 27, 41, 236000),
        expires_at_utc=datetime.datetime(2021, 8, 5, 22, 27, 41, 236000),
        sequence_number=11219,
        lock_token='233146e3-d5a6-45eb-826f-691d82fb8b13'
    )
    with pytest.raises(ValueError, match="Failed to load JSON content from the object."):
        dict = _get_json_content(obj)


def test_get_bytes_eventhubs():
    obj = MockEventhubData(
        body=MockEhBody()
    )
    dict = _get_json_content(obj)
    assert dict.get('data') == 'Eventhub'
    assert dict.get('data_version') == '1.0'

def test_get_bytes_eventhubs_wrong_content():
    obj = MockEventhubData(
        body=MockEhBody(data='random string')
    )

    with pytest.raises(ValueError, match="Failed to load JSON content from the object."):
        dict = _get_json_content(obj)


def test_get_bytes_random_obj():
    json_str = '{"id": "de0fd76c-4ef4-4dfb-ab3a-8f24a307e033", "subject": "https://egtest.dev/cloudcustomevent", "data": {"team": "event grid squad"}, "event_type": "Azure.Sdk.Sample", "event_time": "2020-08-07T02:06:08.11969Z", "data_version": "1.0"}'
    random_obj =  {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "subject":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "event_type":"Azure.Sdk.Sample",
        "event_time":"2020-08-07T02:06:08.11969Z",
        "data_version":"1.0",
    }

    assert _get_json_content(json_str) == random_obj

def test_from_json_sb():
    obj = MockServiceBusReceivedMessage(
        body=MockBody(),
        message_id='3f6c5441-5be5-4f33-80c3-3ffeb6a090ce',
        content_type='application/cloudevents+json; charset=utf-8',
        time_to_live=datetime.timedelta(days=14),
        delivery_count=13,
        enqueued_sequence_number=0,
        enqueued_time_utc=datetime.datetime(2021, 7, 22, 22, 27, 41, 236000),
        expires_at_utc=datetime.datetime(2021, 8, 5, 22, 27, 41, 236000),
        sequence_number=11219,
        lock_token='233146e3-d5a6-45eb-826f-691d82fb8b13'
    )
    event = EventGridEvent.from_json(obj)

    assert event.id == "f208feff-099b-4bda-a341-4afd0fa02fef"
    assert event.data == "ServiceBus"

def test_from_json_eh():
    obj = MockEventhubData(
        body=MockEhBody()
    )
    event = EventGridEvent.from_json(obj)
    assert event.id == "f208feff-099b-4bda-a341-4afd0fa02fef"
    assert event.data == "Eventhub"

def test_from_json_storage():
    eg_storage_dict = """{
        "id":"a0517898-9fa4-4e70-b4a3-afda1dd68672",
        "subject":"/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}",
        "data":{
            "api":"PutBlockList",
            "client_request_id":"6d79dbfb-0e37-4fc4-981f-442c9ca65760",
            "request_id":"831e1650-001e-001b-66ab-eeb76e000000",
            "e_tag":"0x8D4BCC2E4835CD0",
            "content_type":"application/octet-stream",
            "content_length":524288,
            "blob_type":"BlockBlob",
            "url":"https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
            "sequencer":"00000000000004420000000000028963",
            "storage_diagnostics":{"batchId":"b68529f3-68cd-4744-baa4-3c0498ec19f0"}
        },
        "event_type":"Microsoft.Storage.BlobCreated",
        "event_time":"2021-02-18T20:18:10.581147898Z",
        "data_version":"1.0"
    }"""
    obj = MockQueueMessage(content=eg_storage_dict)
    event = EventGridEvent.from_json(obj)
    assert event.data == {
            "api":"PutBlockList",
            "client_request_id":"6d79dbfb-0e37-4fc4-981f-442c9ca65760",
            "request_id":"831e1650-001e-001b-66ab-eeb76e000000",
            "e_tag":"0x8D4BCC2E4835CD0",
            "content_type":"application/octet-stream",
            "content_length":524288,
            "blob_type":"BlockBlob",
            "url":"https://oc2d2817345i60006.blob.core.windows.net/oc2d2817345i200097container/oc2d2817345i20002296blob",
            "sequencer":"00000000000004420000000000028963",
            "storage_diagnostics":{"batchId":"b68529f3-68cd-4744-baa4-3c0498ec19f0"}
        }


def test_from_json():
    json_str = '{"id": "de0fd76c-4ef4-4dfb-ab3a-8f24a307e033", "subject": "https://egtest.dev/cloudcustomevent", "data": {"team": "event grid squad"}, "event_type": "Azure.Sdk.Sample", "event_time": "2020-08-07T02:06:08.11969Z", "data_version": "1.0"}'
    event = EventGridEvent.from_json(json_str)
    assert event.data == {"team": "event grid squad"}
    assert event.event_time == datetime.datetime(2020, 8, 7, 2, 6, 8, 119690, UTC())
