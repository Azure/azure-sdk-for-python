# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Local HTTP CONNECT adapter: tunnel TLS through Toxiproxy without decrypting it."""

import os
import socket
import time
from urllib.parse import urlsplit

from toxiproxy._tcp_observer import TcpObserver
from toxiproxy._toxiproxy_config import validate_endpoint


class ConnectTunnel(TcpObserver):
    def __init__(self, proxy_endpoint, emulator_endpoint):
        validate_endpoint(proxy_endpoint)
        validate_endpoint(emulator_endpoint)
        super().__init__(urlsplit(proxy_endpoint).port or 443)
        port = urlsplit(emulator_endpoint).port or 443
        self.allowed_targets = {f"localhost:{port}", f"127.0.0.1:{port}"}

    @property
    def proxy_url(self):
        return f"http://127.0.0.1:{self.port}"

    def _reply(self, identity, client, status):
        with self.lock:
            self.connections[identity]["connect_status"] = status
        reason = {200: "Connection Established", 400: "Bad Request", 403: "Forbidden", 502: "Bad Gateway"}[status]
        client.sendall(f"HTTP/1.1 {status} {reason}\r\n\r\n".encode("ascii"))
        if status != 200:
            # Closing with unread bytes can reset the socket before Windows delivers the rejection.
            client.shutdown(socket.SHUT_WR)
            client.settimeout(0.1)
            deadline = time.monotonic() + 0.1
            try:
                while time.monotonic() < deadline and client.recv(4096):
                    pass
            except (socket.timeout, ConnectionResetError, ConnectionAbortedError):
                pass

    def _open_upstream(self, identity, client):
        header = bytearray()
        deadline = time.monotonic() + 2
        # Read only the CONNECT headers, never consume following TLS bytes.
        while not header.endswith(b"\r\n\r\n"):
            remaining = deadline - time.monotonic()
            if remaining <= 0 or len(header) >= 8192:
                self._reply(identity, client, 400)
                raise ConnectionAbortedError("CONNECT headers exceeded the time or size limit")
            client.settimeout(remaining)
            byte = client.recv(1)
            if not byte:
                raise ConnectionAbortedError("Client closed before completing CONNECT")
            header.extend(byte)
        client.settimeout(2)
        parts = bytes(header).split(b"\r\n", 1)[0].split(b" ")
        if len(parts) != 3 or parts[0] != b"CONNECT" or parts[2] not in (b"HTTP/1.0", b"HTTP/1.1"):
            self._reply(identity, client, 400)
            raise ConnectionAbortedError("Only HTTP CONNECT is supported")
        if parts[1].lower() not in {target.encode("ascii") for target in self.allowed_targets}:
            self._reply(identity, client, 403)
            raise ConnectionAbortedError("CONNECT target is not the configured emulator")
        with self.lock:
            self.connections[identity]["connect_target"] = parts[1].decode("ascii")
        try:
            upstream = socket.create_connection(self.upstream, timeout=2)
        except OSError as error:
            with self.lock:
                self.connections[identity]["connect_error"] = type(error).__name__
            self._reply(identity, client, 502)
            raise ConnectionAbortedError("Toxiproxy connection failed") from error
        try:
            self._reply(identity, client, 200)
        except BaseException:
            upstream.close()
            raise
        return upstream


def configure_proxy_environment(monkeypatch, tunnel):
    """Scope routing to this pytest process; direct setup runtimes disable proxies."""
    for name in list(os.environ):
        if name.lower() in ("http_proxy", "https_proxy", "all_proxy", "no_proxy"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("HTTPS_PROXY", tunnel.proxy_url)
    monkeypatch.setenv("NO_PROXY", "")
    # Preserve the Gateway V1 scope previously enforced by the synthetic account response.
    monkeypatch.setenv("AZURE_COSMOS_CONNECTION_POOL_GATEWAY_V2_DISABLED", "true")
    monkeypatch.setenv("AZURE_COSMOS_CONNECTION_POOL_GATEWAY_V2_DISABLED_OVERRIDE", "true")
    monkeypatch.delenv("AZURE_COSMOS_E2E_BACKGROUND_ACCOUNT_REFRESH_INTERVAL_MS", raising=False)
