# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async counterpart of test_agent_telephony_protocol.py -- see that module's docstring."""

import inspect
from typing import Any, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

from foundry_features_header_test_base import (
    FAKE_ENDPOINT,
    AsyncFakeCredential,
    FoundryFeaturesHeaderTestBase,
    _RequestCaptured,
)

pytestmark = pytest.mark.asyncio


class CapturingAsyncTransport(AsyncHttpTransport):
    """Async transport that captures the outgoing request and raises _RequestCaptured."""

    async def send(self, request: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        raise _RequestCaptured(request)

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def __aenter__(self) -> "CapturingAsyncTransport":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass


@pytest.fixture(scope="module")
def async_client() -> Iterator[AsyncAIProjectClient]:
    yield AsyncAIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=AsyncFakeCredential(),  # type: ignore[arg-type]
        transport=CapturingAsyncTransport(),
    )


# (method_name, expected HTTP method, expected static URL path -- fake string/required params are
# always rendered as the literal "fake-value" by FoundryFeaturesHeaderTestBase._fake_for_param).
_TELEPHONY_PROTOCOL_CASES: List[Tuple[str, str, str]] = [
    ("create_call_job", "POST", "/agents/fake-value/telephony_call_jobs"),
    ("get_call_job", "GET", "/agents/fake-value/telephony_call_jobs/fake-value"),
    ("cancel_call_job", "POST", "/agents/fake-value/telephony_call_jobs/fake-value:cancel"),
]


class TestAgentTelephonyProtocolAsync(FoundryFeaturesHeaderTestBase):
    """Verify each async `voice_agents.telephony` method builds the correct HTTP method and URL path."""

    @staticmethod
    async def _capture(call: Any) -> Any:
        """Invoke *call()* and return the captured HttpRequest."""
        result = call()

        if inspect.isawaitable(result):
            try:
                await result
            except _RequestCaptured as exc:
                return exc.request
            raise AssertionError("Transport was never called (awaitable completed without raising)")

        ai = result.__aiter__()
        try:
            await ai.__anext__()
        except _RequestCaptured as exc:
            return exc.request
        except StopAsyncIteration:
            raise AssertionError("Iterator exhausted without the transport being called") from None

        raise AssertionError("Transport was never called")

    @pytest.mark.parametrize("method_name,expected_http_method,expected_path", _TELEPHONY_PROTOCOL_CASES)
    async def test_agent_telephony_request_protocol_async(
        self,
        async_client: AsyncAIProjectClient,
        method_name: str,
        expected_http_method: str,
        expected_path: str,
    ) -> None:
        method = getattr(async_client.voice_agents.telephony, method_name)
        request = await self._capture(self._make_fake_call(method))
        assert (
            request.method == expected_http_method
        ), f"{method_name}: expected HTTP method {expected_http_method!r}, got {request.method!r}"
        assert expected_path in request.url, f"{method_name}: expected path {expected_path!r} in URL {request.url!r}"
        assert "Foundry-Features" not in request.headers

    @pytest.mark.parametrize("allow_preview", [False, True])
    @pytest.mark.parametrize("headers", [{}, {"foundry-features": "Custom=V1Preview", "x-test": "preserved"}])
    async def test_conditional_preview_headers(self, allow_preview: bool, headers: dict) -> None:
        async with AsyncAIProjectClient(
            endpoint=FAKE_ENDPOINT,
            credential=AsyncFakeCredential(),
            allow_preview=allow_preview,
            transport=CapturingAsyncTransport(),
        ) as client:
            request = await self._capture(
                lambda: client.voice_agents.telephony.create_call_job(
                    "agent", {}, idempotency_key="test-key", headers=headers.copy()
                )
            )
        expected = headers.get("foundry-features", "VoiceAgents=V1Preview" if allow_preview else None)
        assert request.headers.get("Foundry-Features") == expected
        if headers:
            assert request.headers["x-test"] == "preserved"

    @pytest.mark.parametrize("operation_path", ["agents.create_from_prompt", "voice_agents.conversations.get"])
    async def test_ga_voice_requests_without_preview(
        self, async_client: AsyncAIProjectClient, operation_path: str
    ) -> None:
        operation = async_client
        for attribute in operation_path.split("."):
            operation = getattr(operation, attribute)
        request = await self._capture(self._make_fake_call(operation))
        assert "Foundry-Features" not in request.headers
