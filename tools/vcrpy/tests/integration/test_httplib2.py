# -*- coding: utf-8 -*-
"""Integration tests with httplib2"""

import sys

from six.moves.urllib_parse import urlencode
import pytest
import pytest_httpbin.certs

import vcr

from assertions import assert_cassette_has_one_response

httplib2 = pytest.importorskip("httplib2")


def http():
    """
    Returns an httplib2 HTTP instance
    with the certificate replaced by the httpbin one.
    """
    kwargs = {"ca_certs": pytest_httpbin.certs.where()}
    if sys.version_info[:2] in [(2, 7), (3, 7)]:
        kwargs["disable_ssl_certificate_validation"] = True
    return httplib2.Http(**kwargs)


def test_response_code(tmpdir, httpbin_both):
    """Ensure we can read a response code from a fetch"""
    url = httpbin_both.url
    with vcr.use_cassette(str(tmpdir.join("atts.yaml"))):
        resp, _ = http().request(url)
        code = resp.status

    with vcr.use_cassette(str(tmpdir.join("atts.yaml"))):
        resp, _ = http().request(url)
        assert code == resp.status


def test_random_body(httpbin_both, tmpdir):
    """Ensure we can read the content, and that it's served from cache"""
    url = httpbin_both.url + "/bytes/1024"
    with vcr.use_cassette(str(tmpdir.join("body.yaml"))):
        _, content = http().request(url)
        body = content

    with vcr.use_cassette(str(tmpdir.join("body.yaml"))):
        _, content = http().request(url)
        assert body == content


def test_response_headers(tmpdir, httpbin_both):
    """Ensure we can get information from the response"""
    url = httpbin_both.url
    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        resp, _ = http().request(url)
        headers = resp.items()

    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        resp, _ = http().request(url)
        assert set(headers) == set(resp.items())


def test_effective_url(tmpdir, httpbin_both):
    """Ensure that the effective_url is captured"""
    url = httpbin_both.url + "/redirect-to?url=/html"
    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        resp, _ = http().request(url)
        effective_url = resp["content-location"]
        assert effective_url == httpbin_both + "/html"

    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        resp, _ = http().request(url)
        assert effective_url == resp["content-location"]


def test_multiple_requests(tmpdir, httpbin_both):
    """Ensure that we can cache multiple requests"""
    urls = [httpbin_both.url, httpbin_both.url, httpbin_both.url + "/get", httpbin_both.url + "/bytes/1024"]
    with vcr.use_cassette(str(tmpdir.join("multiple.yaml"))) as cass:
        [http().request(url) for url in urls]
    assert len(cass) == len(urls)


def test_get_data(tmpdir, httpbin_both):
    """Ensure that it works with query data"""
    data = urlencode({"some": 1, "data": "here"})
    url = httpbin_both.url + "/get?" + data
    with vcr.use_cassette(str(tmpdir.join("get_data.yaml"))):
        _, res1 = http().request(url)

    with vcr.use_cassette(str(tmpdir.join("get_data.yaml"))):
        _, res2 = http().request(url)

    assert res1 == res2


def test_post_data(tmpdir, httpbin_both):
    """Ensure that it works when posting data"""
    data = urlencode({"some": 1, "data": "here"})
    url = httpbin_both.url + "/post"
    with vcr.use_cassette(str(tmpdir.join("post_data.yaml"))):
        _, res1 = http().request(url, "POST", data)

    with vcr.use_cassette(str(tmpdir.join("post_data.yaml"))) as cass:
        _, res2 = http().request(url, "POST", data)

    assert res1 == res2
    assert_cassette_has_one_response(cass)


def test_post_unicode_data(tmpdir, httpbin_both):
    """Ensure that it works when posting unicode data"""
    data = urlencode({"snowman": u"☃".encode("utf-8")})
    url = httpbin_both.url + "/post"
    with vcr.use_cassette(str(tmpdir.join("post_data.yaml"))):
        _, res1 = http().request(url, "POST", data)

    with vcr.use_cassette(str(tmpdir.join("post_data.yaml"))) as cass:
        _, res2 = http().request(url, "POST", data)

    assert res1 == res2
    assert_cassette_has_one_response(cass)


def test_cross_scheme(tmpdir, httpbin, httpbin_secure):
    """Ensure that requests between schemes are treated separately"""
    # First fetch a url under https, and then again under https and then
    # ensure that we haven't served anything out of cache, and we have two
    # requests / response pairs in the cassette
    with vcr.use_cassette(str(tmpdir.join("cross_scheme.yaml"))) as cass:
        http().request(httpbin_secure.url)
        http().request(httpbin.url)
        assert len(cass) == 2
        assert cass.play_count == 0


def test_decorator(tmpdir, httpbin_both):
    """Test the decorator version of VCR.py"""
    url = httpbin_both.url

    @vcr.use_cassette(str(tmpdir.join("atts.yaml")))
    def inner1():
        resp, _ = http().request(url)
        return resp["status"]

    @vcr.use_cassette(str(tmpdir.join("atts.yaml")))
    def inner2():
        resp, _ = http().request(url)
        return resp["status"]

    assert inner1() == inner2()
