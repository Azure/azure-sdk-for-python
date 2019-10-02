import pytest
from azure.eventhub import EventData


def test_create_event_data_with_none():
    with pytest.raises(ValueError):
        EventData(None)
