import os
import json
import pytest
import vcr
from six.moves.urllib.request import urlopen


def test_set_serializer_default_config(tmpdir, httpbin):
    my_vcr = vcr.VCR(serializer="json")

    with my_vcr.use_cassette(str(tmpdir.join("test.json"))):
        assert my_vcr.serializer == "json"
        urlopen(httpbin.url + "/get")

    with open(str(tmpdir.join("test.json"))) as f:
        assert json.loads(f.read())


def test_default_set_cassette_library_dir(tmpdir, httpbin):
    my_vcr = vcr.VCR(cassette_library_dir=str(tmpdir.join("subdir")))

    with my_vcr.use_cassette("test.json"):
        urlopen(httpbin.url + "/get")

    assert os.path.exists(str(tmpdir.join("subdir").join("test.json")))


def test_override_set_cassette_library_dir(tmpdir, httpbin):
    my_vcr = vcr.VCR(cassette_library_dir=str(tmpdir.join("subdir")))

    cld = str(tmpdir.join("subdir2"))

    with my_vcr.use_cassette("test.json", cassette_library_dir=cld):
        urlopen(httpbin.url + "/get")

    assert os.path.exists(str(tmpdir.join("subdir2").join("test.json")))
    assert not os.path.exists(str(tmpdir.join("subdir").join("test.json")))


def test_override_match_on(tmpdir, httpbin):
    my_vcr = vcr.VCR(match_on=["method"])

    with my_vcr.use_cassette(str(tmpdir.join("test.json"))):
        urlopen(httpbin.url)

    with my_vcr.use_cassette(str(tmpdir.join("test.json"))) as cass:
        urlopen(httpbin.url + "/get")

    assert len(cass) == 1
    assert cass.play_count == 1


def test_missing_matcher():
    my_vcr = vcr.VCR()
    my_vcr.register_matcher("awesome", object)
    with pytest.raises(KeyError):
        with my_vcr.use_cassette("test.yaml", match_on=["notawesome"]):
            pass
