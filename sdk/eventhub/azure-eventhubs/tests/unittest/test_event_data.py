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
        assert event_data.application_properties is None
        assert event_data.enqueued_time is None
        assert event_data.offset is None
        assert event_data.sequence_number is None
        assert event_data.system_properties == {}
        with pytest.raises(TypeError):
            event_data.body_as_json()


def test_body_json():
    event_data = EventData('{"a":"b"}')
    jo = event_data.body_as_json()
    assert jo["a"] == "b"


def test_app_properties():
    app_props = {"a": "b"}
    event_data = EventData("")
    event_data.application_properties = app_props
    assert event_data.application_properties["a"] == "b"


def test_event_data_batch():
    batch = EventDataBatch(max_size=100, partition_key="par")
    batch.try_add(EventData("A"))
    assert batch.size == 89 and len(batch) == 1
    with pytest.raises(ValueError):
        batch.try_add(EventData("A"))
