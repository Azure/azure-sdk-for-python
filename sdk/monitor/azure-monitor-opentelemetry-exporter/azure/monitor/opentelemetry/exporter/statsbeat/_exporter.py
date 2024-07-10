# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Optional
from opentelemetry.sdk.metrics.export import DataPointT
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter._constants import _STATSBEAT_METRIC_NAME_MAPPINGS


class _StatsBeatExporter(AzureMonitorMetricExporter):

    # pylint: disable=protected-access
    def _point_to_envelope(
        self,
        point: DataPointT,
        name: str,
        resource: Optional[Resource] = None,
        scope: Optional[InstrumentationScope] = None
    ) -> Optional[TelemetryItem]:
        # map statsbeat name from OpenTelemetry name
        name = _STATSBEAT_METRIC_NAME_MAPPINGS[name]
        return super()._point_to_envelope(
            point,
            name,
            resource,
            None,
        )
