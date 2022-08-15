# -*- coding: utf-8 -*-
"""Test requests' interaction with vcr"""
import platform
import pytest
import sys
import vcr
from assertions import assert_cassette_empty, assert_is_json

requests = pytest.importorskip("requests")
from requests.exceptions import ConnectionError  # noqa E402


def test_status_code(httpbin_both, tmpdir):
    """Ensure that we can read the status code"""
    url = httpbin_both.url + "/"
    with vcr.use_cassette(str(tmpdir.join("atts.yaml"))):
        status_code = requests.get(url).status_code

    with vcr.use_cassette(str(tmpdir.join("atts.yaml"))):
        assert status_code == requests.get(url).status_code


def test_headers(httpbin_both, tmpdir):
    """Ensure that we can read the headers back"""
    url = httpbin_both + "/"
    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        headers = requests.get(url).headers

    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        assert headers == requests.get(url).headers


def test_body(tmpdir, httpbin_both):
    """Ensure the responses are all identical enough"""
    url = httpbin_both + "/bytes/1024"
    with vcr.use_cassette(str(tmpdir.join("body.yaml"))):
        content = requests.get(url).content

    with vcr.use_cassette(str(tmpdir.join("body.yaml"))):
        assert content == requests.get(url).content


def test_get_empty_content_type_json(tmpdir, httpbin_both):
    """Ensure GET with application/json content-type and empty request body doesn't crash"""
    url = httpbin_both + "/status/200"
    headers = {"Content-Type": "application/json"}

    with vcr.use_cassette(str(tmpdir.join("get_empty_json.yaml")), match_on=("body",)):
        status = requests.get(url, headers=headers).status_code

    with vcr.use_cassette(str(tmpdir.join("get_empty_json.yaml")), match_on=("body",)):
        assert status == requests.get(url, headers=headers).status_code


def test_effective_url(tmpdir, httpbin_both):
    """Ensure that the effective_url is captured"""
    url = httpbin_both.url + "/redirect-to?url=/html"
    with vcr.use_cassette(str(tmpdir.join("url.yaml"))):
        effective_url = requests.get(url).url
        assert effective_url == httpbin_both.url + "/html"

    with vcr.use_cassette(str(tmpdir.join("url.yaml"))):
        assert effective_url == requests.get(url).url


def test_auth(tmpdir, httpbin_both):
    """Ensure that we can handle basic auth"""
    auth = ("user", "passwd")
    url = httpbin_both + "/basic-auth/user/passwd"
    with vcr.use_cassette(str(tmpdir.join("auth.yaml"))):
        one = requests.get(url, auth=auth)

    with vcr.use_cassette(str(tmpdir.join("auth.yaml"))):
        two = requests.get(url, auth=auth)
        assert one.content == two.content
        assert one.status_code == two.status_code


def test_auth_failed(tmpdir, httpbin_both):
    """Ensure that we can save failed auth statuses"""
    auth = ("user", "wrongwrongwrong")
    url = httpbin_both + "/basic-auth/user/passwd"
    with vcr.use_cassette(str(tmpdir.join("auth-failed.yaml"))) as cass:
        # Ensure that this is empty to begin with
        assert_cassette_empty(cass)
        one = requests.get(url, auth=auth)
        two = requests.get(url, auth=auth)
        assert one.content == two.content
        assert one.status_code == two.status_code == 401


def test_post(tmpdir, httpbin_both):
    """Ensure that we can post and cache the results"""
    data = {"key1": "value1", "key2": "value2"}
    url = httpbin_both + "/post"
    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        req1 = requests.post(url, data).content

    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        req2 = requests.post(url, data).content

    assert req1 == req2


def test_post_chunked_binary(tmpdir, httpbin):
    """Ensure that we can send chunked binary without breaking while trying to concatenate bytes with str."""
    data1 = iter([b"data", b"to", b"send"])
    data2 = iter([b"data", b"to", b"send"])
    url = httpbin.url + "/post"
    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        req1 = requests.post(url, data1).content

    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        req2 = requests.post(url, data2).content

    assert req1 == req2


@pytest.mark.skipif("sys.version_info >= (3, 6)", strict=True, raises=ConnectionError)
@pytest.mark.skipif(
    (3, 5) < sys.version_info < (3, 6) and platform.python_implementation() == "CPython",
    reason="Fails on CPython 3.5",
)
def test_post_chunked_binary_secure(tmpdir, httpbin_secure):
    """Ensure that we can send chunked binary without breaking while trying to concatenate bytes with str."""
    data1 = iter([b"data", b"to", b"send"])
    data2 = iter([b"data", b"to", b"send"])
    url = httpbin_secure.url + "/post"
    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        req1 = requests.post(url, data1).content
        print(req1)

    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        req2 = requests.post(url, data2).content

    assert req1 == req2


def test_redirects(tmpdir, httpbin_both):
    """Ensure that we can handle redirects"""
    url = httpbin_both + "/redirect-to?url=bytes/1024"
    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))):
        content = requests.get(url).content

    with vcr.use_cassette(str(tmpdir.join("requests.yaml"))) as cass:
        assert content == requests.get(url).content
        # Ensure that we've now cached *two* responses. One for the redirect
        # and one for the final fetch
        assert len(cass) == 2
        assert cass.play_count == 2


def test_cross_scheme(tmpdir, httpbin_secure, httpbin):
    """Ensure that requests between schemes are treated separately"""
    # First fetch a url under http, and then again under https and then
    # ensure that we haven't served anything out of cache, and we have two
    # requests / response pairs in the cassette
    with vcr.use_cassette(str(tmpdir.join("cross_scheme.yaml"))) as cass:
        requests.get(httpbin_secure + "/")
        requests.get(httpbin + "/")
        assert cass.play_count == 0
        assert len(cass) == 2


