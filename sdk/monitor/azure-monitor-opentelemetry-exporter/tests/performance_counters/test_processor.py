# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from unittest import mock
from unittest.mock import MagicMock

from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk.trace import ReadableSpan

from azure.monitor.opentelemetry.exporter._performance_counters._processor import (
    _PerformanceCountersLogRecordProcessor,
    _PerformanceCountersSpanProcessor,
)
from azure.monitor.opentelemetry.exporter._performance_counters._manager import (
    _PerformanceCountersManager,
)
from azure.monitor.opentelemetry.exporter._utils import Singleton


class TestPerformanceCountersLogRecordProcessor(unittest.TestCase):
    """Test performance counters log record processor."""

    def setUp(self):
        """Set up test environment."""
        # Reset singleton
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    def tearDown(self):
        """Clean up after tests."""
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._processor._PerformanceCountersManager")
    def test_on_emit_with_manager(self, mock_manager_class):
        """Test on_emit calls manager when available."""
        # Setup mock manager
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        processor = _PerformanceCountersLogRecordProcessor()
        
        # Create mock log data
        mock_log_data = MagicMock(spec=LogData)
        
        processor.on_emit(mock_log_data)
        
        # Verify manager was called
        mock_manager_class.assert_called_once()
        mock_manager._record_log_record.assert_called_once_with(mock_log_data)

    def test_emit_calls_on_emit(self):
        """Test emit method calls on_emit."""
        processor = _PerformanceCountersLogRecordProcessor()
        
        # Mock the on_emit method
        processor.on_emit = MagicMock()
        
        # Create mock log data
        mock_log_data = MagicMock(spec=LogData)
        
        processor.emit(mock_log_data)
        
        # Verify on_emit was called
        processor.on_emit.assert_called_once_with(mock_log_data)

    def test_shutdown(self):
        """Test shutdown method."""
        processor = _PerformanceCountersLogRecordProcessor()
        
        # Should not raise exception
        processor.shutdown()

    def test_force_flush(self):
        """Test force_flush method."""
        processor = _PerformanceCountersLogRecordProcessor()
        
        # Should not raise exception
        processor.force_flush()
        processor.force_flush(timeout_millis=5000)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._processor._PerformanceCountersManager")
    def test_exception_propagation_in_on_emit(self, mock_manager_class):
        """Test that exceptions from manager are propagated."""
        # Setup mock manager to raise exception
        mock_manager = MagicMock()
        mock_manager._record_log_record.side_effect = Exception("Test error")
        mock_manager_class.return_value = mock_manager
        
        processor = _PerformanceCountersLogRecordProcessor()
        
        # Create mock log data
        mock_log_data = MagicMock(spec=LogData)
        
        # Exception should be propagated
        with self.assertRaises(Exception) as context:
            processor.on_emit(mock_log_data)
        
        self.assertEqual(str(context.exception), "Test error")


class TestPerformanceCountersSpanProcessor(unittest.TestCase):
    """Test performance counters span processor."""

    def setUp(self):
        """Set up test environment."""
        # Reset singleton
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    def tearDown(self):
        """Clean up after tests."""
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._processor._PerformanceCountersManager")
    def test_on_end_with_manager(self, mock_manager_class):
        """Test on_end calls manager when available."""
        # Setup mock manager
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        processor = _PerformanceCountersSpanProcessor()
        
        # Create mock span
        mock_span = MagicMock(spec=ReadableSpan)
        
        processor.on_end(mock_span)
        
        # Verify manager was called
        mock_manager_class.assert_called_once()
        mock_manager._record_span.assert_called_once_with(mock_span)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._processor._PerformanceCountersManager")
    def test_exception_propagation_in_on_end(self, mock_manager_class):
        """Test that exceptions from manager are propagated."""
        # Setup mock manager to raise exception
        mock_manager = MagicMock()
        mock_manager._record_span.side_effect = Exception("Test error")
        mock_manager_class.return_value = mock_manager
        
        processor = _PerformanceCountersSpanProcessor()
        
        # Create mock span
        mock_span = MagicMock(spec=ReadableSpan)
        
        # Exception should be propagated
        with self.assertRaises(Exception) as context:
            processor.on_end(mock_span)
        
        self.assertEqual(str(context.exception), "Test error")

    def test_on_end_calls_super(self):
        """Test on_end calls super method."""
        processor = _PerformanceCountersSpanProcessor()
        
        # Mock the super class method
        with mock.patch.object(processor.__class__.__bases__[0], 'on_end') as mock_super_on_end:
            mock_span = MagicMock(spec=ReadableSpan)
            
            processor.on_end(mock_span)
            
            # Verify super was called
            mock_super_on_end.assert_called_once_with(mock_span)
