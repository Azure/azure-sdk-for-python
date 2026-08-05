# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import asyncio
from types import SimpleNamespace

import pytest

from azure.core.exceptions import HttpResponseError

from azure.ai.projects.aio.operations._patch_rle_async import (
    AsyncOpenEnvClient,
    AsyncOpenEnvInstance,
)
from azure.ai.projects.models import (
    RLEInstance,
    RLEInstanceGroup,
    RLEInstanceStatus,
    RLEnvironmentState,
    RLEStepResult,
)
from azure.ai.projects.operations import RLEOperations
from azure.ai.projects.operations._patch_rle import (
    coerce_action,
    OpenEnvClient,
    OpenEnvInstance,
    RLEError,
    RLEQuotaExceededError,
    RLEAtCapacityError,
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


def _pipeline_response(status_code=201, headers=None):
    return SimpleNamespace(http_response=SimpleNamespace(status_code=status_code, headers=headers or {}))


def _error_response(status_code, headers=None):
    # ``HttpResponseError.__init__`` reads ``reason``/``status_code``/``headers`` off the response.
    return SimpleNamespace(status_code=status_code, headers=headers or {}, reason=None)


def _record_runtime(calls, op, instance_id, body=None):
    """Record a delegated runtime call and return a canned result."""
    calls.append((op, instance_id, dict(body) if body is not None else None))
    if op in ("reset", "step"):
        return RLEStepResult(observation={"ok": True})
    if op == "state":
        return RLEnvironmentState(episode_id="e", step_count=1)
    return {"status": "ok"}


class _FakeEnvironments:
    def __init__(self, version="7"):
        self._version = version
        self.calls = []

    def get_environment(self, name):
        self.calls.append(("get_environment", name))
        return SimpleNamespace(name=name, version=self._version)

    def get_environment_version(self, name, version):
        self.calls.append(("get_environment_version", name, version))
        return SimpleNamespace(name=name, version=version)


class _AsyncFakeEnvironments:
    def __init__(self, version="7"):
        self._version = version
        self.calls = []

    async def get_environment(self, name):
        self.calls.append(("get_environment", name))
        return SimpleNamespace(name=name, version=self._version)

    async def get_environment_version(self, name, version):
        self.calls.append(("get_environment_version", name, version))
        return SimpleNamespace(name=name, version=version)


def test_rle_public_symbols_are_available():
    assert OpenEnvClient
    assert AsyncOpenEnvClient
    assert OpenEnvInstance
    assert AsyncOpenEnvInstance
    assert RLEError
    assert RLEQuotaExceededError
    assert RLEAtCapacityError


def test_rle_symbols_exported_from_public_namespace():
    import azure.ai.projects as projects
    import azure.ai.projects.operations as operations
    import azure.ai.projects.aio.operations as aio_operations
    import azure.ai.projects.models as models

    # Customers interact with RLE only through ``project_client.rle.get_openenv_client(...)``; the
    # OpenEnv client/instance types are reachable via the operations namespaces but are intentionally
    # not top-level package exports. Only ``RLEError`` is surfaced at the package root (for excepts).
    assert getattr(projects, "RLEError")
    assert getattr(operations, "OpenEnvClient")
    assert getattr(operations, "OpenEnvInstance")
    assert getattr(aio_operations, "AsyncOpenEnvClient")
    assert getattr(aio_operations, "AsyncOpenEnvInstance")
    assert getattr(models, "RLEStepResult")
    assert getattr(models, "RLEnvironmentState")
    assert getattr(models, "RLEInstance")
    assert getattr(models, "RLEInstanceGroup")


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

    def __init__(self, *, group_id="grp-1", create_status=None):
        self.group_id = group_id
        self._create_status = create_status
        self.created = []
        self.deleted = []

    def create_instance_group(self, body):
        self.created.append(body)
        if self._create_status is not None:
            raise HttpResponseError(response=_error_response(self._create_status))
        return SimpleNamespace(instance_group_id=self.group_id)

    def delete_instance_group(self, instance_group_id):
        self.deleted.append(instance_group_id)


class _FakeInstances:
    """Instance op-group fake that leases distinct running instances on demand.

    Each ``create_instance`` returns a fresh, already-``Running`` instance with its own id, so
    :meth:`OpenEnvClient.get_instance` can lease instances without polling. When ``fail_on`` matches
    the creation index the instance comes back ``Failed``. ``create_status`` simulates a non-2xx
    create (e.g. ``429``) by raising before any instance is returned.
    """

    def __init__(self, *, fail_on=None, create_status=None):
        self._next = 0
        self._fail_on = fail_on
        self._create_status = create_status
        self.released = []
        self.calls = []

    def create_instance(self, instance_group_id, *, cls=None):
        index = self._next
        self._next += 1
        if self._create_status is not None:
            raise HttpResponseError(response=_error_response(self._create_status, {"Retry-After": "0"}))
        if self._fail_on is not None and index == self._fail_on:
            instance = _FakeInstance(f"inst-{index}", RLEInstanceStatus.FAILED, error="boom")
        else:
            instance = _FakeInstance(f"inst-{index}", RLEInstanceStatus.RUNNING)
        if cls is not None:
            return cls(_pipeline_response(201), instance, {})
        return instance

    def get_instance(self, instance_group_id, instance_id):
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    def release_instance(self, instance_group_id, instance_id):
        self.released.append(instance_id)
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    def reset(self, instance_id, body):
        return _record_runtime(self.calls, "reset", instance_id, body)

    def step(self, instance_id, body):
        return _record_runtime(self.calls, "step", instance_id, body)

    def state(self, instance_id):
        return _record_runtime(self.calls, "state", instance_id)


def _make_openenv_client(num_instances=1, *, fail_on=None, groups=None, instances=None, environments=None):
    groups = groups or _FakeInstanceGroups()
    instances = instances or _FakeInstances(fail_on=fail_on)
    client = OpenEnvClient(
        environments=environments or _FakeEnvironments(),
        instance_groups=groups,
        instances=instances,
        name="env-1",
        num_instances=num_instances,
        poll_interval_s=0,
    )
    return client, groups, instances


def test_openenv_client_creates_group_on_enter():
    client, groups, instances = _make_openenv_client(num_instances=3)
    with client:
        # Entering creates one instance group that reserves concurrency on the service. No instances
        # are leased yet -- the service owns the pool and hands them out via get_instance().
        assert client.instance_group_id == "grp-1"
        assert len(groups.created) == 1
        assert groups.created[0].instance_count == 3
        assert client.instances == []
        assert instances.released == []
    # Closing tears down the group.
    assert groups.deleted == ["grp-1"]


def test_openenv_get_instance_leases_on_demand():
    client, _groups, instances = _make_openenv_client(num_instances=2)
    with client:
        first = client.get_instance()
        second = client.get_instance()
        assert isinstance(first, OpenEnvInstance)
        assert {first.id, second.id} == {"inst-0", "inst-1"}
        assert len(client.instances) == 2
    # Closing the client releases every leased instance and tears down the group.
    assert sorted(instances.released) == ["inst-0", "inst-1"]


def test_openenv_get_instance_maps_at_capacity():
    # The service enforces the reservation: once the group is full, create_instance returns 429.
    instances = _FakeInstances(create_status=429)
    client, _groups, _instances = _make_openenv_client(num_instances=1, instances=instances)
    with client:
        with pytest.raises(RLEAtCapacityError):
            client.get_instance()


def test_openenv_get_instance_releases_failed_instance():
    # An instance that never reaches Running is released so it does not leak quota, and the failure
    # surfaces as RLEError.
    instances = _FakeInstances(fail_on=0)
    client, _groups, _instances = _make_openenv_client(num_instances=1, instances=instances)
    with client:
        with pytest.raises(RLEError):
            client.get_instance()
        assert instances.released == ["inst-0"]


def test_openenv_ensure_group_maps_quota_exceeded():
    groups = _FakeInstanceGroups(create_status=403)
    client, _groups, _instances = _make_openenv_client(num_instances=1, groups=groups)
    with pytest.raises(RLEQuotaExceededError):
        client._ensure_group()


def test_openenv_instance_context_releases_on_exit():
    client, _groups, instances = _make_openenv_client(num_instances=1)
    with client:
        with client.get_instance() as instance:
            first_id = instance.id
        # Exiting the instance context released it immediately (no reuse in v1).
        assert instances.released == [first_id]
        assert client.instances == []


def test_openenv_instance_runtime_uses_flat_instance_id():
    client, _groups, instances = _make_openenv_client(num_instances=1)
    with client:
        with client.get_instance() as instance:
            assert instance.instance_group_id == "grp-1"
            assert instance.id == "inst-0"

            assert isinstance(instance.reset(seed=42), RLEStepResult)
            assert isinstance(instance.step({"code": "print(1)"}), RLEStepResult)
            assert isinstance(instance.state(), RLEnvironmentState)

    # Runtime calls delegate to the generated instance operations, addressed by the flat instance id.
    routes = [call[0] for call in instances.calls]
    assert routes == ["reset", "step", "state"]
    assert all(call[1] == "inst-0" for call in instances.calls)
    reset_call = instances.calls[0]
    assert reset_call[2].get("seed") == 42


def test_openenv_get_instance_requires_enter_first():
    client, _groups, _instances = _make_openenv_client(num_instances=1)
    with pytest.raises(RLEError):
        client.get_instance()


def test_ensure_group_resolves_environment_by_name():
    environments = _FakeEnvironments(version="42")
    client, groups, _instances = _make_openenv_client(num_instances=1, environments=environments)
    with client:
        # Resolution is deferred until context entry.
        assert client.instance_group_id == "grp-1"
    assert environments.calls[0] == ("get_environment", "env-1")
    # The create request pins the resolved environment name and version.
    body = groups.created[0]
    assert body.environment_name == "env-1"
    assert body.environment_version == "42"
    assert body.instance_count == 1


def test_ensure_group_resolves_environment_version():
    environments = _FakeEnvironments()
    groups = _FakeInstanceGroups()
    instances = _FakeInstances()
    client = OpenEnvClient(
        environments=environments,
        instance_groups=groups,
        instances=instances,
        name="wordle",
        version="1",
        poll_interval_s=0,
    )
    with client:
        assert client.instance_group_id == "grp-1"
    assert environments.calls[0] == ("get_environment_version", "wordle", "1")
    assert groups.created[0].environment_version == "1"


def test_get_openenv_client_defers_resolution():
    ops = RLEOperations(object(), object(), object(), object())
    ops._environments = _FakeEnvironments()
    ops._instance_groups = _FakeInstanceGroups()
    ops._instances = _FakeInstances()
    client = ops.get_openenv_client(name="wordle-env", version="1")
    assert isinstance(client, OpenEnvClient)
    # The factory does no network I/O; the environment is resolved on context entry, not here.
    assert client.instance_group_id is None
    assert client.num_instances == 1


def test_get_openenv_client_validates_arguments():
    ops = RLEOperations(object(), object(), object(), object())
    with pytest.raises(ValueError):
        ops.get_openenv_client(name="")


class _AsyncFakeInstanceGroups:
    def __init__(self, *, group_id="grp-1", create_status=None):
        self.group_id = group_id
        self._create_status = create_status
        self.created = []
        self.deleted = []

    async def create_instance_group(self, body):
        self.created.append(body)
        if self._create_status is not None:
            raise HttpResponseError(response=_error_response(self._create_status))
        return SimpleNamespace(instance_group_id=self.group_id)

    async def delete_instance_group(self, instance_group_id):
        self.deleted.append(instance_group_id)


class _AsyncFakeInstances:
    def __init__(self, *, fail_on=None, create_status=None):
        self._next = 0
        self._fail_on = fail_on
        self._create_status = create_status
        self.released = []
        self.calls = []

    async def create_instance(self, instance_group_id, *, cls=None):
        index = self._next
        self._next += 1
        if self._create_status is not None:
            raise HttpResponseError(response=_error_response(self._create_status, {"Retry-After": "0"}))
        if self._fail_on is not None and index == self._fail_on:
            instance = _FakeInstance(f"inst-{index}", RLEInstanceStatus.FAILED, error="boom")
        else:
            instance = _FakeInstance(f"inst-{index}", RLEInstanceStatus.RUNNING)
        if cls is not None:
            return cls(_pipeline_response(201), instance, {})
        return instance

    async def get_instance(self, instance_group_id, instance_id):
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    async def release_instance(self, instance_group_id, instance_id):
        self.released.append(instance_id)
        return _FakeInstance(instance_id, RLEInstanceStatus.RUNNING)

    async def reset(self, instance_id, body):
        return _record_runtime(self.calls, "reset", instance_id, body)

    async def step(self, instance_id, body):
        return _record_runtime(self.calls, "step", instance_id, body)

    async def state(self, instance_id):
        return _record_runtime(self.calls, "state", instance_id)


def _make_async_openenv_client(num_instances=1, *, fail_on=None, groups=None, instances=None, environments=None):
    groups = groups or _AsyncFakeInstanceGroups()
    instances = instances or _AsyncFakeInstances(fail_on=fail_on)
    client = AsyncOpenEnvClient(
        environments=environments or _AsyncFakeEnvironments(),
        instance_groups=groups,
        instances=instances,
        name="env-1",
        num_instances=num_instances,
        poll_interval_s=0,
    )
    return client, groups, instances


def test_async_openenv_client_creates_group_and_runs():
    async def run():
        client, groups, instances = _make_async_openenv_client(num_instances=2)
        async with client:
            assert client.instance_group_id == "grp-1"
            # Entering only creates the group; instances are leased on demand.
            assert client.instances == []
            async with await client.get_instance() as instance:
                assert isinstance(instance, AsyncOpenEnvInstance)
                assert instance.id.startswith("inst-")
                assert isinstance(await instance.reset(seed=7), RLEStepResult)
                assert isinstance(await instance.step({"code": "x"}), RLEStepResult)
                assert isinstance(await instance.state(), RLEnvironmentState)
        assert instances.released == ["inst-0"]
        assert groups.deleted == ["grp-1"]
        # Runtime calls delegate to the generated instance operations by flat instance id.
        routes = [call[0] for call in instances.calls]
        assert routes == ["reset", "step", "state"]
        assert all(call[1].startswith("inst-") for call in instances.calls)

    asyncio.run(run())


def test_async_openenv_get_instance_leases_on_demand():
    async def run():
        client, _groups, instances = _make_async_openenv_client(num_instances=2)
        async with client:
            first = await client.get_instance()
            second = await client.get_instance()
            assert {first.id, second.id} == {"inst-0", "inst-1"}
            assert len(client.instances) == 2
            # Releasing frees the instance immediately; v1 does not reuse instances.
            await first.release()
            assert instances.released == [first.id]
        assert sorted(instances.released) == ["inst-0", "inst-1"]

    asyncio.run(run())


def test_async_openenv_get_instance_maps_at_capacity():
    async def run():
        instances = _AsyncFakeInstances(create_status=429)
        client, _groups, _instances = _make_async_openenv_client(num_instances=1, instances=instances)
        async with client:
            with pytest.raises(RLEAtCapacityError):
                await client.get_instance()

    asyncio.run(run())


def test_async_openenv_get_instance_releases_failed_instance():
    async def run():
        instances = _AsyncFakeInstances(fail_on=0)
        client, _groups, _instances = _make_async_openenv_client(num_instances=1, instances=instances)
        async with client:
            with pytest.raises(RLEError):
                await client.get_instance()
            assert instances.released == ["inst-0"]

    asyncio.run(run())


def test_async_openenv_ensure_group_maps_quota_exceeded():
    async def run():
        groups = _AsyncFakeInstanceGroups(create_status=403)
        client, _groups, _instances = _make_async_openenv_client(num_instances=1, groups=groups)
        with pytest.raises(RLEQuotaExceededError):
            await client._ensure_group()

    asyncio.run(run())
