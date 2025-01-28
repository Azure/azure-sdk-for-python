# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import List, Optional, Tuple

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _QUICKPULSE_PROJECTION_COUNT,
    _QUICKPULSE_PROJECTION_CUSTOM,
    _QUICKPULSE_PROJECTION_DURATION,
    _QUICKPULSE_PROJECTION_MAX_VALUE,
    _QUICKPULSE_PROJECTION_MIN_VALUE,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    AggregationType,
    DerivedMetricInfo,
)
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _get_quickpulse_projection_map,
    _set_quickpulse_projection_map,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DependencyData,
    _RequestData,
    _TelemetryData,
)


# Initialize metric projections per DerivedMetricInfo
def _init_derived_metric_projection(filter_info: DerivedMetricInfo):
    derived_metric_agg_value = 0
    if filter_info.aggregation == AggregationType.MIN:
        derived_metric_agg_value = _QUICKPULSE_PROJECTION_MAX_VALUE
    elif filter_info.aggregation == AggregationType.MAX:
        derived_metric_agg_value = _QUICKPULSE_PROJECTION_MIN_VALUE
    elif filter_info.aggregation == AggregationType.SUM:
        derived_metric_agg_value = 0
    elif filter_info.aggregation == AggregationType.AVG:
        derived_metric_agg_value = 0
    _set_quickpulse_projection_map(
        filter_info.id,
        AggregationType(filter_info.aggregation),
        derived_metric_agg_value,
        0,
    )


# Create projections based off of DerivedMetricInfos and current data being processed
def _create_projections(metric_infos: List[DerivedMetricInfo], data: _TelemetryData):
    for metric_info in metric_infos:
        value = 0
        if metric_info.projection == _QUICKPULSE_PROJECTION_COUNT:
            value = 1
        elif metric_info.projection == _QUICKPULSE_PROJECTION_DURATION:
            if isinstance(data, (_DependencyData, _RequestData)):
                value = data.duration  # type: ignore
            else:
                # Duration only supported for Dependency and Requests
                continue
        elif metric_info.projection.startswith(_QUICKPULSE_PROJECTION_CUSTOM):
            key = metric_info.projection.split(_QUICKPULSE_PROJECTION_CUSTOM, 1)[1].strip()
            dim_value = data.custom_dimensions.get(key, 0)
            if dim_value is None:
                continue
            try:
                value = float(dim_value)  # type: ignore
            except ValueError:
                continue
        else:
            continue

        aggregate: Optional[Tuple[float, int]] = _calculate_aggregation(
            AggregationType(metric_info.aggregation),
            metric_info.id,
            value,
        )
        if aggregate:
            _set_quickpulse_projection_map(
                metric_info.id,
                AggregationType(metric_info.aggregation),
                aggregate[0],
                aggregate[1],
            )


# Calculate aggregation based off of previous projection value, aggregation type of a specific metric filter
# Return type is a Tuple of (value, count)
def _calculate_aggregation(aggregation: AggregationType, id: str, value: float) -> Optional[Tuple[float, int]]:
    projection: Optional[Tuple[AggregationType, float, int]] = _get_quickpulse_projection_map().get(id)
    if projection:
        prev_value = projection[1]
        prev_count = projection[2]
        if aggregation == AggregationType.SUM:
            return (prev_value + value, prev_count + 1)
        if aggregation == AggregationType.MIN:
            return (min(prev_value, value), prev_count + 1)
        if aggregation == AggregationType.MAX:
            return (max(prev_value, value), prev_count + 1)
        return (prev_value + value, prev_count + 1)
    return None
