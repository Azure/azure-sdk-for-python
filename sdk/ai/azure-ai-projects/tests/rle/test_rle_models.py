# pylint: disable=too-many-lines
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import asyncio
from types import SimpleNamespace

import pytest

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError, ServiceRequestError

from azure.ai.projects.aio.operations._patch_rle_async import (
    AsyncOpenEnvClient,
    AsyncOpenEnvInstance,
    RLEOperations as AsyncRLEOperations,
)
from azure.ai.projects.aio.operations import _patch_rle_async as async_rle_patch
from azure.ai.projects.models import (
    CreateRLEInstanceGroupRequest,
    ListRLEInstanceGroupsResponse,
    ListRLEnvironmentsResponse,
    ListRLEnvironmentVersionsResponse,
    RLEInstance,
    RLEInstanceGroup,
    RLEInstanceStatus,
    RLEnvironmentState,
    RLEStepResult,
)
from azure.ai.projects.operations import RLEOperations
from azure.ai.projects.operations import _operations as generated_operations
from azure.ai.projects.aio.operations import _operations as generated_async_operations
from azure.ai.projects.operations._patch_rle import (
    coerce_action,
    OpenEnvClient,
    OpenEnvInstance,
    RLEError,
    RLEQuotaExceededError,
    RLEInstanceAcquireTimeoutError,
)


class ActionWithModelDump:
    def model_dump(self):
        return {"code": "model_dump"}


class ActionWithToDict:
    def to_dict(self):
        return {"code": "to_dict"}


class _FakeInstance:
    def __init__(self, instance_id, status, error=None):
        self.instance_id = instance_id
        self.status = status
        self.error = error


class _StaticTokenCredential:
    def get_token(self, *scopes, **kwargs):
        return AccessToken("token", 2**31)


def _pipeline_response(status_code=201, headers=None):
    return SimpleNamespace(
        http_response=SimpleNamespace(status_code=status_code, headers=headers or {})
    )


def _http_response_error(status_code, error_code=None, headers=None):
    # ``HttpResponseError.__init__`` reads ``reason``/``status_code``/``headers`` off the response.
    error = HttpResponseError(
        response=SimpleNamespace(
            status_code=status_code, headers=headers or {}, reason=None
        )
    )
    if error_code is not None:
        error.model = SimpleNamespace(error=SimpleNamespace(code=error_code))
    return error


def _capacity_error(retry_after=5):
    error = _http_response_error(429, headers={"Retry-After": str(retry_after)})
    error.model = SimpleNamespace(code="InstanceGroupAtCapacity")
    return error


def _record_runtime(
    calls,
    op,
    environment_name,
    environment_version,
    instance_group_id,
    instance_id,
    body=None,
):
    """Record a delegated runtime call and return a canned result."""
    calls.append(
        (
            op,
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
            dict(body) if body is not None else None,
        )
    )
    if op in ("reset", "step"):
        return RLEStepResult(observation={"ok": True})
    if op == "state":
        return RLEnvironmentState(episode_id="e", step_count=1)
    return {"status": "ok"}


class _FakeEnvironments:
    def __init__(self, version="resolved-latest"):
        self._version = version
        self.calls = []

    def create_environment(self, body, **kwargs):
        self.calls.append(("create_environment", body, kwargs))
        return SimpleNamespace(name=body.name, acr_image_path=body.acr_image_path)

    def get_environment(self, name):
        self.calls.append(("get_environment", name))
        return SimpleNamespace(name=name, version=self._version)

    def get_environment_version(self, name, version):
        self.calls.append(("get_environment_version", name, version))
        return SimpleNamespace(name=name, version=version)

    def list_environments(self, **kwargs):
        self.calls.append(("list_environments", kwargs))
        return SimpleNamespace(data=[], next_continuation_token=None)

    def list_rl_environment_versions(self, name, **kwargs):
        self.calls.append(("list_rl_environment_versions", name, kwargs))
        return SimpleNamespace(data=[], next_continuation_token=None)


class _AsyncFakeEnvironments:
    def __init__(self, version="resolved-latest"):
        self._version = version
        self.calls = []

    async def create_environment(self, body, **kwargs):
        self.calls.append(("create_environment", body, kwargs))
        return SimpleNamespace(name=body.name, acr_image_path=body.acr_image_path)

    async def get_environment(self, name):
        self.calls.append(("get_environment", name))
        return SimpleNamespace(name=name, version=self._version)

    async def get_environment_version(self, name, version):
        self.calls.append(("get_environment_version", name, version))
        return SimpleNamespace(name=name, version=version)

    async def list_environments(self, **kwargs):
        self.calls.append(("list_environments", kwargs))
        return SimpleNamespace(data=[], next_continuation_token=None)

    async def list_rl_environment_versions(self, name, **kwargs):
        self.calls.append(("list_rl_environment_versions", name, kwargs))
        return SimpleNamespace(data=[], next_continuation_token=None)


def test_rle_public_symbols_are_available():
    assert OpenEnvClient
    assert AsyncOpenEnvClient
    assert OpenEnvInstance
    assert AsyncOpenEnvInstance
    assert RLEError
    assert RLEQuotaExceededError
    assert RLEInstanceAcquireTimeoutError


def test_rle_sync_and_async_modules_export_common_helpers():
    assert {
        "RLEError",
        "RLEQuotaExceededError",
        "RLEInstanceAcquireTimeoutError",
        "coerce_action",
    }.issubset(async_rle_patch.__all__)


def test_rle_symbols_exported_from_public_namespace():
    import azure.ai.projects as projects
    import azure.ai.projects.operations as operations
    import azure.ai.projects.aio.operations as aio_operations
    import azure.ai.projects.models as models

    # Customers interact with RLE only through ``project_client.rle.get_openenv_client(...)``; the
    # OpenEnv client/instance types are reachable via the operations namespaces but are intentionally
    # not top-level package exports. Only ``RLEError`` is surfaced at the package root (for excepts).
    assert getattr(projects, "RLEError")
    assert not hasattr(operations, "RLEError")
    assert getattr(operations, "OpenEnvClient")
    assert getattr(operations, "OpenEnvInstance")
    assert getattr(operations, "RLEInstanceAcquireTimeoutError")
    assert getattr(aio_operations, "AsyncOpenEnvClient")
    assert getattr(aio_operations, "AsyncOpenEnvInstance")
    assert getattr(models, "RLEStepResult")
    assert getattr(models, "RLEnvironmentState")
    assert getattr(models, "RLEInstance")
    assert getattr(models, "RLEInstanceGroup")
    assert (
        getattr(models, "ListRLEnvironmentVersionsResponse")
        is ListRLEnvironmentVersionsResponse
    )


