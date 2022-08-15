# -*- coding: utf-8 -*-
"""Integration tests with urllib2"""

import ssl
from six.moves.urllib.request import urlopen
from six.moves.urllib_parse import urlencode
import pytest_httpbin.certs

# Internal imports
import vcr

from assertions import assert_cassette_has_one_response


def urlopen_with_cafile(*args, **kwargs):
    context = ssl.create_default_context(cafile=pytest_httpbin.certs.where())
    context.check_hostname = False
    kwargs["context"] = context
    try:
        return urlopen(*args, **kwargs)
    except TypeError:
        # python2/pypi don't let us override this
        del kwargs["cafile"]
        return urlopen(*args, **kwargs)


def test_response_code(httpbin_both, tmpdir):
    """Ensure we can read a response code from a fetch"""
    url = httpbin_both.url
    with vcr.use_cassette(str(tmpdir.join("atts.yaml"))):
        code = urlopen_with_cafile(url).getcode()

    with vcr.use_cassette(str(tmpdir.join("atts.yaml"))):
        assert code == urlopen_with_cafile(url).getcode()


def test_random_body(httpbin_both, tmpdir):
    """Ensure we can read the content, and that it's served from cache"""
    url = httpbin_both.url + "/bytes/1024"
    with vcr.use_cassette(str(tmpdir.join("body.yaml"))):
        body = urlopen_with_cafile(url).read()

    with vcr.use_cassette(str(tmpdir.join("body.yaml"))):
        assert body == urlopen_with_cafile(url).read()


def test_response_headers(httpbin_both, tmpdir):
    """Ensure we can get information from the response"""
    url = httpbin_both.url
    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        open1 = urlopen_with_cafile(url).info().items()

    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        open2 = urlopen_with_cafile(url).info().items()

        assert sorted(open1) == sorted(open2)


def test_effective_url(httpbin_both, tmpdir):
    """Ensure that the effective_url is captured"""
    url = httpbin_both.url + "/redirect-to?url=/html"
    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        effective_url = urlopen_with_cafile(url).geturl()
        assert effective_url == httpbin_both.url + "/html"

    with vcr.use_cassette(str(tmpdir.join("headers.yaml"))):
        assert effective_url == urlopen_with_cafile(url).geturl()


def test_multiple_requests(httpbin_both, tmpdir):
    """Ensure that we can cache multiple requests"""
    urls = [httpbin_both.url, httpbin_both.url, httpbin_both.url + "/get", httpbin_both.url + "/bytes/1024"]
    with vcr.use_cassette(str(tmpdir.join("multiple.yaml"))) as cass:
        [urlopen_with_cafile(url) for url in urls]
    assert len(cass) == len(urls)


def test_get_data(httpbin_both, tmpdir):
    """Ensure that it works with query data"""
    data = urlencode({"some": 1, "data": "here"})
    url = httpbin_both.url + "/get?" + data
    with vcr.use_cassette(str(tmpdir.join("get_data.yaml"))):
        res1 = urlopen_with_cafile(url).read()

    with vcr.use_cassette(str(tmpdir.join("get_data.yaml"))):
        res2 = urlopen_with_cafile(url).read()
    assert res1 == res2


def test_post_data(httpbin_both, tmpdir):
    """Ensure that it works when posting data"""
    data = urlencode({"some": 1, "data": "here"}).encode("utf-8")
    url = httpbin_both.url + "/post"
    with vcr.use_cassette(str(tmpdir.join("post_data.yaml"))):
        res1 = urlopen_with_cafile(url, data).read()

    with vcr.use_cassette(str(tmpdir.join("post_data.yaml"))) as cass:
        res2 = urlopen_with_cafile(url, data).read()
        assert len(cass) == 1

    assert res1 == res2
    assert_cassette_has_one_response(cass)


def test_post_unicode_data(httpbin_both, tmpdir):
    """Ensure that it works when posting unicode data"""
    data = urlencode({"snowman": u"☃".encode("utf-8")}).encode("utf-8")
    url = httpbin_both.url + "/post"
    with vcr.use_cassette(str(tmpdir.join("post_data.yaml"))):
        res1 = urlopen_with_cafile(url, data).read()

    with vcr.use_cassette(str(tmpdir.join("post_data.yaml"))) as cass:
        res2 = urlopen_with_cafile(url, data).read()
        assert len(cass) == 1

    assert res1 == res2
    assert_cassette_has_one_response(cass)


def test_cross_scheme(tmpdir, httpbin_secure, httpbin):
    """Ensure that requests between schemes are treated separately"""
    # First fetch a url under https, and then again under https and then
    # ensure that we haven't served anything out of cache, and we have two
    # requests / response pairs in the cassette
    with vcr.use_cassette(str(tmpdir.join("cross_scheme.yaml"))) as cass:
        urlopen_with_cafile(httpbin_secure.url)
        urlopen_with_cafile(httpbin.url)
        assert len(cass) == 2
        assert cass.play_count == 0


def test_decorator(httpbin_both, tmpdir):
    """Test the decorator version of VCR.py"""
    url = httpbin_both.url

    @vcr.use_cassette(str(tmpdir.join("atts.yaml")))
    def inner1():
        return urlopen_with_cafile(url).getcode()

    @vcr.use_cassette(str(tmpdir.join("atts.yaml")))
    def inner2():
        return urlopen_with_cafile(url).getcode()

    assert inner1() == inner2()
