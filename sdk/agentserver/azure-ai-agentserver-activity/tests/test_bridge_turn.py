# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the per-request turn path in :mod:`_m365_bridge`.

Covers the request delegation (``StarletteCloudAdapter.process`` -> ``HttpAdapterBase.process_request``),
the Starlette request adapter (``_StarletteRequestAdapter``), the response
converter (``StarletteCloudAdapter._to_starlette_response``), the outbound-claims construction
(``_build_outbound_claims``), the handler factory (``build_bridge_handler``), and
the idempotent MSAL patch (``_apply_msal_patches``).

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
from azure.ai.agentserver.activity._constants import ErrorCode, MsalPatch, OutboundAuth

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
# _apply_msal_patches — idempotent.
# ---------------------------------------------------------------------------


def test_apply_msal_patches_is_idempotent():
    """Applying the MSAL patch twice sets the flag once and stays a no-op after."""
    from microsoft_agents.authentication.msal.msal_auth import MsalAuth

    # Ensure a clean starting state for this test.
    if hasattr(MsalAuth, MsalPatch.PATCH_FLAG):
        delattr(MsalAuth, MsalPatch.PATCH_FLAG)
    original = MsalAuth.get_agentic_application_token
    try:
        bridge._apply_msal_patches()
        assert getattr(MsalAuth, MsalPatch.PATCH_FLAG) is True
        patched = MsalAuth.get_agentic_application_token
        assert patched is not original

        # Second call must not re-patch (same function object retained).
        bridge._apply_msal_patches()
        assert MsalAuth.get_agentic_application_token is patched
    finally:
        MsalAuth.get_agentic_application_token = original
        if hasattr(MsalAuth, MsalPatch.PATCH_FLAG):
            delattr(MsalAuth, MsalPatch.PATCH_FLAG)


# ---------------------------------------------------------------------------
# _apply_msal_patches — the patched FMI token-exchange closure.
# ---------------------------------------------------------------------------


class _FakeToken:
    def __init__(self, token):
        self.token = token


class _FakeCredential:
    """Captures constructor kwargs and returns a scripted token or raises."""

    last_kwargs: dict = {}

    def __init__(self, **kwargs):
        type(self).last_kwargs = kwargs
        self.closed = False

    async def get_token(self, scope):
        return _FakeToken("fmi-token-123")

    async def close(self):
        self.closed = True


class _RaisingCredential(_FakeCredential):
    async def get_token(self, scope):
        raise RuntimeError("token exchange failed")


@pytest.fixture
def _patched_msal_auth():
    """Apply the FMI patch on a clean MsalAuth and restore it afterwards."""
    from microsoft_agents.authentication.msal.msal_auth import MsalAuth

    if hasattr(MsalAuth, MsalPatch.PATCH_FLAG):
        delattr(MsalAuth, MsalPatch.PATCH_FLAG)
    original = MsalAuth.get_agentic_application_token
    bridge._apply_msal_patches()
    try:
        yield MsalAuth
    finally:
        MsalAuth.get_agentic_application_token = original
        if hasattr(MsalAuth, MsalPatch.PATCH_FLAG):
            delattr(MsalAuth, MsalPatch.PATCH_FLAG)


def test_fmi_token_exchange_success(monkeypatch, _patched_msal_auth, caplog):
    """The patched token method mints a token via ManagedIdentityCredential, logs
    an INFO acquisition line, passes the FMI path, and closes the credential."""
    import logging

    import azure.identity.aio as aio

    monkeypatch.setattr(aio, "ManagedIdentityCredential", _FakeCredential)
    _FakeCredential.last_kwargs = {}

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver.activity.bridge"):
        token = _run(_patched_msal_auth.get_agentic_application_token(object(), "tenant-x", "agent-instance-1"))

    assert token == "fmi-token-123"
    assert _FakeCredential.last_kwargs["identity_config"] == {MsalPatch.FMI_PATH_KEY: "agent-instance-1"}
    assert any("agent-instance-1" in r.message for r in caplog.records)


def test_fmi_token_exchange_includes_client_id_when_configured(monkeypatch, _patched_msal_auth):
    """When the MSAL configuration carries a client id, it is forwarded as the
    managed identity client id."""
    import azure.identity.aio as aio

    monkeypatch.setattr(aio, "ManagedIdentityCredential", _FakeCredential)
    _FakeCredential.last_kwargs = {}

    msal_config = types.SimpleNamespace(**{MsalPatch.MSAL_CLIENT_ID_ATTR: "mi-client-77"})
    fake_self = types.SimpleNamespace(**{MsalPatch.MSAL_CONFIGURATION_ATTR: msal_config})

    token = _run(_patched_msal_auth.get_agentic_application_token(fake_self, "tenant-x", "agent-instance-1"))

    assert token == "fmi-token-123"
    assert _FakeCredential.last_kwargs["client_id"] == "mi-client-77"


def test_fmi_token_exchange_requires_instance_id(_patched_msal_auth):
    """An empty agent app instance id raises ValueError (cannot mint a token)."""
    with pytest.raises(ValueError):
        _run(_patched_msal_auth.get_agentic_application_token(object(), "tenant-x", ""))


def test_fmi_token_exchange_returns_none_on_error(monkeypatch, _patched_msal_auth):
    """A credential failure is swallowed and returns None (no token minted)."""
    import azure.identity.aio as aio

    monkeypatch.setattr(aio, "ManagedIdentityCredential", _RaisingCredential)

    token = _run(_patched_msal_auth.get_agentic_application_token(object(), "tenant-x", "agent-instance-1"))

    assert token is None


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
