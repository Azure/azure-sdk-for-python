# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import sys
import pytest
import json
import xml.etree.ElementTree as ET
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.rest import HttpRequest as RestHttpRequest
try:
    import collections.abc as collections
except ImportError:
    import collections

@pytest.fixture
def old_request():
    return PipelineTransportHttpRequest("GET", "/")

@pytest.fixture
def new_request():
    return RestHttpRequest("GET", "/")

def test_request_attr_parity(old_request, new_request):
    for attr in dir(old_request):
        if not attr[0] == "_":
            # if not a private attr, we want parity
            assert hasattr(new_request, attr)

def test_request_set_attrs(old_request, new_request):
    for attr in dir(old_request):
        if attr[0] == "_":
            continue
        try:
            # if we can set it on the old request, we want to
            # be able to set it on the new
            setattr(old_request, attr, "foo")
        except:
            pass
        else:
            setattr(new_request, attr, "foo")
            assert getattr(old_request, attr) == getattr(new_request, attr) == "foo"

def test_request_multipart_mixed_info(old_request, new_request):
    old_request.multipart_mixed_info = "foo"
    new_request.multipart_mixed_info = "foo"
    assert old_request.multipart_mixed_info == new_request.multipart_mixed_info == "foo"

def test_request_files_attr(old_request, new_request):
    assert old_request.files == new_request.files == None
    old_request.files = {"hello": "world"}
    new_request.files = {"hello": "world"}
    assert old_request.files == new_request.files == {"hello": "world"}

def test_request_data_attr(old_request, new_request):
    assert old_request.data == new_request.data == None
    old_request.data = {"hello": "world"}
    new_request.data = {"hello": "world"}
    assert old_request.data == new_request.data == {"hello": "world"}

def test_request_query(old_request, new_request):
    assert old_request.query == new_request.query == {}
    old_request.url = "http://localhost:5000?a=b&c=d"
    new_request.url = "http://localhost:5000?a=b&c=d"
    assert old_request.query == new_request.query == {'a': 'b', 'c': 'd'}

def test_request_query_and_params_kwarg(old_request):
    # should be same behavior if we pass in query params through the params kwarg in the new requests
    old_request.url = "http://localhost:5000?a=b&c=d"
    new_request = RestHttpRequest("GET", "http://localhost:5000", params={'a': 'b', 'c': 'd'})
    assert old_request.query == new_request.query == {'a': 'b', 'c': 'd'}

def test_request_body(old_request, new_request):
    assert old_request.body == new_request.body == None
    old_request.data = {"hello": "world"}
    new_request.data = {"hello": "world"}
    assert (
        old_request.body ==
        new_request.body ==
        new_request.content ==
        {"hello": "world"}
    )
    # files will not override data
    old_request.files = {"foo": "bar"}
    new_request.files = {"foo": "bar"}
    assert (
        old_request.body ==
        new_request.body ==
        new_request.content ==
        {"hello": "world"}
    )

    # nullify data
    old_request.data = None
    new_request.data = None
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        None
    )

def test_format_parameters(old_request, new_request):
    old_request.url = "a/b/c?t=y"
    new_request.url = "a/b/c?t=y"
    assert old_request.url == new_request.url == "a/b/c?t=y"
    old_request.format_parameters({"g": "h"})
    new_request.format_parameters({"g": "h"})

    # ordering can vary, so not sticking on order
    assert old_request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]
    assert new_request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]

def test_request_format_parameters_and_params_kwarg(old_request):
    # calling format_parameters on an old request should be the same
    # behavior as passing in params to new request
    old_request.url = "a/b/c?t=y"
    old_request.format_parameters({"g": "h"})
    new_request = RestHttpRequest(
        "GET", "a/b/c?t=y", params={"g": "h"}
    )
    assert old_request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]
    assert new_request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]

    # additionally, calling format_parameters on a new request
    # should be the same as passing the params to a new request
    assert new_request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]
    assert new_request.url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]

