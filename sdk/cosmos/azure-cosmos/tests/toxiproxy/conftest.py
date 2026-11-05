# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned proxy routes; run with --confcutdir=tests/toxiproxy."""

import os
import uuid

import pytest

from config.fault_resources import owned_target as owned_target


@pytest.fixture(params=["plain"])
def proxy_route(tmp_path, request, monkeypatch):
    from azure.cosmos import _rust
    from toxiproxy._toxiproxy import OwnedProxy
    from toxiproxy._toxiproxy_config import DRIVER_COMMIT, validate_endpoint
    from toxiproxy._connect_tunnel import ConnectTunnel, configure_proxy_environment
    from config.diagnostics import emit

    mode = request.param
    if mode not in ("plain", "observed", "reset", "sdk-observed"):
        raise ValueError(f"Unknown proxy observation mode: {mode}")
    endpoint = os.environ.get("ACCOUNT_HOST", "")
    validate_endpoint(endpoint)
    assert _rust.__rust_driver_commit__ == DRIVER_COMMIT, "Use the verified pinned driver build"
    proxy = OwnedProxy(
        os.environ.get("TOXIPROXY_SERVER", ""),
        endpoint,
        "cosmos-route-" + uuid.uuid4().hex,
        tmp_path,
        observe=mode != "plain",
    )
    request.addfinalizer(proxy.close)
    proxy.start()
    if mode == "reset":
        proxy.prepare_reset()
    if mode == "sdk-observed":
        proxy.observe_sdk_side()
    tunnel = ConnectTunnel(proxy.sdk_endpoint, endpoint)
    request.addfinalizer(tunnel.close)
    tunnel.start()
    configure_proxy_environment(monkeypatch, tunnel)
    emit("proxy_tunnel_started", proxy_url=tunnel.proxy_url, emulator_endpoint=endpoint,
         upstream=proxy.sdk_endpoint, account_response_modified=False)
    return proxy


@pytest.fixture
def proxy_target(proxy_route, owned_target):
    # Provision only after the proxy fixture has validated the local endpoint.
    return owned_target
