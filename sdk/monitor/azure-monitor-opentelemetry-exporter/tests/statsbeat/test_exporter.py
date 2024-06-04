# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import shutil
import unittest
from unittest import mock
from datetime import datetime

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics.export import NumberDataPoint

from azure.core.exceptions import HttpResponseError
from azure.monitor.opentelemetry.exporter.export._base import ExportResult
from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter.statsbeat._state import _STATSBEAT_STATE
from azure.monitor.opentelemetry.exporter._constants import _STATSBEAT_METRIC_NAME_MAPPINGS
from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient

from azure.monitor.opentelemetry.exporter._generated.models import (
    TelemetryErrorDetails,
    TelemetryItem,
    TrackResponse,
)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


def clean_folder(folder):
    if os.path.isfile(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


# pylint: disable=protected-access
class TestStatsbeatExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.clear()
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "false"
        cls._exporter = _StatsBeatExporter(
            disable_offline_storage=True,
        )
        cls._envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now())]

    @mock.patch(
        'azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics')
    def test_init(self, collect_mock):
        exporter = _StatsBeatExporter(disable_offline_storage=True)
        self.assertFalse(exporter._should_collect_stats())
        collect_mock.assert_not_called()

    def test_point_to_envelope(self):
        resource = Resource.create(attributes={"asd":"test_resource"})
        point=NumberDataPoint(
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=10,
            attributes={},
        )
        for ot_name, sb_name in _STATSBEAT_METRIC_NAME_MAPPINGS.items():
            envelope = self._exporter._point_to_envelope(point, ot_name, resource)
            self.assertEqual(envelope.data.base_data.metrics[0].name, sb_name)
    
    def test_transmit_200_reach_ingestion(self):
        _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            result = self._exporter._transmit(self._envelopes_to_export)
        self.assertTrue(_STATSBEAT_STATE["INITIAL_SUCCESS"])
        self.assertEqual(result, ExportResult.SUCCESS)

    def test_transmit_206_reach_ingestion(self):
        _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=500,
                        message="should retry"
                    )
                ],
            )
            result = self._exporter._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        self.assertTrue(_STATSBEAT_STATE["INITIAL_SUCCESS"])

    def test_transmit_reach_ingestion_code(self):
        _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._reached_ingestion_code") as m, \
            mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as p:
            m.return_value = True
            p.return_value = True
            with mock.patch.object(AzureMonitorClient, 'track', throw(HttpResponseError)):
                result = self._exporter._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
        self.assertTrue(_STATSBEAT_STATE["INITIAL_SUCCESS"])

    def test_transmit_not_reach_ingestion_code(self):
        _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
        _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 1
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._reached_ingestion_code") as m, \
            mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as p:
            m.return_value = False
            p.return_value = False
            with mock.patch.object(AzureMonitorClient, 'track', throw(HttpResponseError)):
                result = self._exporter._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        self.assertFalse(_STATSBEAT_STATE["INITIAL_SUCCESS"])
        self.assertEqual(_STATSBEAT_STATE["INITIAL_FAILURE_COUNT"], 2)

    def test_transmit_not_reach_ingestion_exception(self):
        _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
        _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 1
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.shutdown_statsbeat_metrics") as m:
            with mock.patch.object(AzureMonitorClient, 'track', throw(Exception)):
                result = self._exporter._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        self.assertFalse(_STATSBEAT_STATE["INITIAL_SUCCESS"])
        self.assertEqual(_STATSBEAT_STATE["INITIAL_FAILURE_COUNT"], 2)
        m.assert_not_called()

    def test_transmit_not_reach_ingestion_exception_shutdown(self):
        _STATSBEAT_STATE["INITIAL_SUCCESS"] = False
        _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 2
        with mock.patch("azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.shutdown_statsbeat_metrics") as m:
            with mock.patch.object(AzureMonitorClient, 'track', throw(Exception)):
                result = self._exporter._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        self.assertFalse(_STATSBEAT_STATE["INITIAL_SUCCESS"])
        self.assertEqual(_STATSBEAT_STATE["INITIAL_FAILURE_COUNT"], 3)
        m.assert_called_once()