def test_request_streamed_data_body(old_request, new_request):
    assert old_request.files == new_request.files == None
    assert old_request.data == new_request.data == None
    old_request.files = new_request.files = "foo"
    # passing in iterable
    def streaming_body(data):
        yield data  # pragma: nocover
    old_request.set_streamed_data_body(streaming_body("i will be streamed"))
    new_request.set_streamed_data_body(streaming_body("i will be streamed"))

    assert old_request.files == new_request.files == None
    assert isinstance(old_request.data, collections.Iterable)
    assert isinstance(new_request.data, collections.Iterable)
    assert isinstance(old_request.body, collections.Iterable)
    assert isinstance(new_request.body, collections.Iterable)
    assert isinstance(new_request.content, collections.Iterable)
    assert old_request.headers == new_request.headers == {}

def test_request_streamed_data_body_non_iterable(old_request, new_request):
    # should fail before nullifying the files property
    old_request.files = new_request.files = "foo"
    # passing in non iterable
    with pytest.raises(TypeError) as ex:
        old_request.set_streamed_data_body(1)
    assert "A streamable data source must be an open file-like object or iterable" in str(ex.value)
    assert old_request.data is None
    assert old_request.files == "foo"

    with pytest.raises(TypeError) as ex:
        new_request.set_streamed_data_body(1)
    assert "A streamable data source must be an open file-like object or iterable" in str(ex.value)
    assert old_request.data is None
    assert old_request.files == "foo"
    assert old_request.headers == new_request.headers == {}

def test_request_streamed_data_body_and_content_kwarg(old_request):
    # passing stream bodies to set_streamed_data_body
    # and passing a stream body to the content kwarg of the new request should be the same
    def streaming_body(data):
        yield data  # pragma: nocover
    old_request.set_streamed_data_body(streaming_body("stream"))
    new_request = RestHttpRequest("GET", "/", content=streaming_body("stream"))
    assert old_request.files == new_request.files == None
    assert isinstance(old_request.data, collections.Iterable)
    assert isinstance(new_request.data, collections.Iterable)
    assert isinstance(old_request.body, collections.Iterable)
    assert isinstance(new_request.body, collections.Iterable)
    assert isinstance(new_request.content, collections.Iterable)
    assert old_request.headers == new_request.headers == {}

def test_request_text_body(old_request, new_request):
    assert old_request.files == new_request.files == None
    assert old_request.data == new_request.data == None
    old_request.files = new_request.files = "foo"
    old_request.set_text_body("i am text")
    new_request.set_text_body("i am text")

    assert old_request.files == new_request.files == None
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        "i am text"
    )
    assert old_request.headers['Content-Length'] == new_request.headers['Content-Length'] == '9'
    assert not old_request.headers.get("Content-Type")
    assert new_request.headers["Content-Type"] == "text/plain"

def test_request_text_body_and_content_kwarg(old_request):
    old_request.set_text_body("i am text")
    new_request = RestHttpRequest("GET", "/", content="i am text")
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        "i am text"
    )
    assert old_request.headers["Content-Length"] == new_request.headers["Content-Length"] == "9"
    assert old_request.files == new_request.files == None

def test_request_xml_body(old_request, new_request):
    assert old_request.files == new_request.files == None
    assert old_request.data == new_request.data == None
    old_request.files = new_request.files = "foo"
    xml_input = ET.Element("root")
    old_request.set_xml_body(xml_input)
    new_request.set_xml_body(xml_input)

    assert old_request.files == new_request.files == None
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        b"<?xml version='1.0' encoding='utf-8'?>\n<root />"
    )
    assert old_request.headers == new_request.headers == {'Content-Length': '47'}

def test_request_xml_body_and_content_kwarg(old_request):
    old_request.set_text_body("i am text")
    new_request = RestHttpRequest("GET", "/", content="i am text")
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        "i am text"
    )
    assert old_request.headers["Content-Length"] == new_request.headers["Content-Length"] == "9"
    assert old_request.files == new_request.files == None

def test_request_json_body(old_request, new_request):
    assert old_request.files == new_request.files == None
    assert old_request.data == new_request.data == None
    old_request.files = new_request.files = "foo"
    json_input = {"hello": "world"}
    old_request.set_json_body(json_input)
    new_request.set_json_body(json_input)

    assert old_request.files == new_request.files == None
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        json.dumps(json_input)
    )
    assert old_request.headers["Content-Length"] == new_request.headers['Content-Length'] == '18'
    assert not old_request.headers.get("Content-Type")
    assert new_request.headers["Content-Type"] == "application/json"

