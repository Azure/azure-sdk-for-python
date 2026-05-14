# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the ``ws_ping_interval`` configuration knob.

Parity with :mod:`tests.test_request_limits` / configuration tests in
:mod:`tests.test_graceful_shutdown` — validates the Hypercorn ``ws_ping_interval``
parameter parsing and wiring.
"""
import pytest

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._constants import InvocationsWSConstants


# ---------------------------------------------------------------------------
# Default / accepted values
# ---------------------------------------------------------------------------

def test_ws_ping_interval_default_is_disabled():
    """Default ping interval is 0 (disabled) when no arg / env var is set."""
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 0.0


def test_ws_ping_interval_custom_value():
    """``ws_ping_interval`` is honoured."""
    app = InvocationAgentServerHost(ws_ping_interval=15)
    assert app.ws_ping_interval == 15.0


def test_ws_ping_interval_zero_disables_keepalive():
    """``ws_ping_interval=0`` disables WS-level keep-alive."""
    app = InvocationAgentServerHost(ws_ping_interval=0)
    assert app.ws_ping_interval == 0.0


def test_ws_ping_interval_float_value_accepted():
    """Fractional intervals are coerced to ``float``."""
    app = InvocationAgentServerHost(ws_ping_interval=12.5)
    assert app.ws_ping_interval == 12.5
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert getattr(config, "websocket_ping_interval", None) == 12.5


# ---------------------------------------------------------------------------
# Rejected values (validation)
# ---------------------------------------------------------------------------

def test_ws_ping_interval_negative_rejected():
    """Negative intervals are programming errors."""
    with pytest.raises(ValueError, match="non-negative"):
        InvocationAgentServerHost(ws_ping_interval=-1)


def test_ws_ping_interval_nan_rejected():
    """``ws_ping_interval=nan`` is a programming error."""
    with pytest.raises(ValueError, match="non-negative"):
        InvocationAgentServerHost(ws_ping_interval=float("nan"))


def test_ws_ping_interval_inf_rejected():
    """``ws_ping_interval=inf`` is a programming error."""
    with pytest.raises(ValueError, match="non-negative"):
        InvocationAgentServerHost(ws_ping_interval=float("inf"))


def test_ws_ping_interval_non_numeric_rejected():
    """Strings or non-numeric values surface as ``ValueError``."""
    with pytest.raises(ValueError, match="must be a number"):
        InvocationAgentServerHost(ws_ping_interval="thirty")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Hypercorn config wiring
# ---------------------------------------------------------------------------

def test_ws_ping_interval_propagates_to_hypercorn_config():
    """The configured interval lands on the Hypercorn server config."""
    app = InvocationAgentServerHost(ws_ping_interval=20)
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    # Hypercorn ≥0.14 exposes this attribute.
    assert getattr(config, "websocket_ping_interval", None) == 20.0


def test_ws_ping_interval_zero_sets_attribute_to_none():
    """Zero explicitly sets Hypercorn's ``websocket_ping_interval`` to ``None``."""
    app = InvocationAgentServerHost(ws_ping_interval=0)
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert config.websocket_ping_interval is None  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Property surface
# ---------------------------------------------------------------------------

def test_ws_ping_interval_property_is_read_only():
    """``ws_ping_interval`` is exposed only as a property (no setter)."""
    app = InvocationAgentServerHost(ws_ping_interval=20)
    with pytest.raises(AttributeError):
        app.ws_ping_interval = 10  # type: ignore[misc]


# ---------------------------------------------------------------------------
# WS_KEEPALIVE_INTERVAL env var (platform-injected override)
# ---------------------------------------------------------------------------

def test_ws_keepalive_interval_env_var_used_when_arg_is_none(monkeypatch):
    """Env var drives the interval when no explicit arg is passed."""
    monkeypatch.setenv(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL, "45")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 45.0


def test_ws_keepalive_interval_env_var_zero_disables(monkeypatch):
    """``WS_KEEPALIVE_INTERVAL=0`` disables keep-alive (mirrors SSE)."""
    monkeypatch.setenv(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL, "0")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 0.0
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert getattr(config, "websocket_ping_interval", None) is None


def test_ws_keepalive_interval_env_var_float_accepted(monkeypatch):
    """Fractional env-var values are coerced to ``float``."""
    monkeypatch.setenv(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL, "12.5")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 12.5


def test_ws_keepalive_interval_env_var_empty_uses_default(monkeypatch):
    """An empty env-var value falls back to the default (disabled)."""
    monkeypatch.setenv(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL, "")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 0.0


def test_ws_keepalive_interval_env_var_invalid_rejected(monkeypatch):
    """Non-numeric env-var values surface as ``ValueError`` at startup."""
    monkeypatch.setenv(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL, "thirty")
    with pytest.raises(ValueError, match="WS_KEEPALIVE_INTERVAL"):
        InvocationAgentServerHost()


def test_ws_keepalive_interval_env_var_negative_rejected(monkeypatch):
    """Negative env-var values are programming errors."""
    monkeypatch.setenv(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL, "-5")
    with pytest.raises(ValueError, match="WS_KEEPALIVE_INTERVAL"):
        InvocationAgentServerHost()


def test_ws_ping_interval_arg_overrides_env_var(monkeypatch):
    """Explicit constructor arg wins over the env var."""
    monkeypatch.setenv(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL, "45")
    app = InvocationAgentServerHost(ws_ping_interval=10)
    assert app.ws_ping_interval == 10.0


def test_ws_ping_interval_default_wires_none_into_hypercorn(monkeypatch):
    """With neither arg nor env var, Hypercorn config has ``websocket_ping_interval = None``."""
    monkeypatch.delenv(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL, raising=False)
    app = InvocationAgentServerHost()
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert config.websocket_ping_interval is None  # type: ignore[attr-defined]


def test_ws_ping_interval_positive_wires_into_hypercorn():
    """A positive interval propagates as a float to Hypercorn config."""
    app = InvocationAgentServerHost(ws_ping_interval=12)
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert config.websocket_ping_interval == 12.0  # type: ignore[attr-defined]

