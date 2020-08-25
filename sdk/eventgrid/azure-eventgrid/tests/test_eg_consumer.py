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
from azure.eventgrid import EventGridConsumer, CloudEvent, EventGridEvent, StorageBlobCreatedEventData
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

class EventGridConsumerTests(AzureMgmtTestCase):

    # Cloud Event tests
    @pytest.mark.liveTest
    def test_eg_consumer_cloud_storage_dict(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(cloud_storage_dict)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == CloudEvent
        assert deserialized_event.model.data.__class__ == StorageBlobCreatedEventData
        assert event_json.__class__ == dict

    @pytest.mark.liveTest
    def test_eg_consumer_cloud_storage_string(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(cloud_storage_string)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == CloudEvent
        assert deserialized_event.model.data.__class__ == StorageBlobCreatedEventData
        assert event_json.__class__ == dict

    @pytest.mark.liveTest
    def test_eg_consumer_cloud_storage_bytes(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(cloud_storage_bytes)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == CloudEvent
        assert deserialized_event.model.data.__class__ == StorageBlobCreatedEventData
        assert event_json.__class__ == dict
    
    @pytest.mark.liveTest
    def test_eg_consumer_cloud_custom_dict(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(cloud_custom_dict)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == CloudEvent
        assert deserialized_event.model.data is None
        assert event_json.__class__ == dict

    @pytest.mark.liveTest
    def test_eg_consumer_cloud_custom_string(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(cloud_custom_string)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == CloudEvent
        assert deserialized_event.model.data is None
        assert event_json.__class__ == dict

    @pytest.mark.liveTest
    def test_eg_consumer_cloud_custom_bytes(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(cloud_custom_bytes)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == CloudEvent
        assert deserialized_event.model.data is None
        assert event_json.__class__ == dict
    
    # EG Event tests
    @pytest.mark.liveTest
    def test_eg_consumer_eg_storage_dict(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(eg_storage_dict)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == EventGridEvent
        assert deserialized_event.model.data.__class__ == StorageBlobCreatedEventData
        assert event_json.__class__ == dict

    @pytest.mark.liveTest
    def test_eg_consumer_eg_storage_string(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(eg_storage_string)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == EventGridEvent
        assert deserialized_event.model.data.__class__ == StorageBlobCreatedEventData
        assert event_json.__class__ == dict

    @pytest.mark.liveTest
    def test_eg_consumer_eg_storage_bytes(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(eg_storage_bytes)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == EventGridEvent
        assert deserialized_event.model.data.__class__ == StorageBlobCreatedEventData
        assert event_json.__class__ == dict
    
    @pytest.mark.liveTest
    def test_eg_consumer_eg_custom_dict(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(eg_custom_dict)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == EventGridEvent
        assert deserialized_event.model.data is None
        assert event_json.__class__ == dict

    @pytest.mark.liveTest
    def test_eg_consumer_eg_custom_string(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(eg_custom_string)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == EventGridEvent
        assert deserialized_event.model.data is None
        assert event_json.__class__ == dict

    @pytest.mark.liveTest
    def test_eg_consumer_eg_custom_bytes(self, **kwargs):
        client = EventGridConsumer()
        deserialized_event = client.deserialize_event(eg_custom_bytes)
        event_json = deserialized_event.to_json()
        assert deserialized_event.model.__class__ == EventGridEvent
        assert deserialized_event.model.data is None
        assert event_json.__class__ == dict
