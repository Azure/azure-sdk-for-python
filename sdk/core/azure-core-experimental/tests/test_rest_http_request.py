# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import pytest
from itertools import product

from azure.core.rest import HttpRequest as RestHttpRequest

from rest_client import MockRestClient
from utils import SYNC_TRANSPORTS, HTTP_REQUESTS, NamedIo, create_http_request


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_complicated_json(port, transport, requesttype):
    # thanks to Sean Kane for this test!
    input = {
        "EmptyByte": "",
        "EmptyUnicode": "",
        "SpacesOnlyByte": "   ",
        "SpacesOnlyUnicode": "   ",
        "SpacesBeforeByte": "   Text",
        "SpacesBeforeUnicode": "   Text",
        "SpacesAfterByte": "Text   ",
        "SpacesAfterUnicode": "Text   ",
        "SpacesBeforeAndAfterByte": "   Text   ",
        "SpacesBeforeAndAfterUnicode": "   Text   ",
        "啊齄丂狛": "ꀕ",
        "RowKey": "test2",
        "啊齄丂狛狜": "hello",
        "singlequote": "a''''b",
        "doublequote": 'a""""b',
        "None": None,
    }
    request = create_http_request(requesttype, "POST", "/basic/complicated-json", json=input)
    client = MockRestClient(port, transport=transport())
    r = client.send_request(request)
    r.raise_for_status()


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_multipart_tuple_input_multiple_same_name(port, transport, requesttype):
    client = MockRestClient(port, transport=transport())
    request = create_http_request(
        requesttype,
        "POST",
        "/multipart/tuple-input-multiple-same-name",
        files=[
            ("file", ("firstFileName", NamedIo("firstFile"), "image/pdf")),
            ("file", ("secondFileName", NamedIo("secondFile"), "image/png")),
        ],
    )
    client.send_request(request).raise_for_status()


# Not compatible with legacy HttpRequest object
@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_multipart_tuple_input_multiple_same_name_with_tuple_file_value(port, transport):
    client = MockRestClient(port, transport=transport())
    request = create_http_request(
        RestHttpRequest,
        "POST",
        "/multipart/tuple-input-multiple-same-name-with-tuple-file-value",
        files=[("images", ("foo.png", NamedIo("notMyName.pdf"), "image/png")), ("images", NamedIo("foo.png"))],
    )
    client.send_request(request).raise_for_status()


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_data_and_file_input_same_name(port, transport, requesttype):
    client = MockRestClient(port, transport=transport())
    request = create_http_request(
        requesttype,
        "POST",
        "/multipart/data-and-file-input-same-name",
        data={"message": "Hello, world!"},
        files=[
            ("file", ("firstFileName", NamedIo("firstFile"), "image/pdf")),
            ("file", ("secondFileName", NamedIo("secondFile"), "image/png")),
        ],
    )
    client.send_request(request).raise_for_status()
