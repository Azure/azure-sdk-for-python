# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep prepared request data independent of later customer app edits.

A customer app can change its query parameters after the Python wrapper has
prepared an orders query. Those edits must not change the prepared request.
These helpers copy supported data and make the copy read-only, including
nested values. A read-only view of the customer's original dictionary would
not be enough: changes through the original dictionary would remain visible.
"""

from __future__ import annotations

from collections.abc import ItemsView, Iterator, Mapping
from dataclasses import InitVar, dataclass
from types import MappingProxyType
from typing import Any, Optional


@dataclass(frozen=True, slots=True, eq=False)
class FrozenMapping(Mapping[Any, Any]):
    """Own a read-only snapshot of a mapping and its nested values.

    For example, the Python wrapper can retain an orders-query parameter
    independently of the customer app's list::

        parameter = {"name": "@statuses", "value": ["active"]}
        prepared = FrozenMapping(parameter)
        parameter["value"].append("cancelled")

    ``prepared["value"]`` remains ``("active",)``. Nested mappings become
    FrozenMapping objects, and lists become tuples, which cannot be edited.
    Freezing the dataclass alone would only prevent field reassignment, not
    changes inside a dictionary or list.

    Mapping keys must be None or exact built-in str, int, float or bool values.
    Supported nested values and failures follow ``freeze_json``.
    Equality compares stored keys and values rather than object identity.
    Like a dictionary, this object cannot be used as a dictionary key.
    """

    _values: Mapping[Any, Any]
    _parents: InitVar[Optional[set[int]]] = None

    def __post_init__(self, _parents: Optional[set[int]]) -> None:
        """Copy and freeze entries, then install the owned read-only mapping.

        ``_parents`` contains identities in the current nesting chain, not
        every object already copied. A mapping containing itself raises
        ValueError; two entries referring to the same child are allowed.
        Invalid keys or unsupported nested values raise TypeError.

        Remove this mapping's identity even when copying fails. The final
        attribute assignment installs the snapshot during construction of
        the frozen dataclass; it does not modify the supplied mapping.
        """
        parents = set() if _parents is None else _parents
        identity = id(self._values)
        if identity in parents:
            raise ValueError("Circular reference in prepared request data")
        parents.add(identity)
        try:
            values: dict[Any, Any] = {}
            for key, value in self._values.items():
                if key is not None and type(key) not in (str, int, float, bool):
                    raise TypeError("Prepared JSON mapping keys must be JSON scalars")
                values[key] = freeze_json(value, parents)
        finally:
            parents.remove(identity)
        object.__setattr__(self, "_values", MappingProxyType(values))

    def __getitem__(self, key: Any) -> Any:
        return self._values[key]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def items(self) -> ItemsView[Any, Any]:
        return self._values.items()

    def __deepcopy__(self, memo: dict[int, Any]) -> FrozenMapping:
        """Reuse this object because its stored contents are already read-only.

        No children need copying, so the deepcopy memo is not used.
        """
        return self


def freeze_json(value: Any, parents: Optional[set[int]] = None) -> Any:
    """Freeze supported request values without converting them to JSON bytes.

    Mappings become FrozenMapping objects; lists and tuples become tuples
    whose contents are frozen recursively. None and exact built-in str, int,
    float and bool values are reused, as are exact FrozenMapping instances.
    An exact tuple is reused only when every element is reused unchanged.

    ``parents`` is internal recursion state: identities in the current
    nesting chain. Callers normally omit it. Circular references raise
    ValueError, but repeated references to a child outside that chain are
    allowed. Unsupported values or mapping keys raise TypeError rather than
    being silently converted to strings.

    This prepares Python values, not a complete JSON-validity check.
    Encoding happens later; ``json_mapping`` handles frozen mappings then.
    """
    if value is None or type(value) in (str, int, float, bool, FrozenMapping):
        return value
    parents = set() if parents is None else parents
    if isinstance(value, Mapping):
        return FrozenMapping(value, parents)
    if isinstance(value, (tuple, list)):
        identity = id(value)
        if identity in parents:
            raise ValueError("Circular reference in prepared request data")
        parents.add(identity)
        try:
            result = tuple(freeze_json(item, parents) for item in value)
        finally:
            parents.remove(identity)
        if type(value) is tuple and all(a is b for a, b in zip(value, result)):
            return value
        return result
    raise TypeError(f"Unsupported prepared JSON value: {type(value).__name__}")


_EMPTY_HEADERS = FrozenMapping({})


def freeze_headers(headers: Mapping[str, str]) -> Mapping[str, str]:
    """Retain request headers without depending on the caller's mapping.

    Require a mapping whose keys and values are exact built-in strings;
    otherwise raise TypeError. Copy other mappings, including read-only
    views whose underlying dictionary the customer app could still change.

    Reuse an exact FrozenMapping after checking its entries. Empty mappings
    share one read-only instance because they contain no values to copy.
    """
    if not isinstance(headers, Mapping) or any(
        type(key) is not str or type(value) is not str
        for key, value in headers.items()
    ):
        raise TypeError("Prepared headers must be a mapping of strings to strings")
    if not headers:
        return _EMPTY_HEADERS
    return headers if type(headers) is FrozenMapping else FrozenMapping(headers)


def json_mapping(value: Any) -> dict[Any, Any]:
    """Adapt a FrozenMapping for ``json.dumps(default=json_mapping)``.

    The Python wrapper uses this callback when encoding prepared request data
    for the binding. Return an ordinary dictionary so the encoder writes a
    JSON object; the encoder handles nested values, invoking this callback
    again for nested FrozenMapping objects.

    Only exact FrozenMapping instances are accepted. Other values raise
    TypeError: this is an encoder callback, not a general conversion helper.
    """
    if type(value) is FrozenMapping:
        return dict(value.items())
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
