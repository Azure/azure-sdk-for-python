# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import shutil
import unittest
from unittest import mock

from opentelemetry import metrics
from opentelemetry.sdk import resources
from opentelemetry.sdk.metrics import (
    Counter,
    MeterProvider,
    ValueObserver,
    ValueRecorder,
)
from opentelemetry.sdk.metrics.export import ExportRecord, MetricsExportResult
from opentelemetry.sdk.metrics.export.aggregate import (
    MinMaxSumCountAggregator,
    SumAggregator,
    ValueObserverAggregator,
)
from opentelemetry.sdk.util import ns_to_iso_str

from azure.monitor.opentelemetry.exporter.export._base import ExportResult
from azure.monitor.opentelemetry.exporter.export.metrics._exporter import (
    AzureMonitorMetricsExporter,
)
from azure.monitor.opentelemetry.exporter._generated.models import (
    MetricDataPoint,
    MetricsData,
    MonitorBase,
    TelemetryItem
)
from azure.monitor.opentelemetry.exporter._utils import azure_monitor_context


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# pylint: disable=protected-access
class TestAzureMetricsExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.clear()
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = "1234abcd-5678-4efa-8abc-1234567890ab"
        cls._exporter = AzureMonitorMetricsExporter()

        metrics.set_meter_provider(MeterProvider())
        cls._meter = metrics.get_meter(__name__)
        cls._test_metric = cls._meter.create_counter(
            "testname", "testdesc", "unit", int, ["environment"]
        )
        cls._test_value_recorder = cls._meter.create_valuerecorder(
            "testname2", "testdesc", "unit", int, ["environment"]
        )
        cls._test_obs = cls._meter.register_valueobserver(
            lambda x: x,
            "testname3",
            "testdesc",
            "unit",
            int,
            ["environment"],
        )
        cls._test_labels = tuple({"environment": "staging"}.items())

    @classmethod
    def tearDownClass(cls):
        metrics._METER_PROVIDER = None
        shutil.rmtree(cls._exporter.storage._path, True)

    def test_constructor(self):
        """Test the constructor."""
        exporter = AzureMonitorMetricsExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )

    @mock.patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorMetricsExporter._transmit"
    )
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorMetricsExporter._metric_to_envelope"
    )
    def test_export(self, mte, transmit):
        record = ExportRecord(
            SumAggregator(), self._test_labels, self._test_metric, None
        )
        exporter = self._exporter
        mte.return_value = mock.Mock()
        transmit.return_value = ExportResult.SUCCESS
        result = exporter.export([record])
        self.assertEqual(result, MetricsExportResult.SUCCESS)

    @mock.patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorMetricsExporter._transmit"
    )
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorMetricsExporter._metric_to_envelope"
    )
    def test_export_failed_retryable(self, mte, transmit):
        record = ExportRecord(
            SumAggregator(), self._test_labels, self._test_metric, None
        )
        exporter = self._exporter
        transmit.return_value = ExportResult.FAILED_RETRYABLE
        mte.return_value = mock.Mock()
        storage_mock = mock.Mock()
        exporter.storage.put = storage_mock
        result = exporter.export([record])
        self.assertEqual(result, MetricsExportResult.FAILURE)
        self.assertEqual(storage_mock.call_count, 1)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.logger")
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorMetricsExporter._transmit"
    )
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorMetricsExporter._metric_to_envelope"
    )
    def test_export_exception(self, mte, transmit, logger_mock):
        record = ExportRecord(
            SumAggregator(), self._test_labels, self._test_metric, None
        )
        exporter = self._exporter
        mte.return_value = mock.Mock()
        transmit.side_effect = throw(Exception)
        result = exporter.export([record])
        self.assertEqual(result, MetricsExportResult.FAILURE)
        self.assertEqual(logger_mock.exception.called, True)

    def test_metric_to_envelope_none(self):
        exporter = self._exporter
        self.assertIsNone(exporter._metric_to_envelope(None))

    def test_metric_to_envelope(self):
        aggregator = SumAggregator()
        aggregator.update(123)
        aggregator.take_checkpoint()
        record = ExportRecord(self._test_metric, self._test_labels, aggregator, None)
        exporter = self._exporter
        envelope = exporter._metric_to_envelope(record)
        self.assertIsInstance(envelope, TelemetryItem)
        self.assertEqual(envelope.version, 1)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(
            envelope.time, ns_to_iso_str(aggregator.last_update_timestamp)
        )
        self.assertEqual(envelope.sample_rate, 100)
        self.assertEqual(envelope.sequence, None)
        self.assertEqual(envelope.instrumentation_key, "1234abcd-5678-4efa-8abc-1234567890ab")

        self.assertIsInstance(envelope.data, MonitorBase)
        self.assertIsInstance(envelope.data.base_data, MetricsData)
        self.assertEqual(envelope.data.base_data.version, 2)
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertIsInstance(envelope.data.base_data.metrics[0], MetricDataPoint)
        self.assertEqual(envelope.data.base_data.metrics[0].namespace, "testdesc")
        self.assertEqual(envelope.data.base_data.metrics[0].name, "testname")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 123)
        self.assertEqual(
            envelope.data.base_data.properties["environment"], "staging"
        )

    def test_metric_to_envelope_tags(self):
        aggregator = SumAggregator()
        record = ExportRecord(self._test_metric, self._test_labels, aggregator, None)
        exporter = self._exporter
        envelope = exporter._metric_to_envelope(record)
        self.assertIsNone(envelope.tags.get("ai.cloud.role"))
        self.assertIsNone(envelope.tags.get("ai.cloud.roleInstance"))
        self.assertIsNotNone(envelope.tags.get("ai.device.id"))
        self.assertIsNotNone(envelope.tags.get("ai.device.locale"))
        self.assertIsNotNone(envelope.tags.get("ai.device.osVersion"))
        self.assertIsNotNone(envelope.tags.get("ai.device.type"))
        self.assertIsNotNone(envelope.tags.get("ai.internal.sdkVersion"))

        record.resource = resources.Resource(
            {"service.name": "testServiceName",
             "service.namespace": "testServiceNamespace",
             "service.instance.id": "testServiceInstanceId"})
        envelope = exporter._metric_to_envelope(record)
        self.assertEqual(envelope.tags.get("ai.cloud.role"), "testServiceNamespace.testServiceName")
        self.assertEqual(envelope.tags.get(
            "ai.cloud.roleInstance"), "testServiceInstanceId")

    def test_observer_to_envelope(self):
        aggregator = ValueObserverAggregator()
        aggregator.update(123)
        aggregator.take_checkpoint()
        record = ExportRecord(self._test_obs, self._test_labels, aggregator, None)
        exporter = self._exporter
        envelope = exporter._metric_to_envelope(record)
        self.assertIsInstance(envelope, TelemetryItem)
        self.assertEqual(envelope.version, 1)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(
            envelope.time, ns_to_iso_str(aggregator.last_update_timestamp)
        )
        self.assertEqual(envelope.sample_rate, 100)
        self.assertEqual(envelope.sequence, None)
        self.assertEqual(envelope.instrumentation_key, "1234abcd-5678-4efa-8abc-1234567890ab")

        self.assertIsInstance(envelope.data, MonitorBase)
        self.assertIsInstance(envelope.data.base_data, MetricsData)
        self.assertEqual(envelope.data.base_data.version, 2)
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertIsInstance(envelope.data.base_data.metrics[0], MetricDataPoint)
        self.assertEqual(envelope.data.base_data.metrics[0].namespace, "testdesc")
        self.assertEqual(envelope.data.base_data.metrics[0].name, "testname3")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 123)
        self.assertEqual(
            envelope.data.base_data.properties["environment"], "staging"
        )

    def test_value_recorder_to_envelope(self):
        aggregator = MinMaxSumCountAggregator()
        aggregator.update(100)
        aggregator.update(300)
        aggregator.take_checkpoint()
        record = ExportRecord(
            self._test_value_recorder, self._test_labels, aggregator, None
        )
        exporter = self._exporter
        envelope = exporter._metric_to_envelope(record)
        self.assertIsInstance(envelope, TelemetryItem)
        self.assertEqual(envelope.version, 1)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(
            envelope.time, ns_to_iso_str(aggregator.last_update_timestamp)
        )
        self.assertEqual(envelope.sample_rate, 100)
        self.assertEqual(envelope.sequence, None)
        self.assertEqual(envelope.instrumentation_key, "1234abcd-5678-4efa-8abc-1234567890ab")

        self.assertIsInstance(envelope.data, MonitorBase)
        self.assertIsInstance(envelope.data.base_data, MetricsData)
        self.assertEqual(envelope.data.base_data.version, 2)
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertIsInstance(envelope.data.base_data.metrics[0], MetricDataPoint)
        self.assertEqual(envelope.data.base_data.metrics[0].namespace, "testdesc")
        self.assertEqual(envelope.data.base_data.metrics[0].name, "testname2")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 400)
        self.assertEqual(envelope.data.base_data.metrics[0].min, 100)
        self.assertEqual(envelope.data.base_data.metrics[0].max, 300)
        self.assertEqual(envelope.data.base_data.metrics[0].count, 2)
        self.assertEqual(
            envelope.data.base_data.properties["environment"], "staging"
        )
