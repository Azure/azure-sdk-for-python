# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 016 US9 / SC-016 / SC-017 — hosted-provider transport conformance.

Verifies that ``HostedTaskProvider`` is built on
``azure.core.AsyncPipelineClient`` with the canonical FR-030 policy
chain and exercises the canonical behaviors against an injected fake
transport (no network).

Coverage map:

- ``test_pipeline_policy_chain_composition`` — SC-016: policy chain has
  the required policies in the expected order; ``ContentDecodePolicy``
  is NOT present.
- ``test_retry_on_503_then_success`` — SC-017(a).
- ``test_no_retry_on_409`` — SC-017(b).
- ``test_request_carries_user_agent_and_request_id`` — SC-017(c)(d)(e).
- ``test_gzip_response_decoded_at_call_site`` — SC-017(f).
- ``test_non_json_body_classified`` — SC-017(g).
- ``test_classifier_table`` — FR-006 outcome enumeration (pure-function
  unit test paired with the transport tests for one-stop reviewer
  navigation).
"""

from __future__ import annotations

from typing import Any

import pytest

from azure.ai.agentserver.core.durable._client import (
    HostedTaskProvider,
    TransportClassifiedError,
    _classify_store_write_error,
)
from azure.core.pipeline.policies import (
    AsyncBearerTokenCredentialPolicy,
    AsyncRetryPolicy,
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    RequestIdPolicy,
    UserAgentPolicy,
)

from .conftest import FakeAsyncHttpTransport, FakeResponse


class _StubCredential:
    """Minimal :class:`AsyncTokenCredential`-shaped stub for tests.

    Returns a synthetic token whose ``token`` attribute is the literal
    string ``"<test-token>"`` so request-header assertions can match
    exactly without depending on identity provider behavior.
    """

    async def get_token(self, *scopes: str, **_kwargs: Any) -> Any:
        class _T:
            token = "<test-token>"
            expires_on = 9_999_999_999

        return _T()

    async def close(self) -> None:
        return None


def _make_provider(transport: FakeAsyncHttpTransport) -> HostedTaskProvider:
    return HostedTaskProvider(
        project_endpoint="https://example.invalid",
        credential=_StubCredential(),  # type: ignore[arg-type]
        transport=transport,
    )


# --------------------------------------------------------------------- #
# T012 / SC-016 — pipeline composition
# --------------------------------------------------------------------- #


def test_pipeline_policy_chain_composition() -> None:
    """SC-016: pipeline includes (in this order) request-id, headers,
    user-agent, retry, bearer-token, task-API logging, distributed tracing.
    ContentDecodePolicy is explicitly NOT in the chain."""

    provider = _make_provider(FakeAsyncHttpTransport())
    policies = provider.policies
    policy_types = [type(p) for p in policies]

    # Ordered checks: the first occurrence of each canonical policy
    # type appears in the expected order. We use isinstance to allow
    # subclass substitution (e.g., a CustomHookPolicy variant), but
    # require the canonical positions to remain.
    expected_order = [
        RequestIdPolicy,
        HeadersPolicy,
        UserAgentPolicy,
        AsyncRetryPolicy,
        AsyncBearerTokenCredentialPolicy,
        # TaskApiLoggingPolicy is local — checked by name to avoid
        # a circular import in this test module.
        None,  # placeholder; checked below
        DistributedTracingPolicy,
    ]

    positions: list[int] = []
    for expected in expected_order:
        if expected is None:
            # TaskApiLoggingPolicy slot: find by class name.
            idx = next(
                (i for i, p in enumerate(policies) if type(p).__name__ == "TaskApiLoggingPolicy"),
                -1,
            )
            assert idx != -1, "TaskApiLoggingPolicy missing from pipeline (FR-031)"
            positions.append(idx)
            continue
        idx = next(
            (i for i, p in enumerate(policies) if isinstance(p, expected)),
            -1,
        )
        assert idx != -1, (
            f"Required policy {expected.__name__} missing from pipeline. "
            f"Saw: {[t.__name__ for t in policy_types]}"
        )
        positions.append(idx)

    assert positions == sorted(positions), (
        f"Required policies out of order (FR-030). Expected indices "
        f"non-decreasing; got {positions} for "
        f"{[t.__name__ for t in policy_types]}"
    )

    assert not any(isinstance(p, ContentDecodePolicy) for p in policies), (
        "ContentDecodePolicy MUST NOT be in the pipeline (spec 016 FR-030, "
        "responses-storage gzip lesson). Body parsing is done at the call "
        "site with defensive error handling."
    )


# --------------------------------------------------------------------- #
# T013 / SC-017(a)(b) — retry behavior
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_retry_on_503_then_success() -> None:
    """SC-017(a): 503 → exactly 2 requests for a one-retry-success."""

    transport = FakeAsyncHttpTransport(
        [
            FakeResponse(status_code=503, headers={}, body=b""),
            FakeResponse.json_response({"id": "t-1", "agent_name": "a", "session_id": "s", "status": "pending"}, status_code=200),
        ]
    )
    provider = _make_provider(transport)
    result = await provider.get("t-1")
    assert result is not None
    assert len(transport.requests) == 2, (
        f"Expected exactly 2 requests (1 503 + 1 retry success); got {len(transport.requests)}."
    )


@pytest.mark.asyncio
async def test_no_retry_on_409_binding_mismatch() -> None:
    """SC-017(b): 409 with body MUST NOT be retried regardless of body
    classification. The classifier surfaces the eviction; the retry
    policy stays out of it."""

    transport = FakeAsyncHttpTransport(
        [
            FakeResponse.json_response(
                {"error": {"code": "binding_mismatch", "message": "evicted"}},
                status_code=409,
            ),
        ]
    )
    provider = _make_provider(transport)
    with pytest.raises(TransportClassifiedError) as excinfo:
        await provider.get("t-evicted")
    assert excinfo.value.classification == "evicted"
    assert excinfo.value.status == 409
    assert len(transport.requests) == 1, (
        f"Expected exactly 1 request (no retry on 409); got {len(transport.requests)}."
    )


@pytest.mark.asyncio
async def test_no_retry_on_409_other_body() -> None:
    """SC-017(b) corollary: a 409 with NON-binding_mismatch body is
    classified as 'conflict' and STILL not retried."""

    transport = FakeAsyncHttpTransport(
        [
            FakeResponse.json_response(
                {"error": {"code": "etag_mismatch"}}, status_code=409
            ),
        ]
    )
    provider = _make_provider(transport)
    with pytest.raises(TransportClassifiedError) as excinfo:
        await provider.get("t-conflict")
    assert excinfo.value.classification == "conflict"
    assert len(transport.requests) == 1


# --------------------------------------------------------------------- #
# T014 / SC-017(c)(d)(e) — header presence
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_request_carries_user_agent_and_request_id() -> None:
    """SC-017(c)(d)(e): each request carries Authorization (via the
    bearer-token policy), a User-Agent prefixed with the sdk moniker,
    and an x-ms-client-request-id."""

    transport = FakeAsyncHttpTransport(
        [
            FakeResponse.json_response(
                {"id": "t-1", "agent_name": "a", "session_id": "s", "status": "pending"},
                status_code=200,
            ),
        ]
    )
    provider = _make_provider(transport)
    await provider.get("t-1")
    assert len(transport.requests) == 1
    req = transport.requests[0]
    # Authorization
    auth = req.headers.get("Authorization") or req.headers.get("authorization")
    assert auth and auth.startswith("Bearer "), (
        f"Authorization header missing or malformed; got {auth!r} "
        f"(spec 016 FR-029: bearer token assembly is policy-driven, "
        f"not per-request)"
    )
    # User-Agent
    ua = req.headers.get("User-Agent") or req.headers.get("user-agent")
    assert ua and "ai-agentserver-core/" in ua, (
        f"User-Agent missing the sdk moniker; got {ua!r} "
        f"(spec 016 FR-030: sdk_moniker is 'ai-agentserver-core/{{VERSION}}')"
    )
    # x-ms-client-request-id
    request_id = req.headers.get("x-ms-client-request-id") or req.headers.get(
        "X-MS-Client-Request-Id"
    )
    assert request_id, (
        f"x-ms-client-request-id header missing from request; got "
        f"headers={req.headers!r}"
    )


# --------------------------------------------------------------------- #
# T015 / SC-017(f) — gzip round-trip without ContentDecodePolicy
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_gzip_response_decoded_at_call_site() -> None:
    """SC-017(f): a gzip-encoded JSON response body MUST decode
    successfully even though ContentDecodePolicy is not in the chain.
    The call-site _parse_json_body honors Content-Encoding: gzip."""

    transport = FakeAsyncHttpTransport(
        [
            FakeResponse.gzip_json_response(
                {"id": "t-1", "agent_name": "a", "session_id": "s", "status": "pending"},
                status_code=200,
            ),
        ]
    )
    provider = _make_provider(transport)
    result = await provider.get("t-1")
    assert result is not None
    assert result.id == "t-1"


# --------------------------------------------------------------------- #
# T016 / SC-017(g) — non-JSON body classification
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_non_json_200_body_raises_classified_error() -> None:
    """SC-017(g): a 200 with an HTML body (gateway sentinel page,
    misconfigured endpoint, etc.) MUST raise a classified transport
    error carrying status + truncated body prefix — not a raw
    JSONDecodeError or DecodeError that callers cannot interpret."""

    transport = FakeAsyncHttpTransport(
        [
            FakeResponse.html_response(
                "<html><body>Gateway 502 sentinel page</body></html>",
                status_code=200,
            ),
        ]
    )
    provider = _make_provider(transport)
    with pytest.raises(TransportClassifiedError) as excinfo:
        await provider.get("t-1")
    # status was actually 200 but body was unparseable — the classifier
    # treats 200 as "permanent" but the key requirement is the error
    # carries the status + body prefix.
    assert excinfo.value.status == 200
    assert excinfo.value.body_prefix is not None
    assert "Gateway" in (excinfo.value.body_prefix or "")


# --------------------------------------------------------------------- #
# Bonus — pure-function unit test for the classifier table (FR-006)
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("status", "body", "expected"),
    [
        # Transient: 5xx and standard transient HTTP statuses.
        (500, None, "transient"),
        (502, None, "transient"),
        (503, None, "transient"),
        (504, None, "transient"),
        (408, None, "transient"),
        (429, None, "transient"),
        # Evicted: 409 + binding_mismatch.
        (409, b'{"error": {"code": "binding_mismatch"}}', "evicted"),
        (
            409,
            b'{"error": {"code": "binding_mismatch", "message": "x"}}',
            "evicted",
        ),
        # Conflict: 409 with other body, 412.
        (409, b'{"error": {"code": "etag_mismatch"}}', "conflict"),
        (409, b"", "conflict"),
        (409, b"not json", "conflict"),
        (412, None, "conflict"),
        # Permanent: 404, 400, unrecognised 4xx.
        (404, None, "permanent"),
        (400, None, "permanent"),
        (403, None, "permanent"),
        (422, None, "permanent"),
    ],
)
def test_classifier_table(status: int, body: bytes | None, expected: str) -> None:
    """FR-006 enumeration: pure-function table test paired with the
    transport behavior tests above for one-stop reviewer navigation."""

    assert _classify_store_write_error(status, body) == expected
