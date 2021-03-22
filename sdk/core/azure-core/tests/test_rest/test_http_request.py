# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from typing import Generator, AsyncGenerator
from azure.core.rest import HttpRequest

def test_rest_request_repr():
    request = HttpRequest("GET", "http://example.org")
    assert repr(request) == "<HttpRequest [GET], url: 'http://example.org'>"

def test_rest_no_content():
    request = HttpRequest("GET", "http://example.org")
    assert "Content-Length" not in request.headers

def test_rest_content_length_header():
    request = HttpRequest("POST", "http://example.org", content=b"test 123")
    assert request.headers["Content-Length"] == "8"


def test_rest_iterable_content():
    class Content:
        def __iter__(self):
            yield b"test 123"  # pragma: nocover

    request = HttpRequest("POST", "http://example.org", content=Content())
    assert request.headers == {"Transfer-Encoding": "chunked"}


def test_rest_generator_with_transfer_encoding_header():
    def content():
        yield b"test 123"  # pragma: nocover

    request = HttpRequest("POST", "http://example.org", content=content())
    assert request.headers == {"Transfer-Encoding": "chunked"}


def test_rest_generator_with_content_length_header():
    def content():
        yield b"test 123"  # pragma: nocover

    headers = {"Content-Length": "8"}
    request = HttpRequest(
        "POST", "http://example.org", content=content(), headers=headers
    )
    assert request.headers == {"Content-Length": "8"}


def test_rest_url_encoded_data():
    request = HttpRequest("POST", "http://example.org", data={"test": "123"})

    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert request.content == {'test': '123'}  # httpx makes this just b'test=123'. set_formdata_body is still keeping it as a dict


def test_rest_json_encoded_data():
    request = HttpRequest("POST", "http://example.org", json={"test": 123})

    assert request.headers["Content-Type"] == "application/json"
    assert request.content == '{"test": 123}'


def test_rest_headers():
    request = HttpRequest("POST", "http://example.org", json={"test": 123})

    assert request.headers == {
        "Content-Type": "application/json",
        "Content-Length": "13",
    }


def test_rest_transfer_encoding_header():
    async def streaming_body(data):
        yield data  # pragma: nocover

    data = streaming_body(b"test 123")

    request = HttpRequest("POST", "http://example.org", data=data)
    assert "Content-Length" not in request.headers
    assert request.headers["Transfer-Encoding"] == "chunked"


def test_rest_ignore_transfer_encoding_header_if_content_length_exists():
    """
    `Transfer-Encoding` should be ignored if `Content-Length` has been set explicitly.
    See https://github.com/encode/httpx/issues/1168
    """

    def streaming_body(data):
        yield data  # pragma: nocover

    data = streaming_body(b"abcd")

    headers = {"Content-Length": "4"}
    request = HttpRequest("POST", "http://example.org", data=data, headers=headers)
    assert "Transfer-Encoding" not in request.headers
    assert request.headers["Content-Length"] == "4"

def test_rest_override_accept_encoding_header():
    headers = {"Accept-Encoding": "identity"}

    request = HttpRequest("GET", "http://example.org", headers=headers)
    assert request.headers["Accept-Encoding"] == "identity"


def test_rest_override_content_length_header():
    async def streaming_body(data):
        yield data  # pragma: nocover

    data = streaming_body(b"test 123")
    headers = {"Content-Length": "0"}

    request = HttpRequest("POST", "http://example.org", data=data, headers=headers)
    assert request.headers["Content-Length"] == "0"

"""Test request body"""
def test_rest_empty_content():
    request = HttpRequest("GET", "http://example.org")
    assert request.content == None

def test_rest_bytes_content():
    request = HttpRequest("PUT", "http://example.org", content=b"Hello, world!")
    assert request.headers == {"Content-Length": "13"}
    assert request.content == b"Hello, world!"

    # Support 'data' for compat with requests.
    request = HttpRequest("PUT", "http://example.org", data=b"Hello, world!")

    assert request.headers == {"Content-Length": "13"}
    assert request.content == b"Hello, world!"

    # content length should not be set for GET requests

    request = HttpRequest("GET", "http://example.org", data=b"Hello, world!")

    assert request.headers == {}
    assert request.content == b"Hello, world!"

def test_rest_iterator_content():
    # NOTE: in httpx, content reads out the actual value. Don't do that (yet) in azure rest
    def hello_world():
        yield b"Hello, "
        yield b"world!"

    request = HttpRequest("POST", url="http://example.org", content=hello_world())

    assert request.headers == {"Transfer-Encoding": "chunked"}
    assert isinstance(request.content, Generator)

    # Support 'data' for compat with requests.
    request = HttpRequest("POST", url="http://example.org", data=hello_world())

    assert request.headers == {"Transfer-Encoding": "chunked"}
    assert isinstance(request.content, Generator)

    # transfer encoding should not be set for GET requests
    request = HttpRequest("GET", url="http://example.org", data=hello_world())

    assert request.headers == {}
    assert isinstance(request.content, Generator)


