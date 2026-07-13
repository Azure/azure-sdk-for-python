# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async RLE environment runtime helpers.

These helpers layer a Gymnasium-style ergonomic surface on top of the generated async RLE
operations. Every request is issued through the :class:`~azure.ai.projects.aio.AIProjectClient`
pipeline against the Foundry project endpoint, exactly like the other operation groups.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import time
from typing import Any, Mapping, Optional

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator_async import distributed_trace_async

from ...models import (
    CreateRLSandboxRequest,
    GetMetadataResponse,
    HealthResponse,
    RLEnvironmentState,
    RLSandboxStatus,
    RLStepResult,
    SchemaResponse,
)
from ...operations._patch_rle import (
    _DEFAULT_CREATE_TIMEOUT_S,
    _DEFAULT_POLL_INTERVAL_S,
    _status_matches,
    coerce_action,
    RLEError,
)
from ._operations import (
    RLEnvironmentRuntimeOperations,
    RLEnvironmentsOperations as _RLEnvironmentsOperationsGenerated,
    RLESandboxesOperations,
)


class AsyncRLEEnvironment:
    """Async, Gymnasium-style client for a hosted RLE environment, backed by the project client.

    Instances are created via :meth:`RLEnvironmentsOperations.create_runtime` and lease a sandbox
    from the environment on first use. All requests flow through the owning
    :class:`~azure.ai.projects.aio.AIProjectClient` pipeline and the Foundry project endpoint.
    """

    def __init__(
        self,
        environment_id: str,
        *,
        sandboxes: RLESandboxesOperations,
        runtime: RLEnvironmentRuntimeOperations,
        version: Optional[str] = None,
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        disk: Optional[str] = None,
        env_vars: Optional[Mapping[str, str]] = None,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> None:
        if not environment_id:
            raise ValueError("environment_id is required")
        self.environment_id = environment_id
        self._sandboxes = sandboxes
        self._runtime = runtime
        self._lease_request = CreateRLSandboxRequest(
            version=version,
            cpu=cpu,
            memory=memory,
            disk=disk,
            env_vars=dict(env_vars) if env_vars else None,
        )
        self.create_timeout_s = create_timeout_s
        self.poll_interval_s = poll_interval_s
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

    async def close(self) -> None:
        """Release the leased sandbox, best effort."""
        await self._release_sandbox()

    async def _ensure_leased(self) -> str:
        if self._sandbox_id is not None:
            return self._sandbox_id
        async with self._lease_lock:
            if self._sandbox_id is not None:
                return self._sandbox_id
            sandbox = await self._sandboxes.lease(self.environment_id, self._lease_request)
            if not sandbox.sandbox_id:
                raise RLEError("service did not return a sandbox id")
            sandbox_id = sandbox.sandbox_id
            self._sandbox_id = sandbox_id
            deadline = time.monotonic() + self.create_timeout_s
            while not _status_matches(sandbox.status, RLSandboxStatus.RUNNING):
                if _status_matches(sandbox.status, RLSandboxStatus.FAILED):
                    raise RLEError(f"sandbox {sandbox_id} failed to start: {sandbox.error or 'unknown error'}")
                if time.monotonic() >= deadline:
                    raise RLEError(
                        f"sandbox {sandbox_id} not ready after {self.create_timeout_s:.0f}s "
                        f"(last status: {sandbox.status or 'unknown'})"
                    )
                await asyncio.sleep(self.poll_interval_s)
                sandbox = await self._sandboxes.get_sandbox(self.environment_id, sandbox_id)
            return sandbox_id

    async def _ensure_healthy(self, sandbox_id: str) -> None:
        """Confirm the sandbox reports healthy before issuing a runtime request.

        A failed health probe surfaces as :class:`~azure.core.exceptions.HttpResponseError`,
        consistent with the other operation groups.

        :param sandbox_id: The leased sandbox ID to health-check.
        :type sandbox_id: str
        """
        await self._runtime.health(self.environment_id, sandbox_id)

    async def _ensure_ready(self) -> str:
        """Ensure a sandbox is leased and healthy, returning its ID.

        :return: The ID of the leased, healthy sandbox.
        :rtype: str
        """
        sandbox_id = await self._ensure_leased()
        await self._ensure_healthy(sandbox_id)
        return sandbox_id

    async def _release_sandbox(self) -> None:
        sandbox_id = self._sandbox_id
        if sandbox_id is None:
            return
        self._sandbox_id = None
        try:
            await self._sandboxes.release(self.environment_id, sandbox_id)
        except HttpResponseError:
            pass

    @distributed_trace_async
    async def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs: Any) -> RLStepResult:
        """Start a new episode and return the initial observation.

        :param seed: Optional seed for deterministic episode initialization.
        :type seed: int or None
        :param episode_id: Optional caller-supplied episode identifier.
        :type episode_id: str or None
        :return: The initial step result for the new episode.
        :rtype: ~azure.ai.projects.models.RLStepResult
        """
        sandbox_id = await self._ensure_ready()
        return await self._runtime.reset(self.environment_id, sandbox_id, seed=seed, episode_id=episode_id, **kwargs)

    @distributed_trace_async
    async def step(self, action: Any = None, **action_kwargs: Any) -> RLStepResult:
        """Apply an action and return the resulting observation, reward, and done state.

        :param action: The action to apply, as a mapping or model. Mutually exclusive with keyword fields.
        :type action: any
        :return: The step result after applying the action.
        :rtype: ~azure.ai.projects.models.RLStepResult
        """
        sandbox_id = await self._ensure_ready()
        return await self._runtime.step(self.environment_id, sandbox_id, action=coerce_action(action, action_kwargs))

    @distributed_trace_async
    async def state(self) -> RLEnvironmentState:
        """Return the current environment state.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        sandbox_id = await self._ensure_ready()
        return await self._runtime.state(self.environment_id, sandbox_id)

    @distributed_trace_async
    async def health(self) -> HealthResponse:
        """Return environment health information.

        :return: Environment health information.
        :rtype: ~azure.ai.projects.models.HealthResponse
        """
        sandbox_id = await self._ensure_leased()
        return await self._runtime.health(self.environment_id, sandbox_id)

    @distributed_trace_async
    async def metadata(self) -> GetMetadataResponse:
        """Return environment metadata.

        :return: Environment metadata.
        :rtype: ~azure.ai.projects.models.GetMetadataResponse
        """
        sandbox_id = await self._ensure_ready()
        return await self._runtime.get_metadata(self.environment_id, sandbox_id)

    @distributed_trace_async
    async def schema(self) -> SchemaResponse:
        """Return the environment action and observation schema.

        :return: The environment action and observation schema.
        :rtype: ~azure.ai.projects.models.SchemaResponse
        """
        sandbox_id = await self._ensure_ready()
        return await self._runtime.schema(self.environment_id, sandbox_id)


class RLEnvironmentsOperations(_RLEnvironmentsOperationsGenerated):
    """Async RLE environment operations, extended with a Gymnasium-style runtime helper."""

    def create_runtime(
        self,
        environment_id: str,
        *,
        version: Optional[str] = None,
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        disk: Optional[str] = None,
        env_vars: Optional[Mapping[str, str]] = None,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> AsyncRLEEnvironment:
        """Create an async Gymnasium-style runtime helper that leases a sandbox from an RLE environment.

        The returned :class:`AsyncRLEEnvironment` is an async context manager that leases a sandbox
        on entry, waits until it is ready, and releases it on exit. All requests are issued through
        this client's pipeline and the Foundry project endpoint.

        :param environment_id: The hosted RLE environment ID to lease a sandbox from. Required.
        :type environment_id: str
        :keyword version: Optional environment image version to lease. Defaults to the latest version.
        :paramtype version: str or None
        :keyword cpu: Requested CPU allocation, for example "1" or "500m".
        :paramtype cpu: str or None
        :keyword memory: Requested memory allocation, for example "2Gi".
        :paramtype memory: str or None
        :keyword disk: Requested disk allocation, for example "10Gi".
        :paramtype disk: str or None
        :keyword env_vars: Environment variables to inject into the sandbox.
        :paramtype env_vars: mapping[str, str] or None
        :keyword create_timeout_s: Maximum time to wait for the sandbox to become ready, in seconds.
         Default value is 300.
        :paramtype create_timeout_s: float
        :keyword poll_interval_s: Interval between sandbox readiness polls, in seconds. Default value is 2.
        :paramtype poll_interval_s: float
        :return: An async runtime helper bound to this client.
        :rtype: ~azure.ai.projects.aio.operations.AsyncRLEEnvironment
        """
        sandboxes = RLESandboxesOperations(self._client, self._config, self._serialize, self._deserialize)
        runtime = RLEnvironmentRuntimeOperations(self._client, self._config, self._serialize, self._deserialize)
        return AsyncRLEEnvironment(
            environment_id,
            sandboxes=sandboxes,
            runtime=runtime,
            version=version,
            cpu=cpu,
            memory=memory,
            disk=disk,
            env_vars=env_vars,
            create_timeout_s=create_timeout_s,
            poll_interval_s=poll_interval_s,
        )


__all__ = ["AsyncRLEEnvironment", "RLEnvironmentsOperations"]
