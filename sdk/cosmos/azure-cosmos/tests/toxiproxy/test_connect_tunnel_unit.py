# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise the actual local CONNECT tunnel without Cosmos or Toxiproxy services."""

import os
import socket

import pytest

from toxiproxy._connect_tunnel import ConnectTunnel, configure_proxy_environment


def receive_headers(client):
    header = bytearray()
    while not header.endswith(b"\r\n\r\n"):
        byte = client.recv(1)
        assert byte, "Tunnel closed without a complete HTTP response"
        header.extend(byte)
        assert len(header) < 8192
    return bytes(header)


@pytest.fixture
def route():
    with socket.socket() as upstream:
        upstream.bind(("127.0.0.1", 0))
        upstream.listen()
        upstream.settimeout(2)
        tunnel = ConnectTunnel(
            f"https://127.0.0.1:{upstream.getsockname()[1]}/", "https://localhost:8081/",
        )
        try:
            tunnel.start()
            yield tunnel, upstream
        finally:
            tunnel.close()
        assert not tunnel.thread.is_alive()
        assert all(not worker.is_alive() for worker in tunnel.workers)
        with socket.socket() as probe:
            assert probe.connect_ex(("127.0.0.1", tunnel.port)) != 0


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1"])
@pytest.mark.parametrize("fragmented", [False, True])
def test_connect_forwards_only_tunnel_bytes_in_both_directions_rust(route, host, fragmented):
    tunnel, upstream = route
    with socket.create_connection(("127.0.0.1", tunnel.port), timeout=2) as client:
        header = f"CONNECT {host}:8081 HTTP/1.1\r\nHost: {host}:8081\r\n\r\n".encode("ascii")
        # Coalesced post-header bytes must not disappear into an HTTP parser buffer.
        if fragmented:
            client.sendall(header[:10])
            client.sendall(header[10:] + b"\x16\x03\x03opaque-request")
        else:
            client.sendall(header + b"\x16\x03\x03opaque-request")
        assert receive_headers(client).startswith(b"HTTP/1.1 200 ")
        server, _ = upstream.accept()
        with server:
            server.settimeout(2)
            assert server.recv(1024) == b"\x16\x03\x03opaque-request"
            server.sendall(b"opaque-response")
            assert client.recv(1024) == b"opaque-response"
            server.shutdown(socket.SHUT_WR)
            assert client.recv(1) == b""
    snapshot = tunnel.snapshot()
    assert snapshot["1"]["connect_target"] == f"{host}:8081"
    assert snapshot["1"]["connect_status"] == 200
    assert all(set(event) == {"direction", "bytes", "at"} for event in snapshot["1"]["events"])


@pytest.mark.parametrize("connect_request,status", [
    (b"CONNECT remote.example:8081 HTTP/1.1\r\n\r\n", 403),
    (b"CONNECT localhost:9999 HTTP/1.1\r\n\r\n", 403),
    (b"CONNECT user@localhost:8081 HTTP/1.1\r\n\r\n", 403),
    (b"CONNECT localhost:8081/path HTTP/1.1\r\n\r\n", 403),
    (b"CONNECT localhost:8081 HTTP/2\r\n\r\n", 400),
    (b"GET / HTTP/1.1\r\n\r\n", 400),
    (b"CONNECT localhost:8081 HTTP/1.1\r\nX: " + b"a" * 8192, 400),
])
def test_connect_rejects_wrong_targets_and_protocol_without_forwarding_rust(route, connect_request, status):
    tunnel, upstream = route
    with socket.create_connection(("127.0.0.1", tunnel.port), timeout=2) as client:
        client.sendall(connect_request)
        assert receive_headers(client).startswith(f"HTTP/1.1 {status} ".encode("ascii"))
    upstream.settimeout(0.05)
    with pytest.raises(socket.timeout):
        upstream.accept()
    assert tunnel.snapshot()["1"]["connect_status"] == status


def test_connect_reports_upstream_failure_without_direct_fallback_rust():
    with socket.socket() as unavailable:
        unavailable.bind(("127.0.0.1", 0))
        # Reserved but not listening: connection must fail.
        tunnel = ConnectTunnel(
            f"https://127.0.0.1:{unavailable.getsockname()[1]}/", "https://localhost:8081/",
        )
        try:
            tunnel.start()
            with socket.create_connection(("127.0.0.1", tunnel.port), timeout=3) as client:
                client.sendall(b"CONNECT localhost:8081 HTTP/1.1\r\n\r\n")
                assert receive_headers(client).startswith(b"HTTP/1.1 502 ")
            connection = tunnel.snapshot()["1"]
            assert connection["connect_status"] == 502
            assert connection["connect_error"]
            assert connection["forwarding_started_at"] is None
        finally:
            tunnel.close()


def test_proxy_environment_clears_bypass_and_restores_inherited_settings_rust(monkeypatch, route):
    tunnel, _ = route
    monkeypatch.setenv("HTTPS_PROXY", "http://inherited.invalid:1234")
    monkeypatch.setenv("ALL_PROXY", "http://inherited.invalid:5678")
    monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1")
    monkeypatch.setenv("AZURE_COSMOS_CONNECTION_POOL_GATEWAY_V2_DISABLED", "false")
    monkeypatch.setenv("AZURE_COSMOS_CONNECTION_POOL_GATEWAY_V2_DISABLED_OVERRIDE", "false")
    monkeypatch.setenv("AZURE_COSMOS_E2E_BACKGROUND_ACCOUNT_REFRESH_INTERVAL_MS", "100")
    before = dict(os.environ)
    with monkeypatch.context() as scoped:
        configure_proxy_environment(scoped, tunnel)
        assert os.environ["HTTPS_PROXY"] == tunnel.proxy_url
        assert os.environ["NO_PROXY"] == ""
        assert "ALL_PROXY" not in os.environ and "HTTP_PROXY" not in os.environ
        assert os.environ["AZURE_COSMOS_CONNECTION_POOL_GATEWAY_V2_DISABLED"] == "true"
        assert os.environ["AZURE_COSMOS_CONNECTION_POOL_GATEWAY_V2_DISABLED_OVERRIDE"] == "true"
        assert "AZURE_COSMOS_E2E_BACKGROUND_ACCOUNT_REFRESH_INTERVAL_MS" not in os.environ
    assert dict(os.environ) == before
