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
from typing import IO, Any, Dict, List, Optional, Union

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator_async import distributed_trace_async

from ...models import (
    CreateRLEInstanceGroupRequest,
    CreateRLEnvironmentRequest,
    ListRLEnvironmentsResponse,
    RLEInstance,
    RLEInstanceStatus,
    RLEnvironment,
    RLEnvironmentState,
    RLEnvironmentVersion,
    RLEResetRequest,
    RLEStepRequest,
    RLEStepResult,
)
from ...operations._patch_rle import (
    _DEFAULT_CREATE_TIMEOUT_S,
    _DEFAULT_POLL_INTERVAL_S,
    _parse_retry_after,
    _status_matches,
    coerce_action,
    RLEAtCapacityError,
    RLEError,
    RLEQuotaExceededError,
)
from ._operations import (
    RLEnvironmentsOperations as _RLEnvironmentsOperationsGenerated,
    RLEInstanceGroupsOperations,
    RLEInstancesOperations,
)


async def _acquire_instance(
    instances: RLEInstancesOperations,
    instance_group_id: str,
    *,
    create_timeout_s: float,
    poll_interval_s: float,
) -> RLEInstance:
    """Acquire an instance under a group and poll until it reports the ``Running`` status.

    The service may answer the create request with ``202`` (accepted, no warm instance yet) and a
    ``Retry-After`` hint; in that case the request is re-issued until an instance is provisioned or
    the timeout elapses. A ``429`` response surfaces as :class:`RLEAtCapacityError`.

    :param instances: Generated async instance operations bound to the project client.
    :type instances: ~azure.ai.projects.aio.operations.RLEInstancesOperations
    :param instance_group_id: The instance group to lease an instance from.
    :type instance_group_id: str
    :keyword create_timeout_s: Maximum time to wait for the instance to become ready, in seconds.
    :paramtype create_timeout_s: float
    :keyword poll_interval_s: Interval between instance readiness polls, in seconds.
    :paramtype poll_interval_s: float
    :return: The leased instance, once it reports ``Running``.
    :rtype: ~azure.ai.projects.models.RLEInstance
    """
    deadline = time.monotonic() + create_timeout_s
    captured: Dict[str, Any] = {}

    def _capture(pipeline_response: Any, deserialized: Any, _response_headers: Any) -> Any:
        captured["response"] = pipeline_response.http_response
        return deserialized

    instance: Optional[RLEInstance] = None
    while True:
        try:
            instance = await instances.create_instance(instance_group_id, cls=_capture)
        except HttpResponseError as exc:
            code = getattr(exc.response, "status_code", None)
            if code == 429:
                raise RLEAtCapacityError(
                    f"instance group {instance_group_id} is at capacity",
                    retry_after=_parse_retry_after(exc.response),
                ) from exc
            raise
        status_code = getattr(captured.get("response"), "status_code", None)
        if status_code == 202:
            if time.monotonic() >= deadline:
                raise RLEError(
                    f"instance group {instance_group_id} did not provision an instance "
                    f"within {create_timeout_s:.0f}s"
                )
            await asyncio.sleep(_parse_retry_after(captured.get("response")) or poll_interval_s)
            continue
        break

    if instance is None or not instance.instance_id:
        raise RLEError("service did not return an instance id")
    instance_id = instance.instance_id
    try:
        while not _status_matches(instance.status, RLEInstanceStatus.RUNNING):
            if _status_matches(instance.status, RLEInstanceStatus.FAILED) or _status_matches(
                instance.status, RLEInstanceStatus.CANCELLED
            ):
                raise RLEError(f"instance {instance_id} failed to start: {instance.error or 'unknown error'}")
            if time.monotonic() >= deadline:
                raise RLEError(
                    f"instance {instance_id} not ready after {create_timeout_s:.0f}s "
                    f"(last status: {instance.status or 'unknown'})"
                )
            await asyncio.sleep(poll_interval_s)
            instance = await instances.get_instance(instance_group_id, instance_id)
    except BaseException:
        # The instance was leased but never became usable; release it so it does not leak quota.
        try:
            await instances.release_instance(instance_group_id, instance_id)
        except Exception:  # pylint: disable=broad-except
            pass
        raise
    return instance


