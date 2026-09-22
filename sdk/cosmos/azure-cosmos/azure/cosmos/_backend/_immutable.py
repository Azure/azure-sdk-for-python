# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy Python wrapper request data so caller edits cannot change a pending request."""

from __future__ import annotations

from collections.abc import ItemsView, Iterator, Mapping
from dataclasses import InitVar, dataclass
from types import MappingProxyType
from typing import Any, Optional


@dataclass(frozen=True, slots=True, eq=False)
class FrozenMapping(Mapping[Any, Any]):
    """Read-only copy that compares keys and values like a dictionary.

    Nested dictionaries and lists are also made read-only. Like a dictionary,
    this object cannot be used as a dictionary key.
    """

    _values: Mapping[Any, Any]
    _parents: InitVar[Optional[set[int]]] = None

    def __post_init__(self, _parents: Optional[set[int]]) -> None:
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
        return self


def freeze_json(value: Any, parents: Optional[set[int]] = None) -> Any:
    """Make dictionaries and lists read-only, including their nested values.

    For example, a caller's list becomes a tuple. Values already known to be
    read-only can be reused. Circular references and unsupported value types raise.
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
    if not isinstance(headers, Mapping) or any(
        type(key) is not str or type(value) is not str
        for key, value in headers.items()
    ):
        raise TypeError("Prepared headers must be a mapping of strings to strings")
    if not headers:
        return _EMPTY_HEADERS
    return headers if type(headers) is FrozenMapping else FrozenMapping(headers)


def json_mapping(value: Any) -> dict[Any, Any]:
    """Let the JSON encoder write a FrozenMapping as a JSON object."""
    if type(value) is FrozenMapping:
        return dict(value.items())
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
