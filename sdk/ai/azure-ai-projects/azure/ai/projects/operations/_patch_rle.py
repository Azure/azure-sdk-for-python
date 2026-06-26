# pylint: disable=line-too-long,useless-suppression,networking-import-outside-azure-core-transport
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""RLE environment helpers."""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from azure.core.tracing.decorator import distributed_trace


_DEFAULT_CONTROL_PLANE = os.environ.get("RLE_CONTROL_PLANE", "http://localhost:5000")
_API_VERSION = "v1.0"
_READY_STATUS = "Running"
_FAILED_STATUS = "Failed"
_TERMINAL_STATUSES = frozenset({_READY_STATUS, _FAILED_STATUS, "Stopped"})


class RLEError(RuntimeError):
    """Raised when a call to an RLE environment fails.

    :keyword status: HTTP status code, when the failure came from an HTTP response.
    :paramtype status: int or None
    :keyword body: Raw response body, if any.
    :paramtype body: str or None
    """

    def __init__(self, message: str, *, status: Optional[int] = None, body: Optional[str] = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


@dataclass
class RLEStepResult:
    """Outcome of an RLE ``reset`` or ``step`` call."""

    observation: Dict[str, Any] = field(default_factory=dict)
    reward: Optional[float] = None
    terminated: bool = False
    truncated: bool = False
    info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def done(self) -> bool:
        """Derived Gymnasium ``done`` flag: ``terminated or truncated``."""
        return self.terminated or self.truncated

    @classmethod
    def from_wire(cls, data: Optional[Dict[str, Any]]) -> "RLEStepResult":
        """Create a result from the RLE service wire payload."""
        data = data or {}
        reward = data.get("reward")
        has_split = "terminated" in data or "truncated" in data
        legacy_done = bool(data.get("done", False))
        terminated = bool(data.get("terminated", False if has_split else legacy_done))
        truncated = bool(data.get("truncated", False))
        info = data.get("info")
        metadata = data.get("metadata") or {}
        return cls(
            observation=data.get("observation") or {},
            reward=float(reward) if isinstance(reward, (int, float)) else None,
            terminated=terminated,
            truncated=truncated,
            info=info if isinstance(info, dict) else dict(metadata),
            metadata=metadata,
            raw=data,
        )


@dataclass
class RLEEnvState:
    """Snapshot returned by an RLE environment ``state`` call."""

    episode_id: Optional[str] = None
    step_count: int = 0
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, data: Optional[Dict[str, Any]]) -> "RLEEnvState":
        """Create an environment state from the RLE service wire payload."""
        data = data or {}
        try:
            step_count = int(data.get("step_count", 0))
        except (TypeError, ValueError):
            step_count = 0
        return cls(episode_id=data.get("episode_id"), step_count=step_count, raw=data)


class _SandboxLease:
    __slots__ = ("id", "status", "url", "error", "raw")

    def __init__(self, payload: Mapping[str, Any]) -> None:
        self.id: str = str(payload.get("id", ""))
        self.status: str = str(payload.get("status", ""))
        self.url: Optional[str] = payload.get("url")
        self.error: Optional[str] = payload.get("error")
        self.raw: Dict[str, Any] = dict(payload)

    @property
    def is_ready(self) -> bool:
        return self.status == _READY_STATUS

    @property
    def is_failed(self) -> bool:
        return self.status == _FAILED_STATUS

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATUSES


def _sandbox_collection_url(control_plane: str, project: str, env_id: str, api_version: str = _API_VERSION) -> str:
    base = control_plane.rstrip("/")
    return f"{base}/rle/{api_version}/projects/{project}/environments/{env_id}/sandboxes"


def _sandbox_url(control_plane: str, project: str, env_id: str, sandbox_id: str, api_version: str = _API_VERSION) -> str:
    return f"{_sandbox_collection_url(control_plane, project, env_id, api_version)}/{sandbox_id}"


def _create_body(
    *,
    version: Optional[str] = None,
    cpu: Optional[float] = None,
    memory: Optional[str] = None,
    disk: Optional[str] = None,
    env_vars: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {}
    if version is not None:
        body["version"] = version
    if cpu is not None:
        body["cpu"] = cpu
    if memory is not None:
        body["memory"] = memory
    if disk is not None:
        body["disk"] = disk
    if env_vars:
        body["envVars"] = dict(env_vars)
    return body


def coerce_action(action: Any, action_kwargs: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize a step action into a plain JSON-serializable dictionary."""
    if action is None:
        return dict(action_kwargs)
    if action_kwargs:
        raise TypeError("pass either a single action mapping or keyword fields, not both")
    if hasattr(action, "model_dump"):
        return action.model_dump()
    if hasattr(action, "to_dict"):
        return action.to_dict()
    if isinstance(action, Mapping):
        return dict(action)
    raise TypeError(f"action must be a mapping or keyword fields, got {type(action).__name__}")


