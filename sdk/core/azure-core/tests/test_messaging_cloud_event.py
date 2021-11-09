# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import uuid
import datetime

from azure.core.messaging import CloudEvent
from azure.core.utils._utils import _convert_to_isoformat
from azure.core.utils._messaging_shared import _get_json_content
from azure.core.serialization import NULL

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
            return """{"id":"f208feff-099b-4bda-a341-4afd0fa02fef","source":"https://egsample.dev/sampleevent","data":"ServiceBus","type":"Azure.Sdk.Sample","time":"2021-07-22T22:27:38.960209Z","specversion":"1.0"}"""
        return self.data
    
    next = __next__

class MockEhBody(object):
    def __init__(self, data=None):
        self.data = data

    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.data:
            return b'[{"id":"f208feff-099b-4bda-a341-4afd0fa02fef","source":"https://egsample.dev/sampleevent","data":"Eventhub","type":"Azure.Sdk.Sample","time":"2021-07-22T22:27:38.960209Z","specversion":"1.0"}]'
        return self.data

    next = __next__


# Cloud Event tests
def test_cloud_event_constructor():
    event = CloudEvent(
        source='Azure.Core.Sample',
        type='SampleType',
        data='cloudevent'
        )
    
    assert event.specversion == '1.0'
    assert event.time.__class__ == datetime.datetime
    assert event.id is not None
    assert event.source == 'Azure.Core.Sample'
    assert event.data == 'cloudevent'

def test_cloud_event_constructor_unexpected_keyword():
    with pytest.raises(ValueError) as e:
        event = CloudEvent(
            source='Azure.Core.Sample',
            type='SampleType',
            data='cloudevent',
            unexpected_keyword="not allowed",
            another_bad_kwarg="not allowed either"
            )
        assert "unexpected_keyword" in e
        assert "another_bad_kwarg" in e

def test_cloud_event_constructor_blank_data():
    event = CloudEvent(
        source='Azure.Core.Sample',
        type='SampleType',
        data=''
        )
    
    assert event.specversion == '1.0'
    assert event.time.__class__ == datetime.datetime
    assert event.id is not None
    assert event.source == 'Azure.Core.Sample'
    assert event.data == ''

def test_cloud_event_constructor_NULL_data():
    event = CloudEvent(
        source='Azure.Core.Sample',
        type='SampleType',
        data=NULL
        )

    assert event.data == NULL
    assert event.data is NULL

def test_cloud_event_constructor_none_data():
    event = CloudEvent(
        source='Azure.Core.Sample',
        type='SampleType',
        data=None
        )

    assert event.data == None

def test_cloud_event_constructor_missing_data():
    event = CloudEvent(
        source='Azure.Core.Sample',
        type='SampleType',
        )
    
    assert event.data == None
    assert event.datacontenttype == None
    assert event.dataschema == None
    assert event.subject == None

def test_cloud_storage_dict():
    cloud_storage_dict = {
        "id":"a0517898-9fa4-4e70-b4a3-afda1dd68672",
        "source":"/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}",
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
        "type":"Microsoft.Storage.BlobCreated",
        "time":"2021-02-18T20:18:10.581147898Z",
        "specversion":"1.0"
    }

    event = CloudEvent.from_dict(cloud_storage_dict)
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
    assert event.specversion == "1.0"
    assert event.time.__class__ == datetime.datetime
    assert event.time.month == 2
    assert event.time.day == 18
    assert event.time.hour == 20
    assert event.time.microsecond == 581147
    assert event.__class__ == CloudEvent
    assert "id" in cloud_storage_dict
    assert "data" in cloud_storage_dict


def test_cloud_custom_dict_with_extensions():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10.539861122+00:00",
        "specversion":"1.0",
        "ext1": "example",
        "ext2": "example2"
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
    assert event.data == {"team": "event grid squad"}
    assert event.__class__ == CloudEvent
    assert event.time.month == 2
    assert event.time.day == 18
    assert event.time.hour == 20
    assert event.time.microsecond == 539861
    assert event.extensions == {"ext1": "example", "ext2": "example2"}

