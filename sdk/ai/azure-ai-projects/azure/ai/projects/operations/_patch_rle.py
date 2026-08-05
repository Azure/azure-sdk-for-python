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
  process leased from a group. Runtime calls (reset/step/state/...) address an instance by its flat
  ``instance_id``.
"""

from __future__ import annotations

import threading
import time
from typing import IO, Any, Dict, List, Mapping, Optional, Union

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace

from ..models import (
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
from ._operations import (
    RLEnvironmentsOperations as _RLEnvironmentsOperationsGenerated,
    RLEInstanceGroupsOperations,
    RLEInstancesOperations,
)

_DEFAULT_CREATE_TIMEOUT_S = 900.0
_DEFAULT_POLL_INTERVAL_S = 5.0


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


class RLEAtCapacityError(RLEError):
    """Raised when an instance group is temporarily at capacity and no instance can be leased.

    The service returns ``429`` with a ``Retry-After`` hint. :attr:`retry_after` carries that hint (in
    seconds) when the service provided one, so callers may back off and retry.
    """

    def __init__(self, message: str, *, retry_after: Optional[float] = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


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
        raise TypeError("pass either a single action mapping or keyword fields, not both")
    if hasattr(action, "model_dump"):
        return action.model_dump()
    if hasattr(action, "to_dict"):
        return action.to_dict()
    if isinstance(action, Mapping):
        return dict(action)
    raise TypeError(f"action must be a mapping or keyword fields, got {type(action).__name__}")


def _acquire_instance(
    instances: RLEInstancesOperations,
    instance_group_id: str,
    *,
    create_timeout_s: float,
    poll_interval_s: float,
) -> RLEInstance:
    """Acquire an instance under a group and poll until it reports the ``Running`` status.

    The service may answer the create request with ``202`` (accepted, still provisioning). The create
    operation is not idempotent, so the pending instance returned by the ``202`` is polled by its id
    (honoring any ``Retry-After`` hint on the first wait) until it reports ``Running`` -- the create is
    never re-issued, which would lease and leak an extra instance for each pending response. A ``429``
    response surfaces as :class:`RLEAtCapacityError`.

    :param instances: Generated instance operations bound to the project client.
    :type instances: ~azure.ai.projects.operations.RLEInstancesOperations
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

    # Create the instance exactly once. create_instance is not idempotent: a 202 already carries a
    # pending instance, so it is polled by id below rather than re-POSTed.
    try:
        instance = instances.create_instance(instance_group_id, cls=_capture)
    except HttpResponseError as exc:
        if getattr(exc.response, "status_code", None) == 429:
            raise RLEAtCapacityError(
                f"instance group {instance_group_id} is at capacity",
                retry_after=_parse_retry_after(exc.response),
            ) from exc
        raise

    if instance is None or not instance.instance_id:
        raise RLEError("service did not return an instance id")
    instance_id = instance.instance_id

    # The initial (possibly 202) response may carry a Retry-After hint for the first poll.
    next_wait = _parse_retry_after(captured.get("response")) or poll_interval_s
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
            time.sleep(next_wait)
            next_wait = poll_interval_s
            instance = instances.get_instance(instance_group_id, instance_id)
    except BaseException:
        # The instance was leased but never became usable; release it so it does not leak quota.
        try:
            instances.release_instance(instance_group_id, instance_id)
        except Exception:  # pylint: disable=broad-except
            pass
        raise
    return instance


