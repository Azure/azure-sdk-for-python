# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Prepend a UTC timestamp to SDK log records when no handler will render one.

Scope: enriches the SDK's intentional, hand-written telemetry (HTTP
traces, session lifecycle, heartbeat, crash warnings) on these loggers:

* ``azure.ai.finetuning_sessions._patch``
* ``azure.ai.finetuning_sessions.aio._patch``

Autorest / code-generator helpers under ``_utils/`` are deliberately
excluded -- their logs are plumbing noise that operators do not correlate.

Mechanism: a :class:`logging.Filter` attached to each emitting logger.
For each record, the filter walks the logger's parent chain (honoring
``propagate=False``) and asks "is any handler reachable?". If **no**
handler is reachable, the record will fall through to
``logging.lastResort`` -- whose hardcoded format string is
``"%(levelname)s:%(name)s:%(message)s"`` -- and thus show no timestamp.
In that case the filter prepends ``[<iso-utc-ms>] `` to ``record.msg``
so the rendered line includes a timestamp. If a handler **is** reachable,
the filter is a no-op: the caller's formatter is responsible for the
timestamp (via ``%(asctime)s``, ``record.created``, or JSON time-field
handling), and the SDK does not duplicate it.

The timestamp uses ``record.created`` (set automatically by Python at log
call time), not the time the filter runs -- preserving event time under
queued / async handlers.

This module installs **no handler**, does not change propagation, and
never causes duplicate log lines in any caller-configured setup.

Operators can opt out without code changes by setting the env var
``AZURE_AI_FINETUNING_SESSIONS_SDK_LOG_CONTEXT`` to any of ``0``,
``false``, ``no``, ``off``, ``disable``, ``disabled`` (case-insensitive).
Programmatic control is also available via
``install_default_logging(enabled=True)`` or ``enabled=False``.
"""
from __future__ import annotations

import logging as _logging
import os as _os
from datetime import datetime as _datetime
from datetime import timezone as _timezone
from typing import Optional, Tuple

_SDK_ROOT = "azure.ai.finetuning_sessions"

# Environment variable that lets operators opt OUT of the timestamp
# filter without touching code. Default is enabled. Recognized "falsey"
# values (case-insensitive): "0", "false", "no", "off", "disable",
# "disabled". Any other value -- including unset -- leaves the filter
# enabled.
_ENV_VAR = "AZURE_AI_FINETUNING_SESSIONS_SDK_LOG_CONTEXT"
_FALSEY = frozenset({"0", "false", "no", "off", "disable", "disabled"})

# Child loggers that emit the SDK's intentional, user-facing telemetry.
# When a NEW hand-written SDK module starts emitting telemetry that
# should benefit from the no-handler timestamp fallback, add its dotted
# name here.
_SDK_EMITTING_LOGGERS: Tuple[str, ...] = (
    f"{_SDK_ROOT}._patch",
    f"{_SDK_ROOT}.aio._patch",
)


def _enabled_from_env() -> bool:
    raw = _os.environ.get(_ENV_VAR)
    if raw is None:
        return True
    return raw.strip().lower() not in _FALSEY


def _has_any_handler(name: str) -> bool:
    """True iff at least one handler is reachable in the logger's chain.

    Walks parents until a handler is found or propagation breaks. Mirrors
    the lookup ``Logger.callHandlers`` does, so a ``False`` return means
    the record will be dispatched to ``logging.lastResort``.
    """
    c: Optional[_logging.Logger] = _logging.getLogger(name)
    while c is not None:
        if c.handlers:
            return True
        if not c.propagate:
            return False
        c = c.parent
    return False


class _SdkTimestampFilter(_logging.Filter):
    """Prepend an ISO-8601 UTC timestamp to ``record.msg`` only when no
    handler is configured to render the record's time. Always returns
    ``True`` -- enriches, never drops."""

    def filter(self, record: _logging.LogRecord) -> bool:
        if not _has_any_handler(record.name):
            ts = _datetime.fromtimestamp(
                record.created, _timezone.utc
            ).isoformat(timespec="milliseconds")
            record.msg = f"[{ts}] {record.msg}"
        return True


def install_default_logging(enabled: Optional[bool] = None) -> None:
    """Attach the timestamp filter to every SDK emitting logger.

    :keyword enabled: If ``None`` (default), enablement is read from the
        ``AZURE_AI_FINETUNING_SESSIONS_SDK_LOG_CONTEXT`` env var; the
        filter is on unless the var is set to a falsey value (``0``,
        ``false``, ``no``, ``off``, ``disable``, ``disabled``). Pass
        ``True`` / ``False`` to force-enable or force-disable
        programmatically.

    Idempotent: a second call with ``enabled=True`` does not duplicate
    the filter; a call with ``enabled=False`` removes any previously
    installed instance. Installs no handler and does not change logger
    propagation.
    """
    if enabled is None:
        enabled = _enabled_from_env()

    for name in _SDK_EMITTING_LOGGERS:
        logger = _logging.getLogger(name)
        existing = [f for f in logger.filters if isinstance(f, _SdkTimestampFilter)]
        if not enabled:
            for f in existing:
                logger.removeFilter(f)
            continue
        if existing:
            continue
        logger.addFilter(_SdkTimestampFilter())


__all__ = ["install_default_logging"]
