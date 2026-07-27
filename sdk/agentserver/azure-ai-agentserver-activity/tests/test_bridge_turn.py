# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the per-request turn path in :mod:`_m365_bridge`.

Covers the request delegation (``StarletteCloudAdapter.process`` -> ``HttpAdapterBase.process_request``),
the Starlette request adapter (``_StarletteRequestAdapter``), the response
converter (``StarletteCloudAdapter._to_starlette_response``), the outbound-claims construction
(``_build_outbound_claims``), and the handler factory (``build_bridge_handler``).

These exercise the real M365 ``ClaimsIdentity`` / ``HttpResponse`` types with a
stub adapter + agent app, so no live Bot Connector or network is required.
"""

import asyncio
import types

import pytest
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.activity import get_hosted_agent_env
from azure.ai.agentserver.activity import _cloud_adapter as cloud
from azure.ai.agentserver.activity import _m365_bridge as bridge
from azure.ai.agentserver.activity._constants import ErrorCode, OutboundAuth

# The M365 Agents SDK is an optional dependency; skip this whole module (rather
# than error at collection) when it is not installed, so the package's tests
# still run in an environment without the optional extras.
pytest.importorskip("microsoft_agents.hosting.core")

from microsoft_agents.hosting.core import ClaimsIdentity
from microsoft_agents.hosting.core.http import HttpResponse

# ---------------------------------------------------------------------------
# Stubs.
# ---------------------------------------------------------------------------


class _FakeAdapter:
    """Adapter stub exposing ``process_request`` (the shared M365 pipeline).

    Captures the adapted request + agent it was called with and returns a
    scripted ``HttpResponse``.
    """

    def __init__(self, *, response=None):
        self._response = response if response is not None else HttpResponse(status_code=202)
        self.calls = []

    async def process_request(self, request, agent):
        self.calls.append((request, agent))
        return self._response


class _FakeAgentApp:
    """Agent-app stub exposing an ``on_turn`` coroutine (never actually run)."""

    async def on_turn(self, context):  # pragma: no cover - not invoked by stub adapter
        return None


def _make_request(activity_dict, *, method="POST", headers=None, path_params=None):
    """Build a minimal object exposing the Starlette request surface used here."""
    state = types.SimpleNamespace(activity=activity_dict)
    return types.SimpleNamespace(
        state=state,
        method=method,
        headers=headers or {},
        path_params=path_params or {},
    )


def _run(coroutine):
    return asyncio.run(coroutine)


def _process(agent_app, adapter, request, *, digital_worker, is_hosted, bot_app_id):
    """Drive a request through the turn path: synthesize claims (bridge), attach
    them to the request, then delegate to the CloudAdapter's ``process``."""
    from microsoft_agents.hosting.core import ClaimsIdentity

    request.state.claims_identity = bridge._build_outbound_claims(
        ClaimsIdentity,
        digital_worker=digital_worker,
        is_hosted=is_hosted,
        bot_app_id=bot_app_id,
    )
    return cloud.StarletteCloudAdapter(adapter).process(request, agent_app)


# ---------------------------------------------------------------------------
# _build_outbound_claims — the three auth branches.
# ---------------------------------------------------------------------------


def test_claims_digital_worker_is_anonymous():
    """Digital-worker model uses anonymous claims (FMI patch supplies the token)."""
    claims = bridge._build_outbound_claims(ClaimsIdentity, digital_worker=True, is_hosted=True, bot_app_id="ignored")

    assert claims.is_authenticated is False
    assert claims.authentication_type == OutboundAuth.AUTH_TYPE_ANONYMOUS


def test_claims_simple_local_no_creds_is_anonymous(caplog):
    """Simple model, local, no credential -> anonymous claims + a LOCAL DEV warning."""
    import logging

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver.activity.bridge"):
        claims = bridge._build_outbound_claims(ClaimsIdentity, digital_worker=False, is_hosted=False, bot_app_id="")

    assert claims.is_authenticated is False
    assert claims.authentication_type == OutboundAuth.AUTH_TYPE_ANONYMOUS
    assert any("LOCAL DEV" in r.message for r in caplog.records)


def test_claims_simple_hosted_is_authenticated_bearer():
    """Simple model, hosted, with a bot app id -> authenticated Bearer claims that
    carry appid + audience matching the service-connection client id."""
    claims = bridge._build_outbound_claims(
        ClaimsIdentity, digital_worker=False, is_hosted=True, bot_app_id="client-xyz"
    )

    assert claims.is_authenticated is True
    assert claims.authentication_type == OutboundAuth.AUTH_TYPE_BEARER
    assert claims.get_claim_value(OutboundAuth.CLAIM_APP_ID) == "client-xyz"
    assert claims.get_claim_value(OutboundAuth.CLAIM_AUDIENCE) == "client-xyz"


