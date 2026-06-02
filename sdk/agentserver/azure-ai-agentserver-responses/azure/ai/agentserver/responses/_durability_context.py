# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""DurabilityContext — recovery-awareness state exposed to response handlers.

Per spec 015 FR-040 / FR-005, the handler-facing metadata wrapper rejects
any key (or named-namespace name) starting with ``_`` so that response
handlers cannot accidentally collide with framework-reserved namespaces
(e.g. ``_responses``). The framework layer reaches those namespaces via
the underlying :class:`~azure.ai.agentserver.core.durable.TaskContext`
directly — the primitive itself does not enforce the convention.
"""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from typing import Any, Literal, Optional

DurabilityEntryMode = Literal["fresh", "recovered"]


class _DeveloperMetadataFacade(MutableMapping[str, Any]):
    """Handler-facing wrapper over a ``TaskMetadata``-like backing store.

    Provides the same dict-like + callable shape as
    :class:`~azure.ai.agentserver.core.durable.TaskMetadata` but rejects
    any key (or namespace name) starting with ``_``. Framework layers
    that need to write into reserved namespaces (e.g. ``_responses``)
    must use the underlying ``TaskContext.metadata`` directly — they do
    NOT go through this wrapper.
    """

    def __init__(self, raw: Any, _namespaces: Optional[dict[str, Any]] = None) -> None:
        self._raw = raw
        # For plain-dict backing stores (used in unit tests where the
        # backing object isn't a real TaskMetadata), maintain a private
        # per-namespace dict registry so ``facade(name)`` returns a
        # genuinely isolated store. For real TaskMetadata stores (callable),
        # the underlying primitive owns the registry.
        self._namespaces: dict[str, Any] = _namespaces if _namespaces is not None else {}

    @staticmethod
    def _check_key(key: Any) -> None:
        if isinstance(key, str) and key.startswith("_"):
            raise ValueError(
                f"metadata keys starting with '_' are reserved for "
                f"framework-internal namespaces (got {key!r}). Pick a "
                f"non-underscore-prefixed name."
            )

    def __getitem__(self, key: str) -> Any:
        self._check_key(key)
        return self._raw[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._check_key(key)
        self._raw[key] = value

    def __delitem__(self, key: str) -> None:
        self._check_key(key)
        del self._raw[key]

    def __iter__(self) -> Iterator[str]:
        return iter(k for k in self._raw if not (isinstance(k, str) and k.startswith("_")))

    def __len__(self) -> int:
        return sum(1 for k in self._raw if not (isinstance(k, str) and k.startswith("_")))

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str) and key.startswith("_"):
            return False
        return key in self._raw

    def get(self, key: str, default: Any = None) -> Any:
        if isinstance(key, str) and key.startswith("_"):
            return default
        return self._raw.get(key, default)

    def __call__(self, name: Optional[str] = None) -> "_DeveloperMetadataFacade":
        """Return a sibling namespace facade.

        ``ctx.metadata`` accesses the default (unnamed) namespace.
        ``ctx.metadata(name)`` accesses a named namespace.

        :raises ValueError: If ``name`` starts with ``_`` (reserved).
        """
        if name is None:
            return self
        if not isinstance(name, str):
            raise TypeError(
                f"namespace name must be a str, got {type(name).__name__}"
            )
        if name.startswith("_"):
            raise ValueError(
                f"named namespace {name!r} starts with '_', which is "
                f"reserved for framework-internal layers (e.g. "
                f"'_responses'). Pick a non-underscore-prefixed name."
            )
        raw = self._raw
        if callable(raw):
            sub = raw(name)
            return _DeveloperMetadataFacade(sub)
        # Plain-dict fallback: keep an isolated sub-dict per namespace
        sub = self._namespaces.setdefault(name, {})
        return _DeveloperMetadataFacade(sub)

    async def flush(self) -> None:
        """Force-persist any pending metadata writes for this namespace.

        Delegates to the underlying ``TaskMetadata.flush()`` when present.
        For non-durable / transient contexts (e.g. ``store=false`` responses
        or unit tests where the backing store is a plain ``dict``), this
        is a no-op.
        """
        flush = getattr(self._raw, "flush", None)
        if callable(flush):
            import asyncio  # local import to avoid top-level cycle  # noqa: PLC0415

            result = flush()
            if asyncio.iscoroutine(result):
                await result


class DurabilityContext:
    """Recovery-awareness context exposed to response handlers.

    All properties are read-only except :attr:`metadata`, which is a
    mutable mapping (also callable for named namespaces) for
    developer-controlled checkpointing.

    :param entry_mode: How the handler was entered — ``"fresh"`` for
        normal invocation or ``"recovered"`` after a crash.
    :param retry_attempt: Retry attempt counter — durable across crash
        recovery. Resets to 0 on a successful invocation chain; increments
        only on retryable failures.
    :param was_steered: Whether this invocation resulted from steering.
    :param pending_inputs: Number of queued steering inputs after this one.
    :param metadata: Developer-accessible checkpoint store. Use
        ``ctx.metadata`` for the default namespace or
        ``ctx.metadata(name)`` for a named namespace.
    """

    __slots__ = (
        "_entry_mode",
        "_retry_attempt",
        "_was_steered",
        "_pending_inputs",
        "_metadata",
    )

    def __init__(
        self,
        *,
        entry_mode: DurabilityEntryMode,
        retry_attempt: int,
        was_steered: bool,
        pending_inputs: int,
        metadata: Any,
    ) -> None:
        self._entry_mode = entry_mode
        self._retry_attempt = retry_attempt
        self._was_steered = was_steered
        self._pending_inputs = pending_inputs
        self._metadata = (
            metadata
            if isinstance(metadata, _DeveloperMetadataFacade)
            else _DeveloperMetadataFacade(metadata)
        )

    @property
    def entry_mode(self) -> DurabilityEntryMode:
        """How the handler was entered: ``'fresh'`` or ``'recovered'``."""
        return self._entry_mode

    @property
    def is_recovery(self) -> bool:
        """Convenience: True when this is a recovered re-invocation after a crash.

        Equivalent to ``entry_mode == "recovered"``.
        """
        return self._entry_mode == "recovered"

    @property
    def retry_attempt(self) -> int:
        """Retry attempt counter — durable across crash recovery.

        Resets to 0 on a successful invocation; increments only when the
        handler is re-invoked due to a retryable failure. The value is
        persisted to the task store at lifecycle boundaries, so it is
        stable across both in-process retries and post-crash recovery.

        Per spec 015 FR-001/FR-002, this counter unifies the previous
        ``run_attempt`` (per-process) and the cross-lifetime intent: the
        framework now tracks a single durable retry count.
        """
        return self._retry_attempt

    @property
    def was_steered(self) -> bool:
        """Whether this invocation was triggered by a steering input."""
        return self._was_steered

    @property
    def pending_inputs(self) -> int:
        """Number of queued steering inputs remaining after this one."""
        return self._pending_inputs

    @property
    def metadata(self) -> _DeveloperMetadataFacade:
        """Developer-accessible checkpoint store.

        Use ``ctx.metadata["key"] = value`` for the default namespace, or
        ``ctx.metadata("my_namespace")["key"] = value`` for a named
        namespace. Keys (and namespace names) starting with ``_`` are
        rejected — those are reserved for framework-internal layers.
        """
        return self._metadata
