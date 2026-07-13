# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import asyncio

import pytest

from azure.core.exceptions import HttpResponseError

from azure.ai.projects.aio.operations._patch_rle_async import AsyncRLEEnvironment
from azure.ai.projects.models import (
    GetMetadataResponse,
    HealthResponse,
    RLEnvironmentState,
    RLSandboxStatus,
    RLStepResult,
    SchemaResponse,
)
from azure.ai.projects.operations import RLEnvironmentsOperations
from azure.ai.projects.operations._patch_rle import (
    coerce_action,
    RLEEnvironment,
    RLEError,
)


class ActionWithModelDump:
    def model_dump(self):
        return {"code": "model_dump"}


class ActionWithToDict:
    def to_dict(self):
        return {"code": "to_dict"}


class _FakeSandbox:
    def __init__(self, sandbox_id, status, url=None, error=None):
        self.sandbox_id = sandbox_id
        self.status = status
        self.url = url
        self.error = error


class _FakeSandboxes:
    """Returns the given sequence of statuses across lease + get_sandbox polls."""

    def __init__(self, statuses):
        self._statuses = list(statuses)
        self.released = []

    def lease(self, environment_id, body):
        return _FakeSandbox("sbx-1", self._statuses.pop(0), error="boom")

    def get_sandbox(self, environment_id, sandbox_id):
        return _FakeSandbox(sandbox_id, self._statuses.pop(0), error="boom")

    def release(self, environment_id, sandbox_id):
        self.released.append(sandbox_id)


class _FakeRuntime:
    def __init__(self):
        self.calls = []
        self.health_calls = []
        self.health_error = None

    def reset(self, environment_id, sandbox_id, **kwargs):
        self.calls.append(("reset", environment_id, sandbox_id, kwargs))
        return RLStepResult(observation={"ok": True})

    def step(self, environment_id, sandbox_id, *, action):
        self.calls.append(("step", environment_id, sandbox_id, action))
        return RLStepResult(observation={"stepped": action})

    def state(self, environment_id, sandbox_id):
        return RLEnvironmentState(episode_id="e", step_count=1)

    def health(self, environment_id, sandbox_id):
        self.health_calls.append((environment_id, sandbox_id))
        if self.health_error is not None:
            raise self.health_error
        return HealthResponse({"status": "ok"})

    def get_metadata(self, environment_id, sandbox_id):
        return GetMetadataResponse({"k": "v"})

    def schema(self, environment_id, sandbox_id):
        return SchemaResponse({})


def _make_env(statuses):
    sandboxes = _FakeSandboxes(statuses)
    runtime = _FakeRuntime()
    env = RLEEnvironment("env-1", sandboxes=sandboxes, runtime=runtime, poll_interval_s=0)
    return env, sandboxes, runtime


def test_rle_public_symbols_are_available():
    assert RLEEnvironment
    assert AsyncRLEEnvironment
    assert RLEError


def test_rle_symbols_exported_from_public_namespace():
    import azure.ai.projects as projects
    import azure.ai.projects.aio as aio_projects
    import azure.ai.projects.models as models

    assert getattr(projects, "RLEEnvironment")
    assert getattr(aio_projects, "AsyncRLEEnvironment")
    assert getattr(projects, "RLEError")
    assert getattr(models, "RLStepResult")
    assert getattr(models, "RLEnvironmentState")


def test_create_runtime_returns_bound_helper():
    ops = RLEnvironmentsOperations(object(), object(), object(), object())
    assert hasattr(ops, "create_runtime")
    env = ops.create_runtime("env-9")
    assert isinstance(env, RLEEnvironment)
    assert env.environment_id == "env-9"


