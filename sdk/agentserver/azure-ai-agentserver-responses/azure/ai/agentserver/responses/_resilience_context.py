# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Internal metadata facade for response handler context.

(Spec 024 Phase 5 — Proposal #10 + #13) The pre-Phase-5
``ResilienceContext`` class is DELETED. Its fields are flattened into
top-level :class:`ResponseContext` attributes (``is_recovery``,
``is_steered_turn``, ``pending_input_count``, ``conversation_chain_metadata``).
The ``ResilienceEntryMode`` Literal alias and the ``retry_attempt``
field are also deleted (Proposal #12 / #13).

What survives in this module:

- :class:`_DeveloperMetadataFacade` — the internal wrapper that rejects
  keys / namespaces starting with ``_`` (framework-internal).
  Implements the public :class:`ConversationChainMetadataNamespace` Protocol
  exported from :mod:`azure.ai.agentserver.responses._response_context`.

Per spec 015 FR-040 / FR-005, the handler-facing metadata wrapper
rejects any key (or named-namespace name) starting with ``_`` so that
response handlers cannot accidentally collide with framework-reserved
namespaces (e.g. ``_responses``). The framework layer reaches those
namespaces via the underlying
:class:`~azure.ai.agentserver.core.tasks.TaskContext` directly — the
primitive itself does not enforce the convention.
"""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from typing import Any, Optional


class _DeveloperMetadataFacade(MutableMapping[str, Any]):
    """Handler-facing wrapper over a ``TaskMetadata``-like backing store.

    Provides the same dict-like + callable shape as
    :class:`~azure.ai.agentserver.core.tasks.TaskMetadata` but rejects
    any key (or namespace name) starting with ``_``. Framework layers
    that need to write into reserved namespaces (e.g. ``_responses``)
    must use the underlying ``TaskContext.metadata`` directly — they do
    NOT go through this wrapper.

    Satisfies the public :class:`ConversationChainMetadataNamespace` Protocol.
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

        ``ctx.conversation_chain_metadata`` accesses the default (unnamed) namespace.
        ``ctx.conversation_chain_metadata(name)`` accesses a named namespace.

        :raises ValueError: If ``name`` starts with ``_`` (reserved).
        """
        if name is None:
            return self
        if not isinstance(name, str):
            raise TypeError(f"namespace name must be a str, got {type(name).__name__}")
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
        For non-resilient / transient contexts (e.g. ``store=false`` responses
        or unit tests where the backing store is a plain ``dict``), this
        is a no-op.
        """
        flush = getattr(self._raw, "flush", None)
        if callable(flush):
            import asyncio  # local import to avoid top-level cycle  # noqa: PLC0415

            result = flush()
            if asyncio.iscoroutine(result):
                await result