def test_rle_requires_preview_opt_in():
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

    credential = _StaticTokenCredential()
    with AIProjectClient(
        endpoint="https://example.com/api/projects/test", credential=credential
    ) as client:
        assert not hasattr(client, "rle")
    with AIProjectClient(
        endpoint="https://example.com/api/projects/test",
        credential=credential,
        allow_preview=True,
    ) as client:
        assert isinstance(client.rle, RLEOperations)

    async def run():
        client = AsyncAIProjectClient(
            endpoint="https://example.com/api/projects/test", credential=credential
        )
        try:
            assert not hasattr(client, "rle")
        finally:
            await client.close()

        client = AsyncAIProjectClient(
            endpoint="https://example.com/api/projects/test",
            credential=credential,
            allow_preview=True,
        )
        try:
            assert isinstance(client.rle, AsyncRLEOperations)
        finally:
            await client.close()

    asyncio.run(run())


def test_coerce_action_accepts_mapping_or_keyword_fields():
    assert coerce_action({"code": "mapping"}, {}) == {"code": "mapping"}
    assert coerce_action(None, {"code": "kwargs"}) == {"code": "kwargs"}


def test_coerce_action_accepts_object_serializers():
    assert coerce_action(ActionWithModelDump(), {}) == {"code": "model_dump"}
    assert coerce_action(ActionWithToDict(), {}) == {"code": "to_dict"}


def test_coerce_action_rejects_ambiguous_or_invalid_actions():
    with pytest.raises(TypeError):
        coerce_action({"code": "mapping"}, {"other": "field"})

    with pytest.raises(TypeError):
        coerce_action(42, {})


# ---------------------------------------------------------------------------
# OpenEnv client / instance tests
# ---------------------------------------------------------------------------


class _FakeInstanceGroups:
    """Instance-group op-group fake.

    ``create_instance_group`` returns a group with a fixed id (or raises with ``create_status`` to
    simulate quota/other failures), and ``delete_instance_group`` records the teardown.
    """

    def __init__(self, *, group_id="grp-1", create_status=None, create_error_code=None):
        self.group_id = group_id
        self._create_status = create_status
        self._create_error_code = create_error_code
        self.created = []
        self.routes = []
        self.deleted = []

    def create_instance_group(self, environment_name, environment_version, body):
        self.created.append(body)
        self.routes.append((environment_name, environment_version))
        if self._create_status is not None:
            raise _http_response_error(self._create_status, self._create_error_code)
        return SimpleNamespace(
            id=self.group_id,
            instance_group_id=self.group_id,
            environment_name=environment_name,
            environment_version=environment_version,
        )

    def delete_instance_group(self, environment_name, environment_version, instance_group_id):
        self.routes.append((environment_name, environment_version))
        self.deleted.append(instance_group_id)


