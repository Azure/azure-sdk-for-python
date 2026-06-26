# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import pytest

from azure.ai.projects.aio.operations._patch_rle_async import AsyncRLEEnvironment
from azure.ai.projects.operations._patch_rle import (
    coerce_action,
    RLEEnvState,
    RLEEnvironment,
    RLEError,
    RLEStepResult,
)


class ActionWithModelDump:
    def model_dump(self):
        return {"code": "model_dump"}


class ActionWithToDict:
    def to_dict(self):
        return {"code": "to_dict"}


def test_rle_public_symbols_are_available():
    assert RLEEnvironment
    assert AsyncRLEEnvironment
    assert RLEError
    assert RLEEnvState


def test_rle_symbols_exported_from_public_namespace():
    import azure.ai.projects as projects
    import azure.ai.projects.aio as aio_projects

    assert getattr(projects, "RLEEnvironment")
    assert getattr(aio_projects, "AsyncRLEEnvironment")
    assert getattr(projects, "RLEError")
    assert getattr(projects, "RLEEnvState")
    assert getattr(projects, "RLEStepResult")


def test_step_result_binds_gym_fields_and_derives_done():
    result = RLEStepResult.from_wire(
        {"observation": {"x": 1}, "reward": 1.0, "terminated": True, "truncated": False, "info": {"k": "v"}}
    )

    assert result.terminated
    assert not result.truncated
    assert result.done
    assert result.info == {"k": "v"}
    assert result.reward == 1.0


def test_step_result_legacy_done_maps_to_terminated_and_metadata():
    result = RLEStepResult.from_wire({"observation": {}, "done": True, "metadata": {"m": 1}})

    assert result.terminated
    assert not result.truncated
    assert result.done
    assert result.metadata == {"m": 1}
    assert result.info == {"m": 1}


def test_step_result_done_is_read_only():
    result = RLEStepResult.from_wire({"terminated": True})

    with pytest.raises(AttributeError):
        setattr(result, "done", False)


def test_env_state_defaults_bad_step_count_to_zero():
    state = RLEEnvState.from_wire({"episode_id": "episode", "step_count": "bad"})

    assert state.episode_id == "episode"
    assert state.step_count == 0


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