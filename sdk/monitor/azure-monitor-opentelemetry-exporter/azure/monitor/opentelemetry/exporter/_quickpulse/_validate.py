# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    DerivedMetricInfo,
    DocumentFilterConjunctionGroupInfo,
    FilterInfo,
    PredicateType,
    TelemetryType,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DEPENDENCY_DATA_FIELD_NAMES,
    _KNOWN_STRING_FIELD_NAMES,
    _REQUEST_DATA_FIELD_NAMES,
)
from azure.monitor.opentelemetry.exporter._quickpulse._utils import _filter_time_stamp_to_ms


def _validate_derived_metric_info(metric_info: DerivedMetricInfo) -> bool:
    if not _validate_telemetry_type(metric_info.telemetry_type):
        return False
    if not _validate_custom_metric_projection(metric_info):
        return False
    # Validate filters
    for filter_group in metric_info.filter_groups:
        for filter in filter_group.filters:
            # Validate field names to telemetry type
            # Validate predicate and comparands
            if not _validate_filter_field_name(filter.field_name, metric_info.telemetry_type) or not \
                _validate_filter_predicate_and_comparand(filter):
                return False
    return True


def _validate_document_filter_group_info(doc_filter_group: DocumentFilterConjunctionGroupInfo) -> bool:
    if not _validate_telemetry_type(doc_filter_group.telemetry_type):
        return False
    # Validate filters
    for filter in doc_filter_group.filters.filters:
        # Validate field names to telemetry type
        # Validate predicate and comparands
        if not _validate_filter_field_name(filter.field_name, doc_filter_group.telemetry_type) or not \
            _validate_filter_predicate_and_comparand(filter):
            return False
    return True


def _validate_telemetry_type(telemetry_type: str) -> bool:
     # Validate telemetry type
    try:
        telemetry_type = TelemetryType(telemetry_type)
    except Exception:  # pylint: disable=broad-except
        return False
    # Only REQUEST, DEPENDENCY, EXCEPTION, TRACE are supported
    # No filtering options in UX for PERFORMANCE_COUNTERS
    if telemetry_type not in (
        TelemetryType.REQUEST,
        TelemetryType.DEPENDENCY,
        TelemetryType.EXCEPTION,
        TelemetryType.TRACE,
    ):
        return False
    return True


def _validate_custom_metric_projection(metric_info: DerivedMetricInfo) -> bool:
    # Check for CustomMetric projection
    if metric_info.projection and metric_info.projection.startswith("CustomMetrics."):
        return False
    return True


# pylint: disable=R0911
def _validate_filter_field_name(name: str, telemetry_type: str) -> bool:
    if not name:
        return False
    if name.startswith("CustomMetrics."):
        return False
    if name.startswith("CustomDimensions.") or name == "*":
        return True
    name = name.lower()
    if telemetry_type == TelemetryType.DEPENDENCY.value:
        if name not in _DEPENDENCY_DATA_FIELD_NAMES:
            return False
    elif telemetry_type == TelemetryType.REQUEST.value:
        if name not in _REQUEST_DATA_FIELD_NAMES:
            return False
    elif telemetry_type == TelemetryType.EXCEPTION.value:
        if name not in ("exception.message", "exception.stacktrace"):
            return False
    elif telemetry_type == TelemetryType.TRACE.value:
        if name != "message":
            return False
    else:
        return True
    return True


# pylint: disable=R0911
def _validate_filter_predicate_and_comparand(filter: FilterInfo) -> bool:
    name = filter.field_name
    comparand = filter.comparand
    # Validate predicate type
    try:
        predicate = PredicateType(filter.predicate)
    except Exception:  # pylint: disable=broad-except
        return False
    if not comparand:
        return False
    if name == "*" and predicate not in (PredicateType.CONTAINS, PredicateType.DOES_NOT_CONTAIN):
        return False
    if name in ("ResultCode", "ResponseCode", "Duration"):
        if predicate in (PredicateType.CONTAINS, PredicateType.DOES_NOT_CONTAIN):
            return False
        if name == "Duration":
            # Duration comparand should be a string timestamp
            if _filter_time_stamp_to_ms(comparand) is None:
                return False
        else:
            try:
                # Response/ResultCode comparand should be interpreted as integer
                int(comparand)
            except Exception:  # pylint: disable=broad-except
                return False
    elif name == "Success":
        if predicate not in (PredicateType.EQUAL, PredicateType.NOT_EQUAL):
            return False
        comparand = comparand.lower()
        if comparand not in ("true", "false"):
            return False
    elif name in _KNOWN_STRING_FIELD_NAMES or name.startswith("CustomDimensions."):
        if predicate in (
            PredicateType.GREATER_THAN,
            PredicateType.GREATER_THAN_OR_EQUAL,
            PredicateType.LESS_THAN,
            PredicateType.LESS_THAN_OR_EQUAL,
        ):
            return False
    return True
