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


class DurabilityContext:
    """Recovery-awareness context exposed to response handlers.

    All properties are read-only except ``metadata`` which is a mutable
    mapping for developer-controlled checkpointing.

    :param entry_mode: How the handler was entered — ``"fresh"`` for normal
        invocation or ``"recovered"`` after a crash.
    :param run_attempt: Number of recovery attempts (0 on first run).
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
        """Recovery attempt counter (0 on first run, incremented on each crash recovery)."""
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
