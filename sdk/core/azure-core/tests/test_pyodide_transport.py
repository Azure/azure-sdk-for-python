"""Tests that mock the browser layer."""
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

    @pytest.fixture(scope="class", autouse=True)
    def mock_pyodide_module(self):
        """Create a mock for the Pyodide module."""
        mock_pyodide_module = mock.Mock()
        mock_pyodide_module.http.pyfetch = mock.AsyncMock()
        mock_pyodide_module.JsException = type("JsException", (Exception,), {})
        return mock_pyodide_module

    @pytest.fixture(scope="class", autouse=True)
    def transport(self, mock_pyodide_module):
        """Add the mock Pyodide module to `sys.modules` and import our transport."""
        # Use patch so we don't clutter up the `sys.modules` namespace.
        patch_dict = (
            ("pyodide", mock_pyodide_module),
            ("pyodide.http", mock_pyodide_module.http),
        )
        with mock.patch.dict(sys.modules, patch_dict):
            # weird stuff is hppenig here, have to do full import.
            # if I do `from azure.core.pipline.transport import _pyodide`
            # I end up with `_pyodide = 'pyodide'` ???????
            import azure.core.pipeline.transport._pyodide

            yield azure.core.pipeline.transport._pyodide

    @pytest.fixture(scope="class", autouse=True)
    def pipeline(self, transport):
        """Create a pipeline to test."""
        return AsyncPipeline(transport.PyodideTransport(), [AsyncRetryPolicy()])

    @pytest.fixture(scope="class", autouse=True)
    def mock_pyfetch(self, mock_pyodide_module):
        """Utility fixture for less typing."""
        return mock_pyodide_module.http.pyfetch

    def create_mock_response(
        self, body: bytes, headers: dict, status: int, status_text: str
    ) -> mock.Mock:
        """Create a mock response object that mimics `pyodide.http.FetchResponse`"""
        mock_response = mock.Mock()
        if isinstance(body, str):
            body = bytes(body, encoding="utf-8")
        mock_response.body = body
        mock_response.js_response.headers = headers
        mock_response.status = status
        mock_response.status_text = status_text
        mock_response.bytes = mock.AsyncMock(return_value=body)
        return mock_response

    @pytest.mark.asyncio
    async def test_successful_send(self, mock_pyfetch, mock_pyodide_module, pipeline):
        """Test that a successful send returns the correct values."""
        # setup data
        mock_pyfetch.reset_mock()
        method = "POST"
        headers = {"key": "value"}
        data = b"data"
        request = HttpRequest(
            method=method, url=PLACEHOLDER_ENDPOINT, headers=headers, data=data
        )
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
        assert response.body() == response_body
        assert response.status_code == response_status
        assert response.headers == response_headers
        assert response.reason == response_text

        assert not response._is_closed
        await response.close()
        assert response._is_closed

        # Check that the call had the correct arguments.
        mock_pyfetch.assert_called_once()
        args = mock_pyfetch.call_args.args
        kwargs = mock_pyfetch.call_args.kwargs
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

    @pytest.mark.asyncio
    async def test_download_generator(self, transport):
        """Test that the download generator is working correctly."""
        class ReaderReturn(NamedTuple):
            value: bytes
            done: bool

        response_mock = mock.Mock()
        response_mock.block_size = 5
        response_mock.reader.read = mock.AsyncMock()
        response_mock.reader.read.return_value = ReaderReturn(value=b"01", done=False)
        generator = transport.PyodideStreamDownloadGenerator(response=response_mock)

        assert len(await generator.__anext__()) == response_mock.block_size
        assert response_mock.reader.read.call_count == 3
        assert len(await generator.__anext__()) == response_mock.block_size 
        # 5 because there is a leftover byte from the previous `__anext__` call.
        assert response_mock.reader.read.call_count == 5

        response_mock.reader.read.return_value = ReaderReturn(value=None, done=True)
        await generator.__anext__()
        with pytest.raises(StopAsyncIteration):
            await generator.__anext__()