def test_cloud_custom_dict_ms_precision_is_gt_six():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10.539861122+00:00",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
    assert event.data == {"team": "event grid squad"}
    assert event.__class__ == CloudEvent
    assert event.time.month == 2
    assert event.time.day == 18
    assert event.time.hour == 20
    assert event.time.microsecond == 539861

def test_cloud_custom_dict_ms_precision_is_lt_six():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10.123+00:00",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
    assert event.data == {"team": "event grid squad"}
    assert event.__class__ == CloudEvent
    assert event.time.month == 2
    assert event.time.day == 18
    assert event.time.hour == 20
    assert event.time.microsecond == 123000

def test_cloud_custom_dict_ms_precision_is_eq_six():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10.123456+00:00",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
    assert event.data == {"team": "event grid squad"}
    assert event.__class__ == CloudEvent
    assert event.time.month == 2
    assert event.time.day == 18
    assert event.time.hour == 20
    assert event.time.microsecond == 123456

def test_cloud_custom_dict_ms_precision_is_gt_six_z_not():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10.539861122Z",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
    assert event.data == {"team": "event grid squad"}
    assert event.__class__ == CloudEvent
    assert event.time.month == 2
    assert event.time.day == 18
    assert event.time.hour == 20
    assert event.time.microsecond == 539861

def test_cloud_custom_dict_ms_precision_is_lt_six_z_not():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10.123Z",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
    assert event.data == {"team": "event grid squad"}
    assert event.__class__ == CloudEvent
    assert event.time.month == 2
    assert event.time.day == 18
    assert event.time.hour == 20
    assert event.time.microsecond == 123000

def test_cloud_custom_dict_ms_precision_is_eq_six_z_not():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e034",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10.123456Z",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
    assert event.data == {"team": "event grid squad"}
    assert event.__class__ == CloudEvent
    assert event.time.month == 2
    assert event.time.day == 18
    assert event.time.hour == 20
    assert event.time.microsecond == 123456

def test_cloud_custom_dict_blank_data():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":'',
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10+00:00",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)
    assert event.data == ''
    assert event.__class__ == CloudEvent

def test_cloud_custom_dict_no_data():
    cloud_custom_dict_with_missing_data = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10+00:00",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_missing_data)
    assert event.__class__ == CloudEvent
    assert event.data is None

def test_cloud_custom_dict_null_data():
    cloud_custom_dict_with_none_data = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "type":"Azure.Sdk.Sample",
        "data":None,
        "dataschema":None,
        "time":"2021-02-18T20:18:10+00:00",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_none_data)
    assert event.__class__ == CloudEvent
    assert event.data == NULL
    assert event.dataschema is NULL

def test_cloud_custom_dict_valid_optional_attrs():
    cloud_custom_dict_with_none_data = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "type":"Azure.Sdk.Sample",
        "data":None,
        "dataschema":"exists",
        "time":"2021-02-18T20:18:10+00:00",
        "specversion":"1.0",
    }
    event = CloudEvent.from_dict(cloud_custom_dict_with_none_data)
    assert event.__class__ == CloudEvent
    assert event.data is NULL
    assert event.dataschema == "exists"

def test_cloud_custom_dict_both_data_and_base64():
    cloud_custom_dict_with_data_and_base64 = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":"abc",
        "data_base64":"Y2Wa==",
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-18T20:18:10+00:00",
        "specversion":"1.0",
    }
    with pytest.raises(ValueError):
        event = CloudEvent.from_dict(cloud_custom_dict_with_data_and_base64)

def test_cloud_custom_dict_base64():
    cloud_custom_dict_base64 = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data_base64":'Y2xvdWRldmVudA==',
        "type":"Azure.Sdk.Sample",
        "time":"2021-02-23T17:11:13.308772-08:00",
        "specversion":"1.0"
    }
    event = CloudEvent.from_dict(cloud_custom_dict_base64)
    assert event.data == b'cloudevent'
    assert event.specversion == "1.0"
    assert event.time.hour == 17
    assert event.time.minute == 11
    assert event.time.day == 23
    assert event.time.tzinfo is not None
    assert event.__class__ == CloudEvent

