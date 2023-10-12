# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import base64
from azure.eventgrid._operations._patch import _to_http_request
from azure.eventgrid._serialization import Deserializer
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent


class TestEGClientExceptions():
    
    def test_binary_request_format(self):
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b'this is binary data',
        )

        request = _to_http_request("https://eg-topic.westus2-1.eventgrid.azure.net/api/events", event=event)

        deserialize = Deserializer()
        assert deserialize('str', request.data) == base64.b64encode(b'this is binary data')
        assert request.headers.get("ce-source") == "source"

        

        