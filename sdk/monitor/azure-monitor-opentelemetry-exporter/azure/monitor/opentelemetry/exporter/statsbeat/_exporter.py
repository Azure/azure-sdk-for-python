# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging

from typing import Optional, Any
from opentelemetry.sdk.metrics.export import DataPointT
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter.statsbeat._state import _STATSBEAT_METRIC_NAMES

_logger = logging.getLogger(__name__)


class _StatsBeatExporter(AzureMonitorMetricExporter):

    # pylint: disable=protected-access
    def _point_to_envelope(
        self,
        point: DataPointT,
        name: str,
        resource: Optional[Resource] = None,
        scope: Optional[InstrumentationScope] = None
    ) -> TelemetryItem:
        # map statsbeat name from OpenTelemetry name
        for ot_name, sb_name in _STATSBEAT_METRIC_NAMES:
            if name == ot_name:
                name = sb_name
                continue
        return super()._point_to_envelope(
            point,
            name,
            resource,
            scope,
        )