class RLEEnvironment:
    """Gym-style client for a hosted RLE environment leased by environment ID.

    :param env_id: The hosted RLE environment ID. Required.
    :type env_id: str
    :keyword project: The RLE project name. If omitted, ``RLE_PROJECT`` is used.
    :paramtype project: str or None
    :keyword control_plane: The RLE control-plane endpoint. If omitted, ``RLE_CONTROL_PLANE`` is used,
     falling back to ``http://localhost:5000``.
    :paramtype control_plane: str or None
    :keyword api_version: RLE control-plane API version. Default value is ``v1.0``.
    :paramtype api_version: str
    :keyword timeout_s: Per-request timeout, in seconds. Default value is 30.
    :paramtype timeout_s: float
    :keyword headers: Additional HTTP headers sent to the control plane and data plane.
    :paramtype headers: mapping[str, str] or None
    :keyword token: Bearer token used for authorization.
    :paramtype token: str or None
    """

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
        self.endpoint: Optional[str] = None
        self._sandbox_id: Optional[str] = None
        self._lease_lock = threading.Lock()

    def __enter__(self) -> "RLEEnvironment":
        self._ensure_leased()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    @property
    def sandbox_id(self) -> Optional[str]:
        """ID of the leased sandbox, or ``None`` before the first request."""
        return self._sandbox_id

    def close(self) -> None:
        """Release the leased sandbox, best effort."""
        self._release_sandbox()

    def _ensure_leased(self) -> None:
        if self._sandbox_id is not None:
            return
        with self._lease_lock:
            if self._sandbox_id is not None:
                return
            collection = _sandbox_collection_url(self.control_plane, self.project, self.env_id, self.api_version)
            created = _SandboxLease(self._http("POST", collection, _create_body(**self._sandbox_opts)))
            if not created.id:
                raise RLEError("control plane did not return a sandbox id")
            self._sandbox_id = created.id
            lease = created
            sandbox_url = _sandbox_url(self.control_plane, self.project, self.env_id, created.id, self.api_version)
            deadline = time.monotonic() + self.create_timeout_s
            while not lease.is_ready:
                if lease.is_failed:
                    raise RLEError(f"sandbox {created.id} failed to start: {lease.error or 'unknown error'}")
                if time.monotonic() > deadline:
                    raise RLEError(
                        f"sandbox {created.id} not ready after {self.create_timeout_s:.0f}s "
                        f"(last status: {lease.status or 'unknown'})"
                    )
                time.sleep(self.poll_interval_s)
                lease = _SandboxLease(self._http("GET", sandbox_url))
            if not lease.url:
                raise RLEError(f"sandbox {created.id} is Running but reported no data-plane url")
            self.endpoint = lease.url.rstrip("/")

    def _release_sandbox(self) -> None:
        sandbox_id = self._sandbox_id
        if sandbox_id is None:
            return
        self._sandbox_id = None
        self.endpoint = None
        url = _sandbox_url(self.control_plane, self.project, self.env_id, sandbox_id, self.api_version)
        try:
            self._http("DELETE", url, expect_body=False)
        except RLEError:
            pass

    @distributed_trace
    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **extra: Any) -> RLEStepResult:
        """Start a new episode and return the initial observation."""
        body: Dict[str, Any] = {
            key: value for key, value in {"seed": seed, "episode_id": episode_id, **extra}.items() if value is not None
        }
        return RLEStepResult.from_wire(self._request("POST", "/reset", body))

    @distributed_trace
    def step(self, action: Any = None, **action_kwargs: Any) -> RLEStepResult:
        """Apply an action and return the resulting observation, reward, and done state."""
        return RLEStepResult.from_wire(self._request("POST", "/step", {"action": coerce_action(action, action_kwargs)}))

    @distributed_trace
    def state(self) -> RLEEnvState:
        """Return the current environment state."""
        return RLEEnvState.from_wire(self._request("GET", "/state"))

    @distributed_trace
    def health(self) -> Dict[str, Any]:
        """Return environment health information."""
        return self._request("GET", "/health")

    @distributed_trace
    def metadata(self) -> Dict[str, Any]:
        """Return environment metadata."""
        return self._request("GET", "/metadata")

    @distributed_trace
    def schema(self) -> Dict[str, Any]:
        """Return the environment action and observation schema."""
        return self._request("GET", "/schema")

    def _request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._ensure_leased()
        return self._http(method, f"{self.endpoint}{path}", body)

    def _http(
        self,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        *,
        expect_body: bool = True,
    ) -> Dict[str, Any]:
        data = json.dumps(body or {}).encode("utf-8") if method == "POST" else None
        request = urllib.request.Request(url, data=data, headers=self._headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:  # nosec
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as err:
            detail = ""
            try:
                detail = err.read().decode("utf-8", "replace")
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            raise RLEError(f"{method} {url} failed: HTTP {err.code}", status=err.code, body=detail) from err
        except urllib.error.URLError as err:
            raise RLEError(f"{method} {url} failed: {err.reason}") from err

        if not raw or not expect_body:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError as err:
            raise RLEError(f"{method} {url} returned non-JSON body", body=raw) from err


__all__ = ["RLEEnvironment", "RLEStepResult", "RLEEnvState", "RLEError"]