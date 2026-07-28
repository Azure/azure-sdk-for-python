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
from typing import Any, Dict, IO, List, Mapping, Optional, Union, overload

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator_async import distributed_trace_async

from ...models import (
    CreateRLEnvironmentRequest,
    CreateRLESandboxRequest,
    ListRLEnvironmentsResponse,
    ListRLESandboxesResponse,
    RLEnvironment,
    RLEnvironmentState,
    RLEnvironmentVersion,
    RLEResetRequest,
    RLESandbox,
    RLEStepRequest,
    RLEStepResult,
    RLESandboxStatus,
)
from ...operations._patch_rle import (
    _DEFAULT_CREATE_TIMEOUT_S,
    _DEFAULT_POLL_INTERVAL_S,
    _RLE_FEATURE,
    _status_matches,
    coerce_action,
    RLEError,
)
from ._operations import (
    RLEnvironmentsOperations as _RLEnvironmentsOperationsGenerated,
    RLESandboxesOperations,
)


async def _lease_running_sandbox(
    sandboxes: RLESandboxesOperations,
    environment_id: str,
    lease_request: CreateRLESandboxRequest,
    *,
    create_timeout_s: float,
    poll_interval_s: float,
) -> RLESandbox:
    """Lease a sandbox and poll until it reports the ``Running`` status.

    :param sandboxes: Generated async sandbox operations bound to the project client.
    :type sandboxes: ~azure.ai.projects.aio.operations.RLESandboxesOperations
    :param environment_id: The hosted RLE environment ID to lease from.
    :type environment_id: str
    :param lease_request: The sandbox lease request body.
    :type lease_request: ~azure.ai.projects.models.CreateRLESandboxRequest
    :keyword create_timeout_s: Maximum time to wait for the sandbox to become ready, in seconds.
    :paramtype create_timeout_s: float
    :keyword poll_interval_s: Interval between sandbox readiness polls, in seconds.
    :paramtype poll_interval_s: float
    :return: The leased sandbox, once it reports ``Running``.
    :rtype: ~azure.ai.projects.models.RLESandbox
    """
    sandbox = await sandboxes.lease(environment_id, lease_request, foundry_features=_RLE_FEATURE)
    if not sandbox.sandbox_id:
        raise RLEError("service did not return a sandbox id")
    sandbox_id = sandbox.sandbox_id
    deadline = time.monotonic() + create_timeout_s
    while not _status_matches(sandbox.status, RLESandboxStatus.RUNNING):
        if _status_matches(sandbox.status, RLESandboxStatus.FAILED):
            raise RLEError(f"sandbox {sandbox_id} failed to start: {sandbox.error or 'unknown error'}")
        if time.monotonic() >= deadline:
            raise RLEError(
                f"sandbox {sandbox_id} not ready after {create_timeout_s:.0f}s "
                f"(last status: {sandbox.status or 'unknown'})"
            )
        await asyncio.sleep(poll_interval_s)
        sandbox = await sandboxes.get_sandbox(environment_id, sandbox_id, foundry_features=_RLE_FEATURE)
    return sandbox


