import platform
import pytest


pytestmark = pytest.mark.skipif(platform.python_implementation() == "PyPy", reason="This is ignored for PyPy")


from azure.eventhub import EventData, EventDataBatch


@pytest.mark.parametrize("test_input, expected_result",
                         [("", ""), ("AAA", "AAA"), (None, ValueError), (["a", "b", "c"], "abc"), (b"abc", "abc")])
def test_constructor(test_input, expected_result):
    if isinstance(expected_result, type):
        with pytest.raises(expected_result):
            EventData(test_input)
    else:
        event_data = EventData(test_input)
        assert event_data.body_as_str() == expected_result
        assert event_data.partition_key is None
        assert len(event_data.properties) == 0
        assert event_data.enqueued_time is None
        assert event_data.offset is None
        assert event_data.sequence_number is None
        assert len(event_data.system_properties) == 0
        assert str(event_data) == "{{ body: '{}', properties: {{}} }}".format(expected_result)
        assert repr(event_data) == "EventData(body='{}', properties={{}}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)".format(expected_result)
        with pytest.raises(TypeError):
            event_data.body_as_json()


def test_body_json():
    event_data = EventData('{"a":"b"}')
    assert str(event_data) == "{ body: '{\"a\":\"b\"}', properties: {} }"
    assert repr(event_data) == "EventData(body='{\"a\":\"b\"}', properties={}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)"
    jo = event_data.body_as_json()
    assert jo["a"] == "b"


def test_body_wrong_json():
    event_data = EventData('aaa')
    with pytest.raises(TypeError):
        event_data.body_as_json()


def test_app_properties():
    app_props = {"a": "b"}
    event_data = EventData("")
    event_data.properties = app_props
    assert str(event_data) == "{ body: '', properties: {'a': 'b'} }"
    assert repr(event_data) == "EventData(body='', properties={'a': 'b'}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)"
    assert event_data.properties["a"] == "b"


def test_event_data_batch():
    batch = EventDataBatch(max_size_in_bytes=100, partition_key="par")
    batch.add(EventData("A"))
    assert str(batch) == "EventDataBatch(max_size_in_bytes=100, partition_id=None, partition_key='par', event_count=1)"
    assert repr(batch) == "EventDataBatch(max_size_in_bytes=100, partition_id=None, partition_key='par', event_count=1)"
    assert batch.size_in_bytes == 89 and len(batch) == 1
    with pytest.raises(ValueError):
        batch.add(EventData("A"))
