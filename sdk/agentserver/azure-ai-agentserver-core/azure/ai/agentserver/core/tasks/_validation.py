# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared field validation for the resilient-task primitive.

Both the hosted and local providers MUST enforce the same input
validation rules so a developer running locally observes the same
accept / reject decisions they would observe deployed against the
hosted service. This module is the single source of truth for those
rules — used by ``LocalFileTaskProvider`` to reject pre-write and by
the framework-side construction code in ``_decorator.py`` /
``_run.py`` to fail fast before any provider call.

Spec source: ``docs/task-and-streaming-spec.md`` §28a + §22.1 + §23.9
+ §24 + C-VAL / C-LSE / C-ATT / C-LCM conformance items.
"""

from __future__ import annotations

import json
import re
from typing import Any, NoReturn

from ._exceptions_internal import _HostedConflict


# ── Regex patterns (per §28a.1 / §23.9) ──────────────────────────────

_TASK_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")
_TAG_KEY_RE = re.compile(r"^[a-zA-Z0-9_.\-]{1,64}$")
_ATTACHMENT_KEY_RE = re.compile(r"^[a-zA-Z0-9_.\-]{1,64}$")


# ── Length / count / size caps (per §28a.1, §28a.2, §23.7) ──────────

MAX_AGENT_NAME_LEN = 128
MAX_SESSION_ID_LEN = 128
MAX_TITLE_LEN = 256
MAX_DESCRIPTION_LEN = 1024
MAX_SUSPENSION_REASON_LEN = 256
MAX_TAG_VALUE_LEN = 256
MAX_TAG_ENTRIES = 16
MAX_PAYLOAD_BYTES = 1024 * 1024  # 1 MB
MAX_ERROR_BYTES = 64 * 1024  # 64 KB
MAX_SOURCE_BYTES = 4 * 1024  # 4 KB
MAX_ATTACHMENT_VALUE_BYTES = 10 * 1024 * 1024  # 10 MiB (also enforced in _attachments)
MAX_ATTACHMENT_ENTRIES = 20  # (also enforced in _attachments)
MAX_LEASE_IDENTITY_LEN = 256

# ── Lease duration bounds (per §22.1 LSE-W-1) ────────────────────────

LEASE_DURATION_MIN = 10
LEASE_DURATION_MAX = 3600


# ── Allowed status values + state-transition matrix (per §24, §24.1) ─

_LEGAL_STATUSES = {"pending", "in_progress", "suspended", "completed"}
_LEGACY_STATUS_ALIASES = {"done": "completed"}  # §28a.5

_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"in_progress", "completed"},
    "in_progress": {"pending", "in_progress", "suspended", "completed"},
    "suspended": {"pending", "in_progress", "suspended", "completed"},
    # 'completed' MUST be terminal except no-op completed→completed
    # without other field changes (see §24.2 — checked at the call site,
    # not in the matrix alone).
    "completed": {"completed"},
}

# Fields that MUST NOT appear in a PATCH body (§28a.6 / §24).
IMMUTABLE_PATCH_FIELDS = frozenset({"id", "agent_name", "session_id", "title", "description", "source"})


# ── Helpers ──────────────────────────────────────────────────────────


def _reject(code: str, message: str) -> NoReturn:
    """Raise an ``invalid_request``-coded :class:`_HostedConflict`.

    All validation rejections funnel through here so the wire-status
    and code are uniform. The framework's translation layer converts
    this to the developer-facing :class:`TaskPreconditionFailed`.

    :param code: The wire error code to attach to the conflict.
    :type code: str
    :param message: The human-readable rejection message.
    :type message: str
    """
    raise _HostedConflict(_code=code, status_code=400, message=message)


def _canonical_json_bytes(value: Any) -> int:
    """Return the UTF-8 byte length of ``value`` serialized as canonical JSON.

    Canonicalization matches the service's measurement:
    ``sort_keys=True`` + compact separators (no whitespace).

    :param value: The value to measure as canonical JSON.
    :type value: Any
    :return: The UTF-8 byte length of the canonical-JSON encoding.
    :rtype: int
    """
    return len(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def normalize_legacy_status(status: str | None) -> str | None:
    """Map legacy status aliases to canonical values (§28a.5).

    :param status: The status to normalize, or None.
    :type status: str | None
    :return: The canonical status, or None when ``status`` is None.
    :rtype: str | None
    """
    if status is None:
        return None
    return _LEGACY_STATUS_ALIASES.get(status, status)


# ── Validators (called by both providers) ────────────────────────────


def validate_task_id(task_id: str) -> None:
    """C-VAL-1: task id MUST match ``^[a-zA-Z0-9_-]{1,128}$``.

    :param task_id: The task id to validate.
    :type task_id: str
    """
    if not task_id or not _TASK_ID_RE.match(task_id):
        _reject(
            "invalid_request",
            "id must match [a-zA-Z0-9_-] and be 128 characters or fewer.",
        )


def validate_required_string(value: str | None, field_name: str, max_len: int) -> None:
    """C-VAL-2 / §28a.1: a required string field is non-empty after trim
    and at or under ``max_len``.

    :param value: The field value to validate.
    :type value: str | None
    :param field_name: The field name used in rejection messages.
    :type field_name: str
    :param max_len: The maximum allowed length.
    :type max_len: int
    """
    if value is None or not value.strip():
        _reject("invalid_request", f"{field_name} must be provided.")
    if len(value.strip()) > max_len:
        _reject(
            "invalid_request",
            f"{field_name} exceeds the maximum allowed length of {max_len}.",
        )


def validate_optional_string(value: str | None, field_name: str, max_len: int) -> None:
    """§28a.1: an optional string field, when present, is at or under ``max_len``.

    :param value: The field value to validate, or None.
    :type value: str | None
    :param field_name: The field name used in rejection messages.
    :type field_name: str
    :param max_len: The maximum allowed length.
    :type max_len: int
    """
    if value is None:
        return
    if len(value.strip()) > max_len:
        _reject(
            "invalid_request",
            f"{field_name} exceeds the maximum allowed length of {max_len}.",
        )


def validate_tags(tags: dict[str, Any] | None) -> None:
    """C-VAL-5: tag key regex, value length, total entry count.

    :param tags: The tags mapping to validate, or None.
    :type tags: dict[str, Any] | None
    """
    if tags is None:
        return
    if len(tags) > MAX_TAG_ENTRIES:
        _reject(
            "invalid_request",
            f"tags must contain {MAX_TAG_ENTRIES} entries or fewer.",
        )
    for key, value in tags.items():
        if not _TAG_KEY_RE.match(key or ""):
            _reject(
                "invalid_request",
                "tag keys must match [a-zA-Z0-9_.-] and be 64 characters or fewer.",
            )
        # null-as-delete (PATCH) — value None is meaningful, skip length check
        if value is None:
            continue
        if not isinstance(value, str):
            _reject("invalid_request", "tag values must be strings or null.")
        if len(value) > MAX_TAG_VALUE_LEN:
            _reject(
                "invalid_request",
                f"tag values must be {MAX_TAG_VALUE_LEN} characters or fewer.",
            )


def validate_payload_size(payload: Any) -> None:
    """C-VAL-6: payload canonical-JSON byte count ≤ 1 MB.

    :param payload: The payload to measure and validate.
    :type payload: Any
    """
    if payload is None:
        return
    if _canonical_json_bytes(payload) > MAX_PAYLOAD_BYTES:
        _reject(
            "invalid_request",
            f"payload exceeds the maximum allowed size of {MAX_PAYLOAD_BYTES} bytes.",
        )


def validate_error(error: dict[str, Any] | None) -> None:
    """C-VAL-6 / C-VAL-8: error JSON ≤ 64 KB; required message + type.

    :param error: The error object to validate, or None.
    :type error: dict[str, Any] | None
    """
    if error is None:
        return
    if not isinstance(error, dict):
        _reject("invalid_request", "error must be an object.")
    if _canonical_json_bytes(error) > MAX_ERROR_BYTES:
        _reject(
            "invalid_request",
            f"error exceeds the maximum allowed size of {MAX_ERROR_BYTES} bytes.",
        )
    msg = error.get("message")
    if not isinstance(msg, str) or not msg.strip():
        _reject("invalid_request", "error.message must be a non-empty string.")
    typ = error.get("type")
    if not isinstance(typ, str) or not typ.strip():
        _reject("invalid_request", "error.type must be a non-empty string.")


def normalize_error(error: dict[str, Any] | None) -> dict[str, Any] | None:
    """C-VAL-8: error PATCH defaults ``code`` to ``"error"`` if missing.
    Returns the canonicalized dict (a copy with defaults applied).

    :param error: The error object to canonicalize, or None.
    :type error: dict[str, Any] | None
    :return: The canonicalized error dict, or None when ``error`` is None.
    :rtype: dict[str, Any] | None
    """
    if error is None:
        return None
    out = dict(error)
    if not out.get("code"):
        out["code"] = "error"
    return out


def validate_source(source: dict[str, Any] | None) -> None:
    """C-VAL-6 / C-VAL-7: source ≤ 4 KB and has non-empty ``type``.

    :param source: The source object to validate, or None.
    :type source: dict[str, Any] | None
    """
    if source is None:
        return
    if not isinstance(source, dict):
        _reject("invalid_request", "source must be an object.")
    if _canonical_json_bytes(source) > MAX_SOURCE_BYTES:
        _reject(
            "invalid_request",
            f"source exceeds the maximum allowed size of {MAX_SOURCE_BYTES} bytes.",
        )
    src_type = source.get("type")
    if not isinstance(src_type, str) or not src_type.strip():
        _reject("invalid_request", "source.type must be a non-empty string.")


def validate_attachment_key(key: str) -> None:
    """C-ATT-8: attachment keys MUST match the regex; non-empty after trim.

    :param key: The attachment key to validate.
    :type key: str
    """
    if not key or not key.strip() or not _ATTACHMENT_KEY_RE.match(key.strip()):
        _reject(
            "invalid_request",
            "attachment keys must match [a-zA-Z0-9_.-] and be 64 characters or fewer.",
        )


def validate_attachment_keys(attachments: dict[str, Any] | None) -> None:
    """Validate every key in an attachments dict.

    :param attachments: The attachments mapping whose keys to validate.
    :type attachments: dict[str, Any] | None
    """
    if not attachments:
        return
    for key in attachments.keys():
        validate_attachment_key(key)


def validate_create_status(status: str | None) -> str:
    """Normalize + validate the ``status`` field on CREATE.

    Per §24 / C-LCM-1: only ``pending`` or ``in_progress`` are allowed on
    create. Empty/None defaults to ``pending``. ``"done"`` normalizes
    to ``"completed"`` but is then rejected (create→completed is not
    allowed). ``"failed"`` is rejected outright per §28a.5.

    :param status: The requested create status, or None.
    :type status: str | None
    :return: The normalized, validated status.
    :rtype: str
    """
    status = (status or "pending").strip().lower()
    if status == "failed":
        _reject(
            "invalid_request",
            "Unsupported status 'failed'. Represent failures as completed tasks with a non-null error.",
        )
    normalized = _LEGACY_STATUS_ALIASES.get(status, status)
    if normalized not in {"pending", "in_progress"}:
        _reject("invalid_request", "status on create must be pending or in_progress.")
    return normalized


def validate_patch_status(status: str | None) -> str | None:
    """Normalize + validate the ``status`` field on PATCH.

    Per §24 / C-VAL-9. ``"failed"`` rejected, ``"done"`` normalized.
    Returns the normalized status (or None when not patching status).

    :param status: The requested patch status, or None.
    :type status: str | None
    :return: The normalized status, or None when not patching status.
    :rtype: str | None
    """
    if status is None:
        return None
    status = status.strip().lower()
    if status == "failed":
        _reject(
            "invalid_request",
            "Unsupported status 'failed'. Represent failures as completed tasks with a non-null error.",
        )
    normalized = _LEGACY_STATUS_ALIASES.get(status, status)
    if normalized not in _LEGAL_STATUSES:
        _reject("invalid_request", f"Unsupported status '{status}'.")
    return normalized


def validate_transition(current: str, target: str) -> None:
    """C-LCM-5: enforce the §24.1 transition matrix.

    :param current: The current task status.
    :type current: str
    :param target: The requested target status.
    :type target: str
    """
    current = normalize_legacy_status(current) or current
    target = normalize_legacy_status(target) or target
    allowed = _ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        # invalid_state_transition is technically a 409 per §39.1 but
        # the framework treats it as a framework bug. Use the proper
        # code; translation step handles the rest.
        raise _HostedConflict(
            _code="invalid_state_transition",
            status_code=409,
            message=f"Cannot transition task from '{current}' to '{target}'.",
        )


def validate_lease_params(
    owner: str | None,
    instance_id: str | None,
    duration_seconds: int | None,
) -> tuple[str, str, int] | None:
    """C-LSE-6 / C-LSE-7: all-or-nothing triplet, duration bounds.

    Returns the normalized triplet when all three are supplied, ``None``
    when none are supplied. Raises ``_HostedConflict`` when partial.

    :param owner: The lease owner, or None.
    :type owner: str | None
    :param instance_id: The lease instance id, or None.
    :type instance_id: str | None
    :param duration_seconds: The lease duration in seconds, or None.
    :type duration_seconds: int | None
    :return: The normalized triplet when all three are supplied, else None.
    :rtype: tuple[str, str, int] | None
    """
    any_set = bool(owner) or bool(instance_id) or duration_seconds is not None
    all_set = bool(owner) and bool(instance_id) and duration_seconds is not None
    if any_set and not all_set:
        _reject(
            "invalid_request",
            "lease_owner, lease_instance_id, and lease_duration_seconds must be provided together.",
        )
    if not all_set:
        return None
    assert owner is not None and instance_id is not None  # type narrowing
    assert duration_seconds is not None
    if duration_seconds != 0 and not LEASE_DURATION_MIN <= duration_seconds <= LEASE_DURATION_MAX:
        _reject(
            "invalid_request",
            f"lease_duration_seconds must be 0 or between {LEASE_DURATION_MIN} and {LEASE_DURATION_MAX}.",
        )
    if len(owner) > MAX_LEASE_IDENTITY_LEN:
        _reject(
            "invalid_request",
            f"lease_owner exceeds the maximum allowed length of " f"{MAX_LEASE_IDENTITY_LEN}.",
        )
    if len(instance_id) > MAX_LEASE_IDENTITY_LEN:
        _reject(
            "invalid_request",
            f"lease_instance_id exceeds the maximum allowed length of " f"{MAX_LEASE_IDENTITY_LEN}.",
        )
    return (owner.strip(), instance_id.strip(), duration_seconds)
