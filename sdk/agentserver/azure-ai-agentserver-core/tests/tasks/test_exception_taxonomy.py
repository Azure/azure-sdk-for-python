# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""RED-first tests for  resilient exception taxonomy.

These tests encode,,,,,,
and SC-017. They intentionally import new public names inside tests so
collection can succeed before the implementation lands.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any, ForwardRef, get_args, get_origin, get_type_hints

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task


PUBLIC_EXCEPTION_NAMES = (
    "TaskFailed",
    "TaskCancelled",
    "TaskDeferred",
    "TaskConflictError",
    "LastInputIdPreconditionFailed",
    "SteeringQueueFull",
    "InputTooLarge",
)


def _resilient_module() -> Any:
    return importlib.import_module("azure.ai.agentserver.core.tasks")


def _exceptions_module() -> Any:
    return importlib.import_module("azure.ai.agentserver.core.tasks._exceptions")


def _public_symbol(name: str) -> Any:
    return getattr(_resilient_module(), name)


def _assert_public_import_raises_import_error(name: str) -> None:
    with pytest.raises(ImportError):
        exec(f"from azure.ai.agentserver.core.tasks import {name}", {})


def _signature_parameter_names(obj: Any) -> list[str]:
    return list(inspect.signature(obj).parameters)


def _assert_no_instance_fields(exc: BaseException) -> None:
    assert _instance_field_names(exc) == set()


def _assert_instance_fields(exc: BaseException, expected: set[str]) -> None:
    assert _instance_field_names(exc) == expected


def _instance_field_names(exc: BaseException) -> set[str]:
    fields: set[str] = set()
    try:
        fields.update(vars(exc))
    except TypeError:
        pass

    for cls in type(exc).__mro__:
        slots = getattr(cls, "__slots__", ())
        if isinstance(slots, str):
            slot_names = slots
        else:
            slot_names = slots
        for name in slot_names:
            if name in {"__dict__", "__weakref__"}:
                continue
            if hasattr(exc, name):
                fields.add(name)
    return fields


