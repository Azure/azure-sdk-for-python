# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Internal-metadata facilities for ``OutputItem`` and ``ResponseObject``.

Two live, mutable ``MutableMapping[str, Any]`` views for attaching
framework-internal key/value data that is stripped before any client-facing
payload (see ``hosting/_egress.py``):

- :class:`_ItemInternalMetadataView` — backed by the ``"internal_metadata"``
  key directly on an output item (items round-trip unknown keys verbatim).
- :class:`_ResponseInternalMetadataView` — backed by a reserved
  ``"_internal_metadata"`` key (JSON-encoded) inside the response's *public*
  ``metadata`` map, because the storage service's response envelope is a fixed
  schema with no first-class internal field.

Both views are *live*: every read/write/delete operates on the backing slot, so
``item.internal_metadata["k"] = v`` (or ``response.internal_metadata[...] = ...``)
takes effect immediately. An empty view writes no key.
"""

from __future__ import annotations

import json
from collections.abc import ItemsView, Iterator, KeysView, MutableMapping, ValuesView
from typing import Any

ITEM_KEY = "internal_metadata"
RESERVED_KEY = "_internal_metadata"

# Limits imposed by the storage service's public ``metadata`` map: at most 16
# key/value pairs, each value at most 512 characters. The reserved key consumes
# one of the 16 slots and its JSON-encoded value must fit the length cap.
_MAX_METADATA_KEYS = 16
_MAX_VALUE_LEN = 512


class _ItemInternalMetadataView(MutableMapping):
    """Live view over an output item's ``internal_metadata`` bag.

    The bag is a plain dict stored under the item's ``"internal_metadata"`` key
    (mapping access goes to the model's ``_data``). Values may be any
    JSON-serialisable type; keys must be strings. An emptied bag removes the key
    so an empty view serialises nothing.
    """

    __slots__ = ("_owner",)

    def __init__(self, owner: Any) -> None:
        self._owner = owner

    def _bag(self, *, create: bool = False) -> "dict[str, Any] | None":
        bag = self._owner.get(ITEM_KEY)
        if not isinstance(bag, dict):
            bag = None
        if bag is None and create:
            bag = {}
            self._owner[ITEM_KEY] = bag
        return bag

    def __getitem__(self, key: str) -> Any:
        bag = self._bag()
        if bag is None:
            raise KeyError(key)
        return bag[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if not isinstance(key, str):
            raise TypeError(f"internal_metadata keys must be str, got {type(key).__name__}")
        self._bag(create=True)[key] = value  # type: ignore[index]

    def __delitem__(self, key: str) -> None:
        bag = self._bag()
        if bag is None:
            raise KeyError(key)
        del bag[key]
        if not bag:
            self._owner.pop(ITEM_KEY, None)

    def __iter__(self) -> Iterator[str]:
        return iter(self._bag() or {})

    def __len__(self) -> int:
        return len(self._bag() or {})

    def __contains__(self, key: object) -> bool:
        bag = self._bag()
        return bool(bag) and key in bag

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _ItemInternalMetadataView):
            other = dict(other)
        if isinstance(other, MutableMapping):
            other = dict(other)
        if isinstance(other, dict):
            return dict(self._bag() or {}) == other
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self) -> str:
        return f"internal_metadata({dict(self._bag() or {})!r})"

    # Concrete views so callers can ``.keys()/.values()/.items()`` ergonomically.
    def keys(self) -> KeysView[str]:
        return KeysView(self)

    def values(self) -> ValuesView[Any]:
        return ValuesView(self)

    def items(self) -> ItemsView[str, Any]:
        return ItemsView(self)


class _ResponseInternalMetadataView(MutableMapping):
    """Live view over a response's internal metadata.

    Backed by a reserved ``"_internal_metadata"`` key inside the response's
    public ``metadata`` map. The inner mapping is JSON-encoded (compact +
    deterministic) into that key's string value, so the idempotency byte-compare
    in ``checkpoint()`` is stable. Each mutation re-encodes and enforces the
    storage service's 512-char value limit and 16-key map limit, failing fast
    with ``ValueError``.
    """

    __slots__ = ("_response",)

    def __init__(self, response: Any) -> None:
        self._response = response

    def _decode(self) -> "dict[str, Any]":
        metadata = self._response.metadata
        if not metadata:
            return {}
        raw = metadata.get(RESERVED_KEY)
        if not raw:
            return {}
        try:
            decoded = json.loads(raw)
        except (TypeError, ValueError):
            return {}
        return decoded if isinstance(decoded, dict) else {}

    def _store(self, obj: "dict[str, Any]") -> None:
        metadata = self._response.metadata
        if not obj:
            # Empty internal metadata: remove the reserved key only.
            if metadata and RESERVED_KEY in metadata:
                del metadata[RESERVED_KEY]
            return
        encoded = json.dumps(obj, separators=(",", ":"), sort_keys=True)
        if len(encoded) > _MAX_VALUE_LEN:
            raise ValueError(
                f"internal_metadata encodes to {len(encoded)} chars, exceeding the "
                f"{_MAX_VALUE_LEN}-char limit of the response metadata value"
            )
        if metadata is None:
            self._response.metadata = {}
            metadata = self._response.metadata
        if RESERVED_KEY not in metadata and len(metadata) >= _MAX_METADATA_KEYS:
            raise ValueError(
                f"cannot add internal_metadata: response metadata already has "
                f"{len(metadata)} keys (limit {_MAX_METADATA_KEYS})"
            )
        metadata[RESERVED_KEY] = encoded

    def __getitem__(self, key: str) -> Any:
        return self._decode()[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if not isinstance(key, str):
            raise TypeError(f"internal_metadata keys must be str, got {type(key).__name__}")
        obj = self._decode()
        obj[key] = value
        self._store(obj)

    def __delitem__(self, key: str) -> None:
        obj = self._decode()
        del obj[key]
        self._store(obj)

    def __iter__(self) -> Iterator[str]:
        return iter(self._decode())

    def __len__(self) -> int:
        return len(self._decode())

    def __contains__(self, key: object) -> bool:
        return key in self._decode()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _ResponseInternalMetadataView):
            other = dict(other)
        if isinstance(other, MutableMapping):
            other = dict(other)
        if isinstance(other, dict):
            return self._decode() == other
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self) -> str:
        return f"internal_metadata({self._decode()!r})"

    def keys(self) -> KeysView[str]:
        return KeysView(self)

    def values(self) -> ValuesView[Any]:
        return ValuesView(self)

    def items(self) -> ItemsView[str, Any]:
        return ItemsView(self)


# --------------------------------------------------------------------------
# Property / method factories applied to the model classes by ``_patch.py``.
# --------------------------------------------------------------------------


def _item_internal_metadata_get(self: Any) -> _ItemInternalMetadataView:
    return _ItemInternalMetadataView(self)


def _item_internal_metadata_set(self: Any, value: "MutableMapping[str, Any] | None") -> None:
    if not value:
        self.pop(ITEM_KEY, None)
        return
    new_bag: "dict[str, Any]" = {}
    for key, val in dict(value).items():
        if not isinstance(key, str):
            raise TypeError(f"internal_metadata keys must be str, got {type(key).__name__}")
        new_bag[key] = val
    self[ITEM_KEY] = new_bag


def _item_strip_internal_metadata(self: Any) -> None:
    self.pop(ITEM_KEY, None)


def _response_internal_metadata_get(self: Any) -> _ResponseInternalMetadataView:
    return _ResponseInternalMetadataView(self)


def _response_internal_metadata_set(self: Any, value: "MutableMapping[str, Any] | None") -> None:
    view = _ResponseInternalMetadataView(self)
    # Replace contents wholesale: clear, then store the validated copy.
    if not value:
        view._store({})  # pylint: disable=protected-access
        return
    new_obj: "dict[str, Any]" = {}
    for key, val in dict(value).items():
        if not isinstance(key, str):
            raise TypeError(f"internal_metadata keys must be str, got {type(key).__name__}")
        new_obj[key] = val
    view._store(new_obj)  # pylint: disable=protected-access


def apply_internal_metadata(output_item_cls: type, response_object_cls: type) -> None:
    """Attach the ``internal_metadata`` surface to the model classes.

    :param output_item_cls: The generated ``OutputItem`` base class (all
        concrete output-item subtypes inherit from it).
    :type output_item_cls: type
    :param response_object_cls: The ``ResponseObject`` class.
    :type response_object_cls: type
    """
    output_item_cls.internal_metadata = property(  # type: ignore[attr-defined]
        _item_internal_metadata_get, _item_internal_metadata_set
    )
    output_item_cls.strip_internal_metadata = _item_strip_internal_metadata  # type: ignore[attr-defined]
    response_object_cls.internal_metadata = property(  # type: ignore[attr-defined]
        _response_internal_metadata_get, _response_internal_metadata_set
    )
