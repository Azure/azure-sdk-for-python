# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Mutable progress metadata for resilient tasks.

Provides a dict-like interface with typed mutation methods plus a
**named-namespace** facility:

    ctx.metadata["key"] = "value"          # default namespace
    ctx.metadata("custom")["k"] = 1        # named namespace facade
    ctx.metadata("_reserved")["seq"] = 5   # framework-layer convention

Each namespace persists to a distinct payload slot:

* ``payload["metadata"]``           — default namespace
* ``payload["metadata:<name>"]``    — named namespaces

There is **no auto-flush loop**. Flushes are explicit:

* :meth:`TaskMetadata.flush` — flush THIS namespace only.
* :meth:`TaskMetadata._flush_all` — flush every dirty namespace
  (called by the framework at lifecycle boundaries: suspend,
  complete, fail, steering drain).

The CORE primitive does NOT enforce namespace-name conventions.
Wrapper layers (e.g., responses) may reject ``_*`` names in their
:class:`ResilienceContext` facade — that is wrapper-layer policy
.
"""

from __future__ import annotations

import collections.abc
import logging
from collections.abc import Iterator
from typing import Any, Awaitable, Callable, Optional

from azure.ai.agentserver.core._experimental import experimental

logger = logging.getLogger("azure.ai.agentserver.tasks")

# Sentinel to distinguish "not set" from None
_NOT_SET = object()

# Type alias for the per-namespace flush callback.
# The framework supplies a callback that knows how to persist data for
# a given namespace into the underlying task payload.
NamespaceFlushCallback = Callable[[Optional[str], dict[str, Any]], Awaitable[None]]


@experimental
class TaskMetadata(collections.abc.MutableMapping):
    """Mutable progress dict persisted to the task record's payload.

    The default namespace exposes a ``MutableMapping`` interface
    directly. Named namespaces are accessed via the **callable**
    protocol — ``meta(name)`` returns a sibling namespace facade.

    :param initial: Initial values for the **default** namespace.
    :type initial: dict[str, Any] | None
    :param flush_callback: Async callable invoked by :meth:`flush` to
        persist dirty data. Signature: ``(namespace, data)`` where
        ``namespace`` is ``None`` for the default namespace and a
        ``str`` for named namespaces.
    :type flush_callback: NamespaceFlushCallback | None
    """

    def __init__(
        self,
        initial: dict[str, Any] | None = None,
        *,
        flush_callback: NamespaceFlushCallback | None = None,
        _namespace_name: Optional[str] = None,
        _registry: dict[Optional[str], "TaskMetadata"] | None = None,
    ) -> None:
        self._data: dict[str, Any] = dict(initial) if initial else {}
        self._dirty = False
        self._flush_callback: NamespaceFlushCallback | None = flush_callback
        self._namespace_name: Optional[str] = _namespace_name
        # Registry of namespaces, keyed by namespace name. ``None`` is
        # the default namespace. Child instances created via
        # :meth:`__call__` share the SAME registry so namespace lookups
        # are stable from any facade.
        if _registry is None:
            self._registry: dict[Optional[str], "TaskMetadata"] = {None: self}
        else:
            self._registry = _registry

    # -- Namespace callable protocol  --------------

    def __call__(self, name: Optional[str] = None) -> "TaskMetadata":
        """Return a namespace facade.

                ``meta()`` returns the default namespace; ``meta("custom")``
                returns the named-namespace facade (auto-vivified).

        The core primitive does NOT enforce namespace-name conventions
        (e.g. the leading-underscore reservation). That is a wrapper-
        layer concern — handler-facing wrappers (composed protocol
        packages) may reject ``_*`` names so handlers can't collide with
        framework-reserved namespaces. Framework-layered code (a wrapper
        orchestrator itself) reaches reserved namespaces directly via
        this API.

                :param name: Namespace name. ``None`` returns the default
                    namespace; a string returns the named namespace.
                :type name: str | None
                :return: A namespace facade.
                :rtype: TaskMetadata
        """
        if name is None:
            return self._registry[None]
        if name in self._registry:
            return self._registry[name]
        # Auto-vivify a new namespace; share the registry and inherit
        # the parent's per-namespace flush callback.
        child = TaskMetadata(
            flush_callback=self._flush_callback,
            _namespace_name=name,
            _registry=self._registry,
        )
        self._registry[name] = child
        return child

    @classmethod
    def from_payload(
        cls,
        payload: dict[str, Any] | None,
        *,
        flush_callback: NamespaceFlushCallback | None = None,
    ) -> "TaskMetadata":
        """Construct a fresh :class:`TaskMetadata` from a recovered payload.

        Decodes the per-namespace persistence layout:

        * ``payload["metadata"]`` → default namespace.
        * ``payload["metadata:<name>"]`` → named namespace ``<name>``.

        :param payload: The task's payload dict (or ``None``).
        :type payload: dict[str, Any] | None
        :keyword flush_callback: Per-namespace flush callback to wire into
            every restored namespace.
        :paramtype flush_callback: NamespaceFlushCallback | None
        :return: A fully populated :class:`TaskMetadata` with all named
            namespaces pre-vivified to their recovered state.
        :rtype: TaskMetadata
        """
        payload = payload or {}
        default_data = payload.get("metadata") or {}
        if not isinstance(default_data, dict):
            default_data = {}

        root = cls(initial=default_data, flush_callback=flush_callback)
        for key, value in payload.items():
            if not isinstance(key, str) or not key.startswith("metadata:"):
                continue
            name = key[len("metadata:") :]
            if not name or not isinstance(value, dict):
                continue
            # Auto-vivify and seed
            ns = root(name)
            ns._data = dict(value)  # pylint: disable=protected-access
            ns._dirty = False  # pylint: disable=protected-access
        return root

    # -- Typed mutation methods (operate on THIS namespace) ---------------- #

    def set(self, key: str, value: Any) -> None:
        """Set a key-value pair in this namespace.

        :param key: Metadata key (must be a string).
        :type key: str
        :param value: Any JSON-serializable value.
        :type value: Any
        :raises TypeError: If key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError(f"Metadata key must be a string, got {type(key).__name__}")
        self._data[key] = value
        self._mark_dirty()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value by key.

        :param key: Metadata key.
        :type key: str
        :param default: Default value if key is absent.
        :type default: Any
        :return: The value, or *default*.
        :rtype: Any
        """
        return self._data.get(key, default)

    def increment(self, key: str, delta: int = 1) -> None:
        """Atomically increment a numeric value.

        :param key: Metadata key.
        :type key: str
        :param delta: Amount to add (default 1).
        :type delta: int
        :raises TypeError: If the existing value is not numeric.
        """
        if not isinstance(delta, (int, float)):
            raise TypeError(f"Delta must be numeric, got {type(delta).__name__}")
        current = self._data.get(key, 0)
        if not isinstance(current, (int, float)):
            raise TypeError(f"Cannot increment non-numeric value at key {key!r}: " f"{type(current).__name__}")
        self._data[key] = current + delta
        self._mark_dirty()

    def append(self, key: str, value: Any) -> None:
        """Append a value to a list.

        Creates the list if the key is absent.

        :param key: Metadata key.
        :type key: str
        :param value: Value to append.
        :type value: Any
        :raises TypeError: If the existing value is not a list.
        """
        current = self._data.get(key, _NOT_SET)
        if current is _NOT_SET:
            self._data[key] = [value]
        elif isinstance(current, list):
            current.append(value)
        else:
            raise TypeError(f"Cannot append to non-list value at key {key!r}: " f"{type(current).__name__}")
        self._mark_dirty()

    def to_dict(self) -> dict[str, Any]:
        """Return a snapshot of this namespace's data.

        :return: A shallow copy of the namespace's dict.
        :rtype: dict[str, Any]
        """
        return dict(self._data)

    # -- Dict protocol (MutableMapping) ------------------------------------ #

    def __setitem__(self, key: str, value: Any) -> None:
        if not isinstance(key, str):
            raise TypeError(f"Metadata key must be a string, got {type(key).__name__}")
        self._data[key] = value
        self._mark_dirty()

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __delitem__(self, key: str) -> None:
        del self._data[key]
        self._mark_dirty()

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def keys(self) -> collections.abc.KeysView[str]:
        """Return a view of metadata keys.

        :return: A view of the metadata keys.
        :rtype: ~collections.abc.KeysView[str]
        """
        return self._data.keys()

    def values(self) -> collections.abc.ValuesView[Any]:
        """Return a view of metadata values.

        :return: A view of the metadata values.
        :rtype: ~collections.abc.ValuesView[Any]
        """
        return self._data.values()

    def items(self) -> collections.abc.ItemsView[str, Any]:
        """Return a view of metadata key-value pairs.

        :return: A view of the metadata key-value pairs.
        :rtype: ~collections.abc.ItemsView[str, Any]
        """
        return self._data.items()

    # -- Flush API (explicit; no auto-flush loop) -------------------------- #

    async def flush(self) -> None:
        """Force-flush this namespace's pending changes to storage.

        No-op if there are no pending changes in THIS namespace or no
        flush callback. Sibling namespaces are NOT touched.
        """
        await self._do_flush_one()

    async def _flush_all(self) -> None:
        """— framework-internal: flush every dirty
        namespace (default + all named).

        Called by the framework at lifecycle boundaries (suspend,
        complete, fail, steering drain) to guarantee all in-memory
        mutations land in the task payload before the task transitions.

        The leading underscore is the canonical signal for
        "package-private; not part of the documented developer
        surface." Developers MUST NOT call this — per-namespace
        :meth:`flush` is the only fence pattern they need.
        """
        for ns in list(self._registry.values()):
            await ns._do_flush_one()  # pylint: disable=protected-access

    def _mark_dirty(self) -> None:
        self._dirty = True

    async def _do_flush_one(self) -> None:
        if not self._dirty or self._flush_callback is None:
            return
        try:
            await self._flush_callback(self._namespace_name, dict(self._data))
            self._dirty = False
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning(
                "Failed to flush metadata namespace %r",
                self._namespace_name,
                exc_info=True,
            )


# =========================================================================
#  — JSONValue recursive type alias
# =========================================================================
#
# Public type alias exported via tasks.__init__. TaskMetadata values
# SHOULD be JSON-serializable; this alias documents the value space.

from typing import Union, List, Dict  # pylint: disable=wrong-import-position

try:
    from typing import TypeAlias  # Python 3.10+
except ImportError:  # pragma: no cover
    from typing_extensions import TypeAlias  # type: ignore[assignment]

# Recursive JSON type alias. Forward refs allow self-recursion.
# Use ForwardRef-via-string for the recursive arms so this type-checks
# on all Python versions, and the test's ForwardRef-detection logic
# resolves the recursion to the same alias.
JSONValue: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
    List["JSONValue"],
    Dict[str, "JSONValue"],
]
