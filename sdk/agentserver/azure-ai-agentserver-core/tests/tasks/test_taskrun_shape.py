# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" TaskRun public shape coverage."""

from __future__ import annotations

import inspect
from typing import get_type_hints

from azure.ai.agentserver.core.tasks import TaskMetadata, TaskRun


class TestTaskRunPublicShape:
    """— TaskRun exposes exactly: task_id, input_id, metadata, result, cancel, __await__."""

    def test_taskrun_attributes(self) -> None:
        slots = set(getattr(TaskRun, "__slots__", ()))
        assert "task_id" in slots
        assert "input_id" in slots
        assert not isinstance(inspect.getattr_static(TaskRun, "task_id"), property)
        assert not isinstance(inspect.getattr_static(TaskRun, "input_id"), property)

    def test_taskrun_metadata_property(self) -> None:
        metadata_descriptor = inspect.getattr_static(TaskRun, "metadata")
        assert isinstance(metadata_descriptor, property)
        assert metadata_descriptor.fget is not None
        assert get_type_hints(metadata_descriptor.fget).get("return") is TaskMetadata

    def test_taskrun_result_is_async_method(self) -> None:
        assert inspect.iscoroutinefunction(TaskRun.result)

    def test_taskrun_cancel_is_async_method(self) -> None:
        assert inspect.iscoroutinefunction(TaskRun.cancel)

    def test_taskrun_await_dunder(self) -> None:
        assert callable(TaskRun.__await__)
        assert "result" in inspect.getsource(TaskRun.__await__)

    def test_taskrun_is_queued_is_bool_property(self) -> None:
        descriptor = inspect.getattr_static(TaskRun, "is_queued")
        assert isinstance(descriptor, property)
        assert descriptor.fget is not None
        assert get_type_hints(descriptor.fget).get("return") is bool


class TestTaskRunRemovedMembers:
    """— TaskRun does NOT expose status, delete, refresh, lease_expiry_count."""

    def test_taskrun_no_status(self) -> None:
        assert not hasattr(TaskRun, "status")

    def test_taskrun_no_delete(self) -> None:
        assert not hasattr(TaskRun, "delete")

    def test_taskrun_no_refresh(self) -> None:
        assert not hasattr(TaskRun, "refresh")

    def test_taskrun_no_lease_expiry_count(self) -> None:
        assert not hasattr(TaskRun, "lease_expiry_count")


class TestTaskRunInternalSlotsAbsent:
    """— internal slots not present."""

    def test_taskrun_no_internal_provider_slot(self) -> None:
        assert "_provider" not in getattr(TaskRun, "__slots__", ())

    def test_taskrun_no_terminate_event_slot(self) -> None:
        assert "_terminate_event" not in getattr(TaskRun, "__slots__", ())

    def test_taskrun_no_terminate_reason_ref_slot(self) -> None:
        assert "_terminate_reason_ref" not in getattr(TaskRun, "__slots__", ())

    def test_taskrun_no_status_slot(self) -> None:
        assert "_status" not in getattr(TaskRun, "__slots__", ())

    def test_taskrun_no_lease_expiry_count_slot(self) -> None:
        assert "_lease_expiry_count" not in getattr(TaskRun, "__slots__", ())
