import logging
import sys
import os
import pytest
import json

from azure.eventgrid import EventGridEvent
from devtools_testutils import AzureMgmtTestCase
from _mocks import (
    cloud_storage_dict,
    cloud_custom_dict_base64,
    cloud_custom_dict_with_extensions,
    eg_storage_dict
)

class EventGridDeserializerTests(AzureMgmtTestCase):
    
    # EG Event tests

    def test_eg_storage_from_dict(self, **kwargs):
        event = EventGridEvent.from_dict(eg_storage_dict)
        assert event.__class__ == EventGridEvent
        assert event.event_time == "2020-08-07T02:28:23.867525Z"
        assert event.event_type == "Microsoft.Storage.BlobCreated"