def test_request_json_body_and_json_kwarg(old_request):
    json_input = {"hello": "world"}
    old_request.set_json_body(json_input)
    new_request = RestHttpRequest("GET", "/", json=json_input)
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        json.dumps(json_input)
    )
    assert old_request.headers["Content-Length"] == new_request.headers['Content-Length'] == '18'
    assert not old_request.headers.get("Content-Type")
    assert new_request.headers["Content-Type"] == "application/json"
    assert old_request.files == new_request.files == None

def test_request_formdata_body_files(old_request, new_request):
    assert old_request.files == new_request.files == None
    assert old_request.data == new_request.data == None
    old_request.data = new_request.data = "foo"
    old_request.files = new_request.files = "bar"

    # without the urlencoded content type, set_formdata_body
    # will set it as files
    old_request.set_formdata_body({"fileName": "hello.jpg"})
    new_request.set_formdata_body({"fileName": "hello.jpg"})

    assert old_request.data == new_request.data == None
    assert (
        old_request.files ==
        new_request.files ==
        new_request.content ==
        {'fileName': (None, 'hello.jpg')}
    )

    # we don't set any multipart headers with boundaries
    # we rely on the transport to boundary calculating
    assert old_request.headers == new_request.headers == {}

def test_request_formdata_body_data(old_request, new_request):
    assert old_request.files == new_request.files == None
    assert old_request.data == new_request.data == None
    old_request.data = new_request.data = "foo"
    old_request.files = new_request.files = "bar"

    # with the urlencoded content type, set_formdata_body
    # will set it as data
    old_request.headers["Content-Type"] = "application/x-www-form-urlencoded"
    new_request.headers["Content-Type"] = "application/x-www-form-urlencoded"
    old_request.set_formdata_body({"fileName": "hello.jpg"})
    new_request.set_formdata_body({"fileName": "hello.jpg"})

    assert old_request.files == new_request.files == None
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        {"fileName": "hello.jpg"}
    )
    # old behavior would pop out the Content-Type header
    # new behavior doesn't do that
    assert old_request.headers == {}
    assert new_request.headers == {'Content-Type': "application/x-www-form-urlencoded"}

def test_request_formdata_body_and_files_kwarg(old_request):
    files = {"fileName": "hello.jpg"}
    old_request.set_formdata_body(files)
    new_request = RestHttpRequest("GET", "/", files=files)
    assert old_request.data == new_request.data == None
    assert old_request.body == new_request.body == None
    assert old_request.headers == new_request.headers == {}
    assert old_request.files == new_request.files == {'fileName': (None, 'hello.jpg')}

def test_request_formdata_body_and_data_kwarg(old_request):
    data = {"fileName": "hello.jpg"}
    # with the urlencoded content type, set_formdata_body
    # will set it as data
    old_request.headers["Content-Type"] = "application/x-www-form-urlencoded"
    old_request.set_formdata_body(data)
    new_request = RestHttpRequest("GET", "/", data=data)
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        {"fileName": "hello.jpg"}
    )
    assert old_request.headers == {}
    assert new_request.headers == {"Content-Type": "application/x-www-form-urlencoded"}
    assert old_request.files == new_request.files == None

def test_request_bytes_body(old_request, new_request):
    assert old_request.files == new_request.files == None
    assert old_request.data == new_request.data == None
    old_request.files = new_request.files = "foo"
    bytes_input = b"hello, world!"
    old_request.set_bytes_body(bytes_input)
    new_request.set_bytes_body(bytes_input)

    assert old_request.files == new_request.files == None
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        bytes_input
    )
    assert old_request.headers == new_request.headers == {'Content-Length': '13'}

def test_request_bytes_body_and_content_kwarg(old_request):
    bytes_input = b"hello, world!"
    old_request.set_bytes_body(bytes_input)
    new_request = RestHttpRequest("GET", "/", content=bytes_input)
    assert (
        old_request.data ==
        new_request.data ==
        old_request.body ==
        new_request.body ==
        new_request.content ==
        bytes_input
    )
    if sys.version_info < (3, 0):
        # in 2.7, b'' is a string, so we're setting content-type headers
        assert old_request.headers["Content-Length"] == new_request.headers['Content-Length'] == '13'
        assert new_request.headers["Content-Type"] == "text/plain"
    else:
        assert old_request.headers == new_request.headers == {'Content-Length': '13'}
    assert old_request.files == new_request.files
