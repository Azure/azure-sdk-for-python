# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Local filesystem-backed resilient task provider.

Stores tasks as JSON files under
``${AGENTSERVER_STATE_ROOT:-~/.agentserver}/tasks/{agent_name}/{session_id}/``
(unified storage layout) for local development with
full lifecycle parity.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Iterable

from . import _validation
from ._attachments import (
    _validate_attachment_count,
    _validate_attachment_size,
)
from ._exceptions_internal import TaskNotFound
from ._exceptions_internal import _HostedConflict
from ._models import (
    LeaseInfo,
    TaskCreateRequest,
    TaskInfo,
    TaskPatchRequest,
    TaskStatus,
)

logger = logging.getLogger("azure.ai.agentserver.tasks")


class _LocalEtagMismatch(_HostedConflict, ValueError):
    """ETag mismatch that preserves legacy local-provider ValueError checks."""


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _generate_etag(data: dict[str, Any]) -> str:
    raw = json.dumps(data, sort_keys=True)
    return f"local-{hashlib.sha256(raw.encode()).hexdigest()[:16]}"


def _is_lease_expired(lease: LeaseInfo | None) -> bool:
    if lease is None:
        return True
    try:
        expires = datetime.datetime.fromisoformat(lease.expires_at)
        now = datetime.datetime.now(datetime.timezone.utc)
        return now >= expires
    except (ValueError, TypeError):
        return True


def _expires_at(duration_seconds: int) -> str:
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration_seconds)).isoformat()


def _invalid_request(message: str, task_id: str | None = None) -> None:
    raise _HostedConflict(_code="invalid_request", status_code=400, message=message, task_id=task_id)


def _lease_held(task_id: str) -> None:
    raise _HostedConflict(
        _code="lease_held_by_another",
        status_code=409,
        message="Lease is held by another owner or instance.",
        task_id=task_id,
    )


def _etag_mismatch(task_id: str) -> None:
    raise _LocalEtagMismatch(
        _code="etag_mismatch",
        status_code=412,
        message="ETag mismatch.",
        task_id=task_id,
    )


