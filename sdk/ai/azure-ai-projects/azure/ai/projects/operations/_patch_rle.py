# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""RLE environment runtime helpers.

These helpers layer a Gymnasium-style ergonomic surface on top of the generated RLE operations.
Every request is issued through the :class:`~azure.ai.projects.AIProjectClient` pipeline against the
Foundry project endpoint, exactly like the other operation groups on the client.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, IO, List, Literal, Mapping, Optional, Union, overload

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace

from ..models import (
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
from ..models._enums import _FoundryFeaturesOptInKeys
from ._operations import (
    RLEnvironmentsOperations as _RLEnvironmentsOperationsGenerated,
    RLESandboxesOperations,
)

_DEFAULT_CREATE_TIMEOUT_S = 300.0
_DEFAULT_POLL_INTERVAL_S = 2.0
_RLE_FEATURE: Literal[_FoundryFeaturesOptInKeys.RL_ENVIRONMENT_V1_PREVIEW] = (
    _FoundryFeaturesOptInKeys.RL_ENVIRONMENT_V1_PREVIEW
)


class RLEError(RuntimeError):
    """Raised when leasing an RLE sandbox does not reach a usable state.

    HTTP failures from the service surface as :class:`~azure.core.exceptions.HttpResponseError`,
    consistent with the other operation groups. ``RLEError`` covers client-side lease conditions,
    such as a sandbox that fails to start or never becomes ready within the timeout.
    """


def _status_matches(status: Any, target: RLESandboxStatus) -> bool:
    value = getattr(status, "value", status)
    return str(value or "").lower() == target.value.lower()


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


def _lease_running_sandbox(
    sandboxes: RLESandboxesOperations,
    environment_id: str,
    lease_request: CreateRLESandboxRequest,
    *,
    create_timeout_s: float,
    poll_interval_s: float,
) -> RLESandbox:
    """Lease a sandbox and poll until it reports the ``Running`` status.

    :param sandboxes: Generated sandbox operations bound to the project client.
    :type sandboxes: ~azure.ai.projects.operations.RLESandboxesOperations
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
    sandbox = sandboxes.lease(environment_id, lease_request, foundry_features=_RLE_FEATURE)
    if not sandbox.id:
        raise RLEError("service did not return a sandbox id")
    sandbox_id = sandbox.id
    deadline = time.monotonic() + create_timeout_s
    while not _status_matches(sandbox.status, RLESandboxStatus.RUNNING):
        if _status_matches(sandbox.status, RLESandboxStatus.FAILED):
            raise RLEError(f"sandbox {sandbox_id} failed to start: {sandbox.error or 'unknown error'}")
        if time.monotonic() >= deadline:
            raise RLEError(
                f"sandbox {sandbox_id} not ready after {create_timeout_s:.0f}s "
                f"(last status: {sandbox.status or 'unknown'})"
            )
        time.sleep(poll_interval_s)
        sandbox = sandboxes.get_sandbox(environment_id, sandbox_id, foundry_features=_RLE_FEATURE)
    return sandbox


class OpenEnvInstance:
    """A leased RLE sandbox ("instance") that runs episodes, addressable via its data-plane URI.

    An instance is obtained from :meth:`OpenEnvClient.get_instance`. It wraps a single leased
    sandbox and drives the OpenEnv / Gymnasium runtime operations (``reset``/``step``/``state``)
    against it. Each :meth:`reset` starts a new episode, so an instance may be reused across
    multiple episodes (shared) or scoped to a single episode (exclusive) -- callers pick by how
    they scope the ``with`` block. Runtime requests flow through the owning project client's
    pipeline; :attr:`dataplane_uri` exposes the sandbox's data-plane base URL.

    :param environment_id: The hosted RLE environment ID the instance was leased from. Required.
    :type environment_id: str
    :keyword sandbox: The leased, running sandbox that backs this instance. Required.
    :paramtype sandbox: ~azure.ai.projects.models.RLESandbox
    :keyword sandboxes: Generated sandbox operations bound to the project client. Required.
    :paramtype sandboxes: ~azure.ai.projects.operations.RLESandboxesOperations
    :keyword owner: The :class:`OpenEnvClient` that owns the instance, if any. When set, exiting the
     instance context returns it to the owner's pool instead of releasing it.
    :paramtype owner: ~azure.ai.projects.operations.OpenEnvClient or None
    """

    def __init__(
        self,
        environment_id: str,
        *,
        sandbox: RLESandbox,
        sandboxes: RLESandboxesOperations,
        owner: Optional["OpenEnvClient"] = None,
    ) -> None:
        if not environment_id:
            raise ValueError("environment_id is required")
        if not sandbox.id:
            raise RLEError("sandbox is missing an id")
        self._environment_id = environment_id
        self._sandbox = sandbox
        self._sandbox_id: str = sandbox.id
        self._sandboxes = sandboxes
        self._owner = owner

    @property
    def id(self) -> str:
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

    def __enter__(self) -> "OpenEnvInstance":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.checkin()

    def checkin(self) -> None:
        """Return the instance to its owning :class:`OpenEnvClient` pool, best effort.

        For an instance without an owner this is a no-op; the owner releases the underlying
        sandbox when it is closed.
        """
        owner = self._owner
        if owner is not None:
            owner._return_instance(self)  # pylint: disable=protected-access

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
        self._ensure_healthy()
        body = RLEResetRequest(seed=seed, episode_id=episode_id)
        return self._sandboxes.reset(
            self._environment_id, self._sandbox_id, body, foundry_features=_RLE_FEATURE, **kwargs
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
        body = RLEStepRequest(action=coerce_action(action, action_kwargs))
        return self._sandboxes.step(self._environment_id, self._sandbox_id, body, foundry_features=_RLE_FEATURE)

    @distributed_trace
    def state(self) -> RLEnvironmentState:
        """Return the current environment state for this instance.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        self._ensure_healthy()
        return self._sandboxes.state(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace
    def health(self) -> Dict[str, Any]:
        """Return instance health information.

        :return: Instance health information.
        :rtype: dict[str, any]
        """
        return self._sandboxes.health(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace
    def metadata(self) -> Dict[str, Any]:
        """Return instance metadata.

        :return: Instance metadata.
        :rtype: dict[str, any]
        """
        self._ensure_healthy()
        return self._sandboxes.get_metadata(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    @distributed_trace
    def schema(self) -> Dict[str, Any]:
        """Return the instance action and observation schema.

        :return: The instance action and observation schema.
        :rtype: dict[str, any]
        """
        self._ensure_healthy()
        return self._sandboxes.schema(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    def _ensure_healthy(self) -> None:
        """Confirm the instance reports healthy before issuing a runtime request.

        A failed health probe surfaces as :class:`~azure.core.exceptions.HttpResponseError`,
        consistent with the other operation groups.
        """
        self._sandboxes.health(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)

    def _release(self) -> None:
        """Release the underlying sandbox, best effort."""
        try:
            self._sandboxes.release(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)
        except HttpResponseError:
            pass


class OpenEnvClient:
    """A client over a hosted RLE (OpenEnv) environment with a reserved concurrency quota.

    Created via :meth:`RLEOperations.get_openenv_client`. On entering its context (or calling
    :meth:`reserve`) the client leases ``num_instances`` running instances up front. This is the
    v1 quota model: the customer's concurrency requirement is provided in advance and the request
    fails immediately if the quota cannot be satisfied -- there is no queueing. Future revisions may
    relax this with queueing and elastic scaling.

    :meth:`get_instance` hands out one of the reserved :class:`OpenEnvInstance` objects. Because each
    :meth:`OpenEnvInstance.reset` starts a fresh episode, an instance may be shared across episodes
    (return it to the pool and reuse it) or dedicated to a single episode. Closing the client
    releases every leased instance.

    :keyword environment_id: The hosted RLE environment ID instances are leased from. Required.
    :paramtype environment_id: str
    :keyword sandboxes: Generated sandbox operations bound to the project client. Required.
    :paramtype sandboxes: ~azure.ai.projects.operations.RLESandboxesOperations
    :keyword num_instances: Number of instances to reserve in advance. Required.
    :paramtype num_instances: int
    :keyword lease_request: The sandbox lease request used for every reserved instance. Required.
    :paramtype lease_request: ~azure.ai.projects.models.CreateRLESandboxRequest
    :keyword create_timeout_s: Maximum time to wait for each instance to become ready, in seconds.
     Default value is 300.
    :paramtype create_timeout_s: float
    :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 2.
    :paramtype poll_interval_s: float
    """

    def __init__(
        self,
        *,
        environment_id: str,
        sandboxes: RLESandboxesOperations,
        num_instances: int,
        lease_request: CreateRLESandboxRequest,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> None:
        if not environment_id:
            raise ValueError("environment_id is required")
        if num_instances < 1:
            raise ValueError("num_instances must be >= 1")
        self._environment_id = environment_id
        self._sandboxes = sandboxes
        self._num_instances = num_instances
        self._lease_request = lease_request
        self._create_timeout_s = create_timeout_s
        self._poll_interval_s = poll_interval_s
        self._pool: List[OpenEnvInstance] = []
        self._available: List[OpenEnvInstance] = []
        self._lock = threading.Lock()
        self._reserved = False
        self._closed = False

    @property
    def environment_id(self) -> str:
        """The hosted RLE environment ID instances are leased from."""
        return self._environment_id

    @property
    def num_instances(self) -> int:
        """Number of instances reserved in advance for this client."""
        return self._num_instances

    @property
    def instances(self) -> List[OpenEnvInstance]:
        """The reserved instances owned by this client."""
        return list(self._pool)

    def __enter__(self) -> "OpenEnvClient":
        self.reserve()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def reserve(self) -> None:
        """Lease ``num_instances`` running instances in advance.

        This is idempotent: reserving an already-reserved client does nothing. If the quota cannot
        be satisfied, any partially-leased instances are released and an error is raised (v1 fails
        fast rather than queueing).
        """
        with self._lock:
            if self._reserved:
                return
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            try:
                for _ in range(self._num_instances):
                    sandbox = _lease_running_sandbox(
                        self._sandboxes,
                        self._environment_id,
                        self._lease_request,
                        create_timeout_s=self._create_timeout_s,
                        poll_interval_s=self._poll_interval_s,
                    )
                    instance = OpenEnvInstance(
                        self._environment_id, sandbox=sandbox, sandboxes=self._sandboxes, owner=self
                    )
                    self._pool.append(instance)
                    self._available.append(instance)
            except BaseException:
                self._release_all_locked()
                raise
            self._reserved = True

    def get_instance(self) -> OpenEnvInstance:
        """Check out a reserved instance for one or more episodes.

        The returned :class:`OpenEnvInstance` is a context manager; exiting its context returns it to
        the pool so it can be reused. In v1 the pool is bounded by ``num_instances`` and this
        method fails when every reserved instance is already checked out -- it does not queue.

        :return: A reserved instance ready to run episodes.
        :rtype: ~azure.ai.projects.operations.OpenEnvInstance
        """
        with self._lock:
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            if not self._reserved:
                raise RLEError(
                    "reserve quota first: enter the OpenEnvClient context or call reserve() before get_instance()"
                )
            if not self._available:
                raise RLEError(
                    f"no instance available within the reserved quota (num_instances={self._num_instances}); "
                    "v1 does not queue for additional quota"
                )
            return self._available.pop()

    def _return_instance(self, instance: OpenEnvInstance) -> None:
        with self._lock:
            if self._closed:
                return
            if instance in self._pool and instance not in self._available:
                self._available.append(instance)

    def close(self) -> None:
        """Release every reserved instance, best effort."""
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._release_all_locked()

    def _release_all_locked(self) -> None:
        pool = list(self._pool)
        self._pool.clear()
        self._available.clear()
        for instance in pool:
            instance._release()  # pylint: disable=protected-access


class RLEOperations(_RLEnvironmentsOperationsGenerated, RLESandboxesOperations):
    """Unified RLE operations over environments and sandboxes, plus the OpenEnv client factory.

    Exposes every generated environment operation (create/list/get/delete) and the sandbox
    read operations (``list_sandboxes``/``get_sandbox``) on a single operation group, accessed
    through the client's ``rle`` attribute. Per-episode runtime operations
    (reset/step/state/health/metadata/schema) are driven through the :class:`OpenEnvInstance` objects
    handed out by the :class:`OpenEnvClient` returned by :meth:`get_openenv_client`.
    """

    @overload
    def create_environment(self, body: CreateRLEnvironmentRequest, **kwargs: Any) -> RLEnvironment: ...
    @overload
    def create_environment(self, body: IO[bytes], **kwargs: Any) -> RLEnvironment: ...
    @overload
    def create_environment(
        self, *, acr_image_path: str, name: Optional[str] = None, **kwargs: Any
    ) -> RLEnvironment: ...

    @distributed_trace
    def create_environment(
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
        kwargs.pop("foundry_features", None)
        if body is None:
            if acr_image_path is None:
                raise TypeError("pass either a request body or the acr_image_path keyword")
            body = CreateRLEnvironmentRequest(acr_image_path=acr_image_path, name=name)
        elif acr_image_path is not None or name is not None:
            raise TypeError("pass either a request body or keyword fields, not both")
        return super().create_environment(body, foundry_features=_RLE_FEATURE, **kwargs)

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
        kwargs.pop("foundry_features", None)
        return super().list_environments(foundry_features=_RLE_FEATURE, name=name, skip=skip, top=top, **kwargs)

    @distributed_trace
    def get_environment(self, name: str, **kwargs: Any) -> RLEnvironment:
        """Get a hosted RLE environment by name, returning its latest version.

        The required preview feature opt-in is supplied automatically.

        :param name: Environment name. Required.
        :type name: str
        :return: The RLE environment.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        """
        kwargs.pop("foundry_features", None)
        return super().get_environment(name, foundry_features=_RLE_FEATURE, **kwargs)

    @distributed_trace
    def get_environment_version(self, name: str, version: str, **kwargs: Any) -> RLEnvironment:
        """Get a specific version of a hosted RLE environment.

        The required preview feature opt-in is supplied automatically.

        :param name: Environment name. Required.
        :type name: str
        :param version: Environment version identifier. Required.
        :type version: str
        :return: The RLE environment version.
        :rtype: ~azure.ai.projects.models.RLEnvironment
        """
        kwargs.pop("foundry_features", None)
        return super().get_environment_version(name, version, foundry_features=_RLE_FEATURE, **kwargs)

    @distributed_trace
    def delete_environment_version(self, name: str, version: str, **kwargs: Any) -> None:
        """Delete a specific version of a hosted RLE environment.

        The required preview feature opt-in is supplied automatically.

        :param name: Environment name. Required.
        :type name: str
        :param version: Environment version identifier. Required.
        :type version: str
        :return: None
        :rtype: None
        """
        kwargs.pop("foundry_features", None)
        return super().delete_environment_version(name, version, foundry_features=_RLE_FEATURE, **kwargs)

    @distributed_trace
    def list_rl_environment_versions(self, name: str, **kwargs: Any) -> List[RLEnvironmentVersion]:
        """List historical versions of a hosted RLE environment.

        The required preview feature opt-in is supplied automatically.

        :param name: Environment name. Required.
        :type name: str
        :return: The environment versions.
        :rtype: list[~azure.ai.projects.models.RLEnvironmentVersion]
        """
        kwargs.pop("foundry_features", None)
        return super().list_rl_environment_versions(name, foundry_features=_RLE_FEATURE, **kwargs)

    # --- Sandbox operations (preview feature opt-in supplied automatically) ---

    @distributed_trace
    def list_sandboxes(
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
        return super().list_sandboxes(environment_id, foundry_features=_RLE_FEATURE, skip=skip, top=top, **kwargs)

    @distributed_trace
    def get_sandbox(self, environment_id: str, sandbox_id: str, **kwargs: Any) -> RLESandbox:
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
        return super().get_sandbox(environment_id, sandbox_id, foundry_features=_RLE_FEATURE, **kwargs)

    @distributed_trace
    def get_openenv_client(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        num_instances: int = 1,
        env_vars: Optional[Mapping[str, str]] = None,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> OpenEnvClient:
        """Create an :class:`OpenEnvClient` over a hosted RLE environment with a reserved quota.

        The environment is resolved by ``name`` (and ``version`` when supplied). The returned client
        is a context manager: entering it leases ``num_instances`` running instances up front and
        fails fast if that quota cannot be satisfied (v1 does not queue). :meth:`OpenEnvClient.get_instance`
        then hands out reserved :class:`OpenEnvInstance` objects to run episodes on. All requests are
        issued through this client's pipeline and the Foundry project endpoint.

        :keyword name: The hosted RLE environment name to resolve. Required.
        :paramtype name: str
        :keyword version: Optional environment image version. When set, the environment is resolved at
         that version and every instance is leased against it; otherwise the latest version is used.
        :paramtype version: str or None
        :keyword num_instances: Number of instances to reserve in advance. The customer's concurrency
         requirement, provided up front. Default value is 1.
        :paramtype num_instances: int
        :keyword env_vars: Environment variables to inject into each instance.
        :paramtype env_vars: mapping[str, str] or None
        :keyword create_timeout_s: Maximum time to wait for each instance to become ready, in seconds.
         Default value is 300.
        :paramtype create_timeout_s: float
        :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 2.
        :paramtype poll_interval_s: float
        :return: An OpenEnv client bound to this client.
        :rtype: ~azure.ai.projects.operations.OpenEnvClient
        """
        if not name:
            raise ValueError("name is required")
        if num_instances < 1:
            raise ValueError("num_instances must be >= 1")
        if version is not None:
            environment = self.get_environment_version(name, version)
        else:
            environment = self.get_environment(name)
        environment_id = environment.environment_id
        if not environment_id:
            raise RLEError(f"environment '{name}' did not resolve to an environment id")
        lease_request = CreateRLESandboxRequest(
            version=version,
            env_vars=dict(env_vars) if env_vars else None,
        )
        return OpenEnvClient(
            environment_id=environment_id,
            sandboxes=self,
            num_instances=num_instances,
            lease_request=lease_request,
            create_timeout_s=create_timeout_s,
            poll_interval_s=poll_interval_s,
        )


__all__ = [
    "OpenEnvClient",
    "RLEError",
    "OpenEnvInstance",
    "RLEOperations",
    "coerce_action",
]
