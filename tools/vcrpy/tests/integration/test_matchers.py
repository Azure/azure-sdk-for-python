import vcr
import pytest
from six.moves.urllib.request import urlopen


DEFAULT_URI = "http://httpbin.org/get?p1=q1&p2=q2"  # base uri for testing


def _replace_httpbin(uri, httpbin, httpbin_secure):
    return uri.replace("http://httpbin.org", httpbin.url).replace("https://httpbin.org", httpbin_secure.url)


@pytest.fixture
def cassette(tmpdir, httpbin, httpbin_secure):
    """
    Helper fixture used to prepare the cassete
    returns path to the recorded cassette
    """
    default_uri = _replace_httpbin(DEFAULT_URI, httpbin, httpbin_secure)

    cassette_path = str(tmpdir.join("test.yml"))
    with vcr.use_cassette(cassette_path, record_mode="all"):
        urlopen(default_uri)
    return cassette_path


@pytest.mark.parametrize(
    "matcher, matching_uri, not_matching_uri",
    [
        ("uri", "http://httpbin.org/get?p1=q1&p2=q2", "http://httpbin.org/get?p2=q2&p1=q1"),
        ("scheme", "http://google.com/post?a=b", "https://httpbin.org/get?p1=q1&p2=q2"),
        ("host", "https://httpbin.org/post?a=b", "http://google.com/get?p1=q1&p2=q2"),
        ("path", "https://google.com/get?a=b", "http://httpbin.org/post?p1=q1&p2=q2"),
        ("query", "https://google.com/get?p2=q2&p1=q1", "http://httpbin.org/get?p1=q1&a=b"),
    ],
)
def test_matchers(httpbin, httpbin_secure, cassette, matcher, matching_uri, not_matching_uri):

    matching_uri = _replace_httpbin(matching_uri, httpbin, httpbin_secure)
    not_matching_uri = _replace_httpbin(not_matching_uri, httpbin, httpbin_secure)
    default_uri = _replace_httpbin(DEFAULT_URI, httpbin, httpbin_secure)

    # play cassette with default uri
    with vcr.use_cassette(cassette, match_on=[matcher]) as cass:
        urlopen(default_uri)
        assert cass.play_count == 1

    # play cassette with matching on uri
    with vcr.use_cassette(cassette, match_on=[matcher]) as cass:
        urlopen(matching_uri)
        assert cass.play_count == 1

    # play cassette with not matching on uri, it should fail
    with pytest.raises(vcr.errors.CannotOverwriteExistingCassetteException):
        with vcr.use_cassette(cassette, match_on=[matcher]) as cass:
            urlopen(not_matching_uri)


def test_method_matcher(cassette, httpbin, httpbin_secure):
    default_uri = _replace_httpbin(DEFAULT_URI, httpbin, httpbin_secure)

    # play cassette with matching on method
    with vcr.use_cassette(cassette, match_on=["method"]) as cass:
        urlopen("https://google.com/get?a=b")
        assert cass.play_count == 1

    # should fail if method does not match
    with pytest.raises(vcr.errors.CannotOverwriteExistingCassetteException):
        with vcr.use_cassette(cassette, match_on=["method"]) as cass:
            # is a POST request
            urlopen(default_uri, data=b"")


@pytest.mark.parametrize(
    "uri", [DEFAULT_URI, "http://httpbin.org/get?p2=q2&p1=q1", "http://httpbin.org/get?p2=q2&p1=q1"]
)
def test_default_matcher_matches(cassette, uri, httpbin, httpbin_secure):

    uri = _replace_httpbin(uri, httpbin, httpbin_secure)

    with vcr.use_cassette(cassette) as cass:
        urlopen(uri)
        assert cass.play_count == 1


@pytest.mark.parametrize(
    "uri",
    [
        "https://httpbin.org/get?p1=q1&p2=q2",
        "http://google.com/get?p1=q1&p2=q2",
        "http://httpbin.org/post?p1=q1&p2=q2",
        "http://httpbin.org/get?p1=q1&a=b",
    ],
)
def test_default_matcher_does_not_match(cassette, uri, httpbin, httpbin_secure):
    uri = _replace_httpbin(uri, httpbin, httpbin_secure)
    with pytest.raises(vcr.errors.CannotOverwriteExistingCassetteException):
        with vcr.use_cassette(cassette):
            urlopen(uri)


def test_default_matcher_does_not_match_on_method(cassette, httpbin, httpbin_secure):
    default_uri = _replace_httpbin(DEFAULT_URI, httpbin, httpbin_secure)
    with pytest.raises(vcr.errors.CannotOverwriteExistingCassetteException):
        with vcr.use_cassette(cassette):
            # is a POST request
            urlopen(default_uri, data=b"")
