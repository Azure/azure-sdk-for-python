# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Integration tests verifying HTTP/2 support via Hypercorn.

**TLS tests** start a real Hypercorn server with a self-signed cert and
connect via HTTP/2 using ``httpx`` with ALPN negotiation.  # cspell:ignore ALPN

**h2c tests** (HTTP/2 cleartext) start a plain-TCP Hypercorn server and
connect via HTTP/2 *prior knowledge* (``http1=False, http2=True``),
proving that HTTP/2 works without any TLS certificates.

Requirements (auto-skipped when missing):
- ``cryptography`` — self-signed certificate generation (TLS tests only)
- ``h2`` — HTTP/2 client support in httpx (installed with hypercorn)
"""
from __future__ import annotations

import asyncio
import datetime
import ipaddress
import socket
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio

cryptography = pytest.importorskip("cryptography", reason="cryptography needed for TLS cert generation")
pytest.importorskip("h2", reason="h2 needed for HTTP/2 client support")

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

import httpx
from hypercorn.asyncio import serve as _hypercorn_serve
from hypercorn.config import Config as HypercornConfig
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver import AgentServer


# ---------------------------------------------------------------------------
# Test agents
# ---------------------------------------------------------------------------


class _EchoAgent(AgentServer):
    """Agent that echoes the request body in the response."""

    async def invoke(self, request: Request) -> Response:
        body = await request.body()
        return JSONResponse({"echo": body.decode()})


class _StreamAgent(AgentServer):
    """Agent that returns a streaming response."""

    async def invoke(self, request: Request) -> Response:
        async def generate() -> AsyncGenerator[bytes, None]:
            for chunk in [b"chunk1", b"chunk2", b"chunk3"]:
                yield chunk

        return StreamingResponse(generate(), media_type="application/octet-stream")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_free_port() -> int:
    """Find an available TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _generate_self_signed_cert(cert_path: Path, key_path: Path) -> None:
    """Generate a self-signed TLS certificate for localhost / 127.0.0.1."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(hours=1))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


async def _wait_for_server(host: str, port: int, timeout: float = 5.0) -> None:
    """Poll until the server is accepting connections."""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        try:
            _, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return
        except OSError:
            await asyncio.sleep(0.05)
    raise TimeoutError(f"Server on {host}:{port} did not start within {timeout}s")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tls_cert_pair():
    """Generate a self-signed cert + key in a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cert_path = Path(tmpdir) / "cert.pem"
        key_path = Path(tmpdir) / "key.pem"
        _generate_self_signed_cert(cert_path, key_path)
        yield str(cert_path), str(key_path)


@pytest_asyncio.fixture()
async def echo_h2_server(tls_cert_pair):
    """Start _EchoAgent on a random port with TLS, yield the port."""
    cert_path, key_path = tls_cert_pair
    port = _get_free_port()

    agent = _EchoAgent()
    config = HypercornConfig()
    config.bind = [f"127.0.0.1:{port}"]
    config.certfile = cert_path
    config.keyfile = key_path
    config.graceful_timeout = 1.0

    shutdown_event = asyncio.Event()
    task = asyncio.create_task(
        _hypercorn_serve(agent.app, config, shutdown_trigger=shutdown_event.wait)
    )
    await _wait_for_server("127.0.0.1", port)
    yield port

    shutdown_event.set()
    await task


@pytest_asyncio.fixture()
async def stream_h2_server(tls_cert_pair):
    """Start _StreamAgent on a random port with TLS, yield the port."""
    cert_path, key_path = tls_cert_pair
    port = _get_free_port()

    agent = _StreamAgent()
    config = HypercornConfig()
    config.bind = [f"127.0.0.1:{port}"]
    config.certfile = cert_path
    config.keyfile = key_path
    config.graceful_timeout = 1.0

    shutdown_event = asyncio.Event()
    task = asyncio.create_task(
        _hypercorn_serve(agent.app, config, shutdown_trigger=shutdown_event.wait)
    )
    await _wait_for_server("127.0.0.1", port)
    yield port

    shutdown_event.set()
    await task


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHttp2Health:
    """Verify health endpoints work over HTTP/2."""

    @pytest.mark.asyncio
    async def test_h2_liveness(self, echo_h2_server):
        port = echo_h2_server
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            resp = await client.get(f"https://127.0.0.1:{port}/liveness")
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/2"
            assert resp.json() == {"status": "alive"}

    @pytest.mark.asyncio
    async def test_h2_readiness(self, echo_h2_server):
        port = echo_h2_server
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            resp = await client.get(f"https://127.0.0.1:{port}/readiness")
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/2"
            assert resp.json() == {"status": "ready"}


