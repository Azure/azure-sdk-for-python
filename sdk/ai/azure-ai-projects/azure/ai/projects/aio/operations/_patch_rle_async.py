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
from typing import Any, Callable, Dict, Optional, Union

from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.exceptions import AzureError, HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ...models import (
    CreateRLEInstanceGroupRequest,
    CreateRLEnvironmentRequest,
    ListRLEnvironmentVersionsResponse,
    ListRLEnvironmentsResponse,
    RLEInstance,
    RLEInstanceStatus,
    RLEnvironment,
    RLEnvironmentState,
    RLEnvironmentVersionBump,
    RLEPaginationOrder,
    RLEResetRequest,
    RLEStepRequest,
    RLEStepResult,
)
from ...operations._patch_rle import (
    _DEFAULT_INSTANCE_ACQUIRE_TIMEOUT_S,
    _DEFAULT_POLL_INTERVAL_S,
    _TRANSIENT_HEALTH_STATUS_CODES,
    _capacity_retry,
    _error_code,
    _is_healthy_response,
    _is_quota_exceeded_error,
    _parse_retry_after,
    _status_matches,
    _validate_instance_acquire_timeout,
    _validate_pagination_limit,
    coerce_action,
    RLEError,
    RLEInstanceAcquireTimeoutError,
    RLEQuotaExceededError,
)
from ._operations import (
    RLEnvironmentsOperations as _RLEnvironmentsOperationsGenerated,
    RLEInstanceGroupsOperations,
    RLEInstancesOperations,
    RLEInstanceRuntimeOperations,
)


async def _sleep_before_deadline(delay: float, deadline: float) -> bool:
    remaining = deadline - time.monotonic()
    if remaining <= 0 or delay >= remaining:
        return False
    await asyncio.sleep(max(0.0, delay))
    return True


