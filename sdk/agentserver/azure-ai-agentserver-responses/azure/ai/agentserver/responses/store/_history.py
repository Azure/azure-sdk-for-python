# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Shared history-resolution rules for response providers."""

from __future__ import annotations

from typing import Any

_NON_REPLAYABLE_STATUSES: frozenset[str] = frozenset({"failed"})


def normalize_status(status: Any) -> str | None:
    """Return *status* as the plain string the wire uses, or ``None`` when unset.

    Accepts the raw string stored on a response envelope as well as an enum
    member whose ``value`` is that string, so providers persist and compare
    the same representation regardless of how the status was produced.

    :param status: The stored response status, if any.
    :type status: Any
    :returns: The status string, or ``None``.
    :rtype: str | None
    """
    if status is None:
        return None
    return str(getattr(status, "value", status))


def is_replayable_status(status: Any) -> bool:
    """Return whether a response with *status* contributes its own items to history.

    Only a ``failed`` response is excluded: its input is what made the turn
    fail, so replaying it would fail every later turn in the same conversation
    or chain. Responses in any other state (including ``incomplete`` and
    ``cancelled``) keep their items in history, as does a response whose
    status is unknown.

    :param status: The stored response status, if any.
    :type status: Any
    :returns: ``True`` when the response's input and output items are replayable.
    :rtype: bool
    """
    normalized = normalize_status(status)
    if normalized is None:
        return True
    return normalized not in _NON_REPLAYABLE_STATUSES