def test_claims_simple_with_credential_local_is_authenticated():
    """Simple model, local but a Bot Connector credential is configured ->
    authenticated path (a credential exists to mint a real token)."""
    claims = bridge._build_outbound_claims(
        ClaimsIdentity, digital_worker=False, is_hosted=False, bot_app_id="client-xyz"
    )

    assert claims.is_authenticated is True
    assert claims.authentication_type == OutboundAuth.AUTH_TYPE_BEARER


def test_claims_authenticated_with_empty_bot_app_id_has_empty_claims():
    """Authenticated path with an empty bot app id still returns Bearer claims
    but with no appid/audience entries."""
    claims = bridge._build_outbound_claims(ClaimsIdentity, digital_worker=False, is_hosted=True, bot_app_id="")

    assert claims.is_authenticated is True
    assert claims.authentication_type == OutboundAuth.AUTH_TYPE_BEARER
    assert claims.get_claim_value(OutboundAuth.CLAIM_APP_ID) is None


# ---------------------------------------------------------------------------
# StarletteCloudAdapter.process — delegates to HttpAdapterBase.process_request.
# ---------------------------------------------------------------------------


def test_process_delegates_to_process_request():
    """process() adapts the request + synthesized claims and hands them to
    ``adapter.process_request(adapted, agent_app)``, converting the result."""
    adapter = _FakeAdapter(response=HttpResponse(status_code=202))
    agent_app = _FakeAgentApp()
    request = _make_request({"type": "message", "conversation": {"id": "c1"}})

    resp = _run(
        _process(
            agent_app,
            adapter,
            request,
            digital_worker=False,
            is_hosted=True,
            bot_app_id="client-xyz",
        )
    )

    assert resp.status_code == 202
    assert len(adapter.calls) == 1
    adapted_request, passed_agent = adapter.calls[0]
    assert passed_agent is agent_app
    # The adapted request exposes the synthesized outbound claims (authenticated
    # Bearer because hosted + bot app id) and the parsed activity dict.
    claims = adapted_request.get_claims_identity()
    assert claims.is_authenticated is True
    assert claims.authentication_type == OutboundAuth.AUTH_TYPE_BEARER
    assert _run(adapted_request.json()) == {"type": "message", "conversation": {"id": "c1"}}


def test_process_converts_success_body():
    """A 200 HttpResponse with a body becomes a JSONResponse carrying that body."""
    adapter = _FakeAdapter(response=HttpResponse(status_code=200, body={"ok": True}))
    request = _make_request({"type": "invoke", "conversation": {"id": "c1"}})

    resp = _run(
        _process(
            _FakeAgentApp(),
            adapter,
            request,
            digital_worker=False,
            is_hosted=True,
            bot_app_id="client-xyz",
        )
    )

    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 200


def test_process_wraps_400_in_error_envelope():
    """A 400 from the pipeline is re-wrapped into the activity error envelope."""
    adapter = _FakeAdapter(response=HttpResponse(status_code=400, body={"error": "Activity must have type"}))
    request = _make_request({"type": "message"})

    resp = _run(
        _process(
            _FakeAgentApp(),
            adapter,
            request,
            digital_worker=False,
            is_hosted=False,
            bot_app_id="",
        )
    )

    assert resp.status_code == 400
    assert isinstance(resp, JSONResponse)


def test_process_maps_401():
    """A 401 from the pipeline maps to a 401 response."""
    adapter = _FakeAdapter(response=HttpResponse(status_code=401, body={"error": "Unauthorized"}))
    request = _make_request({"type": "message", "conversation": {"id": "c1"}})

    resp = _run(
        _process(
            _FakeAgentApp(),
            adapter,
            request,
            digital_worker=False,
            is_hosted=True,
            bot_app_id="client-xyz",
        )
    )

    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# _StarletteRequestAdapter — the HttpRequestProtocol adapter.
# ---------------------------------------------------------------------------


def test_request_adapter_exposes_request_surface():
    """The adapter maps method / headers / json / path params from the request,
    and reads the claims identity attached to ``request.state`` (as auth
    middleware / the bridge sets it)."""
    claims = ClaimsIdentity({}, is_authenticated=False)
    request = _make_request(
        {"type": "message"},
        method="POST",
        headers={"x-test": "1"},
        path_params={"conversation_id": "c9"},
    )
    request.state.claims_identity = claims
    adapted = cloud._StarletteRequestAdapter(request)

    assert adapted.method == "POST"
    assert adapted.headers == {"x-test": "1"}
    assert _run(adapted.json()) == {"type": "message"}
    assert adapted.get_claims_identity() is claims
    assert adapted.get_path_param("conversation_id") == "c9"
    assert adapted.get_path_param("missing") == ""


