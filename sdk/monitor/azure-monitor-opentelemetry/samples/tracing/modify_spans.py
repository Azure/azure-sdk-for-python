# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.sdk.trace import SpanProcessor

# Define a custom processor to modify your spans
class SpanEnrichingProcessor(SpanProcessor):

    def on_end(self, span):
        # Prefix the span name with the string "Updated-".
        span._name = "Updated-" + span.name
        # Add the custom dimension "CustomDimension1" with the value "Value1".
        span._attributes["CustomDimension1"] = "Value1"
         # Add the custom dimension "CustomDimension2" with the value "Value2".
        span._attributes["CustomDimension2"] = "Value2"

# Create a SpanEnrichingProcessor instance.
span_enrich_processor = SpanEnrichingProcessor()

# Pass in your processor to configuration options
configure_azure_monitor(
    span_processors=[span_enrich_processor]
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("this_span_will_be_modified"):
    print("Hello, World!")

input()
