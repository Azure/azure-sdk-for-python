# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor

from azure.monitor.opentelemetry.exporter._quickpulse._live_metrics import record_span


class _QuickpulseSpanProcessor(SpanProcessor):

    def on_end(self, span: ReadableSpan) -> None:
        record_span(span)
        return super().on_end(span)
