# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from opentelemetry.trace import TraceFlags
from azure.monitor.opentelemetry._processor import _AzureMonitorLogRecordProcessor


class TestAzureMonitorLogRecordProcessor(unittest.TestCase):

    @patch('azure.monitor.opentelemetry._processor.BatchLogRecordProcessor.emit')
    def test_emit(self, emit_mock):
        exporter = Mock()
        log_data = Mock()
        log_record = Mock()
        log_record.span_id = 123
        log_record.trace_flags = TraceFlags(TraceFlags.SAMPLED)
        log_data.log_record = log_record
        proc = _AzureMonitorLogRecordProcessor(exporter)
        proc.emit(log_data)
        emit_mock.assert_called_once_with(log_data)

    @patch('azure.monitor.opentelemetry._processor.BatchLogRecordProcessor.emit')
    def test_emit_sampled_out(self, emit_mock):
        exporter = Mock()
        log_data = Mock()
        log_record = Mock()
        log_record.span_id = 123
        log_record.trace_flags = TraceFlags(TraceFlags.DEFAULT)
        log_data.log_record = log_record
        proc = _AzureMonitorLogRecordProcessor(exporter)
        proc.emit(log_data)
        emit_mock.assert_not_called()

    @patch('azure.monitor.opentelemetry._processor.BatchLogRecordProcessor.emit')
    def test_emit_disabled(self, emit_mock):
        exporter = Mock()
        log_data = Mock()
        log_record = Mock()
        log_record.span_id = 123
        log_record.trace_flags = TraceFlags(TraceFlags.DEFAULT)
        log_data.log_record = log_record
        proc = _AzureMonitorLogRecordProcessor(exporter, disable_trace_based_sampling=True)
        proc.emit(log_data)
        emit_mock.assert_called_once_with(log_data)
