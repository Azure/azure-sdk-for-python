import logging
import sys
import os
import pytest
import json

from azure.eventgrid import EventGridEvent
from devtools_testutils import AzureMgmtTestCase
from _mocks import (
    eg_storage_dict
)

class EventGridDeserializerTests(AzureMgmtTestCase):
    
    # EG Event tests

    def test_eg_storage_from_dict(self, **kwargs):
        event = EventGridEvent.from_dict(eg_storage_dict)
        assert event.__class__ == EventGridEvent
        assert event.event_type == "Microsoft.Storage.BlobCreated"
