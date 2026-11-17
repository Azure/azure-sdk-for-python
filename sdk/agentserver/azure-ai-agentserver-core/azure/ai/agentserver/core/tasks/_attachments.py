# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Task attachments support.

Helpers for the input-promotion mechanism that lets the resilient
primitive support per-input payloads up to 10 MiB by spilling oversized
inputs into ``task.attachments`` (decoupled from the shared 1 MB
``task.payload`` budget). See `the SOT spec`
for the authoritative wire contract and `the SOT spec`
for the speckit-flow spec.

This module exports:

- Tunables / constants (``_INPUT_THRESHOLD_BYTES``,
  ``_STEERING_THRESHOLD_BYTES``, ``_MAX_ATTACHMENT_SIZE_BYTES``,
  ``_MAX_ATTACHMENTS``, ``_STEERING_QUEUE_CAP``,
  ``_FUNCTION_INPUT_KEY``, ``_STEERING_INPUT_KEY_PREFIX``).
- Hash helper: :func:`_compute_attachment_hash`.
- Ref helpers: :func:`_make_ref`, :func:`_is_ref`, :func:`_ref_key`,
  :func:`_ref_hash`.
- Promotion router: :func:`_resolve_input_storage`.
- Backward-compat-NOT-needed read: :func:`_read_input_value`.
- Size enforcement: :func:`_validate_attachment_size`,
  :func:`_validate_attachment_count`.

All names are underscore-prefixed (framework-private); promotion is
invisible to handler authors.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ._exceptions import (
    InputTooLarge,
    OutputTooLarge,
    _AttachmentLimitExceeded,
    _AttachmentTooLarge,
)

# --------------------------------------------------------------------------- #
# Wire shape constants
# --------------------------------------------------------------------------- #

#: The single magic key whose value is the ref's nested object. A payload
#: slot or queue entry that is a 1-key dict with this key is a ref;
#: anything else is treated as inline. See spec.md §4.3.
_ATTACHMENT_REF_KEY = "__attachment_ref__"

#: The framework-reserved attachment key for the function input.
_FUNCTION_INPUT_KEY = "input"

#: The framework-reserved attachment-key prefix for queued steering inputs.
#: The full key is ``f"{prefix}{seq}"`` where ``seq`` is the monotonic
#: counter from ``payload["steering"]["next_input_seq"]``.
_STEERING_INPUT_KEY_PREFIX = "steering_input_"

#:   — framework-reserved attachment key for the
#: per-turn output value. Output is ALWAYS stored via this attachment
#: (no inline threshold) so it never consumes payload budget.
_OUTPUT_KEY = "output"

#: Hash algorithm prefix (RFC-6920-style namespacing). The value after the
#: ``:`` is the lowercase-hex digest. Prefix lets us migrate to a different
#: algorithm in the future without ambiguity.
_HASH_ALGO_PREFIX = "sha256:"

# --------------------------------------------------------------------------- #
# Size + count caps (authoritative reference: task-attachments.md §2.4 + §3)
# --------------------------------------------------------------------------- #

#: Function input promotion threshold (200 KiB). Inputs whose serialized
#: form exceeds this are promoted to ``attachments["input"]``.
_INPUT_THRESHOLD_BYTES = 200 * 1024

#: Steering input promotion threshold (20 KiB). Inputs whose serialized
#: form exceeds this are promoted to
#: ``attachments["_steering_input_<seq>"]``.
_STEERING_THRESHOLD_BYTES = 20 * 1024

#: Per-attachment value cap (10 MiB). Server-side hard cap; enforced
#: client-side via :class:`InputTooLarge` (developer-facing) /
#: :class:`_AttachmentTooLarge` (provider-internal; see
#: :func:`_remap_attachment_error`) before any HTTP call.
_MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024

#: Per-task attachment-entry cap. Server-side hard cap; enforced
#: client-side via :class:`_AttachmentLimitExceeded` (provider-internal).
_MAX_ATTACHMENTS = 20

#: Framework's steering queue hard cap. At most this many entries can be
#: queued (whether inline or refs). The 10th append raises
#: :class:`~._exceptions.SteeringQueueFull`. Combined with the 1 reserved
#: slot for the function input, the framework uses at most 10 of the 20
#: attachment slots; the other 10 remain free for future features.
_STEERING_QUEUE_CAP = 9


