import vcr
from six.moves.urllib.request import urlopen


def test_recorded_request_uri_with_redirected_request(tmpdir, httpbin):
    with vcr.use_cassette(str(tmpdir.join("test.yml"))) as cass:
        assert len(cass) == 0
        urlopen(httpbin.url + "/redirect/3")
        assert cass.requests[0].uri == httpbin.url + "/redirect/3"
        assert cass.requests[3].uri == httpbin.url + "/get"
        assert len(cass) == 4


def test_records_multiple_header_values(tmpdir, httpbin):
    with vcr.use_cassette(str(tmpdir.join("test.yml"))) as cass:
        assert len(cass) == 0
        urlopen(httpbin.url + "/response-headers?foo=bar&foo=baz")
        assert len(cass) == 1
        assert cass.responses[0]["headers"]["foo"] == ["bar", "baz"]
