# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import asyncio

import pytest

from azure.core.exceptions import HttpResponseError

from azure.ai.projects.aio.operations._patch_rle_async import (
    AsyncOpenEnvClient,
    AsyncOpenEnvInstance,
)
from azure.ai.projects.models import (
    RLEnvironmentState,
    RLESandboxStatus,
    RLEStepResult,
)
from azure.ai.projects.models import CreateRLEnvironmentRequest, CreateRLESandboxRequest
from azure.ai.projects.operations import RLEOperations
from azure.ai.projects.operations._operations import RLEnvironmentsOperations as _GenEnvOps
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
        self.sandbox_id = sandbox_id
        self.status = status
        self.base_url = base_url
        self.error = error


def test_rle_public_symbols_are_available():
    assert OpenEnvClient
    assert AsyncOpenEnvClient
    assert OpenEnvInstance
    assert AsyncOpenEnvInstance
    assert RLEError


def test_rle_symbols_exported_from_public_namespace():
    import azure.ai.projects as projects
    import azure.ai.projects.aio as aio_projects
    import azure.ai.projects.models as models

    assert getattr(projects, "OpenEnvClient")
    assert getattr(projects, "OpenEnvInstance")
    assert getattr(aio_projects, "AsyncOpenEnvClient")
    assert getattr(aio_projects, "AsyncOpenEnvInstance")
    assert getattr(projects, "RLEError")
    assert getattr(models, "RLEStepResult")
    assert getattr(models, "RLEnvironmentState")
    assert getattr(models, "RLESandbox")


def _capture_env_ops(monkeypatch):
    """Patch the generated environment base methods to record forwarded calls."""
    calls = {}

    def rec(name):
        def _inner(self, *args, **kwargs):
            calls[name] = {"args": args, "kwargs": kwargs}
            return name

        return _inner

    for m in (
        "create_environment",
        "list_environments",
        "get_environment",
        "get_environment_version",
        "delete_environment_version",
        "list_rl_environment_versions",
    ):
        monkeypatch.setattr(_GenEnvOps, m, rec(m))
    return calls


def test_create_environment_from_keyword_fields_defaults_feature(monkeypatch):
    calls = _capture_env_ops(monkeypatch)
    ops = RLEOperations(object(), object(), object(), object())

    assert ops.create_environment(acr_image_path="acr.io/img:1", name="pong") == "create_environment"
    body = calls["create_environment"]["args"][0]
    assert isinstance(body, CreateRLEnvironmentRequest)
    assert body.acr_image_path == "acr.io/img:1"
    assert body.name == "pong"
    assert calls["create_environment"]["kwargs"]["foundry_features"] == _RLE_FEATURE


def test_create_environment_from_body_passes_through(monkeypatch):
    calls = _capture_env_ops(monkeypatch)
    ops = RLEOperations(object(), object(), object(), object())
    req = CreateRLEnvironmentRequest(acr_image_path="acr.io/img:2")

    ops.create_environment(req)
    assert calls["create_environment"]["args"][0] is req
    assert calls["create_environment"]["kwargs"]["foundry_features"] == _RLE_FEATURE


def test_create_environment_rejects_missing_and_ambiguous_args(monkeypatch):
    _capture_env_ops(monkeypatch)
    ops = RLEOperations(object(), object(), object(), object())

    with pytest.raises(TypeError):
        ops.create_environment()

    with pytest.raises(TypeError):
        ops.create_environment(CreateRLEnvironmentRequest(acr_image_path="x"), acr_image_path="y")


