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
        allow_preview=True,
        transport=CapturingAsyncTransport(),
    )


# (method_name, expected HTTP method, expected static URL path -- fake string/required params are
# always rendered as the literal "fake-value" by FoundryFeaturesHeaderTestBase._fake_for_param).
_TELEPHONY_PROTOCOL_CASES: List[Tuple[str, str, str]] = [
    ("create_telephony_call_job", "POST", "/agents/fake-value/telephony/call_jobs"),
    ("get_telephony_call_job", "GET", "/agents/fake-value/telephony/call_jobs/fake-value"),
    ("cancel_telephony_call_job", "POST", "/agents/fake-value/telephony/call_jobs/fake-value:cancel"),
    ("create_telephony_campaign", "POST", "/agents/fake-value/telephony/campaigns"),
    ("get_telephony_campaign", "GET", "/agents/fake-value/telephony/campaigns/fake-value"),
    (
        "begin_import_telephony_campaign_recipients",
        "POST",
        "/agents/fake-value/telephony/campaigns/fake-value/recipients:import",
    ),
    (
        "get_telephony_campaign_recipient_import",
        "GET",
        "/agents/fake-value/telephony/campaigns/fake-value/recipient_imports/fake-value",
    ),
    ("begin_validate_telephony_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:validate"),
    ("begin_publish_telephony_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:publish"),
    ("pause_telephony_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:pause"),
    ("resume_telephony_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:resume"),
    ("cancel_telephony_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:cancel"),
    ("get_telephony_operation", "GET", "/agents/fake-value/telephony/operations/fake-value"),
]


class TestAgentTelephonyProtocolAsync(FoundryFeaturesHeaderTestBase):
    """Verify each async `agent_telephony` method builds the correct HTTP method and URL path."""

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
        method = getattr(async_client.agent_telephony, method_name)
        request = await self._capture(self._make_fake_call(method))
        assert (
            request.method == expected_http_method
        ), f"{method_name}: expected HTTP method {expected_http_method!r}, got {request.method!r}"
        assert expected_path in request.url, f"{method_name}: expected path {expected_path!r} in URL {request.url!r}"
