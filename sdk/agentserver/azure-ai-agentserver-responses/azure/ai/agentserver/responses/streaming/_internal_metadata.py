# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Response-level internal metadata backed by the public metadata map."""

from __future__ import annotations

import json
from collections.abc import Iterator, MutableMapping
from typing import Any

_RESERVED_KEY = "_internal_metadata"
_MAX_METADATA_KEYS = 16
_MAX_VALUE_LEN = 512


class _ResponseInternalMetadataView(MutableMapping[str, Any]):
    """Live view over JSON-encoded response-level internal metadata."""

    __slots__ = ("_response",)

    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response
        metadata = response.get("metadata")
        if isinstance(metadata, dict) and isinstance(metadata.get(_RESERVED_KEY), dict):
            self._store(dict(metadata[_RESERVED_KEY]))

    def _decode(self) -> dict[str, Any]:
        metadata = self._response.get("metadata")
        if not isinstance(metadata, dict):
            return {}
        raw = metadata.get(_RESERVED_KEY)
        if isinstance(raw, dict):
            return dict(raw)
        if not isinstance(raw, str) or not raw:
            return {}
        try:
            decoded = json.loads(raw)
        except (TypeError, ValueError):
            return {}
        return decoded if isinstance(decoded, dict) else {}

    def _store(self, value: dict[str, Any]) -> None:
        metadata = self._response.get("metadata")
        if not value:
            if isinstance(metadata, dict):
                metadata.pop(_RESERVED_KEY, None)
            return

        encoded = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        if len(encoded) > _MAX_VALUE_LEN:
            raise ValueError(
                f"internal_metadata encodes to {len(encoded)} chars, exceeding the "
                f"{_MAX_VALUE_LEN}-char limit of the response metadata value"
            )

        if not isinstance(metadata, dict):
            metadata = {}
            self._response["metadata"] = metadata
        projected_key_count = len(metadata) + (0 if _RESERVED_KEY in metadata else 1)
        if projected_key_count > _MAX_METADATA_KEYS:
            raise ValueError(
                f"cannot add internal_metadata: response metadata already has "
                f"{len(metadata)} keys (limit {_MAX_METADATA_KEYS})"
            )
        metadata[_RESERVED_KEY] = encoded

    def __getitem__(self, key: str) -> Any:
        return self._decode()[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if not isinstance(key, str):
            raise TypeError(f"internal_metadata keys must be str, got {type(key).__name__}")
        metadata = self._decode()
        metadata[key] = value
        self._store(metadata)

    def __delitem__(self, key: str) -> None:
        metadata = self._decode()
        del metadata[key]
        self._store(metadata)

    def __iter__(self) -> Iterator[str]:
        return iter(self._decode())

    def __len__(self) -> int:
        return len(self._decode())
