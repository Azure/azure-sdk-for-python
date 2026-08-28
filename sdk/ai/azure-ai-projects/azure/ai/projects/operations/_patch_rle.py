# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""RLE environment runtime helpers.

These helpers layer a Gymnasium-style ergonomic surface on top of the generated RLE operations.
Every request is issued through the :class:`~azure.ai.projects.AIProjectClient` pipeline against the
Foundry project endpoint, exactly like the other operation groups on the client.

The RLE surface models two service concepts:

* An **instance group** (:class:`~azure.ai.projects.models.RLEInstanceGroup`) reserves capacity for a
  hosted environment at a pinned version and owns a fixed number of instances.
* An **instance** (:class:`~azure.ai.projects.models.RLEInstance`) is a single running environment
  process leased from a group. Runtime calls (reset/step/state/...) use the resolved environment
  name and version, instance-group id, and instance id returned by the service.
"""

from __future__ import annotations

import math
import threading
import time
from typing import Any, Dict, Mapping, Optional, Tuple, Union

from azure.core.exceptions import AzureError, HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ..models import (
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
from ._operations import (
    RLEnvironmentsOperations as _RLEnvironmentsOperationsGenerated,
    RLEInstanceGroupsOperations,
    RLEInstancesOperations,
    RLEInstanceRuntimeOperations,
)

_DEFAULT_INSTANCE_ACQUIRE_TIMEOUT_S = 900.0
_MAX_INSTANCE_ACQUIRE_TIMEOUT_S = 3600.0
_DEFAULT_POLL_INTERVAL_S = 5.0
_MAX_PAGINATION_LIMIT = 100
_QUOTA_EXCEEDED_CODE = "QuotaExceeded"
_INSTANCE_GROUP_AT_CAPACITY_CODE = "InstanceGroupAtCapacity"
_TRANSIENT_HEALTH_STATUS_CODES = frozenset(
    (404, 408, 409, 425, 429, 500, 502, 503, 504)
)


class RLEError(RuntimeError):
    """Raised when leasing an RLE instance does not reach a usable state.

    HTTP failures from the service surface as :class:`~azure.core.exceptions.HttpResponseError`,
    consistent with the other operation groups. ``RLEError`` covers client-side lease conditions,
    such as an instance that fails to start or never becomes ready within the timeout.
    """


class RLEQuotaExceededError(RLEError):
    """Raised when an instance group cannot be created because the project quota is exhausted.

    This is a terminal condition (the service returns ``403``): the request will not succeed until
    capacity is freed or quota is increased, so the client does not retry.
    """


class RLEInstanceAcquireTimeoutError(RLEError):
    """Raised when an RLE instance cannot be acquired before the configured deadline."""

    def __init__(
        self,
        message: str,
        *,
        timeout: float,
        last_status: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.timeout = timeout
        self.last_status = last_status
        self.details = details


def _error_code(model: Any) -> Optional[str]:
    return getattr(model, "code", None) or getattr(
        getattr(model, "error", None), "code", None
    )


def _is_quota_exceeded_error(exc: HttpResponseError) -> bool:
    return (
        exc.status_code == 403
        and _error_code(getattr(exc, "model", None)) == _QUOTA_EXCEEDED_CODE
    )


def _status_matches(status: Any, target: RLEInstanceStatus) -> bool:
    value = getattr(status, "value", status)
    return str(value or "").lower() == target.value.lower()


def _parse_retry_after(response: Any) -> Optional[float]:
    """Extract a ``Retry-After`` hint (in seconds) from an HTTP response, if present.

    :param response: An HTTP response exposing a ``headers`` mapping.
    :type response: any
    :return: The retry delay in seconds, or ``None`` when no valid hint is present.
    :rtype: float or None
    """
    headers = getattr(response, "headers", None)
    if not headers:
        return None
    raw = headers.get("Retry-After") or headers.get("retry-after")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _validate_instance_acquire_timeout(instance_acquire_timeout: float) -> float:
    try:
        value = float(instance_acquire_timeout)
    except (TypeError, ValueError) as exc:
        raise ValueError("instance_acquire_timeout must be a finite number") from exc
    if not math.isfinite(value) or value <= 0:
        raise ValueError(
            "instance_acquire_timeout must be a finite number greater than 0"
        )
    if value > _MAX_INSTANCE_ACQUIRE_TIMEOUT_S:
        raise ValueError(
            f"instance_acquire_timeout must be <= {_MAX_INSTANCE_ACQUIRE_TIMEOUT_S:.0f} seconds"
        )
    return value


def _validate_pagination_limit(limit: Optional[int]) -> None:
    if limit is not None and not 1 <= limit <= _MAX_PAGINATION_LIMIT:
        raise ValueError(
            f"limit must be in the range [1, {_MAX_PAGINATION_LIMIT}]"
        )


def _validate_poll_interval(poll_interval_s: float) -> float:
    try:
        value = float(poll_interval_s)
    except (TypeError, ValueError) as exc:
        raise ValueError("poll_interval_s must be a finite number") from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError("poll_interval_s must be a finite number greater than or equal to 0")
    return value


def _is_healthy_response(response: Any) -> bool:
    del response
    return True


def _capacity_details(exc: HttpResponseError) -> Optional[Any]:
    if getattr(exc.response, "status_code", None) != 429:
        return None
    model = getattr(exc, "model", None)
    return model if _error_code(model) == _INSTANCE_GROUP_AT_CAPACITY_CODE else None


def _capacity_retry(
    exc: HttpResponseError, fallback_delay: float
) -> Optional[Tuple[Any, float]]:
    details = _capacity_details(exc)
    if details is None:
        return None
    retry_after = _parse_retry_after(exc.response)
    return details, fallback_delay if retry_after is None else retry_after


def _sleep_before_deadline(delay: float, deadline: float) -> bool:
    remaining = deadline - time.monotonic()
    if remaining <= 0 or delay >= remaining:
        return False
    time.sleep(max(0.0, delay))
    return True


def coerce_action(action: Any, action_kwargs: Mapping[str, Any]) -> dict:
    """Normalize a step action into a plain JSON-serializable dictionary.

    :param action: A single action as a mapping or a model exposing ``model_dump``/``to_dict``.
     Mutually exclusive with ``action_kwargs``.
    :type action: any
    :param action_kwargs: Action fields supplied as keyword arguments. Mutually exclusive with ``action``.
    :type action_kwargs: mapping[str, any]
    :return: The action as a plain dictionary.
    :rtype: dict
    """
    if action is None:
        return dict(action_kwargs)
    if action_kwargs:
        raise TypeError(
            "pass either a single action mapping or keyword fields, not both"
        )
    if hasattr(action, "model_dump"):
        return action.model_dump()
    if hasattr(action, "to_dict"):
        return action.to_dict()
    if isinstance(action, Mapping):
        return dict(action)
    raise TypeError(
        f"action must be a mapping or keyword fields, got {type(action).__name__}"
    )


def _acquire_instance(
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

    :param instances: Generated instance operations bound to the project client.
    :type instances: ~azure.ai.projects.operations.RLEInstancesOperations
    :param runtime: Generated instance runtime operations bound to the project client.
    :type runtime: ~azure.ai.projects.operations.RLEInstanceRuntimeOperations
    :param environment_name: The environment that owns the instance group.
    :type environment_name: str
    :param environment_version: Resolved environment version that owns the instance group.
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

    def _capture(
        pipeline_response: Any, deserialized: Any, _response_headers: Any
    ) -> Any:
        captured["response"] = pipeline_response.http_response
        return deserialized

    while True:
        captured.clear()
        try:
            instance = instances.create_instance(
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
            if not _sleep_before_deadline(retry_after, deadline):
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
            if not _sleep_before_deadline(next_wait, deadline):
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
            instance = instances.get_instance(
                environment_name,
                environment_version,
                instance_group_id,
                instance_id,
            )

        while True:
            try:
                health = runtime.health(
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
            if not _sleep_before_deadline(poll_interval_s, deadline):
                raise RLEInstanceAcquireTimeoutError(
                    f"instance {instance_id} runtime was not healthy after "
                    f"{instance_acquire_timeout:.0f}s",
                    timeout=instance_acquire_timeout,
                    last_status="Unhealthy",
                )
    except BaseException:
        # The instance was leased but never became usable; release it so it does not leak quota.
        try:
            instances.delete_instance(
                environment_name,
                environment_version,
                instance_group_id,
                instance_id,
            )
        except Exception:  # pylint: disable=broad-except
            pass
        raise
    return instance


class OpenEnvInstance:
    """A leased RLE instance that runs episodes under a resolved environment version.

    An instance is obtained from :meth:`OpenEnvClient.get_instance`. It wraps a single leased
    :class:`~azure.ai.projects.models.RLEInstance` and drives the OpenEnv / Gymnasium runtime
    operations (``reset``/``step``/``state``) against it. Each :meth:`reset` starts a new episode, so
    an instance may run one or more episodes while it is checked out. v1 does not reuse instances:
    exiting the instance's ``with`` block releases the underlying instance immediately. Runtime
    requests flow through the owning project client's pipeline.

    :param environment_name: The environment that owns the instance group. Required.
    :type environment_name: str
    :param instance_group_id: The instance group the instance was leased from. Required.
    :type instance_group_id: str
    :keyword environment_version: Resolved environment version that owns the instance group.
    :paramtype environment_version: str
    :keyword instance: The leased, running instance that backs this object. Required.
    :paramtype instance: ~azure.ai.projects.models.RLEInstance
    :keyword instances: Generated instance lifecycle operations bound to the project client. Required.
    :paramtype instances: ~azure.ai.projects.operations.RLEInstancesOperations
    :keyword runtime: Generated instance runtime operations bound to the project client. Required.
    :paramtype runtime: ~azure.ai.projects.operations.RLEInstanceRuntimeOperations
    """

    def __init__(
        self,
        environment_name: str,
        instance_group_id: str,
        *,
        environment_version: str,
        instance: RLEInstance,
        instances: RLEInstancesOperations,
        runtime: RLEInstanceRuntimeOperations,
    ) -> None:
        if not environment_name:
            raise ValueError("environment_name is required")
        if not environment_version:
            raise ValueError("environment_version is required")
        if not instance_group_id:
            raise ValueError("instance_group_id is required")
        if not instance.instance_id:
            raise RLEError("instance is missing an id")
        self._environment_name = environment_name
        self._environment_version = environment_version
        self._instance_group_id = instance_group_id
        self._instance: Optional[RLEInstance] = instance
        self._instance_id: Optional[str] = instance.instance_id
        self._instances = instances
        self._runtime = runtime

    @property
    def id(self) -> str:
        """Identifier of the leased instance that backs this object.

        :rtype: str
        """
        if self._instance_id is None:
            raise RLEError("instance has been released")
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
        """The underlying leased instance model.

        :rtype: ~azure.ai.projects.models.RLEInstance
        """
        if self._instance is None:
            raise RLEError("instance has been released")
        return self._instance

    def __enter__(self) -> "OpenEnvInstance":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.release()

    def release(self) -> None:
        """Release this leased instance on the service, best effort.

        Invoked automatically on context exit. v1 does not reuse instances: once an instance leaves
        its ``with`` block the underlying instance is released immediately, which frees its slot in
        the group's reservation so another instance can be leased.
        """
        self._release()

    @distributed_trace
    def reset(
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
        self._ensure_healthy()
        return self._runtime.reset(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
            RLEResetRequest(seed=seed, episode_id=episode_id),
            **kwargs,
        )

    @distributed_trace
    def step(self, action: Any = None, **action_kwargs: Any) -> RLEStepResult:
        """Apply an action and return the resulting observation, reward, and done state.

        :param action: The action to apply, as a mapping or model. Mutually exclusive with keyword fields.
        :type action: any
        :return: The step result after applying the action.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        self._ensure_healthy()
        return self._runtime.step(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
            RLEStepRequest(action=coerce_action(action, action_kwargs)),
        )

    @distributed_trace
    def state(self) -> RLEnvironmentState:
        """Return the current environment state for this instance.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        self._ensure_healthy()
        return self._runtime.state(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
        )

    @distributed_trace
    def health(self) -> Dict[str, Any]:
        """Return instance health information.

        :return: Instance health information.
        :rtype: dict[str, any]
        """
        return self._runtime.health(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
        )

    @distributed_trace
    def metadata(self) -> Dict[str, Any]:
        """Return instance metadata.

        :return: Instance metadata.
        :rtype: dict[str, any]
        """
        self._ensure_healthy()
        return self._runtime.get_metadata(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
        )

    @distributed_trace
    def schema(self) -> Dict[str, Any]:
        """Return the instance action and observation schema.

        :return: The instance action and observation schema.
        :rtype: dict[str, any]
        """
        self._ensure_healthy()
        return self._runtime.schema(
            self._environment_name,
            self._environment_version,
            self._instance_group_id,
            self.id,
        )

    def _ensure_healthy(self) -> None:
        health = self.health()
        if not _is_healthy_response(health):
            raise RLEError(f"instance {self.id} is not healthy")

    def _release(self) -> None:
        """Release the underlying instance, best effort."""
        instance_id = self._instance_id
        if instance_id is None:
            return
        self._instance = None
        self._instance_id = None
        try:
            self._instances.delete_instance(
                self._environment_name,
                self._environment_version,
                self._instance_group_id,
                instance_id,
            )
        except AzureError:
            pass


class OpenEnvClient:  # pylint: disable=too-many-instance-attributes,client-accepts-api-version-keyword,missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
    """A client over a hosted RLE (OpenEnv) environment with a reserved concurrency quota.

    Created via :meth:`RLEOperations.get_openenv_client`. On entering its context the client creates a
    single instance group under ``name`` (optionally pinned to ``version``) that reserves
    ``max_active_instances`` concurrent
    instances on the service and fails immediately if that quota cannot be granted -- there is no
    queueing. The service owns the reservation and the pool of instances; this client keeps no local
    pool. Future revisions may relax this with queueing and elastic scaling.

    :meth:`get_instance` leases a running :class:`OpenEnvInstance` from the group on demand. Because
    each :meth:`OpenEnvInstance.reset` starts a fresh episode, an instance may run one or more
    episodes while checked out; exiting its context releases the underlying instance immediately (v1
    does not reuse instances). Leasing more than ``max_active_instances`` at once fails until an outstanding
    instance is released. Closing the client deletes the group, which releases any instances still
    leased on the service; the client keeps no local list of leased instances.

    :keyword environments: Generated environment operations used to resolve the environment. Required.
    :paramtype environments: ~azure.ai.projects.operations.RLEnvironmentsOperations
    :keyword instance_groups: Generated instance group operations bound to the project client. Required.
    :paramtype instance_groups: ~azure.ai.projects.operations.RLEInstanceGroupsOperations
    :keyword instances: Generated instance lifecycle operations bound to the project client. Required.
    :paramtype instances: ~azure.ai.projects.operations.RLEInstancesOperations
    :keyword runtime: Generated instance runtime operations bound to the project client. Required.
    :paramtype runtime: ~azure.ai.projects.operations.RLEInstanceRuntimeOperations
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
            _validate_poll_interval(poll_interval_s),
        )
        self._instance_group_id: Optional[str] = None
        self._lock = threading.Lock()
        self._closed = False

    @property
    def instance_group_id(self) -> Optional[str]:
        """The instance group id backing this client, once created (else ``None``)."""
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
        """Resolved environment version after context entry, otherwise the requested version."""
        return self._version

    def __enter__(self) -> "OpenEnvClient":
        self._ensure_group()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _ensure_group(self) -> None:
        """Create the instance group that reserves this client's concurrency on the service.

        Idempotent: a second call is a no-op once the group exists. The group reserves capacity for
        ``max_active_instances`` concurrent instances; the service owns that reservation and the pool, and
        hands instances out (tracking how many remain) as :meth:`get_instance` leases them. If the
        quota cannot be satisfied the service returns ``403`` and this raises
        :class:`RLEQuotaExceededError` (v1 fails fast rather than queueing).
        """
        with self._lock:
            if self._instance_group_id is not None:
                return
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            if self._version is None:
                environment = self._environments.get_environment(self._name)
                if not environment.version:
                    raise RLEError("service did not return the environment's latest version")
                self._version = environment.version
            try:
                group = self._instance_groups.create_instance_group(
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
                    self._instance_groups.delete_instance_group(
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

    def get_instance(self) -> OpenEnvInstance:
        """Lease a running instance from the group for one or more episodes.

        This leases an instance from the service on demand: it creates an instance under the group and
        waits (up to ``instance_acquire_timeout``) for capacity, ``Running`` status, and runtime health.
        The service owns the pool and
        the reservation -- there is no client-side pool. Because the group reserves ``max_active_instances``
        concurrent instances, temporary capacity responses are retried until capacity becomes available
        or the acquisition timeout expires.

        The returned :class:`OpenEnvInstance` is a context manager; exiting its context releases the
        underlying instance back to the service immediately (v1 does not reuse instances). The service
        owns the pool and the reservation, so this client keeps no local bookkeeping of leased
        instances; closing the client deletes the group, which releases any instances still leased.

        :return: A leased instance ready to run episodes.
        :rtype: ~azure.ai.projects.operations.OpenEnvInstance
        """
        with self._lock:
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            group_id = self._instance_group_id
        if group_id is None:
            raise RLEError(
                "reserve quota first: enter the OpenEnvClient context before get_instance()"
            )
        environment_version = self._version
        if environment_version is None:
            raise RLEError(
                "service did not resolve the instance group's environment version"
            )
        instance = _acquire_instance(
            self._instances,
            self._runtime,
            self._name,
            environment_version,
            group_id,
            instance_acquire_timeout=self._acquire_settings[0],
            poll_interval_s=self._acquire_settings[1],
        )
        openenv_instance = OpenEnvInstance(
            self._name,
            group_id,
            environment_version=environment_version,
            instance=instance,
            instances=self._instances,
            runtime=self._runtime,
        )
        with self._lock:
            if self._closed:
                openenv_instance._release()  # pylint: disable=protected-access
                raise RLEError("OpenEnv client is closed")
        return openenv_instance

    def close(self) -> None:
        """Tear down the instance group, best effort.

        The service releases any instances still leased under the group when it is deleted, so this
        client does not release them individually.
        """
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._close_group_locked()

    def _close_group_locked(self) -> None:
        group_id = self._instance_group_id
        if group_id is None:
            return
        environment_version = self._version
        if environment_version is None:
            raise RLEError("service did not resolve the instance group's environment version")
        self._instance_group_id = None
        try:
            self._instance_groups.delete_instance_group(
                self._name,
                environment_version,
                group_id,
            )
        except AzureError:
            pass


class RLEOperations:
    """Operations for hosted RLE environments, accessed through the client's ``rle`` attribute.

    This operation group exposes environment management (:meth:`create_environment`,
    :meth:`list_environments`, :meth:`get_environment`, :meth:`get_environment_version`,
    :meth:`list_environment_versions`, :meth:`delete_environment_version`) alongside
    :meth:`get_openenv_client`, which resolves a hosted RLE environment and returns an
    :class:`OpenEnvClient`. Episodes are then driven through that client and the
    :class:`OpenEnvInstance` objects it hands out (reset/step/state/health/metadata/schema).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._environments = _RLEnvironmentsOperationsGenerated(*args, **kwargs)
        self._instance_groups = RLEInstanceGroupsOperations(*args, **kwargs)
        self._instances = RLEInstancesOperations(*args, **kwargs)
        self._runtime = RLEInstanceRuntimeOperations(*args, **kwargs)

    @distributed_trace
    def create_environment(
        self,
        acr_image_path: str,
        *,
        name: Optional[str] = None,
        version_bump: Optional[Union[str, RLEnvironmentVersionBump]] = None,
        **kwargs: Any,
    ) -> RLEnvironment:
        """Create a new hosted RLE environment.

        :param acr_image_path: Azure Container Registry image path that backs the environment. Required.
        :type acr_image_path: str
        :keyword name: Optional environment name. The service assigns one when omitted.
        :paramtype name: str or None
        :keyword version_bump: Semantic version component to increment. Omit to let the service choose.
        :paramtype version_bump: str or ~azure.ai.projects.models.RLEnvironmentVersionBump or None
        :return: The created RLEnvironment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if not acr_image_path:
            raise ValueError("acr_image_path is required")
        return self._environments.create_environment(
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
    ) -> ItemPaged[RLEnvironment]:
        """List all hosted RLE environments in the project.

        :keyword name: Optional environment name filter. When set, returns at most a single matching
         environment. Default value is None.
        :paramtype name: str or None
        :keyword limit: Maximum number of environments to return. Valid range is [1, 100].
        :paramtype limit: int or None
        :keyword continuation_token: Opaque continuation token from a previous page. Omit to fetch the first page.
        :paramtype continuation_token: str or None
        :keyword order: Sort order for the page. Known values are "asc" and "desc".
        :paramtype order: str or ~azure.ai.projects.models.RLEPaginationOrder or None
        :return: An iterator over hosted RLE environments.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.RLEnvironment]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _validate_pagination_limit(limit)
        operation_kwargs = dict(kwargs)

        def get_next(next_token: Optional[str] = None) -> ListRLEnvironmentsResponse:
            return self._environments.list_environments(
                name=name,
                limit=limit,
                continuation_token_parameter=(
                    continuation_token if next_token is None else next_token
                ),
                order=order,
                **operation_kwargs,
            )

        def extract_data(
            response: ListRLEnvironmentsResponse,
        ) -> Tuple[Optional[str], Any]:
            return response.next_continuation_token, iter(response.data)

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def get_environment(self, name: str, **kwargs: Any) -> RLEnvironment:
        """Get a hosted RLE environment by name. Returns the latest version of the environment.

        :param name: Environment name. Required.
        :type name: str
        :return: The requested RLEnvironment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._environments.get_environment(name, **kwargs)

    @distributed_trace
    def get_environment_version(
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
        return self._environments.get_environment_version(name, version, **kwargs)

    @distributed_trace
    def list_environment_versions(
        self,
        name: str,
        *,
        limit: Optional[int] = None,
        continuation_token: Optional[str] = None,
        order: Optional[Union[str, RLEPaginationOrder]] = None,
        **kwargs: Any,
    ) -> ItemPaged[RLEnvironment]:
        """List historical versions of a hosted RLE environment.

        :param name: Environment name. Required.
        :type name: str
        :keyword limit: Maximum number of versions to return. Valid range is [1, 100].
        :paramtype limit: int or None
        :keyword continuation_token: Opaque continuation token from a previous page. Omit to fetch the first page.
        :paramtype continuation_token: str or None
        :keyword order: Sort order for the page. Known values are "asc" and "desc".
        :paramtype order: str or ~azure.ai.projects.models.RLEPaginationOrder or None
        :return: An iterator over historical environment versions.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.projects.models.RLEnvironment]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _validate_pagination_limit(limit)
        operation_kwargs = dict(kwargs)

        def get_next(
            next_token: Optional[str] = None,
        ) -> ListRLEnvironmentVersionsResponse:
            return self._environments.list_rl_environment_versions(
                name,
                limit=limit,
                continuation_token_parameter=(
                    continuation_token if next_token is None else next_token
                ),
                order=order,
                **operation_kwargs,
            )

        def extract_data(
            response: ListRLEnvironmentVersionsResponse,
        ) -> Tuple[Optional[str], Any]:
            return response.next_continuation_token, iter(response.data)

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def delete_environment_version(
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
        self._environments.delete_environment_version(name, version, **kwargs)

    @distributed_trace
    def get_openenv_client(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        max_active_instances: int = 1,
        instance_acquire_timeout: float = _DEFAULT_INSTANCE_ACQUIRE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> OpenEnvClient:
        """Create an :class:`OpenEnvClient` over a hosted RLE environment.

        This constructs the client without any network I/O. The returned client is a context manager:
        entering it creates an instance group under ``name`` (and ``version`` when supplied) -- so a
        missing or invalid environment fails on entry -- that reserves
        its concurrency on the service and fails fast if that quota cannot be granted (v1 does not
        queue). :meth:`OpenEnvClient.get_instance` then leases running :class:`OpenEnvInstance`
        objects from the group on demand to run episodes on. Requests flow through this client's
        pipeline and the Foundry project endpoint.

        :keyword name: The hosted RLE environment name to resolve. Required.
        :paramtype name: str
        :keyword version: Optional environment image version. When set, the instance group is created
         under that version; otherwise the service uses the latest version.
        :paramtype version: str or None
        :keyword max_active_instances: Concurrency to reserve on the group, so that several episodes can run
         concurrently. Defaults to 1.
        :paramtype max_active_instances: int
        :keyword instance_acquire_timeout: Maximum time to wait for capacity, provisioning, and
         runtime health when leasing an instance, in seconds. Defaults to 900 and is capped at 3600.
        :paramtype instance_acquire_timeout: float
        :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 5.
        :paramtype poll_interval_s: float
        :return: An OpenEnv client bound to this client.
        :rtype: ~azure.ai.projects.operations.OpenEnvClient
        """
        if not name:
            raise ValueError("name is required")
        return OpenEnvClient(
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
    "OpenEnvClient",
    "RLEError",
    "RLEQuotaExceededError",
    "RLEInstanceAcquireTimeoutError",
    "OpenEnvInstance",
    "RLEOperations",
    "coerce_action",
]
