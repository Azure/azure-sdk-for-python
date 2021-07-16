from six import BytesIO
from vcr.filters import (
    remove_headers,
    replace_headers,
    remove_query_parameters,
    replace_query_parameters,
    remove_post_data_parameters,
    replace_post_data_parameters,
    decode_response,
)
from vcr.compat import mock
from vcr.request import Request
import gzip
import json
import zlib


def test_replace_headers():
    # This tests all of:
    #   1. keeping a header
    #   2. removing a header
    #   3. replacing a header
    #   4. replacing a header using a callable
    #   5. removing a header using a callable
    #   6. replacing a header that doesn't exist
    headers = {"one": ["keep"], "two": ["lose"], "three": ["change"], "four": ["shout"], "five": ["whisper"]}
    request = Request("GET", "http://google.com", "", headers)
    replace_headers(
        request,
        [
            ("two", None),
            ("three", "tada"),
            ("four", lambda key, value, request: value.upper()),
            ("five", lambda key, value, request: None),
            ("six", "doesntexist"),
        ],
    )
    assert request.headers == {"one": "keep", "three": "tada", "four": "SHOUT"}


def test_replace_headers_empty():
    headers = {"hello": "goodbye", "secret": "header"}
    request = Request("GET", "http://google.com", "", headers)
    replace_headers(request, [])
    assert request.headers == headers


def test_replace_headers_callable():
    # This goes beyond test_replace_headers() to ensure that the callable
    # receives the expected arguments.
    headers = {"hey": "there"}
    request = Request("GET", "http://google.com", "", headers)
    callme = mock.Mock(return_value="ho")
    replace_headers(request, [("hey", callme)])
    assert request.headers == {"hey": "ho"}
    assert callme.call_args == ((), {"request": request, "key": "hey", "value": "there"})


def test_remove_headers():
    # Test the backward-compatible API wrapper.
    headers = {"hello": ["goodbye"], "secret": ["header"]}
    request = Request("GET", "http://google.com", "", headers)
    remove_headers(request, ["secret"])
    assert request.headers == {"hello": "goodbye"}


def test_replace_query_parameters():
    # This tests all of:
    #   1. keeping a parameter
    #   2. removing a parameter
    #   3. replacing a parameter
    #   4. replacing a parameter using a callable
    #   5. removing a parameter using a callable
    #   6. replacing a parameter that doesn't exist
    uri = "http://g.com/?one=keep&two=lose&three=change&four=shout&five=whisper"
    request = Request("GET", uri, "", {})
    replace_query_parameters(
        request,
        [
            ("two", None),
            ("three", "tada"),
            ("four", lambda key, value, request: value.upper()),
            ("five", lambda key, value, request: None),
            ("six", "doesntexist"),
        ],
    )
    assert request.query == [("four", "SHOUT"), ("one", "keep"), ("three", "tada")]


def test_remove_all_query_parameters():
    uri = "http://g.com/?q=cowboys&w=1"
    request = Request("GET", uri, "", {})
    replace_query_parameters(request, [("w", None), ("q", None)])
    assert request.uri == "http://g.com/"


def test_replace_query_parameters_callable():
    # This goes beyond test_replace_query_parameters() to ensure that the
    # callable receives the expected arguments.
    uri = "http://g.com/?hey=there"
    request = Request("GET", uri, "", {})
    callme = mock.Mock(return_value="ho")
    replace_query_parameters(request, [("hey", callme)])
    assert request.uri == "http://g.com/?hey=ho"
    assert callme.call_args == ((), {"request": request, "key": "hey", "value": "there"})


def test_remove_query_parameters():
    # Test the backward-compatible API wrapper.
    uri = "http://g.com/?q=cowboys&w=1"
    request = Request("GET", uri, "", {})
    remove_query_parameters(request, ["w"])
    assert request.uri == "http://g.com/?q=cowboys"


def test_replace_post_data_parameters():
    # This tests all of:
    #   1. keeping a parameter
    #   2. removing a parameter
    #   3. replacing a parameter
    #   4. replacing a parameter using a callable
    #   5. removing a parameter using a callable
    #   6. replacing a parameter that doesn't exist
    body = b"one=keep&two=lose&three=change&four=shout&five=whisper"
    request = Request("POST", "http://google.com", body, {})
    replace_post_data_parameters(
        request,
        [
            ("two", None),
            ("three", "tada"),
            ("four", lambda key, value, request: value.upper()),
            ("five", lambda key, value, request: None),
            ("six", "doesntexist"),
        ],
    )
    assert request.body == b"one=keep&three=tada&four=SHOUT"


def test_replace_post_data_parameters_empty_body():
    # This test ensures replace_post_data_parameters doesn't throw exception when body is empty.
    body = None
    request = Request("POST", "http://google.com", body, {})
    replace_post_data_parameters(
        request,
        [
            ("two", None),
            ("three", "tada"),
            ("four", lambda key, value, request: value.upper()),
            ("five", lambda key, value, request: None),
            ("six", "doesntexist"),
        ],
    )
    assert request.body is None


