# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""DurabilityContext — recovery-awareness state exposed to response handlers."""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from typing import Any, Literal

DurabilityEntryMode = Literal["fresh", "recovered"]


class _FilteredMetadata(MutableMapping[str, Any]):
    """A filtered view of TaskMetadata that hides _framework.* keys.

    Developers interact with this wrapper; framework-internal state is
    stored under the ``_framework.`` prefix and invisible to handler code.
    """

    _FRAMEWORK_PREFIX = "_framework."

    def __init__(self, raw: MutableMapping[str, Any]) -> None:
        self._raw = raw

    def __getitem__(self, key: str) -> Any:
        if key.startswith(self._FRAMEWORK_PREFIX):
            raise KeyError(key)
        return self._raw[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if key.startswith(self._FRAMEWORK_PREFIX):
            raise ValueError(
                f"Keys starting with '{self._FRAMEWORK_PREFIX}' are reserved "
                f"for framework-internal use and cannot be set via metadata."
            )
        self._raw[key] = value

    def __delitem__(self, key: str) -> None:
        if key.startswith(self._FRAMEWORK_PREFIX):
            raise KeyError(key)
        del self._raw[key]

    def __iter__(self) -> Iterator[str]:
        return (k for k in self._raw if not k.startswith(self._FRAMEWORK_PREFIX))

    def __len__(self) -> int:
        return sum(1 for k in self._raw if not k.startswith(self._FRAMEWORK_PREFIX))

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str) and key.startswith(self._FRAMEWORK_PREFIX):
            return False
        return key in self._raw

    async def flush(self) -> None:
        """Force-persist any pending metadata writes to the task store.

        Delegates to the underlying ``TaskMetadata.flush()`` when present.
        For non-durable / transient contexts (e.g. ``store=false`` responses
        or unit tests) the underlying mapping is a plain ``dict`` and this
        is a no-op.

        Use this after a watermark write that gates a subsequent
        side-effecting upstream call, so a crash between the write and the
        call still recovers cleanly (the recovered handler will see the
        persisted watermark and not re-issue the side effect).
        """
        flush = getattr(self._raw, "flush", None)
        if callable(flush):
            import asyncio  # local import to avoid top-level cycle  # noqa: PLC0415

            result = flush()
            if asyncio.iscoroutine(result):
                await result


class DurabilityContext:
    """Recovery-awareness context exposed to response handlers.

    All properties are read-only except ``metadata`` which is a mutable
    mapping for developer-controlled checkpointing.

    :param entry_mode: How the handler was entered — ``"fresh"`` for normal
        invocation or ``"recovered"`` after a crash.
    :param run_attempt: Per-process retry attempt counter (see the
        :attr:`run_attempt` property docstring for the **important**
        caveat about cross-lifetime semantics).
    :param was_steered: Whether this invocation resulted from steering.
    :param pending_inputs: Number of queued steering inputs after this one.
    :param metadata: Developer-accessible checkpoint store.
    """

    __slots__ = (
        "_entry_mode",
        "_run_attempt",
        "_was_steered",
        "_pending_inputs",
        "_metadata",
    )

    def __init__(
        self,
        *,
        entry_mode: DurabilityEntryMode,
        run_attempt: int,
        was_steered: bool,
        pending_inputs: int,
        metadata: MutableMapping[str, Any],
    ) -> None:
        self._entry_mode = entry_mode
        self._run_attempt = run_attempt
        self._was_steered = was_steered
        self._pending_inputs = pending_inputs
        self._metadata = _FilteredMetadata(metadata) if not isinstance(metadata, _FilteredMetadata) else metadata

    @property
    def entry_mode(self) -> DurabilityEntryMode:
        """How the handler was entered: 'fresh' or 'recovered'."""
        return self._entry_mode

    @property
    def is_recovery(self) -> bool:
        """Convenience: True when this is a recovered re-invocation after a crash.

        Equivalent to ``entry_mode == "recovered"`` — use this for the common
        check; use :attr:`entry_mode` for the rare case where you need to
        distinguish from a resumed steerable turn.
        """
        return self._entry_mode == "recovered"

    @property
    def run_attempt(self) -> int:
        """Per-process retry attempt counter.

        .. warning::
           **Per-process semantics — this counter does NOT survive crash
           recovery.** It increments only within a single process
           lifetime, on in-process retries after a handler raises. On a
           new process lifetime (i.e. after the framework re-invokes the
           handler post-crash), ``run_attempt`` resets to 0.

           To detect whether your handler is running for the first time
           or as a crash-recovered re-invocation, use
           :attr:`is_recovery` (equivalently ``entry_mode == "recovered"``).
           Those signals ARE cross-lifetime stable.

           The original design intent was for ``run_attempt`` to be a
           cross-lifetime counter (incrementing on every re-invocation,
           whether in-process retry or post-crash recovery). The
           implementation drifted and the cross-lifetime semantic is
           tracked as backlog item B10 in
           ``sdk/agentserver/specs/backlog.md``. Until that lands,
           handlers must use ``is_recovery`` for cross-lifetime
           detection.
        """
        return self._run_attempt

    @property
    def was_steered(self) -> bool:
        """Whether this invocation was triggered by a steering input."""
        return self._was_steered

    @property
    def pending_inputs(self) -> int:
        """Number of queued steering inputs remaining after this one."""
        return self._pending_inputs

    @property
    def metadata(self) -> MutableMapping[str, Any]:
        """Developer-accessible checkpoint store (survives crashes).

        Keys prefixed with ``_framework.`` are reserved and not visible.
        """
        return self._metadata
