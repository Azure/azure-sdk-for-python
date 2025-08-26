# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Optional
from opentelemetry.sdk.metrics.export import DataPointT
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from azure.monitor.opentelemetry.exporter._constants import _STATSBEAT_METRIC_NAME_MAPPINGS


class _StatsBeatExporter:
    def __init__(self, **kwargs):
        # Create the actual exporter using delayed import
        from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

        self._exporter = AzureMonitorMetricExporter(**kwargs)

    def _point_to_envelope(
        self,
        point: DataPointT,
        name: str,
        resource: Optional[Resource] = None,
        scope: Optional[InstrumentationScope] = None,
    ) -> Optional[TelemetryItem]:
        # map statsbeat name from OpenTelemetry name
        name = _STATSBEAT_METRIC_NAME_MAPPINGS[name]
        return self._exporter._point_to_envelope(
            point,
            name,
            resource,
            None,
        )

    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped exporter."""
        return getattr(self._exporter, name)