def test_remove_post_data_parameters():
    # Test the backward-compatible API wrapper.
    body = b"id=secret&foo=bar"
    request = Request("POST", "http://google.com", body, {})
    remove_post_data_parameters(request, ["id"])
    assert request.body == b"foo=bar"


def test_preserve_multiple_post_data_parameters():
    body = b"id=secret&foo=bar&foo=baz"
    request = Request("POST", "http://google.com", body, {})
    replace_post_data_parameters(request, [("id", None)])
    assert request.body == b"foo=bar&foo=baz"


def test_remove_all_post_data_parameters():
    body = b"id=secret&foo=bar"
    request = Request("POST", "http://google.com", body, {})
    replace_post_data_parameters(request, [("id", None), ("foo", None)])
    assert request.body == b""


def test_replace_json_post_data_parameters():
    # This tests all of:
    #   1. keeping a parameter
    #   2. removing a parameter
    #   3. replacing a parameter
    #   4. replacing a parameter using a callable
    #   5. removing a parameter using a callable
    #   6. replacing a parameter that doesn't exist
    body = b'{"one": "keep", "two": "lose", "three": "change", "four": "shout", "five": "whisper"}'
    request = Request("POST", "http://google.com", body, {})
    request.headers["Content-Type"] = "application/json"
    replace_post_data_parameters(
        request,
        [
            ("two", None),
            ("three", "tada"),
            ("four", lambda key, value, request: value.upper()),
            ("five", lambda key, value, request: None),
            ("six", "doesntexist"),
        ],
    )
    request_data = json.loads(request.body.decode("utf-8"))
    expected_data = json.loads('{"one": "keep", "three": "tada", "four": "SHOUT"}')
    assert request_data == expected_data


def test_remove_json_post_data_parameters():
    # Test the backward-compatible API wrapper.
    body = b'{"id": "secret", "foo": "bar", "baz": "qux"}'
    request = Request("POST", "http://google.com", body, {})
    request.headers["Content-Type"] = "application/json"
    remove_post_data_parameters(request, ["id"])
    request_body_json = json.loads(request.body.decode("utf-8"))
    expected_json = json.loads(b'{"foo": "bar", "baz": "qux"}'.decode("utf-8"))
    assert request_body_json == expected_json


def test_remove_all_json_post_data_parameters():
    body = b'{"id": "secret", "foo": "bar"}'
    request = Request("POST", "http://google.com", body, {})
    request.headers["Content-Type"] = "application/json"
    replace_post_data_parameters(request, [("id", None), ("foo", None)])
    assert request.body == b"{}"


def test_decode_response_uncompressed():
    recorded_response = {
        "status": {"message": "OK", "code": 200},
        "headers": {
            "content-length": ["10806"],
            "date": ["Fri, 24 Oct 2014 18:35:37 GMT"],
            "content-type": ["text/html; charset=utf-8"],
        },
        "body": {"string": b""},
    }
    assert decode_response(recorded_response) == recorded_response


def test_decode_response_deflate():
    body = b"deflate message"
    deflate_response = {
        "body": {"string": zlib.compress(body)},
        "headers": {
            "access-control-allow-credentials": ["true"],
            "access-control-allow-origin": ["*"],
            "connection": ["keep-alive"],
            "content-encoding": ["deflate"],
            "content-length": ["177"],
            "content-type": ["application/json"],
            "date": ["Wed, 02 Dec 2015 19:44:32 GMT"],
            "server": ["nginx"],
        },
        "status": {"code": 200, "message": "OK"},
    }
    decoded_response = decode_response(deflate_response)
    assert decoded_response["body"]["string"] == body
    assert decoded_response["headers"]["content-length"] == [str(len(body))]


def test_decode_response_gzip():
    body = b"gzip message"

    buf = BytesIO()
    f = gzip.GzipFile("a", fileobj=buf, mode="wb")
    f.write(body)
    f.close()

    compressed_body = buf.getvalue()
    buf.close()
    gzip_response = {
        "body": {"string": compressed_body},
        "headers": {
            "access-control-allow-credentials": ["true"],
            "access-control-allow-origin": ["*"],
            "connection": ["keep-alive"],
            "content-encoding": ["gzip"],
            "content-length": ["177"],
            "content-type": ["application/json"],
            "date": ["Wed, 02 Dec 2015 19:44:32 GMT"],
            "server": ["nginx"],
        },
        "status": {"code": 200, "message": "OK"},
    }
    decoded_response = decode_response(gzip_response)
    assert decoded_response["body"]["string"] == body
    assert decoded_response["headers"]["content-length"] == [str(len(body))]