async def _setup_manager(tmp_path: Path) -> tuple[Any, Any]:
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    provider = LocalFileTaskProvider(Path(str(tmp_path)))
    config = type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()
    manager = TaskManager(config=config, provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    return manager, mgr_mod


async def _teardown_manager(manager: Any, mgr_mod: Any) -> None:
    await manager.shutdown()
    mgr_mod._manager = None


class TestPublicExceptionExports:
    """,, SC-017 — exception public-surface."""

    def test_7_public_exceptions_exported(self):
        all_names = set(getattr(_resilient_module(), "__all__", ()))
        for name in PUBLIC_EXCEPTION_NAMES:
            assert name in all_names
            assert hasattr(_resilient_module(), name)

    def test_TaskNotFound_not_in_public_all(self):
        assert "TaskNotFound" not in getattr(_resilient_module(), "__all__", ())

    def test_TaskNotFound_import_raises_ImportError(self):
        _assert_public_import_raises_import_error("TaskNotFound")

    def test_TaskPreconditionFailed_not_in_public_all(self):
        assert "TaskPreconditionFailed" not in getattr(_resilient_module(), "__all__", ())

    def test_TaskPreconditionFailed_import_raises_ImportError(self):
        _assert_public_import_raises_import_error("TaskPreconditionFailed")

    def test_OutputTooLarge_not_in_public_all(self):
        assert "OutputTooLarge" not in getattr(_resilient_module(), "__all__", ())

    def test_OutputTooLarge_import_raises_ImportError(self):
        _assert_public_import_raises_import_error("OutputTooLarge")

    def test_TaskCancelledError_does_not_exist(self):
        _assert_public_import_raises_import_error("TaskCancelledError")


class TestExceptionShapes:
    """— bare-vs-fielded rule. No exception carries task_id."""

    def test_TaskCancelled_bare_no_fields(self):
        TaskCancelled = _public_symbol("TaskCancelled")
        assert _signature_parameter_names(TaskCancelled) == []
        exc = TaskCancelled()
        assert not hasattr(exc, "task_id")
        _assert_no_instance_fields(exc)

    def test_TaskDeferred_bare_no_fields(self):
        TaskDeferred = _public_symbol("TaskDeferred")
        assert _signature_parameter_names(TaskDeferred) == []
        exc = TaskDeferred()
        assert not hasattr(exc, "task_id")
        _assert_no_instance_fields(exc)

    def test_SteeringQueueFull_bare_no_fields(self):
        SteeringQueueFull = _public_symbol("SteeringQueueFull")
        assert _signature_parameter_names(SteeringQueueFull) == []
        exc = SteeringQueueFull()
        assert not hasattr(exc, "task_id")
        _assert_no_instance_fields(exc)

    def test_InputTooLarge_bare_no_fields(self):
        InputTooLarge = _public_symbol("InputTooLarge")
        assert _signature_parameter_names(InputTooLarge) == []
        exc = InputTooLarge()
        assert not hasattr(exc, "task_id")
        _assert_no_instance_fields(exc)

    def test_TaskFailed_carries_error_only(self):
        TaskFailed = _public_symbol("TaskFailed")
        assert _signature_parameter_names(TaskFailed) == ["error"]
        error = {"type": "X", "message": "y", "traceback": "z"}
        exc = TaskFailed(error=error)
        assert exc.error == error
        assert not hasattr(exc, "task_id")
        _assert_instance_fields(exc, {"error"})

    def test_TaskConflictError_carries_current_status_only(self):
        TaskConflictError = _public_symbol("TaskConflictError")
        assert _signature_parameter_names(TaskConflictError) == ["current_status"]
        exc = TaskConflictError(current_status="in_progress")
        assert exc.current_status == "in_progress"
        assert not hasattr(exc, "task_id")
        _assert_instance_fields(exc, {"current_status"})

    def test_LastInputIdPreconditionFailed_carries_actual_only(self):
        LastInputIdPreconditionFailed = _public_symbol("LastInputIdPreconditionFailed")
        assert _signature_parameter_names(LastInputIdPreconditionFailed) == ["actual_last_input_id"]
        exc = LastInputIdPreconditionFailed(actual_last_input_id="input-2")
        assert exc.actual_last_input_id == "input-2"
        assert not hasattr(exc, "expected_last_input_id")
        assert not hasattr(exc, "task_id")
        _assert_instance_fields(exc, {"actual_last_input_id"})

    def test_no_public_exception_has_task_id_attribute(self):
        factories = {
            "TaskFailed": lambda cls: cls(error={"type": "X", "message": "y", "traceback": "z"}),
            "TaskCancelled": lambda cls: cls(),
            "TaskDeferred": lambda cls: cls(),
            "TaskConflictError": lambda cls: cls(current_status="in_progress"),
            "LastInputIdPreconditionFailed": lambda cls: cls(actual_last_input_id="input-2"),
            "SteeringQueueFull": lambda cls: cls(),
            "InputTooLarge": lambda cls: cls(),
        }
        for name in PUBLIC_EXCEPTION_NAMES:
            exc = factories[name](_public_symbol(name))
            assert not hasattr(exc, "task_id"), f"{name} must not carry task_id"


class TestTypedDicts:
    """— TaskErrorDict + TaskExhaustedRetriesErrorDict TypedDicts."""

    def test_TaskErrorDict_in_public_surface(self):
        from azure.ai.agentserver.core.tasks import TaskErrorDict

        assert TaskErrorDict.__name__ == "TaskErrorDict"

    def test_TaskErrorDict_field_shape(self):
        TaskErrorDict = _public_symbol("TaskErrorDict")
        hints = get_type_hints(TaskErrorDict)
        assert set(hints) == {"type", "message", "traceback"}
        assert hints["type"] is str
        assert hints["message"] is str
        assert hints["traceback"] is str

    def test_TaskExhaustedRetriesErrorDict_in_public_surface(self):
        from azure.ai.agentserver.core.tasks import TaskExhaustedRetriesErrorDict

        assert TaskExhaustedRetriesErrorDict.__name__ == "TaskExhaustedRetriesErrorDict"

    def test_TaskExhaustedRetriesErrorDict_field_shape(self):
        TaskExhaustedRetriesErrorDict = _public_symbol("TaskExhaustedRetriesErrorDict")
        hints = get_type_hints(TaskExhaustedRetriesErrorDict)
        assert set(hints) == {
            "type",
            "attempts",
            "last_error",
            "last_error_type",
            "traceback",
        }
        assert get_args(hints["type"]) == ("exhausted_retries",)
        assert hints["attempts"] is int
        assert hints["last_error"] is str
        assert hints["last_error_type"] is str
        assert hints["traceback"] is str

    def test_TaskFailed_error_typed_as_union(self):
        TaskFailed = _public_symbol("TaskFailed")
        TaskErrorDict = _public_symbol("TaskErrorDict")
        TaskExhaustedRetriesErrorDict = _public_symbol("TaskExhaustedRetriesErrorDict")
        hints = get_type_hints(TaskFailed, globalns=vars(_exceptions_module()))
        assert "error" in hints
        assert set(get_args(hints["error"])) == {
            TaskErrorDict,
            TaskExhaustedRetriesErrorDict,
        }


class TestJSONValueAlias:
    """— JSONValue recursive type alias exported."""

    def test_JSONValue_in_public_surface(self):
        from azure.ai.agentserver.core.tasks import JSONValue

        assert JSONValue is not None

    def test_JSONValue_is_recursive_type(self):
        JSONValue = _public_symbol("JSONValue")
        args = set(get_args(JSONValue))
        assert {str, int, float, bool, type(None)}.issubset(args)

        list_branch = next(
            (arg for arg in args if get_origin(arg) is list or getattr(arg, "__origin__", None) is list), None
        )
        dict_branch = next(
            (arg for arg in args if get_origin(arg) is dict or getattr(arg, "__origin__", None) is dict), None
        )
        assert list_branch is not None
        assert dict_branch is not None

        list_args = get_args(list_branch)
        dict_args = get_args(dict_branch)
        assert len(list_args) == 1
        assert dict_args[0] is str
        assert _is_json_value_recursive_arg(list_args[0], JSONValue)
        assert _is_json_value_recursive_arg(dict_args[1], JSONValue)


def _is_json_value_recursive_arg(arg: Any, alias: Any) -> bool:
    if arg == alias or arg == "JSONValue":
        return True
    if isinstance(arg, ForwardRef):
        return arg.__forward_arg__ == "JSONValue"
    return False


class TestTaskFailedCauseInvariant:
    """— TaskFailed.__cause__ is None for handler-raised exceptions."""

    @pytest.mark.asyncio
    async def test_TaskFailed_cause_is_none(self, tmp_path: Path):
        class CustomException(Exception):
            pass

        @task(name="cause-invariant", title="cause-invariant")
        async def raises_custom(ctx: TaskContext[str]) -> str:
            raise CustomException("boom")

        TaskFailed = _public_symbol("TaskFailed")
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            with pytest.raises(TaskFailed) as exc_info:
                await raises_custom.run(task_id="cause-invariant", input="x")
            assert exc_info.value.__cause__ is None
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestTaskDeferredSemantics:
    """Verify TaskDeferred has NO 'cancellation' semantic baked in."""

    def test_TaskDeferred_is_not_subclass_of_TaskCancelled(self):
        TaskCancelled = _public_symbol("TaskCancelled")
        TaskDeferred = _public_symbol("TaskDeferred")
        assert issubclass(TaskCancelled, Exception)
        assert issubclass(TaskDeferred, Exception)
        assert not issubclass(TaskDeferred, TaskCancelled)
        assert not issubclass(TaskCancelled, TaskDeferred)

    def test_TaskDeferred_in_public_surface(self):
        from azure.ai.agentserver.core.tasks import TaskDeferred

        assert TaskDeferred.__name__ == "TaskDeferred"
