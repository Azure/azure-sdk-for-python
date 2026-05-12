# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Internal data models for the durable task subsystem.

These types represent wire-level task records and request/response shapes
used by providers. They are **not** part of the public API.
"""

from __future__ import annotations

from typing import Any, Literal

TaskStatus = Literal["pending", "in_progress", "suspended", "completed"]
"""Valid task status values."""


class LeaseInfo:
    """Lease details on a task record.

    :param owner: Stable lease owner (e.g. ``"session:sess_abc"``).
    :type owner: str
    :param instance_id: Ephemeral per-process instance identifier.
    :type instance_id: str
    :param generation: Fencing token — increments on re-acquisition.
    :type generation: int
    :param expires_at: ISO 8601 expiry timestamp.
    :type expires_at: str
    :param expiry_count: Number of times ownership changed via expiry.
    :type expiry_count: int
    """

    __slots__ = ("owner", "instance_id", "generation", "expires_at", "expiry_count")

    def __init__(
        self,
        owner: str,
        instance_id: str,
        generation: int,
        expires_at: str,
        expiry_count: int = 0,
    ) -> None:
        self.owner = owner
        self.instance_id = instance_id
        self.generation = generation
        self.expires_at = expires_at
        self.expiry_count = expiry_count

    def __repr__(self) -> str:
        return (
            f"LeaseInfo(owner={self.owner!r}, instance_id={self.instance_id!r}, "
            f"generation={self.generation!r}, expires_at={self.expires_at!r}, "
            f"expiry_count={self.expiry_count!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LeaseInfo):
            return NotImplemented
        return (
            self.owner == other.owner
            and self.instance_id == other.instance_id
            and self.generation == other.generation
            and self.expires_at == other.expires_at
            and self.expiry_count == other.expiry_count
        )


class TaskInfo:
    """Internal representation of a task record from the store.

    :param id: Unique task identifier.
    :type id: str
    :param agent_name: Agent scope.
    :type agent_name: str
    :param session_id: Session scope.
    :type session_id: str
    :param status: Current task status.
    :type status: TaskStatus
    :param title: Human-readable title.
    :type title: str | None
    :param description: Optional description.
    :type description: str | None
    :param lease: Active lease details, or ``None``.
    :type lease: LeaseInfo | None
    :param payload: Arbitrary JSON payload (input, metadata, output buckets).
    :type payload: dict[str, Any] | None
    :param tags: Key-value tags.
    :type tags: dict[str, str] | None
    :param error: Structured error details on failure.
    :type error: dict[str, Any] | None
    :param suspension_reason: Reason for suspension.
    :type suspension_reason: str | None
    :param etag: Optimistic concurrency token.
    :type etag: str
    :param created_at: ISO 8601 creation timestamp.
    :type created_at: str
    :param updated_at: ISO 8601 last-update timestamp.
    :type updated_at: str
    :param started_at: ISO 8601 timestamp of first ``in_progress`` transition.
    :type started_at: str | None
    :param completed_at: ISO 8601 timestamp of ``completed`` transition.
    :type completed_at: str | None
    """

    __slots__ = (
        "id",
        "agent_name",
        "session_id",
        "status",
        "title",
        "description",
        "lease",
        "payload",
        "tags",
        "error",
        "suspension_reason",
        "etag",
        "created_at",
        "updated_at",
        "started_at",
        "completed_at",
        "source",
    )

    def __init__(
        self,
        id: str,  # noqa: A002
        agent_name: str,
        session_id: str,
        status: TaskStatus,
        title: str | None = None,
        description: str | None = None,
        lease: LeaseInfo | None = None,
        payload: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        error: dict[str, Any] | None = None,
        suspension_reason: str | None = None,
        etag: str = "",
        created_at: str = "",
        updated_at: str = "",
        started_at: str | None = None,
        completed_at: str | None = None,
        source: dict[str, Any] | None = None,
    ) -> None:
        self.id = id
        self.agent_name = agent_name
        self.session_id = session_id
        self.status = status
        self.title = title
        self.description = description
        self.lease = lease
        self.payload = payload
        self.tags = tags
        self.error = error
        self.suspension_reason = suspension_reason
        self.etag = etag
        self.created_at = created_at
        self.updated_at = updated_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.source = source

    def __repr__(self) -> str:
        return f"TaskInfo(id={self.id!r}, status={self.status!r}, agent_name={self.agent_name!r})"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskInfo:
        """Construct a :class:`TaskInfo` from a JSON-decoded dict.

        :param data: Dictionary as returned by the Task Storage API.
        :type data: dict[str, Any]
        :return: A populated TaskInfo instance.
        :rtype: TaskInfo
        """
        lease_data = data.get("lease")
        lease = (
            LeaseInfo(
                owner=lease_data["owner"],
                instance_id=lease_data["instance_id"],
                generation=lease_data.get("generation", 0),
                expires_at=lease_data.get("expires_at", ""),
                expiry_count=lease_data.get("expiry_count", 0),
            )
            if lease_data
            else None
        )
        return cls(
            id=data["id"],
            agent_name=data.get("agent_name", ""),
            session_id=data.get("session_id", ""),
            status=data.get("status", "pending"),
            title=data.get("title"),
            description=data.get("description"),
            lease=lease,
            payload=data.get("payload"),
            tags=data.get("tags"),
            error=data.get("error"),
            suspension_reason=data.get("suspension_reason"),
            etag=data.get("etag", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            source=data.get("source"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary.

        :return: Dictionary suitable for JSON serialization.
        :rtype: dict[str, Any]
        """
        result: dict[str, Any] = {
            "object": "task",
            "id": self.id,
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "status": self.status,
        }
        if self.title is not None:
            result["title"] = self.title
        if self.description is not None:
            result["description"] = self.description
        if self.lease is not None:
            result["lease"] = {
                "owner": self.lease.owner,
                "instance_id": self.lease.instance_id,
                "generation": self.lease.generation,
                "expires_at": self.lease.expires_at,
                "expiry_count": self.lease.expiry_count,
            }
        else:
            result["lease"] = None
        if self.payload is not None:
            result["payload"] = self.payload
        if self.tags is not None:
            result["tags"] = self.tags
        if self.error is not None:
            result["error"] = self.error
        if self.suspension_reason is not None:
            result["suspension_reason"] = self.suspension_reason
        if self.source is not None:
            result["source"] = self.source
        result["etag"] = self.etag
        result["created_at"] = self.created_at
        result["updated_at"] = self.updated_at
        result["started_at"] = self.started_at
        result["completed_at"] = self.completed_at
        return result


