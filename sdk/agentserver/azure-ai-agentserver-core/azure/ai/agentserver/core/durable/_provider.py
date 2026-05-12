# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Storage provider protocol for the durable task subsystem.

Defines the structural typing contract that hosted and local providers
must satisfy. Uses :class:`typing.Protocol` (PEP 544) — implementations
do not need to inherit from this class.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ._models import TaskCreateRequest, TaskInfo, TaskPatchRequest, TaskStatus


@runtime_checkable
class DurableTaskProvider(Protocol):
    """Async storage backend for durable tasks.

    Both :class:`HostedDurableTaskProvider` (HTTP → Task Storage API) and
    :class:`LocalFileDurableTaskProvider` (filesystem) implement this
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
        agent_name: str,
        session_id: str,
        status: TaskStatus | None = None,
        lease_owner: str | None = None,
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
        :return: Matching task records.
        :rtype: list[TaskInfo]
        """
        ...
