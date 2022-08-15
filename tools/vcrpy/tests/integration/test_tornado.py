# -*- coding: utf-8 -*-
"""Test requests' interaction with vcr"""

import json

import pytest
import vcr
from vcr.errors import CannotOverwriteExistingCassetteException

from assertions import assert_cassette_empty, assert_is_json

tornado = pytest.importorskip("tornado")
http = pytest.importorskip("tornado.httpclient")

# whether the current version of Tornado supports the raise_error argument for
# fetch().
supports_raise_error = tornado.version_info >= (4,)


@pytest.fixture(params=["simple", "curl", "default"])
def get_client(request):
    if request.param == "simple":
        from tornado import simple_httpclient as simple

        return lambda: simple.SimpleAsyncHTTPClient()
    elif request.param == "curl":
        curl = pytest.importorskip("tornado.curl_httpclient")
        return lambda: curl.CurlAsyncHTTPClient()
    else:
        return lambda: http.AsyncHTTPClient()


def get(client, url, **kwargs):
    fetch_kwargs = {}
    if supports_raise_error:
        fetch_kwargs["raise_error"] = kwargs.pop("raise_error", True)

    return client.fetch(http.HTTPRequest(url, method="GET", **kwargs), **fetch_kwargs)


def post(client, url, data=None, **kwargs):
    if data:
        kwargs["body"] = json.dumps(data)
    return client.fetch(http.HTTPRequest(url, method="POST", **kwargs))


@pytest.fixture(params=["https", "http"])
def scheme(request):
    """Fixture that returns both http and https."""
    return request.param


@pytest.mark.gen_test
def test_status_code(get_client, scheme, tmpdir):
    """Ensure that we can read the status code"""
    url = scheme + "://httpbin.org/"
    with vcr.use_cassette(str(tmpdir.join("atts.yaml"))):
        status_code = (yield get(get_client(), url)).code

    with vcr.use_cassette(str(tmpdir.join("atts.yaml"))) as cass:
        assert status_code == (yield get(get_client(), url)).code
        assert 1 == cass.play_count


@pytest.mark.gen_test
def test_headers(get_client, scheme, tmpdir):
    """Ensure that we can read the headers back"""
    url = scheme + "://httpbin.org/"
    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        headers = (yield get(get_client(), url)).headers

    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))) as cass:
        assert headers == (yield get(get_client(), url)).headers
        assert 1 == cass.play_count


@pytest.mark.gen_test
def test_body(get_client, tmpdir, scheme):
    """Ensure the responses are all identical enough"""

    url = scheme + "://httpbin.org/bytes/1024"
    with vcr.use_cassette(str(tmpdir.join("body.yaml"))):
        content = (yield get(get_client(), url)).body

    with vcr.use_cassette(str(tmpdir.join("body.yaml"))) as cass:
        assert content == (yield get(get_client(), url)).body
        assert 1 == cass.play_count


@pytest.mark.gen_test
def test_effective_url(get_client, scheme, tmpdir):
    """Ensure that the effective_url is captured"""
    url = scheme + "://httpbin.org/redirect-to?url=/html"
    with vcr.use_cassette(str(tmpdir.join("url.yaml"))):
        effective_url = (yield get(get_client(), url)).effective_url
        assert effective_url == scheme + "://httpbin.org/html"

    with vcr.use_cassette(str(tmpdir.join("url.yaml"))) as cass:
        assert effective_url == (yield get(get_client(), url)).effective_url
        assert 1 == cass.play_count


@pytest.mark.gen_test
def test_auth(get_client, tmpdir, scheme):
    """Ensure that we can handle basic auth"""
    auth = ("user", "passwd")
    url = scheme + "://httpbin.org/basic-auth/user/passwd"
    with vcr.use_cassette(str(tmpdir.join("auth.yaml"))):
        one = yield get(get_client(), url, auth_username=auth[0], auth_password=auth[1])

    with vcr.use_cassette(str(tmpdir.join("auth.yaml"))) as cass:
        two = yield get(get_client(), url, auth_username=auth[0], auth_password=auth[1])
        assert one.body == two.body
        assert one.code == two.code
        assert 1 == cass.play_count


