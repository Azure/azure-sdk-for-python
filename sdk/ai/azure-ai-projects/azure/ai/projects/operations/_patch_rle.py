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

import json
import threading
import time
from typing import Any, Dict, List, Literal, Mapping, Optional

from azure.core.exceptions import HttpResponseError, map_error
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace

from ..models import (
    CreateRLESandboxRequest,
    RLEnvironmentState,
    RLEResetRequest,
    RLESandbox,
    RLEStepRequest,
    RLEStepResult,
    RLESandboxStatus,
)
from ..models._enums import _FoundryFeaturesOptInKeys
from .._utils.model_base import SdkJSONEncoder, _deserialize
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
    try:
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
    except BaseException:
        # The sandbox was leased but never became usable; release it so it does not leak quota.
        try:
            sandboxes.release(environment_id, sandbox_id, foundry_features=_RLE_FEATURE)
        except Exception:  # pylint: disable=broad-except
            pass
        raise
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
        self._client = getattr(sandboxes, "_client", None)
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
        body = RLEResetRequest(seed=seed, episode_id=episode_id)
        response = self._dataplane_request("POST", "/reset", body=body, **kwargs)
        return _deserialize(RLEStepResult, response.json())

    @distributed_trace
    def step(self, action: Any = None, **action_kwargs: Any) -> RLEStepResult:
        """Apply an action and return the resulting observation, reward, and done state.

        :param action: The action to apply, as a mapping or model. Mutually exclusive with keyword fields.
        :type action: any
        :return: The step result after applying the action.
        :rtype: ~azure.ai.projects.models.RLEStepResult
        """
        body = RLEStepRequest(action=coerce_action(action, action_kwargs))
        response = self._dataplane_request("POST", "/step", body=body)
        return _deserialize(RLEStepResult, response.json())

    @distributed_trace
    def state(self) -> RLEnvironmentState:
        """Return the current environment state for this instance.

        :return: The current environment state.
        :rtype: ~azure.ai.projects.models.RLEnvironmentState
        """
        response = self._dataplane_request("GET", "/state")
        return _deserialize(RLEnvironmentState, response.json())

    @distributed_trace
    def health(self) -> Dict[str, Any]:
        """Return instance health information.

        :return: Instance health information.
        :rtype: dict[str, any]
        """
        response = self._dataplane_request("GET", "/health")
        return response.json()

    @distributed_trace
    def metadata(self) -> Dict[str, Any]:
        """Return instance metadata.

        :return: Instance metadata.
        :rtype: dict[str, any]
        """
        response = self._dataplane_request("GET", "/metadata")
        return response.json()

    @distributed_trace
    def schema(self) -> Dict[str, Any]:
        """Return the instance action and observation schema.

        :return: The instance action and observation schema.
        :rtype: dict[str, any]
        """
        response = self._dataplane_request("GET", "/schema")
        return response.json()

    def _dataplane_request(self, method: str, route: str, *, body: Any = None, **kwargs: Any) -> Any:
        """Issue an OpenEnv data-plane request against this instance's :attr:`dataplane_uri`.

        The request flows through the owning project client's pipeline (auth, retries, tracing)
        but targets the sandbox's data-plane base URL directly instead of the control plane.

        :param method: HTTP method, e.g. ``"GET"`` or ``"POST"``.
        :type method: str
        :param route: OpenEnv route to append to the data-plane base URL, e.g. ``"/reset"``.
        :type route: str
        :keyword body: Optional request body model serialized as JSON.
        :paramtype body: any
        :return: The raw HTTP response.
        :rtype: ~azure.core.rest.HttpResponse
        """
        base = self._sandbox.base_url
        if not base:
            raise RLEError("instance has no data-plane URI; the sandbox is not running")
        if self._client is None:
            raise RLEError("instance is not bound to a pipeline client")
        url = base.rstrip("/") + route
        headers = {"Accept": "application/json"}
        content: Optional[str] = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            content = json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore[call-arg]
        request = HttpRequest(method=method, url=url, headers=headers, content=content)
        response = self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        ).http_response
        if response.status_code not in (200,):
            map_error(status_code=response.status_code, response=response, error_map={})
            raise HttpResponseError(response=response)
        return response

    def _release(self) -> None:
        """Release the underlying sandbox, best effort."""
        try:
            self._sandboxes.release(self._environment_id, self._sandbox_id, foundry_features=_RLE_FEATURE)
        except HttpResponseError:
            pass


