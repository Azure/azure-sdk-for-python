# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import sys
from rest_client import TestRestClient
import pytest
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.rest import HttpRequest as RestHttpRequest
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport

@pytest.fixture
def old_request(port):
    return PipelineTransportHttpRequest("GET", "http://localhost:{}/streams/basic".format(port))

@pytest.fixture
def old_response(old_request):
    return RequestsTransport().send(old_request)

@pytest.fixture
def new_request(port):
    return RestHttpRequest("GET", "http://localhost:{}/streams/basic".format(port))

@pytest.fixture
def new_response(new_request):
    return RequestsTransport().send(new_request)

def test_response_attr_parity(old_response, new_response):
    for attr in dir(old_response):
        if not attr[0] == "_":
            # if not a private attr, we want partiy
            assert hasattr(new_response, attr)

def test_response_set_attrs(old_response, new_response):
    for attr in dir(old_response):
        if attr[0] == "_":
            continue
        try:
            # if we can set it on the old request, we want to
            # be able to set it on the new
            setattr(old_response, attr, "foo")
        except:
            pass
        else:
            setattr(new_response, attr, "foo")
            assert getattr(old_response, attr) == getattr(new_response, attr) == "foo"

def test_response_block_size(old_response, new_response):
    assert old_response.block_size == new_response.block_size == 4096
    old_response.block_size = 500
    new_response.block_size = 500
    assert old_response.block_size == new_response.block_size == 500

def test_response_body(old_response, new_response):
    assert old_response.body() == new_response.body() == b"Hello, world!"

def test_response_internal_response(old_response, new_response, port):
    assert old_response.internal_response.url == new_response.internal_response.url == "http://localhost:{}/streams/basic".format(port)
    old_response.internal_response = "foo"
    new_response.internal_response = "foo"
    assert old_response.internal_response == new_response.internal_response == "foo"

def test_response_stream_download(old_request, new_request):
    transport = RequestsTransport()
    pipeline = Pipeline(transport)

    old_response = transport.send(old_request, stream=True)
    old_string = b"".join(old_response.stream_download(pipeline=pipeline))

    new_response = transport.send(new_request, stream=True)
    new_string = b"".join(new_response.stream_download(pipeline))
    assert old_string == new_string == b"Hello, world!"

def test_response_request(old_response, new_response, port):
    assert old_response.request.url == new_response.request.url == "http://localhost:{}/streams/basic".format(port)
    old_response.request = "foo"
    new_response.request = "foo"
    assert old_response.request == new_response.request == "foo"

def test_response_status_code(old_response, new_response):
    assert old_response.status_code == new_response.status_code == 200
    old_response.status_code = 202
    new_response.status_code = 202
    assert old_response.status_code == new_response.status_code == 202

def test_response_headers(old_response, new_response):
    assert set(old_response.headers.keys()) == set(new_response.headers.keys()) == set(["Content-Type", "Connection", "Server", "Date"])
    old_response.headers = {"Hello": "world!"}
    new_response.headers = {"Hello": "world!"}
    assert old_response.headers == new_response.headers == {"Hello": "world!"}

def test_response_reason(old_response, new_response):
    assert old_response.reason == new_response.reason == "OK"
    old_response.reason = "Not OK"
    new_response.reason = "Not OK"
    assert old_response.reason == new_response.reason == "Not OK"

def test_response_content_type(old_response, new_response):
    assert old_response.content_type == new_response.content_type == "text/html; charset=utf-8"
    old_response.content_type = "application/json"
    new_response.content_type = "application/json"
    assert old_response.content_type == new_response.content_type == "application/json"

def _create_multiapart_request(http_request_class):
    class ResponsePolicy(object):

        def on_request(self, *args):
            return

        def on_response(self, request, response):
            response.http_response.headers['x-ms-fun'] = 'true'

    req0 = http_request_class("DELETE", "/container0/blob0")
    req1 = http_request_class("DELETE", "/container1/blob1")
    request = http_request_class("POST", "/multipart/request")
    request.set_multipart_mixed(req0, req1, policies=[ResponsePolicy()])
    return request

def _test_parts(response):
    # hack the content type
    parts = response.parts()
    assert len(parts) == 2

    parts0 = parts[0]
    assert parts0.status_code == 202
    assert parts0.headers['x-ms-fun'] == 'true'

    parts1 = parts[1]
    assert parts1.status_code == 404
    assert parts1.headers['x-ms-fun'] == 'true'

@pytest.mark.skipif(sys.version_info < (3, 0), reason="Multipart serialization not supported on 2.7")
def test_response_parts(port):
    old_request = _create_multiapart_request(PipelineTransportHttpRequest)
    new_request = _create_multiapart_request(RestHttpRequest)

    old_response = TestRestClient(port).send_request(old_request, stream=True)
    new_response = TestRestClient(port).send_request(new_request, stream=True)
    _test_parts(old_response)
    _test_parts(new_response)
