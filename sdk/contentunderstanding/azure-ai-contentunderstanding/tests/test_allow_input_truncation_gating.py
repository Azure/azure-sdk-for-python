# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Offline tests for allow_input_truncation API-version gating.

Preview-only query parameter must raise ValueError on GA clients for JSON and
binary LRO analyze paths. Passing the kwarg through generated ops (not params
injection) is required so api_version_validation sees it.

Inline analyze methods are themselves preview-only (method_added_on), so on GA
they fail before param gating — covered separately.
"""

from __future__ import annotations

from typing import Any, cast, Optional
from unittest.mock import Mock

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
from azure.core.rest import AsyncHttpResponse, HttpRequest, HttpResponse

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.aio import (
    ContentUnderstandingClient as AsyncContentUnderstandingClient,
)
from azure.ai.contentunderstanding.models import AnalysisInput
from testpreparer import GA_API_VERSION, PREVIEW_API_VERSION

_ENDPOINT = "https://sanitized.services.ai.azure.com"
_ANALYZER_ID = "prebuilt-layout"
_BINARY = b"%PDF-1.4 fake"
_URL_INPUT = [AnalysisInput(url="https://example.com/doc.pdf")]


class _CaptureTransport(HttpTransport):
    """Records the outbound request URL then returns a minimal error response."""

    def __init__(self) -> None:
        self.last_url: Optional[str] = None

    def send(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:  # noqa: ARG002
        self.last_url = str(getattr(request, "url", request))
        response = Mock(spec=HttpResponse)
        response.status_code = 400
        response.headers = {}
        response.reason = "Bad Request"
        response.content_type = "application/json"
        response.text = lambda encoding=None: (
            '{"error":{"code":"InvalidRequest","message":"test"}}'
        )  # noqa: ARG005
        response.content = response.text().encode("utf-8")
        response.body = lambda: response.content
        response.stream_download = Mock(return_value=iter(()))
        response.request = request
        return response  # type: ignore[return-value]

    def open(self) -> None:
        return None

    def close(self) -> None:
        return None

    def __enter__(self) -> "_CaptureTransport":
        return self

    def __exit__(self, *args: Any) -> None:
        return None


class _AsyncCaptureTransport(AsyncHttpTransport):
    """Async transport that records the request URL and returns an error response."""

    def __init__(self) -> None:
        self.last_url: Optional[str] = None

    async def send(
        self, request: HttpRequest, **kwargs: Any
    ) -> AsyncHttpResponse:  # noqa: ARG002
        self.last_url = str(getattr(request, "url", request))
        response = Mock(spec=AsyncHttpResponse)
        response.status_code = 400
        response.headers = {}
        response.reason = "Bad Request"
        response.content_type = "application/json"
        response.text = lambda encoding=None: (
            '{"error":{"code":"InvalidRequest","message":"test"}}'
        )  # noqa: ARG005
        response.content = response.text().encode("utf-8")
        response.body = lambda: response.content
        response.stream_download = Mock(return_value=iter(()))
        response.request = request
        return cast(AsyncHttpResponse, response)

    async def open(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def __aenter__(self) -> "_AsyncCaptureTransport":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None


def _ga_client(**kwargs: Any) -> ContentUnderstandingClient:
    return ContentUnderstandingClient(
        endpoint=_ENDPOINT,
        credential=AzureKeyCredential("fake-key"),
        api_version=GA_API_VERSION,
        **kwargs,
    )


def _preview_client(**kwargs: Any) -> ContentUnderstandingClient:
    return ContentUnderstandingClient(
        endpoint=_ENDPOINT,
        credential=AzureKeyCredential("fake-key"),
        api_version=PREVIEW_API_VERSION,
        **kwargs,
    )


def _ga_async_client(**kwargs: Any) -> AsyncContentUnderstandingClient:
    return AsyncContentUnderstandingClient(
        endpoint=_ENDPOINT,
        credential=AzureKeyCredential("fake-key"),
        api_version=GA_API_VERSION,
        **kwargs,
    )


def _preview_async_client(**kwargs: Any) -> AsyncContentUnderstandingClient:
    return AsyncContentUnderstandingClient(
        endpoint=_ENDPOINT,
        credential=AzureKeyCredential("fake-key"),
        api_version=PREVIEW_API_VERSION,
        **kwargs,
    )


class TestAllowInputTruncationGating:
    """GA clients must reject allow_input_truncation; preview clients must accept it."""

    def test_ga_begin_analyze_rejects_allow_input_truncation(self) -> None:
        client = _ga_client()
        with pytest.raises(ValueError, match="allow_input_truncation"):
            client.begin_analyze(
                analyzer_id=_ANALYZER_ID,
                inputs=_URL_INPUT,
                allow_input_truncation=True,
            )

    def test_ga_begin_analyze_binary_rejects_allow_input_truncation(self) -> None:
        """Regression: binary must not bypass gating via params injection."""
        client = _ga_client()
        with pytest.raises(ValueError, match="allow_input_truncation"):
            client.begin_analyze_binary(
                analyzer_id=_ANALYZER_ID,
                binary_input=_BINARY,
                allow_input_truncation=True,
            )

    def test_ga_analyze_inline_unavailable(self) -> None:
        """Inline APIs are method-gated on preview; GA fails before param checks."""
        client = _ga_client()
        with pytest.raises(ValueError, match="analyze_inline"):
            client.analyze_inline(
                analyzer_id=_ANALYZER_ID,
                inputs=_URL_INPUT,
                allow_input_truncation=True,
            )

    def test_ga_analyze_binary_inline_unavailable(self) -> None:
        client = _ga_client()
        with pytest.raises(ValueError, match="analyze_binary_inline"):
            client.analyze_binary_inline(
                analyzer_id=_ANALYZER_ID,
                binary_input=_BINARY,
                allow_input_truncation=True,
            )

    def test_ga_omitted_allow_input_truncation_does_not_raise_value_error(self) -> None:
        """Omitting the preview kwarg on GA must not trip api_version_validation."""
        transport = _CaptureTransport()
        client = _ga_client(transport=transport)
        with pytest.raises(Exception) as exc_info:
            client.begin_analyze_binary(analyzer_id=_ANALYZER_ID, binary_input=_BINARY)
        assert not isinstance(
            exc_info.value, ValueError
        ) or "allow_input_truncation" not in str(exc_info.value)

    def test_preview_begin_analyze_sends_allow_input_truncation_query(self) -> None:
        transport = _CaptureTransport()
        client = _preview_client(transport=transport)
        with pytest.raises(Exception) as exc_info:
            client.begin_analyze(
                analyzer_id=_ANALYZER_ID,
                inputs=_URL_INPUT,
                allow_input_truncation=True,
            )
        assert not isinstance(exc_info.value, ValueError)
        assert transport.last_url is not None
        assert "allowInputTruncation=true" in transport.last_url

    def test_preview_begin_analyze_false_sends_allow_input_truncation_query(
        self,
    ) -> None:
        transport = _CaptureTransport()
        client = _preview_client(transport=transport)
        with pytest.raises(Exception) as exc_info:
            client.begin_analyze(
                analyzer_id=_ANALYZER_ID,
                inputs=_URL_INPUT,
                allow_input_truncation=False,
            )
        assert not isinstance(exc_info.value, ValueError)
        assert transport.last_url is not None
        assert "allowInputTruncation=false" in transport.last_url

    def test_preview_begin_analyze_binary_sends_allow_input_truncation_query(
        self,
    ) -> None:
        transport = _CaptureTransport()
        client = _preview_client(transport=transport)
        with pytest.raises(Exception) as exc_info:
            client.begin_analyze_binary(
                analyzer_id=_ANALYZER_ID,
                binary_input=_BINARY,
                allow_input_truncation=True,
            )
        assert not isinstance(exc_info.value, ValueError)
        assert transport.last_url is not None
        assert "allowInputTruncation=true" in transport.last_url

    def test_preview_analyze_binary_inline_sends_allow_input_truncation_query(
        self,
    ) -> None:
        transport = _CaptureTransport()
        client = _preview_client(transport=transport)
        with pytest.raises(Exception) as exc_info:
            client.analyze_binary_inline(
                analyzer_id=_ANALYZER_ID,
                binary_input=_BINARY,
                allow_input_truncation=True,
            )
        assert not isinstance(exc_info.value, ValueError)
        assert transport.last_url is not None
        assert "allowInputTruncation=true" in transport.last_url


class TestAllowInputTruncationGatingAsync:
    """Async coverage mirrors every sync gating and query-forwarding scenario."""

    @pytest.mark.asyncio
    async def test_ga_begin_analyze_rejects_allow_input_truncation(self) -> None:
        client = _ga_async_client()
        async with client:
            with pytest.raises(ValueError, match="allow_input_truncation"):
                await client.begin_analyze(
                    analyzer_id=_ANALYZER_ID,
                    inputs=_URL_INPUT,
                    allow_input_truncation=True,
                )

    @pytest.mark.asyncio
    async def test_ga_begin_analyze_binary_rejects_allow_input_truncation(self) -> None:
        client = _ga_async_client()
        async with client:
            with pytest.raises(ValueError, match="allow_input_truncation"):
                await client.begin_analyze_binary(
                    analyzer_id=_ANALYZER_ID,
                    binary_input=_BINARY,
                    allow_input_truncation=True,
                )

    @pytest.mark.asyncio
    async def test_ga_analyze_inline_unavailable(self) -> None:
        client = _ga_async_client()
        async with client:
            with pytest.raises(ValueError, match="analyze_inline"):
                await client.analyze_inline(
                    analyzer_id=_ANALYZER_ID,
                    inputs=_URL_INPUT,
                    allow_input_truncation=True,
                )

    @pytest.mark.asyncio
    async def test_ga_analyze_binary_inline_unavailable(self) -> None:
        client = _ga_async_client()
        async with client:
            with pytest.raises(ValueError, match="analyze_binary_inline"):
                await client.analyze_binary_inline(
                    analyzer_id=_ANALYZER_ID,
                    binary_input=_BINARY,
                    allow_input_truncation=True,
                )

    @pytest.mark.asyncio
    async def test_ga_omitted_allow_input_truncation_does_not_raise_value_error(
        self,
    ) -> None:
        transport = _AsyncCaptureTransport()
        client = _ga_async_client(transport=transport)
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.begin_analyze_binary(
                    analyzer_id=_ANALYZER_ID, binary_input=_BINARY
                )
        assert not isinstance(
            exc_info.value, ValueError
        ) or "allow_input_truncation" not in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_preview_begin_analyze_sends_allow_input_truncation_query(
        self,
    ) -> None:
        transport = _AsyncCaptureTransport()
        client = _preview_async_client(transport=transport)
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.begin_analyze(
                    analyzer_id=_ANALYZER_ID,
                    inputs=_URL_INPUT,
                    allow_input_truncation=True,
                )
        assert not isinstance(exc_info.value, ValueError)
        assert transport.last_url is not None
        assert "allowInputTruncation=true" in transport.last_url

    @pytest.mark.asyncio
    async def test_preview_begin_analyze_false_sends_allow_input_truncation_query(
        self,
    ) -> None:
        transport = _AsyncCaptureTransport()
        client = _preview_async_client(transport=transport)
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.begin_analyze(
                    analyzer_id=_ANALYZER_ID,
                    inputs=_URL_INPUT,
                    allow_input_truncation=False,
                )
        assert not isinstance(exc_info.value, ValueError)
        assert transport.last_url is not None
        assert "allowInputTruncation=false" in transport.last_url

    @pytest.mark.asyncio
    async def test_preview_begin_analyze_binary_sends_allow_input_truncation_query(
        self,
    ) -> None:
        transport = _AsyncCaptureTransport()
        client = _preview_async_client(transport=transport)
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.begin_analyze_binary(
                    analyzer_id=_ANALYZER_ID,
                    binary_input=_BINARY,
                    allow_input_truncation=True,
                )
        assert not isinstance(exc_info.value, ValueError)
        assert transport.last_url is not None
        assert "allowInputTruncation=true" in transport.last_url

    @pytest.mark.asyncio
    async def test_preview_analyze_binary_inline_sends_allow_input_truncation_query(
        self,
    ) -> None:
        transport = _AsyncCaptureTransport()
        client = _preview_async_client(transport=transport)
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.analyze_binary_inline(
                    analyzer_id=_ANALYZER_ID,
                    binary_input=_BINARY,
                    allow_input_truncation=True,
                )
        assert not isinstance(exc_info.value, ValueError)
        assert transport.last_url is not None
        assert "allowInputTruncation=true" in transport.last_url