class TestHttp2Invoke:
    """Verify invocation works over HTTP/2."""

    @pytest.mark.asyncio
    async def test_h2_invoke_returns_200(self, echo_h2_server):
        port = echo_h2_server
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            resp = await client.post(
                f"https://127.0.0.1:{port}/invocations",
                json={"message": "hello"},
            )
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/2"
            data = resp.json()
            assert "echo" in data

    @pytest.mark.asyncio
    async def test_h2_invocation_id_header(self, echo_h2_server):
        port = echo_h2_server
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            resp = await client.post(
                f"https://127.0.0.1:{port}/invocations",
                json={"message": "test"},
            )
            assert resp.http_version == "HTTP/2"
            assert "x-agent-invocation-id" in resp.headers

    @pytest.mark.asyncio
    async def test_h2_multiple_requests_on_same_connection(self, echo_h2_server):
        """HTTP/2 multiplexing: multiple requests on a single connection."""
        port = echo_h2_server
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            responses = await asyncio.gather(
                client.post(f"https://127.0.0.1:{port}/invocations", json={"n": 1}),
                client.post(f"https://127.0.0.1:{port}/invocations", json={"n": 2}),
                client.post(f"https://127.0.0.1:{port}/invocations", json={"n": 3}),
            )
            for resp in responses:
                assert resp.status_code == 200
                assert resp.http_version == "HTTP/2"
            # Each invocation gets a unique ID
            ids = {resp.headers["x-agent-invocation-id"] for resp in responses}
            assert len(ids) == 3


class TestHttp2Streaming:
    """Verify streaming responses work over HTTP/2."""

    @pytest.mark.asyncio
    async def test_h2_streaming_response(self, stream_h2_server):
        port = stream_h2_server
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            resp = await client.post(
                f"https://127.0.0.1:{port}/invocations",
                json={},
            )
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/2"
            assert resp.content == b"chunk1chunk2chunk3"

    @pytest.mark.asyncio
    async def test_h2_streaming_has_invocation_id(self, stream_h2_server):
        port = stream_h2_server
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            resp = await client.post(
                f"https://127.0.0.1:{port}/invocations",
                json={},
            )
            assert resp.http_version == "HTTP/2"
            assert "x-agent-invocation-id" in resp.headers


class TestHttp1Fallback:
    """Verify HTTP/1.1 still works (client without h2 negotiation)."""

    @pytest.mark.asyncio
    async def test_http1_invoke(self, echo_h2_server):
        """A client that does not request HTTP/2 gets HTTP/1.1."""
        port = echo_h2_server
        async with httpx.AsyncClient(http2=False, verify=False) as client:
            resp = await client.post(
                f"https://127.0.0.1:{port}/invocations",
                json={"message": "http1"},
            )
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/1.1"


# ===========================================================================
# h2c (HTTP/2 cleartext) — no TLS certificates required
# ===========================================================================


@pytest_asyncio.fixture()
async def echo_h2c_server():
    """Start _EchoAgent on a random port *without* TLS, yield the port."""
    port = _get_free_port()

    agent = _EchoAgent()
    config = HypercornConfig()
    config.bind = [f"127.0.0.1:{port}"]
    config.graceful_timeout = 1.0

    shutdown_event = asyncio.Event()
    task = asyncio.create_task(
        _hypercorn_serve(agent.app, config, shutdown_trigger=shutdown_event.wait)
    )
    await _wait_for_server("127.0.0.1", port)
    yield port

    shutdown_event.set()
    await task


@pytest_asyncio.fixture()
async def stream_h2c_server():
    """Start _StreamAgent on a random port *without* TLS, yield the port."""
    port = _get_free_port()

    agent = _StreamAgent()
    config = HypercornConfig()
    config.bind = [f"127.0.0.1:{port}"]
    config.graceful_timeout = 1.0

    shutdown_event = asyncio.Event()
    task = asyncio.create_task(
        _hypercorn_serve(agent.app, config, shutdown_trigger=shutdown_event.wait)
    )
    await _wait_for_server("127.0.0.1", port)
    yield port

    shutdown_event.set()
    await task


