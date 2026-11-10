# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Self-tests for the crash-injection harness (T-052).

Exercises the harness against a trivial built-in HTTP server (not against any
SDK sample) to verify the harness mechanics work before any sample relies on
it: start → ready probe → POST → kill → restart → ready probe.

We use ``http.server`` to spin up a minimal echo server. No httpx server, no
SDK dependencies — just a sanity check that the kill/restart roundtrip
behaves as advertised.
"""

from __future__ import annotations

import errno
import platform
import socket
import textwrap
from pathlib import Path

import pytest

from tests.e2e._crash_harness import CrashHarness

_ECHO_SERVER_SOURCE = textwrap.dedent(
    """
    \"\"\"Minimal echo HTTP server used by crash-harness self-tests.\"\"\"
    import os
    import sys
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


    class _EchoHandler(BaseHTTPRequestHandler):
        # Keep-alive: clients close first, so the server port never enters TIME_WAIT.
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            if self.path == "/health/live":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"OK")
                return
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format, *args):
            pass


    def main():
        port = int(os.environ.get("PORT", "0") or "0")
        server = ThreadingHTTPServer(("127.0.0.1", port), _EchoHandler)
        server.serve_forever()


    if __name__ == "__main__":
        main()
    """
).lstrip()


@pytest.fixture()
def echo_server_path(tmp_path: Path) -> Path:
    path = tmp_path / "echo_server.py"
    path.write_text(_ECHO_SERVER_SOURCE)
    return path


pytestmark = pytest.mark.skipif(
    platform.system() in ("Windows", "Darwin"),
    reason="Self-tests use a throwaway http.server subprocess unreachable on macOS CI; harness is POSIX-only.",
)


@pytest.mark.asyncio
async def test_harness_starts_and_responds_to_health_probe(tmp_path: Path, echo_server_path: Path) -> None:
    """Spawn the harness, hit /health/live via the client, observe 200."""
    harness = CrashHarness(sample_module=echo_server_path, tmp_path=tmp_path)
    await harness.start()
    try:
        response = await harness.client.get("/health/live")
        assert response.status_code == 200
        assert response.text == "OK"
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_harness_kill_terminates_subprocess(tmp_path: Path, echo_server_path: Path) -> None:
    """After kill(), the subprocess pid is gone and client is closed."""
    harness = CrashHarness(sample_module=echo_server_path, tmp_path=tmp_path)
    await harness.start()
    pid = harness.pid
    try:
        assert pid is not None
        await harness.kill()
        assert harness.pid is None
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_harness_kill_then_restart_round_trip(tmp_path: Path, echo_server_path: Path) -> None:
    """Kill + restart yields a fresh subprocess responding to the same port."""
    harness = CrashHarness(sample_module=echo_server_path, tmp_path=tmp_path)
    await harness.start()
    first_pid = harness.pid
    try:
        await harness.kill()
        assert harness.pid is None
        await harness.restart()
        second_pid = harness.pid
        assert second_pid is not None
        assert second_pid != first_pid
        response = await harness.client.get("/health/live")
        assert response.status_code == 200
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_harness_resilient_storage_dirs_persist(tmp_path: Path, echo_server_path: Path) -> None:
    """tmp_path subdirectories survive kill + restart."""
    harness = CrashHarness(sample_module=echo_server_path, tmp_path=tmp_path)
    await harness.start()
    try:
        # The harness pre-creates these.
        assert (tmp_path / "tasks").exists()
        assert (tmp_path / "responses").exists()
        assert (tmp_path / "streams").exists()
        # Write a marker file that the subprocess doesn't touch.
        marker = tmp_path / "responses" / "marker.txt"
        marker.write_text("survives-restart")
        await harness.kill()
        await harness.restart()
        assert marker.read_text() == "survives-restart"
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_harness_close_is_idempotent(tmp_path: Path, echo_server_path: Path) -> None:
    """close() can be called multiple times without raising."""
    harness = CrashHarness(sample_module=echo_server_path, tmp_path=tmp_path)
    await harness.start()
    await harness.close()
    await harness.close()  # second close is a no-op


@pytest.mark.asyncio
async def test_harness_reserves_auto_picked_port_across_restart(tmp_path: Path, echo_server_path: Path) -> None:
    """Other pickers cannot take the auto-picked port before spawn or between lifetimes.

    CI runs wheel and sdist legs concurrently; an unreserved port let a second
    harness lose the bind race and probe the other leg's server as its own.
    """
    harness = CrashHarness(sample_module=echo_server_path, tmp_path=tmp_path)

    def _bind_exclusive() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", harness.port))

    try:
        with pytest.raises(OSError) as before_spawn:
            _bind_exclusive()
        assert before_spawn.value.errno == errno.EADDRINUSE
        await harness.start()
        await harness.kill()
        with pytest.raises(OSError) as between_lifetimes:
            _bind_exclusive()
        assert between_lifetimes.value.errno == errno.EADDRINUSE
        await harness.restart()
        response = await harness.client.get("/health/live")
        assert response.status_code == 200
        await harness.kill()
        with pytest.raises(OSError) as after_restart:
            _bind_exclusive()
        assert after_restart.value.errno == errno.EADDRINUSE
    finally:
        await harness.close()
