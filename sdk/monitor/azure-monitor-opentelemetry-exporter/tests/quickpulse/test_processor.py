# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._quickpulse._processor import (
    _QuickpulseLogRecordProcessor,
    _QuickpulseSpanProcessor,
)
from azure.monitor.opentelemetry.exporter._quickpulse._manager import _QuickpulseManager


class TestQuickpulseLogRecordProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qpm = mock.Mock()
        _QuickpulseManager._instances[_QuickpulseManager] = cls.qpm

    @classmethod
    def tearDownClass(cls) -> None:
        # Reset singleton state - only clear QuickpulseManager instances
        if _QuickpulseManager in _QuickpulseManager._instances:
            del _QuickpulseManager._instances[_QuickpulseManager]

    @mock.patch(
        "azure.monitor.opentelemetry.exporter._quickpulse._processor.get_quickpulse_manager"
    )
    def test_emit(self, mock_get_manager):
        mock_manager = mock.Mock()
        mock_get_manager.return_value = mock_manager

        processor = _QuickpulseLogRecordProcessor()
        readable_log_record = mock.Mock()
        processor.on_emit(readable_log_record)

        mock_get_manager.assert_called_once()
        mock_manager._record_log_record.assert_called_once_with(readable_log_record)


class TestQuickpulseSpanProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qpm = mock.Mock()
        _QuickpulseManager._instances[_QuickpulseManager] = cls.qpm

    @classmethod
    def tearDownClass(cls) -> None:
        # Reset singleton state - only clear QuickpulseManager instances
        if _QuickpulseManager in _QuickpulseManager._instances:
            del _QuickpulseManager._instances[_QuickpulseManager]

    @mock.patch(
        "azure.monitor.opentelemetry.exporter._quickpulse._processor.get_quickpulse_manager"
    )
    def test_on_end(self, mock_get_manager):
        mock_manager = mock.Mock()
        mock_get_manager.return_value = mock_manager

        processor = _QuickpulseSpanProcessor()
        span = mock.Mock()
        processor.on_end(span)
        mock_manager._record_span.assert_called_once_with(span)