def test_environment_leases_polls_runs_and_releases():
    env, sandboxes, runtime = _make_env([RLSandboxStatus.CREATING, RLSandboxStatus.RUNNING])

    with env:
        assert env.sandbox_id == "sbx-1"

        reset_result = env.reset(seed=7)
        assert isinstance(reset_result, RLStepResult)
        assert runtime.calls[0] == ("reset", "env-1", "sbx-1", {"seed": 7, "episode_id": None})

        step_result = env.step({"code": "print(1)"})
        assert isinstance(step_result, RLStepResult)
        assert runtime.calls[1] == ("step", "env-1", "sbx-1", {"code": "print(1)"})

        state = env.state()
        assert isinstance(state, RLEnvironmentState)
        assert isinstance(env.health(), HealthResponse)
        assert isinstance(env.metadata(), GetMetadataResponse)
        assert isinstance(env.schema(), SchemaResponse)

        # reset, step, state, metadata, schema each health-gate (5), plus the explicit health() op (1).
        assert len(runtime.health_calls) == 6
        assert all(call == ("env-1", "sbx-1") for call in runtime.health_calls)

    assert sandboxes.released == ["sbx-1"]
    assert env.sandbox_id is None


def test_runtime_op_is_health_gated_before_running():
    env, _sandboxes, runtime = _make_env([RLSandboxStatus.RUNNING])

    env.reset(seed=1)

    assert runtime.health_calls == [("env-1", "sbx-1")]


def test_runtime_op_propagates_unhealthy_sandbox():
    env, _sandboxes, runtime = _make_env([RLSandboxStatus.RUNNING])
    runtime.health_error = HttpResponseError(message="sandbox is unhealthy")

    with pytest.raises(HttpResponseError):
        env.step({"code": "print(1)"})

    assert runtime.calls == []


def test_environment_raises_when_sandbox_fails():
    env, _sandboxes, _runtime = _make_env([RLSandboxStatus.FAILED])

    with pytest.raises(RLEError):
        env._ensure_leased()


def test_environment_raises_on_ready_timeout():
    sandboxes = _FakeSandboxes([RLSandboxStatus.CREATING, RLSandboxStatus.CREATING])
    env = RLEEnvironment("env-1", sandboxes=sandboxes, runtime=_FakeRuntime(), poll_interval_s=0, create_timeout_s=0)

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

    async def lease(self, environment_id, body):
        return _FakeSandbox("sbx-1", self._statuses.pop(0))

    async def get_sandbox(self, environment_id, sandbox_id):
        return _FakeSandbox(sandbox_id, self._statuses.pop(0))

    async def release(self, environment_id, sandbox_id):
        self.released.append(sandbox_id)


class _AsyncFakeRuntime:
    def __init__(self):
        self.health_calls = []

    async def reset(self, environment_id, sandbox_id, **kwargs):
        return RLStepResult(observation={"ok": True})

    async def step(self, environment_id, sandbox_id, *, action):
        return RLStepResult(observation={"stepped": action})

    async def state(self, environment_id, sandbox_id):
        return RLEnvironmentState(episode_id="e", step_count=1)

    async def health(self, environment_id, sandbox_id):
        self.health_calls.append((environment_id, sandbox_id))
        return HealthResponse({"status": "ok"})


def test_async_environment_leases_runs_and_releases():
    async def run():
        sandboxes = _AsyncFakeSandboxes([RLSandboxStatus.CREATING, RLSandboxStatus.RUNNING])
        runtime = _AsyncFakeRuntime()
        env = AsyncRLEEnvironment("env-1", sandboxes=sandboxes, runtime=runtime, poll_interval_s=0)
        async with env:
            assert env.sandbox_id == "sbx-1"
            assert isinstance(await env.reset(seed=1), RLStepResult)
            assert isinstance(await env.step({"code": "x"}), RLStepResult)
            assert isinstance(await env.state(), RLEnvironmentState)
        # reset, step, state each health-gate before running.
        assert runtime.health_calls == [("env-1", "sbx-1")] * 3
        assert sandboxes.released == ["sbx-1"]

    asyncio.run(run())