def test_request_adapter_claims_default_none():
    """When no claims are attached to the request, get_claims_identity is None."""
    request = _make_request({"type": "message"})
    adapted = cloud._StarletteRequestAdapter(request)

    assert adapted.get_claims_identity() is None


# ---------------------------------------------------------------------------
# StarletteCloudAdapter._to_starlette_response — HttpResponse conversion.
# ---------------------------------------------------------------------------

_to_response = cloud.StarletteCloudAdapter._to_starlette_response


def test_to_response_bodyless_success():
    """A bodyless success HttpResponse becomes a plain Response with the status."""
    resp = _to_response(HttpResponse(status_code=202))

    assert isinstance(resp, Response)
    assert resp.status_code == 202


def test_to_response_success_body_passthrough():
    """A success body is passed through as a JSONResponse."""
    resp = _to_response(HttpResponse(status_code=200, body={"ok": True}))

    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 200


def test_to_response_400_uses_invalid_request_envelope():
    """A 400 is re-wrapped into {'error': {'code': invalid_request, 'message'}}."""
    import json

    resp = _to_response(HttpResponse(status_code=400, body={"error": "bad activity"}))

    assert resp.status_code == 400
    payload = json.loads(bytes(resp.body))
    assert payload["error"]["code"] == ErrorCode.INVALID_REQUEST
    assert payload["error"]["message"] == "bad activity"


def test_to_response_500_uses_internal_error_envelope():
    """A non-400 error maps to the internal_error code with a default message."""
    import json

    resp = _to_response(HttpResponse(status_code=500, body=None))

    assert resp.status_code == 500
    payload = json.loads(bytes(resp.body))
    assert payload["error"]["code"] == ErrorCode.INTERNAL_ERROR


def test_to_response_preserves_headers():
    """Headers carried on the HttpResponse are preserved on the Starlette response."""
    resp = _to_response(HttpResponse(status_code=200, body={"ok": True}, headers={"x-keep": "yes"}))

    assert resp.headers.get("x-keep") == "yes"


# ---------------------------------------------------------------------------
# build_bridge_handler — binds a working handler to the CloudAdapter.
# ---------------------------------------------------------------------------


def test_build_bridge_handler_returns_working_handler():
    """The factory returns a handler bound to the app + adapter that drives the
    CloudAdapter's process (delegating to process_request)."""
    adapter = _FakeAdapter(response=HttpResponse(status_code=202))
    agent_app = _FakeAgentApp()

    handler = bridge.build_bridge_handler(agent_app, adapter, digital_worker=True, is_hosted=False, bot_app_id="abc")
    resp = _run(handler(_make_request({"type": "message", "conversation": {"id": "c1"}})))

    assert resp.status_code == 202
    assert len(adapter.calls) == 1
    adapted_request, passed_agent = adapter.calls[0]
    assert passed_agent is agent_app
    # Digital-worker model -> anonymous outbound claims bound into the request.
    assert adapted_request.get_claims_identity().is_authenticated is False


# ---------------------------------------------------------------------------
# build_m365_app — real build + injected fast-path.
# ---------------------------------------------------------------------------


def test_build_m365_app_builds_real_stack(monkeypatch):
    """The default path builds a real AgentApplication + adapter from resolved
    connection config (no injected components)."""
    monkeypatch.setenv("FOUNDRY_AGENT_INSTANCE_CLIENT_ID", "11111111-1111-1111-1111-111111111111")
    monkeypatch.setenv("FOUNDRY_AGENT_TENANT_ID", "22222222-2222-2222-2222-222222222222")

    from microsoft_agents.hosting.core import MemoryStorage

    connection_config = get_hosted_agent_env(digital_worker=False)
    app, adapter = bridge.build_m365_app(
        digital_worker=False, connection_config=connection_config, storage=MemoryStorage()
    )

    from microsoft_agents.hosting.core import AgentApplication, HttpAdapterBase

    assert isinstance(app, AgentApplication)
    assert isinstance(adapter, HttpAdapterBase)


def test_build_m365_app_fast_path_returns_injected_app():
    """When an agent_app is injected, it is returned as-is with its own adapter
    (no build, connection_config ignored)."""

    class _App:
        adapter = object()

    injected = _App()
    app, adapter = bridge.build_m365_app(digital_worker=False, connection_config={}, storage=None, agent_app=injected)

    assert app is injected
    assert adapter is injected.adapter