class AsyncOpenEnvInstance:
    """A leased RLE instance that runs episodes, addressable by its flat ``instance_id``.

    An instance is obtained from :meth:`AsyncOpenEnvClient.get_instance`. It wraps a single leased
    :class:`~azure.ai.projects.models.RLEInstance` and drives the OpenEnv / Gymnasium runtime
    operations (``reset``/``step``/``state``) against it. Each :meth:`reset` starts a new episode, so
    an instance may run one or more episodes while it is checked out. v1 does not reuse instances:
    exiting the instance's ``async with`` block releases the underlying instance immediately. Runtime
    requests flow through the owning project client's pipeline.

    :param instance_group_id: The instance group the instance was leased from. Required.
    :type instance_group_id: str
    :keyword instance: The leased, running instance that backs this object. Required.
    :paramtype instance: ~azure.ai.projects.models.RLEInstance
    :keyword instances: Generated async instance operations bound to the project client. Required.
    :paramtype instances: ~azure.ai.projects.aio.operations.RLEInstancesOperations
    """

    def __init__(
        self,
        instance_group_id: str,
        *,
        instance: RLEInstance,
        instances: RLEInstancesOperations,
    ) -> None:
        if not instance_group_id:
            raise ValueError("instance_group_id is required")
        if not instance.instance_id:
            raise RLEError("instance is missing an id")
        self._instance_group_id = instance_group_id
        self._instance = instance
        self._instance_id: str = instance.instance_id
        self._instances = instances

    @property
    def id(self) -> str:
        """Identifier of the leased instance that backs this object."""
        return self._instance_id

    @property
    def instance_group_id(self) -> str:
        """The instance group the instance was leased from."""
        return self._instance_group_id

    @property
    def instance(self) -> RLEInstance:
        """The underlying leased instance model."""
        return self._instance

    async def __aenter__(self) -> "AsyncOpenEnvInstance":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.release()

    async def release(self) -> None:
        """Release this leased instance on the service, best effort.

        Invoked automatically on context exit. v1 does not reuse instances: once an instance leaves
        its ``async with`` block the underlying instance is released immediately, which frees its slot
        in the group's reservation so another instance can be leased.
        """
        await self._release()

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
        return await self._instances.reset(
            self._instance_id,
            RLEResetRequest(seed=seed, episode_id=episode_id),
            **kwargs,
        )

    @distributed_trace_async
    async def step(self, action: Any = None, **action_kwargs: Any) -> RLEStepResult:
        """Apply an action and return the resulting observation, reward, and done state.

        :param action: The action to apply, as a mapping or model. Mutually exclusive with keyword fields.
        :type action: any
        :return: The step result after applying the action.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        return await self._instances.step(
            self._instance_id,
            RLEStepRequest(action=coerce_action(action, action_kwargs)),
        )

    @distributed_trace_async
    async def state(self) -> RLEnvironmentState:
        """Return the current environment state for this instance.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        return await self._instances.state(self._instance_id)

    @distributed_trace_async
    async def health(self) -> Dict[str, Any]:
        """Return instance health information.

        :return: Instance health information.
        :rtype: dict[str, any]
        """
        return await self._instances.health(self._instance_id)

    @distributed_trace_async
    async def metadata(self) -> Dict[str, Any]:
        """Return instance metadata.

        :return: Instance metadata.
        :rtype: dict[str, any]
        """
        return await self._instances.get_metadata(self._instance_id)

    @distributed_trace_async
    async def schema(self) -> Dict[str, Any]:
        """Return the instance action and observation schema.

        :return: The instance action and observation schema.
        :rtype: dict[str, any]
        """
        return await self._instances.schema(self._instance_id)

    async def _release(self) -> None:
        """Release the underlying instance, best effort."""
        try:
            await self._instances.release_instance(self._instance_group_id, self._instance_id)
        except HttpResponseError:
            pass