async def _acquire_instance(
    instances: RLEInstancesOperations,
    runtime: RLEInstanceRuntimeOperations,
    environment_name: str,
    environment_version: str,
    instance_group_id: str,
    *,
    instance_acquire_timeout: float,
    poll_interval_s: float,
) -> RLEInstance:
    """Acquire an instance under a group and wait until its runtime reports healthy.

    The service may answer the create request with ``202`` (accepted, still provisioning). The create
    operation is not idempotent, so the pending instance returned by the ``202`` is polled by its id
    (honoring any ``Retry-After`` hint on the first wait) until it reports ``Running`` -- the create is
    never re-issued. A ``429`` ``InstanceGroupAtCapacity`` response is retried using its
    ``Retry-After`` hint until the shared acquisition deadline expires. Once control-plane status is
    ``Running``, the runtime health endpoint is polled until it reports healthy.

    :param instances: Generated async instance operations bound to the project client.
    :type instances: ~azure.ai.projects.aio.operations.RLEInstancesOperations
    :param runtime: Generated async instance runtime operations bound to the project client.
    :type runtime: ~azure.ai.projects.aio.operations.RLEInstanceRuntimeOperations
    :param environment_name: The environment name that owns the instance group.
    :type environment_name: str
    :param environment_version: The resolved environment version.
    :type environment_version: str
    :param instance_group_id: The instance group to lease an instance from.
    :type instance_group_id: str
    :keyword instance_acquire_timeout: Maximum time to acquire a healthy instance, in seconds.
    :paramtype instance_acquire_timeout: float
    :keyword poll_interval_s: Interval between instance readiness polls, in seconds.
    :paramtype poll_interval_s: float
    :return: The leased instance, once it reports ``Running`` and healthy.
    :rtype: ~azure.ai.projects.models.RLEInstance
    """
    deadline = time.monotonic() + instance_acquire_timeout
    captured: Dict[str, Any] = {}

    def _capture(pipeline_response: Any, deserialized: Any, _response_headers: Any) -> Any:
        captured["response"] = pipeline_response.http_response
        return deserialized

    while True:
        captured.clear()
        try:
            instance = await instances.create_instance(
                environment_name,
                environment_version,
                instance_group_id,
                cls=_capture,
            )
            break
        except HttpResponseError as exc:
            capacity_retry = _capacity_retry(exc, poll_interval_s)
            if capacity_retry is None:
                raise
            details, retry_after = capacity_retry
            if not await _sleep_before_deadline(retry_after, deadline):
                raise RLEInstanceAcquireTimeoutError(
                    f"instance group {instance_group_id} remained at capacity for "
                    f"{instance_acquire_timeout:.0f}s",
                    timeout=instance_acquire_timeout,
                    last_status=_error_code(details),
                    details=details,
                ) from exc
    if instance is None or not instance.instance_id:
        raise RLEError("service did not return an instance id")
    instance_id = instance.instance_id

    # The initial (possibly 202) response may carry a Retry-After hint for the first poll.
    initial_retry_after = _parse_retry_after(captured.get("response"))
    next_wait = initial_retry_after if initial_retry_after is not None else poll_interval_s
    try:
        while not _status_matches(instance.status, RLEInstanceStatus.RUNNING):
            if any(
                _status_matches(instance.status, terminal_status)
                for terminal_status in (
                    RLEInstanceStatus.STOPPED,
                    RLEInstanceStatus.FAILED,
                    RLEInstanceStatus.DELETED,
                )
            ):
                raise RLEError(
                    f"instance {instance_id} failed to start: {instance.error or 'unknown error'}"
                )
            if time.monotonic() >= deadline:
                last_status = str(
                    getattr(instance.status, "value", instance.status) or "unknown"
                )
                raise RLEInstanceAcquireTimeoutError(
                    f"instance {instance_id} not ready after {instance_acquire_timeout:.0f}s "
                    f"(last status: {last_status})",
                    timeout=instance_acquire_timeout,
                    last_status=last_status,
                )
            if not await _sleep_before_deadline(next_wait, deadline):
                last_status = str(
                    getattr(instance.status, "value", instance.status) or "unknown"
                )
                raise RLEInstanceAcquireTimeoutError(
                    f"instance {instance_id} not ready after {instance_acquire_timeout:.0f}s "
                    f"(last status: {last_status})",
                    timeout=instance_acquire_timeout,
                    last_status=last_status,
                )
            next_wait = poll_interval_s
            instance = await instances.get_instance(
                environment_name,
                environment_version,
                instance_group_id,
                instance_id,
            )

        while True:
            try:
                health = await runtime.health(
                    environment_name,
                    environment_version,
                    instance_group_id,
                    instance_id,
                )
                if _is_healthy_response(health):
                    break
            except HttpResponseError as exc:
                if (
                    getattr(exc.response, "status_code", None)
                    not in _TRANSIENT_HEALTH_STATUS_CODES
                ):
                    raise
            if not await _sleep_before_deadline(poll_interval_s, deadline):
                raise RLEInstanceAcquireTimeoutError(
                    f"instance {instance_id} runtime was not healthy after "
                    f"{instance_acquire_timeout:.0f}s",
                    timeout=instance_acquire_timeout,
                    last_status="Unhealthy",
                )
    except BaseException:
        # The instance was leased but never became usable; release it so it does not leak quota.
        try:
            await instances.delete_instance(
                environment_name,
                environment_version,
                instance_group_id,
                instance_id,
            )
        except Exception:  # pylint: disable=broad-except
            pass
        raise
    return instance


