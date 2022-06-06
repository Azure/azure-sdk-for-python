# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from json import dumps
from flask import (
    Response,
    Blueprint,
)

encoding_api = Blueprint('encoding_api', __name__)

@encoding_api.route('/latin-1', methods=['GET'])
def latin_1():
    r = Response(
        u"Latin 1: ÿ".encode("latin-1"), status=200
    )
    r.headers["Content-Type"] = "text/plain; charset=latin-1"
    return r

@encoding_api.route('/latin-1-with-utf-8', methods=['GET'])
def latin_1_charset_utf8():
    r = Response(
        u"Latin 1: ÿ".encode("latin-1"), status=200
    )
    r.headers["Content-Type"] = "text/plain; charset=utf-8"
    return r

@encoding_api.route('/no-charset', methods=['GET'])
def latin_1_no_charset():
    r = Response(
        "Hello, world!", status=200
    )
    r.headers["Content-Type"] = "text/plain"
    return r

@encoding_api.route('/iso-8859-1', methods=['GET'])
def iso_8859_1():
    r = Response(
        u"Accented: Österreich".encode("iso-8859-1"), status=200
    )
    r.headers["Content-Type"] = "text/plain"
    return r

@encoding_api.route('/emoji', methods=['GET'])
def emoji():
    r = Response(
        u"👩", status=200
    )
    return r

@encoding_api.route('/emoji-family-skin-tone-modifier', methods=['GET'])
def emoji_family_skin_tone_modifier():
    r = Response(
        u"👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987", status=200
    )
    return r

@encoding_api.route('/korean', methods=['GET'])
def korean():
    r = Response(
        "아가", status=200
    )
    return r

@encoding_api.route('/json', methods=['GET'])
def json():
    data = {"greeting": "hello", "recipient": "world"}
    content = dumps(data).encode("utf-16")
    r = Response(
        content, status=200
    )
    r.headers["Content-Type"] = "application/json; charset=utf-16"
    return r

@encoding_api.route('/invalid-codec-name', methods=['GET'])
def invalid_codec_name():
    r = Response(
        "おはようございます。".encode("utf-8"), status=200
    )
    r.headers["Content-Type"] = "text/plain; charset=invalid-codec-name"
    return r

@encoding_api.route('/no-charset', methods=['GET'])
def no_charset():
    r = Response(
        "Hello, world!", status=200
    )
    r.headers["Content-Type"] = "text/plain"
    return r

@encoding_api.route('/gzip', methods=['GET'])
def gzip_content_encoding():
    r = Response(
        b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\n\xcbH\xcd\xc9\xc9W(\xcf/\xcaI\x01\x00\x85\x11J\r\x0b\x00\x00\x00', status=200
    )
    r.headers["Content-Type"] = "text/plain"
    r.headers['Content-Encoding'] = "gzip"
    return r