class AsyncOpenEnvClient:
    """An async client over a hosted RLE (OpenEnv) environment with a reserved concurrency quota.

    Created via :meth:`RLEOperations.get_openenv_client`. The environment is resolved lazily by
    ``name`` (optionally pinned to ``version``) when the client is first entered. On entering its
    context the client creates a single instance group that reserves ``num_instances`` concurrent
    instances on the service and fails immediately if that quota cannot be granted -- there is no
    queueing. The service owns the reservation and the pool of instances; this client keeps no local
    pool. Future revisions may relax this with queueing and elastic scaling.

    :meth:`get_instance` leases a running :class:`AsyncOpenEnvInstance` from the group on demand.
    Because each :meth:`AsyncOpenEnvInstance.reset` starts a fresh episode, an instance may run one or
    more episodes while checked out; exiting its context releases the underlying instance immediately
    (v1 does not reuse instances). Leasing more than ``num_instances`` at once fails until an
    outstanding instance is released. Closing the client deletes the group, which releases any
    instances still leased on the service; the client keeps no local list of leased instances.

    :keyword environments: Generated async environment operations used to resolve the environment. Required.
    :paramtype environments: ~azure.ai.projects.aio.operations.RLEnvironmentsOperations
    :keyword instance_groups: Generated async instance group operations bound to the project client. Required.
    :paramtype instance_groups: ~azure.ai.projects.aio.operations.RLEInstanceGroupsOperations
    :keyword instances: Generated async instance operations bound to the project client. Required.
    :paramtype instances: ~azure.ai.projects.aio.operations.RLEInstancesOperations
    :keyword name: The hosted RLE environment name to resolve. Required.
    :paramtype name: str
    :keyword version: Optional environment image version to resolve and lease against.
    :paramtype version: str or None
    :keyword num_instances: Concurrency to reserve on the group. Defaults to 1.
    :paramtype num_instances: int
    :keyword create_timeout_s: Maximum time to wait for each leased instance to become ready, in
     seconds. Default value is 300.
    :paramtype create_timeout_s: float
    :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 2.
    :paramtype poll_interval_s: float
    """

    def __init__(
        self,
        *,
        environments: _RLEnvironmentsOperationsGenerated,
        instance_groups: RLEInstanceGroupsOperations,
        instances: RLEInstancesOperations,
        name: str,
        version: Optional[str] = None,
        num_instances: int = 1,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> None:
        if not name:
            raise ValueError("name is required")
        if num_instances < 1:
            raise ValueError("num_instances must be >= 1")
        self._environments = environments
        self._instance_groups = instance_groups
        self._instances = instances
        self._name = name
        self._version = version
        self._num_instances = num_instances
        self._create_timeout_s = create_timeout_s
        self._poll_interval_s = poll_interval_s
        self._environment_name: Optional[str] = None
        self._environment_version: Optional[str] = None
        self._instance_group_id: Optional[str] = None
        self._lock = asyncio.Lock()
        self._closed = False

    @property
    def instance_group_id(self) -> Optional[str]:
        """The instance group id backing this client, once created (else ``None``)."""
        return self._instance_group_id

    @property
    def num_instances(self) -> int:
        """Concurrency the instance group reserves on the service for this client."""
        return self._num_instances

    async def __aenter__(self) -> "AsyncOpenEnvClient":
        await self._resolve_environment()
        await self._ensure_group()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def _resolve_environment(self) -> None:
        """Resolve ``name``/``version`` to a concrete environment name and version.

        Invoked on context entry (``__aenter__``) before reservation, so a missing environment
        surfaces when the client is entered. Idempotent: a second call is a no-op once resolved. The
        instance group create request requires a pinned environment version, so the latest version is
        resolved when the caller did not supply one.
        """
        if self._environment_name is not None:
            return
        if self._version is not None:
            environment = await self._environments.get_environment_version(self._name, self._version)
        else:
            environment = await self._environments.get_environment(self._name)
        environment_name = getattr(environment, "name", None) or self._name
        environment_version = self._version or getattr(environment, "version", None)
        if not environment_version:
            raise RLEError(f"environment '{self._name}' did not resolve to a version")
        self._environment_name = environment_name
        self._environment_version = environment_version

    async def _ensure_group(self) -> None:
        """Create the instance group that reserves this client's concurrency on the service.

        Idempotent: a second call is a no-op once the group exists. The group reserves capacity for
        ``num_instances`` concurrent instances; the service owns that reservation and the pool, and
        hands instances out (tracking how many remain) as :meth:`get_instance` leases them. If the
        quota cannot be satisfied the service returns ``403`` and this raises
        :class:`RLEQuotaExceededError` (v1 fails fast rather than queueing).
        """
        async with self._lock:
            if self._instance_group_id is not None:
                return
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            if self._environment_name is None:
                await self._resolve_environment()
            try:
                group = await self._instance_groups.create_instance_group(
                    CreateRLEInstanceGroupRequest(
                        environment_name=self._environment_name,
                        environment_version=self._environment_version,
                        instance_count=self._num_instances,
                    ),
                )
            except HttpResponseError as exc:
                if getattr(exc.response, "status_code", None) == 403:
                    raise RLEQuotaExceededError(
                        f"quota exceeded creating an instance group for environment '{self._name}'"
                    ) from exc
                raise
            if not group.instance_group_id:
                raise RLEError("service did not return an instance group id")
            self._instance_group_id = group.instance_group_id

    async def get_instance(self) -> AsyncOpenEnvInstance:
        """Lease a running instance from the group for one or more episodes.

        This leases an instance from the service on demand: it creates an instance under the group and
        waits (up to ``create_timeout_s``) for it to report ``Running``. The service owns the pool and
        the reservation -- there is no client-side pool. Because the group reserves ``num_instances``
        concurrent instances, leasing more than that at once fails with :class:`RLEAtCapacityError`
        (``429``) until an outstanding instance is released; v1 does not queue for additional quota.

        The returned :class:`AsyncOpenEnvInstance` is an async context manager; exiting its context
        releases the underlying instance back to the service immediately (v1 does not reuse instances).
        The service owns the pool and the reservation, so this client keeps no local bookkeeping of
        leased instances; closing the client deletes the group, which releases any instances still
        leased.

        :return: A leased instance ready to run episodes.
        :rtype: ~azure.ai.projects.aio.operations.AsyncOpenEnvInstance
        """
        async with self._lock:
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            group_id = self._instance_group_id
        if group_id is None:
            raise RLEError("reserve quota first: enter the AsyncOpenEnvClient context before get_instance()")
        instance = await _acquire_instance(
            self._instances,
            group_id,
            create_timeout_s=self._create_timeout_s,
            poll_interval_s=self._poll_interval_s,
        )
        openenv_instance = AsyncOpenEnvInstance(group_id, instance=instance, instances=self._instances)
        async with self._lock:
            if self._closed:
                await openenv_instance._release()  # pylint: disable=protected-access
                raise RLEError("OpenEnv client is closed")
        return openenv_instance

    async def close(self) -> None:
        """Tear down the instance group, best effort.

        The service releases any instances still leased under the group when it is deleted, so this
        client does not release them individually.
        """
        async with self._lock:
            if self._closed:
                return
            self._closed = True
            await self._close_group_locked()

    async def _close_group_locked(self) -> None:
        group_id = self._instance_group_id
        if group_id is None:
            return
        self._instance_group_id = None
        try:
            await self._instance_groups.delete_instance_group(group_id)
        except HttpResponseError:
            pass


class RLEOperations:
    """Async operations for hosted RLE environments, accessed through the client's ``rle`` attribute.

    This operation group exposes environment management (:meth:`create_environment`,
    :meth:`list_environments`, :meth:`get_environment`, :meth:`get_environment_version`,
    :meth:`list_environment_versions`, :meth:`delete_environment_version`) alongside
    :meth:`get_openenv_client`, which resolves a hosted RLE environment and returns an
    :class:`AsyncOpenEnvClient`. Episodes are then driven through that client and the
    :class:`AsyncOpenEnvInstance` objects it hands out (reset/step/state/health/metadata/schema).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._environments = _RLEnvironmentsOperationsGenerated(*args, **kwargs)
        self._instance_groups = RLEInstanceGroupsOperations(*args, **kwargs)
        self._instances = RLEInstancesOperations(*args, **kwargs)

    @distributed_trace_async
    async def create_environment(
        self, body: Union[CreateRLEnvironmentRequest, IO[bytes]], **kwargs: Any
    ) -> RLEnvironment:
        """Create a new hosted RLE environment.

        :param body: The environment to create. Is either a
         :class:`~azure.ai.projects.models.CreateRLEnvironmentRequest` or a binary body. Required.
        :type body: ~azure.ai.projects.models.CreateRLEnvironmentRequest or IO[bytes]
        :return: The created RLEnvironment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._environments.create_environment(body, **kwargs)

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

        :keyword name: Optional environment name filter. When set, returns at most a single matching
         environment. Default value is None.
        :paramtype name: str or None
        :keyword skip: Number of environments to skip. Defaults to 0. Default value is None.
        :paramtype skip: int or None
        :keyword top: Maximum number of environments to return. Defaults to 50; valid range is
         [1, 200]. Default value is None.
        :paramtype top: int or None
        :return: The list of hosted RLE environments.
        :rtype: ~azure.ai.projects.models.ListRLEnvironmentsResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._environments.list_environments(name=name, skip=skip, top=top, **kwargs)

    @distributed_trace_async
    async def get_environment(self, name: str, **kwargs: Any) -> RLEnvironment:
        """Get a hosted RLE environment by name. Returns the latest version of the environment.

        :param name: Environment name. Required.
        :type name: str
        :return: The requested RLEnvironment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._environments.get_environment(name, **kwargs)

    @distributed_trace_async
    async def get_environment_version(self, name: str, version: str, **kwargs: Any) -> RLEnvironment:
        """Get a specific version of a hosted RLE environment by name and version.

        :param name: Environment name. Required.
        :type name: str
        :param version: Environment version identifier. Required.
        :type version: str
        :return: The requested RLEnvironment at the given version.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._environments.get_environment_version(name, version, **kwargs)

    @distributed_trace_async
    async def list_environment_versions(self, name: str, **kwargs: Any) -> List[RLEnvironmentVersion]:
        """List historical versions of a hosted RLE environment.

        :param name: Environment name. Required.
        :type name: str
        :return: The list of environment versions.
        :rtype: list[~azure.ai.projects.models.RLEnvironmentVersion]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._environments.list_rl_environment_versions(name, **kwargs)

    @distributed_trace_async
    async def delete_environment_version(self, name: str, version: str, **kwargs: Any) -> None:
        """Delete a specific version of a hosted RLE environment.

        :param name: Environment name. Required.
        :type name: str
        :param version: Environment version identifier. Required.
        :type version: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        await self._environments.delete_environment_version(name, version, **kwargs)

    def get_openenv_client(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        num_instances: int = 1,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> AsyncOpenEnvClient:
        """Create an :class:`AsyncOpenEnvClient` over a hosted RLE environment.

        This constructs the client without any network I/O (no awaiting needed), so callers can write
        ``async with client.rle.get_openenv_client(...) as openenv_client:``. The returned client is an
        async context manager: entering it resolves the environment by ``name`` (and ``version`` when
        supplied) -- so a missing or invalid environment fails on entry -- then creates an instance
        group that reserves its concurrency on the service and fails fast if that quota cannot be
        granted (v1 does not queue). :meth:`AsyncOpenEnvClient.get_instance` then leases running
        :class:`AsyncOpenEnvInstance` objects from the group on demand to run episodes on.

        :keyword name: The hosted RLE environment name to resolve. Required.
        :paramtype name: str
        :keyword version: Optional environment image version. When set, the environment is resolved at
         that version and the instance group is pinned to it; otherwise the latest version is used.
        :paramtype version: str or None
        :keyword num_instances: Concurrency to reserve on the group, so that several episodes can run
         concurrently on the event loop. Defaults to 1.
        :paramtype num_instances: int
        :keyword create_timeout_s: Maximum time to wait for each leased instance to become ready, in
         seconds. Default value is 300.
        :paramtype create_timeout_s: float
        :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 2.
        :paramtype poll_interval_s: float
        :return: An async OpenEnv client bound to this client.
        :rtype: ~azure.ai.projects.aio.operations.AsyncOpenEnvClient
        """
        if not name:
            raise ValueError("name is required")
        return AsyncOpenEnvClient(
            environments=self._environments,
            instance_groups=self._instance_groups,
            instances=self._instances,
            name=name,
            version=version,
            num_instances=num_instances,
            create_timeout_s=create_timeout_s,
            poll_interval_s=poll_interval_s,
        )


__all__ = [
    "AsyncOpenEnvClient",
    "AsyncOpenEnvInstance",
    "RLEOperations",
]
