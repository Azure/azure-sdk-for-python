# -*- coding: utf-8 -*-
"""Tests for cassettes with custom persistence"""

# External imports
import os
from six.moves.urllib.request import urlopen

# Internal imports
import vcr
from vcr.persisters.filesystem import FilesystemPersister


class CustomFilesystemPersister(object):
    """Behaves just like default FilesystemPersister but adds .test extension
       to the cassette file"""

    @staticmethod
    def load_cassette(cassette_path, serializer):
        cassette_path += ".test"
        return FilesystemPersister.load_cassette(cassette_path, serializer)

    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        cassette_path += ".test"
        FilesystemPersister.save_cassette(cassette_path, cassette_dict, serializer)


def test_save_cassette_with_custom_persister(tmpdir, httpbin):
    """Ensure you can save a cassette using custom persister"""
    my_vcr = vcr.VCR()
    my_vcr.register_persister(CustomFilesystemPersister)

    # Check to make sure directory doesnt exist
    assert not os.path.exists(str(tmpdir.join("nonexistent")))

    # Run VCR to create dir and cassette file using new save_cassette callback
    with my_vcr.use_cassette(str(tmpdir.join("nonexistent", "cassette.yml"))):
        urlopen(httpbin.url).read()

    # Callback should have made the file and the directory
    assert os.path.exists(str(tmpdir.join("nonexistent", "cassette.yml.test")))


def test_load_cassette_with_custom_persister(tmpdir, httpbin):
    """
    Ensure you can load a cassette using custom persister
    """
    my_vcr = vcr.VCR()
    my_vcr.register_persister(CustomFilesystemPersister)

    test_fixture = str(tmpdir.join("synopsis.json.test"))

    with my_vcr.use_cassette(test_fixture, serializer="json"):
        response = urlopen(httpbin.url).read()
        assert b"difficult sometimes" in response
