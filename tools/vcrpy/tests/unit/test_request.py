import pytest

from vcr.request import Request, HeadersDict


@pytest.mark.parametrize(
    "method, uri, expected_str",
    [
        ("GET", "http://www.google.com/", "<Request (GET) http://www.google.com/>"),
        ("OPTIONS", "*", "<Request (OPTIONS) *>"),
        ("CONNECT", "host.some.where:1234", "<Request (CONNECT) host.some.where:1234>"),
    ],
)
def test_str(method, uri, expected_str):
    assert str(Request(method, uri, "", {})) == expected_str


def test_headers():
    headers = {"X-Header1": ["h1"], "X-Header2": "h2"}
    req = Request("GET", "http://go.com/", "", headers)
    assert req.headers == {"X-Header1": "h1", "X-Header2": "h2"}
    req.headers["X-Header1"] = "h11"
    assert req.headers == {"X-Header1": "h11", "X-Header2": "h2"}


def test_add_header_deprecated():
    req = Request("GET", "http://go.com/", "", {})
    pytest.deprecated_call(req.add_header, "foo", "bar")
    assert req.headers == {"foo": "bar"}


@pytest.mark.parametrize(
    "uri, expected_port",
    [
        ("http://go.com/", 80),
        ("http://go.com:80/", 80),
        ("http://go.com:3000/", 3000),
        ("https://go.com/", 443),
        ("https://go.com:443/", 443),
        ("https://go.com:3000/", 3000),
        ("*", None),
    ],
)
def test_port(uri, expected_port):
    req = Request("GET", uri, "", {})
    assert req.port == expected_port


@pytest.mark.parametrize(
    "method, uri",
    [
        ("GET", "http://go.com/"),
        ("GET", "http://go.com:80/"),
        ("CONNECT", "localhost:1234"),
        ("OPTIONS", "*"),
    ],
)
def test_uri(method, uri):
    assert Request(method, uri, "", {}).uri == uri


def test_HeadersDict():

    # Simple test of CaseInsensitiveDict
    h = HeadersDict()
    assert h == {}
    h["Content-Type"] = "application/json"
    assert h == {"Content-Type": "application/json"}
    assert h["content-type"] == "application/json"
    assert h["CONTENT-TYPE"] == "application/json"

    # Test feature of HeadersDict: devolve list to first element
    h = HeadersDict()
    assert h == {}
    h["x"] = ["foo", "bar"]
    assert h == {"x": "foo"}

    # Test feature of HeadersDict: preserve original key case
    h = HeadersDict()
    assert h == {}
    h["Content-Type"] = "application/json"
    assert h == {"Content-Type": "application/json"}
    h["content-type"] = "text/plain"
    assert h == {"Content-Type": "text/plain"}
    h["CONtent-tyPE"] = "whoa"
    assert h == {"Content-Type": "whoa"}
