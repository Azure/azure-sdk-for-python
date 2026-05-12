# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Hosted durable task provider — HTTP client for the Foundry Task Storage API.

Communicates with ``{FOUNDRY_PROJECT_ENDPOINT}/storage/tasks`` using
``httpx.AsyncClient``. Bearer tokens are obtained lazily from
``DefaultAzureCredential`` when running in a hosted environment.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ._exceptions import TaskNotFound
from ._models import (
    LeaseInfo,
    TaskCreateRequest,
    TaskInfo,
    TaskPatchRequest,
    TaskStatus,
)

logger = logging.getLogger("azure.ai.agentserver.durable")

_AUTH_SCOPE = "https://ai.azure.com/.default"
_API_VERSION = "v1"


class HostedDurableTaskProvider:
    """HTTP-backed provider for the Foundry Task Storage API.

    :param project_endpoint: The ``FOUNDRY_PROJECT_ENDPOINT`` base URL.
    :type project_endpoint: str
    :param credential: An ``azure.identity.aio.DefaultAzureCredential``
        instance, or any token credential supporting ``get_token(scope)``.
    :type credential: Any
    """

    def __init__(self, project_endpoint: str, credential: Any) -> None:
        self._base_url = f"{project_endpoint.rstrip('/')}/storage/tasks"
        self._credential = credential
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _get_headers(self) -> dict[str, str]:
        token = await self._credential.get_token(_AUTH_SCOPE)
        return {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
        }

    async def create(self, request: TaskCreateRequest) -> TaskInfo:
        """Create a new task via POST /storage/tasks.

        :param request: Task creation parameters.
        :type request: TaskCreateRequest
        :return: The created task record.
        :rtype: TaskInfo
        """
        headers = await self._get_headers()
        params: dict[str, str] = {"api-version": _API_VERSION}
        if request.lease_owner is not None:
            params["lease_owner"] = request.lease_owner
        if request.lease_instance_id is not None:
            params["lease_instance_id"] = request.lease_instance_id
        if request.lease_duration_seconds is not None:
            params["lease_duration_seconds"] = str(request.lease_duration_seconds)

        body: dict[str, Any] = {
            "agent_name": request.agent_name,
            "session_id": request.session_id,
        }
        if request.id is not None:
            body["id"] = request.id
        if request.status != "pending":
            body["status"] = request.status
        if request.title is not None:
            body["title"] = request.title
        if request.description is not None:
            body["description"] = request.description
        if request.payload is not None:
            body["payload"] = request.payload
        if request.tags is not None:
            body["tags"] = request.tags
        if request.source is not None:
            body["source"] = request.source

        response = await self._client.post(self._base_url, json=body, headers=headers, params=params)
        response.raise_for_status()
        return TaskInfo.from_dict(response.json())

    async def get(self, task_id: str) -> TaskInfo | None:
        """Get a task by ID via GET /storage/tasks/{id}.

        :param task_id: The task identifier.
        :type task_id: str
        :return: The task record, or ``None`` if not found.
        :rtype: TaskInfo | None
        """
        headers = await self._get_headers()
        response = await self._client.get(
            f"{self._base_url}/{task_id}",
            headers=headers,
            params={"api-version": _API_VERSION},
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return TaskInfo.from_dict(response.json())

    async def update(self, task_id: str, patch: TaskPatchRequest) -> TaskInfo:
        """Update a task via PATCH /storage/tasks/{id}.

        :param task_id: The task identifier.
        :type task_id: str
        :param patch: Fields to update.
        :type patch: TaskPatchRequest
        :return: The updated task record.
        :rtype: TaskInfo
        :raises TaskNotFound: If the task does not exist.
        """
        headers = await self._get_headers()
        params: dict[str, str] = {"api-version": _API_VERSION}
        if patch.lease_owner is not None:
            params["lease_owner"] = patch.lease_owner
        if patch.lease_instance_id is not None:
            params["lease_instance_id"] = patch.lease_instance_id
        if patch.lease_duration_seconds is not None:
            params["lease_duration_seconds"] = str(patch.lease_duration_seconds)

        body: dict[str, Any] = {}
        if patch.status is not None:
            body["status"] = patch.status
        if patch.payload is not None:
            body["payload"] = patch.payload
        if patch.tags is not None:
            body["tags"] = patch.tags
        if patch.error is not None:
            body["error"] = patch.error
        if patch.suspension_reason is not None:
            body["suspension_reason"] = patch.suspension_reason

        if patch.if_match is not None:
            headers["If-Match"] = f'"{patch.if_match}"'

        response = await self._client.patch(
            f"{self._base_url}/{task_id}",
            json=body,
            headers=headers,
            params=params,
        )
        if response.status_code == 404:
            raise TaskNotFound(task_id)
        response.raise_for_status()
        return TaskInfo.from_dict(response.json())

    async def delete(
        self,
        task_id: str,
        *,
        force: bool = False,
        cascade: bool = False,
    ) -> None:
        """Delete a task via DELETE /storage/tasks/{id}.

        :param task_id: The task identifier.
        :type task_id: str
        :keyword force: Release active lease before deleting.
        :paramtype force: bool
        :keyword cascade: Delete dependent tasks.
        :paramtype cascade: bool
        """
        headers = await self._get_headers()
        params: dict[str, str] = {"api-version": _API_VERSION}
        if force:
            params["force"] = "true"
        if cascade:
            params["cascade"] = "true"

        response = await self._client.delete(
            f"{self._base_url}/{task_id}",
            headers=headers,
            params=params,
        )
        if response.status_code == 404:
            raise TaskNotFound(task_id)
        response.raise_for_status()

    async def list(
        self,
        *,
        agent_name: str,
        session_id: str,
        status: TaskStatus | None = None,
        lease_owner: str | None = None,
    ) -> list[TaskInfo]:
        """List tasks via GET /storage/tasks.

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
        headers = await self._get_headers()
        params: dict[str, str] = {
            "api-version": _API_VERSION,
            "agent_name": agent_name,
            "session_id": session_id,
        }
        if status is not None:
            params["status"] = status
        if lease_owner is not None:
            params["lease_owner"] = lease_owner

        response = await self._client.get(self._base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        items: list[dict[str, Any]] = data.get("data", data.get("items", []))
        return [TaskInfo.from_dict(item) for item in items]

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
