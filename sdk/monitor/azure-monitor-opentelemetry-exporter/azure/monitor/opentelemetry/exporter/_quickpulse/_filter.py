# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime, timedelta, timezone
import json
import sys
from typing import Dict, List, Optional, Union

from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk.metrics._internal.point import (
    NumberDataPoint,
    HistogramDataPoint,
)
from opentelemetry.sdk.metrics.export import MetricsData as OTMetricsData
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.util.types import Attributes

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _QUICKPULSE_METRIC_NAME_MAPPINGS,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    AggregationType,
    DerivedMetricInfo,
    DocumentIngress,
    DocumentType,
    Exception as ExceptionDocument,
    MetricPoint,
    MonitoringDataPoint,
    RemoteDependency as RemoteDependencyDocument,
    Request as RequestDocument,
    TelemetryType,
    Trace as TraceDocument,
)
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _set_quickpulse_etag,
    _set_quickpulse_derived_metric,
    _set_quickpulse_metric_filters,
)


# Updates filter configuration when etag has changed
def _update_filter_configuration(etag: str, config_bytes: bytes):
    seen_ids = set()
    # config is a byte string that when decoded is a json
    config = json.loads(config_bytes.decode("utf-8"))
    metric_filters: Dict[TelemetryType, List[DerivedMetricInfo]] = {}
    for metric_filter in config.get("Metrics", []):
        metric_info = DerivedMetricInfo.from_dict(metric_filter)
        # Skip duplicate ids
        if metric_info.id in seen_ids:
            continue
        telemetry_type: TelemetryType = TelemetryType(metric_info.telemetry_type)
        # TODO: Filter out invalid configs: telemetry type, operand
        _init_derived_metric(metric_info)
        derived_metrics = metric_filters.get(telemetry_type, [])
        derived_metrics.append(metric_info)
        metric_filters[telemetry_type] = derived_metrics
        seen_ids.add(metric_info.id)
    _set_quickpulse_metric_filters(metric_filters)
    # Update new etag
    _set_quickpulse_etag(etag)


# Initialize metric values per DerivedMetricInfo
def _init_derived_metric(filter_info: DerivedMetricInfo):
    derived_metric_agg_value = 0
    if filter_info.aggregation == AggregationType.MIN:
        derived_metric_agg_value = sys.maxsize
    elif filter_info.aggregation == AggregationType.MAX:
        derived_metric_agg_value = -sys.maxsize - 1
    elif filter_info.aggregation == AggregationType.SUM:
        derived_metric_agg_value = 0
    else:
        derived_metric_agg_value = 0
    _set_quickpulse_derived_metric(
        filter_info.id,
        filter_info.aggregation,
        derived_metric_agg_value,
    )
