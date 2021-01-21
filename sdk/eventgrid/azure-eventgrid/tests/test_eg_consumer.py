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
from azure.eventgrid.systemevents import StorageBlobCreatedEventData
from _mocks import (
    cloud_storage_dict,
    cloud_storage_string,
    cloud_storage_bytes,
    cloud_custom_dict,
    cloud_custom_string,
    cloud_custom_bytes,
    eg_custom_dict,
    eg_custom_string,
    eg_custom_bytes,
    eg_storage_dict,
    eg_storage_string,
    eg_storage_bytes
    )

class EventGridDeserializerTests(AzureMgmtTestCase):

    # Cloud Event tests
    def test_eg_consumer_cloud_storage_dict(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_cloud_events(cloud_storage_dict)
        assert deserialized_event.__class__ == CloudEvent
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data.__class__ == StorageBlobCreatedEventData

    def test_eg_consumer_cloud_storage_string(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_cloud_events(cloud_storage_string)
        assert deserialized_event.__class__ == CloudEvent
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data.__class__ == StorageBlobCreatedEventData

    def test_eg_consumer_cloud_storage_bytes(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_cloud_events(cloud_storage_bytes)
        assert deserialized_event.__class__ == CloudEvent
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data.__class__ == StorageBlobCreatedEventData
    

    def test_eg_consumer_cloud_custom_dict(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_cloud_events(cloud_custom_dict)
        assert deserialized_event.__class__ == CloudEvent
        assert deserialized_event.data == {"team": "event grid squad"}
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data is None


    def test_eg_consumer_cloud_custom_string(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_cloud_events(cloud_custom_string)
        assert deserialized_event.__class__ == CloudEvent
        assert deserialized_event.data == {"team": "event grid squad"}
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data is None


    def test_eg_consumer_cloud_custom_bytes(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_cloud_events(cloud_custom_bytes)
        assert deserialized_event.__class__ == CloudEvent
        assert deserialized_event.data == {"team": "event grid squad"}
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data is None
    
    # EG Event tests

    def test_eg_consumer_eg_storage_dict(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_eventgrid_events(eg_storage_dict)
        assert deserialized_event.__class__ == EventGridEvent
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data.__class__ == StorageBlobCreatedEventData


    def test_eg_consumer_eg_storage_string(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_eventgrid_events(eg_storage_string)
        assert deserialized_event.__class__ == EventGridEvent
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data.__class__ == StorageBlobCreatedEventData


    def test_eg_consumer_eg_storage_bytes(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_eventgrid_events(eg_storage_bytes)
        assert deserialized_event.__class__ == EventGridEvent
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data.__class__ == StorageBlobCreatedEventData
    

    def test_eg_consumer_eg_custom_dict(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_eventgrid_events(eg_custom_dict)
        assert deserialized_event.__class__ == EventGridEvent
        assert deserialized_event.data == {"team": "event grid squad"}
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data is None


    def test_eg_consumer_eg_custom_string(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_eventgrid_events(eg_custom_string)
        assert deserialized_event.__class__ == EventGridEvent
        assert deserialized_event.data == {"team": "event grid squad"}
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data is None


    def test_eg_consumer_eg_custom_bytes(self, **kwargs):
        client = EventGridDeserializer()
        deserialized_event = client.deserialize_eventgrid_events(eg_custom_bytes)
        assert deserialized_event.__class__ == EventGridEvent
        assert deserialized_event.data == {"team": "event grid squad"}
        assert deserialized_event.data.__class__ == dict
        assert deserialized_event.system_event_data is None
