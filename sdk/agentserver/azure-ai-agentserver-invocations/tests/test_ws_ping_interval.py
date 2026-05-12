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

def test_ws_ping_interval_default_is_30_seconds():
    """Default ping interval matches the spec (30 s)."""
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == InvocationsWSConstants.DEFAULT_PING_INTERVAL_S
    assert app.ws_ping_interval == 30.0


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


def test_ws_ping_interval_zero_does_not_override_hypercorn_default():
    """Zero leaves Hypercorn's default (None = disabled) intact."""
    app = InvocationAgentServerHost(ws_ping_interval=0)
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    # Hypercorn default is None — our wiring leaves it unset for 0.
    assert getattr(config, "websocket_ping_interval", None) is None


# ---------------------------------------------------------------------------
# Property surface
# ---------------------------------------------------------------------------

def test_ws_ping_interval_property_is_read_only():
    """``ws_ping_interval`` is exposed only as a property (no setter)."""
    app = InvocationAgentServerHost(ws_ping_interval=20)
    with pytest.raises(AttributeError):
        app.ws_ping_interval = 10  # type: ignore[misc]
