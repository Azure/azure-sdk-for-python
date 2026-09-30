# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Storage provider protocol for the resilient task subsystem.

Defines the structural typing contract that hosted and local providers
must satisfy. Uses :class:`typing.Protocol` (PEP 544) — implementations
do not need to inherit from this class.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ._models import TaskCreateRequest, TaskInfo, TaskPatchRequest, TaskStatus


@runtime_checkable
class TaskProvider(Protocol):
    """Async storage backend for resilient tasks.

    Both :class:`HostedTaskProvider` (HTTP → Task Storage API) and
    :class:`LocalFileTaskProvider` (filesystem) implement this
    protocol.
    """

    async def create(self, request: TaskCreateRequest) -> TaskInfo:
        """Create a new task.

        :param request: Task creation parameters.
        :type request: TaskCreateRequest
        :return: The created task record.
        :rtype: TaskInfo
        """
        ...

    async def get(self, task_id: str) -> TaskInfo | None:
        """Get a single task by ID.

        :param task_id: The task identifier.
        :type task_id: str
        :return: The task record, or ``None`` if not found.
        :rtype: TaskInfo | None
        """
        ...

    async def update(self, task_id: str, patch: TaskPatchRequest) -> TaskInfo:
        """Update a task via PATCH semantics.

        :param task_id: The task identifier.
        :type task_id: str
        :param patch: Fields to update.
        :type patch: TaskPatchRequest
        :return: The updated task record.
        :rtype: TaskInfo
        :raises TaskNotFound: If the task does not exist.
        """
        ...

    async def delete(
        self,
        task_id: str,
        *,
        force: bool = False,
        cascade: bool = False,
    ) -> None:
        """Delete a task.

        :param task_id: The task identifier.
        :type task_id: str
        :keyword force: Release active lease before deleting.
        :paramtype force: bool
        :keyword cascade: Delete dependent tasks.
        :paramtype cascade: bool
        """
        ...

    async def list(
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
        """List tasks with filters.

        :keyword agent_name: Filter by agent name.
        :paramtype agent_name: str
        :keyword session_id: Filter by session ID.
        :paramtype session_id: str
        :keyword status: Filter by task status.
        :paramtype status: TaskStatus | None
        :keyword lease_owner: Filter by lease owner.
        :paramtype lease_owner: str | None
        :keyword tag: Filter by tags (AND semantics — all must match).
        :paramtype tag: dict[str, str] | None
        :keyword source_type: Filter by source type.
        :paramtype source_type: str | None
        :keyword has_error: Filter by whether the task has a recorded error.
        :paramtype has_error: bool | None
        :keyword lease_expired: Filter by whether the task's lease has expired.
        :paramtype lease_expired: bool | None
        :keyword limit: Maximum number of records to return.
        :paramtype limit: int | None
        :keyword after: Return records after this pagination cursor.
        :paramtype after: str | None
        :keyword before: Return records before this pagination cursor.
        :paramtype before: str | None
        :keyword order: Sort order for the returned records.
        :paramtype order: str | None
        :keyword omit_attachment_values: When True, omit attachment values from results.
        :paramtype omit_attachment_values: bool
        :return: Matching task records.
        :rtype: list[TaskInfo]
        """
        ...