def test_gzip(tmpdir, httpbin_both):
    """
    Ensure that requests (actually urllib3) is able to automatically decompress
    the response body
    """
    url = httpbin_both + "/gzip"
    response = requests.get(url)

    with vcr.use_cassette(str(tmpdir.join("gzip.yaml"))):
        response = requests.get(url)
        assert_is_json(response.content)

    with vcr.use_cassette(str(tmpdir.join("gzip.yaml"))):
        assert_is_json(response.content)


def test_session_and_connection_close(tmpdir, httpbin):
    """
    This tests the issue in https://github.com/kevin1024/vcrpy/issues/48

    If you use a requests.session and the connection is closed, then an
    exception is raised in the urllib3 module vendored into requests:
    `AttributeError: 'NoneType' object has no attribute 'settimeout'`
    """
    with vcr.use_cassette(str(tmpdir.join("session_connection_closed.yaml"))):
        session = requests.session()

        session.get(httpbin + "/get", headers={"Connection": "close"})
        session.get(httpbin + "/get", headers={"Connection": "close"})


def test_https_with_cert_validation_disabled(tmpdir, httpbin_secure):
    with vcr.use_cassette(str(tmpdir.join("cert_validation_disabled.yaml"))):
        requests.get(httpbin_secure.url, verify=False)


def test_session_can_make_requests_after_requests_unpatched(tmpdir, httpbin):
    with vcr.use_cassette(str(tmpdir.join("test_session_after_unpatched.yaml"))):
        session = requests.session()
        session.get(httpbin + "/get")

    with vcr.use_cassette(str(tmpdir.join("test_session_after_unpatched.yaml"))):
        session = requests.session()
        session.get(httpbin + "/get")

    session.get(httpbin + "/status/200")


def test_session_created_before_use_cassette_is_patched(tmpdir, httpbin_both):
    url = httpbin_both + "/bytes/1024"
    # Record arbitrary, random data to the cassette
    with vcr.use_cassette(str(tmpdir.join("session_created_outside.yaml"))):
        session = requests.session()
        body = session.get(url).content

    # Create a session outside of any cassette context manager
    session = requests.session()
    # Make a request to make sure that a connectionpool is instantiated
    session.get(httpbin_both + "/get")

    with vcr.use_cassette(str(tmpdir.join("session_created_outside.yaml"))):
        # These should only be the same if the patching succeeded.
        assert session.get(url).content == body


def test_nested_cassettes_with_session_created_before_nesting(httpbin_both, tmpdir):
    """
    This tests ensures that a session that was created while one cassette was
    active is patched to the use the responses of a second cassette when it
    is enabled.
    """
    url = httpbin_both + "/bytes/1024"
    with vcr.use_cassette(str(tmpdir.join("first_nested.yaml"))):
        session = requests.session()
        first_body = session.get(url).content
        with vcr.use_cassette(str(tmpdir.join("second_nested.yaml"))):
            second_body = session.get(url).content
            third_body = requests.get(url).content

    with vcr.use_cassette(str(tmpdir.join("second_nested.yaml"))):
        session = requests.session()
        assert session.get(url).content == second_body
        with vcr.use_cassette(str(tmpdir.join("first_nested.yaml"))):
            assert session.get(url).content == first_body
        assert session.get(url).content == third_body

    # Make sure that the session can now get content normally.
    assert "User-agent" in session.get(httpbin_both.url + "/robots.txt").text


def test_post_file(tmpdir, httpbin_both):
    """Ensure that we handle posting a file."""
    url = httpbin_both + "/post"
    with vcr.use_cassette(str(tmpdir.join("post_file.yaml"))) as cass, open("tox.ini", "rb") as f:
        original_response = requests.post(url, f).content

    # This also tests that we do the right thing with matching the body when they are files.
    with vcr.use_cassette(
        str(tmpdir.join("post_file.yaml")),
        match_on=("method", "scheme", "host", "port", "path", "query", "body"),
    ) as cass:
        with open("tox.ini", "rb") as f:
            tox_content = f.read()
        assert cass.requests[0].body.read() == tox_content
        with open("tox.ini", "rb") as f:
            new_response = requests.post(url, f).content
        assert original_response == new_response


def test_filter_post_params(tmpdir, httpbin_both):
    """
    This tests the issue in https://github.com/kevin1024/vcrpy/issues/158

    Ensure that a post request made through requests can still be filtered.
    with vcr.use_cassette(cass_file, filter_post_data_parameters=['id']) as cass:
        assert b'id=secret' not in cass.requests[0].body
    """
    url = httpbin_both.url + "/post"
    cass_loc = str(tmpdir.join("filter_post_params.yaml"))
    with vcr.use_cassette(cass_loc, filter_post_data_parameters=["key"]) as cass:
        requests.post(url, data={"key": "value"})
    with vcr.use_cassette(cass_loc, filter_post_data_parameters=["key"]) as cass:
        assert b"key=value" not in cass.requests[0].body


def test_post_unicode_match_on_body(tmpdir, httpbin_both):
    """Ensure that matching on POST body that contains Unicode characters works."""
    data = {"key1": "value1", "●‿●": "٩(●̮̮̃•̃)۶"}
    url = httpbin_both + "/post"

    with vcr.use_cassette(str(tmpdir.join("requests.yaml")), additional_matchers=("body",)):
        req1 = requests.post(url, data).content

    with vcr.use_cassette(str(tmpdir.join("requests.yaml")), additional_matchers=("body",)):
        req2 = requests.post(url, data).content

    assert req1 == req2