@pytest.mark.asyncio
async def test_rest_aiterator_content():
    async def hello_world():
        yield b"Hello, "
        yield b"world!"

    request = HttpRequest("POST", url="http://example.org", content=hello_world())

    assert request.headers == {"Transfer-Encoding": "chunked"}
    assert isinstance(request.content, AsyncGenerator)

    # Support 'data' for compat with requests.
    request = HttpRequest("POST", url="http://example.org", data=hello_world())

    assert request.headers == {"Transfer-Encoding": "chunked"}
    assert isinstance(request.content, AsyncGenerator)

    # transfer encoding should not be set for GET requests
    request = HttpRequest("GET", url="http://example.org", data=hello_world())

    assert request.headers == {}
    assert isinstance(request.content, AsyncGenerator)


def test_rest_json_content():
    request = HttpRequest("POST", url="http://example.org", json={"Hello": "world!"})

    assert request.headers == {
        "Content-Length": "19",
        "Content-Type": "application/json",
    }
    assert request.content == '{"Hello": "world!"}'

def test_rest_urlencoded_content():
    # NOTE: not adding content length setting and content testing bc we're not adding content length in the rest code
    # that's dealt with later in the pipeline.
    request = HttpRequest("POST", url="http://example.org", data={"Hello": "world!"})
    assert request.headers == {
        "Content-Type": "application/x-www-form-urlencoded",
    }

# NOTE: commenting out multipart files content setting tests for now. We currently leave the content length / type setting for the pipeline
# to do on the internal request.

# def test_rest_multipart_files_content():
#     files = {"file": io.BytesIO(b"<file content>")}
#     request = HttpRequest("POST", url="http://example.org", files=files)

#     assert request.headers == {
#         "Content-Length": "138",
#         "Content-Type": "multipart/form-data; boundary=+++",
#     }
#     assert request.content == b"".join(
#         [
#             b"--+++\r\n",
#             b'Content-Disposition: form-data; name="file"; filename="upload"\r\n',
#             b"Content-Type: application/octet-stream\r\n",
#             b"\r\n",
#             b"<file content>\r\n",
#             b"--+++--\r\n",
#         ]
#     )

# def test_rest_multipart_data_and_files_content():
#     data = {"message": "Hello, world!"}
#     files = {"file": io.BytesIO(b"<file content>")}
#     request = HttpRequest("POST", url="http://example.org", data=data, files=files)

#     assert request.headers == {
#         "Content-Length": "210",
#         "Content-Type": "multipart/form-data; boundary=+++",
#     }
#     assert request.content == b"".join(
#         [
#             b"--+++\r\n",
#             b'Content-Disposition: form-data; name="message"\r\n',
#             b"\r\n",
#             b"Hello, world!\r\n",
#             b"--+++\r\n",
#             b'Content-Disposition: form-data; name="file"; filename="upload"\r\n',
#             b"Content-Type: application/octet-stream\r\n",
#             b"\r\n",
#             b"<file content>\r\n",
#             b"--+++--\r\n",
#         ]
#     )

def test_rest_empty_request():
    request = HttpRequest("POST", url="http://example.org", data={}, files={})

    assert request.headers == {}
    assert request.content == {} # in core, we don't convert urlencoded dict to bytes representation in content

# NOTE: For files, we don't allow list of tuples yet, just dict. Will uncomment when we add this capability
# def test_rest_multipart_multiple_files_single_input_content():
#     files = [
#         ("file", io.BytesIO(b"<file content 1>")),
#         ("file", io.BytesIO(b"<file content 2>")),
#     ]
#     request = HttpRequest("POST", url="http://example.org", files=files)
#     assert request.headers == {
#         "Content-Length": "271",
#         "Content-Type": "multipart/form-data; boundary=+++",
#     }
#     assert request.content == b"".join(
#         [
#             b"--+++\r\n",
#             b'Content-Disposition: form-data; name="file"; filename="upload"\r\n',
#             b"Content-Type: application/octet-stream\r\n",
#             b"\r\n",
#             b"<file content 1>\r\n",
#             b"--+++\r\n",
#             b'Content-Disposition: form-data; name="file"; filename="upload"\r\n',
#             b"Content-Type: application/octet-stream\r\n",
#             b"\r\n",
#             b"<file content 2>\r\n",
#             b"--+++--\r\n",
#         ]
#     )
