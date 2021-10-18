# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.pipeline.transport._base import _urljoin

def test_basic():
    assert (
        _urljoin("http://example.com/", "hello") ==
        _urljoin("http://example.com/", "/hello") ==
        "http://example.com/hello"
    )
    assert _urljoin('devstoreaccount1', '') == 'devstoreaccount1'
    assert _urljoin('devstoreaccount1', 'testdir/') == 'devstoreaccount1/testdir/'
    assert _urljoin('devstoreaccount1/', '') == 'devstoreaccount1/'
    assert _urljoin('devstoreaccount1/', 'testdir/') == 'devstoreaccount1/testdir/'

def test_query():
    assert (
        _urljoin("http://example.com/", "hello?foo=bar") ==
        _urljoin("http://example.com/", "/hello?foo=bar") ==
        "http://example.com/hello?foo=bar"
    )
    assert _urljoin("http://example.com", "?foo=bar") == "http://example.com?foo=bar"

    # if you explicitly say your stub url starts with a forward slash, we don't get rid of that
    assert _urljoin("http://example.com", "/?foo=bar") == "http://example.com/?foo=bar"
    assert _urljoin("", "?foo=bar") == "?foo=bar"
    assert (
        _urljoin("", "/?foo=bar") ==
        _urljoin("/", "?foo=bar") ==
        _urljoin("/", "/?foo=bar") ==
        "/?foo=bar"
    )

def test_extra_slashes():
    assert (
        _urljoin("http://example.com//", "hello") ==
        _urljoin("http://example.com///", "/hello") ==
        "http://example.com/hello"
    )

def test_colons():
    assert (
        _urljoin("http://example.com/", ":colon") ==
        _urljoin("http://example.com/", "/:colon") ==
        "http://example.com/:colon"
    )

def test_base_url_with_query():
    assert _urljoin("http://example.com/path?query=one&query=two", "?query=three") == "http://example.com/path?query=one&query=two&query=three"
