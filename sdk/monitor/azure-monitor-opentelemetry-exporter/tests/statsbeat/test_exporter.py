# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from gc import collect
import os
import unittest
from unittest import mock

from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics.export import NumberDataPoint

from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter._constants import _STATSBEAT_METRIC_NAME_MAPPINGS

# pylint: disable=protected-access
class TestStatsbeatExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.clear()
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = "1234abcd-5678-4efa-8abc-1234567890ab"

    @mock.patch(
        'azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.collect_statsbeat_metrics')
    def test_init(self, collect_mock):
        exporter = _StatsBeatExporter()
        self.assertFalse(exporter._should_collect_stats())
        collect_mock.assert_not_called()

    def test_point_to_envelope(self):
        exporter = _StatsBeatExporter()
        resource = Resource.create(attributes={"asd":"test_resource"})
        scope = InstrumentationScope("test_scope")
        point=NumberDataPoint(
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=10,
            attributes={},
        )
        for ot_name, sb_name in _STATSBEAT_METRIC_NAME_MAPPINGS.items():
            envelope = exporter._point_to_envelope(point, ot_name, resource, scope)
            self.assertEqual(envelope.data.base_data.metrics[0].name, sb_name)
