# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# cSpell:disable

import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._live_metrics import enable_live_metrics


class TestLiveMetrics(unittest.TestCase):

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics._QuickpulseManager")
    def test_enable_live_metrics(self, manager_mock):
        mock_resource = mock.Mock()
        enable_live_metrics(
            connection_string="test_cs",
            resource=mock_resource,
        )
        manager_mock.assert_called_with(connection_string="test_cs", resource=mock_resource)

# cSpell:enable
