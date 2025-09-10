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

    def test_emit(self):
        processor = _QuickpulseLogRecordProcessor()
        log_data = mock.Mock()
        processor.on_emit(log_data)
        self.qpm._record_log_record.assert_called_once_with(log_data)


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

    def test_on_end(self):
        processor = _QuickpulseSpanProcessor()
        span = mock.Mock()
        processor.on_end(span)
        self.qpm._record_span.assert_called_once_with(span)