def test_data_and_base64_both_exist_raises():
    with pytest.raises(ValueError):
        CloudEvent.from_dict(
            {"source":'sample',
            "type":'type',
            "data":'data',
            "data_base64":'Y2kQ=='
            }
        )

def test_cloud_event_repr():
    event = CloudEvent(
        source='Azure.Core.Sample',
        type='SampleType',
        data='cloudevent'
        )

    assert repr(event).startswith("CloudEvent(source=Azure.Core.Sample, type=SampleType, specversion=1.0,")

def test_extensions_upper_case_value_error():	
    with pytest.raises(ValueError):	
        event = CloudEvent(	
            source='sample',	
            type='type',	
            data='data',	
            extensions={"lowercase123": "accepted", "NOTlower123": "not allowed"}	
        )

def test_extensions_not_alphanumeric_value_error():	
    with pytest.raises(ValueError):	
        event = CloudEvent(	
            source='sample',	
            type='type',	
            data='data',	
            extensions={"lowercase123": "accepted", "not@lph@nu^^3ic": "not allowed"}	
        )

def test_cloud_from_dict_with_invalid_extensions():
    cloud_custom_dict_with_extensions = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2020-08-07T02:06:08.11969Z",
        "specversion":"1.0",
        "ext1": "example",
        "BADext2": "example2"
    }
    with pytest.raises(ValueError):
        event = CloudEvent.from_dict(cloud_custom_dict_with_extensions)

def test_cloud_custom_dict_ms_precision_is_gt_six():
    time ="2021-02-18T20:18:10.539861122+00:00"
    date_obj = _convert_to_isoformat(time)

    assert date_obj.month == 2
    assert date_obj.day == 18
    assert date_obj.hour == 20
    assert date_obj.microsecond == 539861

def test_cloud_custom_dict_ms_precision_is_lt_six():
    time ="2021-02-18T20:18:10.123+00:00"
    date_obj = _convert_to_isoformat(time)

    assert date_obj.month == 2
    assert date_obj.day == 18
    assert date_obj.hour == 20
    assert date_obj.microsecond == 123000

def test_cloud_custom_dict_ms_precision_is_eq_six():
    time ="2021-02-18T20:18:10.123456+00:00"
    date_obj = _convert_to_isoformat(time)

    assert date_obj.month == 2
    assert date_obj.day == 18
    assert date_obj.hour == 20
    assert date_obj.microsecond == 123456

def test_cloud_custom_dict_ms_precision_is_gt_six_z_not():
    time ="2021-02-18T20:18:10.539861122Z"
    date_obj = _convert_to_isoformat(time)

    assert date_obj.month == 2
    assert date_obj.day == 18
    assert date_obj.hour == 20
    assert date_obj.microsecond == 539861

def test_cloud_custom_dict_ms_precision_is_lt_six_z_not():
    time ="2021-02-18T20:18:10.123Z"
    date_obj = _convert_to_isoformat(time)

    assert date_obj.month == 2
    assert date_obj.day == 18
    assert date_obj.hour == 20
    assert date_obj.microsecond == 123000

def test_cloud_custom_dict_ms_precision_is_eq_six_z_not():
    time ="2021-02-18T20:18:10.123456Z"
    date_obj = _convert_to_isoformat(time)

    assert date_obj.month == 2
    assert date_obj.day == 18
    assert date_obj.hour == 20
    assert date_obj.microsecond == 123456

def test_eventgrid_event_schema_raises():
    cloud_custom_dict = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "data":{"team": "event grid squad"},
        "dataVersion": "1.0",
        "subject":"Azure.Sdk.Sample",
        "eventTime":"2020-08-07T02:06:08.11969Z",
        "eventType":"pull request",
    }
    with pytest.raises(ValueError, match="The event you are trying to parse follows the Eventgrid Schema. You can parse EventGrid events using EventGridEvent.from_dict method in the azure-eventgrid library."):
        CloudEvent.from_dict(cloud_custom_dict)

