# -*- coding: utf-8 -*-
"""Basic tests for cassettes"""

# External imports
import os
from six.moves.urllib.request import urlopen

# Internal imports
import vcr


def test_nonexistent_directory(tmpdir, httpbin):
    """If we load a cassette in a nonexistent directory, it can save ok"""
    # Check to make sure directory doesnt exist
    assert not os.path.exists(str(tmpdir.join("nonexistent")))

    # Run VCR to create dir and cassette file
    with vcr.use_cassette(str(tmpdir.join("nonexistent", "cassette.yml"))):
        urlopen(httpbin.url).read()

    # This should have made the file and the directory
    assert os.path.exists(str(tmpdir.join("nonexistent", "cassette.yml")))


def test_unpatch(tmpdir, httpbin):
    """Ensure that our cassette gets unpatched when we're done"""
    with vcr.use_cassette(str(tmpdir.join("unpatch.yaml"))) as cass:
        urlopen(httpbin.url).read()

    # Make the same request, and assert that we haven't served any more
    # requests out of cache
    urlopen(httpbin.url).read()
    assert cass.play_count == 0


def test_basic_json_use(tmpdir, httpbin):
    """
    Ensure you can load a json serialized cassette
    """
    test_fixture = str(tmpdir.join("synopsis.json"))
    with vcr.use_cassette(test_fixture, serializer="json"):
        response = urlopen(httpbin.url).read()
        assert b"difficult sometimes" in response


def test_patched_content(tmpdir, httpbin):
    """
    Ensure that what you pull from a cassette is what came from the
    request
    """
    with vcr.use_cassette(str(tmpdir.join("synopsis.yaml"))) as cass:
        response = urlopen(httpbin.url).read()
        assert cass.play_count == 0

    with vcr.use_cassette(str(tmpdir.join("synopsis.yaml"))) as cass:
        response2 = urlopen(httpbin.url).read()
        assert cass.play_count == 1
        cass._save(force=True)

    with vcr.use_cassette(str(tmpdir.join("synopsis.yaml"))) as cass:
        response3 = urlopen(httpbin.url).read()
        assert cass.play_count == 1

    assert response == response2
    assert response2 == response3


def test_patched_content_json(tmpdir, httpbin):
    """
    Ensure that what you pull from a json cassette is what came from the
    request
    """

    testfile = str(tmpdir.join("synopsis.json"))

    with vcr.use_cassette(testfile) as cass:
        response = urlopen(httpbin.url).read()
        assert cass.play_count == 0

    with vcr.use_cassette(testfile) as cass:
        response2 = urlopen(httpbin.url).read()
        assert cass.play_count == 1
        cass._save(force=True)

    with vcr.use_cassette(testfile) as cass:
        response3 = urlopen(httpbin.url).read()
        assert cass.play_count == 1

    assert response == response2
    assert response2 == response3
