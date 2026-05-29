# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Crash-injection harness for cross-process recovery testing (T-051).

Spawns an HTTP server as a subprocess, exposes ``kill()`` (SIGKILL) and
``restart()`` APIs, plus an ``httpx.AsyncClient`` for POST + reconnect. Wires
the subprocess against ``LocalDurableProvider`` + ``FileResponseStore`` +
``FileStreamProvider`` against a common ``tmp_path`` so durable state
survives the kill.

POSIX-only (uses ``os.kill(pid, SIGKILL)``). See spec 013 §Q1 for the
crash-injection mechanism decision.

Usage in a test:

.. code-block:: python

    @pytest.mark.asyncio
    async def test_recovery(tmp_path: Path) -> None:
        harness = CrashHarness(
            sample_module="azure_ai_agentserver_responses_samples.sample_18_durable_copilot",
            tmp_path=tmp_path,
        )
        await harness.start()
        try:
            response = await harness.client.post("/responses", json={"input": "hi"})
            response_id = response.json()["id"]
            await harness.kill()
            await harness.restart()
            await harness.client.get(f"/responses/{response_id}")
        finally:
            await harness.close()
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import os
import signal
import socket
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import httpx


class CrashHarness:
    """Spawn-and-kill harness for cross-process recovery testing.

    :param sample_module: Importable module name (e.g.
        ``"my_pkg.sample_18_durable_copilot"``) or a Python file path. The
        subprocess runs ``python -m <module>`` if given a module name, or
        ``python <path>`` if given a file path.
    :type sample_module: str | ~types.ModuleType | ~pathlib.Path
    :param tmp_path: Storage root. Subdirectories ``tasks/``, ``responses/``,
        ``streams/`` will be created.
    :type tmp_path: ~pathlib.Path
    :param port: Optional explicit port. If ``None``, the harness binds an
        ephemeral port (bind 0, read assignment) and passes it to the
        subprocess via ``PORT`` env var.
    :type port: int | None
    :param readiness_timeout_seconds: How long to wait for the subprocess to
        respond to the ``/health/live`` probe. Default 10.
    :type readiness_timeout_seconds: float
    :param env_extras: Additional environment variables to pass to the
        subprocess. Merged onto the harness's defaults.
    :type env_extras: dict[str, str] | None
    """

    def __init__(
        self,
        sample_module: str | ModuleType | Path,
        tmp_path: Path,
        *,
        port: int | None = None,
        readiness_timeout_seconds: float = 10.0,
        env_extras: dict[str, str] | None = None,
    ) -> None:
        if isinstance(sample_module, ModuleType):
            sample_target = sample_module.__name__
            self._target_kind = "module"
        elif isinstance(sample_module, Path):
            sample_target = str(sample_module)
            self._target_kind = "path"
        else:
            sample_target = sample_module
            # Heuristic: paths contain a separator or end with .py
            if os.sep in sample_target or sample_target.endswith(".py"):
                self._target_kind = "path"
            else:
                self._target_kind = "module"

        self._sample_target = sample_target
        self._tmp_path = Path(tmp_path)
        self._tmp_path.mkdir(parents=True, exist_ok=True)
        (self._tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
        (self._tmp_path / "responses").mkdir(parents=True, exist_ok=True)
        (self._tmp_path / "streams").mkdir(parents=True, exist_ok=True)

        self._port = port if port is not None else self._pick_ephemeral_port()
        self._readiness_timeout = readiness_timeout_seconds
        self._env_extras = dict(env_extras or {})

        self._process: subprocess.Popen[bytes] | None = None
        self._client: httpx.AsyncClient | None = None

    @staticmethod
    def _pick_ephemeral_port() -> int:
        """Pick an ephemeral port by binding to 0 and reading the assignment.

        :returns: A port number believed to be free at this moment. (TOCTOU
            races are possible but unlikely on a single dev box.)
        :rtype: int
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    @property
    def port(self) -> int:
        """Port the subprocess is bound to.

        :rtype: int
        """
        return self._port

    @property
    def base_url(self) -> str:
        """Base URL for the subprocess HTTP server.

        :rtype: str
        """
        return f"http://127.0.0.1:{self._port}"

    @property
    def client(self) -> httpx.AsyncClient:
        """HTTP client pre-configured for the subprocess.

        :raises RuntimeError: If ``start()`` has not been called.
        :rtype: ~httpx.AsyncClient
        """
        if self._client is None:
            raise RuntimeError("CrashHarness.client accessed before start()")
        return self._client

    @property
    def pid(self) -> int | None:
        """PID of the running subprocess, or ``None`` if not running.

        :rtype: int | None
        """
        if self._process is None or self._process.poll() is not None:
            return None
        return self._process.pid

    def _build_env(self) -> dict[str, str]:
        """Compose the subprocess environment.

        Wires PORT and the three durable storage paths so the
        sample can pick them up. Specific environment variable names are a
        convention the sample author honours.

        :rtype: dict[str, str]
        """
        env = dict(os.environ)
        env["PORT"] = str(self._port)
        env["AGENTSERVER_DURABLE_TASKS_PATH"] = str(self._tmp_path / "tasks")
        env["AGENTSERVER_RESPONSE_STORE_PATH"] = str(self._tmp_path / "responses")
        env["AGENTSERVER_STREAM_STORE_PATH"] = str(self._tmp_path / "streams")
        env.update(self._env_extras)
        return env

    def _spawn(self) -> subprocess.Popen[bytes]:
        """Spawn the subprocess.

        :rtype: ~subprocess.Popen
        """
        if self._target_kind == "module":
            cmd = [sys.executable, "-m", self._sample_target]
        else:
            cmd = [sys.executable, self._sample_target]
        return subprocess.Popen(
            cmd,
            env=self._build_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )

    async def _wait_for_ready(self) -> None:
        """Poll ``/health/live`` until the subprocess responds or times out.

        :raises RuntimeError: If the subprocess does not become ready.
        """
        deadline = asyncio.get_event_loop().time() + self._readiness_timeout
        last_error: Exception | None = None
        while asyncio.get_event_loop().time() < deadline:
            # Subprocess may have crashed already.
            if self._process is not None and self._process.poll() is not None:
                stdout, stderr = self._process.communicate()
                raise RuntimeError(
                    "CrashHarness subprocess exited during startup. "
                    f"stdout={stdout!r} stderr={stderr!r}"
                )
            try:
                async with httpx.AsyncClient(timeout=1.0) as probe:
                    response = await probe.get(f"{self.base_url}/health/live")
                if response.status_code < 500:
                    return
            except Exception as exc:  # pylint: disable=broad-exception-caught
                last_error = exc
            await asyncio.sleep(0.1)
        raise RuntimeError(
            f"CrashHarness: subprocess did not become ready within "
            f"{self._readiness_timeout}s (last probe error: {last_error!r})"
        )

    async def start(self) -> None:
        """Spawn the subprocess and wait for it to become ready.

        :raises RuntimeError: If the subprocess fails to start or never becomes ready.
        """
        if self._process is not None:
            raise RuntimeError("CrashHarness already started")
        self._process = self._spawn()
        try:
            await self._wait_for_ready()
        except Exception:
            # Clean up the failed subprocess.
            await self.kill()
            raise
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def kill(self) -> int | None:
        """Send SIGKILL to the subprocess and wait for it to exit.

        :returns: The exit code, or ``None`` if there was no live subprocess.
        :rtype: int | None
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        if self._process is None:
            return None
        if self._process.poll() is not None:
            return self._process.returncode
        try:
            # SIGKILL the whole process group so any children die too.
            os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try:
                self._process.kill()
            except ProcessLookupError:
                pass
        try:
            # Use a short blocking wait — the subprocess just got SIGKILL.
            return self._process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            return None

    async def restart(self) -> None:
        """Restart the subprocess at the same ``tmp_path`` and same port.

        Equivalent to a fresh ``start()`` after a ``kill()``. The durable
        storage under ``tmp_path/{tasks,responses,streams}`` survives, so
        the new subprocess sees the prior state.
        """
        if self._process is not None and self._process.poll() is None:
            await self.kill()
        self._process = None
        # Same port — assume the OS released it after SIGKILL.
        # (Add a brief sleep to allow socket TIME_WAIT to clear if needed.)
        await asyncio.sleep(0.05)
        self._process = self._spawn()
        try:
            await self._wait_for_ready()
        except Exception:
            await self.kill()
            raise
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def terminate(self, *, wait_seconds: float = 30.0) -> int | None:
        """Send SIGTERM to the subprocess and wait for it to exit.

        Unlike :meth:`kill` (SIGKILL), this gives the subprocess a chance
        to run its graceful-shutdown handlers — the in-process shutdown
        loop fires within ``shutdown_grace_period_seconds`` (which the
        test controls via the ``AGENTSERVER_SHUTDOWN_GRACE_SECONDS`` env
        var passed in ``env_extras``).

        Use cases (per ``durability-contract.md`` §Termination paths):

        - **Path A** — pass a long ``wait_seconds`` and configure a long
          grace; the handler completes naturally before grace expires.
        - **Path B** — pass a moderate ``wait_seconds`` and configure a
          SHORT grace; the handler doesn't finish in time and the
          in-process shutdown loop fires the per-row marker before
          subprocess exit.

        :keyword wait_seconds: How long to wait for clean exit before
            falling back to SIGKILL. Should exceed the configured
            ``shutdown_grace_period_seconds`` to give the in-process
            shutdown loop time to run.
        :paramtype wait_seconds: float
        :returns: The exit code, or ``None`` if there was no live subprocess.
        :rtype: int | None
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        if self._process is None:
            return None
        if self._process.poll() is not None:
            return self._process.returncode
        try:
            # SIGTERM the whole process group so children get it too.
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            try:
                self._process.terminate()
            except ProcessLookupError:
                pass
        try:
            return self._process.wait(timeout=wait_seconds)
        except subprocess.TimeoutExpired:
            # Grace exceeded — fall back to SIGKILL so the test can proceed.
            return await self.kill()

    async def close(self) -> None:
        """Tear down the harness and any associated resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        if self._process is not None and self._process.poll() is None:
            await self.kill()
        self._process = None

    async def __aenter__(self) -> "CrashHarness":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
