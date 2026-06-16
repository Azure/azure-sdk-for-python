# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the ``ws_ping_interval`` configuration knob.

The interval lives on :class:`~azure.ai.agentserver.core.AgentConfig` and is
resolved from the ``WS_KEEPALIVE_INTERVAL`` environment variable
(auto-injected by AgentService into hosted-agent containers).  The Hypercorn
wiring lives in :class:`AgentServerHost._build_hypercorn_config`; the
invocations package exposes a convenience ``app.ws_ping_interval`` property
that reads the same config value.
"""
import pytest

from azure.ai.agentserver.invocations import InvocationAgentServerHost


_ENV_NAME = "WS_KEEPALIVE_INTERVAL"


# ---------------------------------------------------------------------------
# Default / accepted values (env-driven)
# ---------------------------------------------------------------------------

def test_ws_ping_interval_default_is_disabled(monkeypatch):
    """Default ping interval is 0 (disabled) when the env var is not set."""
    monkeypatch.delenv(_ENV_NAME, raising=False)
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 0.0


def test_ws_ping_interval_custom_value(monkeypatch):
    """``WS_KEEPALIVE_INTERVAL`` is honoured."""
    monkeypatch.setenv(_ENV_NAME, "15")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 15.0


def test_ws_ping_interval_zero_disables_keepalive(monkeypatch):
    """``WS_KEEPALIVE_INTERVAL=0`` disables WS-level keep-alive."""
    monkeypatch.setenv(_ENV_NAME, "0")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 0.0


def test_ws_ping_interval_float_value_accepted(monkeypatch):
    """Fractional intervals are coerced to ``float``."""
    monkeypatch.setenv(_ENV_NAME, "12.5")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 12.5
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert getattr(config, "websocket_ping_interval", None) == 12.5


def test_ws_ping_interval_empty_env_uses_default(monkeypatch):
    """An empty env-var value falls back to the default (disabled)."""
    monkeypatch.setenv(_ENV_NAME, "")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == 0.0


# ---------------------------------------------------------------------------
# Rejected values (validation surfaces at AgentConfig.from_env)
# ---------------------------------------------------------------------------

def test_ws_ping_interval_negative_rejected(monkeypatch):
    """Negative env-var values are programming errors."""
    monkeypatch.setenv(_ENV_NAME, "-1")
    with pytest.raises(ValueError, match="non-negative"):
        InvocationAgentServerHost()


def test_ws_ping_interval_non_numeric_rejected(monkeypatch):
    """Non-numeric env-var values surface as ``ValueError`` at startup."""
    monkeypatch.setenv(_ENV_NAME, "thirty")
    with pytest.raises(ValueError, match=_ENV_NAME):
        InvocationAgentServerHost()


# ---------------------------------------------------------------------------
# Hypercorn config wiring (delegated to core's _build_hypercorn_config)
# ---------------------------------------------------------------------------

def test_ws_ping_interval_propagates_to_hypercorn_config(monkeypatch):
    """The configured interval lands on the Hypercorn server config."""
    monkeypatch.setenv(_ENV_NAME, "20")
    app = InvocationAgentServerHost()
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    # Hypercorn ≥0.14 exposes this attribute.
    assert getattr(config, "websocket_ping_interval", None) == 20.0


def test_ws_ping_interval_zero_sets_attribute_to_none(monkeypatch):
    """Zero explicitly sets Hypercorn's ``websocket_ping_interval`` to ``None``."""
    monkeypatch.setenv(_ENV_NAME, "0")
    app = InvocationAgentServerHost()
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert config.websocket_ping_interval is None  # type: ignore[attr-defined]


def test_ws_ping_interval_default_wires_none_into_hypercorn(monkeypatch):
    """With no env var, Hypercorn config has ``websocket_ping_interval = None``."""
    monkeypatch.delenv(_ENV_NAME, raising=False)
    app = InvocationAgentServerHost()
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert config.websocket_ping_interval is None  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Property surface
# ---------------------------------------------------------------------------

def test_ws_ping_interval_property_is_read_only(monkeypatch):
    """``ws_ping_interval`` is exposed only as a property (no setter)."""
    monkeypatch.setenv(_ENV_NAME, "20")
    app = InvocationAgentServerHost()
    with pytest.raises(AttributeError):
        app.ws_ping_interval = 10  # type: ignore[misc]


def test_ws_ping_interval_mirrors_config(monkeypatch):
    """The property is a thin alias for ``app.config.ws_ping_interval``."""
    monkeypatch.setenv(_ENV_NAME, "7.5")
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == app.config.ws_ping_interval == 7.5
