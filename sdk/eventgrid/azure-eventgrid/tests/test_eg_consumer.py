#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import pytest
import json
import datetime as dt

from devtools_testutils import AzureMgmtTestCase
from msrest.serialization import UTC
from azure.eventgrid import EventGridDeserializer, CloudEvent, EventGridEvent
from _mocks import (
    eg_bytes,
    eg_string,
    eg_unicode,
    cloud_bytes,
    cloud_string,
    cloud_unicode,
    cloud_string_with_data_base64
    )

class EventGridDeserializerTests(AzureMgmtTestCase):

    # Cloud Event tests
    def test_eg_consumer_cloud_unicode(self, **kwargs):
        deserialized_events = EventGridDeserializer.deserialize_cloud_events(cloud_unicode)
        for deserialized_event in deserialized_events:
            assert deserialized_event.__class__ == CloudEvent
            assert deserialized_event.data.__class__ == dict

    def test_eg_consumer_cloud_string(self, **kwargs):
        deserialized_events = EventGridDeserializer.deserialize_cloud_events(cloud_string)
        for deserialized_event in deserialized_events:
            assert deserialized_event.__class__ == CloudEvent
            assert deserialized_event.data.__class__ == dict

    def test_eg_consumer_cloud_bytes(self, **kwargs):
        deserialized_events = EventGridDeserializer.deserialize_cloud_events(cloud_bytes)
        for deserialized_event in deserialized_events:
            assert deserialized_event.__class__ == CloudEvent
            assert deserialized_event.data.__class__ == dict

    # EG Event tests

    def test_eg_consumer_eg_storage_unicode(self, **kwargs):
        deserialized_events = EventGridDeserializer.deserialize_eventgrid_events(eg_unicode)
        for deserialized_event in deserialized_events:
            assert deserialized_event.__class__ == EventGridEvent
            assert deserialized_event.data.__class__ == dict


    def test_eg_consumer_eg_storage_string(self, **kwargs):
        deserialized_events = EventGridDeserializer.deserialize_eventgrid_events(eg_string)
        for deserialized_event in deserialized_events:
            assert deserialized_event.__class__ == EventGridEvent
            assert deserialized_event.data.__class__ == dict


    def test_eg_consumer_eg_storage_bytes(self, **kwargs):
        deserialized_events = EventGridDeserializer.deserialize_eventgrid_events(eg_bytes)
        for deserialized_event in deserialized_events:
            assert deserialized_event.__class__ == EventGridEvent
            assert deserialized_event.data.__class__ == dict
