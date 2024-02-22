# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import platform
import unittest
from unittest import mock

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource, ResourceAttributes

from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import MonitoringDataPoint
from azure.monitor.opentelemetry.exporter._quickpulse._exporter import (
    _QuickpulseExporter,
    _QuickpulseMetricReader,
)
from azure.monitor.opentelemetry.exporter._quickpulse._live_metrics import (
    enable_live_metrics,
    _QuickpulseManager,
)
from azure.monitor.opentelemetry.exporter._utils import (
    _get_sdk_version,
    _populate_part_a_fields,
)


class TestLiveMetrics(unittest.TestCase):

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._QuickpulseManager")
    def test_enable_live_metrics(self, manager_mock):
        mock_resource = mock.Mock()
        enable_live_metrics(
            connection_string="test_cs",
            resource=mock_resource,
        )
        manager_mock.assert_called_with("test_cs", mock_resource)


class TestQuickpulseManager(unittest.TestCase):

    @mock.patch("opentelemetry.sdk.metrics.MeterProvider.__new__")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._QuickpulseMetricReader.__new__")
    @mock.patch("opentelemetry.sdk.trace.id_generator.RandomIdGenerator.__new__")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._QuickpulseExporter.__new__")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated.models.MonitoringDataPoint.__new__")
    def test_init(self, point_mock, exporter_mock, generator_mock, reader_mock, provider_mock):
        point_inst_mock = mock.Mock()
        point_mock.return_value = point_inst_mock
        exporter_inst_mock = mock.Mock()
        exporter_mock.return_value = exporter_inst_mock
        reader_inst_mock = mock.Mock()
        reader_mock.return_value = reader_inst_mock
        provider_inst_mock = mock.Mock()
        provider_mock.return_value = provider_inst_mock
        generator_inst_mock = mock.Mock()
        generator_mock.return_value = generator_inst_mock
        generator_inst_mock.generate_trace_id.return_value = "test_trace_id"
        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_INSTANCE_ID: "test_instance",
                ResourceAttributes.SERVICE_NAME: "test_service",
            }
        )
        part_a_fields = _populate_part_a_fields(resource)
        qpm = _QuickpulseManager(
            connection_string="test_cs",
            resource=resource,
        )
        self.assertEqual(qpm._base_monitoring_data_point, point_inst_mock)
        self.assertEqual(qpm._exporter, exporter_inst_mock)
        self.assertEqual(qpm._reader, reader_inst_mock)
        self.assertEqual(qpm._meter_provider, provider_inst_mock)
        point_mock.assert_called_with(
            MonitoringDataPoint,
            version=_get_sdk_version(),
            invariant_version=1,
            instance=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE, ""),
            role_name=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE, ""),
            machine_name=platform.node(),
            stream_id="test_trace_id",
        )
        exporter_mock.assert_called_with(_QuickpulseExporter, "test_cs")
        reader_mock.assert_called_with(_QuickpulseMetricReader, exporter_inst_mock, point_inst_mock)
        provider_mock.assert_called_with(MeterProvider, [reader_inst_mock])
