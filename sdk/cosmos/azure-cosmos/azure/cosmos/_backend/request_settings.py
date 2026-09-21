# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check request setting types before passing them to the Rust binding.

Separate objects hold item, query, and resource settings. They cannot be edited
after construction. For example, max_item_count must be an integer or None,
not a Boolean. Individual settings also apply the range checks defined below;
this module does not decide whether an option applies to a particular API.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
import math
from typing import Any, ClassVar, Literal, Optional, Union, get_args, get_origin, get_type_hints
from .partition_key_input import BindingPartitionKey


_ANNOTATIONS: dict[type, dict[str, Any]] = {}


def _annotations(cls: type) -> dict[str, Any]:
    if cls not in _ANNOTATIONS:
        _ANNOTATIONS[cls] = get_type_hints(cls)
    return _ANNOTATIONS[cls]


def _matches(value: Any, annotation: Any) -> bool:
    origin, args = get_origin(annotation), get_args(annotation)
    if origin is Union:
        return any(_matches(value, arg) for arg in args)
    if origin is Literal:
        return any(type(value) is type(choice) and value == choice for choice in args)
    if origin is tuple:
        return isinstance(value, tuple) and all(_matches(item, args[0]) for item in value)
    if annotation is float:
        return type(value) is int or (type(value) is float and math.isfinite(value))
    if annotation in (bool, int, str, type(None)):
        return type(value) is annotation
    return isinstance(value, annotation)


@dataclass(frozen=True)
class _ValidatedSettings:
    def __post_init__(self) -> None:
        annotations = _annotations(type(self))
        for member in fields(self):
            value = getattr(self, member.name)
            if not _matches(value, annotations[member.name]):
                raise TypeError(f"{type(self).__name__}.{member.name} has an invalid value type")


@dataclass(frozen=True)
class HedgingSettings(_ValidatedSettings):
    enabled: bool
    threshold_ms: Optional[int] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.enabled:
            if self.threshold_ms is None or not 0 < self.threshold_ms < 2**64:
                raise ValueError("Enabled hedging requires a positive u64 threshold_ms")
        elif self.threshold_ms is not None:
            raise ValueError("Disabled hedging must not specify threshold_ms")


@dataclass(frozen=True)
class ItemSettings(_ValidatedSettings):
    if_match: Optional[str] = None
    if_none_match: Optional[str] = None
    pre_triggers: Optional[tuple[str, ...]] = None
    post_triggers: Optional[tuple[str, ...]] = None
    indexing_directive: Optional[Union[int, str]] = None
    max_staleness_ms: Optional[int] = None


@dataclass(frozen=True)
class QuerySettings(_ValidatedSettings):
    max_item_count: Optional[int] = None
    continuation: Optional[str] = None
    is_query: Optional[bool] = None
    enable_cross_partition: Optional[bool] = None
    enable_scan: Optional[bool] = None
    populate_index_metrics: Optional[bool] = None
    populate_query_metrics: Optional[bool] = None
    populate_query_advice: Optional[bool] = None
    is_query_plan: Optional[bool] = None
    supported_features: Optional[str] = None
    version: Optional[str] = None
    continuation_limit_kb: Optional[int] = None


@dataclass(frozen=True)
class ResourceSettings(_ValidatedSettings):
    container_rid: Optional[str] = None
    offer_throughput: Optional[int] = None
    autoscale_settings: Optional[str] = None
    offer_type: Optional[str] = None
    resource_token_expiry_seconds: Optional[int] = None
    enable_ru_per_minute: Optional[bool] = None
    disable_ru_per_minute: Optional[bool] = None
    enable_script_logging: Optional[bool] = None
    populate_partition_statistics: Optional[bool] = None
    populate_quota_info: Optional[bool] = None
    content_type: Optional[str] = None


@dataclass(frozen=True)
class RequestSettings(_ValidatedSettings):
    protocol_version: ClassVar[int] = 3
    priority: Optional[Literal["High", "Low"]] = None
    throughput_bucket: Optional[int] = None
    activity_id: Optional[str] = None
    correlated_activity_id: Optional[str] = None
    session_token: Optional[str] = None
    no_response: Optional[bool] = None
    excluded_locations: Optional[tuple[str, ...]] = None
    hedging: Optional[HedgingSettings] = None
    timeout_seconds: Optional[float] = None
    consistency_level: Optional[str] = None
    item: ItemSettings = field(default_factory=ItemSettings)
    query: QuerySettings = field(default_factory=QuerySettings)
    resource: ResourceSettings = field(default_factory=ResourceSettings)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.timeout_seconds is not None and not 0 < self.timeout_seconds < 2**64:
            raise ValueError("timeout_seconds must be finite, positive and less than 2**64")
        if self.throughput_bucket is not None and not 0 <= self.throughput_bucket < 2**32:
            raise ValueError("throughput_bucket must be an unsigned 32-bit integer")


def _request_settings_schema() -> dict[str, tuple[str, ...]]:
    """List setting fields so Python and the compiled binding can be compared."""
    return {
        cls.__name__: tuple(member.name for member in fields(cls))
        for cls in (RequestSettings, ItemSettings, QuerySettings, ResourceSettings, HedgingSettings, BindingPartitionKey)
    }


def native_settings_contract_error(native: Any) -> Optional[str]:
    """Return an error message if the binding expects different setting fields.

    The Rust backend saves this result and raises it when a driver is needed.
    This function does not itself raise the returned compatibility error.
    """
    exported = getattr(native, "_request_settings_schema", None)
    if exported is None:
        return "Incompatible native request protocol: rebuild azure.cosmos._rust for typed settings."
    actual = exported()
    expected = _request_settings_schema()
    if actual.keys() != expected.keys() or any(set(actual[name]) != set(fields) for name, fields in expected.items()):
        return "Python/native request settings schemas differ; rebuild azure.cosmos._rust."
    return None
