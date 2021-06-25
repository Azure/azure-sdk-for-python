# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import json
import datetime

from azure.core.messaging import CloudEvent
from azure.core._utils import _convert_to_isoformat
from azure.core.serialization import NULL

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