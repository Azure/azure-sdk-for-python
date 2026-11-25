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
    """Keep supplied values and missing-key instructions distinct for the binding.

    For example, "customer-17" becomes one component. An empty sequence and
    NonePartitionKeyValue keep different kinds so later handling can distinguish
    the original inputs.

    :param Any value: Public scalar, hierarchical key, or missing-key sentinel.
    :return: Typed binding input retaining the supplied key's kind.
    :rtype: ~azure.cosmos._backend.partition_key_input.BindingPartitionKey
    """
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
    """Query/change-feed normalization retains undefined hierarchical components.

    :param Sequence[Any] components: Hierarchical key components, including missing-key sentinels.
    :return: Typed binding components with undefined and null values kept distinct.
    :rtype: ~azure.cosmos._backend.partition_key_input.BindingPartitionKey
    """
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


def normalize_feed_range_partition_key(value: Any) -> BindingPartitionKey:
    """Keep missing range components distinct from JSON null without changing item inputs.

    :param Any value: Public partition key used to derive a feed range.
    :return: Typed binding input preserving undefined hierarchical components.
    :rtype: ~azure.cosmos._backend.partition_key_input.BindingPartitionKey
    """
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        return normalize_partition_key(value)
    return BindingPartitionKey(
        "components",
        tuple(
            UNDEFINED_PARTITION_KEY
            if component is NonePartitionKeyValue or isinstance(component, _Undefined)
            else None if isinstance(component, _Empty) else _scalar(component)
            for component in value
        ),
    )


def parse_customer_partition_key_header(header: str) -> BindingPartitionKey:
    """Decode an explicitly supplied HTTP header, never an internally serialized key.

    :param str header: Customer-supplied JSON array of partition-key components.
    :return: Normalized components, or a cross-partition input for an empty array.
    :rtype: ~azure.cosmos._backend.partition_key_input.BindingPartitionKey
    """
    values = json.loads(header)
    if not isinstance(values, list):
        raise ValueError("Partition-key header must contain a JSON array")
    if not values:
        return BindingPartitionKey("cross_partition")
    return normalize_partition_key(values)


def serialize_partition_key_for_continuation(key: BindingPartitionKey) -> str:
    """Serialize components for continuation compatibility, not a binding request.

    For example, ("customer-17",) becomes '["customer-17"]'. Preserve this
    representation so already-saved continuation tokens keep the same identity.

    :param BindingPartitionKey key: Component-based binding input to serialize.
    :return: Compact JSON array with undefined components represented as empty objects.
    :rtype: str
    """
    if key.kind != "components":
        raise ValueError("A scoped bookmark requires partition-key components")
    return json.dumps(
        [{} if value is UNDEFINED_PARTITION_KEY else value for value in key.values],
        separators=(",", ":"),
        allow_nan=False,
    )