class OpenEnvInstance:
    """A leased RLE instance that runs episodes, addressable by its flat ``instance_id``.

    An instance is obtained from :meth:`OpenEnvClient.get_instance`. It wraps a single leased
    :class:`~azure.ai.projects.models.RLEInstance` and drives the OpenEnv / Gymnasium runtime
    operations (``reset``/``step``/``state``) against it. Each :meth:`reset` starts a new episode, so
    an instance may run one or more episodes while it is checked out. v1 does not reuse instances:
    exiting the instance's ``with`` block releases the underlying instance immediately. Runtime
    requests flow through the owning project client's pipeline.

    :param instance_group_id: The instance group the instance was leased from. Required.
    :type instance_group_id: str
    :keyword instance: The leased, running instance that backs this object. Required.
    :paramtype instance: ~azure.ai.projects.models.RLEInstance
    :keyword instances: Generated instance operations bound to the project client. Required.
    :paramtype instances: ~azure.ai.projects.operations.RLEInstancesOperations
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
    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs: Any) -> RLEStepResult:
        """Start a new episode on this instance and return the initial observation.

        :param seed: Optional seed for deterministic episode initialization.
        :type seed: int or None
        :param episode_id: Optional caller-supplied episode identifier.
        :type episode_id: str or None
        :return: The initial step result for the new episode.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        return self._instances.reset(
            self._instance_id,
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
        return self._instances.step(
            self._instance_id,
            RLEStepRequest(action=coerce_action(action, action_kwargs)),
        )

    @distributed_trace
    def state(self) -> RLEnvironmentState:
        """Return the current environment state for this instance.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        return self._instances.state(self._instance_id)

    @distributed_trace
    def health(self) -> Dict[str, Any]:
        """Return instance health information.

        :return: Instance health information.
        :rtype: dict[str, any]
        """
        return self._instances.health(self._instance_id)

    @distributed_trace
    def metadata(self) -> Dict[str, Any]:
        """Return instance metadata.

        :return: Instance metadata.
        :rtype: dict[str, any]
        """
        return self._instances.get_metadata(self._instance_id)

    @distributed_trace
    def schema(self) -> Dict[str, Any]:
        """Return the instance action and observation schema.

        :return: The instance action and observation schema.
        :rtype: dict[str, any]
        """
        return self._instances.schema(self._instance_id)

    def _release(self) -> None:
        """Release the underlying instance, best effort."""
        try:
            self._instances.release_instance(self._instance_group_id, self._instance_id)
        except HttpResponseError:
            pass


class OpenEnvClient:
    """A client over a hosted RLE (OpenEnv) environment with a reserved concurrency quota.

    Created via :meth:`RLEOperations.get_openenv_client`. The environment is resolved lazily by
    ``name`` (optionally pinned to ``version``) when the client is first entered. On entering its
    context the client creates a single instance group that reserves ``num_instances`` concurrent
    instances on the service and fails immediately if that quota cannot be granted -- there is no
    queueing. The service owns the reservation and the pool of instances; this client keeps no local
    pool. Future revisions may relax this with queueing and elastic scaling.

    :meth:`get_instance` leases a running :class:`OpenEnvInstance` from the group on demand. Because
    each :meth:`OpenEnvInstance.reset` starts a fresh episode, an instance may run one or more
    episodes while checked out; exiting its context releases the underlying instance immediately (v1
    does not reuse instances). Leasing more than ``num_instances`` at once fails until an outstanding
    instance is released. Closing the client deletes the group, which releases any instances still
    leased on the service; the client keeps no local list of leased instances.

    :keyword environments: Generated environment operations used to resolve the environment. Required.
    :paramtype environments: ~azure.ai.projects.operations.RLEnvironmentsOperations
    :keyword instance_groups: Generated instance group operations bound to the project client. Required.
    :paramtype instance_groups: ~azure.ai.projects.operations.RLEInstanceGroupsOperations
    :keyword instances: Generated instance operations bound to the project client. Required.
    :paramtype instances: ~azure.ai.projects.operations.RLEInstancesOperations
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
        self._lock = threading.Lock()
        self._closed = False

    @property
    def instance_group_id(self) -> Optional[str]:
        """The instance group id backing this client, once created (else ``None``)."""
        return self._instance_group_id

    @property
    def num_instances(self) -> int:
        """Concurrency the instance group reserves on the service for this client."""
        return self._num_instances

    def __enter__(self) -> "OpenEnvClient":
        self._resolve_environment()
        self._ensure_group()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _resolve_environment(self) -> None:
        """Resolve ``name``/``version`` to a concrete environment name and version.

        Invoked on context entry (``__enter__``) before reservation, so a missing environment
        surfaces when the client is entered. Idempotent: a second call is a no-op once resolved. The
        instance group create request requires a pinned environment version, so the latest version is
        resolved when the caller did not supply one.
        """
        if self._environment_name is not None:
            return
        if self._version is not None:
            environment = self._environments.get_environment_version(self._name, self._version)
        else:
            environment = self._environments.get_environment(self._name)
        environment_name = getattr(environment, "name", None) or self._name
        environment_version = self._version or getattr(environment, "version", None)
        if not environment_version:
            raise RLEError(f"environment '{self._name}' did not resolve to a version")
        self._environment_name = environment_name
        self._environment_version = environment_version

    def _ensure_group(self) -> None:
        """Create the instance group that reserves this client's concurrency on the service.

        Idempotent: a second call is a no-op once the group exists. The group reserves capacity for
        ``num_instances`` concurrent instances; the service owns that reservation and the pool, and
        hands instances out (tracking how many remain) as :meth:`get_instance` leases them. If the
        quota cannot be satisfied the service returns ``403`` and this raises
        :class:`RLEQuotaExceededError` (v1 fails fast rather than queueing).
        """
        with self._lock:
            if self._instance_group_id is not None:
                return
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            if self._environment_name is None:
                self._resolve_environment()
            try:
                group = self._instance_groups.create_instance_group(
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

    def get_instance(self) -> OpenEnvInstance:
        """Lease a running instance from the group for one or more episodes.

        This leases an instance from the service on demand: it creates an instance under the group and
        waits (up to ``create_timeout_s``) for it to report ``Running``. The service owns the pool and
        the reservation -- there is no client-side pool. Because the group reserves ``num_instances``
        concurrent instances, leasing more than that at once fails with :class:`RLEAtCapacityError`
        (``429``) until an outstanding instance is released; v1 does not queue for additional quota.

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
            raise RLEError("reserve quota first: enter the OpenEnvClient context before get_instance()")
        instance = _acquire_instance(
            self._instances,
            group_id,
            create_timeout_s=self._create_timeout_s,
            poll_interval_s=self._poll_interval_s,
        )
        openenv_instance = OpenEnvInstance(group_id, instance=instance, instances=self._instances)
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
        self._instance_group_id = None
        try:
            self._instance_groups.delete_instance_group(group_id)
        except HttpResponseError:
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

    @distributed_trace
    def create_environment(self, body: Union[CreateRLEnvironmentRequest, IO[bytes]], **kwargs: Any) -> RLEnvironment:
        """Create a new hosted RLE environment.

        :param body: The environment to create. Is either a
         :class:`~azure.ai.projects.models.CreateRLEnvironmentRequest` or a binary body. Required.
        :type body: ~azure.ai.projects.models.CreateRLEnvironmentRequest or IO[bytes]
        :return: The created RLEnvironment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._environments.create_environment(body, **kwargs)

    @distributed_trace
    def list_environments(
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
        return self._environments.list_environments(name=name, skip=skip, top=top, **kwargs)

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
    def get_environment_version(self, name: str, version: str, **kwargs: Any) -> RLEnvironment:
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
    def list_environment_versions(self, name: str, **kwargs: Any) -> List[RLEnvironmentVersion]:
        """List historical versions of a hosted RLE environment.

        :param name: Environment name. Required.
        :type name: str
        :return: The list of environment versions.
        :rtype: list[~azure.ai.projects.models.RLEnvironmentVersion]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._environments.list_rl_environment_versions(name, **kwargs)

    @distributed_trace
    def delete_environment_version(self, name: str, version: str, **kwargs: Any) -> None:
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
        num_instances: int = 1,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> OpenEnvClient:
        """Create an :class:`OpenEnvClient` over a hosted RLE environment.

        This constructs the client without any network I/O. The returned client is a context manager:
        entering it resolves the environment by ``name`` (and ``version`` when supplied) -- so a
        missing or invalid environment fails on entry -- then creates an instance group that reserves
        its concurrency on the service and fails fast if that quota cannot be granted (v1 does not
        queue). :meth:`OpenEnvClient.get_instance` then leases running :class:`OpenEnvInstance`
        objects from the group on demand to run episodes on. Requests flow through this client's
        pipeline and the Foundry project endpoint.

        :keyword name: The hosted RLE environment name to resolve. Required.
        :paramtype name: str
        :keyword version: Optional environment image version. When set, the environment is resolved at
         that version and the instance group is pinned to it; otherwise the latest version is used.
        :paramtype version: str or None
        :keyword num_instances: Concurrency to reserve on the group, so that several episodes can run
         concurrently. Defaults to 1.
        :paramtype num_instances: int
        :keyword create_timeout_s: Maximum time to wait for each leased instance to become ready, in
         seconds. Default value is 300.
        :paramtype create_timeout_s: float
        :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 2.
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
            name=name,
            version=version,
            num_instances=num_instances,
            create_timeout_s=create_timeout_s,
            poll_interval_s=poll_interval_s,
        )


__all__ = [
    "OpenEnvClient",
    "RLEError",
    "RLEQuotaExceededError",
    "RLEAtCapacityError",
    "OpenEnvInstance",
    "RLEOperations",
    "coerce_action",
]
