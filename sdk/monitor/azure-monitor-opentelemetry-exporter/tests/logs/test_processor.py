import os
import unittest
from unittest import mock

from opentelemetry.sdk import _logs
from opentelemetry._logs import LogRecord
from opentelemetry.context import Context
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, InMemoryLogRecordExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry._logs.severity import SeverityNumber
from opentelemetry.trace import TraceFlags, set_span_in_context, SpanContext, NonRecordingSpan

from azure.monitor.opentelemetry.exporter import ApplicationInsightsSampler
from azure.monitor.opentelemetry.exporter._constants import _SAMPLE_RATE_KEY
from azure.monitor.opentelemetry.exporter.export.logs._exporter import (
    AzureMonitorLogExporter,
)
from azure.monitor.opentelemetry.exporter.export.logs._processor import (
    _AzureBatchLogRecordProcessor,
)


# pylint: disable=protected-access, line-too-long
class TestAzureBatchLogRecordProcessor(unittest.TestCase):
    """Test cases for the Azure Monitor Batch Log Record Processor with trace-based sampling."""

    @classmethod
    def setUpClass(cls):
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
        cls._exporter = AzureMonitorLogExporter()

    def test_processor_initialization_without_trace_based_sampling(self):
        """Test processor initialization without trace-based sampling enabled."""
        processor = _AzureBatchLogRecordProcessor(self._exporter, options={})
        self.assertFalse(processor._enable_trace_based_sampling_for_logs)

    def test_processor_initialization_with_trace_based_sampling(self):
        """Test processor initialization with trace-based sampling enabled."""
        processor = _AzureBatchLogRecordProcessor(
            self._exporter, options={"enable_trace_based_sampling_for_logs": True}
        )
        self.assertTrue(processor._enable_trace_based_sampling_for_logs)

    def test_processor_initialization_without_options(self):
        """Test processor initialization without options."""
        processor = _AzureBatchLogRecordProcessor(self._exporter)
        self.assertIsNone(processor._enable_trace_based_sampling_for_logs)

    def test_on_emit_with_trace_based_sampling_disabled(self):
        """Test on_emit does not filter logs when trace-based sampling is disabled."""
        processor = _AzureBatchLogRecordProcessor(self._exporter, options={})

        mock_span_context = mock.Mock()
        mock_span_context.is_valid = True
        mock_span_context.trace_flags.sampled = False

        mock_span = mock.Mock()
        mock_span.get_span_context.return_value = mock_span_context

        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=2909973987304607650,
            trace_flags=TraceFlags.DEFAULT,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)

        log_record = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Test log",
            ),
            InstrumentationScope("test_name"),
        )

        # Mock the parent class's on_emit method through super
        with mock.patch("opentelemetry.sdk._logs.export.BatchLogRecordProcessor.on_emit") as parent_on_emit_mock:
            processor.on_emit(log_record)
            # Parent on_emit should be called because trace-based sampling is disabled
            parent_on_emit_mock.assert_called_once()

    def test_on_emit_with_trace_based_sampling_enabled_and_unsampled_trace(self):  # cspell:disable-line
        """Test on_emit filters logs when trace-based sampling is enabled and trace is unsampled."""  # cspell:disable-line
        processor = _AzureBatchLogRecordProcessor(
            self._exporter, options={"enable_trace_based_sampling_for_logs": True}
        )

        mock_span_context = mock.Mock()
        mock_span_context.is_valid = True
        mock_span_context.trace_flags.sampled = False

        mock_span = mock.Mock()
        mock_span.get_span_context.return_value = mock_span_context

        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=2909973987304607650,
            trace_flags=TraceFlags.DEFAULT,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)

        log_record = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Test log",
            ),
            InstrumentationScope("test_name"),
        )
        # Mock get_current_span to return our mock span with proper get_span_context method
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.export.logs._processor.get_current_span", return_value=mock_span
        ):
            # Mock only the parent class's on_emit method
            with mock.patch("opentelemetry.sdk._logs.export.BatchLogRecordProcessor.on_emit") as parent_on_emit_mock:
                processor.on_emit(log_record)
                # Parent on_emit should NOT be called because trace is unsampled and filtering is enabled # cspell:disable-line
                parent_on_emit_mock.assert_not_called()

    def test_on_emit_with_trace_based_sampling_enabled_and_sampled_trace(self):
        """Test on_emit does not filter logs when trace-based sampling is enabled and trace is sampled."""
        processor = _AzureBatchLogRecordProcessor(
            self._exporter, options={"enable_trace_based_sampling_for_logs": True}
        )

        mock_span_context = mock.Mock()
        mock_span_context.is_valid = True
        mock_span_context.trace_flags.sampled = True

        mock_span = mock.Mock()
        mock_span.get_span_context.return_value = mock_span_context

        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=2909973987304607650,
            trace_flags=TraceFlags.SAMPLED,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)

        log_record = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Test log",
            ),
            InstrumentationScope("test_name"),
        )

        with mock.patch(
            "azure.monitor.opentelemetry.exporter.export.logs._processor.get_current_span", return_value=mock_span
        ):
            with mock.patch("opentelemetry.sdk._logs.export.BatchLogRecordProcessor.on_emit") as parent_on_emit_mock:
                processor.on_emit(log_record)
                # Parent on_emit should be called because trace is sampled
                parent_on_emit_mock.assert_called_once()

    def test_on_emit_with_trace_based_sampling_enabled_and_invalid_span_context(self):
        """Test on_emit does not filter logs with invalid span context."""
        processor = _AzureBatchLogRecordProcessor(
            self._exporter, options={"enable_trace_based_sampling_for_logs": True}
        )

        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=0,
            trace_flags=TraceFlags.DEFAULT,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)

        log_record = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Test log",
            ),
            InstrumentationScope("test_name"),
        )

        with mock.patch("opentelemetry.sdk._logs.export.BatchLogRecordProcessor.on_emit") as parent_on_emit_mock:
            processor.on_emit(log_record)
            parent_on_emit_mock.assert_called_once()

    def test_filtering_uses_context_span_not_record_flags(self):
        exporter = InMemoryLogRecordExporter()
        processor = _AzureBatchLogRecordProcessor(exporter, options={"enable_trace_based_sampling_for_logs": True})
        self.addCleanup(processor.shutdown)

        processor.on_emit(_logs.ReadWriteLogRecord(LogRecord(trace_id=1, span_id=2, body="kept")))
        unsampled = NonRecordingSpan(SpanContext(1, 2, is_remote=True, trace_flags=TraceFlags(0)))
        record = LogRecord(
            context=set_span_in_context(unsampled), trace_flags=TraceFlags(TraceFlags.SAMPLED), body="dropped"
        )
        processor.on_emit(_logs.ReadWriteLogRecord(record))

        self.assertTrue(processor.force_flush())
        (kept,) = exporter.get_finished_logs()
        self.assertEqual(kept.log_record.body, "kept")
        self.assertIsNone(self._exporter._log_to_envelope(kept).sample_rate)

    def test_batch_preserves_sample_rate_and_user_attribute(self):
        exporter = InMemoryLogRecordExporter()
        processor = _AzureBatchLogRecordProcessor(exporter, options={"enable_trace_based_sampling_for_logs": True})
        self.addCleanup(processor.shutdown)
        provider = TracerProvider(sampler=ApplicationInsightsSampler(0.05))
        self.addCleanup(provider.shutdown)
        tracer = provider.get_tracer(__name__)
        # Trace ID 1 is in the first 5% of the Application Insights sampler's hash range.
        with (
            mock.patch.object(provider.id_generator, "generate_trace_id", return_value=1),
            tracer.start_as_current_span("sampled") as span,
        ):
            record = _logs.ReadWriteLogRecord(
                LogRecord(body="full record", attributes={"customer": "preserved"}),
                limits=_logs.LogRecordLimits(max_log_record_attributes=1),
            )
            processor.on_emit(record)
            # The batch must reflect the rate at emission, not a later change to the span.
            span.set_attribute(_SAMPLE_RATE_KEY, 50)

        self.assertTrue(processor.force_flush())
        (log,) = exporter.get_finished_logs()
        envelope = self._exporter._log_to_envelope(log).as_dict()
        self.assertEqual(envelope["sampleRate"], 5)
        self.assertEqual(envelope["data"]["baseData"]["properties"], {"customer": "preserved"})

    def test_only_a_matching_span_with_a_valid_rate_weights_logs(self):
        provider = TracerProvider()
        self.addCleanup(provider.shutdown)
        span = provider.get_tracer(__name__).start_span("sampled")
        self.addCleanup(span.end)
        context = set_span_in_context(span)
        propagated = set_span_in_context(NonRecordingSpan(span.get_span_context()))

        exporter = InMemoryLogRecordExporter()
        processor = _AzureBatchLogRecordProcessor(exporter, options={"enable_trace_based_sampling_for_logs": True})
        self.addCleanup(processor.shutdown)
        span.set_attribute(_SAMPLE_RATE_KEY, 50)
        mismatched = LogRecord(context=context)
        mismatched.span_id = 1 if mismatched.span_id != 1 else 2
        processor.on_emit(_logs.ReadWriteLogRecord(mismatched))
        for ctx in (propagated, Context()):
            processor.on_emit(_logs.ReadWriteLogRecord(LogRecord(context=ctx)))
        for rate in (0, 100, 101, True, "invalid", "0.5"):
            span.set_attribute(_SAMPLE_RATE_KEY, rate)
            processor.on_emit(_logs.ReadWriteLogRecord(LogRecord(context=context)))
        self.assertTrue(processor.force_flush())
        rates = [self._exporter._log_to_envelope(log).sample_rate for log in exporter.get_finished_logs()]
        self.assertEqual(rates, [None] * 8 + [0.5])

    def test_unfiltered_exporter_on_same_provider_does_not_inherit_rate(self):
        tracer_provider = TracerProvider(sampler=ApplicationInsightsSampler(0.05))
        self.addCleanup(tracer_provider.shutdown)
        tracer = tracer_provider.get_tracer(__name__)
        for filtered_first in (True, False):
            with self.subTest(filtered_first=filtered_first):
                provider = _logs.LoggerProvider()
                self.addCleanup(provider.shutdown)
                filtered, unfiltered = InMemoryLogRecordExporter(), InMemoryLogRecordExporter()
                processors = (
                    _AzureBatchLogRecordProcessor(filtered, options={"enable_trace_based_sampling_for_logs": True}),
                    BatchLogRecordProcessor(unfiltered),
                )
                for processor in processors if filtered_first else reversed(processors):
                    provider.add_log_record_processor(processor)
                logger = provider.get_logger(__name__)
                with (
                    mock.patch.object(tracer_provider.id_generator, "generate_trace_id", return_value=1),
                    tracer.start_as_current_span("sampled"),
                ):
                    logger.emit(body="kept")
                dropped = NonRecordingSpan(SpanContext(1, 2, is_remote=True, trace_flags=TraceFlags(0)))
                logger.emit(body="not sampled", context=set_span_in_context(dropped))
                self.assertTrue(provider.force_flush())
                for exporter, expected in ((filtered, [5]), (unfiltered, [None, None])):
                    rates = [self._exporter._log_to_envelope(log).sample_rate for log in exporter.get_finished_logs()]
                    self.assertEqual(rates, expected)

    def test_on_emit_with_trace_based_sampling_enabled_and_no_context(self):
        """Test on_emit does not filter logs when there is no log record context."""
        processor = _AzureBatchLogRecordProcessor(
            self._exporter, options={"enable_trace_based_sampling_for_logs": True}
        )

        log_record = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419456,
                context=None,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Test log",
            ),
            InstrumentationScope("test_name"),
        )

        with mock.patch("opentelemetry.sdk._logs.export.BatchLogRecordProcessor.on_emit") as parent_on_emit_mock:
            processor.on_emit(log_record)
            # Parent on_emit should be called because there's no context
            parent_on_emit_mock.assert_called_once()

    def test_on_emit_integration_with_multiple_log_records(self):
        """Integration test: verify processor handles multiple log records correctly with trace-based sampling."""
        processor = _AzureBatchLogRecordProcessor(
            self._exporter, options={"enable_trace_based_sampling_for_logs": True}
        )

        # Create unsampled span context # cspell:disable-line
        mock_span_context_unsampled = mock.Mock()  # cspell:disable-line
        mock_span_context_unsampled.is_valid = True  # cspell:disable-line
        mock_span_context_unsampled.trace_flags.sampled = False  # cspell:disable-line

        mock_span_unsampled = mock.Mock()  # cspell:disable-line
        mock_span_unsampled.get_span_context.return_value = mock_span_context_unsampled  # cspell:disable-line

        # Create sampled span context
        mock_span_context_sampled = mock.Mock()
        mock_span_context_sampled.is_valid = True
        mock_span_context_sampled.trace_flags.sampled = True

        mock_span_sampled = mock.Mock()
        mock_span_sampled.get_span_context.return_value = mock_span_context_sampled

        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=2909973987304607650,
            trace_flags=TraceFlags.DEFAULT,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)

        log_record_unsampled = _logs.ReadWriteLogRecord(  # cspell:disable-line
            LogRecord(
                timestamp=1646865018558419456,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Unsampled log",  # cspell:disable-line
            ),
            InstrumentationScope("test_name"),
        )

        span_context = SpanContext(
            trace_id=125960616039069540489478540494783893221,
            span_id=2909973987304607650,
            trace_flags=TraceFlags.SAMPLED,
            is_remote=False,
        )
        span = NonRecordingSpan(span_context)
        ctx = set_span_in_context(span)

        log_record_sampled = _logs.ReadWriteLogRecord(
            LogRecord(
                timestamp=1646865018558419457,
                context=ctx,
                severity_text="INFO",
                severity_number=SeverityNumber.INFO,
                body="Sampled log",
            ),
            InstrumentationScope("test_name"),
        )

        with mock.patch(
            "azure.monitor.opentelemetry.exporter.export.logs._processor.get_current_span"
        ) as get_span_mock:
            with mock.patch("opentelemetry.sdk._logs.export.BatchLogRecordProcessor.on_emit") as parent_on_emit_mock:
                # Test unsampled log is filtered # cspell:disable-line
                get_span_mock.return_value = mock_span_unsampled  # cspell:disable-line
                processor.on_emit(log_record_unsampled)  # cspell:disable-line
                parent_on_emit_mock.assert_not_called()

                # Reset mock
                parent_on_emit_mock.reset_mock()
                get_span_mock.reset_mock()

                # Test sampled log is not filtered
                get_span_mock.return_value = mock_span_sampled
                processor.on_emit(log_record_sampled)
                parent_on_emit_mock.assert_called_once()
