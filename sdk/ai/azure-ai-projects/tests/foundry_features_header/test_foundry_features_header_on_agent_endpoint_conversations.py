# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests unconditional Foundry-Features header behavior on sync `agent_endpoint_conversations` methods.

Unlike the optional-header methods covered in test_foundry_features_header_on_ga_operations.py,
`agent_endpoint_conversations` is wrapped with `_OperationMethodHeaderProxy` directly in
`_patch.py`, so it always sends `Foundry-Features: VoiceAgents=V1Preview` regardless of whether
`allow_preview` was set on the `AIProjectClient` constructor.
"""

from typing import Any, ClassVar, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import HttpTransport
from azure.ai.projects import AIProjectClient

from foundry_features_header_test_base import (
    FAKE_ENDPOINT,
    FakeCredential,
    FoundryFeaturesHeaderTestBase,
    _AGENT_ENDPOINT_CONVERSATIONS_EXPECTED_HEADER_VALUE,
    _AGENT_ENDPOINT_CONVERSATIONS_TEST_CASES,
    _RequestCaptured,
)


class CapturingTransport(HttpTransport):
    """Sync transport that captures the outgoing request and raises _RequestCaptured."""

    def send(self, request: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        raise _RequestCaptured(request)

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __enter__(self) -> "CapturingTransport":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


@pytest.fixture(scope="module")
def client_preview_enabled() -> Iterator[AIProjectClient]:
    with AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        allow_preview=True,
        transport=CapturingTransport(),
    ) as c:
        yield c


@pytest.fixture(scope="module")
def client_preview_disabled() -> Iterator[AIProjectClient]:
    with AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        transport=CapturingTransport(),
    ) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def _print_report_agent_endpoint_conversations() -> Iterator[None]:
    """Print a Foundry-Features report after all sync agent_endpoint_conversations tests finish."""
    yield
    report = TestFoundryFeaturesHeaderOnAgentEndpointConversations._report
    if report:
        max_len = TestFoundryFeaturesHeaderOnAgentEndpointConversations._report_max_label_len
        print(
            "\n\nFoundry-Features header report on agent_endpoint_conversations (sync) — "
            "always present regardless of allow_preview:"
        )
        for label, header_value in sorted(report):
            print(f'{label:<{max_len}}  |  "{header_value}"')


class TestFoundryFeaturesHeaderOnAgentEndpointConversations(FoundryFeaturesHeaderTestBase):
    """Sync tests verifying the Foundry-Features header is always sent on
    `agent_endpoint_conversations` methods, whether or not `allow_preview` was set.
    """

    _report: ClassVar[List[Tuple[str, str]]] = []
    _report_max_label_len: ClassVar[int] = 0

    @staticmethod
    def _capture(call: Any) -> Any:
        """Call *call()* and return the captured HttpRequest."""
        try:
            result = call()
        except _RequestCaptured as exc:
            return exc.request

        try:
            next(iter(result))
        except _RequestCaptured as exc:
            return exc.request
        except StopIteration:
            raise AssertionError("Iterator exhausted without the transport being called") from None

        raise AssertionError("Transport was never called")

    @classmethod
    def _assert_header_present(cls, label: str, call: Any) -> None:
        request = cls._capture(call)
        cls._record_header_assertion(label, request, _AGENT_ENDPOINT_CONVERSATIONS_EXPECTED_HEADER_VALUE)

    @pytest.mark.parametrize("method_name", _AGENT_ENDPOINT_CONVERSATIONS_TEST_CASES)
    def test_foundry_features_header_present_on_agent_endpoint_conversations_when_preview_enabled(
        self,
        client_preview_enabled: AIProjectClient,
        method_name: str,
    ) -> None:
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        self._assert_header_present(f"{method_name} (allow_preview=True)", self._make_fake_call(method))

    @pytest.mark.parametrize("method_name", _AGENT_ENDPOINT_CONVERSATIONS_TEST_CASES)
    def test_foundry_features_header_present_on_agent_endpoint_conversations_when_preview_not_enabled(
        self,
        client_preview_disabled: AIProjectClient,
        method_name: str,
    ) -> None:
        """Even without `allow_preview`, agent_endpoint_conversations methods always send the header."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_disabled, subclient_name)
        method = getattr(sc, method_attr)
        self._assert_header_present(f"{method_name} (allow_preview unset)", self._make_fake_call(method))