# --------------------------------------------------------------------------- #
# Hash helper
# --------------------------------------------------------------------------- #


def _compute_attachment_hash(serialized: Any) -> str:
    """Compute the content hash of a serialized attachment value.

    The value is re-serialized to canonical JSON bytes
    (``sort_keys=True``, no whitespace, separators ``(",", ":")``) and
    hashed with SHA-256. The output is prefixed with ``"sha256:"`` so a
    future migration to a different algorithm is unambiguous.

    :param serialized: The JSON-compatible value (already framework-
        serialized via ``_serialize_input``).
    :type serialized: Any
    :return: ``"sha256:<64 lowercase hex chars>"``.
    :rtype: str
    """
    raw = json.dumps(serialized, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{_HASH_ALGO_PREFIX}{digest}"


# --------------------------------------------------------------------------- #
# Ref helpers
# --------------------------------------------------------------------------- #


def _make_ref(key: str, serialized: Any) -> dict[str, dict[str, str]]:
    """Build a self-contained ref slot for the given attachment.

    Shape::

        {"__attachment_ref__": {"key": "<key>", "hash": "sha256:..."}}

    :param key: The attachment key the ref points at.
    :type key: str
    :param serialized: The attachment value (used to compute the content hash).
    :type serialized: Any
    :return: The ref slot dict.
    :rtype: dict
    """
    return {
        _ATTACHMENT_REF_KEY: {
            "key": key,
            "hash": _compute_attachment_hash(serialized),
        }
    }


def _is_ref(slot: Any) -> bool:
    """Return True iff *slot* is the strict ref shape.

    A slot is a ref iff ALL of:

    1. It is a ``dict``.
    2. It has exactly one top-level key.
    3. The sole key is :data:`_ATTACHMENT_REF_KEY`.
    4. The value is itself a ``dict`` containing both ``"key"`` and ``"hash"``.

    Anything else (raw values, dicts shaped differently, other types) is
    treated as inline.

    :param slot: The candidate slot.
    :type slot: Any
    :return: True iff *slot* is the strict ref shape.
    :rtype: bool
    """
    if not isinstance(slot, dict):
        return False
    if len(slot) != 1:
        return False
    nested = slot.get(_ATTACHMENT_REF_KEY)
    if not isinstance(nested, dict):
        return False
    return "key" in nested and "hash" in nested


def _ref_key(slot: dict[str, dict[str, str]]) -> str:
    """Return the attachment key carried by a ref slot.

    Caller MUST have validated the slot with :func:`_is_ref` first.

    :param slot: A ref slot (output of :func:`_make_ref`).
    :type slot: dict[str, dict[str, str]]
    :return: The attachment key string.
    :rtype: str
    """
    return slot[_ATTACHMENT_REF_KEY]["key"]


def _ref_hash(slot: dict[str, dict[str, str]]) -> str:
    """Return the content hash carried by a ref slot.

    Caller MUST have validated the slot with :func:`_is_ref` first.

    :param slot: A ref slot (output of :func:`_make_ref`).
    :type slot: dict[str, dict[str, str]]
    :return: The ``"sha256:<hex>"`` hash string.
    :rtype: str
    """
    return slot[_ATTACHMENT_REF_KEY]["hash"]


# --------------------------------------------------------------------------- #
# Promotion router
# --------------------------------------------------------------------------- #


def _serialized_size_bytes(serialized: Any) -> int:
    """Return the JSON wire-byte size of an already-serialized value.

    Uses the same canonical encoding as the hash so the byte count
    matches what the server will store. (We don't subtract for JSON
    framing the server adds around the value because that framing is
    constant overhead unrelated to the per-value cap.)

    :param serialized: The JSON-compatible value.
    :type serialized: Any
    :return: The JSON wire-byte size of the serialized value.
    :rtype: int
    """
    return len(json.dumps(serialized, separators=(",", ":")).encode("utf-8"))


def _resolve_input_storage(
    serialized: Any,
    *,
    threshold_bytes: int,
    key_for_attachment: str,
    task_id: str,
) -> tuple[str, Any]:
    """Decide whether an input goes inline or to an attachment.

    Returns a 2-tuple ``(mode, value)``:

    - ``("inline", serialized)`` — caller writes ``serialized`` directly
      into payload (no attachments write).
    - ``("attachment", ref_slot)`` — caller writes ``serialized`` into
      ``attachments[key_for_attachment]`` AND writes ``ref_slot`` into
      payload (or queue), in a SINGLE PATCH.

    Raises :class:`~._exceptions.InputTooLarge` if the serialized form
    exceeds the per-attachment cap.

    :param serialized: The JSON-compatible value to route.
    :type serialized: Any
    :keyword threshold_bytes: Below-or-equal stays inline; strictly
        greater is promoted. Use :data:`_INPUT_THRESHOLD_BYTES` for
        function inputs and :data:`_STEERING_THRESHOLD_BYTES` for
        steering inputs.
    :paramtype threshold_bytes: int
    :keyword key_for_attachment: The attachment key to use if promoted.
        Caller-allocated to keep this helper stateless.
    :paramtype key_for_attachment: str
    :keyword task_id: For error context only.
    :paramtype task_id: str
    :return: ``("inline", serialized)`` or ``("attachment", ref_slot)``.
    :rtype: tuple[str, Any]
    :raises InputTooLarge: If the serialized form exceeds the
        per-attachment cap (:data:`_MAX_ATTACHMENT_SIZE_BYTES`).
    """
    size = _serialized_size_bytes(serialized)
    if size > _MAX_ATTACHMENT_SIZE_BYTES:
        raise InputTooLarge(
            task_id=task_id,
            size_bytes=size,
            max_bytes=_MAX_ATTACHMENT_SIZE_BYTES,
        )
    if size <= threshold_bytes:
        return ("inline", serialized)
    ref_slot = _make_ref(key_for_attachment, serialized)
    return ("attachment", ref_slot)


# --------------------------------------------------------------------------- #
# Unified read
# --------------------------------------------------------------------------- #


def _read_input_value(
    slot: Any,
    attachments: dict[str, Any] | None,
) -> Any:
    """Return the actual input value from a payload slot.

    If *slot* is a ref (per :func:`_is_ref`), looks up
    ``attachments[ref_key]`` and returns that value.
    Otherwise returns *slot* as-is (inline).

    No backward-compat for the legacy raw-input shape (per Decision 10
    in ``research.md``): the framework only writes ``("inline",
    serialized)`` or ``("attachment", ref)`` — both are handled by this
    one function.

    Raises ``KeyError`` if *slot* is a ref but the referenced attachment
    is missing — caller's responsibility to surface a meaningful error.

    :param slot: The payload slot or queue entry.
    :type slot: Any
    :param attachments: The task's attachments dict (from
        ``TaskInfo.attachments``). May be ``None`` if no attachments
        exist; in that case, encountering a ref raises ``KeyError``.
    :type attachments: dict[str, Any] | None
    :return: The deserialized input value.
    :rtype: Any
    """
    if not _is_ref(slot):
        return slot
    key = _ref_key(slot)
    if attachments is None:
        raise KeyError(
            f"Slot is a ref to attachment {key!r} but no attachments are present "
            f"on the task. Wire-shape invariant violated."
        )
    if key not in attachments:
        raise KeyError(
            f"Slot is a ref to attachment {key!r} but that attachment is missing. "
            f"Available attachment keys: {sorted(attachments.keys())!r}"
        )
    return attachments[key]


# --------------------------------------------------------------------------- #
# Size + count validators (used by the HTTP client + local provider)
# --------------------------------------------------------------------------- #


def _validate_attachment_size(
    task_id: str,
    attachment_key: str,
    value: Any,
) -> None:
    """Raise :class:`_AttachmentTooLarge` if *value* exceeds the per-attachment cap.

        Skip if value is ``None`` (representing a delete in a PATCH).

    : this raises the framework-internal
        ``_AttachmentTooLarge``. Callers above the provider layer
        (framework write paths) catch it and re-raise via
        :func:`_remap_attachment_error` as the developer-facing
        ``InputTooLarge`` / ``OutputTooLarge`` based on the
        attachment-key prefix.

        :param task_id: Task identifier for error context.
        :type task_id: str
        :param attachment_key: Attachment key for error context.
        :type attachment_key: str
        :param value: The JSON-compatible attachment value.
        :type value: Any
        :raises _AttachmentTooLarge: If the serialized form exceeds the cap.
    """
    if value is None:
        return  # null = delete; no size to enforce
    size = _serialized_size_bytes(value)
    if size > _MAX_ATTACHMENT_SIZE_BYTES:
        raise _AttachmentTooLarge(
            task_id=task_id,
            attachment_key=attachment_key,
            size_bytes=size,
            max_bytes=_MAX_ATTACHMENT_SIZE_BYTES,
        )


def _validate_attachment_count(
    task_id: str,
    current_count: int,
    additions: int = 1,
) -> None:
    """Raise :class:`_AttachmentLimitExceeded` if adding *additions* exceeds the per-task cap.

      — internal-only exception; framework treats
    propagation as a bug (the framework's own reserved usage is at
    most 11 of 20 slots) and converts to ``RuntimeError`` at the boundary.

    :param task_id: Task identifier for error context.
    :type task_id: str
    :param current_count: Number of attachments currently on the task
        (excluding any that this PATCH deletes).
    :type current_count: int
    :param additions: Number of new attachment entries this PATCH adds.
    :type additions: int
    :raises _AttachmentLimitExceeded: If ``current_count + additions > _MAX_ATTACHMENTS``.
    """
    if current_count + additions > _MAX_ATTACHMENTS:
        raise _AttachmentLimitExceeded(
            task_id=task_id,
            current_count=current_count,
            max_count=_MAX_ATTACHMENTS,
        )


def _remap_attachment_error(exc: "_AttachmentTooLarge") -> Exception:
    """— translate the internal ``_AttachmentTooLarge``
    raised against a framework-reserved attachment key into the
    developer-facing exception.

    Dispatch by attachment-key prefix:

    - ``_input`` → :class:`InputTooLarge`
    - ``_steering_input_<seq>`` → :class:`InputTooLarge`
    - ``_output`` → :class:`OutputTooLarge`
    - anything else → :class:`RuntimeError` (framework bug — the
      framework's own attachment writes only use the reserved keys).

    Callers do ``raise _remap_attachment_error(internal)`` so the
    traceback reflects the framework's re-raise site, not the
    provider's raise site.

    :param exc: The internal attachment-too-large error to translate.
    :type exc: _AttachmentTooLarge
    :return: The developer-facing exception to raise.
    :rtype: Exception
    """
    key = getattr(exc, "attachment_key", "")
    task_id = getattr(exc, "task_id", "")
    size_bytes = getattr(exc, "size_bytes", 0)
    max_bytes = getattr(exc, "max_bytes", _MAX_ATTACHMENT_SIZE_BYTES)
    if key == _FUNCTION_INPUT_KEY or key.startswith(_STEERING_INPUT_KEY_PREFIX):
        return InputTooLarge(task_id=task_id, size_bytes=size_bytes, max_bytes=max_bytes)
    if key == _OUTPUT_KEY:
        return OutputTooLarge(task_id=task_id, size_bytes=size_bytes, max_bytes=max_bytes)
    return RuntimeError(
        f"Framework bug: _AttachmentTooLarge raised for unknown "
        f"framework-reserved attachment key {key!r} on task {task_id!r}: "
        f"{size_bytes} bytes > {max_bytes} byte cap."
    )


__all__ = [
    "_ATTACHMENT_REF_KEY",
    "_FUNCTION_INPUT_KEY",
    "_HASH_ALGO_PREFIX",
    "_INPUT_THRESHOLD_BYTES",
    "_MAX_ATTACHMENTS",
    "_MAX_ATTACHMENT_SIZE_BYTES",
    "_OUTPUT_KEY",
    "_STEERING_INPUT_KEY_PREFIX",
    "_STEERING_QUEUE_CAP",
    "_STEERING_THRESHOLD_BYTES",
    "_compute_attachment_hash",
    "_is_ref",
    "_make_ref",
    "_read_input_value",
    "_ref_hash",
    "_ref_key",
    "_remap_attachment_error",
    "_resolve_input_storage",
    "_serialized_size_bytes",
    "_validate_attachment_count",
    "_validate_attachment_size",
]