class AsyncOpenEnvInstance:  # pylint: disable=too-many-instance-attributes
    """A leased RLE instance that runs episodes under a resolved environment version.

    An instance context is obtained from :meth:`AsyncOpenEnvClient.get_instance`. Entering it leases a
    running :class:`~azure.ai.projects.models.RLEInstance`; the instance then drives the OpenEnv /
    Gymnasium runtime operations (``reset``/``step``/``state``). Each :meth:`reset` starts a new
    episode, so an instance may run one or more episodes while it is checked out. Exiting the
    instance's ``async with`` block releases the underlying instance immediately.

    :param environment_name: The environment that owns the instance group. Required.
    :type environment_name: str
    :param instance_group_id: The instance group to lease from. Required.
    :type instance_group_id: str
    :keyword environment_version: Resolved environment version that owns the instance group.
    :paramtype environment_version: str
    :keyword instances: Generated async instance lifecycle operations bound to the project client. Required.
    :paramtype instances: ~azure.ai.projects.aio.operations.RLEInstancesOperations
    :keyword runtime: Generated async instance runtime operations bound to the project client. Required.
    :paramtype runtime: ~azure.ai.projects.aio.operations.RLEInstanceRuntimeOperations
    """

    def __init__(
        self,
        environment_name: str,
        instance_group_id: str,
        *,
        environment_version: str,
        instances: RLEInstancesOperations,
        runtime: RLEInstanceRuntimeOperations,
        instance_acquire_timeout: float,
        poll_interval_s: float,
        is_client_closed: Callable[[], bool],
    ) -> None:
        if not environment_name:
            raise ValueError("environment_name is required")
        if not instance_group_id:
            raise ValueError("instance_group_id is required")
        if not environment_version:
            raise ValueError("environment_version is required")
        self._environment_name = environment_name
        self._environment_version = environment_version
        self._instance_group_id = instance_group_id
        self._instances = instances
        self._runtime = runtime
        self._instance_acquire_timeout = instance_acquire_timeout
        self._poll_interval_s = poll_interval_s
        self._is_client_closed = is_client_closed
        self._instance: Optional[RLEInstance] = None
        self._instance_id: Optional[str] = None
        self._released = False

    @property
    def id(self) -> str:
        """Identifier of the leased instance that backs this object."""
        if self._instance_id is None:
            if self._released:
                raise RLEError("instance has been released")
            raise RLEError(
                "enter the AsyncOpenEnvInstance context before accessing the instance"
            )
        return self._instance_id

    @property
    def instance_group_id(self) -> str:
        """The instance group the instance was leased from.

        :rtype: str
        """
        return self._instance_group_id

    @property
    def environment_name(self) -> str:
        """Resolved environment name that owns this instance.

        :rtype: str
        """
        return self._environment_name

    @property
    def environment_version(self) -> str:
        """Resolved environment version that owns this instance.

        :rtype: str
        """
        return self._environment_version

    @property
    def instance(self) -> RLEInstance:
        """The underlying leased instance model."""
        if self._instance is None:
            if self._released:
                raise RLEError("instance has been released")
            raise RLEError(
                "enter the AsyncOpenEnvInstance context before accessing the instance"
            )
        return self._instance

    async def __aenter__(self) -> "AsyncOpenEnvInstance":
        if self._released:
            raise RLEError("instance has been released")
        if self._instance is not None:
            raise RLEError("AsyncOpenEnvInstance context is already entered")
        if self._is_client_closed():
            raise RLEError("OpenEnv client is closed")
        instance = await _acquire_instance(
            self._instances,
            self._runtime,
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            instance_acquire_timeout=self._instance_acquire_timeout,
            poll_interval_s=self._poll_interval_s,
        )
        self._instance = instance
        self._instance_id = instance.instance_id
        if self._is_client_closed():
            await self._release()
            raise RLEError("OpenEnv client is closed")
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
    async def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> RLEStepResult:
        """Start a new episode on this instance and return the initial observation.

        :param seed: Optional seed for deterministic episode initialization.
        :type seed: int or None
        :param episode_id: Optional caller-supplied episode identifier.
        :type episode_id: str or None
        :return: The initial step result for the new episode.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        await self._ensure_healthy()
        return await self._runtime.reset(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
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
        await self._ensure_healthy()
        return await self._runtime.step(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
            RLEStepRequest(action=coerce_action(action, action_kwargs)),
        )

    @distributed_trace_async
    async def state(self) -> RLEnvironmentState:
        """Return the current environment state for this instance.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        await self._ensure_healthy()
        return await self._runtime.state(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
        )

    @distributed_trace_async
    async def health(self) -> Dict[str, Any]:
        """Return instance health information.

        :return: Instance health information.
        :rtype: dict[str, any]
        """
        return await self._runtime.health(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
        )

    @distributed_trace_async
    async def metadata(self) -> Dict[str, Any]:
        """Return instance metadata.

        :return: Instance metadata.
        :rtype: dict[str, any]
        """
        await self._ensure_healthy()
        return await self._runtime.get_metadata(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
        )

    @distributed_trace_async
    async def schema(self) -> Dict[str, Any]:
        """Return the instance action and observation schema.

        :return: The instance action and observation schema.
        :rtype: dict[str, any]
        """
        await self._ensure_healthy()
        return await self._runtime.schema(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
        )

    async def _ensure_healthy(self) -> None:
        health = await self.health()
        if not _is_healthy_response(health):
            raise RLEError(f"instance {self.id} is not healthy")

    async def _release(self) -> None:
        """Release the underlying instance, best effort."""
        instance_id = self._instance_id
        if instance_id is None:
            return
        self._instance = None
        self._instance_id = None
        self._released = True
        try:
            await self._instances.delete_instance(
                self._environment_name,
                self._environment_version,
                self._instance_group_id,
                instance_id,
            )
        except AzureError:
            pass


