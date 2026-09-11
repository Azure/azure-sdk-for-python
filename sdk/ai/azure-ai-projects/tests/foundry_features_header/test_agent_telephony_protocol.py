# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Mocked protocol-level tests for the `agent_telephony` (batch 2) call-job/campaign operation
group, covering request construction (HTTP method + URL path) without depending on the live test
service's currently-unavailable API-version support for these routes (see
`tests/agents/test_voice_agent_telephony_campaign.py`, whose recorded tests are all skipped for
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
    FAKE_ENDPOINT,
    FakeCredential,
    FoundryFeaturesHeaderTestBase,
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
        allow_preview=True,
        transport=CapturingTransport(),
    ) as c:
        yield c


# (method_name, expected HTTP method, expected static URL path -- fake string/required params are
# always rendered as the literal "fake-value" by FoundryFeaturesHeaderTestBase._fake_for_param).
_TELEPHONY_PROTOCOL_CASES: List[Tuple[str, str, str]] = [
    ("create_call_job", "POST", "/agents/fake-value/telephony/call_jobs"),
    ("get_call_job", "GET", "/agents/fake-value/telephony/call_jobs/fake-value"),
    ("cancel_call_job", "POST", "/agents/fake-value/telephony/call_jobs/fake-value:cancel"),
    ("create_campaign", "POST", "/agents/fake-value/telephony/campaigns"),
    ("get_campaign", "GET", "/agents/fake-value/telephony/campaigns/fake-value"),
    (
        "begin_import_campaign_recipients",
        "POST",
        "/agents/fake-value/telephony/campaigns/fake-value/recipients:import",
    ),
    (
        "get_campaign_recipient_import",
        "GET",
        "/agents/fake-value/telephony/campaigns/fake-value/recipient_imports/fake-value",
    ),
    ("begin_validate_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:validate"),
    ("begin_publish_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:publish"),
    ("pause_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:pause"),
    ("resume_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:resume"),
    ("cancel_campaign", "POST", "/agents/fake-value/telephony/campaigns/fake-value:cancel"),
    ("get_operation", "GET", "/agents/fake-value/telephony/operations/fake-value"),
]


class TestAgentTelephonyProtocol(FoundryFeaturesHeaderTestBase):
    """Verify each `agent_telephony` method builds the correct HTTP method and URL path."""

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
        method = getattr(client.beta.agent_telephony, method_name)
        request = self._capture(self._make_fake_call(method))
        assert (
            request.method == expected_http_method
        ), f"{method_name}: expected HTTP method {expected_http_method!r}, got {request.method!r}"
        assert expected_path in request.url, f"{method_name}: expected path {expected_path!r} in URL {request.url!r}"
