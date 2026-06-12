# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Internal framework-private exceptions.

These exception types are NEVER exported from
``azure.ai.agentserver.core.durable.__init__``. They exist purely as
internal discriminators the framework's classifier code raises so
that lifecycle / retry / error-mapping code can branch on the
underlying cause without leaking service-API vocabulary onto the
developer surface.

The translation from these internal types → developer-facing types
is documented in ``docs/task-and-streaming-spec.md`` §39.1.
"""

from __future__ import annotations


class _HostedConflict(Exception):
    """Internal discriminator for service-emitted error codes.

    The hosted task service returns distinct error codes for distinct
    failure conditions (``task_immutable``, ``invalid_state_transition``,
    ``lease_held_by_another``, ``task_already_exists``,
    ``lease_ownership_changed``, ``etag_mismatch``, ``invalid_request``).
    The hosted provider's response classifier wraps each in this type
    so the framework's lifecycle code can dispatch on ``_code`` and
    translate to the appropriate public exception (or retry
    transparently for ``etag_mismatch`` / ``lease_ownership_changed``).

    The local file provider raises the same type with the same ``_code``
    directly for the equivalent in-process conditions, so the
    framework's dispatch table works against either backing.

    The leading underscore on the class name AND on ``_code`` is the
    Python-canonical signal: package-private, never imported by
    developer code, never appears in docstrings of public APIs.

    :param _code: One of the service's structured error code strings.
        Matches the ``code`` field of the JSON error envelope on the
        wire.
    :type _code: str
    :param status_code: The HTTP status code the service would return
        (or would have returned, in local mode). 400 / 409 / 412 per
        §39.1.
    :type status_code: int
    :param message: Optional human-readable message for diagnostic
        purposes. NEVER reaches developer code as-is — the framework's
        translation step writes its own framework-vocabulary message
        on the public exception.
    :type message: str | None
    :param task_id: Optional task identifier for log correlation.
    :type task_id: str | None
    """

    __slots__ = ("_code", "status_code", "message", "task_id")

    def __init__(
        self,
        _code: str,
        status_code: int,
        message: str | None = None,
        task_id: str | None = None,
    ) -> None:
        super().__init__(message or _code)
        self._code = _code
        self.status_code = status_code
        self.message = message
        self.task_id = task_id

    def __repr__(self) -> str:
        return (
            f"_HostedConflict(_code={self._code!r}, "
            f"status_code={self.status_code!r}, "
            f"task_id={self.task_id!r})"
        )


# Public name "_HostedConflict" is exported via class definition above.
# Intentionally NOT added to any __all__; underscore prefix already
# excludes it from `from _exceptions_internal import *` and signals
# package-private intent.
__all__: list[str] = []