class AsyncRLEInstance:
    """Async leased RLE sandbox ("instance"), addressable via its data-plane URI.

    An instance is obtained from :meth:`AsyncOpenEnvClient.get_instance`. It wraps a single leased
    sandbox and drives the OpenEnv / Gymnasium runtime operations (``reset``/``step``/``state``)
    against it. Each :meth:`reset` starts a new episode, so an instance may be reused across
    multiple episodes (shared) or scoped to a single episode (exclusive). Runtime requests flow
    through the owning project client's pipeline; :attr:`dataplane_uri` exposes the sandbox's
    data-plane base URL.
    """

    def __init__(
        self,
        environment_id: str,
        *,
        sandbox: RLESandbox,
        sandboxes: RLESandboxesOperations,
        owner: Optional["AsyncOpenEnvClient"] = None,
    ) -> None:
        if not environment_id:
            raise ValueError("environment_id is required")
        if not sandbox.sandbox_id:
            raise RLEError("sandbox is missing an id")
        self._environment_id = environment_id
        self._sandbox = sandbox
        self._sandbox_id: str = sandbox.sandbox_id
        self._sandboxes = sandboxes
        self._owner = owner

    @property
    def instance_id(self) -> str:
        """Identifier of the leased sandbox that backs this instance."""
        return self._sandbox_id

    @property
    def environment_id(self) -> str:
        """The hosted RLE environment ID the instance was leased from."""
        return self._environment_id

    @property
    def dataplane_uri(self) -> Optional[str]:
        """Data-plane base URL for the instance runtime, present once the sandbox is running."""
        return self._sandbox.base_url

    @property
    def sandbox(self) -> RLESandbox:
        """The underlying leased sandbox model."""
        return self._sandbox

    async def __aenter__(self) -> "AsyncRLEInstance":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.checkin()

    async def checkin(self) -> None:
        """Return the instance to its owning :class:`AsyncOpenEnvClient` pool, best effort."""
        owner = self._owner
        if owner is not None:
            await owner._return_instance(self)  # pylint: disable=protected-access

    @distributed_trace_async
    async def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs: Any) -> RLEStepResult:
        """Start a new episode on this instance and return the initial observation.

        :param seed: Optional seed for deterministic episode initialization.
        :type seed: int or None
        :param episode_id: Optional caller-supplied episode identifier.
        :type episode_id: str or None
        :return: The initial step result for the new episode.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        body = RLEResetRequest(seed=seed, episode_id=episode_id)
        return await self._sandboxes.reset(
            self._environment_id, self._sandbox_id, body, foundry_features=_RLE_FEATURE, **kwargs
        )

    @distributed_trace_async
    async def step(self, action: Any = None, **action_kwargs: Any) -> RLEStepResult:
        """Apply an action and return the resulting observation, reward, and done state.

        :param action: The action to apply, as a mapping or model. Mutually exclusive with keyword fields.
        :type action: any
        :return: The step result after applying the action.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        body = RLEStepRequest(action=coerce_action(action, action_kwargs))
        return await self._sandboxes.step(self._environment_id, self._sandbox_id, body, foundry_features=_RLE_FEATURE)

    @distributed_trace_async
    async def state(self) -> RLEnvironmentState:
        """Return the current environment state for this instance.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        return await self._sandboxes.state(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace_async
    async def health(self) -> Dict[str, Any]:
        """Return instance health information.

        :return: Instance health information.
        :rtype: dict[str, any]
        """
        return await self._sandboxes.health(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace_async
    async def metadata(self) -> Dict[str, Any]:
        """Return instance metadata.

        :return: Instance metadata.
        :rtype: dict[str, any]
        """
        return await self._sandboxes.get_metadata(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace_async
    async def schema(self) -> Dict[str, Any]:
        """Return the instance action and observation schema.

        :return: The instance action and observation schema.
        :rtype: dict[str, any]
        """
        return await self._sandboxes.schema(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    async def _release(self) -> None:
        """Release the underlying sandbox, best effort."""
        try:
            await self._sandboxes.release(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)
        except HttpResponseError:
            pass


class AsyncOpenEnvClient:
    """Async client over a hosted RLE (OpenEnv) environment with a reserved concurrency quota.

    Created via :meth:`RLEOperations.get_openenv_client`. On entering its context (or calling
    :meth:`reserve`) the client leases ``min_concurrency`` running instances up front. This is the
    v1 quota model: the customer's concurrency requirement is provided in advance and the request
    fails immediately if the quota cannot be satisfied -- there is no queueing.

    :meth:`get_instance` hands out one of the reserved :class:`AsyncRLEInstance` objects. Closing the
    client releases every leased instance.
    """

    def __init__(
        self,
        *,
        environment_id: str,
        sandboxes: RLESandboxesOperations,
        min_concurrency: int,
        lease_request: CreateRLESandboxRequest,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> None:
        if not environment_id:
            raise ValueError("environment_id is required")
        if min_concurrency < 1:
            raise ValueError("min_concurrency must be >= 1")
        self._environment_id = environment_id
        self._sandboxes = sandboxes
        self._min_concurrency = min_concurrency
        self._lease_request = lease_request
        self._create_timeout_s = create_timeout_s
        self._poll_interval_s = poll_interval_s
        self._pool: List[AsyncRLEInstance] = []
        self._available: List[AsyncRLEInstance] = []
        self._lock = asyncio.Lock()
        self._reserved = False
        self._closed = False

    @property
    def environment_id(self) -> str:
        """The hosted RLE environment ID instances are leased from."""
        return self._environment_id

    @property
    def min_concurrency(self) -> int:
        """Number of instances reserved in advance for this client."""
        return self._min_concurrency

    @property
    def instances(self) -> List[AsyncRLEInstance]:
        """The reserved instances owned by this client."""
        return list(self._pool)

    async def __aenter__(self) -> "AsyncOpenEnvClient":
        await self.reserve()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def reserve(self) -> None:
        """Lease ``min_concurrency`` running instances in advance.

        Idempotent. If the quota cannot be satisfied, any partially-leased instances are released
        and an error is raised (v1 fails fast rather than queueing).
        """
        async with self._lock:
            if self._reserved:
                return
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            try:
                for _ in range(self._min_concurrency):
                    sandbox = await _lease_running_sandbox(
                        self._sandboxes,
                        self._environment_id,
                        self._lease_request,
                        create_timeout_s=self._create_timeout_s,
                        poll_interval_s=self._poll_interval_s,
                    )
                    instance = AsyncRLEInstance(
                        self._environment_id, sandbox=sandbox, sandboxes=self._sandboxes, owner=self
                    )
                    self._pool.append(instance)
                    self._available.append(instance)
            except BaseException:
                await self._release_all_locked()
                raise
            self._reserved = True

    async def get_instance(self) -> AsyncRLEInstance:
        """Check out a reserved instance for one or more episodes.

        The returned :class:`AsyncRLEInstance` is an async context manager; exiting its context
        returns it to the pool. In v1 the pool is bounded by ``min_concurrency`` and this method
        fails when every reserved instance is already checked out -- it does not queue.

        :return: A reserved instance ready to run episodes.
        :rtype: ~azure.ai.projects.aio.operations.AsyncRLEInstance
        """
        async with self._lock:
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            if not self._reserved:
                raise RLEError(
                    "reserve quota first: enter the AsyncOpenEnvClient context or call reserve() before get_instance()"
                )
            if not self._available:
                raise RLEError(
                    f"no instance available within the reserved quota (min_concurrency={self._min_concurrency}); "
                    "v1 does not queue for additional quota"
                )
            return self._available.pop()

    async def _return_instance(self, instance: AsyncRLEInstance) -> None:
        async with self._lock:
            if self._closed:
                return
            if instance in self._pool and instance not in self._available:
                self._available.append(instance)

    async def close(self) -> None:
        """Release every reserved instance, best effort."""
        async with self._lock:
            if self._closed:
                return
            self._closed = True
            await self._release_all_locked()

    async def _release_all_locked(self) -> None:
        pool = list(self._pool)
        self._pool.clear()
        self._available.clear()
        for instance in pool:
            await instance._release()  # pylint: disable=protected-access


class AsyncRLESandboxSession:
    """Async, Gymnasium-style session over a leased RLE sandbox, backed by the project client.

    Instances are created via :meth:`RLEOperations.create_session` and lease a sandbox
    from the environment on first use. All requests flow through the owning
    :class:`~azure.ai.projects.aio.AIProjectClient` pipeline and the Foundry project endpoint.
    """

    def __init__(
        self,
        environment_id: str,
        *,
        sandboxes: RLESandboxesOperations,
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
        self._lease_request = CreateRLESandboxRequest(
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

    async def __aenter__(self) -> "AsyncRLESandboxSession":
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
            sandbox = await self._sandboxes.lease(
                self.environment_id, self._lease_request, foundry_features=_RLE_FEATURE
            )
            if not sandbox.sandbox_id:
                raise RLEError("service did not return a sandbox id")
            sandbox_id = sandbox.sandbox_id
            self._sandbox_id = sandbox_id
            deadline = time.monotonic() + self.create_timeout_s
            while not _status_matches(sandbox.status, RLESandboxStatus.RUNNING):
                if _status_matches(sandbox.status, RLESandboxStatus.FAILED):
                    raise RLEError(f"sandbox {sandbox_id} failed to start: {sandbox.error or 'unknown error'}")
                if time.monotonic() >= deadline:
                    raise RLEError(
                        f"sandbox {sandbox_id} not ready after {self.create_timeout_s:.0f}s "
                        f"(last status: {sandbox.status or 'unknown'})"
                    )
                await asyncio.sleep(self.poll_interval_s)
                sandbox = await self._sandboxes.get_sandbox(
                    self.environment_id, sandbox_id, foundry_features=_RLE_FEATURE
                )
            return sandbox_id

    async def _ensure_healthy(self, sandbox_id: str) -> None:
        """Confirm the sandbox reports healthy before issuing a runtime request.

        A failed health probe surfaces as :class:`~azure.core.exceptions.HttpResponseError`,
        consistent with the other operation groups.

        :param sandbox_id: The leased sandbox ID to health-check.
        :type sandbox_id: str
        """
        await self._sandboxes.health(self.environment_id, sandbox_id, foundry_features=_RLE_FEATURE)

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
            await self._sandboxes.release(self.environment_id, sandbox_id, foundry_features=_RLE_FEATURE)
        except HttpResponseError:
            pass

    @distributed_trace_async
    async def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs: Any) -> RLEStepResult:
        """Start a new episode and return the initial observation.

        :param seed: Optional seed for deterministic episode initialization.
        :type seed: int or None
        :param episode_id: Optional caller-supplied episode identifier.
        :type episode_id: str or None
        :return: The initial step result for the new episode.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        sandbox_id = await self._ensure_ready()
        body = RLEResetRequest(seed=seed, episode_id=episode_id)
        return await self._sandboxes.reset(
            self.environment_id, sandbox_id, body, foundry_features=_RLE_FEATURE, **kwargs
        )

    @distributed_trace_async
    async def step(self, action: Any = None, **action_kwargs: Any) -> RLEStepResult:
        """Apply an action and return the resulting observation, reward, and done state.

        :param action: The action to apply, as a mapping or model. Mutually exclusive with keyword fields.
        :type action: any
        :return: The step result after applying the action.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        sandbox_id = await self._ensure_ready()
        body = RLEStepRequest(action=coerce_action(action, action_kwargs))
        return await self._sandboxes.step(self.environment_id, sandbox_id, body, foundry_features=_RLE_FEATURE)

    @distributed_trace_async
    async def state(self) -> RLEnvironmentState:
        """Return the current environment state.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        sandbox_id = await self._ensure_ready()
        return await self._sandboxes.state(self.environment_id, sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace_async
    async def health(self) -> Dict[str, Any]:
        """Return environment health information.

        :return: Environment health information.
        :rtype: dict[str, any]
        """
        sandbox_id = await self._ensure_leased()
        return await self._sandboxes.health(self.environment_id, sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace_async
    async def metadata(self) -> Dict[str, Any]:
        """Return environment metadata.

        :return: Environment metadata.
        :rtype: dict[str, any]
        """
        sandbox_id = await self._ensure_ready()
        return await self._sandboxes.get_metadata(self.environment_id, sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace_async
    async def schema(self) -> Dict[str, Any]:
        """Return the environment action and observation schema.

        :return: The environment action and observation schema.
        :rtype: dict[str, any]
        """
        sandbox_id = await self._ensure_ready()
        return await self._sandboxes.schema(self.environment_id, sandbox_id, foundry_features=_RLE_FEATURE)


class RLEOperations(_RLEnvironmentsOperationsGenerated, RLESandboxesOperations):
    """Async unified RLE operations over environments and sandboxes, plus a session helper.

    Exposes every generated environment operation (create/list/get/delete) and the sandbox
    read operations (``list_sandboxes``/``get_sandbox``) on a single operation group, accessed
    through the client's ``rle`` attribute. Sandbox lifecycle and per-episode runtime operations
    (lease/reset/step/state/health/metadata/schema/release) are driven through the ergonomic
    :class:`AsyncRLESandboxSession` returned by :meth:`create_session`.
    """

    @overload
    async def create_environment(self, body: CreateRLEnvironmentRequest, **kwargs: Any) -> RLEnvironment: ...
    @overload
    async def create_environment(self, body: IO[bytes], **kwargs: Any) -> RLEnvironment: ...
    @overload
    async def create_environment(
        self, *, acr_image_path: str, name: Optional[str] = None, **kwargs: Any
    ) -> RLEnvironment: ...

    @distributed_trace_async
    async def create_environment(
        self,
        body: Union[CreateRLEnvironmentRequest, IO[bytes], None] = None,
        *,
        acr_image_path: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> RLEnvironment:
        """Create a new hosted RLE environment.

        The required preview feature opt-in is supplied automatically. Pass either a request
        ``body`` or the ``acr_image_path`` (and optional ``name``) keyword fields.

        :param body: The environment to create, as a ``CreateRLEnvironmentRequest`` or ``IO[bytes]``.
         Mutually exclusive with the ``acr_image_path``/``name`` keyword fields.
        :type body: ~azure.ai.projects.models.CreateRLEnvironmentRequest or IO[bytes] or None
        :keyword acr_image_path: Container image reference (ACR path) that backs the environment.
         Required when ``body`` is not supplied.
        :paramtype acr_image_path: str or None
        :keyword name: Optional caller-provided display name for the environment.
        :paramtype name: str or None
        :return: The created RLE environment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        """
        if body is None:
            if acr_image_path is None:
                raise TypeError("pass either a request body or the acr_image_path keyword")
            body = CreateRLEnvironmentRequest(acr_image_path=acr_image_path, name=name)
        elif acr_image_path is not None or name is not None:
            raise TypeError("pass either a request body or keyword fields, not both")
        return await super().create_environment(body, foundry_features=_RLE_FEATURE, **kwargs)

    @distributed_trace_async
    async def list_environments(
        self,
        *,
        name: Optional[str] = None,
        skip: Optional[int] = None,
        top: Optional[int] = None,
        **kwargs: Any,
    ) -> ListRLEnvironmentsResponse:
        """List all hosted RLE environments in the project.

        The required preview feature opt-in is supplied automatically.

        :keyword name: Optional environment name filter. When set, returns at most a single match.
        :paramtype name: str or None
        :keyword skip: Number of environments to skip. Defaults to 0.
        :paramtype skip: int or None
        :keyword top: Maximum number of environments to return. Defaults to 50; range is [1, 200].
        :paramtype top: int or None
        :return: The listing response.
        :rtype: ~azure.ai.projects.models.ListRLEnvironmentsResponse
        """
        return await super().list_environments(foundry_features=_RLE_FEATURE, name=name, skip=skip, top=top, **kwargs)

    @distributed_trace_async
    async def get_environment(self, name: str, **kwargs: Any) -> RLEnvironment:
        """Get a hosted RLE environment by name, returning its latest version.

        The required preview feature opt-in is supplied automatically.

        :param name: Environment name. Required.
        :type name: str
        :return: The RLE environment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        """
        return await super().get_environment(name, foundry_features=_RLE_FEATURE, **kwargs)

    @distributed_trace_async
    async def get_environment_version(self, name: str, version: str, **kwargs: Any) -> RLEnvironment:
        """Get a specific version of a hosted RLE environment.

        The required preview feature opt-in is supplied automatically.

        :param name: Environment name. Required.
        :type name: str
        :param version: Environment version identifier. Required.
        :type version: str
        :return: The RLE environment version.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        """
        return await super().get_environment_version(name, version, foundry_features=_RLE_FEATURE, **kwargs)

    @distributed_trace_async
    async def delete_environment_version(self, name: str, version: str, **kwargs: Any) -> None:
        """Delete a specific version of a hosted RLE environment.

        The required preview feature opt-in is supplied automatically.

        :param name: Environment name. Required.
        :type name: str
        :param version: Environment version identifier. Required.
        :type version: str
        :return: None
        :rtype: None
        """
        return await super().delete_environment_version(name, version, foundry_features=_RLE_FEATURE, **kwargs)

    @distributed_trace_async
    async def list_rl_environment_versions(self, name: str, **kwargs: Any) -> List[RLEnvironmentVersion]:
        """List historical versions of a hosted RLE environment.

        The required preview feature opt-in is supplied automatically.

        :param name: Environment name. Required.
        :type name: str
        :return: The environment versions.
        :rtype: list[~azure.ai.projects.models.RLEnvironmentVersion]
        """
        kwargs.pop("foundry_features", None)
        return await super().list_rl_environment_versions(name, foundry_features=_RLE_FEATURE, **kwargs)

    # --- Sandbox operations (preview feature opt-in supplied automatically) ---

    @distributed_trace_async
    async def list_sandboxes(
        self,
        environment_id: str,
        *,
        skip: Optional[int] = None,
        top: Optional[int] = None,
        **kwargs: Any,
    ) -> ListRLESandboxesResponse:
        """List sandboxes currently leased for an environment.

        The required preview feature opt-in is supplied automatically.

        :param environment_id: Environment identifier whose sandboxes to list. Required.
        :type environment_id: str
        :keyword skip: Number of sandboxes to skip. Defaults to 0.
        :paramtype skip: int or None
        :keyword top: Maximum number of sandboxes to return. Defaults to 50; range is [1, 200].
        :paramtype top: int or None
        :return: The listing response.
        :rtype: ~azure.ai.projects.models.ListRLESandboxesResponse
        """
        kwargs.pop("foundry_features", None)
        return await super().list_sandboxes(environment_id, foundry_features=_RLE_FEATURE, skip=skip, top=top, **kwargs)

    @distributed_trace_async
    async def get_sandbox(self, environment_id: str, sandbox_id: str, **kwargs: Any) -> RLESandbox:
        """Fetch the latest lifecycle state for a leased sandbox.

        The required preview feature opt-in is supplied automatically.

        :param environment_id: Environment identifier the sandbox belongs to. Required.
        :type environment_id: str
        :param sandbox_id: Sandbox identifier. Required.
        :type sandbox_id: str
        :return: The sandbox.
        :rtype: ~azure.ai.projects.models.RLESandbox
        """
        kwargs.pop("foundry_features", None)
        return await super().get_sandbox(environment_id, sandbox_id, foundry_features=_RLE_FEATURE, **kwargs)

    def create_session(
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
    ) -> AsyncRLESandboxSession:
        """Create an async Gymnasium-style session that leases a sandbox from an RLE environment.

        The returned :class:`AsyncRLESandboxSession` is an async context manager that leases a sandbox
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
        :return: An async sandbox session bound to this client.
        :rtype: ~azure.ai.projects.aio.operations.AsyncRLESandboxSession
        """
        return AsyncRLESandboxSession(
            environment_id,
            sandboxes=self,
            version=version,
            cpu=cpu,
            memory=memory,
            disk=disk,
            env_vars=env_vars,
            create_timeout_s=create_timeout_s,
            poll_interval_s=poll_interval_s,
        )

    @distributed_trace_async
    async def get_openenv_client(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        min_concurrency: int = 1,
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        disk: Optional[str] = None,
        env_vars: Optional[Mapping[str, str]] = None,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> AsyncOpenEnvClient:
        """Create an :class:`AsyncOpenEnvClient` over a hosted RLE environment with a reserved quota.

        The environment is resolved by ``name`` (and ``version`` when supplied). The returned client
        is an async context manager: entering it leases ``min_concurrency`` running instances up front
        and fails fast if that quota cannot be satisfied (v1 does not queue).
        :meth:`AsyncOpenEnvClient.get_instance` then hands out reserved :class:`AsyncRLEInstance`
        objects to run episodes on.

        :keyword name: The hosted RLE environment name to resolve. Required.
        :paramtype name: str
        :keyword version: Optional environment image version. When set, the environment is resolved at
         that version and every instance is leased against it; otherwise the latest version is used.
        :paramtype version: str or None
        :keyword min_concurrency: Number of instances to reserve in advance. The customer's concurrency
         requirement, provided up front. Default value is 1.
        :paramtype min_concurrency: int
        :keyword cpu: Requested CPU allocation per instance, for example "1" or "500m".
        :paramtype cpu: str or None
        :keyword memory: Requested memory allocation per instance, for example "2Gi".
        :paramtype memory: str or None
        :keyword disk: Requested disk allocation per instance, for example "10Gi".
        :paramtype disk: str or None
        :keyword env_vars: Environment variables to inject into each instance.
        :paramtype env_vars: mapping[str, str] or None
        :keyword create_timeout_s: Maximum time to wait for each instance to become ready, in seconds.
         Default value is 300.
        :paramtype create_timeout_s: float
        :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 2.
        :paramtype poll_interval_s: float
        :return: An async OpenEnv client bound to this client.
        :rtype: ~azure.ai.projects.aio.operations.AsyncOpenEnvClient
        """
        if not name:
            raise ValueError("name is required")
        if min_concurrency < 1:
            raise ValueError("min_concurrency must be >= 1")
        if version is not None:
            environment = await self.get_environment_version(name, version)
        else:
            environment = await self.get_environment(name)
        environment_id = environment.environment_id
        if not environment_id:
            raise RLEError(f"environment '{name}' did not resolve to an environment id")
        lease_request = CreateRLESandboxRequest(
            version=version,
            cpu=cpu,
            memory=memory,
            disk=disk,
            env_vars=dict(env_vars) if env_vars else None,
        )
        return AsyncOpenEnvClient(
            environment_id=environment_id,
            sandboxes=self,
            min_concurrency=min_concurrency,
            lease_request=lease_request,
            create_timeout_s=create_timeout_s,
            poll_interval_s=poll_interval_s,
        )


__all__ = [
    "AsyncOpenEnvClient",
    "AsyncRLEInstance",
    "AsyncRLESandboxSession",
    "RLEOperations",
]
