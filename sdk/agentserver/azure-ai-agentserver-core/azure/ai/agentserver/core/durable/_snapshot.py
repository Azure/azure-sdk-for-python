# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Public ``TaskSnapshot`` type returned by ``Task.get(task_id)``.

Spec 019 FR-C-002 / §35a — a read-only, frozen value object that
exposes only the documented developer-facing fields of a persisted
task record. Framework-internal slots (``lease``, ``etag``, ``tags``,
``source``, ``attachments``, ``_steering``-prefixed payload keys,
etc.) are intentionally NOT projected onto the snapshot.

Constructed via :meth:`TaskSnapshot.from_task_info` so the framework
controls the projection in one place; callers do not instantiate
this directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from ._attachments import _OUTPUT_KEY, _is_ref, _read_input_value

if TYPE_CHECKING:
    from ._models import TaskInfo, TaskStatus

Output = TypeVar("Output")


@dataclass(frozen=True)
class TaskSnapshot(Generic[Output]):
    """Read-only point-in-time view of any non-deleted task.

    Returned by :meth:`Task.get`. The instance reflects the record at
    the moment ``Task.get`` was called; re-call to refresh.

    Spec 019 FR-C-002 / C-INTROSPECT-1..8 — the public field set is
    fixed; framework-internal storage details (lease, etag, raw
    payload, raw attachments, source, tags, ``_``-prefixed payload
    keys) are deliberately excluded.

    :ivar task_id: The persisted task id.
    :ivar status: The four-value stored status
        (``pending`` / ``in_progress`` / ``suspended`` / ``completed``).
    :ivar created_at: Server-stamped record-creation time.
    :ivar updated_at: Server-stamped last-PATCH time.
    :ivar started_at: Time the first turn entered ``in_progress``;
        ``None`` while still ``pending``.
    :ivar completed_at: Time the record transitioned to terminal
        ``completed``; ``None`` for non-terminal statuses.
    :ivar output: The resolved output value (handler return,
        ``ctx.suspend(output=X)`` value, or ``None``). Promoted
        ``_output`` attachments are followed transparently — the
        developer sees the typed value, not the ref.
    :ivar error: Structured error info for failed terminations
        (``{"type": ..., "message": ..., ...}``); ``None`` otherwise.
    :ivar suspension_reason: The ``reason=`` argument from the last
        ``ctx.suspend()`` call; ``None`` unless status is
        ``suspended``.
    :ivar metadata: The default-namespace metadata only. Named
        namespaces are NOT surfaced on the snapshot.
    :ivar lease_expiry_count: Current expiry counter; ``0`` unless
        the lease has expired at least once.
    """

    task_id: str
    status: "TaskStatus"
    created_at: datetime | None
    updated_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    output: Output | None
    error: dict[str, Any] | None
    suspension_reason: str | None
    metadata: dict[str, Any]
    lease_expiry_count: int

    @classmethod
    def from_task_info(cls, info: "TaskInfo") -> "TaskSnapshot[Any]":
        """Project a :class:`TaskInfo` record onto a public snapshot.

        Resolves any promoted ``_output`` attachment via
        :func:`_read_input_value`. Surfaces only the default-namespace
        metadata (the canonical, always-present namespace). Strips
        every framework-internal field per FR-C-002.
        """
        payload = info.payload or {}
        attachments = info.attachments
        output_slot = payload.get("output")
        if output_slot is None:
            resolved_output: Any = None
        elif _is_ref(output_slot):
            try:
                resolved_output = _read_input_value(output_slot, attachments)
            except KeyError:
                # Ref points at a missing attachment — surface None
                # rather than raising, since the snapshot is best-effort
                # read-only introspection. Operators can diagnose via
                # the framework's structured logs.
                resolved_output = None
        else:
            resolved_output = output_slot

        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}

        return cls(
            task_id=info.id,
            status=info.status,
            created_at=_parse_iso(info.created_at),
            updated_at=_parse_iso(info.updated_at),
            started_at=_parse_iso(info.started_at),
            completed_at=_parse_iso(info.completed_at),
            output=resolved_output,
            error=info.error,
            suspension_reason=info.suspension_reason,
            metadata=dict(metadata),
            lease_expiry_count=(info.lease.expiry_count if info.lease else 0),
        )


def _parse_iso(value: Any) -> datetime | None:
    """Best-effort ISO-8601 parser for snapshot timestamps."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        # Python's fromisoformat handles offsets like "+00:00" on 3.11+;
        # tolerate trailing "Z" for hosted-server emissions.
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


# Use _OUTPUT_KEY indirectly to avoid an unused-import warning when this
# module is consumed via __init__'s re-export. The constant participates
# in the design-spec narrative (FR-C-003 / FR-C-005) tying snapshot
# resolution to the framework-reserved attachment key.
_OUTPUT_KEY_RECORDED = _OUTPUT_KEY