class _FakeInstances:
    """Instance op-group fake that leases distinct running instances on demand.

    Each ``create_instance`` returns a fresh, already-``Running`` instance with its own id, so
    :meth:`OpenEnvClient.get_instance` can lease instances without polling. When ``fail_on`` matches
    the creation index the instance comes back ``Failed``. ``create_status`` simulates a non-2xx
    create (e.g. ``429``) by raising before any instance is returned.
    """

    def __init__(
        self,
        *,
        fail_on=None,
        create_status=None,
        capacity_failures=0,
        capacity_retry_after=0,
        health_statuses=None,
    ):
        self._next = 0
        self._fail_on = fail_on
        self._create_status = create_status
        self._capacity_failures = capacity_failures
        self._capacity_retry_after = capacity_retry_after
        self._health_statuses = list(health_statuses or [])
        self.released = []
        self.create_routes = []
        self.release_routes = []
        self.calls = []

    def create_instance(
        self, environment_name, environment_version, instance_group_id, *, cls=None
    ):
        self.create_routes.append(
            (environment_name, environment_version, instance_group_id)
        )
        index = self._next
        self._next += 1
        if self._capacity_failures:
            self._capacity_failures -= 1
            raise _capacity_error(self._capacity_retry_after)
        if self._create_status is not None:
            if self._create_status == 429:
                raise _capacity_error()
            raise _http_response_error(
                self._create_status, headers={"Retry-After": "0"}
            )
        if self._fail_on is not None and index == self._fail_on:
            instance = _FakeInstance(
                f"inst-{index}", RLEInstanceStatus.FAILED, error="boom"
            )
        else:
            instance = _FakeInstance(f"inst-{index}", RLEInstanceStatus.RUNNING)
        if cls is not None:
            return cls(_pipeline_response(201), instance, {})
        return instance

    def get_instance(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    def delete_instance(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        self.release_routes.append(
            (environment_name, environment_version, instance_group_id, instance_id)
        )
        self.released.append(instance_id)
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    def reset(
        self,
        environment_name,
        environment_version,
        instance_group_id,
        instance_id,
        body,
    ):
        return _record_runtime(
            self.calls,
            "reset",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
            body,
        )

    def step(
        self,
        environment_name,
        environment_version,
        instance_group_id,
        instance_id,
        body,
    ):
        return _record_runtime(
            self.calls,
            "step",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
            body,
        )

    def state(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return _record_runtime(
            self.calls,
            "state",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
        )

    def health(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        if self._health_statuses:
            status = self._health_statuses.pop(0)
            self.calls.append(
                (
                    "health",
                    environment_name,
                    environment_version,
                    instance_group_id,
                    instance_id,
                    None,
                )
            )
            return {"status": status}
        return _record_runtime(
            self.calls,
            "health",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
        )

    def get_metadata(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return _record_runtime(
            self.calls,
            "metadata",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
        )

    def schema(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return _record_runtime(
            self.calls,
            "schema",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
        )


class _FakeInstances202:
    """Instance fake whose create returns ``202`` (pending) and later reports ``Running``.

    Regression fake for the 202 path: ``create_instance`` is non-idempotent, so it must be issued
    exactly once and the pending instance it returns must be polled by id via ``get_instance``.
    ``create_count``/``get_count`` record the call counts so a test can prove the create is not
    re-issued while provisioning.
    """

    def __init__(self, *, running_after=1):
        self.create_count = 0
        self.get_count = 0
        self.released = []
        self._running_after = running_after

    def create_instance(
        self, environment_name, environment_version, instance_group_id, *, cls=None
    ):
        self.create_count += 1
        instance = _FakeInstance("inst-0", RLEInstanceStatus.CREATING)
        response = _pipeline_response(202, {"Retry-After": "0"})
        if cls is not None:
            return cls(response, instance, {})
        return instance

    def get_instance(
        self,
        environment_name,
        environment_version,
        instance_group_id,
        instance_id,
    ):
        self.get_count += 1
        status = (
            RLEInstanceStatus.RUNNING
            if self.get_count >= self._running_after
            else RLEInstanceStatus.CREATING
        )
        return _FakeInstance(instance_id, status)

    def delete_instance(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        self.released.append(instance_id)
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    def health(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return {"status": "ok"}


def _make_openenv_client(
    max_active_instances=1,
    *,
    fail_on=None,
    groups=None,
    instances=None,
    environments=None,
    instance_acquire_timeout=900,
):
    groups = groups or _FakeInstanceGroups()
    instances = instances or _FakeInstances(fail_on=fail_on)
    client = OpenEnvClient(
        environments=environments or _FakeEnvironments(),
        instance_groups=groups,
        instances=instances,
        runtime=instances,
        name="env-1",
        max_active_instances=max_active_instances,
        instance_acquire_timeout=instance_acquire_timeout,
        poll_interval_s=0,
    )
    return client, groups, instances


def test_openenv_client_creates_group_on_enter():
    client, groups, instances = _make_openenv_client(max_active_instances=3)
    with client:
        # Entering creates one instance group that reserves concurrency on the service. No instances
        # are leased yet -- the service owns the pool and hands them out via get_instance().
        assert client.instance_group_id == "grp-1"
        assert len(groups.created) == 1
        assert groups.created[0].max_active_instances == 3
        assert instances.released == []
    # Closing tears down the group.
    assert groups.deleted == ["grp-1"]


def test_openenv_get_instance_leases_on_demand():
    client, groups, instances = _make_openenv_client(max_active_instances=2)
    with client:
        first = client.get_instance()
        second = client.get_instance()
        assert isinstance(first, OpenEnvInstance)
        assert {first.id, second.id} == {"inst-0", "inst-1"}
    # Closing deletes the group; the service releases any still-leased instances when the group is
    # deleted, so the client does not release them individually.
    assert groups.deleted == ["grp-1"]
    assert instances.released == []


def test_openenv_get_instance_retries_capacity_until_timeout():
    instances = _FakeInstances(create_status=429)
    client, _groups, _instances = _make_openenv_client(
        max_active_instances=1,
        instances=instances,
        instance_acquire_timeout=0.01,
    )
    with client:
        with pytest.raises(RLEInstanceAcquireTimeoutError) as exc_info:
            client.get_instance()
    assert exc_info.value.timeout == 0.01
    assert exc_info.value.last_status == "InstanceGroupAtCapacity"
    assert exc_info.value.details is not None
    assert exc_info.value.details.code == "InstanceGroupAtCapacity"


def test_openenv_get_instance_retries_capacity_then_succeeds(monkeypatch):
    delays = []
    monkeypatch.setattr(
        "azure.ai.projects.operations._patch_rle.time.sleep", delays.append
    )
    instances = _FakeInstances(capacity_failures=1, capacity_retry_after=2)
    client, _groups, _instances = _make_openenv_client(instances=instances)
    with client:
        with client.get_instance() as instance:
            assert instance.id == "inst-1"
    assert len(instances.create_routes) == 2
    assert delays == [2]


def test_openenv_get_instance_does_not_retry_untyped_429():
    class _Untyped429Instances(_FakeInstances):
        def create_instance(
            self,
            environment_name,
            environment_version,
            instance_group_id,
            *,
            cls=None,
        ):
            self.create_routes.append(
                (environment_name, environment_version, instance_group_id)
            )
            raise _http_response_error(429, headers={"Retry-After": "0"})

    instances = _Untyped429Instances()
    client, _groups, _instances = _make_openenv_client(instances=instances)
    with client:
        with pytest.raises(HttpResponseError):
            client.get_instance()
    assert len(instances.create_routes) == 1


def test_openenv_get_instance_releases_failed_instance():
    # An instance that never reaches Running is released so it does not leak quota, and the failure
    # surfaces as RLEError.
    instances = _FakeInstances(fail_on=0)
    client, _groups, _instances = _make_openenv_client(
        max_active_instances=1, instances=instances
    )
    with client:
        with pytest.raises(RLEError):
            client.get_instance()
        assert instances.released == ["inst-0"]


def test_openenv_get_instance_polls_pending_202_without_recreating():
    # A 202 already contains a pending instance. create_instance is not idempotent, so it must be
    # issued exactly once and the pending instance polled by id -- re-POSTing would lease and leak an
    # extra instance for every pending response.
    instances = _FakeInstances202(running_after=2)
    client, _groups, _instances = _make_openenv_client(
        max_active_instances=1, instances=instances
    )
    with client:
        with client.get_instance() as instance:
            assert instance.id == "inst-0"
            assert instance.instance.status == RLEInstanceStatus.RUNNING
    assert instances.create_count == 1
    assert instances.get_count >= 1
    assert instances.released == ["inst-0"]


def test_openenv_get_instance_releases_pending_instance_when_interrupted(monkeypatch):
    instances = _FakeInstances202(running_after=2)

    def interrupt(_delay):
        raise KeyboardInterrupt

    monkeypatch.setattr("azure.ai.projects.operations._patch_rle.time.sleep", interrupt)
    client, _groups, _instances = _make_openenv_client(instances=instances)
    with client:
        with pytest.raises(KeyboardInterrupt):
            client.get_instance()
    assert instances.create_count == 1
    assert instances.released == ["inst-0"]


def test_openenv_get_instance_waits_for_runtime_health():
    instances = _FakeInstances(health_statuses=["starting", "healthy"])
    client, _groups, _instances = _make_openenv_client(instances=instances)
    with client:
        with client.get_instance() as instance:
            assert instance.id == "inst-0"
    assert [call[0] for call in instances.calls] == ["health", "health"]


def test_openenv_get_instance_releases_instance_when_health_times_out():
    class _UnhealthyInstances(_FakeInstances):
        def health(
            self, environment_name, environment_version, instance_group_id, instance_id
        ):
            return {"status": "starting"}

    instances = _UnhealthyInstances()
    client, _groups, _instances = _make_openenv_client(
        instances=instances,
        instance_acquire_timeout=0.01,
    )
    with client:
        with pytest.raises(
            RLEInstanceAcquireTimeoutError, match="runtime was not healthy"
        ):
            client.get_instance()
    assert instances.released == ["inst-0"]


def test_openenv_ensure_group_maps_quota_exceeded():
    groups = _FakeInstanceGroups(create_status=403, create_error_code="QuotaExceeded")
    client, _groups, _instances = _make_openenv_client(
        max_active_instances=1, groups=groups
    )
    with pytest.raises(RLEQuotaExceededError):
        client._ensure_group()


@pytest.mark.parametrize(
    "error_code", ["AuthorizationFailed", "preview_feature_required"]
)
def test_openenv_ensure_group_preserves_non_quota_403(error_code):
    groups = _FakeInstanceGroups(create_status=403, create_error_code=error_code)
    client, _groups, _instances = _make_openenv_client(
        max_active_instances=1, groups=groups
    )
    with pytest.raises(HttpResponseError):
        client._ensure_group()


def test_openenv_ensure_group_deletes_incomplete_group():
    class _IncompleteGroupResponse(_FakeInstanceGroups):
        def create_instance_group(self, environment_name, environment_version, body):
            group = super().create_instance_group(
                environment_name, environment_version, body
            )
            group.environment_version = None
            return group

    groups = _IncompleteGroupResponse()
    client, _groups, _instances = _make_openenv_client(groups=groups)

    with pytest.raises(RLEError, match="environment name and version"):
        client._ensure_group()

    assert groups.deleted == ["grp-1"]


def test_openenv_instance_context_releases_on_exit():
    client, _groups, instances = _make_openenv_client(max_active_instances=1)
    with client:
        with client.get_instance() as instance:
            first_id = instance.id
        # Exiting the instance context released it immediately (no reuse in v1).
        assert instances.released == [first_id]


def test_openenv_instance_release_is_idempotent_and_blocks_runtime_calls():
    client, _groups, instances = _make_openenv_client(max_active_instances=1)
    with client:
        instance = client.get_instance()
        instance.release()
        instance.release()

        assert instances.released == ["inst-0"]
        with pytest.raises(RLEError, match="released"):
            instance.reset()
        with pytest.raises(RLEError, match="released"):
            instance.health()


def test_openenv_instance_release_ignores_transport_failures():
    class _TransportFailingInstances(_FakeInstances):
        def delete_instance(
            self, environment_name, environment_version, instance_group_id, instance_id
        ):
            raise ServiceRequestError("connection lost")

    client, _groups, _instances = _make_openenv_client(
        instances=_TransportFailingInstances()
    )
    with client:
        client.get_instance().release()


def test_openenv_close_ignores_transport_failures():
    class _TransportFailingGroups(_FakeInstanceGroups):
        def delete_instance_group(
            self, environment_name, environment_version, instance_group_id
        ):
            raise ServiceRequestError("connection lost")

    client, _groups, _instances = _make_openenv_client(
        groups=_TransportFailingGroups()
    )
    with client:
        pass


def test_openenv_pending_instance_honors_zero_retry_after(monkeypatch):
    delays = []
    monkeypatch.setattr(
        "azure.ai.projects.operations._patch_rle.time.sleep", delays.append
    )
    instances = _FakeInstances202(running_after=1)
    client = OpenEnvClient(
        environments=_FakeEnvironments(),
        instance_groups=_FakeInstanceGroups(),
        instances=instances,
        runtime=instances,
        name="env-1",
        poll_interval_s=5,
    )
    with client:
        with client.get_instance():
            pass
    assert delays == [0.0]


def test_openenv_instance_runtime_uses_resolved_environment_route():
    client, _groups, instances = _make_openenv_client(max_active_instances=1)
    with client:
        with client.get_instance() as instance:
            assert instance.instance_group_id == "grp-1"
            assert instance.id == "inst-0"
            assert instance.environment_name == "env-1"
            assert instance.environment_version == "resolved-latest"

            assert isinstance(instance.reset(seed=42), RLEStepResult)
            assert isinstance(instance.step({"code": "print(1)"}), RLEStepResult)
            assert isinstance(instance.state(), RLEnvironmentState)
            assert instance.health() == {"status": "ok"}
            assert instance.metadata() == {"status": "ok"}
            assert instance.schema() == {"status": "ok"}

    # Runtime calls use the environment identity resolved by the instance-group create response.
    routes = [call[0] for call in instances.calls]
    assert routes == [
        "health",
        "health",
        "reset",
        "health",
        "step",
        "health",
        "state",
        "health",
        "health",
        "metadata",
        "health",
        "schema",
    ]
    assert all(
        call[1:5] == ("env-1", "resolved-latest", "grp-1", "inst-0")
        for call in instances.calls
    )
    reset_call = instances.calls[2]
    assert reset_call[5].get("seed") == 42


def test_openenv_runtime_calls_use_runtime_operations_group():
    instances = _FakeInstances()
    runtime = _FakeInstances()
    client = OpenEnvClient(
        environments=_FakeEnvironments(),
        instance_groups=_FakeInstanceGroups(),
        instances=instances,
        runtime=runtime,
        name="env-1",
        poll_interval_s=0,
    )
    with client:
        with client.get_instance() as instance:
            instance.reset()
            instance.step({"code": "x"})
            instance.state()
            instance.metadata()
            instance.schema()

    assert instances.calls == []
    assert [call[0] for call in runtime.calls] == [
        "health",
        "health",
        "reset",
        "health",
        "step",
        "health",
        "state",
        "health",
        "metadata",
        "health",
        "schema",
    ]


def test_openenv_instance_blocks_workload_when_health_check_fails():
    instances = _FakeInstances(health_statuses=["ok", "starting"])
    client, _groups, _instances = _make_openenv_client(instances=instances)
    with client:
        with client.get_instance() as instance:
            with pytest.raises(RLEError, match="is not healthy"):
                instance.reset()
    assert [call[0] for call in instances.calls] == ["health", "health"]


def test_openenv_get_instance_requires_enter_first():
    client, _groups, _instances = _make_openenv_client(max_active_instances=1)
    with pytest.raises(RLEError):
        client.get_instance()


def test_ensure_group_resolves_latest_environment_version():
    environments = _FakeEnvironments(version="42")
    client, groups, instances = _make_openenv_client(
        max_active_instances=1, environments=environments
    )
    with client:
        assert client.instance_group_id == "grp-1"
        with client.get_instance():
            pass
    assert environments.calls == [("get_environment", "env-1")]
    assert groups.routes[0] == ("env-1", "42")
    assert groups.routes[1] == ("env-1", "42")
    assert instances.create_routes == [("env-1", "42", "grp-1")]
    body = groups.created[0]
    assert body.max_active_instances == 1


def test_ensure_group_uses_versioned_environment_route():
    environments = _FakeEnvironments()
    groups = _FakeInstanceGroups()
    instances = _FakeInstances()
    client = OpenEnvClient(
        environments=environments,
        instance_groups=groups,
        instances=instances,
        runtime=instances,
        name="wordle",
        version="1",
        poll_interval_s=0,
    )
    with client:
        assert client.instance_group_id == "grp-1"
    assert environments.calls == []
    assert groups.routes[0] == ("wordle", "1")
    assert groups.routes[1] == ("wordle", "1")


def test_get_openenv_client_defers_resolution():
    ops = RLEOperations(object(), object(), object(), object())
    ops._environments = _FakeEnvironments()
    ops._instance_groups = _FakeInstanceGroups()
    ops._instances = _FakeInstances()
    client = ops.get_openenv_client(name="wordle-env", version="1")
    assert isinstance(client, OpenEnvClient)
    # The factory does no network I/O; the environment is resolved on context entry, not here.
    assert client.instance_group_id is None
    assert client.max_active_instances == 1
    assert client.environment_name == "wordle-env"
    assert client.environment_version == "1"


def test_get_openenv_client_validates_arguments():
    ops = RLEOperations(object(), object(), object(), object())
    with pytest.raises(ValueError):
        ops.get_openenv_client(name="")
    for timeout in (0, -1, float("inf"), float("nan"), 3601):
        with pytest.raises(ValueError, match="instance_acquire_timeout"):
            ops.get_openenv_client(name="wordle", instance_acquire_timeout=timeout)


def test_create_environment_builds_request():
    ops = RLEOperations(object(), object(), object(), object())
    environments = _FakeEnvironments()
    ops._environments = environments
    result = ops.create_environment(
        "wordle", "registry.azurecr.io/wordle:v1", version_bump="Minor"
    )
    assert result.name == "wordle"
    body = environments.calls[0][1]
    assert body.name == "wordle"
    assert body.acr_image_path == "registry.azurecr.io/wordle:v1"
    assert body.version_bump == "Minor"


def test_environment_list_helpers_forward_continuation_token_pagination():
    ops = RLEOperations(object(), object(), object(), object())
    environments = _FakeEnvironments()
    ops._environments = environments

    assert list(
        ops.list_environments(
            name="wordle", limit=10, continuation_token="first", order="asc"
        )
    ) == []
    assert list(
        ops.list_environment_versions(
            "wordle", limit=5, continuation_token="last", order="desc"
        )
    ) == []

    assert environments.calls == [
        (
            "list_environments",
            {
                "name": "wordle",
                "limit": 10,
                "continuation_token_parameter": "first",
                "order": "asc",
            },
        ),
        (
            "list_rl_environment_versions",
            "wordle",
            {"limit": 5, "continuation_token_parameter": "last", "order": "desc"},
        ),
    ]


def test_async_environment_list_helpers_return_pagers():
    async def run():
        ops = AsyncRLEOperations(object(), object(), object(), object())
        environments = _AsyncFakeEnvironments()
        ops._environments = environments

        environments_pager = ops.list_environments(
            name="wordle", limit=10, continuation_token="first", order="asc"
        )
        versions_pager = ops.list_environment_versions(
            "wordle", limit=5, continuation_token="last", order="desc"
        )

        assert [item async for item in environments_pager] == []
        assert [item async for item in versions_pager] == []
        assert environments.calls == [
            (
                "list_environments",
                {
                    "name": "wordle",
                    "limit": 10,
                    "continuation_token_parameter": "first",
                    "order": "asc",
                },
            ),
            (
                "list_rl_environment_versions",
                "wordle",
                {"limit": 5, "continuation_token_parameter": "last", "order": "desc"},
            ),
        ]

    asyncio.run(run())


@pytest.mark.parametrize("limit", (0, 101))
def test_environment_list_helpers_reject_invalid_pagination_limits(limit):
    ops = RLEOperations(object(), object(), object(), object())
    environments = _FakeEnvironments()
    ops._environments = environments

    with pytest.raises(ValueError, match=r"range \[1, 100\]"):
        ops.list_environments(limit=limit)
    with pytest.raises(ValueError, match=r"range \[1, 100\]"):
        ops.list_environment_versions("wordle", limit=limit)

    assert environments.calls == []


@pytest.mark.parametrize("limit", (0, 101))
def test_async_environment_list_helpers_reject_invalid_pagination_limits(limit):
    async def run():
        ops = AsyncRLEOperations(object(), object(), object(), object())
        environments = _AsyncFakeEnvironments()
        ops._environments = environments

        with pytest.raises(ValueError, match=r"range \[1, 100\]"):
            ops.list_environments(limit=limit)
        with pytest.raises(ValueError, match=r"range \[1, 100\]"):
            ops.list_environment_versions("wordle", limit=limit)

        assert environments.calls == []

    asyncio.run(run())


def test_rle_list_responses_expose_continuation_tokens():
    environment_response = ListRLEnvironmentsResponse(
        data=[], next_continuation_token="environments-next"
    )
    version_response = ListRLEnvironmentVersionsResponse(
        data=[], next_continuation_token="versions-next"
    )
    instance_group_response = ListRLEInstanceGroupsResponse(
        data=[], next_continuation_token="groups-next"
    )

    assert environment_response.next_continuation_token == "environments-next"
    assert version_response.next_continuation_token == "versions-next"
    assert instance_group_response.next_continuation_token == "groups-next"


def test_instance_group_list_builder_uses_continuation_token_pagination():
    request = (
        generated_operations.build_rle_instance_groups_list_instance_groups_request(
            "wordle",
            "1",
            limit=20,
            continuation_token_parameter="groups-next",
        )
    )

    assert request.query["limit"] == "20"
    assert request.query["continuationToken"] == "groups-next"
    assert "after" not in request.query
    assert "before" not in request.query


def test_create_environment_builder_uses_collection_root():
    request = generated_operations.build_rl_environments_create_environment_request()
    assert request.url.split("?")[0] == "/rl_environments"


@pytest.mark.parametrize(
    "builder_name,args,suffix",
    [
        (
            "build_rle_instance_groups_create_instance_group_request",
            (),
            "/instance_groups",
        ),
        (
            "build_rle_instance_groups_list_instance_groups_request",
            (),
            "/instance_groups",
        ),
        (
            "build_rle_instance_groups_get_instance_group_request",
            ("group-1",),
            "/instance_groups/group-1",
        ),
        (
            "build_rle_instance_groups_delete_instance_group_request",
            ("group-1",),
            "/instance_groups/group-1",
        ),
        (
            "build_rle_instances_create_instance_request",
            ("group-1",),
            "/instance_groups/group-1/instances",
        ),
        (
            "build_rle_instances_get_instance_request",
            ("group-1", "instance-1"),
            "/instance_groups/group-1/instances/instance-1",
        ),
        (
            "build_rle_instances_delete_instance_request",
            ("group-1", "instance-1"),
            "/instance_groups/group-1/instances/instance-1",
        ),
    ],
)
def test_rle_control_plane_routes_include_environment(builder_name, args, suffix):
    builder = getattr(generated_operations, builder_name)
    request = builder("wordle", "42", *args)
    assert request.url.split("?")[0] == f"/rl_environments/wordle/versions/42{suffix}"


@pytest.mark.parametrize(
    "operation", ["reset", "step", "state", "health", "get_metadata", "schema"]
)
def test_rle_runtime_routes_include_resolved_environment_and_group(operation):
    builder = getattr(
        generated_operations, f"build_rle_instance_runtime_{operation}_request"
    )
    request = builder("wordle", "42", "group-1", "instance-1")
    suffix = "metadata" if operation == "get_metadata" else operation
    assert request.url.split("?")[0] == (
        "/rl_environments/wordle/versions/42/instance_groups/group-1/"
        f"instances/instance-1/openenv/{suffix}"
    )


@pytest.mark.parametrize(
    "operation", ["reset", "step", "state", "health", "get_metadata", "schema"]
)
def test_rle_runtime_routes_require_environment_version(operation):
    builder = getattr(
        generated_operations, f"build_rle_instance_runtime_{operation}_request"
    )
    with pytest.raises(ValueError):
        builder("wordle", None, "group-1", "instance-1")


def test_create_instance_group_request_uses_max_active_instances():
    request = CreateRLEInstanceGroupRequest(max_active_instances=3)
    assert request.max_active_instances == 3
    assert not hasattr(request, "environment_name")
    assert not hasattr(request, "environment_version")


def test_unsupported_instance_group_operations_are_not_public():
    from azure.ai.projects.aio.operations import _operations as aio_generated_operations

    assert not hasattr(
        generated_operations.RLEInstanceGroupsOperations, "update_instance_group"
    )
    assert not hasattr(
        aio_generated_operations.RLEInstanceGroupsOperations, "update_instance_group"
    )
    assert not hasattr(generated_operations.RLEInstancesOperations, "list_instances")
    assert not hasattr(
        aio_generated_operations.RLEInstancesOperations, "list_instances"
    )


class _AsyncFakeInstanceGroups:
    def __init__(self, *, group_id="grp-1", create_status=None, create_error_code=None):
        self.group_id = group_id
        self._create_status = create_status
        self._create_error_code = create_error_code
        self.created = []
        self.routes = []
        self.deleted = []

    async def create_instance_group(self, environment_name, environment_version, body):
        self.created.append(body)
        self.routes.append((environment_name, environment_version))
        if self._create_status is not None:
            raise _http_response_error(self._create_status, self._create_error_code)
        return SimpleNamespace(
            id=self.group_id,
            instance_group_id=self.group_id,
            environment_name=environment_name,
            environment_version=environment_version,
        )

    async def delete_instance_group(
        self, environment_name, environment_version, instance_group_id
    ):
        self.routes.append((environment_name, environment_version))
        self.deleted.append(instance_group_id)


class _AsyncFakeInstances:
    def __init__(
        self,
        *,
        fail_on=None,
        create_status=None,
        capacity_failures=0,
        capacity_retry_after=0,
        health_statuses=None,
    ):
        self._next = 0
        self._fail_on = fail_on
        self._create_status = create_status
        self._capacity_failures = capacity_failures
        self._capacity_retry_after = capacity_retry_after
        self._health_statuses = list(health_statuses or [])
        self.released = []
        self.create_routes = []
        self.release_routes = []
        self.calls = []

    async def create_instance(
        self, environment_name, environment_version, instance_group_id, *, cls=None
    ):
        self.create_routes.append(
            (environment_name, environment_version, instance_group_id)
        )
        index = self._next
        self._next += 1
        if self._capacity_failures:
            self._capacity_failures -= 1
            raise _capacity_error(self._capacity_retry_after)
        if self._create_status is not None:
            if self._create_status == 429:
                raise _capacity_error()
            raise _http_response_error(
                self._create_status, headers={"Retry-After": "0"}
            )
        if self._fail_on is not None and index == self._fail_on:
            instance = _FakeInstance(
                f"inst-{index}", RLEInstanceStatus.FAILED, error="boom"
            )
        else:
            instance = _FakeInstance(f"inst-{index}", RLEInstanceStatus.RUNNING)
        if cls is not None:
            return cls(_pipeline_response(201), instance, {})
        return instance

    async def get_instance(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    async def delete_instance(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        self.release_routes.append(
            (environment_name, environment_version, instance_group_id, instance_id)
        )
        self.released.append(instance_id)
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    async def reset(
        self,
        environment_name,
        environment_version,
        instance_group_id,
        instance_id,
        body,
    ):
        return _record_runtime(
            self.calls,
            "reset",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
            body,
        )

    async def step(
        self,
        environment_name,
        environment_version,
        instance_group_id,
        instance_id,
        body,
    ):
        return _record_runtime(
            self.calls,
            "step",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
            body,
        )

    async def state(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return _record_runtime(
            self.calls,
            "state",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
        )

    async def health(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        if self._health_statuses:
            status = self._health_statuses.pop(0)
            self.calls.append(
                (
                    "health",
                    environment_name,
                    environment_version,
                    instance_group_id,
                    instance_id,
                    None,
                )
            )
            return {"status": status}
        return _record_runtime(
            self.calls,
            "health",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
        )

    async def get_metadata(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return _record_runtime(
            self.calls,
            "metadata",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
        )

    async def schema(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return _record_runtime(
            self.calls,
            "schema",
            environment_name,
            environment_version,
            instance_group_id,
            instance_id,
        )


class _AsyncFakeInstances202:
    """Async instance fake whose create returns ``202`` (pending) and later reports ``Running``.

    Async regression fake for the 202 path: ``create_instance`` is non-idempotent, so it must be
    issued exactly once and the pending instance polled by id via ``get_instance``.
    """

    def __init__(self, *, running_after=1):
        self.create_count = 0
        self.get_count = 0
        self.released = []
        self._running_after = running_after

    async def create_instance(
        self, environment_name, environment_version, instance_group_id, *, cls=None
    ):
        self.create_count += 1
        instance = _FakeInstance("inst-0", RLEInstanceStatus.CREATING)
        response = _pipeline_response(202, {"Retry-After": "0"})
        if cls is not None:
            return cls(response, instance, {})
        return instance

    async def get_instance(
        self,
        environment_name,
        environment_version,
        instance_group_id,
        instance_id,
    ):
        self.get_count += 1
        status = (
            RLEInstanceStatus.RUNNING
            if self.get_count >= self._running_after
            else RLEInstanceStatus.CREATING
        )
        return _FakeInstance(instance_id, status)

    async def delete_instance(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        self.released.append(instance_id)
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    async def health(
        self, environment_name, environment_version, instance_group_id, instance_id
    ):
        return {"status": "ok"}


def _make_async_openenv_client(
    max_active_instances=1,
    *,
    fail_on=None,
    groups=None,
    instances=None,
    environments=None,
    instance_acquire_timeout=900,
):
    groups = groups or _AsyncFakeInstanceGroups()
    instances = instances or _AsyncFakeInstances(fail_on=fail_on)
    client = AsyncOpenEnvClient(
        environments=environments or _AsyncFakeEnvironments(),
        instance_groups=groups,
        instances=instances,
        runtime=instances,
        name="env-1",
        max_active_instances=max_active_instances,
        instance_acquire_timeout=instance_acquire_timeout,
        poll_interval_s=0,
    )
    return client, groups, instances


def test_async_openenv_client_creates_group_and_runs():
    async def run():
        client, groups, instances = _make_async_openenv_client(max_active_instances=2)
        async with client:
            assert client.instance_group_id == "grp-1"
            assert client.environment_name == "env-1"
            assert client.environment_version == "resolved-latest"
            # Entering only creates the group; instances are leased on demand.
            instance_context = client.get_instance()
            assert instances._next == 0
            async with instance_context as instance:
                assert isinstance(instance, AsyncOpenEnvInstance)
                assert instance.id.startswith("inst-")
                assert instance.environment_name == "env-1"
                assert instance.environment_version == "resolved-latest"
                assert isinstance(await instance.reset(seed=7), RLEStepResult)
                assert isinstance(await instance.step({"code": "x"}), RLEStepResult)
                assert isinstance(await instance.state(), RLEnvironmentState)
                assert await instance.health() == {"status": "ok"}
                assert await instance.metadata() == {"status": "ok"}
                assert await instance.schema() == {"status": "ok"}
        assert instances.released == ["inst-0"]
        assert instances.create_routes == [("env-1", "resolved-latest", "grp-1")]
        assert groups.deleted == ["grp-1"]
        assert groups.routes == [
            ("env-1", "resolved-latest"),
            ("env-1", "resolved-latest"),
        ]
        # Runtime calls use the environment identity resolved by the instance-group create response.
        routes = [call[0] for call in instances.calls]
        assert routes == [
            "health",
            "health",
            "reset",
            "health",
            "step",
            "health",
            "state",
            "health",
            "health",
            "metadata",
            "health",
            "schema",
        ]
        assert all(
            call[1:5] == ("env-1", "resolved-latest", "grp-1", "inst-0")
            for call in instances.calls
        )

    asyncio.run(run())


def test_async_openenv_runtime_calls_use_runtime_operations_group():
    async def run():
        instances = _AsyncFakeInstances()
        runtime = _AsyncFakeInstances()
        client = AsyncOpenEnvClient(
            environments=_AsyncFakeEnvironments(),
            instance_groups=_AsyncFakeInstanceGroups(),
            instances=instances,
            runtime=runtime,
            name="env-1",
            poll_interval_s=0,
        )
        async with client:
            async with client.get_instance() as instance:
                await instance.reset()
                await instance.step({"code": "x"})
                await instance.state()
                await instance.metadata()
                await instance.schema()

        assert instances.calls == []
        assert [call[0] for call in runtime.calls] == [
            "health",
            "health",
            "reset",
            "health",
            "step",
            "health",
            "state",
            "health",
            "metadata",
            "health",
            "schema",
        ]

    asyncio.run(run())


def test_async_openenv_instance_blocks_workload_when_health_check_fails():
    async def run():
        instances = _AsyncFakeInstances(health_statuses=["ok", "starting"])
        client, _groups, _instances = _make_async_openenv_client(instances=instances)
        async with client:
            async with client.get_instance() as instance:
                with pytest.raises(RLEError, match="is not healthy"):
                    await instance.step({"code": "x"})
        assert [call[0] for call in instances.calls] == ["health", "health"]

    asyncio.run(run())


def test_async_openenv_instance_release_is_idempotent_and_blocks_runtime_calls():
    async def run():
        client, _groups, instances = _make_async_openenv_client(max_active_instances=1)
        async with client:
            instance = client.get_instance()
            await instance.__aenter__()
            await instance.release()
            await instance.release()

            assert instances.released == ["inst-0"]
            with pytest.raises(RLEError, match="released"):
                await instance.reset()
            with pytest.raises(RLEError, match="released"):
                await instance.health()

    asyncio.run(run())


def test_async_openenv_instance_release_ignores_transport_failures():
    class _TransportFailingInstances(_AsyncFakeInstances):
        async def delete_instance(
            self, environment_name, environment_version, instance_group_id, instance_id
        ):
            raise ServiceRequestError("connection lost")

    async def run():
        client, _groups, _instances = _make_async_openenv_client(
            instances=_TransportFailingInstances()
        )
        async with client:
            instance = client.get_instance()
            await instance.__aenter__()
            await instance.release()

    asyncio.run(run())


def test_async_openenv_close_ignores_transport_failures():
    class _TransportFailingGroups(_AsyncFakeInstanceGroups):
        async def delete_instance_group(
            self, environment_name, environment_version, instance_group_id
        ):
            raise ServiceRequestError("connection lost")

    async def run():
        client, _groups, _instances = _make_async_openenv_client(
            groups=_TransportFailingGroups()
        )
        async with client:
            pass

    asyncio.run(run())


def test_async_openenv_pending_instance_honors_zero_retry_after(monkeypatch):
    delays = []

    async def record_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(
        "azure.ai.projects.aio.operations._patch_rle_async.asyncio.sleep", record_sleep
    )

    async def run():
        instances = _AsyncFakeInstances202(running_after=1)
        client = AsyncOpenEnvClient(
            environments=_AsyncFakeEnvironments(),
            instance_groups=_AsyncFakeInstanceGroups(),
            instances=instances,
            runtime=instances,
            name="env-1",
            poll_interval_s=5,
        )
        async with client:
            async with client.get_instance():
                pass

    asyncio.run(run())
    assert delays == [0.0]


def test_async_openenv_get_instance_leases_on_demand():
    async def run():
        client, groups, instances = _make_async_openenv_client(max_active_instances=2)
        async with client:
            first_context = client.get_instance()
            second_context = client.get_instance()
            async with first_context as first, second_context as second:
                assert {first.id, second.id} == {"inst-0", "inst-1"}
            assert instances.released == ["inst-1", "inst-0"]
        assert groups.deleted == ["grp-1"]

    asyncio.run(run())


def test_async_openenv_get_instance_requires_enter_first():
    client, _groups, _instances = _make_async_openenv_client(max_active_instances=1)
    with pytest.raises(RLEError):
        client.get_instance()


def test_async_openenv_get_instance_retries_capacity_until_timeout():
    async def run():
        instances = _AsyncFakeInstances(create_status=429)
        client, _groups, _instances = _make_async_openenv_client(
            max_active_instances=1,
            instances=instances,
            instance_acquire_timeout=0.01,
        )
        async with client:
            with pytest.raises(RLEInstanceAcquireTimeoutError) as exc_info:
                async with client.get_instance():
                    pass
        assert exc_info.value.timeout == 0.01
        assert exc_info.value.last_status == "InstanceGroupAtCapacity"
        assert exc_info.value.details is not None
        assert exc_info.value.details.code == "InstanceGroupAtCapacity"

    asyncio.run(run())


def test_async_openenv_capacity_timeout_handles_nested_error_code():
    class _NestedCapacityInstances(_AsyncFakeInstances):
        async def create_instance(
            self, environment_name, environment_version, instance_group_id, *, cls=None
        ):
            error = _capacity_error(retry_after=1)
            error.model = SimpleNamespace(
                error=SimpleNamespace(code="InstanceGroupAtCapacity")
            )
            raise error

    async def run():
        client, _groups, _instances = _make_async_openenv_client(
            instances=_NestedCapacityInstances(),
            instance_acquire_timeout=0.01,
        )
        async with client:
            with pytest.raises(RLEInstanceAcquireTimeoutError) as exc_info:
                async with client.get_instance():
                    pass
        assert exc_info.value.last_status == "InstanceGroupAtCapacity"

    asyncio.run(run())


def test_async_openenv_get_instance_retries_capacity_then_succeeds(monkeypatch):
    delays = []

    async def record_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(
        "azure.ai.projects.aio.operations._patch_rle_async.asyncio.sleep", record_sleep
    )

    async def run():
        instances = _AsyncFakeInstances(capacity_failures=1, capacity_retry_after=2)
        client, _groups, _instances = _make_async_openenv_client(instances=instances)
        async with client:
            async with client.get_instance() as instance:
                assert instance.id == "inst-1"
        assert len(instances.create_routes) == 2

    asyncio.run(run())
    assert delays == [2]


def test_async_openenv_get_instance_does_not_retry_untyped_429():
    class _Untyped429Instances(_AsyncFakeInstances):
        async def create_instance(
            self,
            environment_name,
            environment_version,
            instance_group_id,
            *,
            cls=None,
        ):
            self.create_routes.append(
                (environment_name, environment_version, instance_group_id)
            )
            raise _http_response_error(429, headers={"Retry-After": "0"})

    async def run():
        instances = _Untyped429Instances()
        client, _groups, _instances = _make_async_openenv_client(instances=instances)
        async with client:
            with pytest.raises(HttpResponseError):
                async with client.get_instance():
                    pass
        assert len(instances.create_routes) == 1

    asyncio.run(run())


def test_async_openenv_get_instance_releases_failed_instance():
    async def run():
        instances = _AsyncFakeInstances(fail_on=0)
        client, _groups, _instances = _make_async_openenv_client(
            max_active_instances=1, instances=instances
        )
        async with client:
            with pytest.raises(RLEError):
                async with client.get_instance():
                    pass
            assert instances.released == ["inst-0"]

    asyncio.run(run())


def test_async_openenv_get_instance_polls_pending_202_without_recreating():
    async def run():
        # A 202 already contains a pending instance. create_instance is not idempotent, so it must be
        # issued exactly once and the pending instance polled by id -- re-POSTing would lease and leak
        # an extra instance for every pending response.
        instances = _AsyncFakeInstances202(running_after=2)
        client, _groups, _instances = _make_async_openenv_client(
            max_active_instances=1, instances=instances
        )
        async with client:
            async with client.get_instance() as instance:
                assert instance.id == "inst-0"
                assert instance.instance.status == RLEInstanceStatus.RUNNING
        assert instances.create_count == 1
        assert instances.get_count >= 1
        assert instances.released == ["inst-0"]

    asyncio.run(run())


def test_async_openenv_get_instance_releases_pending_instance_when_cancelled(
    monkeypatch,
):
    async def cancel(_delay):
        raise asyncio.CancelledError

    monkeypatch.setattr(
        "azure.ai.projects.aio.operations._patch_rle_async.asyncio.sleep", cancel
    )

    async def run():
        instances = _AsyncFakeInstances202(running_after=2)
        client, _groups, _instances = _make_async_openenv_client(instances=instances)
        async with client:
            with pytest.raises(asyncio.CancelledError):
                async with client.get_instance():
                    pass
        assert instances.create_count == 1
        assert instances.released == ["inst-0"]

    asyncio.run(run())


def test_async_openenv_get_instance_waits_for_runtime_health():
    async def run():
        instances = _AsyncFakeInstances(health_statuses=["starting", "healthy"])
        client, _groups, _instances = _make_async_openenv_client(instances=instances)
        async with client:
            async with client.get_instance() as instance:
                assert instance.id == "inst-0"
        assert [call[0] for call in instances.calls] == ["health", "health"]

    asyncio.run(run())


def test_async_openenv_get_instance_releases_instance_when_health_times_out():
    class _UnhealthyInstances(_AsyncFakeInstances):
        async def health(
            self, environment_name, environment_version, instance_group_id, instance_id
        ):
            return {"status": "starting"}

    async def run():
        instances = _UnhealthyInstances()
        client, _groups, _instances = _make_async_openenv_client(
            instances=instances,
            instance_acquire_timeout=0.01,
        )
        async with client:
            with pytest.raises(
                RLEInstanceAcquireTimeoutError, match="runtime was not healthy"
            ):
                async with client.get_instance():
                    pass
        assert instances.released == ["inst-0"]

    asyncio.run(run())


def test_async_openenv_ensure_group_maps_quota_exceeded():
    async def run():
        groups = _AsyncFakeInstanceGroups(
            create_status=403, create_error_code="QuotaExceeded"
        )
        client, _groups, _instances = _make_async_openenv_client(
            max_active_instances=1, groups=groups
        )
        with pytest.raises(RLEQuotaExceededError):
            await client._ensure_group()

    asyncio.run(run())


@pytest.mark.parametrize(
    "error_code", ["AuthorizationFailed", "preview_feature_required"]
)
def test_async_openenv_ensure_group_preserves_non_quota_403(error_code):
    async def run():
        groups = _AsyncFakeInstanceGroups(
            create_status=403, create_error_code=error_code
        )
        client, _groups, _instances = _make_async_openenv_client(
            max_active_instances=1, groups=groups
        )
        with pytest.raises(HttpResponseError):
            await client._ensure_group()

    asyncio.run(run())


def test_async_openenv_ensure_group_deletes_incomplete_group():
    class _IncompleteGroupResponse(_AsyncFakeInstanceGroups):
        async def create_instance_group(self, environment_name, environment_version, body):
            group = await super().create_instance_group(
                environment_name, environment_version, body
            )
            group.environment_version = None
            return group

    async def run():
        groups = _IncompleteGroupResponse()
        client, _groups, _instances = _make_async_openenv_client(groups=groups)

        with pytest.raises(RLEError, match="environment name and version"):
            await client._ensure_group()

        assert groups.deleted == ["grp-1"]

    asyncio.run(run())


def test_async_create_environment_builds_request():
    async def run():
        ops = AsyncRLEOperations(object(), object(), object(), object())
        environments = _AsyncFakeEnvironments()
        ops._environments = environments
        result = await ops.create_environment(
            "wordle", "registry.azurecr.io/wordle:v1", version_bump="Major"
        )
        assert result.name == "wordle"
        body = environments.calls[0][1]
        assert body.name == "wordle"
        assert body.acr_image_path == "registry.azurecr.io/wordle:v1"
        assert body.version_bump == "Major"

    asyncio.run(run())
