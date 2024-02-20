# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import requests
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import get_tracer, SpanContext, SpanKind, TraceFlags

# Define a custom processor to filter your spans
class SpanFilteringProcessor(SpanProcessor):

    # Prevents exporting spans that are of kind INTERNAL
    def on_start(self, span, parent_context):
        # Check if the span is an internal activity.
        if span._kind is SpanKind.INTERNAL:
            # Create a new span context with the following properties:
            #   * The trace ID is the same as the trace ID of the original span.
            #   * The span ID is the same as the span ID of the original span.
            #   * The is_remote property is set to `False`.
            #   * The trace flags are set to `DEFAULT`.
            #   * The trace state is the same as the trace state of the original span.
            span._context = SpanContext(
                span.context.trace_id,
                span.context.span_id,
                span.context.is_remote,
                TraceFlags(TraceFlags.DEFAULT),
                span.context.trace_state,
            )

# Create a SpanFilteringProcessor instance.
span_filter_processor = SpanFilteringProcessor()

# Pass in your processor to configuration options
configure_azure_monitor(
    span_processors=[span_filter_processor]
)

tracer = get_tracer(__name__)

with tracer.start_as_current_span("this_span_is_ignored"):
    # Requests made using the requests library will be automatically captured
    # The span generated from this request call will be tracked since it is not an INTERNAL span
    response = requests.get("https://azure.microsoft.com/", timeout=5)
    print("Hello, World!")

input()
