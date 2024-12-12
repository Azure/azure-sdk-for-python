# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from dataclasses import fields
from typing import Dict, List

from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    DerivedMetricInfo,
    FilterConjunctionGroupInfo,
    FilterInfo,
    PredicateType,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DATA_FIELD_NAMES,
    _TelemetryData,
)
from azure.monitor.opentelemetry.exporter._quickpulse._utils import _filter_time_stamp_to_ms


def _rename_exception_fields_for_filtering(filter_groups: FilterConjunctionGroupInfo):
    for filter in filter_groups.filters:
        if filter.field_name.startswith("Exception."):
            filter.field_name = filter.field_name.replace("Exception.", "")


def _check_metric_filters(metric_infos: List[DerivedMetricInfo], data: _TelemetryData) -> bool:
    match = False
    for metric_info in metric_infos:
        # Should only be a single `FilterConjunctionGroupInfo` in `filter_groups`
        # but we use a logical OR to match if there is more than one
        for group in metric_info.filter_groups:
            match = match or _check_filters(group.filters, data)
    return match


# pylint: disable=R0911
def _check_filters(filters: List[FilterInfo], data: _TelemetryData) -> bool:
    if not filters:
        return True
    # # All of the filters need to match for this to return true (and operation).
    for filter in filters:
        name = filter.field_name
        predicate = filter.predicate
        comparand = filter.comparand
        if name == "*":
            return _check_any_field_filter(filter, data)
        if name.startswith("CustomDimensions."):
            return _check_custom_dim_field_filter(filter, data.custom_dimensions)
        field_names = _DATA_FIELD_NAMES.get(type(data))
        if field_names is None:
            field_names = {}
        field_name = field_names.get(name.lower(), "")
        val = getattr(data, field_name, "")
        if name == "Success":
            if predicate == PredicateType.EQUAL:
                return str(val).lower() == comparand.lower()
            if predicate == PredicateType.NOT_EQUAL:
                return str(val).lower() != comparand.lower()
        elif name in ("ResultCode", "ResponseCode", "Duration"):
            try:
                val = int(val)
            except Exception:  # pylint: disable=broad-exception-caught,invalid-name
                return False
            numerical_val = _filter_time_stamp_to_ms(comparand) if name == "Duration" else int(comparand)
            if numerical_val is None:
                return False
            if predicate == PredicateType.EQUAL:
                return val == numerical_val
            if predicate == PredicateType.NOT_EQUAL:
                return val != numerical_val
            if predicate == PredicateType.GREATER_THAN:
                return val > numerical_val
            if predicate == PredicateType.GREATER_THAN_OR_EQUAL:
                return val >= numerical_val
            if predicate == PredicateType.LESS_THAN:
                return val < numerical_val
            if predicate == PredicateType.LESS_THAN_OR_EQUAL:
                return val <= numerical_val
            return False
        else:
            # string fields
            return _field_string_compare(str(val), comparand, predicate)

    return False


def _check_any_field_filter(filter: FilterInfo, data: _TelemetryData) -> bool:
    # At this point, the only predicates possible to pass in are Contains and DoesNotContain
    # At config validation time the predicate is checked to be one of these two.
    for field in fields(data):
        if field.name == "custom_dimensions":
            for val in data.custom_dimensions.values():
                if _field_string_compare(str(val), filter.comparand, filter.predicate):
                    return True
        else:
            val = getattr(data, field.name, None)  # type: ignore
            if val is not None:
                if _field_string_compare(str(val), filter.comparand, filter.predicate):
                    return True
    return False


def _check_custom_dim_field_filter(filter: FilterInfo, custom_dimensions: Dict[str, str]) -> bool:
    field = filter.field_name.replace("CustomDimensions.", "")
    value = custom_dimensions.get(field)
    if value is not None:
        return _field_string_compare(str(value), filter.comparand, filter.predicate)
    return False


def _field_string_compare(value: str, comparand: str, predicate: str) -> bool:
    if predicate == PredicateType.EQUAL:
        return value == comparand
    if predicate == PredicateType.NOT_EQUAL:
        return value != comparand
    if predicate == PredicateType.CONTAINS:
        return comparand.lower() in value.lower()
    if predicate == PredicateType.DOES_NOT_CONTAIN:
        return comparand.lower() not in value.lower()
    return False
