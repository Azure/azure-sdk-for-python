import pytest
import vcr
from six.moves.urllib.request import urlopen


def test_making_extra_request_raises_exception(tmpdir, httpbin):
    # make two requests in the first request that are considered
    # identical (since the match is based on method)
    with vcr.use_cassette(str(tmpdir.join("test.json")), match_on=["method"]):
        urlopen(httpbin.url + "/status/200")
        urlopen(httpbin.url + "/status/201")

    # Now, try to make three requests.  The first two should return the
    # correct status codes in order, and the third should raise an
    # exception.
    with vcr.use_cassette(str(tmpdir.join("test.json")), match_on=["method"]):
        assert urlopen(httpbin.url + "/status/200").getcode() == 200
        assert urlopen(httpbin.url + "/status/201").getcode() == 201
        with pytest.raises(Exception):
            urlopen(httpbin.url + "/status/200")
