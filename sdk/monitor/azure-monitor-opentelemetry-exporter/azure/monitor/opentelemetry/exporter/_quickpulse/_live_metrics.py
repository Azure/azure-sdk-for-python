# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import platform

from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._quickpulse._exporter import (
    _QuickpulseExporter,
    _QuickpulseMetricReader,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import MonitoringDataPoint
from azure.monitor.opentelemetry.exporter._utils import _get_sdk_version, _populate_part_a_fields
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.sdk.resources import Resource


def enable_live_metrics(connection_string: str) -> None:
    QuickpulseManager(connection_string)


class QuickpulseManager:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls._instance = super(QuickpulseManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, connection_string: str, resource: Resource) -> None:
        self._connection_string = connection_string
        self._exporter = _QuickpulseExporter(self._connection_string)
        part_a_fields = _populate_part_a_fields(resource)
        id_generator = RandomIdGenerator()
        self._base_monitoring_data_point = MonitoringDataPoint(
            version=_get_sdk_version(),
            invariant_version=1,
            instance=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE, ""),
            role_name=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE),
            machine_name=platform.node(),
            stream_id=id_generator.generate_trace_id()
        )
        self._reader = _QuickpulseMetricReader(self._exporter, self._base_monitoring_data_point)
        