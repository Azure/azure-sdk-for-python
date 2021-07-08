import multiprocessing
import pytest
from six.moves import xmlrpc_client, xmlrpc_server

requests = pytest.importorskip("requests")

import vcr  # NOQA

try:
    import httplib
except ImportError:
    import http.client as httplib


def test_domain_redirect():
    """Ensure that redirects across domains are considered unique"""
    # In this example, seomoz.org redirects to moz.com, and if those
    # requests are considered identical, then we'll be stuck in a redirect
    # loop.
    url = "http://seomoz.org/"
    with vcr.use_cassette("tests/fixtures/wild/domain_redirect.yaml") as cass:
        requests.get(url, headers={"User-Agent": "vcrpy-test"})
        # Ensure that we've now served two responses. One for the original
        # redirect, and a second for the actual fetch
        assert len(cass) == 2


def test_flickr_multipart_upload(httpbin, tmpdir):
    """
    The python-flickr-api project does a multipart
    upload that confuses vcrpy
    """

    def _pretend_to_be_flickr_library():
        content_type, body = "text/plain", "HELLO WORLD"
        h = httplib.HTTPConnection(httpbin.host, httpbin.port)
        headers = {"Content-Type": content_type, "content-length": str(len(body))}
        h.request("POST", "/post/", headers=headers)
        h.send(body)
        r = h.getresponse()
        data = r.read()
        h.close()

        return data

    testfile = str(tmpdir.join("flickr.yml"))
    with vcr.use_cassette(testfile) as cass:
        _pretend_to_be_flickr_library()
        assert len(cass) == 1

    with vcr.use_cassette(testfile) as cass:
        assert len(cass) == 1
        _pretend_to_be_flickr_library()
        assert cass.play_count == 1


def test_flickr_should_respond_with_200(tmpdir):
    testfile = str(tmpdir.join("flickr.yml"))
    with vcr.use_cassette(testfile):
        r = requests.post("https://api.flickr.com/services/upload", verify=False)
        assert r.status_code == 200


def test_cookies(tmpdir, httpbin):
    testfile = str(tmpdir.join("cookies.yml"))
    with vcr.use_cassette(testfile):
        s = requests.Session()
        s.get(httpbin.url + "/cookies/set?k1=v1&k2=v2")

        r2 = s.get(httpbin.url + "/cookies")
        assert len(r2.json()["cookies"]) == 2


def test_amazon_doctype(tmpdir):
    # amazon gzips its homepage.  For some reason, in requests 2.7, it's not
    # getting gunzipped.
    with vcr.use_cassette(str(tmpdir.join("amz.yml"))):
        r = requests.get("http://www.amazon.com", verify=False)
    assert "html" in r.text


def start_rpc_server(q):
    httpd = xmlrpc_server.SimpleXMLRPCServer(("127.0.0.1", 0))
    httpd.register_function(pow)
    q.put("http://{}:{}".format(*httpd.server_address))
    httpd.serve_forever()


@pytest.yield_fixture(scope="session")
def rpc_server():
    q = multiprocessing.Queue()
    proxy_process = multiprocessing.Process(target=start_rpc_server, args=(q,))
    try:
        proxy_process.start()
        yield q.get()
    finally:
        proxy_process.terminate()


def test_xmlrpclib(tmpdir, rpc_server):
    with vcr.use_cassette(str(tmpdir.join("xmlrpcvideo.yaml"))):
        roundup_server = xmlrpc_client.ServerProxy(rpc_server, allow_none=True)
        original_schema = roundup_server.pow(2, 4)

    with vcr.use_cassette(str(tmpdir.join("xmlrpcvideo.yaml"))):
        roundup_server = xmlrpc_client.ServerProxy(rpc_server, allow_none=True)
        second_schema = roundup_server.pow(2, 4)

    assert original_schema == second_schema