@pytest.mark.gen_test
def test_auth_failed(get_client, tmpdir, scheme):
    """Ensure that we can save failed auth statuses"""
    auth = ("user", "wrongwrongwrong")
    url = scheme + "://httpbin.org/basic-auth/user/passwd"
    with vcr.use_cassette(str(tmpdir.join("auth-failed.yaml"))) as cass:
        # Ensure that this is empty to begin with
        assert_cassette_empty(cass)
        with pytest.raises(http.HTTPError) as exc_info:
            yield get(get_client(), url, auth_username=auth[0], auth_password=auth[1])
        one = exc_info.value.response
        assert exc_info.value.code == 401

    with vcr.use_cassette(str(tmpdir.join("auth-failed.yaml"))) as cass:
        with pytest.raises(http.HTTPError) as exc_info:
            two = yield get(get_client(), url, auth_username=auth[0], auth_password=auth[1])
        two = exc_info.value.response
        assert exc_info.value.code == 401
        assert one.body == two.body
        assert one.code == two.code == 401
        assert 1 == cass.play_count


@pytest.mark.gen_test
def test_post(get_client, tmpdir, scheme):
    """Ensure that we can post and cache the results"""
    data = {"key1": "value1", "key2": "value2"}
    url = scheme + "://httpbin.org/post"
    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        req1 = (yield post(get_client(), url, data)).body

    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))) as cass:
        req2 = (yield post(get_client(), url, data)).body

    assert req1 == req2
    assert 1 == cass.play_count


@pytest.mark.gen_test
def test_redirects(get_client, tmpdir, scheme):
    """Ensure that we can handle redirects"""
    url = scheme + "://httpbin.org/redirect-to?url=bytes/1024"
    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        content = (yield get(get_client(), url)).body

    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))) as cass:
        assert content == (yield get(get_client(), url)).body
        assert cass.play_count == 1


@pytest.mark.gen_test
def test_cross_scheme(get_client, tmpdir, scheme):
    """Ensure that requests between schemes are treated separately"""
    # First fetch a url under http, and then again under https and then
    # ensure that we haven't served anything out of cache, and we have two
    # requests / response pairs in the cassette
    with vcr.use_cassette(str(tmpdir.join("cross_scheme.yaml"))) as cass:
        yield get(get_client(), "https://httpbin.org/")
        yield get(get_client(), "http://httpbin.org/")
        assert cass.play_count == 0
        assert len(cass) == 2

    # Then repeat the same requests and ensure both were replayed.
    with vcr.use_cassette(str(tmpdir.join("cross_scheme.yaml"))) as cass:
        yield get(get_client(), "https://httpbin.org/")
        yield get(get_client(), "http://httpbin.org/")
        assert cass.play_count == 2


@pytest.mark.gen_test
def test_gzip(get_client, tmpdir, scheme):
    """
    Ensure that httpclient is able to automatically decompress the response
    body
    """
    url = scheme + "://httpbin.org/gzip"

    # use_gzip was renamed to decompress_response in 4.0
    kwargs = {}
    if tornado.version_info < (4,):
        kwargs["use_gzip"] = True
    else:
        kwargs["decompress_response"] = True

    with vcr.use_cassette(str(tmpdir.join("gzip.yaml"))):
        response = yield get(get_client(), url, **kwargs)
        assert_is_json(response.body)

    with vcr.use_cassette(str(tmpdir.join("gzip.yaml"))) as cass:
        response = yield get(get_client(), url, **kwargs)
        assert_is_json(response.body)
        assert 1 == cass.play_count


@pytest.mark.gen_test
def test_https_with_cert_validation_disabled(get_client, tmpdir):
    cass_path = str(tmpdir.join("cert_validation_disabled.yaml"))

    with vcr.use_cassette(cass_path):
        yield get(get_client(), "https://httpbin.org", validate_cert=False)

    with vcr.use_cassette(cass_path) as cass:
        yield get(get_client(), "https://httpbin.org", validate_cert=False)
        assert 1 == cass.play_count


@pytest.mark.gen_test
def test_unsupported_features_raises_in_future(get_client, tmpdir):
    """Ensure that the exception for an AsyncHTTPClient feature not being
    supported is raised inside the future."""

    def callback(chunk):
        assert False, "Did not expect to be called."

    with vcr.use_cassette(str(tmpdir.join("invalid.yaml"))):
        future = get(get_client(), "http://httpbin.org", streaming_callback=callback)

    with pytest.raises(Exception) as excinfo:
        yield future

    assert "not yet supported by VCR" in str(excinfo)