def test_wrong_schema_raises_no_source():
    cloud_custom_dict = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2020-08-07T02:06:08.11969Z",
        "specversion":"1.0",
    }
    with pytest.raises(ValueError, match="The event does not conform to the cloud event spec https://github.com/cloudevents/spec. The `source` and `type` params are required."):
        CloudEvent.from_dict(cloud_custom_dict)

def test_wrong_schema_raises_no_type():
    cloud_custom_dict = {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "data":{"team": "event grid squad"},
        "source":"Azure/Sdk/Sample",
        "time":"2020-08-07T02:06:08.11969Z",
        "specversion":"1.0",
    }
    with pytest.raises(ValueError, match="The event does not conform to the cloud event spec https://github.com/cloudevents/spec. The `source` and `type` params are required."):
        CloudEvent.from_dict(cloud_custom_dict)

def test_get_bytes_storage_queue():
    cloud_storage_dict = """{
        "id":"a0517898-9fa4-4e70-b4a3-afda1dd68672",
        "source":"/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}",
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
        "type":"Microsoft.Storage.BlobCreated",
        "time":"2021-02-18T20:18:10.581147898Z",
        "specversion":"1.0"
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
    assert dict.get('specversion') == "1.0"

def test_get_bytes_storage_queue_wrong_content():
    cloud_storage_string = u'This is a random string which must fail'
    obj = MockQueueMessage(content=cloud_storage_string)

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
    assert dict.get('specversion') == '1.0'

def test_get_bytes_servicebus_wrong_content():
    obj = MockServiceBusReceivedMessage(
        body=MockBody(data="random string"),
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
        _get_json_content(obj)

def test_get_bytes_eventhubs():
    obj = MockEventhubData(
        body=MockEhBody()
    )
    dict = _get_json_content(obj)
    assert dict.get('data') == 'Eventhub'
    assert dict.get('specversion') == '1.0'

def test_get_bytes_eventhubs_wrong_content():
    obj = MockEventhubData(
        body=MockEhBody(data='random string')
    )

    with pytest.raises(ValueError, match="Failed to load JSON content from the object."):
        dict = _get_json_content(obj)

def test_get_bytes_random_obj():
    json_str = '{"id": "de0fd76c-4ef4-4dfb-ab3a-8f24a307e033", "source": "https://egtest.dev/cloudcustomevent", "data": {"team": "event grid squad"}, "type": "Azure.Sdk.Sample", "time": "2020-08-07T02:06:08.11969Z", "specversion": "1.0"}'
    random_obj =  {
        "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
        "source":"https://egtest.dev/cloudcustomevent",
        "data":{"team": "event grid squad"},
        "type":"Azure.Sdk.Sample",
        "time":"2020-08-07T02:06:08.11969Z",
        "specversion":"1.0"
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
    event = CloudEvent.from_json(obj)

    assert event.id == "f208feff-099b-4bda-a341-4afd0fa02fef"
    assert event.data == "ServiceBus"

def test_from_json_eh():
    obj = MockEventhubData(
        body=MockEhBody()
    )
    event = CloudEvent.from_json(obj)
    assert event.id == "f208feff-099b-4bda-a341-4afd0fa02fef"
    assert event.data == "Eventhub"

def test_from_json_storage():
    cloud_storage_dict = """{
        "id":"a0517898-9fa4-4e70-b4a3-afda1dd68672",
        "source":"/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}",
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
        "type":"Microsoft.Storage.BlobCreated",
        "time":"2021-02-18T20:18:10.581147898Z",
        "specversion":"1.0"
    }"""
    obj = MockQueueMessage(content=cloud_storage_dict)
    event = CloudEvent.from_json(obj)
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
    json_str = '{"id": "de0fd76c-4ef4-4dfb-ab3a-8f24a307e033", "source": "https://egtest.dev/cloudcustomevent", "data": {"team": "event grid squad"}, "type": "Azure.Sdk.Sample", "time": "2020-08-07T02:06:08.11969Z", "specversion": "1.0"}'
    event = CloudEvent.from_json(json_str)

    assert event.data == {"team": "event grid squad"}
    assert event.time.year == 2020
    assert event.time.month == 8
    assert event.time.day == 7
    assert event.time.hour == 2
