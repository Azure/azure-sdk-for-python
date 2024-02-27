# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import platform
from typing import Any, Optional

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.sdk.resources import Resource
from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._quickpulse._exporter import (
    _QuickpulseExporter,
    _QuickpulseMetricReader,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import MonitoringDataPoint
from azure.monitor.opentelemetry.exporter._utils import (
    _get_sdk_version,
    _populate_part_a_fields,
    Singleton,
)


def enable_live_metrics(**kwargs: Any) -> None:
    """Azure Monitor base exporter for OpenTelemetry.

    :keyword str connection_string: The connection string used for your Application Insights resource.
    :keyword Resource resource: The OpenTelemetry Resource used for this Python application.
    :rtype: None
    """
    _QuickpulseManager(kwargs.get('connection_string'), kwargs.get('resource'))


class _QuickpulseManager(metaclass=Singleton):

    def __init__(self, connection_string: Optional[str], resource: Optional[Resource]) -> None:
        self._exporter = _QuickpulseExporter(connection_string)
        part_a_fields = {}
        if resource:
            part_a_fields = _populate_part_a_fields(resource)
        id_generator = RandomIdGenerator()
        self._base_monitoring_data_point = MonitoringDataPoint(
            version=_get_sdk_version(),
            invariant_version=1,
            instance=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE, ""),
            role_name=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE, ""),
            machine_name=platform.node(),
            stream_id=str(id_generator.generate_trace_id()),
        )
        self._reader = _QuickpulseMetricReader(self._exporter, self._base_monitoring_data_point)
        self._meter_provider = MeterProvider([self._reader])
