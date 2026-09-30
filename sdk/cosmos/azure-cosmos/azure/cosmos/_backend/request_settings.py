# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check Python wrapper request settings before calling the binding.

Separate objects hold item, query, and resource settings. They cannot be edited
after construction. For example, max_item_count must be an integer or None,
not a Boolean. Individual settings also apply the range checks defined below;
this module does not decide whether an option applies to a particular API.
Checks are explicit; request construction does not resolve type annotations.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
import math
from typing import Any, ClassVar, Literal, NoReturn, Optional, Union
from .partition_key_input import BindingPartitionKey


@dataclass(frozen=True)
class _ValidatedSettings:
    def _invalid_type(self, name: str) -> NoReturn:
        raise TypeError(f"{type(self).__name__}.{name} has an invalid value type")

    def _check_type(self, name: str, value: Any, expected: type, *, optional: bool = True) -> None:
        if (value is not None or not optional) and type(value) is not expected:
            self._invalid_type(name)

    def _check_strings(self, name: str, value: Any) -> None:
        if value is not None and (
            not isinstance(value, tuple) or any(type(item) is not str for item in value)
        ):
            self._invalid_type(name)

    def _check_number(self, name: str, value: Any) -> None:
        if type(value) is not int and (type(value) is not float or not math.isfinite(value)):
            self._invalid_type(name)


@dataclass(frozen=True)
class HedgingSettings(_ValidatedSettings):
    enabled: bool
    threshold_ms: Optional[int] = None

    def __post_init__(self) -> None:
        self._check_type("enabled", self.enabled, bool, optional=False)
        self._check_type("threshold_ms", self.threshold_ms, int)
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

    def __post_init__(self) -> None:
        self._check_type("if_match", self.if_match, str)
        self._check_type("if_none_match", self.if_none_match, str)
        self._check_strings("pre_triggers", self.pre_triggers)
        self._check_strings("post_triggers", self.post_triggers)
        if self.indexing_directive is not None and type(self.indexing_directive) not in (int, str):
            self._invalid_type("indexing_directive")
        self._check_type("max_staleness_ms", self.max_staleness_ms, int)


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

    def __post_init__(self) -> None:
        self._check_type("max_item_count", self.max_item_count, int)
        self._check_type("continuation", self.continuation, str)
        self._check_type("is_query", self.is_query, bool)
        self._check_type("enable_cross_partition", self.enable_cross_partition, bool)
        self._check_type("enable_scan", self.enable_scan, bool)
        self._check_type("populate_index_metrics", self.populate_index_metrics, bool)
        self._check_type("populate_query_metrics", self.populate_query_metrics, bool)
        self._check_type("populate_query_advice", self.populate_query_advice, bool)
        self._check_type("is_query_plan", self.is_query_plan, bool)
        self._check_type("supported_features", self.supported_features, str)
        self._check_type("version", self.version, str)
        self._check_type("continuation_limit_kb", self.continuation_limit_kb, int)


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

    def __post_init__(self) -> None:
        self._check_type("container_rid", self.container_rid, str)
        self._check_type("offer_throughput", self.offer_throughput, int)
        self._check_type("autoscale_settings", self.autoscale_settings, str)
        self._check_type("offer_type", self.offer_type, str)
        self._check_type("resource_token_expiry_seconds", self.resource_token_expiry_seconds, int)
        self._check_type("enable_ru_per_minute", self.enable_ru_per_minute, bool)
        self._check_type("disable_ru_per_minute", self.disable_ru_per_minute, bool)
        self._check_type("enable_script_logging", self.enable_script_logging, bool)
        self._check_type("populate_partition_statistics", self.populate_partition_statistics, bool)
        self._check_type("populate_quota_info", self.populate_quota_info, bool)
        self._check_type("content_type", self.content_type, str)


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
        if self.priority is not None and (
            type(self.priority) is not str or self.priority not in ("High", "Low")
        ):
            self._invalid_type("priority")
        self._check_type("throughput_bucket", self.throughput_bucket, int)
        self._check_type("activity_id", self.activity_id, str)
        self._check_type("correlated_activity_id", self.correlated_activity_id, str)
        self._check_type("session_token", self.session_token, str)
        self._check_type("no_response", self.no_response, bool)
        self._check_strings("excluded_locations", self.excluded_locations)
        if self.hedging is not None and not isinstance(self.hedging, HedgingSettings):
            self._invalid_type("hedging")
        if self.timeout_seconds is not None:
            self._check_number("timeout_seconds", self.timeout_seconds)
        self._check_type("consistency_level", self.consistency_level, str)
        if not isinstance(self.item, ItemSettings):
            self._invalid_type("item")
        if not isinstance(self.query, QuerySettings):
            self._invalid_type("query")
        if not isinstance(self.resource, ResourceSettings):
            self._invalid_type("resource")
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


def binding_settings_contract_error(binding: Any) -> Optional[str]:
    """Return an error message if the binding expects different setting fields.

    The Python wrapper saves this result and raises it before driver acquisition.
    This function does not itself raise the returned compatibility error.
    """
    exported = getattr(binding, "_request_settings_schema", None)
    if exported is None:
        return "Incompatible native request protocol: rebuild azure.cosmos._rust for typed settings."
    actual = exported()
    expected = _request_settings_schema()
    if actual.keys() != expected.keys() or any(set(actual[name]) != set(fields) for name, fields in expected.items()):
        return "Python/native request settings schemas differ; rebuild azure.cosmos._rust."
    return None
