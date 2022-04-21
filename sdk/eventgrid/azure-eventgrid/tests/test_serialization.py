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
import base64
import datetime as dt

from devtools_testutils import AzureMgmtTestCase
from msrest.serialization import UTC
from azure.core.messaging import CloudEvent
from azure.eventgrid._generated import models as internal_models
from azure.eventgrid._helpers import _cloud_event_to_generated
from azure.eventgrid import SystemEventNames, EventGridEvent
from _mocks import (
    cloud_storage_dict,
    cloud_storage_string,
    cloud_storage_bytes,
    )

class EventGridSerializationTests(AzureMgmtTestCase):

    def _assert_cloud_event_serialized(self, expected, actual):
        assert expected['source'] == actual['source']
        assert expected['type'] == actual['type']
        assert actual['specversion'] == '1.0'
        assert 'id' in actual
        assert 'time' in actual

    # Cloud Event tests
    def test_cloud_event_serialization_extension_bytes(self, **kwargs):
        data = b"cloudevent"
        cloud_event = CloudEvent(
                source="http://samplesource.dev",
                data=data,
                type="Sample.Cloud.Event",
                extensions={'e1':1, 'e2':2}
                )
        
        cloud_event.subject = "subject" # to test explicit setting of prop
        encoded = base64.b64encode(data).decode('utf-8')
        internal = _cloud_event_to_generated(cloud_event)

        assert internal.additional_properties is not None
        assert 'e1' in internal.additional_properties

        json  = internal.serialize()

        expected = {
            'source':'http://samplesource.dev',
            'data_base64': encoded,
            'type':'Sample.Cloud.Event',
            'reason_code':204,
            'e1':1,
            'e2':2
        }

        self._assert_cloud_event_serialized(expected, json)
        assert expected['data_base64'] == json['data_base64']


    def test_cloud_event_serialization_extension_string(self, **kwargs):
        data = "cloudevent"
        cloud_event = CloudEvent(
                source="http://samplesource.dev",
                data=data,
                type="Sample.Cloud.Event",
                extensions={'e1':1, 'e2':2}
                )
        
        cloud_event.subject = "subject" # to test explicit setting of prop
        internal = _cloud_event_to_generated(cloud_event)

        assert internal.additional_properties is not None
        assert 'e1' in internal.additional_properties

        json  = internal.serialize()

        expected = {
            'source':'http://samplesource.dev',
            'data': data,
            'type':'Sample.Cloud.Event',
            'reason_code':204,
            'e1':1,
            'e2':2
        }

        self._assert_cloud_event_serialized(expected, json)
        if sys.version_info > (3, 5):
            assert expected['data'] == json['data']
        else:
            encoded = base64.b64encode(data).decode('utf-8')
            expected['data_base64'] = encoded
            assert expected['data_base64'] == json['data_base64']
            assert 'data' not in json

    def test_event_grid_event_raises_on_no_data(self):
        with pytest.raises(TypeError):
            eg_event = EventGridEvent(
                    subject="sample",
                    event_type="Sample.EventGrid.Event",
                    data_version="2.0"
                    )

    def test_import_from_sytem_events(self):
        var = SystemEventNames.AcsChatMemberAddedToThreadWithUserEventName 
        assert var == "Microsoft.Communication.ChatMemberAddedToThreadWithUser"
        assert SystemEventNames.KeyVaultKeyNearExpiryEventName == "Microsoft.KeyVault.KeyNearExpiry"
        var = SystemEventNames.ServiceBusActiveMessagesAvailableWithNoListenersEventName
        assert var == "Microsoft.ServiceBus.ActiveMessagesAvailableWithNoListeners"
        var = SystemEventNames.AcsChatThreadParticipantAddedEventName
        assert var == "Microsoft.Communication.ChatThreadParticipantAdded"
        var = SystemEventNames.AcsChatThreadParticipantRemovedEventName
        assert var == "Microsoft.Communication.ChatThreadParticipantRemoved"

    def test_eg_event_repr(self):
        event = EventGridEvent(
                subject="sample2", 
                data="eventgridevent2", 
                event_type="Sample.EventGrid.Event",
                data_version="2.0"
            )
        
        assert "EventGridEvent(subject=sample2" in event.__repr__()

    def test_servicebus_system_events_alias(self):
        val = "Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListeners"
        assert SystemEventNames.ServiceBusDeadletterMessagesAvailableWithNoListenerEventName == SystemEventNames.ServiceBusDeadletterMessagesAvailableWithNoListenersEventName
        assert SystemEventNames.ServiceBusDeadletterMessagesAvailableWithNoListenerEventName == val
        assert SystemEventNames.ServiceBusDeadletterMessagesAvailableWithNoListenersEventName == val
        assert SystemEventNames(val) == SystemEventNames.ServiceBusDeadletterMessagesAvailableWithNoListenerEventName
        assert SystemEventNames(val) == SystemEventNames.ServiceBusDeadletterMessagesAvailableWithNoListenersEventName
        with pytest.raises(ValueError):
            SystemEventNames("Microsoft.ServiceBus.DeadletterMessagesAvailableWithNoListener")