class TestH2cHealth:
    """Verify health endpoints work over h2c (HTTP/2 cleartext)."""

    @pytest.mark.asyncio
    async def test_h2c_liveness(self, echo_h2c_server):
        port = echo_h2c_server
        async with httpx.AsyncClient(http1=False, http2=True) as client:
            resp = await client.get(f"http://127.0.0.1:{port}/liveness")
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/2"
            assert resp.json() == {"status": "alive"}

    @pytest.mark.asyncio
    async def test_h2c_readiness(self, echo_h2c_server):
        port = echo_h2c_server
        async with httpx.AsyncClient(http1=False, http2=True) as client:
            resp = await client.get(f"http://127.0.0.1:{port}/readiness")
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/2"
            assert resp.json() == {"status": "ready"}


class TestH2cInvoke:
    """Verify invocation works over h2c (HTTP/2 cleartext)."""

    @pytest.mark.asyncio
    async def test_h2c_invoke_returns_200(self, echo_h2c_server):
        port = echo_h2c_server
        async with httpx.AsyncClient(http1=False, http2=True) as client:
            resp = await client.post(
                f"http://127.0.0.1:{port}/invocations",
                json={"message": "hello"},
            )
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/2"
            data = resp.json()
            assert "echo" in data

    @pytest.mark.asyncio
    async def test_h2c_invocation_id_header(self, echo_h2c_server):
        port = echo_h2c_server
        async with httpx.AsyncClient(http1=False, http2=True) as client:
            resp = await client.post(
                f"http://127.0.0.1:{port}/invocations",
                json={"message": "test"},
            )
            assert resp.http_version == "HTTP/2"
            assert "x-agent-invocation-id" in resp.headers

    @pytest.mark.asyncio
    async def test_h2c_multiplexing(self, echo_h2c_server):
        """HTTP/2 multiplexing over cleartext: concurrent requests, unique IDs."""
        port = echo_h2c_server
        async with httpx.AsyncClient(http1=False, http2=True) as client:
            responses = await asyncio.gather(
                client.post(f"http://127.0.0.1:{port}/invocations", json={"n": 1}),
                client.post(f"http://127.0.0.1:{port}/invocations", json={"n": 2}),
                client.post(f"http://127.0.0.1:{port}/invocations", json={"n": 3}),
            )
            for resp in responses:
                assert resp.status_code == 200
                assert resp.http_version == "HTTP/2"
            ids = {resp.headers["x-agent-invocation-id"] for resp in responses}
            assert len(ids) == 3


class TestH2cStreaming:
    """Verify streaming responses work over h2c (HTTP/2 cleartext)."""

    @pytest.mark.asyncio
    async def test_h2c_streaming_response(self, stream_h2c_server):
        port = stream_h2c_server
        async with httpx.AsyncClient(http1=False, http2=True) as client:
            resp = await client.post(
                f"http://127.0.0.1:{port}/invocations",
                json={},
            )
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/2"
            assert resp.content == b"chunk1chunk2chunk3"

    @pytest.mark.asyncio
    async def test_h2c_streaming_has_invocation_id(self, stream_h2c_server):
        port = stream_h2c_server
        async with httpx.AsyncClient(http1=False, http2=True) as client:
            resp = await client.post(
                f"http://127.0.0.1:{port}/invocations",
                json={},
            )
            assert resp.http_version == "HTTP/2"
            assert "x-agent-invocation-id" in resp.headers


class TestH2cFallback:
    """Verify HTTP/1.1 still works on the plain-TCP server."""

    @pytest.mark.asyncio
    async def test_h2c_server_accepts_http1(self, echo_h2c_server):
        """A client that only speaks HTTP/1.1 is served normally."""
        port = echo_h2c_server
        async with httpx.AsyncClient(http1=True, http2=False) as client:
            resp = await client.post(
                f"http://127.0.0.1:{port}/invocations",
                json={"message": "http1"},
            )
            assert resp.status_code == 200
            assert resp.http_version == "HTTP/1.1"
