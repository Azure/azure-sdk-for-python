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
from azure.eventgrid import CloudEvent
from azure.eventgrid import models
from azure.eventgrid._generated import models as internal_models
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
                foo="bar",
                extensions={'e1':1, 'e2':2}
                )
        
        cloud_event.subject = "subject" # to test explicit setting of prop
        encoded = base64.b64encode(data).decode('utf-8')
        internal = cloud_event._to_generated()

        assert internal.additional_properties is not None
        assert 'foo' not in internal.additional_properties
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
                foo="bar",
                extensions={'e1':1, 'e2':2}
                )
        
        cloud_event.subject = "subject" # to test explicit setting of prop
        internal = cloud_event._to_generated()

        assert internal.additional_properties is not None
        assert 'foo' not in internal.additional_properties
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
    
    def test_models_exist_in_namespace(self):
        exposed = dir(models)
        generated = dir(internal_models)

        diff = {m for m in list(set(generated) - set(exposed)) if not m.startswith('_')}
        assert diff == {'CloudEvent', 'EventGridEvent'}
