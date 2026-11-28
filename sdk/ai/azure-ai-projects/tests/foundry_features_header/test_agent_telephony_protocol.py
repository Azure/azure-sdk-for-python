# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Mocked protocol-level tests for the `voice_agents.telephony` (batch 2) call-job
operation group, covering request construction (HTTP method + URL path) without depending on the
live test service's currently-unavailable API-version support for these routes (see
`tests/agents/test_voice_agent_telephony_call_job.py`, whose recorded tests are all skipped for
that reason).

Uses the same request-capturing-transport technique as
`tests/foundry_features_header/test_foundry_features_header_on_ga_operations.py`: a transport
that raises as soon as a request is about to be sent, so the generated request builder's URL/method
construction is exercised end-to-end (through the real client, real serialization, and the real
pipeline) without any network I/O or a live/recorded backend.
"""

from typing import Any, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import HttpTransport
from azure.ai.projects import AIProjectClient

from foundry_features_header_test_base import (
    CONDITIONAL_VOICE_TELEPHONY_METHODS,
    FAKE_ENDPOINT,
    FakeCredential,
    FoundryFeaturesHeaderTestBase,
    GA_VOICE_OPERATION_PATHS,
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
def client() -> Iterator[AIProjectClient]:
    with AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        transport=CapturingTransport(),
    ) as c:
        yield c


# (method_name, expected HTTP method, expected static URL path -- fake string/required params are
# always rendered as the literal "fake-value" by FoundryFeaturesHeaderTestBase._fake_for_param).
_TELEPHONY_PROTOCOL_CASES: List[Tuple[str, str, str]] = [
    ("create_call_job", "POST", "/agents/fake-value/telephony_call_jobs"),
    ("get_call_job", "GET", "/agents/fake-value/telephony_call_jobs/fake-value"),
    ("cancel_call_job", "POST", "/agents/fake-value/telephony_call_jobs/fake-value:cancel"),
]


class TestAgentTelephonyProtocol(FoundryFeaturesHeaderTestBase):
    """Verify each `voice_agents.telephony` method builds the correct HTTP method and URL path."""

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

    @pytest.mark.parametrize("method_name,expected_http_method,expected_path", _TELEPHONY_PROTOCOL_CASES)
    def test_agent_telephony_request_protocol(
        self,
        client: AIProjectClient,
        method_name: str,
        expected_http_method: str,
        expected_path: str,
    ) -> None:
        method = getattr(client.voice_agents.telephony, method_name)
        request = self._capture(self._make_fake_call(method))
        assert (
            request.method == expected_http_method
        ), f"{method_name}: expected HTTP method {expected_http_method!r}, got {request.method!r}"
        assert expected_path in request.url, f"{method_name}: expected path {expected_path!r} in URL {request.url!r}"
        assert "Foundry-Features" not in request.headers

    @pytest.mark.parametrize("allow_preview", [False, True])
    @pytest.mark.parametrize("method_name", CONDITIONAL_VOICE_TELEPHONY_METHODS)
    def test_preview_opt_in_on_conditional_writes(self, allow_preview: bool, method_name: str) -> None:
        with AIProjectClient(
            endpoint=FAKE_ENDPOINT,
            credential=FakeCredential(),
            allow_preview=allow_preview,
            transport=CapturingTransport(),
        ) as client:
            method = getattr(client.voice_agents.telephony, method_name)
            request = self._capture(self._make_fake_call(method))
        assert request.headers.get("Foundry-Features") == ("VoiceAgents=V1Preview" if allow_preview else None)

    @pytest.mark.parametrize("allow_preview", [False, True])
    @pytest.mark.parametrize("method_name", ["create_call_job", "list_call_jobs"])
    @pytest.mark.parametrize("headers", [{}, {"foundry-features": "Custom=V1Preview", "x-test": "preserved"}])
    def test_conditional_preview_headers(self, allow_preview: bool, method_name: str, headers: dict) -> None:
        with AIProjectClient(
            endpoint=FAKE_ENDPOINT,
            credential=FakeCredential(),
            allow_preview=allow_preview,
            transport=CapturingTransport(),
        ) as client:
            method = getattr(client.voice_agents.telephony, method_name)
            request = self._capture(self._make_fake_call(method, extra_kwargs={"headers": headers.copy()}))
        automatic = "VoiceAgents=V1Preview" if allow_preview and method_name == "create_call_job" else None
        expected = headers.get("foundry-features", automatic)
        assert request.headers.get("Foundry-Features") == expected
        if headers:
            assert request.headers["x-test"] == "preserved"

    @pytest.mark.parametrize("allow_preview", [False, True])
    @pytest.mark.parametrize("operation_path", GA_VOICE_OPERATION_PATHS)
    def test_ga_voice_requests_without_preview(self, allow_preview: bool, operation_path: str) -> None:
        with AIProjectClient(
            endpoint=FAKE_ENDPOINT,
            credential=FakeCredential(),
            allow_preview=allow_preview,
            transport=CapturingTransport(),
        ) as client:
            operation = client
            for attribute in operation_path.split("."):
                operation = getattr(operation, attribute)
            request = self._capture(self._make_fake_call(operation))
        assert "Foundry-Features" not in request.headers
