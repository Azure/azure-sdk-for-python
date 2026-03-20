# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

# Using always_on sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "always_on"
# The sampling rate is 1.0, so 100% of the traces are sampled.

# Using always_off sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "always_off"
# The sampling rate is 0.0, so None of the traces are sampled.

# Using trace_id_ratio sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "trace_id_ratio"
# Set the OTEL_TRACES_SAMPLER_ARG environment variable to 0.1; it must be a number between 0 and 1
# or it defaults to 1.0.
# A sampling rate of 0.1 means approximately 10% of your traces are sent.

# Using parentbased_always_on sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "parentbased_always_on"
# The sampling rate is 1.0, so 100% of the traces are sampled.

# Using parentbased_always_off sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "parentbased_always_off"
# The sampling rate is 0.0, so None of the traces are sampled.

# Using parentbased_trace_id_ratio sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "parentbased_trace_id_ratio"
# Set the OTEL_TRACES_SAMPLER_ARG environment variable to 0.45; it must be a number between 0 and 1
# or it defaults to 1.0.
# A sampling rate of 0.45 means approximately 45% of your traces are sent.

# Using rate limited sampler (this is the default sampler)
# Set the OTEL_TRACES_SAMPLER environment variable to "microsoft.rate_limited"
# Set the OTEL_TRACES_SAMPLER_ARG environment variable to the desired rate limit (e.g., 0.5 means
# one trace every two seconds, while 5.0 means five traces per second)
# You can also configure the rate limited sampler by passing the `traces_per_second` argument to
# `configure_azure_monitor`.

# Example: configure rate-limited sampler directly via code
# configure_azure_monitor(
#     traces_per_second=0.5,
# )

# Using fixed percentage sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "microsoft.fixed_percentage"
# Set the OTEL_TRACES_SAMPLER_ARG environment variable to 0.2; it must be a number between 0 and 1 or
# it defaults to 1.0.
# When configuring sampling via `configure_azure_monitor`, the default sampler is rate limited. To use the classic Application Insights # pylint: disable=line-too-long
# sampler instead, set `sampling_ratio` to 1.0. # pylint: disable=line-too-long

# Example: configure fixed-percentage sampler via code
# configure_azure_monitor(
#     sampling_ratio=1.0,
#     traces_per_second=0.0,
# )

# Using trace_based_sampling configuration # cspell: ignore unsampled
# Determines whether the logger should drop log records associated with unsampled traces.
# Passing the enable_trace_based_sampling_for_logs=True argument to configure_azure_monitor ensures that log records associated with
# unsampled traces are dropped by the logger.
# A log record is considered associated with an unsampled trace if it has a valid `SpanId` and its `TraceFlags` indicate that the trace is unsampled.
# The value of this config is False by default.

# Example: enable trace-based sampling for logs
# configure_azure_monitor(
#     enable_trace_based_sampling_for_logs=True,
# )

configure_azure_monitor()

tracer = trace.get_tracer(__name__)

for i in range(100):
    with tracer.start_as_current_span("hello"):
        print("Hello, World!")

input()
