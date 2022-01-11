# -*- coding: utf-8 -*-
"""Basic tests about save behavior"""

# External imports
import os
import time
from six.moves.urllib.request import urlopen

# Internal imports
import vcr


def test_disk_saver_nowrite(tmpdir, httpbin):
    """
    Ensure that when you close a cassette without changing it it doesn't
    rewrite the file
    """
    fname = str(tmpdir.join("synopsis.yaml"))
    with vcr.use_cassette(fname) as cass:
        urlopen(httpbin.url).read()
        assert cass.play_count == 0
    last_mod = os.path.getmtime(fname)

    with vcr.use_cassette(fname) as cass:
        urlopen(httpbin.url).read()
        assert cass.play_count == 1
        assert cass.dirty is False
    last_mod2 = os.path.getmtime(fname)

    assert last_mod == last_mod2


def test_disk_saver_write(tmpdir, httpbin):
    """
    Ensure that when you close a cassette after changing it it does
    rewrite the file
    """
    fname = str(tmpdir.join("synopsis.yaml"))
    with vcr.use_cassette(fname) as cass:
        urlopen(httpbin.url).read()
        assert cass.play_count == 0
    last_mod = os.path.getmtime(fname)

    # Make sure at least 1 second passes, otherwise sometimes
    # the mtime doesn't change
    time.sleep(1)

    with vcr.use_cassette(fname, record_mode="any") as cass:
        urlopen(httpbin.url).read()
        urlopen(httpbin.url + "/get").read()
        assert cass.play_count == 1
        assert cass.dirty
    last_mod2 = os.path.getmtime(fname)

    assert last_mod != last_mod2
