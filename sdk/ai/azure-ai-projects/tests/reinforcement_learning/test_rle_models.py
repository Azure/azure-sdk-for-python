# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import asyncio
import json
from types import SimpleNamespace

import pytest

from azure.ai.projects.aio.operations._patch_rle_async import (
    AsyncOpenEnvClient,
    AsyncOpenEnvInstance,
)
from azure.ai.projects.models import (
    RLEnvironmentState,
    RLESandboxStatus,
    RLEStepResult,
)
from azure.ai.projects.operations import RLEOperations
from azure.ai.projects.operations._patch_rle import (
    coerce_action,
    OpenEnvClient,
    OpenEnvInstance,
    RLEError,
    _RLE_FEATURE,
)


class ActionWithModelDump:
    def model_dump(self):
        return {"code": "model_dump"}


class ActionWithToDict:
    def to_dict(self):
        return {"code": "to_dict"}


class _FakeSandbox:
    def __init__(self, sandbox_id, status, base_url=None, error=None):
        self.id = sandbox_id
        self.status = status
        self.base_url = base_url
        self.error = error


class _FakeResponse:
    """Minimal stand-in for an HTTP response returned by the (fake) pipeline."""

    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = {} if payload is None else payload

    def json(self):
        return self._payload


def _handle_dataplane(recorder, request):
    """Record a data-plane request and return a canned response for its route."""
    method = request.method
    url = request.url
    route = "/" + url.rstrip("/").rsplit("/", 1)[-1]
    body = None
    raw = getattr(request, "content", None)
    if raw:
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        body = json.loads(raw)
    recorder.calls.append((route.lstrip("/"), method, url, body))
    if route in ("/reset", "/step"):
        payload = dict(RLEStepResult(observation={"ok": True}))
    elif route == "/state":
        payload = dict(RLEnvironmentState(episode_id="e", step_count=1))
    else:
        payload = {"status": "ok"}
    return _FakeResponse(200, payload)


class _FakeSyncPipeline:
    def __init__(self, recorder):
        self._recorder = recorder

    def run(self, request, **kwargs):  # noqa: D401
        return SimpleNamespace(http_response=_handle_dataplane(self._recorder, request))


class _FakeSyncPipelineClient:
    def __init__(self, recorder):
        self._pipeline = _FakeSyncPipeline(recorder)


class _FakeAsyncPipeline:
    def __init__(self, recorder):
        self._recorder = recorder

    async def run(self, request, **kwargs):
        return SimpleNamespace(http_response=_handle_dataplane(self._recorder, request))


class _FakeAsyncPipelineClient:
    def __init__(self, recorder):
        self._pipeline = _FakeAsyncPipeline(recorder)


