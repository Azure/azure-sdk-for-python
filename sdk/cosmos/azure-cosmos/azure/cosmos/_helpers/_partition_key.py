# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Normalize public partition keys without encoding an internal HTTP header."""

from __future__ import annotations

import json
from typing import Any, Sequence

from .._backend.partition_key_input import BindingPartitionKey, UNDEFINED_PARTITION_KEY
from ..partition_key import NonePartitionKeyValue, _Empty, _Undefined
from .._backend.partition_key_input import PartitionKeyComponent
from ._wire_encoding import normalize_utf16_surrogates


def _scalar(value: Any) -> PartitionKeyComponent:
    if value is None:
        return None
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, str):
        text = str.__str__(value)
        return text if text.isascii() else normalize_utf16_surrogates(text)
    if isinstance(value, int):
        return int.__int__(value)
    if isinstance(value, float):
        return float.__float__(value)
    if isinstance(value, dict) and not value:
        return UNDEFINED_PARTITION_KEY
    raise TypeError("Unsupported partition-key component type")


def normalize_partition_key(value: Any) -> BindingPartitionKey:
    """Preserve point/feed-range sentinel rules, including empty-sequence provenance."""
    if isinstance(value, _Undefined):
        return BindingPartitionKey("components", (UNDEFINED_PARTITION_KEY,))
    if isinstance(value, _Empty) or value is NonePartitionKeyValue:
        return BindingPartitionKey("empty_sentinel")
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if not value:
            return BindingPartitionKey("empty_sequence")
        return BindingPartitionKey(
            "components",
            tuple(
                (
                    None
                    if isinstance(component, (_Empty, _Undefined))
                    else _scalar(component)
                )
                for component in value
            ),
        )
    return BindingPartitionKey("components", (_scalar(value),))


def query_partition_key_components(components: Sequence[Any]) -> BindingPartitionKey:
    """Query/change-feed normalization retains undefined hierarchical components."""
    return BindingPartitionKey(
        "components",
        tuple(
            (
                UNDEFINED_PARTITION_KEY
                if isinstance(value, _Undefined)
                else None if isinstance(value, _Empty) else _scalar(value)
            )
            for value in components
        ),
    )


def parse_customer_partition_key_header(header: str) -> BindingPartitionKey:
    """Decode an explicitly supplied HTTP header, never an internally serialized key."""
    values = json.loads(header)
    if not isinstance(values, list):
        raise ValueError("Partition-key header must contain a JSON array")
    if not values:
        return BindingPartitionKey("cross_partition")
    return normalize_partition_key(values)


def partition_key_bookmark_value(key: BindingPartitionKey) -> str:
    """Keep existing persisted bookmark identities; this is not the native transport."""
    if key.kind != "components":
        raise ValueError("A scoped bookmark requires partition-key components")
    return json.dumps(
        [{} if value is UNDEFINED_PARTITION_KEY else value for value in key.values],
        separators=(",", ":"),
        allow_nan=False,
    )
