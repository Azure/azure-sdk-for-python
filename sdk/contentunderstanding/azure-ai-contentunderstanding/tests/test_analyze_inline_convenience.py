# pylint: disable=line-too-long,useless-suppression,protected-access
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Offline unit tests for inline analyze convenience wrapping.

``_wrap_inline_response_cls`` is shared by sync and async clients: on HTTP 200
responses whose envelope status is not Succeeded, it raises HttpResponseError
(matching failed completed analyze-LRO behavior).
"""

from __future__ import annotations

import io
import json
from typing import Any, cast, Optional
from unittest.mock import Mock

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
from azure.core.rest import AsyncHttpResponse, HttpRequest, HttpResponse

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding._patch import _wrap_inline_response_cls
from azure.ai.contentunderstanding.aio import (
    ContentUnderstandingClient as AsyncContentUnderstandingClient,
)
from azure.ai.contentunderstanding.models import (
    AnalysisResult,
    AnalysisInput,
    ContentAnalyzerInlineResponse,
    OperationState,
)


_ENDPOINT = "https://sanitized.services.ai.azure.com"
_ANALYZER_ID = "prebuilt-layout"
_BINARY = b"%PDF-1.4 fake"
_URL_INPUT = [AnalysisInput(url="https://example.com/doc.pdf")]


def _pipeline_response() -> Any:
    pipeline_response = Mock()
    pipeline_response.http_response = Mock()
    return pipeline_response


def _inline_response(status: str) -> ContentAnalyzerInlineResponse:
    return ContentAnalyzerInlineResponse(
        {
            "status": status,
            "result": {
                "analyzerId": "prebuilt-layout",
                "apiVersion": "2026-06-01-preview",
                "contents": [],
            },
        }
    )


def _inline_payload(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "result": {
            "analyzerId": _ANALYZER_ID,
            "apiVersion": "2026-06-01-preview",
            "contents": [],
        },
    }


def _mock_response(
    request: HttpRequest,
    payload: dict[str, Any],
    response_type: type[HttpResponse] | type[AsyncHttpResponse],
) -> HttpResponse | AsyncHttpResponse:
    response = Mock(spec=response_type)
    response.status_code = 200
    response.headers = {}
    response.reason = "OK"
    response.content_type = "application/json"
    response.request = request
    response.text = lambda encoding=None: json.dumps(
        payload
    )  # pylint: disable=unused-argument
    response.json.return_value = payload
    return response


class _InlineTransport(HttpTransport):
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload
        self.request_count = 0
        self.response: Optional[HttpResponse] = None

    def send(
        self, request: HttpRequest, **kwargs: Any
    ) -> HttpResponse:  # pylint: disable=unused-argument
        self.request_count += 1
        response = cast(
            HttpResponse, _mock_response(request, self._payload, HttpResponse)
        )
        self.response = response
        return response

    def open(self) -> None:
        return None

    def close(self) -> None:
        return None

    def __enter__(self) -> "_InlineTransport":
        return self

    def __exit__(self, *args: Any) -> None:
        return None


class _AsyncInlineTransport(AsyncHttpTransport):
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload
        self.request_count = 0
        self.response: Optional[AsyncHttpResponse] = None

    async def send(
        self, request: HttpRequest, **kwargs: Any
    ) -> AsyncHttpResponse:  # pylint: disable=unused-argument
        self.request_count += 1
        response = cast(
            AsyncHttpResponse, _mock_response(request, self._payload, AsyncHttpResponse)
        )
        self.response = response
        return response

    async def open(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def __aenter__(self) -> "_AsyncInlineTransport":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None


def _assert_succeeded(result: ContentAnalyzerInlineResponse) -> None:
    assert result.status in (OperationState.SUCCEEDED, "Succeeded")
    assert isinstance(result.result, AnalysisResult)


@pytest.mark.parametrize("method_name", ["analyze_inline", "analyze_binary_inline"])
@pytest.mark.parametrize("status", ["Failed", "Succeeded"])
def test_inline_public_methods_handle_completed_envelopes(
    method_name: str, status: str
) -> None:
    transport = _InlineTransport(_inline_payload(status))
    client = ContentUnderstandingClient(
        endpoint=_ENDPOINT,
        credential=AzureKeyCredential("fake-key"),
        api_version="2026-06-01-preview",
        transport=transport,
    )

    def invoke() -> ContentAnalyzerInlineResponse:
        if method_name == "analyze_inline":
            return client.analyze_inline(analyzer_id=_ANALYZER_ID, inputs=_URL_INPUT)
        return client.analyze_binary_inline(
            analyzer_id=_ANALYZER_ID, binary_input=_BINARY
        )

    if status == "Failed":
        with pytest.raises(HttpResponseError) as exc_info:
            invoke()
        assert exc_info.value.response is transport.response
        assert exc_info.value.response is not None
        assert exc_info.value.response.status_code == 200
    else:
        _assert_succeeded(invoke())

    assert transport.request_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("method_name", ["analyze_inline", "analyze_binary_inline"])
@pytest.mark.parametrize("status", ["Failed", "Succeeded"])
async def test_inline_public_methods_handle_completed_envelopes_async(
    method_name: str, status: str
) -> None:
    transport = _AsyncInlineTransport(_inline_payload(status))
    client = AsyncContentUnderstandingClient(
        endpoint=_ENDPOINT,
        credential=AzureKeyCredential("fake-key"),
        api_version="2026-06-01-preview",
        transport=transport,
    )

    async def invoke() -> ContentAnalyzerInlineResponse:
        if method_name == "analyze_inline":
            return await client.analyze_inline(
                analyzer_id=_ANALYZER_ID, inputs=_URL_INPUT
            )
        return await client.analyze_binary_inline(
            analyzer_id=_ANALYZER_ID, binary_input=_BINARY
        )

    async with client:
        if status == "Failed":
            with pytest.raises(HttpResponseError) as exc_info:
                await invoke()
            assert exc_info.value.response is transport.response
            assert exc_info.value.response is not None
            assert exc_info.value.response.status_code == 200
        else:
            _assert_succeeded(await invoke())

    assert transport.request_count == 1


class TestWrapInlineResponseCls:
    """Unit tests for ``_wrap_inline_response_cls``."""

    def test_wrap_inline_raises_on_failed_status(self) -> None:
        """Failed inline envelope status raises HttpResponseError."""
        cls = _wrap_inline_response_cls()
        pipeline_response = _pipeline_response()
        deserialized = _inline_response("Failed")

        with pytest.raises(HttpResponseError) as exc_info:
            cls(pipeline_response, deserialized, {})

        assert exc_info.value.response is pipeline_response.http_response

    def test_wrap_inline_returns_response_on_succeeded(self) -> None:
        """Succeeded inline envelope returns ContentAnalyzerInlineResponse."""
        cls = _wrap_inline_response_cls()
        pipeline_response = _pipeline_response()
        deserialized = _inline_response("Succeeded")

        result = cls(pipeline_response, deserialized, {})

        assert result is deserialized
        assert result.status in (OperationState.SUCCEEDED, "Succeeded")
        assert isinstance(result.result, AnalysisResult)

    def test_wrap_inline_composes_user_cls(self) -> None:
        """Optional user cls is invoked after the Succeeded status check."""
        user_called: dict[str, Any] = {}

        def user_cls(
            pipeline_response: Any, deserialized: Any, response_headers: Any
        ) -> Any:
            user_called["pipeline_response"] = pipeline_response
            user_called["deserialized"] = deserialized
            user_called["response_headers"] = response_headers
            return ("user-wrapped", deserialized)

        cls = _wrap_inline_response_cls(user_cls)
        pipeline_response = _pipeline_response()
        deserialized = _inline_response("Succeeded")
        headers = {"x-ms-request-id": "req-1"}

        result = cls(pipeline_response, deserialized, headers)

        assert result == ("user-wrapped", deserialized)
        assert user_called["pipeline_response"] is pipeline_response
        assert user_called["deserialized"] is deserialized
        assert user_called["response_headers"] == headers

    def test_wrap_inline_user_cls_not_called_on_failed(self) -> None:
        """Failed status raises before invoking a user cls."""

        def user_cls(
            pipeline_response: Any, deserialized: Any, response_headers: Any
        ) -> Any:
            raise AssertionError("user cls should not run on Failed status")

        cls = _wrap_inline_response_cls(user_cls)
        with pytest.raises(HttpResponseError):
            cls(_pipeline_response(), _inline_response("Failed"), {})


class TestAnalyzeInlineContentType:
    """analyze_inline must normalize content_type=None like begin_analyze."""

    def test_analyze_inline_normalizes_none_content_type(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from azure.ai.contentunderstanding import ContentUnderstandingClient
        from azure.ai.contentunderstanding._client import (
            ContentUnderstandingClient as GeneratedClient,
        )
        from azure.ai.contentunderstanding.models import AnalysisInput
        from azure.core.credentials import AzureKeyCredential

        captured: dict[str, Any] = {}

        def fake_analyze_inline(_self: Any, **kwargs: Any) -> None:
            captured.update(kwargs)
            raise RuntimeError("stop")

        monkeypatch.setattr(GeneratedClient, "analyze_inline", fake_analyze_inline)

        client = ContentUnderstandingClient(
            endpoint="https://sanitized.services.ai.azure.com",
            credential=AzureKeyCredential("fake-key"),
            api_version="2026-06-01-preview",
        )
        with pytest.raises(RuntimeError, match="stop"):
            client.analyze_inline(
                analyzer_id="prebuilt-layout",
                inputs=[AnalysisInput(url="https://example.com/doc.pdf")],
                content_type=None,
            )
        assert captured["content_type"] == "application/json"

    @pytest.mark.asyncio
    async def test_analyze_inline_async_normalizes_none_content_type(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
        from azure.ai.contentunderstanding.aio._client import (
            ContentUnderstandingClient as GeneratedClient,
        )
        from azure.ai.contentunderstanding.models import AnalysisInput
        from azure.core.credentials import AzureKeyCredential

        captured: dict[str, Any] = {}

        async def fake_analyze_inline(_self: Any, **kwargs: Any) -> None:
            captured.update(kwargs)
            raise RuntimeError("stop")

        monkeypatch.setattr(GeneratedClient, "analyze_inline", fake_analyze_inline)

        client = ContentUnderstandingClient(
            endpoint="https://sanitized.services.ai.azure.com",
            credential=AzureKeyCredential("fake-key"),
            api_version="2026-06-01-preview",
        )
        async with client:
            with pytest.raises(RuntimeError, match="stop"):
                await client.analyze_inline(
                    analyzer_id="prebuilt-layout",
                    inputs=[AnalysisInput(url="https://example.com/doc.pdf")],
                    content_type=None,
                )
        assert captured["content_type"] == "application/json"


class TestAnalyzeInlineBodyForms:
    """analyze_inline accepts a raw ``body=`` (JSON dict or IO[bytes]), matching begin_analyze."""

    def test_analyze_inline_json_body_passthrough(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from azure.ai.contentunderstanding import ContentUnderstandingClient
        from azure.ai.contentunderstanding._client import (
            ContentUnderstandingClient as GeneratedClient,
        )
        from azure.core.credentials import AzureKeyCredential

        captured: dict[str, Any] = {}

        def fake_analyze_inline(_self: Any, **kwargs: Any) -> None:
            captured.update(kwargs)
            raise RuntimeError("stop")

        monkeypatch.setattr(GeneratedClient, "analyze_inline", fake_analyze_inline)

        client = ContentUnderstandingClient(
            endpoint="https://sanitized.services.ai.azure.com",
            credential=AzureKeyCredential("fake-key"),
            api_version="2026-06-01-preview",
        )
        body = {"inputs": [{"url": "https://example.com/doc.pdf"}]}
        with pytest.raises(RuntimeError, match="stop"):
            client.analyze_inline(analyzer_id=_ANALYZER_ID, body=body)

        assert captured["body"] == body
        assert captured["content_type"] == "application/json"

    def test_analyze_inline_binary_body_passthrough(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from azure.ai.contentunderstanding import ContentUnderstandingClient
        from azure.ai.contentunderstanding._client import (
            ContentUnderstandingClient as GeneratedClient,
        )
        from azure.core.credentials import AzureKeyCredential

        captured: dict[str, Any] = {}

        def fake_analyze_inline(_self: Any, **kwargs: Any) -> None:
            captured.update(kwargs)
            raise RuntimeError("stop")

        monkeypatch.setattr(GeneratedClient, "analyze_inline", fake_analyze_inline)

        client = ContentUnderstandingClient(
            endpoint="https://sanitized.services.ai.azure.com",
            credential=AzureKeyCredential("fake-key"),
            api_version="2026-06-01-preview",
        )
        stream = io.BytesIO(_BINARY)
        with pytest.raises(RuntimeError, match="stop"):
            client.analyze_inline(analyzer_id=_ANALYZER_ID, body=stream)

        assert captured["body"] is stream

    @pytest.mark.asyncio
    async def test_analyze_inline_async_json_body_passthrough(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
        from azure.ai.contentunderstanding.aio._client import (
            ContentUnderstandingClient as GeneratedClient,
        )
        from azure.core.credentials import AzureKeyCredential

        captured: dict[str, Any] = {}

        async def fake_analyze_inline(_self: Any, **kwargs: Any) -> None:
            captured.update(kwargs)
            raise RuntimeError("stop")

        monkeypatch.setattr(GeneratedClient, "analyze_inline", fake_analyze_inline)

        client = ContentUnderstandingClient(
            endpoint="https://sanitized.services.ai.azure.com",
            credential=AzureKeyCredential("fake-key"),
            api_version="2026-06-01-preview",
        )
        body = {"inputs": [{"url": "https://example.com/doc.pdf"}]}
        async with client:
            with pytest.raises(RuntimeError, match="stop"):
                await client.analyze_inline(analyzer_id=_ANALYZER_ID, body=body)

        assert captured["body"] == body
        assert captured["content_type"] == "application/json"

    @pytest.mark.asyncio
    async def test_analyze_inline_async_binary_body_passthrough(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
        from azure.ai.contentunderstanding.aio._client import (
            ContentUnderstandingClient as GeneratedClient,
        )
        from azure.core.credentials import AzureKeyCredential

        captured: dict[str, Any] = {}

        async def fake_analyze_inline(_self: Any, **kwargs: Any) -> None:
            captured.update(kwargs)
            raise RuntimeError("stop")

        monkeypatch.setattr(GeneratedClient, "analyze_inline", fake_analyze_inline)

        client = ContentUnderstandingClient(
            endpoint="https://sanitized.services.ai.azure.com",
            credential=AzureKeyCredential("fake-key"),
            api_version="2026-06-01-preview",
        )
        stream = io.BytesIO(_BINARY)
        async with client:
            with pytest.raises(RuntimeError, match="stop"):
                await client.analyze_inline(analyzer_id=_ANALYZER_ID, body=stream)

        assert captured["body"] is stream
