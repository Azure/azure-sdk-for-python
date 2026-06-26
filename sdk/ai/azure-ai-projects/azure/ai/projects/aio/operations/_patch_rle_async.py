# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async RLE environment helpers."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, Mapping, Optional

from azure.core.tracing.decorator_async import distributed_trace_async

from ...operations._patch_rle import (
    _API_VERSION,
    _DEFAULT_CONTROL_PLANE,
    _SandboxLease,
    _create_body,
    _sandbox_collection_url,
    _sandbox_url,
    coerce_action,
    RLEError,
    RLEEnvState,
    RLEStepResult,
)


class AsyncRLEEnvironment:
    """Async, gym-style client for a hosted RLE environment leased by environment ID."""

    def __init__(
        self,
        env_id: str,
        *,
        project: Optional[str] = None,
        control_plane: Optional[str] = None,
        api_version: str = _API_VERSION,
        timeout_s: float = 30.0,
        headers: Optional[Mapping[str, str]] = None,
        token: Optional[str] = None,
        session: Any = None,
        version: Optional[str] = None,
        cpu: Optional[float] = None,
        memory: Optional[str] = None,
        disk: Optional[str] = None,
        env_vars: Optional[Mapping[str, str]] = None,
        create_timeout_s: float = 300.0,
        poll_interval_s: float = 2.0,
    ) -> None:
        if not env_id:
            raise ValueError("env_id is required")
        project = project or os.environ.get("RLE_PROJECT")
        if not project:
            raise ValueError("project is required (pass project= or set RLE_PROJECT)")
        self.env_id = env_id
        self.project = project
        self.control_plane = (control_plane or _DEFAULT_CONTROL_PLANE).rstrip("/")
        self.api_version = api_version
        self.timeout_s = timeout_s
        self.create_timeout_s = create_timeout_s
        self.poll_interval_s = poll_interval_s
        self._sandbox_opts = {
            "version": version,
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "env_vars": env_vars,
        }
        self._headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
        if headers:
            self._headers.update(headers)
        if token:
            self._headers["Authorization"] = f"Bearer {token}"
        self._session = session
        self._owns_session = session is None
        self.endpoint: Optional[str] = None
        self._sandbox_id: Optional[str] = None
        self._lease_lock = asyncio.Lock()

    async def __aenter__(self) -> "AsyncRLEEnvironment":
        await self._ensure_leased()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    @property
    def sandbox_id(self) -> Optional[str]:
        """ID of the leased sandbox, or ``None`` before the first request."""
        return self._sandbox_id

    async def _get_session(self) -> Any:
        if self._session is None:
            import aiohttp

            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Release the leased sandbox and close the owned HTTP session."""
        try:
            await self._release_sandbox()
        finally:
            if self._owns_session and self._session is not None:
                await self._session.close()
                self._session = None

    async def _ensure_leased(self) -> None:
        if self._sandbox_id is not None:
            return
        async with self._lease_lock:
            if self._sandbox_id is not None:
                return
            collection = _sandbox_collection_url(self.control_plane, self.project, self.env_id, self.api_version)
            created = _SandboxLease(await self._control_request("POST", collection, _create_body(**self._sandbox_opts)))
            if not created.id:
                raise RLEError("control plane did not return a sandbox id")
            self._sandbox_id = created.id
            lease = created
            loop = asyncio.get_running_loop()
            deadline = loop.time() + self.create_timeout_s
            sandbox_url = _sandbox_url(self.control_plane, self.project, self.env_id, created.id, self.api_version)
            while not lease.is_ready:
                if lease.is_failed:
                    raise RLEError(f"sandbox {created.id} failed to start: {lease.error or 'unknown error'}")
                if loop.time() > deadline:
                    raise RLEError(
                        f"sandbox {created.id} not ready after {self.create_timeout_s:.0f}s "
                        f"(last status: {lease.status or 'unknown'})"
                    )
                await asyncio.sleep(self.poll_interval_s)
                lease = _SandboxLease(await self._control_request("GET", sandbox_url))
            if not lease.url:
                raise RLEError(f"sandbox {created.id} is Running but reported no data-plane url")
            self.endpoint = lease.url.rstrip("/")

    async def _release_sandbox(self) -> None:
        sandbox_id = self._sandbox_id
        if sandbox_id is None:
            return
        self._sandbox_id = None
        self.endpoint = None
        url = _sandbox_url(self.control_plane, self.project, self.env_id, sandbox_id, self.api_version)
        try:
            await self._control_request("DELETE", url, expect_body=False)
        except RLEError:
            pass

    @distributed_trace_async
    async def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **extra: Any) -> RLEStepResult:
        """Start a new episode and return the initial observation."""
        body: Dict[str, Any] = {
            key: value for key, value in {"seed": seed, "episode_id": episode_id, **extra}.items() if value is not None
        }
        return RLEStepResult.from_wire(await self._request("POST", "/reset", body))

    @distributed_trace_async
    async def step(self, action: Any = None, **action_kwargs: Any) -> RLEStepResult:
        """Apply an action and return the resulting observation, reward, and done state."""
        return RLEStepResult.from_wire(await self._request("POST", "/step", {"action": coerce_action(action, action_kwargs)}))

    @distributed_trace_async
    async def state(self) -> RLEEnvState:
        """Return the current environment state."""
        return RLEEnvState.from_wire(await self._request("GET", "/state"))

    @distributed_trace_async
    async def health(self) -> Dict[str, Any]:
        """Return environment health information."""
        return await self._request("GET", "/health")

    @distributed_trace_async
    async def metadata(self) -> Dict[str, Any]:
        """Return environment metadata."""
        return await self._request("GET", "/metadata")

    @distributed_trace_async
    async def schema(self) -> Dict[str, Any]:
        """Return the environment action and observation schema."""
        return await self._request("GET", "/schema")

    async def _request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        await self._ensure_leased()
        return await self._http(method, f"{self.endpoint}{path}", body)

    async def _control_request(
        self, method: str, url: str, body: Optional[Dict[str, Any]] = None, *, expect_body: bool = True
    ) -> Dict[str, Any]:
        return await self._http(method, url, body, send_body=method == "POST", expect_body=expect_body)

    async def _http(
        self,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        *,
        send_body: Optional[bool] = None,
        expect_body: bool = True,
    ) -> Dict[str, Any]:
        import aiohttp

        session = await self._get_session()
        timeout = aiohttp.ClientTimeout(total=self.timeout_s)
        if send_body is None:
            send_body = method == "POST"
        payload = (body or {}) if send_body else None
        try:
            async with session.request(method, url, json=payload, headers=self._headers, timeout=timeout) as response:
                text = await response.text()
                if response.status >= 400:
                    raise RLEError(f"{method} {url} failed: HTTP {response.status}", status=response.status, body=text)
        except aiohttp.ClientError as err:
            raise RLEError(f"{method} {url} failed: {err}") from err

        if not text or not expect_body:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            raise RLEError(f"{method} {url} returned non-JSON body", body=text) from err


__all__ = ["AsyncRLEEnvironment"]