class AsyncOpenEnvClient:  # pylint: disable=too-many-instance-attributes,missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs,client-accepts-api-version-keyword,async-client-bad-name
    """An async client over a hosted RLE (OpenEnv) environment with a reserved concurrency quota.

    Created via :meth:`RLEOperations.get_openenv_client`. On entering its context the client creates a
    single instance group under ``name`` (optionally pinned to ``version``) that reserves
    ``max_active_instances`` concurrent
    instances on the service and fails immediately if that quota cannot be granted -- there is no
    queueing. The service owns the reservation and the pool of instances; this client keeps no local
    pool. Future revisions may relax this with queueing and elastic scaling.

    :meth:`get_instance` leases a running :class:`AsyncOpenEnvInstance` from the group on demand.
    Because each :meth:`AsyncOpenEnvInstance.reset` starts a fresh episode, an instance may run one or
    more episodes while checked out; exiting its context releases the underlying instance immediately
    (v1 does not reuse instances). Leasing more than ``max_active_instances`` at once fails until an
    outstanding instance is released. Closing the client deletes the group, which releases any
    instances still leased on the service; the client keeps no local list of leased instances.

    :keyword environments: Generated async environment operations used to resolve the environment. Required.
    :paramtype environments: ~azure.ai.projects.aio.operations.RLEnvironmentsOperations
    :keyword instance_groups: Generated async instance group operations bound to the project client. Required.
    :paramtype instance_groups: ~azure.ai.projects.aio.operations.RLEInstanceGroupsOperations
    :keyword instances: Generated async instance lifecycle operations bound to the project client. Required.
    :paramtype instances: ~azure.ai.projects.aio.operations.RLEInstancesOperations
    :keyword runtime: Generated async instance runtime operations bound to the project client. Required.
    :paramtype runtime: ~azure.ai.projects.aio.operations.RLEInstanceRuntimeOperations
    :keyword name: The hosted RLE environment name to resolve. Required.
    :paramtype name: str
    :keyword version: Optional environment image version to resolve and lease against.
    :paramtype version: str or None
    :keyword max_active_instances: Concurrency to reserve on the group. Defaults to 1.
    :paramtype max_active_instances: int
    :keyword instance_acquire_timeout: Maximum time to wait for capacity, provisioning, and runtime
     health when leasing an instance, in seconds. Defaults to 900 and is capped at 3600.
    :paramtype instance_acquire_timeout: float
    :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 5.
    :paramtype poll_interval_s: float
    """

    def __init__(
        self,
        *,
        environments: _RLEnvironmentsOperationsGenerated,
        instance_groups: RLEInstanceGroupsOperations,
        instances: RLEInstancesOperations,
        runtime: RLEInstanceRuntimeOperations,
        name: str,
        version: Optional[str] = None,
        max_active_instances: int = 1,
        instance_acquire_timeout: float = _DEFAULT_INSTANCE_ACQUIRE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> None:
        if not name:
            raise ValueError("name is required")
        if max_active_instances < 1:
            raise ValueError("max_active_instances must be >= 1")
        self._environments = environments
        self._instance_groups = instance_groups
        self._instances = instances
        self._runtime = runtime
        self._name = name
        self._version = version
        self._max_active_instances = max_active_instances
        self._acquire_settings = (
            _validate_instance_acquire_timeout(instance_acquire_timeout),
            poll_interval_s,
        )
        self._instance_group_id: Optional[str] = None
        self._lock = asyncio.Lock()
        self._closed = False

    @property
    def instance_group_id(self) -> Optional[str]:
        """The instance group id backing this client, once created (else ``None``).

        :rtype: str or None
        """
        return self._instance_group_id

    @property
    def max_active_instances(self) -> int:
        """Concurrency the instance group reserves on the service for this client.

        :rtype: int
        """
        return self._max_active_instances

    @property
    def environment_name(self) -> str:
        """Environment name, resolved from the instance-group response after context entry.

        :rtype: str
        """
        return self._name

    @property
    def environment_version(self) -> Optional[str]:
        """Resolved environment version after context entry, otherwise the requested version.

        :rtype: str or None
        """
        return self._version

    async def __aenter__(self) -> "AsyncOpenEnvClient":
        await self._ensure_group()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def _ensure_group(self) -> None:
        """Create the instance group that reserves this client's concurrency on the service.

        Idempotent: a second call is a no-op once the group exists. The group reserves capacity for
        ``max_active_instances`` concurrent instances; the service owns that reservation and the pool, and
        hands instances out (tracking how many remain) as :meth:`get_instance` leases them. If the
        quota cannot be satisfied the service returns ``403`` and this raises
        :class:`RLEQuotaExceededError` (v1 fails fast rather than queueing).
        """
        async with self._lock:
            if self._instance_group_id is not None:
                return
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            if self._version is None:
                environment = await self._environments.get_environment(self._name)
                if not environment.version:
                    raise RLEError("service did not return the environment's latest version")
                self._version = environment.version
            try:
                group = await self._instance_groups.create_instance_group(
                    self._name,
                    self._version,
                    CreateRLEInstanceGroupRequest(
                        max_active_instances=self._max_active_instances,
                    ),
                )
            except HttpResponseError as exc:
                if _is_quota_exceeded_error(exc):
                    raise RLEQuotaExceededError(
                        f"quota exceeded creating an instance group for environment '{self._name}'"
                    ) from exc
                raise
            if not group.instance_group_id:
                raise RLEError("service did not return an instance group id")
            if not group.environment_name or not group.environment_version:
                try:
                    await self._instance_groups.delete_instance_group(
                        self._name,
                        self._version,
                        group.instance_group_id,
                    )
                except AzureError:
                    pass
                raise RLEError(
                    "service did not return the instance group's environment name and version"
                )
            self._name = group.environment_name
            self._version = group.environment_version
            self._instance_group_id = group.instance_group_id

    def get_instance(self) -> AsyncOpenEnvInstance:
        """Create an async context manager that leases a running instance on entry.

        This method performs no I/O. Entering the returned async context manager creates an instance
        under the group and waits (up to ``instance_acquire_timeout``) for capacity, ``Running``
        status, and runtime health. Because
        the group reserves ``max_active_instances`` concurrent instances, temporary capacity responses
        are retried until capacity becomes available or the acquisition timeout expires.

        The returned :class:`AsyncOpenEnvInstance` is an async context manager; exiting its context
        releases the underlying instance back to the service immediately (v1 does not reuse instances).
        The service owns the pool and the reservation, so this client keeps no local bookkeeping of
        leased instances; closing the client deletes the group, which releases any instances still
        leased.

        :return: An async context manager that yields a leased instance ready to run episodes.
        :rtype: ~azure.ai.projects.aio.operations.AsyncOpenEnvInstance
        """
        if self._closed:
            raise RLEError("OpenEnv client is closed")
        group_id = self._instance_group_id
        if group_id is None:
            raise RLEError(
                "reserve quota first: enter the AsyncOpenEnvClient context before get_instance()"
            )
        environment_version = self._version
        if environment_version is None:
            raise RLEError(
                "service did not resolve the instance group's environment version"
            )
        return AsyncOpenEnvInstance(
            self._name,
            group_id,
            environment_version=environment_version,
            instances=self._instances,
            runtime=self._runtime,
            instance_acquire_timeout=self._acquire_settings[0],
            poll_interval_s=self._acquire_settings[1],
            is_client_closed=lambda: self._closed,
        )

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
        environment_version = self._version
        if environment_version is None:
            raise RLEError("service did not resolve the instance group's environment version")
        self._instance_group_id = None
        try:
            await self._instance_groups.delete_instance_group(
                self._name,
                environment_version,
                group_id,
            )
        except AzureError:
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
        self._runtime = RLEInstanceRuntimeOperations(*args, **kwargs)

    @distributed_trace_async
    async def create_environment(
        self,
        name: str,
        acr_image_path: str,
        *,
        version_bump: Optional[Union[str, RLEnvironmentVersionBump]] = None,
        **kwargs: Any,
    ) -> RLEnvironment:
        """Create a new hosted RLE environment.

        :param name: Environment name. Required.
        :type name: str
        :param acr_image_path: Azure Container Registry image path that backs the environment. Required.
        :type acr_image_path: str
        :keyword version_bump: Strategy for bumping the environment version. Default value is None.
        :paramtype version_bump: str or ~azure.ai.projects.models.RLEnvironmentVersionBump or None
        :return: The created RLEnvironment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if not name:
            raise ValueError("name is required")
        if not acr_image_path:
            raise ValueError("acr_image_path is required")
        return await self._environments.create_environment(
            CreateRLEnvironmentRequest(
                name=name, acr_image_path=acr_image_path, version_bump=version_bump
            ),
            **kwargs,
        )

    @distributed_trace
    def list_environments(
        self,
        *,
        name: Optional[str] = None,
        limit: Optional[int] = None,
        continuation_token: Optional[str] = None,
        order: Optional[Union[str, RLEPaginationOrder]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[RLEnvironment]:
        """List all hosted RLE environments in the project.

        :keyword name: Optional environment name filter. When set, returns at most a single matching
         environment. Default value is None.
        :paramtype name: str or None
        :keyword limit: Maximum number of environments to return. Valid range is [1, 100].
        :paramtype limit: int or None
        :keyword continuation_token: Opaque continuation token from a previous page. Omit to fetch the first page.
        :paramtype continuation_token: str or None
        :keyword order: Pagination order. Default value is None.
        :paramtype order: str or ~azure.ai.projects.models.RLEPaginationOrder or None
        :return: An async iterator over hosted RLE environments.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.projects.models.RLEnvironment]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _validate_pagination_limit(limit)
        operation_kwargs = dict(kwargs)

        async def get_next(next_token: Optional[str] = None) -> ListRLEnvironmentsResponse:
            return await self._environments.list_environments(
                name=name,
                limit=limit,
                continuation_token_parameter=(
                    continuation_token if next_token is None else next_token
                ),
                order=order,
                **operation_kwargs,
            )

        async def extract_data(
            response: ListRLEnvironmentsResponse,
        ) -> tuple[Optional[str], AsyncList[RLEnvironment]]:
            return response.next_continuation_token, AsyncList(response.data)

        return AsyncItemPaged(get_next, extract_data)

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
    async def get_environment_version(
        self, name: str, version: str, **kwargs: Any
    ) -> RLEnvironment:
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

    @distributed_trace
    def list_environment_versions(
        self,
        name: str,
        *,
        limit: Optional[int] = None,
        continuation_token: Optional[str] = None,
        order: Optional[Union[str, RLEPaginationOrder]] = None,
        **kwargs: Any,
    ) -> AsyncItemPaged[RLEnvironment]:
        """List historical versions of a hosted RLE environment.

        :param name: Environment name. Required.
        :type name: str
        :keyword limit: Maximum number of versions to return. Valid range is [1, 100].
        :paramtype limit: int or None
        :keyword continuation_token: Opaque continuation token from a previous page. Omit to fetch the first page.
        :paramtype continuation_token: str or None
        :keyword order: Pagination order. Default value is None.
        :paramtype order: str or ~azure.ai.projects.models.RLEPaginationOrder or None
        :return: An async iterator over historical environment versions.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.projects.models.RLEnvironment]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _validate_pagination_limit(limit)
        operation_kwargs = dict(kwargs)

        async def get_next(
            next_token: Optional[str] = None,
        ) -> ListRLEnvironmentVersionsResponse:
            return await self._environments.list_rl_environment_versions(
                name,
                limit=limit,
                continuation_token_parameter=(
                    continuation_token if next_token is None else next_token
                ),
                order=order,
                **operation_kwargs,
            )

        async def extract_data(
            response: ListRLEnvironmentVersionsResponse,
        ) -> tuple[Optional[str], AsyncList[RLEnvironment]]:
            return response.next_continuation_token, AsyncList(response.data)

        return AsyncItemPaged(get_next, extract_data)

    @distributed_trace_async
    async def delete_environment_version(
        self, name: str, version: str, **kwargs: Any
    ) -> None:
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
        max_active_instances: int = 1,
        instance_acquire_timeout: float = _DEFAULT_INSTANCE_ACQUIRE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> AsyncOpenEnvClient:
        """Create an :class:`AsyncOpenEnvClient` over a hosted RLE environment.

        This constructs the client without any network I/O (no awaiting needed), so callers can write
        ``async with client.rle.get_openenv_client(...) as openenv_client:``. The returned client is an
        async context manager: entering it creates an instance group under ``name`` (and ``version``
        when supplied) -- so a missing or invalid environment fails on entry -- and reserves its
        concurrency on the service, failing fast if that quota cannot be
        granted (v1 does not queue). :meth:`AsyncOpenEnvClient.get_instance` then leases running
        :class:`AsyncOpenEnvInstance` objects from the group on demand to run episodes on.

        :keyword name: The hosted RLE environment name to resolve. Required.
        :paramtype name: str
        :keyword version: Optional environment image version. When set, the instance group is created
         under that version; otherwise the service uses the latest version.
        :paramtype version: str or None
        :keyword max_active_instances: Concurrency to reserve on the group, so that several episodes can run
         concurrently on the event loop. Defaults to 1.
        :paramtype max_active_instances: int
        :keyword instance_acquire_timeout: Maximum time to wait for capacity, provisioning, and
         runtime health when leasing an instance, in seconds. Defaults to 900 and is capped at 3600.
        :paramtype instance_acquire_timeout: float
        :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 5.
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
            runtime=self._runtime,
            name=name,
            version=version,
            max_active_instances=max_active_instances,
            instance_acquire_timeout=instance_acquire_timeout,
            poll_interval_s=poll_interval_s,
        )


__all__ = [
    "AsyncOpenEnvClient",
    "AsyncOpenEnvInstance",
    "RLEError",
    "RLEQuotaExceededError",
    "RLEInstanceAcquireTimeoutError",
    "RLEOperations",
    "coerce_action",
]
