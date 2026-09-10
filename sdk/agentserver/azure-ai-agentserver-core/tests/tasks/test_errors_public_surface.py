# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Area D — Developer-facing error rename + prefix dispatch
(, SC-9b, SC-11).

Verifies:

- ``OutputTooLarge`` is exported from
  ``azure.ai.agentserver.core.tasks``.
- ``AttachmentTooLarge`` and ``AttachmentLimitExceeded`` are NOT
  public  — importing them by their old names
  raises ``ImportError`` and they do not appear in ``__all__``
  (SC-11).
- The framework's prefix-dispatch wrapper translates the internal
  ``_AttachmentTooLarge`` raised against a known attachment-key
  prefix into the right developer-facing exception:

  - ``_input`` → ``InputTooLarge``
  - ``_steering_input_<seq>`` → ``InputTooLarge`` (/ SC-9b)
  - ``_output`` → ``OutputTooLarge``

Reference: docs/task-and-streaming-spec.md §23.7, §39, §59 C-ATT-4.
"""

from __future__ import annotations

import asyncio
import importlib
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task


# --------------------------------------------------------------------- #
#  — OutputTooLarge is a public exception
# --------------------------------------------------------------------- #


def test_output_too_large_is_public() -> None:
    """/ SC-9 — ``OutputTooLarge`` MUST be importable from
    the public ``azure.ai.agentserver.core.tasks`` surface and MUST
    inherit ``ValueError``.
    """
    from azure.ai.agentserver.core.tasks._exceptions import OutputTooLarge

    assert issubclass(OutputTooLarge, ValueError), "OutputTooLarge MUST be a ValueError subclass per "
    # Must accept the documented constructor shape.
    exc = OutputTooLarge(task_id="t", size_bytes=3_000_000, max_bytes=2_097_152)
    #: exception.task_id removed
    assert exc.size_bytes == 3_000_000
    assert exc.max_bytes == 2_097_152


# --------------------------------------------------------------------- #
#  /  / SC-11 — attachment-vocabulary errors are internal
# --------------------------------------------------------------------- #


def test_attachment_too_large_not_public() -> None:
    """/ SC-11 — ``AttachmentTooLarge`` MUST be absent from
    the public surface; ``from resilient import AttachmentTooLarge``
    raises ``ImportError``.
    """
    mod = importlib.import_module("azure.ai.agentserver.core.tasks")
    assert "AttachmentTooLarge" not in (mod.__all__ or ()), (
        "AttachmentTooLarge must NOT appear in resilient.__all__ "
        ". Attachments are a framework concept that "
        "developers never name."
    )
    with pytest.raises(ImportError):
        # Force a clean ImportError on the explicit name.
        exec("from azure.ai.agentserver.core.tasks import AttachmentTooLarge", {})


def test_attachment_limit_exceeded_not_public() -> None:
    """/ SC-11 — same rule for ``AttachmentLimitExceeded``."""
    mod = importlib.import_module("azure.ai.agentserver.core.tasks")
    assert "AttachmentLimitExceeded" not in (mod.__all__ or ()), (
        "AttachmentLimitExceeded must NOT appear in resilient.__all__ " "."
    )
    with pytest.raises(ImportError):
        exec("from azure.ai.agentserver.core.tasks import AttachmentLimitExceeded", {})


# --------------------------------------------------------------------- #
#  — framework re-raises by attachment-key prefix
# --------------------------------------------------------------------- #


def _internal_attachment_too_large_cls():
    """Locate the internal ``_AttachmentTooLarge`` exception class.

      says the rename target is
    ``_AttachmentTooLarge`` (leading underscore). Implementation
    detail; tests reach into ``_exceptions`` for the rename.
    """
    mod = importlib.import_module("azure.ai.agentserver.core.tasks._exceptions")
    return getattr(mod, "_AttachmentTooLarge")


def test_input_too_large_remap_from_steering_key() -> None:
    """/ SC-9b — when the framework receives the internal
    ``_AttachmentTooLarge`` for a ``_steering_input_<seq>`` key, it
    MUST re-raise ``InputTooLarge`` (NOT a steering-specific type).
    The prefix dispatcher treats ``_input`` and ``_steering_input_*``
    uniformly because both are caller-supplied inputs at the
    developer's layer.
    """
    from azure.ai.agentserver.core.tasks import InputTooLarge

    internal_cls = _internal_attachment_too_large_cls()
    mod = importlib.import_module("azure.ai.agentserver.core.tasks._attachments")
    dispatcher = (
        getattr(mod, "_remap_attachment_error", None)
        or getattr(mod, "_attachments_error_to_developer_facing", None)
        or getattr(mod, "_remap_attachment_too_large", None)
    )
    assert dispatcher is not None

    internal = internal_cls(task_id="t", attachment_key="steering_input_3", size_bytes=3_000_000, max_bytes=2_097_152)
    with pytest.raises(InputTooLarge):
        raise dispatcher(internal)


def test_output_too_large_remap_from_internal_output_key() -> None:
    """— for the ``_output`` attachment key, the prefix
    dispatcher MUST re-raise ``OutputTooLarge``.
    """
    from azure.ai.agentserver.core.tasks._exceptions import OutputTooLarge

    internal_cls = _internal_attachment_too_large_cls()
    mod = importlib.import_module("azure.ai.agentserver.core.tasks._attachments")
    dispatcher = (
        getattr(mod, "_remap_attachment_error", None)
        or getattr(mod, "_attachments_error_to_developer_facing", None)
        or getattr(mod, "_remap_attachment_too_large", None)
    )
    assert dispatcher is not None

    internal = internal_cls(task_id="t", attachment_key="output", size_bytes=3_000_000, max_bytes=2_097_152)
    with pytest.raises(OutputTooLarge) as excinfo:
        raise dispatcher(internal)
    #: exception.task_id removed
    assert excinfo.value.size_bytes == 3_000_000


# ===========================================================================
#  — Workstream C: no new public exports from the parity work
# ===========================================================================


def test_hosted_conflict_is_not_public() -> None:
    """C-ERR-4: `_HostedConflict` MUST NOT be in the public exception surface.

    It is an internal discriminator the framework's response classifier
    raises so lifecycle code can branch on the service's distinct error
    codes (task_immutable, lease_held_by_another, etag_mismatch, ...).
    The developer never imports it, catches it, or sees its name.
    """
    import azure.ai.agentserver.core.tasks as pub

    assert not hasattr(pub, "_HostedConflict"), (
        "_HostedConflict is internal; it MUST NOT be exported via the " "public `resilient` namespace."
    )
    assert "_HostedConflict" not in getattr(pub, "__all__", []), "_HostedConflict must not appear in __all__."


def test_no_service_code_strings_as_public_type_names() -> None:
    """C-ERR-5: service error code strings must NOT appear as public type names.

    The service emits codes like 'task_immutable', 'lease_held_by_another',
    etc. These are internal dispatch keys only; no developer-facing Python
    class should be named after them.
    """
    import azure.ai.agentserver.core.tasks as pub

    service_code_camel_cases = {
        "TaskImmutable",
        "InvalidStateTransition",
        "LeaseHeldByAnother",
        "TaskAlreadyExists",
        "LeaseOwnershipChanged",
        "EtagMismatch",
    }
    for name in service_code_camel_cases:
        assert not hasattr(pub, name), (
            f"{name!r} must not be exported from the public resilient namespace "
            f"— service codes belong to internal dispatch only."
        )


# ===========================================================================
#  Phase 2c — framework translation of internal hosted conflicts
# ===========================================================================


class _HostedConflictInjectingProvider:
    """Provider wrapper that injects one internal hosted conflict per op."""

    def __init__(self, delegate: Any) -> None:
        self._delegate = delegate
        self._failures: dict[str, list[tuple[str, int, str | None]]] = {}
        self.hide_first_get_for: set[str] = set()
        self.update_calls = 0

    def fail_once(self, op: str, code: str, *, status_code: int = 409, message: str | None = None) -> None:
        self._failures.setdefault(op, []).append((code, status_code, message))

    def _pop_failure(self, op: str, task_id: str | None) -> None:
        failures = self._failures.get(op)
        if not failures:
            return
        code, status_code, message = failures.pop(0)
        from azure.ai.agentserver.core.tasks._exceptions_internal import _HostedConflict

        raise _HostedConflict(_code=code, status_code=status_code, message=message, task_id=task_id)

    async def create(self, request: Any) -> Any:
        task_id = getattr(request, "id", None)
        self._pop_failure("create", task_id)
        return await self._delegate.create(request)

    async def get(self, task_id: str) -> Any:
        if task_id in self.hide_first_get_for:
            self.hide_first_get_for.remove(task_id)
            return None
        self._pop_failure("get", task_id)
        return await self._delegate.get(task_id)

    async def update(self, task_id: str, patch: Any) -> Any:
        self.update_calls += 1
        self._pop_failure("update", task_id)
        return await self._delegate.update(task_id, patch)

    async def delete(self, task_id: str, *, force: bool = False, cascade: bool = False) -> None:
        self._pop_failure("delete", task_id)
        await self._delegate.delete(task_id, force=force, cascade=cascade)

    async def list(self, **kwargs: Any) -> Any:
        self._pop_failure("list", None)
        return await self._delegate.list(**kwargs)


async def _setup_translation_manager(tmp_path: Path) -> tuple[Any, Any, Any]:
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    delegate = LocalFileTaskProvider(Path(str(tmp_path)))
    provider = _HostedConflictInjectingProvider(delegate)
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
    return manager, mgr_mod, provider


async def _teardown_translation_manager(manager: Any, mgr_mod: Any) -> None:
    await manager.shutdown()
    mgr_mod._manager = None


async def _seed_task(provider: Any, task_id: str, status: str) -> None:
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

    await provider._delegate.create(  # pylint: disable=protected-access
        TaskCreateRequest(
            id=task_id,
            agent_name="test-agent",
            session_id="test-session",
            status=status,
            title=f"{task_id}-title",
            payload={"input": "seed"},
        )
    )


@pytest.mark.asyncio
async def test_task_run_translates_task_immutable_to_completed_conflict(tmp_path) -> None:
    from azure.ai.agentserver.core.tasks._exceptions import TaskConflictError
    from azure.ai.agentserver.core.tasks._exceptions_internal import _HostedConflict

    manager, mgr_mod, provider = await _setup_translation_manager(tmp_path)
    try:
        await _seed_task(provider, "hosted-immutable", "pending")
        provider.fail_once("update", "task_immutable", message="Completed tasks are immutable.")

        @task(name="hosted-immutable", title="hosted-immutable")
        async def immutable_task(ctx: TaskContext[str]) -> str:
            return "unreachable"

        with pytest.raises(TaskConflictError) as excinfo:
            await immutable_task.run(task_id="hosted-immutable", input="new")
        assert excinfo.value.current_status == "completed"
        assert not isinstance(excinfo.value, _HostedConflict)
    finally:
        await _teardown_translation_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_task_already_exists_observes_status_for_public_conflict(tmp_path) -> None:
    from azure.ai.agentserver.core.tasks._exceptions import TaskConflictError

    manager, mgr_mod, provider = await _setup_translation_manager(tmp_path)
    try:
        await _seed_task(provider, "hosted-create-race", "completed")
        provider.hide_first_get_for.add("hosted-create-race")
        provider.fail_once("create", "task_already_exists", message="Task already exists.")

        @task(name="hosted-create-race", title="hosted-create-race")
        async def create_race_task(ctx: TaskContext[str]) -> str:
            return "unreachable"

        with pytest.raises(TaskConflictError) as excinfo:
            await create_race_task.run(task_id="hosted-create-race", input="new")
        #: exception.task_id removed
        assert excinfo.value.current_status == "completed"
    finally:
        await _teardown_translation_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_invalid_request_translates_to_task_precondition_failed(tmp_path) -> None:
    from azure.ai.agentserver.core.tasks._exceptions import TaskPreconditionFailed
    from azure.ai.agentserver.core.tasks._exceptions_internal import _HostedConflict

    manager, mgr_mod, provider = await _setup_translation_manager(tmp_path)
    try:
        await _seed_task(provider, "hosted-invalid-request", "pending")
        provider.fail_once("update", "invalid_request", status_code=400, message="lease rule failed")

        @task(name="hosted-invalid-request", title="hosted-invalid-request")
        async def invalid_request_task(ctx: TaskContext[str]) -> str:
            return "unreachable"

        with pytest.raises(TaskPreconditionFailed) as excinfo:
            await invalid_request_task.run(task_id="hosted-invalid-request", input="new")
        #: exception.task_id removed
        assert "lease rule failed" in str(excinfo.value)
        assert not isinstance(excinfo.value, _HostedConflict)
    finally:
        await _teardown_translation_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_etag_mismatch_retries_without_exposing_hosted_conflict(tmp_path) -> None:
    from azure.ai.agentserver.core.tasks._exceptions_internal import _HostedConflict

    manager, mgr_mod, provider = await _setup_translation_manager(tmp_path)
    try:
        await _seed_task(provider, "hosted-etag-retry", "suspended")
        provider.fail_once("update", "etag_mismatch", status_code=412, message="ETag mismatch.")

        @task(name="hosted-etag-retry", title="hosted-etag-retry")
        async def etag_retry_task(ctx: TaskContext[str]) -> str:
            return f"resumed:{ctx.input}"

        result = await etag_retry_task.run(task_id="hosted-etag-retry", input="new")
        assert result == "resumed:new"
        assert provider.update_calls >= 2
    except Exception as exc:
        assert not isinstance(exc, _HostedConflict)
        raise
    finally:
        await _teardown_translation_manager(manager, mgr_mod)