@pytest.mark.skipif(not supports_raise_error, reason="raise_error unavailable in tornado <= 3")
@pytest.mark.gen_test
def test_unsupported_features_raise_error_disabled(get_client, tmpdir):
    """Ensure that the exception for an AsyncHTTPClient feature not being
    supported is not raised if raise_error=False."""

    def callback(chunk):
        assert False, "Did not expect to be called."

    with vcr.use_cassette(str(tmpdir.join("invalid.yaml"))):
        response = yield get(
            get_client(), "http://httpbin.org", streaming_callback=callback, raise_error=False
        )

    assert "not yet supported by VCR" in str(response.error)


@pytest.mark.gen_test
def test_cannot_overwrite_cassette_raises_in_future(get_client, tmpdir):
    """Ensure that CannotOverwriteExistingCassetteException is raised inside
    the future."""

    with vcr.use_cassette(str(tmpdir.join("overwrite.yaml"))):
        yield get(get_client(), "http://httpbin.org/get")

    with vcr.use_cassette(str(tmpdir.join("overwrite.yaml"))):
        future = get(get_client(), "http://httpbin.org/headers")

    with pytest.raises(CannotOverwriteExistingCassetteException):
        yield future


@pytest.mark.skipif(not supports_raise_error, reason="raise_error unavailable in tornado <= 3")
@pytest.mark.gen_test
def test_cannot_overwrite_cassette_raise_error_disabled(get_client, tmpdir):
    """Ensure that CannotOverwriteExistingCassetteException is not raised if
    raise_error=False in the fetch() call."""

    with vcr.use_cassette(str(tmpdir.join("overwrite.yaml"))):
        yield get(get_client(), "http://httpbin.org/get", raise_error=False)

    with vcr.use_cassette(str(tmpdir.join("overwrite.yaml"))):
        response = yield get(get_client(), "http://httpbin.org/headers", raise_error=False)

    assert isinstance(response.error, CannotOverwriteExistingCassetteException)


@pytest.mark.gen_test
@vcr.use_cassette(path_transformer=vcr.default_vcr.ensure_suffix(".yaml"))
def test_tornado_with_decorator_use_cassette(get_client):
    response = yield get_client().fetch(http.HTTPRequest("http://www.google.com/", method="GET"))
    assert response.body.decode("utf-8") == "not actually google"


@pytest.mark.gen_test
@vcr.use_cassette(path_transformer=vcr.default_vcr.ensure_suffix(".yaml"))
def test_tornado_exception_can_be_caught(get_client):
    try:
        yield get(get_client(), "http://httpbin.org/status/500")
    except http.HTTPError as e:
        assert e.code == 500

    try:
        yield get(get_client(), "http://httpbin.org/status/404")
    except http.HTTPError as e:
        assert e.code == 404


@pytest.mark.gen_test
def test_existing_references_get_patched(tmpdir):
    from tornado.httpclient import AsyncHTTPClient

    with vcr.use_cassette(str(tmpdir.join("data.yaml"))):
        client = AsyncHTTPClient()
        yield get(client, "http://httpbin.org/get")

    with vcr.use_cassette(str(tmpdir.join("data.yaml"))) as cass:
        yield get(client, "http://httpbin.org/get")
        assert cass.play_count == 1


@pytest.mark.gen_test
def test_existing_instances_get_patched(get_client, tmpdir):
    """Ensure that existing instances of AsyncHTTPClient get patched upon
    entering VCR context."""

    client = get_client()

    with vcr.use_cassette(str(tmpdir.join("data.yaml"))):
        yield get(client, "http://httpbin.org/get")

    with vcr.use_cassette(str(tmpdir.join("data.yaml"))) as cass:
        yield get(client, "http://httpbin.org/get")
        assert cass.play_count == 1


@pytest.mark.gen_test
def test_request_time_is_set(get_client, tmpdir):
    """Ensures that the request_time on HTTPResponses is set."""

    with vcr.use_cassette(str(tmpdir.join("data.yaml"))):
        client = get_client()
        response = yield get(client, "http://httpbin.org/get")
        assert response.request_time is not None

    with vcr.use_cassette(str(tmpdir.join("data.yaml"))) as cass:
        client = get_client()
        response = yield get(client, "http://httpbin.org/get")
        assert response.request_time is not None
        assert cass.play_count == 1
