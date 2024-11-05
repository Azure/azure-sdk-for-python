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
"""Tests that mock the browser layer."""
import asyncio
import sys
from typing import NamedTuple
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline._base_async import AsyncPipeline
from azure.core.pipeline.policies._retry_async import AsyncRetryPolicy
from azure.core.rest import HttpRequest

PLACEHOLDER_ENDPOINT = "https://my-resource-group.cognitiveservices.azure.com/"


class TestPyodideTransportClass:
    """Unittest for the Pyodide transport."""

    @pytest.fixture()
    def mock_pyodide_module(self):
        """Create a mock for the Pyodide module."""
        mock_pyodide_module = mock.Mock()
        mock_pyodide_module.http.pyfetch = mock.Mock()
        mock_pyodide_module.JsException = type("JsException", (Exception,), {})
        return mock_pyodide_module

    @pytest.fixture()
    def mock_js_module(self):
        """Mock the `js` module"""
        return mock.Mock()

    @pytest.fixture()
    def transport(self, mock_pyodide_module, mock_js_module):
        """Add the mock Pyodide module to `sys.modules` and import our transport."""
        import azure.core.experimental.transport._pyodide

        with mock.patch.multiple(
            "azure.core.experimental.transport._pyodide",
            js=mock_js_module,
            pyfetch=mock_pyodide_module.http.pyfetch,
            JsException=mock_pyodide_module.JsException,
        ):

            yield azure.core.experimental.transport._pyodide

    @pytest.fixture()
    def pipeline(self, transport):
        """Create a pipeline to test."""
        return AsyncPipeline(transport.PyodideTransport(), [AsyncRetryPolicy()])

    @pytest.fixture()
    def mock_pyfetch(self, mock_pyodide_module):
        """Utility fixture for less typing."""
        return mock_pyodide_module.http.pyfetch

    def create_mock_response(self, body: bytes, headers: dict, status: int, status_text: str) -> mock.Mock:
        """Create a mock response object that mimics `pyodide.http.FetchResponse`"""
        mock_response = mock.Mock()
        mock_response.body = body
        mock_response.js_response.headers = headers
        mock_response.status = status
        mock_response.status_text = status_text
        bytes_promise = asyncio.Future()
        bytes_promise.set_result(body)
        mock_response.bytes = mock.Mock()
        mock_response.bytes.return_value = bytes_promise
        mock_response.clone.return_value = mock_response

        response_promise = asyncio.Future()
        response_promise.set_result(mock_response)
        return response_promise

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.version_info >= (3, 13), reason="cgi is removed in Python 3.13")
    async def test_successful_send(self, mock_pyfetch, mock_pyodide_module, pipeline):
        """Test that a successful send returns the correct values."""
        # setup data
        mock_pyfetch.reset_mock()
        method = "POST"
        headers = {"key": "value"}
        data = b"data"
        request = HttpRequest(method=method, url=PLACEHOLDER_ENDPOINT, headers=headers, data=data)
        response_body = b"0123"
        response_headers = {"header": "value"}
        response_status = 200
        response_text = "OK"
        mock_response = self.create_mock_response(
            body=response_body,
            headers=response_headers,
            status=response_status,
            status_text=response_text,
        )
        mock_pyodide_module.http.pyfetch.return_value = mock_response
        response = (await pipeline.run(request=request)).http_response
        # Check that the pipeline processed the data correctly.
        await response.load_body()
        assert response.body() == response_body
        assert response.status_code == response_status
        assert response.headers == response_headers
        assert response.reason == response_text

        assert not response._is_closed
        await response.close()
        assert response._is_closed

        # Check that the call had the correct arguments.
        mock_pyfetch.assert_called_once()
        args = mock_pyfetch.call_args[0]
        kwargs = mock_pyfetch.call_args[1]
        assert len(args) == 1
        assert args[0] == PLACEHOLDER_ENDPOINT
        assert kwargs["method"] == method
        assert kwargs["body"] == data
        assert not kwargs["allow_redirects"]
        assert kwargs["headers"]["key"] == "value"
        assert kwargs["headers"]["Content-Length"] == str(len(data))
        assert kwargs["verify"]
        assert kwargs["cert"] is None
        assert not kwargs["files"]

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.version_info >= (3, 13), reason="cgi is removed in Python 3.13")
    async def test_unsuccessful_send(self, mock_pyfetch, mock_pyodide_module, pipeline):
        """Test that the pipeline is failing correctly."""
        mock_pyfetch.reset_mock()
        mock_pyfetch.side_effect = mock_pyodide_module.JsException
        retry_total = 3
        request = HttpRequest(method="GET", url=PLACEHOLDER_ENDPOINT)
        with pytest.raises(HttpResponseError):
            await pipeline.run(request)
        # 3 retries plus the original request.
        assert mock_pyfetch.call_count == retry_total + 1

    @pytest.mark.skipif(sys.version_info >= (3, 13), reason="cgi is removed in Python 3.13")
    def test_valid_import(self, transport):
        """Test that we can import Pyodide classes from `azure.core.pipeline.transport`
        Adding the transport fixture will mock the Pyodide modules in `sys.modules`.
        """
        # Use patch so we don't clutter up the `sys.modules` namespace.
        import azure.core.experimental.transport as transport

        assert transport.PyodideTransport
