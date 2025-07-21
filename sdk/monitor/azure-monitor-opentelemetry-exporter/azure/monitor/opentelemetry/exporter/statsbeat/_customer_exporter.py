# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from typing import Optional
from opentelemetry.sdk.metrics.export import DataPointT
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from azure.monitor.opentelemetry.exporter.export.metrics._exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem


class _CustomerStatsBeatExporter(AzureMonitorMetricExporter):
    def _is_customer_stats_exporter(self) -> bool:
        return True

    def _point_to_envelope(
        self,
        point: DataPointT,
        name: str,
        resource: Optional[Resource] = None,
        scope: Optional[InstrumentationScope] = None,
    ) -> Optional[TelemetryItem]:
        return super()._point_to_envelope(
            point,
            name,
            resource,
            None,
        )
