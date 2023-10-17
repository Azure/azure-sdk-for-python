# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import json
import base64
from azure.eventgrid._operations._patch import _to_http_request
from azure.eventgrid._model_base import AzureJSONEncoder
from azure.eventgrid.models import *
from azure.core.messaging import CloudEvent

class MyTestClass(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    
class TestEGClientExceptions():
    
    def test_binary_request_format(self):
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b'this is binary data',
        )

        request = _to_http_request("https://eg-topic.westus2-1.eventgrid.azure.net/api/events", event=event)

        assert request.data == json.dumps(base64.b64encode(event.data), cls=AzureJSONEncoder, exclude_readonly=True)
        assert request.headers.get("ce-source") == "source"
        assert request.headers.get("ce-subject") == "MySubject"
        assert request.headers.get("ce-type") == "Contoso.Items.ItemReceived"

    
    def test_binary_request_format_with_extensions(self):
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=b'this is binary data',
            extensions={"extension1": "value1", "extension2": "value2"}
        )

        request = _to_http_request("https://eg-topic.westus2-1.eventgrid.azure.net/api/events", event=event)

        assert request.data == json.dumps(base64.b64encode(event.data), cls=AzureJSONEncoder, exclude_readonly=True)
        assert request.headers.get("ce-source") == "source"
        assert request.headers.get("ce-subject") == "MySubject"
        assert request.headers.get("ce-type") == "Contoso.Items.ItemReceived"
        assert request.headers.get("ce-extension").get("extension1") == "value1"

    def test_binary_request_format_with_extensions_and_datacontenttype(self):
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data='this is my data',
            datacontenttype="application/json",
            extensions={"extension1": "value1", "extension2": "value2"}
        )

        request = _to_http_request("https://eg-topic.westus2-1.eventgrid.azure.net/api/events", event=event)

        assert request.data == json.dumps(base64.b64encode(event.data), cls=AzureJSONEncoder, exclude_readonly=True)
        assert request.headers.get("ce-source") == "source"
        assert request.headers.get("ce-subject") == "MySubject"
        assert request.headers.get("ce-type") == "Contoso.Items.ItemReceived"
        assert request.headers.get("ce-extension").get("extension1") == "value1"

    def test_complex_binary_request_format(self):
        test_class = MyTestClass("test")
        event = CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="source",
            subject="MySubject",
            data=test_class,
            datacontenttype="application/json",
            extensions={"extension1": "value1", "extension2": "value2"}
        )

        request = _to_http_request("https://eg-topic.westus2-1.eventgrid.azure.net/api/events", event=event)

        assert request.data == json.dumps(base64.b64encode(event.data), cls=AzureJSONEncoder, exclude_readonly=True)
        assert request.headers.get("ce-source") == "source"
        assert request.headers.get("ce-subject") == "MySubject"
        assert request.headers.get("ce-type") == "Contoso.Items.ItemReceived"
        assert request.headers.get("ce-extension").get("extension1") == "value1"
        