class _FakeEnvironments:
    def __init__(self, environment_id="env-1"):
        self._eid = environment_id
        self.calls = []

    def get_environment(self, name, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.calls.append(("get_environment", name))
        return SimpleNamespace(environment_id=self._eid)

    def get_environment_version(self, name, version, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.calls.append(("get_environment_version", name, version))
        return SimpleNamespace(environment_id=self._eid)


class _AsyncFakeEnvironments:
    def __init__(self, environment_id="env-1"):
        self._eid = environment_id
        self.calls = []

    async def get_environment(self, name, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.calls.append(("get_environment", name))
        return SimpleNamespace(environment_id=self._eid)

    async def get_environment_version(self, name, version, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.calls.append(("get_environment_version", name, version))
        return SimpleNamespace(environment_id=self._eid)


def test_rle_public_symbols_are_available():
    assert OpenEnvClient
    assert AsyncOpenEnvClient
    assert OpenEnvInstance
    assert AsyncOpenEnvInstance
    assert RLEError


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
    assert getattr(models, "RLESandbox")


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


class _PoolFakeSandboxes:
    """Sandbox op-group fake that leases distinct running sandboxes for pool tests.

    Each ``lease`` returns a fresh, already-``Running`` sandbox with its own id and data-plane URL,
    so an :class:`OpenEnvClient` can reserve ``num_instances`` distinct instances without polling.
    """

    def __init__(self, *, fail_on=None):
        self._next = 0
        self._fail_on = fail_on
        self.released = []
        self.calls = []
        self._client = _FakeSyncPipelineClient(self)

    def lease(self, environment_id, body, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        index = self._next
        self._next += 1
        if self._fail_on is not None and index == self._fail_on:
            return _FakeSandbox(f"sbx-{index}", RLESandboxStatus.FAILED, error="boom")
        return _FakeSandbox(f"sbx-{index}", RLESandboxStatus.RUNNING, base_url=f"https://dataplane/{index}")

    def get_sandbox(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        return _FakeSandbox(sandbox_id, RLESandboxStatus.RUNNING)

    def release(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.released.append(sandbox_id)


def _make_openenv_client(num_instances=1, *, fail_on=None, environments=None):
    sandboxes = _PoolFakeSandboxes(fail_on=fail_on)
    client = OpenEnvClient(
        environments=environments or _FakeEnvironments(),
        sandboxes=sandboxes,
        name="env-1",
        num_instances=num_instances,
        poll_interval_s=0,
    )
    return client, sandboxes


def test_openenv_client_reserves_quota_in_advance():
    client, sandboxes = _make_openenv_client(num_instances=3)
    with client:
        # Quota reserved up front: three distinct instances leased before any get_instance().
        assert len(client.instances) == 3
        ids = {inst.id for inst in client.instances}
        assert ids == {"sbx-0", "sbx-1", "sbx-2"}
        assert sandboxes.released == []
    # Closing the client releases every reserved instance.
    assert sorted(sandboxes.released) == ["sbx-0", "sbx-1", "sbx-2"]


def test_openenv_client_reserve_fails_fast_and_releases_partial():
    # Second lease fails; both the failed sandbox and the first (partially-leased) instance must be
    # released, no queueing. The failed sandbox is released first (at the point of failure), then the
    # already-pooled instance during reserve() cleanup.
    client, sandboxes = _make_openenv_client(num_instances=3, fail_on=1)
    with pytest.raises(RLEError):
        client._reserve()
    assert sandboxes.released == ["sbx-1", "sbx-0"]
    assert client.instances == []


def test_openenv_get_instance_is_bounded_by_quota():
    client, _sandboxes = _make_openenv_client(num_instances=1)
    with client:
        instance = client.get_instance()
        assert isinstance(instance, OpenEnvInstance)
        # Quota is exhausted; v1 fails fast instead of queueing.
        with pytest.raises(RLEError):
            client.get_instance()
        # Returning it to the pool frees the quota for reuse (shared across episodes).
        instance.checkin()
        again = client.get_instance()
        assert again is instance


def test_openenv_instance_context_returns_to_pool():
    client, _sandboxes = _make_openenv_client(num_instances=1)
    with client:
        with client.get_instance() as instance:
            first_id = instance.id
        # Exiting the instance context returned it to the pool for the next episode.
        with client.get_instance() as reused:
            assert reused.id == first_id


def test_openenv_instance_runtime_uses_dataplane_uri():
    client, sandboxes = _make_openenv_client(num_instances=1)
    with client:
        with client.get_instance() as instance:
            assert instance.dataplane_uri == "https://dataplane/0"
            assert instance.environment_id == "env-1"

            assert isinstance(instance.reset(seed=42), RLEStepResult)
            assert isinstance(instance.step({"code": "print(1)"}), RLEStepResult)
            assert isinstance(instance.state(), RLEnvironmentState)

    # Runtime calls target the instance's data-plane URI (unprefixed OpenEnv routes), not the
    # control plane.
    routes = [call[0] for call in sandboxes.calls]
    assert routes == ["reset", "step", "state"]
    assert all(call[2].startswith("https://dataplane/0/") for call in sandboxes.calls)
    reset_call = sandboxes.calls[0]
    assert reset_call[1] == "POST"
    assert reset_call[3].get("seed") == 42


def test_openenv_get_instance_requires_reserve_first():
    client, _sandboxes = _make_openenv_client(num_instances=1)
    with pytest.raises(RLEError):
        client.get_instance()


def test_reserve_resolves_environment_by_name():
    environments = _FakeEnvironments("env-42")
    client, _sandboxes = _make_openenv_client(num_instances=1, environments=environments)
    with client:
        # Resolution is deferred until context entry / reserve().
        assert client.environment_id == "env-42"
    assert environments.calls[0] == ("get_environment", "env-1")


def test_reserve_resolves_environment_version():
    environments = _FakeEnvironments("env-9")
    sandboxes = _PoolFakeSandboxes()
    client = OpenEnvClient(
        environments=environments,
        sandboxes=sandboxes,
        name="wordle",
        version="1",
        poll_interval_s=0,
    )
    with client:
        assert client.environment_id == "env-9"
    assert environments.calls[0] == ("get_environment_version", "wordle", "1")


def test_get_openenv_client_defers_resolution():
    ops = RLEOperations(object(), object(), object(), object())
    ops._environments = _FakeEnvironments("env-77")
    client = ops.get_openenv_client(name="wordle-env", version="1")
    assert isinstance(client, OpenEnvClient)
    # The factory does no network I/O; the environment is resolved on context entry, not here.
    assert client.environment_id is None
    assert client.num_instances == 1


def test_get_openenv_client_validates_arguments():
    ops = RLEOperations(object(), object(), object(), object())
    with pytest.raises(ValueError):
        ops.get_openenv_client(name="")


class _AsyncPoolFakeSandboxes:
    def __init__(self, *, fail_on=None):
        self._next = 0
        self._fail_on = fail_on
        self.released = []
        self.calls = []
        self._client = _FakeAsyncPipelineClient(self)

    async def lease(self, environment_id, body, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        index = self._next
        self._next += 1
        if self._fail_on is not None and index == self._fail_on:
            return _FakeSandbox(f"sbx-{index}", RLESandboxStatus.FAILED, error="boom")
        return _FakeSandbox(f"sbx-{index}", RLESandboxStatus.RUNNING, base_url=f"https://dataplane/{index}")

    async def get_sandbox(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        return _FakeSandbox(sandbox_id, RLESandboxStatus.RUNNING)

    async def release(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.released.append(sandbox_id)


def _make_async_openenv_client(num_instances=1, *, fail_on=None, environments=None):
    sandboxes = _AsyncPoolFakeSandboxes(fail_on=fail_on)
    client = AsyncOpenEnvClient(
        environments=environments or _AsyncFakeEnvironments(),
        sandboxes=sandboxes,
        name="env-1",
        num_instances=num_instances,
        poll_interval_s=0,
    )
    return client, sandboxes


def test_async_openenv_client_reserves_and_runs():
    async def run():
        client, sandboxes = _make_async_openenv_client(num_instances=2)
        async with client:
            assert len(client.instances) == 2
            # get_instance() is a synchronous accessor now (symmetric with the sync surface).
            async with client.get_instance() as instance:
                assert isinstance(instance, AsyncOpenEnvInstance)
                assert instance.dataplane_uri in {"https://dataplane/0", "https://dataplane/1"}
                assert isinstance(await instance.reset(seed=7), RLEStepResult)
                assert isinstance(await instance.step({"code": "x"}), RLEStepResult)
                assert isinstance(await instance.state(), RLEnvironmentState)
        assert sorted(sandboxes.released) == ["sbx-0", "sbx-1"]
        # Runtime calls went to the data-plane URI.
        routes = [call[0] for call in sandboxes.calls]
        assert routes == ["reset", "step", "state"]
        assert all(call[2].startswith("https://dataplane/") for call in sandboxes.calls)

    asyncio.run(run())


def test_async_openenv_get_instance_is_bounded_by_quota():
    async def run():
        client, _sandboxes = _make_async_openenv_client(num_instances=1)
        async with client:
            instance = client.get_instance()
            with pytest.raises(RLEError):
                client.get_instance()
            await instance.checkin()
            again = client.get_instance()
            assert again is instance

    asyncio.run(run())


def test_async_openenv_reserve_fails_fast_and_releases_partial():
    async def run():
        client, sandboxes = _make_async_openenv_client(num_instances=3, fail_on=1)
        with pytest.raises(RLEError):
            await client._reserve()
        assert sandboxes.released == ["sbx-1", "sbx-0"]
        assert client.instances == []

    asyncio.run(run())
