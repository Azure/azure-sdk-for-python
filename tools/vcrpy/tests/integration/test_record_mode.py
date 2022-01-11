import pytest
import vcr
from six.moves.urllib.request import urlopen


def test_once_record_mode(tmpdir, httpbin):
    testfile = str(tmpdir.join("recordmode.yml"))
    with vcr.use_cassette(testfile, record_mode="once"):
        # cassette file doesn't exist, so create.
        urlopen(httpbin.url).read()

    with vcr.use_cassette(testfile, record_mode="once"):
        # make the same request again
        urlopen(httpbin.url).read()

        # the first time, it's played from the cassette.
        # but, try to access something else from the same cassette, and an
        # exception is raised.
        with pytest.raises(Exception):
            urlopen(httpbin.url + "/get").read()


def test_once_record_mode_two_times(tmpdir, httpbin):
    testfile = str(tmpdir.join("recordmode.yml"))
    with vcr.use_cassette(testfile, record_mode="once"):
        # get two of the same file
        urlopen(httpbin.url).read()
        urlopen(httpbin.url).read()

    with vcr.use_cassette(testfile, record_mode="once"):
        # do it again
        urlopen(httpbin.url).read()
        urlopen(httpbin.url).read()


def test_once_mode_three_times(tmpdir, httpbin):
    testfile = str(tmpdir.join("recordmode.yml"))
    with vcr.use_cassette(testfile, record_mode="once"):
        # get three of the same file
        urlopen(httpbin.url).read()
        urlopen(httpbin.url).read()
        urlopen(httpbin.url).read()


def test_new_episodes_record_mode(tmpdir, httpbin):
    testfile = str(tmpdir.join("recordmode.yml"))

    with vcr.use_cassette(testfile, record_mode="new_episodes"):
        # cassette file doesn't exist, so create.
        urlopen(httpbin.url).read()

    with vcr.use_cassette(testfile, record_mode="new_episodes") as cass:
        # make the same request again
        urlopen(httpbin.url).read()

        # all responses have been played
        assert cass.all_played

        # in the "new_episodes" record mode, we can add more requests to
        # a cassette without repurcussions.
        urlopen(httpbin.url + "/get").read()

        # one of the responses has been played
        assert cass.play_count == 1

        # not all responses have been played
        assert not cass.all_played

    with vcr.use_cassette(testfile, record_mode="new_episodes") as cass:
        # the cassette should now have 2 responses
        assert len(cass.responses) == 2


def test_new_episodes_record_mode_two_times(tmpdir, httpbin):
    testfile = str(tmpdir.join("recordmode.yml"))
    url = httpbin.url + "/bytes/1024"
    with vcr.use_cassette(testfile, record_mode="new_episodes"):
        # cassette file doesn't exist, so create.
        original_first_response = urlopen(url).read()

    with vcr.use_cassette(testfile, record_mode="new_episodes"):
        # make the same request again
        assert urlopen(url).read() == original_first_response

        # in the "new_episodes" record mode, we can add the same request
        # to the cassette without repercussions
        original_second_response = urlopen(url).read()

    with vcr.use_cassette(testfile, record_mode="once"):
        # make the same request again
        assert urlopen(url).read() == original_first_response
        assert urlopen(url).read() == original_second_response
        # now that we are back in once mode, this should raise
        # an error.
        with pytest.raises(Exception):
            urlopen(url).read()


def test_all_record_mode(tmpdir, httpbin):
    testfile = str(tmpdir.join("recordmode.yml"))

    with vcr.use_cassette(testfile, record_mode="all"):
        # cassette file doesn't exist, so create.
        urlopen(httpbin.url).read()

    with vcr.use_cassette(testfile, record_mode="all") as cass:
        # make the same request again
        urlopen(httpbin.url).read()

        # in the "all" record mode, we can add more requests to
        # a cassette without repurcussions.
        urlopen(httpbin.url + "/get").read()

        # The cassette was never actually played, even though it existed.
        # that's because, in "all" mode, the requests all go directly to
        # the source and bypass the cassette.
        assert cass.play_count == 0


def test_none_record_mode(tmpdir, httpbin):
    # Cassette file doesn't exist, yet we are trying to make a request.
    # raise hell.
    testfile = str(tmpdir.join("recordmode.yml"))
    with vcr.use_cassette(testfile, record_mode="none"):
        with pytest.raises(Exception):
            urlopen(httpbin.url).read()


def test_none_record_mode_with_existing_cassette(tmpdir, httpbin):
    # create a cassette file
    testfile = str(tmpdir.join("recordmode.yml"))

    with vcr.use_cassette(testfile, record_mode="all"):
        urlopen(httpbin.url).read()

    # play from cassette file
    with vcr.use_cassette(testfile, record_mode="none") as cass:
        urlopen(httpbin.url).read()
        assert cass.play_count == 1
        # but if I try to hit the net, raise an exception.
        with pytest.raises(Exception):
            urlopen(httpbin.url + "/get").read()
