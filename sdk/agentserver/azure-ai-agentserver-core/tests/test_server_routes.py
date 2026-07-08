# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for port resolution and unknown-route handling."""
import os
from unittest import mock

import pytest
import httpx

from azure.ai.agentserver.core import AgentServerHost
from azure.ai.agentserver.core._config import resolve_port



# ------------------------------------------------------------------ #
# Port resolution
# ------------------------------------------------------------------ #


class TestResolvePort:
    """Tests for resolve_port() — explicit > env > default."""

    def test_explicit_port_wins(self) -> None:
        assert resolve_port(9090) == 9090

    def test_env_var_port(self) -> None:
        with mock.patch.dict(os.environ, {"PORT": "7777"}):
            assert resolve_port(None) == 7777

    def test_default_port(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            # Remove PORT if set so the default is used.
            env = os.environ.copy()
            env.pop("PORT", None)
            with mock.patch.dict(os.environ, env, clear=True):
                assert resolve_port(None) == 8088

    def test_invalid_env_var_raises(self) -> None:
        with mock.patch.dict(os.environ, {"PORT": "not-a-number"}):
            with pytest.raises(ValueError, match="Invalid value for PORT"):
                resolve_port(None)

    def test_non_int_explicit_raises(self) -> None:
        with pytest.raises(ValueError, match="expected an integer"):
            resolve_port("8080")  # type: ignore[arg-type]

    def test_port_out_of_range_explicit(self) -> None:
        with pytest.raises(ValueError, match="expected 1-65535"):
            resolve_port(0)

    def test_port_above_range_explicit(self) -> None:
        with pytest.raises(ValueError, match="expected 1-65535"):
            resolve_port(70000)

    def test_env_var_port_out_of_range(self) -> None:
        with mock.patch.dict(os.environ, {"PORT": "0"}):
            with pytest.raises(ValueError, match="expected 1-65535"):
                resolve_port(None)

    def test_env_var_port_above_range(self) -> None:
        with mock.patch.dict(os.environ, {"PORT": "99999"}):
            with pytest.raises(ValueError, match="expected 1-65535"):
                resolve_port(None)


# ------------------------------------------------------------------ #
# Unknown route
# ------------------------------------------------------------------ #


@pytest.fixture()
def client() -> httpx.AsyncClient:
    agent = AgentServerHost()
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent),
        base_url="http://testserver",
    )


@pytest.mark.asyncio
async def test_unknown_route_returns_404(client: httpx.AsyncClient) -> None:
    """A request to an unregistered path returns 404."""
    resp = await client.get("/no-such-endpoint")
    assert resp.status_code == 404