class TaskCreateRequest:
    """Request body for creating a task.

    :param agent_name: Agent scope.
    :type agent_name: str
    :param session_id: Session scope.
    :type session_id: str
    :param status: Initial status (``"pending"`` or ``"in_progress"``).
    :type status: TaskStatus
    :param id: Optional client-supplied task ID.
    :type id: str | None
    :param title: Human-readable title.
    :type title: str | None
    :param description: Optional description.
    :type description: str | None
    :param payload: Initial payload (input bucket).
    :type payload: dict[str, Any] | None
    :param tags: Initial tags.
    :type tags: dict[str, str] | None
    :param lease_owner: Required when ``status`` is ``"in_progress"``.
    :type lease_owner: str | None
    :param lease_instance_id: Required when ``status`` is ``"in_progress"``.
    :type lease_instance_id: str | None
    :param lease_duration_seconds: Lease TTL. Required with lease params.
    :type lease_duration_seconds: int | None
    """

    __slots__ = (
        "agent_name",
        "session_id",
        "status",
        "id",
        "title",
        "description",
        "payload",
        "tags",
        "source",
        "lease_owner",
        "lease_instance_id",
        "lease_duration_seconds",
    )

    def __init__(
        self,
        agent_name: str,
        session_id: str,
        status: TaskStatus = "pending",
        id: str | None = None,  # noqa: A002
        title: str | None = None,
        description: str | None = None,
        payload: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        source: dict[str, Any] | None = None,
        lease_owner: str | None = None,
        lease_instance_id: str | None = None,
        lease_duration_seconds: int | None = None,
    ) -> None:
        self.agent_name = agent_name
        self.session_id = session_id
        self.status = status
        self.id = id
        self.title = title
        self.description = description
        self.payload = payload
        self.tags = tags
        self.source = source
        self.lease_owner = lease_owner
        self.lease_instance_id = lease_instance_id
        self.lease_duration_seconds = lease_duration_seconds


class TaskPatchRequest:
    """Request body for patching a task.

    Only non-``None`` fields are included in the PATCH payload.

    :param status: New status.
    :type status: TaskStatus | None
    :param payload: Payload patch (shallow-merge semantics).
    :type payload: dict[str, Any] | None
    :param tags: Tags patch (null-as-delete merge).
    :type tags: dict[str, str] | None
    :param error: Structured error (on failure).
    :type error: dict[str, Any] | None
    :param suspension_reason: Reason for suspension.
    :type suspension_reason: str | None
    :param lease_owner: Lease owner for transitions.
    :type lease_owner: str | None
    :param lease_instance_id: Lease instance for transitions.
    :type lease_instance_id: str | None
    :param lease_duration_seconds: Lease TTL override.
    :type lease_duration_seconds: int | None
    :param if_match: ETag for optimistic concurrency.
    :type if_match: str | None
    """

    __slots__ = (
        "status",
        "payload",
        "tags",
        "error",
        "suspension_reason",
        "lease_owner",
        "lease_instance_id",
        "lease_duration_seconds",
        "if_match",
    )

    def __init__(
        self,
        status: TaskStatus | None = None,
        payload: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        error: dict[str, Any] | None = None,
        suspension_reason: str | None = None,
        lease_owner: str | None = None,
        lease_instance_id: str | None = None,
        lease_duration_seconds: int | None = None,
        if_match: str | None = None,
    ) -> None:
        self.status = status
        self.payload = payload
        self.tags = tags
        self.error = error
        self.suspension_reason = suspension_reason
        self.lease_owner = lease_owner
        self.lease_instance_id = lease_instance_id
        self.lease_duration_seconds = lease_duration_seconds
        self.if_match = if_match