class LocalFileTaskProvider:
    """Filesystem-backed provider for local development.

    Tasks are stored as individual JSON files. Lease expiry is simulated
    by checking timestamps on read.

    :param base_dir: Root directory for task storage.
        Defaults to ``${AGENTSERVER_STATE_ROOT:-~/.agentserver}/tasks``
        via :func:`azure.ai.agentserver.core._config.resolve_state_subdir`.
    :type base_dir: Path | None
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            from .._config import (  # pylint: disable=import-outside-toplevel
                resolve_state_subdir,
            )

            base_dir = resolve_state_subdir("tasks")
        self._base_dir = base_dir

    def _task_dir(self, agent_name: str, session_id: str) -> Path:
        return self._base_dir / agent_name / session_id

    def _task_path(self, agent_name: str, session_id: str, task_id: str) -> Path:
        return self._task_dir(agent_name, session_id) / f"{task_id}.json"

    def _find_task_path(self, task_id: str) -> Path | None:
        """Search all agent/session dirs for a task file.

        :param task_id: The task identifier.
        :type task_id: str
        :return: The path to the task file, or None.
        :rtype: ~pathlib.Path | None
        """
        if not self._base_dir.exists():
            return None
        for agent_dir in self._base_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            for session_dir in agent_dir.iterdir():
                if not session_dir.is_dir():
                    continue
                path = session_dir / f"{task_id}.json"
                if path.exists():
                    return path
        return None

    def _iter_task_paths(self, agent_name: str | None, session_id: str | None) -> Iterable[Path]:
        if not self._base_dir.exists():
            return []
        if agent_name is not None and session_id is not None:
            task_dir = self._task_dir(agent_name, session_id)
            return task_dir.glob("*.json") if task_dir.exists() else []
        if agent_name is not None:
            agent_dir = self._base_dir / agent_name
            if not agent_dir.exists():
                return []
            return (
                path
                for session_dir in agent_dir.iterdir()
                if session_dir.is_dir()
                for path in session_dir.glob("*.json")
            )
        if session_id is not None:
            return (
                path
                for agent_dir in self._base_dir.iterdir()
                if agent_dir.is_dir()
                for session_dir in agent_dir.iterdir()
                if session_dir.is_dir() and session_dir.name == session_id
                for path in session_dir.glob("*.json")
            )
        return (
            path
            for agent_dir in self._base_dir.iterdir()
            if agent_dir.is_dir()
            for session_dir in agent_dir.iterdir()
            if session_dir.is_dir()
            for path in session_dir.glob("*.json")
        )

    def _read_task(self, path: Path) -> TaskInfo | None:
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return TaskInfo.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            logger.warning("Corrupt task file: %s", path)
            return None

    def _write_task(self, task: TaskInfo) -> None:
        path = self._task_path(task.agent_name, task.session_id, task.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = task.to_dict()
        data["etag"] = _generate_etag(data)
        task.etag = data["etag"]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def _validate_create_request(request: TaskCreateRequest, task_id: str) -> str:
        _validation.validate_task_id(task_id)
        _validation.validate_required_string(request.agent_name, "agent_name", _validation.MAX_AGENT_NAME_LEN)
        _validation.validate_required_string(request.session_id, "session_id", _validation.MAX_SESSION_ID_LEN)
        _validation.validate_required_string(request.title, "title", _validation.MAX_TITLE_LEN)
        _validation.validate_optional_string(request.description, "description", _validation.MAX_DESCRIPTION_LEN)
        _validation.validate_tags(request.tags)
        _validation.validate_payload_size(request.payload)
        _validation.validate_source(request.source)
        _validation.validate_attachment_keys(request.attachments)
        try:
            return _validation.validate_create_status(request.status)
        except _HostedConflict:
            # A few local-only recovery tests seed terminal/suspended records
            # directly through the provider. Preserve that legacy seeding path
            # while still rejecting the reserved "failed" input status.
            if request.status == "failed":
                raise
            return _validation.validate_patch_status(request.status) or "pending"

    @staticmethod
    def _validate_create_attachments(task_id: str, attachments: dict[str, Any] | None) -> dict[str, Any] | None:
        if attachments is None:
            return None
        additions = sum(1 for value in attachments.values() if value is not None)
        _validate_attachment_count(task_id=task_id, current_count=0, additions=additions)
        for key, value in attachments.items():
            _validate_attachment_size(task_id=task_id, attachment_key=key, value=value)
        created = {key: value for key, value in attachments.items() if value is not None}
        return created or None

    async def create(self, request: TaskCreateRequest) -> TaskInfo:
        """Create a new task as a JSON file.

        :param request: Task creation parameters.
        :type request: TaskCreateRequest
        :return: The created task record.
        :rtype: TaskInfo
        """
        now = _now_iso()
        task_id = request.id or f"task-{os.urandom(8).hex()}"
        status = self._validate_create_request(request, task_id)
        lease_request = _validation.validate_lease_params(
            request.lease_owner,
            request.lease_instance_id,
            request.lease_duration_seconds,
        )

        if status == "pending" and lease_request is not None:
            _invalid_request(
                "lease_owner, lease_instance_id, and lease_duration_seconds must "
                "not be provided when status is pending.",
                task_id,
            )
        if self._find_task_path(task_id) is not None:
            raise _HostedConflict(
                _code="task_already_exists",
                status_code=409,
                message=f"Task {task_id!r} already exists.",
                task_id=task_id,
            )

        lease: LeaseInfo | None = None
        started_at: str | None = None
        completed_at: str | None = now if status == "completed" else None
        if lease_request is not None:
            owner, instance_id, duration_seconds = lease_request
            lease = LeaseInfo(
                owner=owner,
                instance_id=instance_id,
                generation=0,
                expires_at=_expires_at(duration_seconds),
                expiry_count=0,
                heartbeat_at=now,
            )
            if status == "in_progress":
                started_at = now

        task = TaskInfo(
            id=task_id,
            agent_name=request.agent_name,
            session_id=request.session_id,
            status=status,  # type: ignore[arg-type]
            title=request.title,
            description=request.description,
            lease=lease,
            payload=request.payload,
            tags=request.tags,
            source=request.source,
            attachments=self._validate_create_attachments(task_id, request.attachments),
            created_at=now,
            updated_at=now,
            started_at=started_at,
            completed_at=completed_at,
        )
        self._write_task(task)
        logger.debug("Created local task %s", task_id)
        return task

    async def get(self, task_id: str) -> TaskInfo | None:
        """Get a task by ID from the filesystem.

        :param task_id: The task identifier.
        :type task_id: str
        :return: The task record, or ``None`` if not found.
        :rtype: TaskInfo | None
        """
        path = self._find_task_path(task_id)
        if path is None:
            return None
        return self._read_task(path)

    @staticmethod
    def _reject_immutable_patch_fields(patch: TaskPatchRequest | dict[str, Any], task_id: str) -> None:
        for field_name in _validation.IMMUTABLE_PATCH_FIELDS:
            if isinstance(patch, dict):
                value = patch.get(field_name)
            else:
                value = getattr(patch, field_name, None)
            if value is None:
                continue
            if field_name == "source":
                _validation.validate_source(value)
            _invalid_request(f"{field_name} is immutable and cannot be patched.", task_id)

    @staticmethod
    def _patch_is_completed_noop(
        patch: TaskPatchRequest,
        normalized_status: str | None,
        lease_request: tuple[str, str, int] | None,
    ) -> bool:
        return (
            normalized_status in (None, "completed")
            and patch.payload is None
            and patch.tags is None
            and patch.error is None
            and patch.suspension_reason is None
            and lease_request is None
            and patch.attachments is None
            and not getattr(patch, "clear_attachments", False)
        )

    @staticmethod
    def _lease_matches(lease: LeaseInfo | None, owner: str, instance_id: str) -> bool:
        return lease is not None and lease.owner == owner and lease.instance_id == instance_id

    @staticmethod
    def _apply_lease_acquisition(
        task: TaskInfo,
        lease_request: tuple[str, str, int],
        now: str,
    ) -> None:
        owner, instance_id, duration_seconds = lease_request
        current = task.lease
        generation = 0
        expiry_count = 0
        if current is not None:
            expired = _is_lease_expired(current)
            expiry_count = current.expiry_count
            if current.owner == owner and current.instance_id == instance_id:
                generation = current.generation
            elif current.owner == owner:
                generation = current.generation + 1
                if expired:
                    expiry_count = current.expiry_count + 1
            elif expired:
                generation = current.generation + 1
                expiry_count = current.expiry_count + 1
            else:
                _lease_held(task.id)

        task.lease = LeaseInfo(
            owner=owner,
            instance_id=instance_id,
            generation=generation,
            expires_at=_expires_at(duration_seconds),
            expiry_count=expiry_count,
            heartbeat_at=now,
        )

    @staticmethod
    def _validate_lease_rules(
        task: TaskInfo,
        target_status: str,
        status_change: bool,
        lease_request: tuple[str, str, int] | None,
    ) -> None:
        if lease_request is None:
            if status_change and task.status == "in_progress" and target_status == "pending":
                _lease_held(task.id)
            return

        owner, instance_id, duration_seconds = lease_request
        if status_change and duration_seconds == 0:
            _invalid_request(
                "lease_duration_seconds=0 cannot be combined with a status change.",
                task.id,
            )
        if status_change and target_status in {"completed", "suspended"}:
            _invalid_request(
                "lease parameters cannot be supplied when transitioning to " f"{target_status}.",
                task.id,
            )
        if status_change and task.status == "in_progress" and target_status == "pending":
            if not LocalFileTaskProvider._lease_matches(task.lease, owner, instance_id):
                _lease_held(task.id)
        if not status_change and duration_seconds > 0 and task.status != "in_progress":
            _invalid_request(
                "Lease renewal is only allowed when current status is in_progress.",
                task.id,
            )
        if duration_seconds == 0:
            if task.lease is None:
                _invalid_request("No lease is available to force-expire.", task.id)
            if not _is_lease_expired(task.lease) and not LocalFileTaskProvider._lease_matches(
                task.lease, owner, instance_id
            ):
                _lease_held(task.id)
        elif task.lease is not None and task.lease.owner != owner and not _is_lease_expired(task.lease):
            _lease_held(task.id)

    @staticmethod
    def _apply_payload_patch(task: TaskInfo, payload: Any) -> None:
        if payload is None:
            return
        if isinstance(payload, dict):
            current = task.payload if isinstance(task.payload, dict) else {}
            merged = dict(current)
            merged.update(payload)
            _validation.validate_payload_size(merged)
            task.payload = merged
        else:
            _validation.validate_payload_size(payload)
            task.payload = payload

    @staticmethod
    def _apply_tags_patch(task: TaskInfo, tags: dict[str, Any]) -> None:
        merged = dict(task.tags or {})
        for key, value in tags.items():
            if value is None:
                merged.pop(key, None)
            else:
                merged[key] = value
        _validation.validate_tags(merged)
        task.tags = merged or None

    @staticmethod
    def _apply_attachments_patch(
        task: TaskInfo,
        attachments: dict[str, Any] | None,
        clear_attachments: bool,
    ) -> None:
        if clear_attachments:
            task.attachments = None
            return
        if attachments is None:
            return
        _validation.validate_attachment_keys(attachments)
        for key, value in attachments.items():
            _validate_attachment_size(task_id=task.id, attachment_key=key, value=value)
        merged = dict(task.attachments or {})
        for key, value in attachments.items():
            if value is None:
                merged.pop(key, None)
            else:
                merged[key] = value
        _validate_attachment_count(task_id=task.id, current_count=len(merged), additions=0)
        task.attachments = merged or None

    async def update(  # pylint: disable=too-many-branches,too-many-statements
        self, task_id: str, patch: TaskPatchRequest
    ) -> TaskInfo:
        """Update a task via PATCH semantics.

        :param task_id: The task identifier.
        :type task_id: str
        :param patch: Fields to update.
        :type patch: TaskPatchRequest
        :return: The updated task record.
        :rtype: TaskInfo
        :raises TaskNotFound: If the task does not exist.
        """
        path = self._find_task_path(task_id)
        if path is None:
            raise TaskNotFound(task_id)

        task = self._read_task(path)
        if task is None:
            raise TaskNotFound(task_id)

        if patch.if_match is not None and patch.if_match != task.etag:
            _etag_mismatch(task_id)

        normalized_status = _validation.validate_patch_status(patch.status)
        lease_request = _validation.validate_lease_params(
            patch.lease_owner,
            patch.lease_instance_id,
            patch.lease_duration_seconds,
        )
        self._reject_immutable_patch_fields(patch, task_id)
        _validation.validate_tags(patch.tags)
        _validation.validate_payload_size(patch.payload)
        _validation.validate_error(patch.error)
        normalized_error = _validation.normalize_error(patch.error)
        _validation.validate_optional_string(
            patch.suspension_reason,
            "suspension_reason",
            _validation.MAX_SUSPENSION_REASON_LEN,
        )

        if getattr(patch, "clear_attachments", False) and patch.attachments is not None:
            _invalid_request("clear_attachments cannot be combined with attachments patch.", task_id)

        target_status = normalized_status or task.status
        if patch.suspension_reason is not None and target_status != "suspended":
            _invalid_request(
                "suspension_reason is only allowed when target status is suspended.",
                task_id,
            )

        if task.status == "completed":
            if self._patch_is_completed_noop(patch, normalized_status, lease_request):
                return task
            raise _HostedConflict(
                _code="task_immutable",
                status_code=409,
                message="Completed tasks are immutable.",
                task_id=task_id,
            )

        status_change = normalized_status is not None and normalized_status != task.status
        if status_change:
            _validation.validate_transition(task.status, target_status)
        self._validate_lease_rules(task, target_status, status_change, lease_request)

        now = _now_iso()
        if status_change:
            task.status = target_status  # type: ignore[assignment]
            if target_status == "pending":
                task.lease = None
                task.suspension_reason = None
            elif target_status == "in_progress":
                if lease_request is not None:
                    self._apply_lease_acquisition(task, lease_request, now)
                if task.started_at is None:
                    task.started_at = now
                task.suspension_reason = None
                task.completed_at = None
            elif target_status == "completed":
                task.lease = None
                task.suspension_reason = None
                if task.completed_at is None:
                    task.completed_at = now
            elif target_status == "suspended":
                task.lease = None
                task.suspension_reason = patch.suspension_reason
                task.completed_at = None
        elif lease_request is not None:
            _, _, duration_seconds = lease_request
            if duration_seconds == 0:
                assert task.lease is not None
                task.lease.expires_at = now
                task.lease.heartbeat_at = now
            else:
                self._apply_lease_acquisition(task, lease_request, now)

        self._apply_payload_patch(task, patch.payload)
        if patch.tags is not None:
            self._apply_tags_patch(task, patch.tags)
        self._apply_attachments_patch(
            task,
            patch.attachments,
            getattr(patch, "clear_attachments", False),
        )
        if normalized_error is not None:
            task.error = normalized_error
        if not status_change and patch.suspension_reason is not None:
            task.suspension_reason = patch.suspension_reason

        task.updated_at = now
        self._write_task(task)
        return task

    async def delete(
        self,
        task_id: str,
        *,
        force: bool = False,
        cascade: bool = False,  # pylint: disable=unused-argument
        if_match: str | None = None,
    ) -> None:
        """Delete a task JSON file.

        :param task_id: The task identifier.
        :type task_id: str
        :keyword force: Required for non-terminal tasks.
        :paramtype force: bool
        :keyword cascade: Delete dependent tasks (no-op for local).
        :paramtype cascade: bool
        :keyword if_match: ETag precondition for delete.
        :paramtype if_match: str | None
        """
        path = self._find_task_path(task_id)
        if path is None:
            raise TaskNotFound(task_id)
        task = self._read_task(path)
        if task is None:
            raise TaskNotFound(task_id)
        if if_match is not None and if_match != task.etag:
            _etag_mismatch(task_id)
        if task.status != "completed" and not force:
            _invalid_request("Non-terminal tasks require force=true for deletion.", task_id)
        path.unlink(missing_ok=True)
        logger.debug("Deleted local task %s", task_id)

    async def list(  # pylint: disable=too-many-branches
        self,
        *,
        agent_name: str | None = None,
        session_id: str | None = None,
        status: TaskStatus | str | None = None,
        lease_owner: str | None = None,
        tag: dict[str, str] | None = None,
        source_type: str | None = None,
        has_error: bool | None = None,
        lease_expired: bool | None = None,
        limit: int | None = None,
        after: str | None = None,
        before: str | None = None,
        order: str | None = None,
        omit_attachment_values: bool = False,
    ) -> list[TaskInfo]:
        """List tasks from the filesystem.

        :keyword agent_name: Filter to tasks owned by this agent name.
        :paramtype agent_name: str | None
        :keyword session_id: Filter to tasks for this session ID.
        :paramtype session_id: str | None
        :keyword status: Optional status filter.
        :paramtype status: TaskStatus | str | None
        :keyword lease_owner: Optional lease-owner filter.
        :paramtype lease_owner: str | None
        :keyword tag: Optional tag-equality filter.
        :paramtype tag: dict[str, str] | None
        :keyword source_type: Optional source-type filter.
        :paramtype source_type: str | None
        :keyword has_error: Optional filter for tasks that have a recorded error.
        :paramtype has_error: bool | None
        :keyword lease_expired: Optional filter for tasks whose lease has expired.
        :paramtype lease_expired: bool | None
        :keyword limit: Page size for pagination.
        :paramtype limit: int | None
        :keyword after: Return tasks after this pagination cursor.
        :paramtype after: str | None
        :keyword before: Return tasks before this pagination cursor (unsupported).
        :paramtype before: str | None
        :keyword order: Sort order (``asc`` or ``desc``).
        :paramtype order: str | None
        :keyword omit_attachment_values: When True, omit attachment values from results.
        :paramtype omit_attachment_values: bool
        :return: All matching tasks.
        :rtype: list[TaskInfo]
        """
        if before is not None:
            _invalid_request("before is not supported for task list.")
        page_size = 20 if limit is None else limit
        if page_size <= 0:
            _invalid_request("limit must be greater than 0.")
        page_size = min(page_size, 100)
        sort_order = order or "desc"
        if sort_order not in {"asc", "desc"}:
            _invalid_request("order must be 'asc' or 'desc'.")
        normalized_status = _validation.normalize_legacy_status(status)

        results: list[TaskInfo] = []
        for path in self._iter_task_paths(agent_name, session_id):
            task = self._read_task(path)
            if task is None:
                continue
            if agent_name is not None and task.agent_name != agent_name:
                continue
            if session_id is not None and task.session_id != session_id:
                continue
            if normalized_status is not None and task.status != normalized_status:
                continue
            if lease_owner is not None:
                if task.lease is None or task.lease.owner != lease_owner:
                    continue
            if tag is not None:
                task_tags = task.tags or {}
                if not all(task_tags.get(key) == value for key, value in tag.items()):
                    continue
            if source_type is not None:
                task_source = task.source or {}
                if task_source.get("type") != source_type:
                    continue
            if has_error is not None and bool(task.error) != has_error:
                continue
            if lease_expired is not None and _is_lease_expired(task.lease) != lease_expired:
                continue
            results.append(task)

        results.sort(key=lambda item: item.created_at or "", reverse=sort_order == "desc")
        if after is not None:
            for index, task in enumerate(results):
                if task.id == after:
                    results = results[index + 1 :]
                    break
            else:
                results = []
        results = results[:page_size]
        if omit_attachment_values:
            for task in results:
                if task.attachments is not None:
                    task.attachments = {key: None for key in task.attachments}
        return results
