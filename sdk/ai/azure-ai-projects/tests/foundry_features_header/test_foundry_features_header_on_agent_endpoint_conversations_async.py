# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests unconditional Foundry-Features header behavior on async `agent_endpoint_conversations` methods.

Unlike the optional-header methods covered in test_foundry_features_header_on_ga_operations_async.py,
`agent_endpoint_conversations` is wrapped with `_OperationMethodHeaderProxy` directly in
`aio/_patch.py`, so it always sends `Foundry-Features: VoiceAgents=V1Preview` regardless of whether
`allow_preview` was set on the `AIProjectClient` constructor.
"""

import inspect
from typing import Any, ClassVar, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

from foundry_features_header_test_base import (
    FAKE_ENDPOINT,
    AsyncFakeCredential,
    FoundryFeaturesHeaderTestBase,
    _AGENT_ENDPOINT_CONVERSATIONS_EXPECTED_HEADER_VALUE,
    _AGENT_ENDPOINT_CONVERSATIONS_TEST_CASES,
    _RequestCaptured,
)


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
def async_client_preview_enabled() -> Iterator[AsyncAIProjectClient]:
    yield AsyncAIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=AsyncFakeCredential(),  # type: ignore[arg-type]
        allow_preview=True,
        transport=CapturingAsyncTransport(),
    )


@pytest.fixture(scope="module")
def async_client_preview_disabled() -> Iterator[AsyncAIProjectClient]:
    yield AsyncAIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=AsyncFakeCredential(),  # type: ignore[arg-type]
        transport=CapturingAsyncTransport(),
    )


@pytest.fixture(scope="module", autouse=True)
def _print_report_agent_endpoint_conversations_async() -> Iterator[None]:
    """Print a Foundry-Features report after all async agent_endpoint_conversations tests finish."""
    yield
    report = TestFoundryFeaturesHeaderOnAgentEndpointConversationsAsync._report
    if report:
        max_len = TestFoundryFeaturesHeaderOnAgentEndpointConversationsAsync._report_max_label_len
        print(
            "\n\nFoundry-Features header report on agent_endpoint_conversations (async) — "
            "always present regardless of allow_preview:"
        )
        for label, header_value in sorted(report):
            print(f'{label:<{max_len}}  |  "{header_value}"')


class TestFoundryFeaturesHeaderOnAgentEndpointConversationsAsync(FoundryFeaturesHeaderTestBase):
    """Async tests verifying the Foundry-Features header is always sent on
    `agent_endpoint_conversations` methods, whether or not `allow_preview` was set.
    """

    _report: ClassVar[List[Tuple[str, str]]] = []
    _report_max_label_len: ClassVar[int] = 0

    @staticmethod
    async def _capture_async(call: Any) -> Any:
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

    @classmethod
    async def _assert_header_present_async(cls, label: str, call: Any) -> None:
        request = await cls._capture_async(call)
        cls._record_header_assertion(label, request, _AGENT_ENDPOINT_CONVERSATIONS_EXPECTED_HEADER_VALUE)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name", _AGENT_ENDPOINT_CONVERSATIONS_TEST_CASES)
    async def test_foundry_features_header_present_on_agent_endpoint_conversations_when_preview_enabled_async(
        self,
        async_client_preview_enabled: AsyncAIProjectClient,
        method_name: str,
    ) -> None:
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(async_client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        await self._assert_header_present_async(
            f"{method_name} (allow_preview=True)", self._make_fake_call(method)
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name", _AGENT_ENDPOINT_CONVERSATIONS_TEST_CASES)
    async def test_foundry_features_header_present_on_agent_endpoint_conversations_when_preview_not_enabled_async(
        self,
        async_client_preview_disabled: AsyncAIProjectClient,
        method_name: str,
    ) -> None:
        """Even without `allow_preview`, agent_endpoint_conversations methods always send the header."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(async_client_preview_disabled, subclient_name)
        method = getattr(sc, method_attr)
        await self._assert_header_present_async(
            f"{method_name} (allow_preview unset)", self._make_fake_call(method)
        )