class OpenEnvClient:
    """A client over a hosted RLE (OpenEnv) environment with a reserved concurrency quota.

    Created via :meth:`RLEOperations.get_openenv_client`. The environment is resolved lazily by
    ``name`` (optionally pinned to ``version``) when the client is first entered. On entering its
    context (or calling :meth:`reserve`) the client leases its reserved instances up front and fails
    immediately if they cannot be provisioned -- there is no queueing. Future revisions may relax
    this with queueing and elastic scaling.

    :meth:`get_instance` hands out one of the reserved :class:`OpenEnvInstance` objects. Because each
    :meth:`OpenEnvInstance.reset` starts a fresh episode, an instance may be shared across episodes
    (return it to the pool and reuse it) or dedicated to a single episode. Closing the client
    releases every leased instance.

    :keyword environments: Generated environment operations used to resolve the environment. Required.
    :paramtype environments: ~azure.ai.projects.operations.RLEnvironmentsOperations
    :keyword sandboxes: Generated sandbox operations bound to the project client. Required.
    :paramtype sandboxes: ~azure.ai.projects.operations.RLESandboxesOperations
    :keyword name: The hosted RLE environment name to resolve. Required.
    :paramtype name: str
    :keyword version: Optional environment image version to resolve and lease against.
    :paramtype version: str or None
    :keyword env_vars: Environment variables to inject into each instance.
    :paramtype env_vars: mapping[str, str] or None
    :keyword num_instances: Number of instances to reserve in advance (internal; defaults to 1).
    :paramtype num_instances: int
    :keyword create_timeout_s: Maximum time to wait for each instance to become ready, in seconds.
     Default value is 300.
    :paramtype create_timeout_s: float
    :keyword poll_interval_s: Interval between instance readiness polls, in seconds. Default value is 2.
    :paramtype poll_interval_s: float
    """

    def __init__(
        self,
        *,
        environments: _RLEnvironmentsOperationsGenerated,
        sandboxes: RLESandboxesOperations,
        name: str,
        version: Optional[str] = None,
        env_vars: Optional[Mapping[str, str]] = None,
        num_instances: int = 1,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> None:
        if not name:
            raise ValueError("name is required")
        if num_instances < 1:
            raise ValueError("num_instances must be >= 1")
        self._environments = environments
        self._sandboxes = sandboxes
        self._name = name
        self._version = version
        self._env_vars = dict(env_vars) if env_vars else None
        self._num_instances = num_instances
        self._create_timeout_s = create_timeout_s
        self._poll_interval_s = poll_interval_s
        self._environment_id: Optional[str] = None
        self._lease_request: Optional[CreateRLESandboxRequest] = None
        self._pool: List[OpenEnvInstance] = []
        self._available: List[OpenEnvInstance] = []
        self._lock = threading.Lock()
        self._reserved = False
        self._closed = False

    @property
    def environment_id(self) -> Optional[str]:
        """The hosted RLE environment ID instances are leased from, once resolved (else ``None``)."""
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

    def _resolve_environment(self) -> None:
        """Resolve ``name``/``version`` to a hosted environment id and build the lease request.

        Called eagerly by :meth:`RLEOperations.get_openenv_client` so a missing environment surfaces
        at the call site. Idempotent: a second call is a no-op once the environment is resolved.
        """
        if self._environment_id is not None:
            return
        if self._version is not None:
            environment = self._environments.get_environment_version(
                self._name, self._version, foundry_features=_RLE_FEATURE
            )
        else:
            environment = self._environments.get_environment(self._name, foundry_features=_RLE_FEATURE)
        environment_id = getattr(environment, "environment_id", None) or getattr(environment, "id", None)
        if not environment_id:
            raise RLEError(f"environment '{self._name}' did not resolve to an environment id")
        self._environment_id = environment_id
        self._lease_request = CreateRLESandboxRequest(
            version=self._version,
            env_vars=dict(self._env_vars) if self._env_vars else None,
        )

    def reserve(self) -> None:
        """Lease ``num_instances`` running instances in advance.

        This is idempotent: reserving an already-reserved client does nothing. The environment is
        resolved on first use if it was not already resolved at construction time. If the quota
        cannot be satisfied, any partially-leased instances are released and an error is raised (v1
        fails fast rather than queueing).
        """
        # TODO: Temporary client-side reservation. This leases each instance individually and fails
        # fast when the requested quota cannot be met. Going forward we will rely on the service to
        # reserve quota and guarantee that ``num_instances`` are provisioned (with queueing and
        # other flexibility), at which point this per-instance leasing loop can be removed.
        with self._lock:
            if self._reserved:
                return
            if self._closed:
                raise RLEError("OpenEnv client is closed")
            if self._environment_id is None:
                self._resolve_environment()
            environment_id = self._environment_id
            lease_request = self._lease_request
            try:
                for _ in range(self._num_instances):
                    sandbox = _lease_running_sandbox(
                        self._sandboxes,
                        environment_id,
                        lease_request,
                        create_timeout_s=self._create_timeout_s,
                        poll_interval_s=self._poll_interval_s,
                    )
                    instance = OpenEnvInstance(environment_id, sandbox=sandbox, sandboxes=self._sandboxes, owner=self)
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


class RLEOperations:
    """Factory for the OpenEnv client over hosted RLE environments.

    Accessed through the client's ``rle`` attribute, this operation group exposes a single entry
    point, :meth:`get_openenv_client`, which resolves a hosted RLE environment and returns an
    :class:`OpenEnvClient`. Customers drive environments entirely through that client and the
    :class:`OpenEnvInstance` objects it hands out (reset/step/state/health/metadata/schema); the
    underlying environment and sandbox management operations are internal.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._environments = _RLEnvironmentsOperationsGenerated(*args, **kwargs)
        self._sandboxes = RLESandboxesOperations(*args, **kwargs)

    @distributed_trace
    def get_openenv_client(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        env_vars: Optional[Mapping[str, str]] = None,
        create_timeout_s: float = _DEFAULT_CREATE_TIMEOUT_S,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    ) -> OpenEnvClient:
        """Create an :class:`OpenEnvClient` over a hosted RLE environment.

        The environment is resolved by ``name`` (and ``version`` when supplied) here, so a missing or
        invalid environment fails at this call. The returned client is a context manager: entering it
        reserves its instances up front and fails fast if that quota cannot be satisfied (v1 does not
        queue).
        :meth:`OpenEnvClient.get_instance` then hands out reserved :class:`OpenEnvInstance` objects to
        run episodes on. Control-plane requests flow through this client's pipeline and the Foundry
        project endpoint; runtime calls (reset/step/state/...) target each instance's data-plane URI.

        :keyword name: The hosted RLE environment name to resolve. Required.
        :paramtype name: str
        :keyword version: Optional environment image version. When set, the environment is resolved at
         that version and every instance is leased against it; otherwise the latest version is used.
        :paramtype version: str or None
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
        client = OpenEnvClient(
            environments=self._environments,
            sandboxes=self._sandboxes,
            name=name,
            version=version,
            env_vars=env_vars,
            create_timeout_s=create_timeout_s,
            poll_interval_s=poll_interval_s,
        )
        client._resolve_environment()
        return client


__all__ = [
    "OpenEnvClient",
    "RLEError",
    "OpenEnvInstance",
    "RLEOperations",
    "coerce_action",
]
