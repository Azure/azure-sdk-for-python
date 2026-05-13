# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Local filesystem-backed durable task provider.

Stores tasks as JSON files under ``$HOME/.durable-tasks/{agent_name}/{session_id}/``
for local development with full lifecycle parity.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any

from ._exceptions import TaskNotFound
from ._models import (
    LeaseInfo,
    TaskCreateRequest,
    TaskInfo,
    TaskPatchRequest,
    TaskStatus,
)

logger = logging.getLogger("azure.ai.agentserver.durable")


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


class LocalFileDurableTaskProvider:
    """Filesystem-backed provider for local development.

    Tasks are stored as individual JSON files. Lease expiry is simulated
    by checking timestamps on read.

    :param base_dir: Root directory for task storage.
        Defaults to ``$HOME/.durable-tasks``.
    :type base_dir: Path | None
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or Path.home() / ".durable-tasks"

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

    async def create(self, request: TaskCreateRequest) -> TaskInfo:
        """Create a new task as a JSON file.

        :param request: Task creation parameters.
        :type request: TaskCreateRequest
        :return: The created task record.
        :rtype: TaskInfo
        """
        now = _now_iso()
        task_id = request.id or f"task-{os.urandom(8).hex()}"

        lease: LeaseInfo | None = None
        started_at: str | None = None
        status: TaskStatus = request.status

        if request.lease_owner and request.lease_instance_id and request.lease_duration_seconds:
            expires_at = (
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(seconds=request.lease_duration_seconds)
            ).isoformat()
            lease = LeaseInfo(
                owner=request.lease_owner,
                instance_id=request.lease_instance_id,
                generation=0,
                expires_at=expires_at,
                expiry_count=0,
            )
            if status == "in_progress":
                started_at = now

        task = TaskInfo(
            id=task_id,
            agent_name=request.agent_name,
            session_id=request.session_id,
            status=status,
            title=request.title,
            description=request.description,
            lease=lease,
            payload=request.payload,
            tags=request.tags,
            source=request.source,
            created_at=now,
            updated_at=now,
            started_at=started_at,
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

    async def update(self, task_id: str, patch: TaskPatchRequest) -> TaskInfo:  # pylint: disable=too-many-branches,too-many-statements
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

        # ETag check
        if patch.if_match is not None and patch.if_match != task.etag:
            raise ValueError(f"ETag mismatch: expected {patch.if_match!r}, " f"got {task.etag!r}")

        now = _now_iso()

        if patch.status is not None:
            old_status = task.status  # noqa: F841  # pylint: disable=unused-variable
            task.status = patch.status

            if patch.status == "in_progress" and task.started_at is None:
                task.started_at = now
            if patch.status == "completed":
                task.completed_at = now
            if patch.status == "suspended":
                task.suspension_reason = patch.suspension_reason

            # Lease handling on status transitions
            if patch.status in ("completed", "suspended"):
                task.lease = None
            elif patch.status == "in_progress" and patch.lease_owner and patch.lease_instance_id:
                duration = patch.lease_duration_seconds or 60
                expires_at = (
                    datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration)
                ).isoformat()
                old_gen = task.lease.generation if task.lease else -1
                new_gen = (
                    old_gen + 1
                    if patch.lease_instance_id != (task.lease.instance_id if task.lease else "")
                    else max(old_gen, 0)
                )
                task.lease = LeaseInfo(
                    owner=patch.lease_owner,
                    instance_id=patch.lease_instance_id,
                    generation=new_gen,
                    expires_at=expires_at,
                    expiry_count=task.lease.expiry_count if task.lease else 0,
                )

        # Lease renewal (no status change)
        if patch.status is None and patch.lease_owner and patch.lease_instance_id:
            duration = patch.lease_duration_seconds or 60
            expires_at = (
                datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration)
            ).isoformat()
            if task.lease and patch.lease_instance_id != task.lease.instance_id:
                # Reclaim with new instance
                task.lease = LeaseInfo(
                    owner=patch.lease_owner,
                    instance_id=patch.lease_instance_id,
                    generation=task.lease.generation + 1,
                    expires_at=expires_at,
                    expiry_count=task.lease.expiry_count,
                )
            elif task.lease:
                # Simple renewal
                task.lease = LeaseInfo(
                    owner=task.lease.owner,
                    instance_id=task.lease.instance_id,
                    generation=task.lease.generation,
                    expires_at=expires_at,
                    expiry_count=task.lease.expiry_count,
                )
            else:
                task.lease = LeaseInfo(
                    owner=patch.lease_owner,
                    instance_id=patch.lease_instance_id,
                    generation=0,
                    expires_at=expires_at,
                )

        # Force-expire: lease_duration_seconds=0
        if patch.lease_duration_seconds == 0 and task.lease:
            task.lease = LeaseInfo(
                owner=task.lease.owner,
                instance_id=task.lease.instance_id,
                generation=task.lease.generation,
                expires_at=_now_iso(),
                expiry_count=task.lease.expiry_count,
            )

        # Payload shallow-merge
        if patch.payload is not None:
            if task.payload is None:
                task.payload = {}
            for key, value in patch.payload.items():
                if isinstance(value, dict) and isinstance(task.payload.get(key), dict):
                    task.payload[key].update(value)
                else:
                    task.payload[key] = value

        # Tags null-as-delete merge
        if patch.tags is not None:
            if task.tags is None:
                task.tags = {}
            for key, value in patch.tags.items():
                if value is None:
                    task.tags.pop(key, None)
                else:
                    task.tags[key] = value

        if patch.error is not None:
            task.error = patch.error

        task.updated_at = now
        self._write_task(task)
        return task

    async def delete(
        self,
        task_id: str,
        *,
        force: bool = False,  # pylint: disable=unused-argument
        cascade: bool = False,  # pylint: disable=unused-argument
    ) -> None:
        """Delete a task JSON file.

        :param task_id: The task identifier.
        :type task_id: str
        :keyword force: Release active lease before deleting.
        :paramtype force: bool
        :keyword cascade: Delete dependent tasks (no-op for local).
        :paramtype cascade: bool
        """
        path = self._find_task_path(task_id)
        if path is None:
            raise TaskNotFound(task_id)
        path.unlink(missing_ok=True)
        logger.debug("Deleted local task %s", task_id)

    async def list(
        self,
        *,
        agent_name: str,
        session_id: str,
        status: TaskStatus | None = None,
        lease_owner: str | None = None,
    ) -> list[TaskInfo]:
        """List tasks from the filesystem.

        :keyword agent_name: Filter by agent name.
        :paramtype agent_name: str
        :keyword session_id: Filter by session ID.
        :paramtype session_id: str
        :keyword status: Filter by task status.
        :paramtype status: TaskStatus | None
        :keyword lease_owner: Filter by lease owner.
        :paramtype lease_owner: str | None
        :return: Matching task records.
        :rtype: list[TaskInfo]
        """
        task_dir = self._task_dir(agent_name, session_id)
        if not task_dir.exists():
            return []

        results: list[TaskInfo] = []
        for path in task_dir.glob("*.json"):
            task = self._read_task(path)
            if task is None:
                continue
            if status is not None and task.status != status:
                continue
            if lease_owner is not None:
                if task.lease is None or task.lease.owner != lease_owner:
                    continue
            results.append(task)
        return results
