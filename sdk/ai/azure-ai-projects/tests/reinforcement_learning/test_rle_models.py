# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import asyncio

import pytest

from azure.core.exceptions import HttpResponseError

from azure.ai.projects.aio.operations._patch_rle_async import AsyncRLESandboxSession
from azure.ai.projects.models import (
    RLEnvironmentState,
    RLESandboxStatus,
    RLEStepResult,
)
from azure.ai.projects.models import CreateRLEnvironmentRequest
from azure.ai.projects.operations import RLEOperations
from azure.ai.projects.operations._operations import RLEnvironmentsOperations as _GenEnvOps
from azure.ai.projects.operations._patch_rle import (
    coerce_action,
    RLESandboxSession,
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


class _FakeSandboxes:
    """Single sandbox op-group fake covering lifecycle + runtime ops for the new RLE shape.

    Every generated RLE op requires the ``foundry_features`` opt-in keyword, so each method
    asserts it was supplied.
    """

    def __init__(self, statuses):
        self._statuses = list(statuses)
        self.released = []
        self.calls = []
        self.health_calls = []
        self.health_error = None

    def lease(self, environment_id, body, *, foundry_features):
        assert foundry_features is not None
        return _FakeSandbox("sbx-1", self._statuses.pop(0), error="boom")

    def get_sandbox(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        return _FakeSandbox(sandbox_id, self._statuses.pop(0), error="boom")

    def release(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        self.released.append(sandbox_id)

    def reset(self, environment_id, sandbox_id, body, *, foundry_features):
        assert foundry_features is not None
        self.calls.append(("reset", environment_id, sandbox_id, {"seed": body.seed, "episode_id": body.episode_id}))
        return RLEStepResult(observation={"ok": True})

    def step(self, environment_id, sandbox_id, body, *, foundry_features):
        assert foundry_features is not None
        self.calls.append(("step", environment_id, sandbox_id, body.action))
        return RLEStepResult(observation={"stepped": body.action})

    def state(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        return RLEnvironmentState(episode_id="e", step_count=1)

    def health(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        self.health_calls.append((environment_id, sandbox_id))
        if self.health_error is not None:
            raise self.health_error
        return {"status": "ok"}

    def get_metadata(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        return {"k": "v"}

    def schema(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        return {}


def _make_env(statuses):
    sandboxes = _FakeSandboxes(statuses)
    env = RLESandboxSession("env-1", sandboxes=sandboxes, poll_interval_s=0)
    return env, sandboxes


def test_rle_public_symbols_are_available():
    assert RLESandboxSession
    assert AsyncRLESandboxSession
    assert RLEError


def test_rle_symbols_exported_from_public_namespace():
    import azure.ai.projects as projects
    import azure.ai.projects.aio as aio_projects
    import azure.ai.projects.models as models

    assert getattr(projects, "RLESandboxSession")
    assert getattr(aio_projects, "AsyncRLESandboxSession")
    assert getattr(projects, "RLEError")
    assert getattr(models, "RLEStepResult")
    assert getattr(models, "RLEnvironmentState")
    assert getattr(models, "RLESandbox")


def test_create_session_returns_bound_helper():
    ops = RLEOperations(object(), object(), object(), object())
    assert hasattr(ops, "create_session")
    env = ops.create_session("env-9")
    assert isinstance(env, RLESandboxSession)
    assert env.environment_id == "env-9"


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


def test_environment_leases_polls_runs_and_releases():
    env, sandboxes = _make_env([RLESandboxStatus.CREATING, RLESandboxStatus.RUNNING])

    with env:
        assert env.sandbox_id == "sbx-1"

        reset_result = env.reset(seed=7)
        assert isinstance(reset_result, RLEStepResult)
        assert sandboxes.calls[0] == ("reset", "env-1", "sbx-1", {"seed": 7, "episode_id": None})

        step_result = env.step({"code": "print(1)"})
        assert isinstance(step_result, RLEStepResult)
        assert sandboxes.calls[1] == ("step", "env-1", "sbx-1", {"code": "print(1)"})

        state = env.state()
        assert isinstance(state, RLEnvironmentState)
        assert env.health() == {"status": "ok"}
        assert env.metadata() == {"k": "v"}
        assert env.schema() == {}

        # reset, step, state, metadata, schema each health-gate (5), plus the explicit health() op (1).
        assert len(sandboxes.health_calls) == 6
        assert all(call == ("env-1", "sbx-1") for call in sandboxes.health_calls)

    assert sandboxes.released == ["sbx-1"]
    assert env.sandbox_id is None


def test_runtime_op_is_health_gated_before_running():
    env, sandboxes = _make_env([RLESandboxStatus.RUNNING])

    env.reset(seed=1)

    assert sandboxes.health_calls == [("env-1", "sbx-1")]


def test_runtime_op_propagates_unhealthy_sandbox():
    env, sandboxes = _make_env([RLESandboxStatus.RUNNING])
    sandboxes.health_error = HttpResponseError(message="sandbox is unhealthy")

    with pytest.raises(HttpResponseError):
        env.step({"code": "print(1)"})

    assert sandboxes.calls == []


def test_environment_raises_when_sandbox_fails():
    env, _sandboxes = _make_env([RLESandboxStatus.FAILED])

    with pytest.raises(RLEError):
        env._ensure_leased()


def test_environment_raises_on_ready_timeout():
    sandboxes = _FakeSandboxes([RLESandboxStatus.CREATING, RLESandboxStatus.CREATING])
    env = RLESandboxSession("env-1", sandboxes=sandboxes, poll_interval_s=0, create_timeout_s=0)

    with pytest.raises(RLEError):
        env._ensure_leased()


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


class _AsyncFakeSandboxes:
    def __init__(self, statuses):
        self._statuses = list(statuses)
        self.released = []
        self.health_calls = []

    async def lease(self, environment_id, body, *, foundry_features):
        assert foundry_features is not None
        return _FakeSandbox("sbx-1", self._statuses.pop(0))

    async def get_sandbox(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        return _FakeSandbox(sandbox_id, self._statuses.pop(0))

    async def release(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        self.released.append(sandbox_id)

    async def reset(self, environment_id, sandbox_id, body, *, foundry_features):
        assert foundry_features is not None
        return RLEStepResult(observation={"ok": True})

    async def step(self, environment_id, sandbox_id, body, *, foundry_features):
        assert foundry_features is not None
        return RLEStepResult(observation={"stepped": body.action})

    async def state(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        return RLEnvironmentState(episode_id="e", step_count=1)

    async def health(self, environment_id, sandbox_id, *, foundry_features):
        assert foundry_features is not None
        self.health_calls.append((environment_id, sandbox_id))
        return {"status": "ok"}


def test_async_environment_leases_runs_and_releases():
    async def run():
        sandboxes = _AsyncFakeSandboxes([RLESandboxStatus.CREATING, RLESandboxStatus.RUNNING])
        env = AsyncRLESandboxSession("env-1", sandboxes=sandboxes, poll_interval_s=0)
        async with env:
            assert env.sandbox_id == "sbx-1"
            assert isinstance(await env.reset(seed=1), RLEStepResult)
            assert isinstance(await env.step({"code": "x"}), RLEStepResult)
            assert isinstance(await env.state(), RLEnvironmentState)
        # reset, step, state each health-gate before running.
        assert sandboxes.health_calls == [("env-1", "sbx-1")] * 3
        assert sandboxes.released == ["sbx-1"]

    asyncio.run(run())