def test_environment_read_and_delete_default_feature(monkeypatch):
    calls = _capture_env_ops(monkeypatch)
    ops = RLEOperations(object(), object(), object(), object())

    ops.list_environments(name="pong", top=5)
    assert calls["list_environments"]["kwargs"]["foundry_features"] == _RLE_FEATURE
    assert calls["list_environments"]["kwargs"]["name"] == "pong"
    assert calls["list_environments"]["kwargs"]["top"] == 5

    ops.get_environment("pong")
    assert calls["get_environment"]["args"] == ("pong",)
    assert calls["get_environment"]["kwargs"]["foundry_features"] == _RLE_FEATURE

    ops.get_environment_version("pong", "3")
    assert calls["get_environment_version"]["args"] == ("pong", "3")
    assert calls["get_environment_version"]["kwargs"]["foundry_features"] == _RLE_FEATURE

    ops.delete_environment_version("pong", "3")
    assert calls["delete_environment_version"]["args"] == ("pong", "3")
    assert calls["delete_environment_version"]["kwargs"]["foundry_features"] == _RLE_FEATURE

    ops.list_rl_environment_versions("pong")
    assert calls["list_rl_environment_versions"]["args"] == ("pong",)
    assert calls["list_rl_environment_versions"]["kwargs"]["foundry_features"] == _RLE_FEATURE


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

    def reset(self, environment_id, sandbox_id, body, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.calls.append(("reset", environment_id, sandbox_id, {"seed": body.seed, "episode_id": body.episode_id}))
        return RLEStepResult(observation={"ok": True})

    def step(self, environment_id, sandbox_id, body, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.calls.append(("step", environment_id, sandbox_id, body.action))
        return RLEStepResult(observation={"stepped": body.action})

    def state(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        return RLEnvironmentState(episode_id="e", step_count=1)

    def health(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        return {"status": "ok"}


def _make_openenv_client(num_instances=1, *, fail_on=None):
    sandboxes = _PoolFakeSandboxes(fail_on=fail_on)
    client = OpenEnvClient(
        environment_id="env-1",
        sandboxes=sandboxes,
        num_instances=num_instances,
        lease_request=CreateRLESandboxRequest(),
        poll_interval_s=0,
    )
    return client, sandboxes


def test_openenv_client_reserves_quota_in_advance():
    client, sandboxes = _make_openenv_client(num_instances=3)
    with client:
        # Quota reserved up front: three distinct instances leased before any get_instance().
        assert len(client.instances) == 3
        ids = {inst.instance_id for inst in client.instances}
        assert ids == {"sbx-0", "sbx-1", "sbx-2"}
        assert sandboxes.released == []
    # Closing the client releases every reserved instance.
    assert sorted(sandboxes.released) == ["sbx-0", "sbx-1", "sbx-2"]


def test_openenv_client_reserve_fails_fast_and_releases_partial():
    # Second lease fails; the first (partially-leased) instance must be released, no queueing.
    client, sandboxes = _make_openenv_client(num_instances=3, fail_on=1)
    with pytest.raises(RLEError):
        client.reserve()
    assert sandboxes.released == ["sbx-0"]
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
            first_id = instance.instance_id
        # Exiting the instance context returned it to the pool for the next episode.
        with client.get_instance() as reused:
            assert reused.instance_id == first_id


def test_openenv_instance_exposes_dataplane_uri_and_forwards_ops():
    client, sandboxes = _make_openenv_client(num_instances=1)
    with client:
        with client.get_instance() as instance:
            assert instance.dataplane_uri == "https://dataplane/0"
            assert instance.environment_id == "env-1"

            assert isinstance(instance.reset(seed=42), RLEStepResult)
            assert sandboxes.calls[0] == ("reset", "env-1", "sbx-0", {"seed": 42, "episode_id": None})

            assert isinstance(instance.step({"code": "print(1)"}), RLEStepResult)
            assert sandboxes.calls[1] == ("step", "env-1", "sbx-0", {"code": "print(1)"})

            assert isinstance(instance.state(), RLEnvironmentState)


def test_openenv_get_instance_requires_reserve_first():
    client, _sandboxes = _make_openenv_client(num_instances=1)
    with pytest.raises(RLEError):
        client.get_instance()


def test_get_openenv_client_resolves_environment_by_name(monkeypatch):
    captured = {}

    class _Env:
        environment_id = "env-42"

    def fake_get_environment(self, name, **kwargs):
        captured["get_environment"] = name
        return _Env()

    def fake_get_environment_version(self, name, version, **kwargs):
        captured["get_environment_version"] = (name, version)
        return _Env()

    monkeypatch.setattr(RLEOperations, "get_environment", fake_get_environment)
    monkeypatch.setattr(RLEOperations, "get_environment_version", fake_get_environment_version)

    ops = RLEOperations(object(), object(), object(), object())

    client = ops.get_openenv_client(name="wordle-env", num_instances=5)
    assert isinstance(client, OpenEnvClient)
    assert client.environment_id == "env-42"
    assert client.num_instances == 5
    assert captured["get_environment"] == "wordle-env"

    ops.get_openenv_client(name="wordle-env", version="1")
    assert captured["get_environment_version"] == ("wordle-env", "1")


def test_get_openenv_client_validates_arguments():
    ops = RLEOperations(object(), object(), object(), object())
    with pytest.raises(ValueError):
        ops.get_openenv_client(name="")
    with pytest.raises(ValueError):
        ops.get_openenv_client(name="env", num_instances=0)


class _AsyncPoolFakeSandboxes:
    def __init__(self, *, fail_on=None):
        self._next = 0
        self._fail_on = fail_on
        self.released = []
        self.calls = []

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

    async def reset(self, environment_id, sandbox_id, body, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.calls.append(("reset", sandbox_id, body.seed))
        return RLEStepResult(observation={"ok": True})

    async def step(self, environment_id, sandbox_id, body, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        self.calls.append(("step", sandbox_id, body.action))
        return RLEStepResult(observation={"stepped": body.action})

    async def state(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        return RLEnvironmentState(episode_id="e", step_count=1)

    async def health(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is _RLE_FEATURE
        return {"status": "ok"}


def _make_async_openenv_client(num_instances=1, *, fail_on=None):
    sandboxes = _AsyncPoolFakeSandboxes(fail_on=fail_on)
    client = AsyncOpenEnvClient(
        environment_id="env-1",
        sandboxes=sandboxes,
        num_instances=num_instances,
        lease_request=CreateRLESandboxRequest(),
        poll_interval_s=0,
    )
    return client, sandboxes


def test_async_openenv_client_reserves_and_runs():
    async def run():
        client, sandboxes = _make_async_openenv_client(num_instances=2)
        async with client:
            assert len(client.instances) == 2
            async with await client.get_instance() as instance:
                assert isinstance(instance, AsyncOpenEnvInstance)
                assert instance.dataplane_uri in {"https://dataplane/0", "https://dataplane/1"}
                assert isinstance(await instance.reset(seed=7), RLEStepResult)
                assert isinstance(await instance.step({"code": "x"}), RLEStepResult)
                assert isinstance(await instance.state(), RLEnvironmentState)
        assert sorted(sandboxes.released) == ["sbx-0", "sbx-1"]

    asyncio.run(run())


def test_async_openenv_get_instance_is_bounded_by_quota():
    async def run():
        client, _sandboxes = _make_async_openenv_client(num_instances=1)
        async with client:
            instance = await client.get_instance()
            with pytest.raises(RLEError):
                await client.get_instance()
            await instance.checkin()
            again = await client.get_instance()
            assert again is instance

    asyncio.run(run())


def test_async_openenv_reserve_fails_fast_and_releases_partial():
    async def run():
        client, sandboxes = _make_async_openenv_client(num_instances=3, fail_on=1)
        with pytest.raises(RLEError):
            await client.reserve()
        assert sandboxes.released == ["sbx-0"]
        assert client.instances == []

    asyncio.run(run())
