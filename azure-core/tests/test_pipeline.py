# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------

import json
import requests
import datetime
from enum import Enum
import unittest

try:
    from unittest import mock
except ImportError:
    import mock
import xml.etree.ElementTree as ET
import sys

import pytest

from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies.base import SansIOHTTPPolicy
from azure.core.pipeline.transport import (
    HttpRequest,
    HttpTransport
    # ClientRawResponse, TODO: not yet copied from msrest
)

from azure.core.configuration import Configuration


def test_sans_io_exception():
    class BrokenSender(HttpTransport):
        def send(self, request, **config):
            raise ValueError("Broken")

        def __exit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None

    pipeline = Pipeline(BrokenSender(), [SansIOHTTPPolicy()])

    req = HttpRequest("GET", "/")
    with pytest.raises(ValueError):
        pipeline.run(req)

    class SwapExec(SansIOHTTPPolicy):
        def on_exception(self, requests, **kwargs):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise NotImplementedError(exc_value)

    pipeline = Pipeline(BrokenSender(), [SwapExec()])
    with pytest.raises(NotImplementedError):
        pipeline.run(req)


class TestClientRequest(unittest.TestCase):
    def test_request_json(self):

        request = HttpRequest("GET", "/")
        data = "Lots of dataaaa"
        request.set_json_body(data)

        self.assertEqual(request.data, json.dumps(data))
        self.assertEqual(request.headers.get("Content-Length"), "17")

    def test_request_data(self):

        request = HttpRequest("GET", "/")
        data = "Lots of dataaaa"
        request.set_bytes_body(data)

        self.assertEqual(request.data, data)
        self.assertEqual(request.headers.get("Content-Length"), "15")

    def test_request_xml(self):
        request = HttpRequest("GET", "/")
        data = ET.Element("root")
        request.set_xml_body(data)

        assert request.data == b"<?xml version='1.0' encoding='utf8'?>\n<root />"

    def test_request_url_with_params(self):

        request = HttpRequest("GET", "/")
        request.url = "a/b/c?t=y"
        request.format_parameters({"g": "h"})

        self.assertIn(request.url, ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"])


if __name__ == "__main__":
    unittest.main()
