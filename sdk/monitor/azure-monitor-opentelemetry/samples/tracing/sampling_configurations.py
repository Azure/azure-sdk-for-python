from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Using always_on sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "always_on"
# The sampling rate is 1.0, so 100% of the traces are sampled.

# Using always_off sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "always_off"
# The sampling rate is 0.0, so None of the traces are sampled.

# Using trace_id_ratio sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "trace_id_ratio"
# Set the OTEL_TRACES_SAMPLER_ARG environment variable to 0.1, it has to be a number between 0 and 1, else it will throw an error and default to 1.0
# The sampling rate is 0.1 means approximately 10% of your traces are sent

# Using parentbased_always_on sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "parentbased_always_on"
# The sampling rate is 1.0, so 100% of the traces are sampled.

# Using parentbased_always_off sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "parentbased_always_off"
# The sampling rate is 0.0, so None of the traces are sampled.

# Using parentbased_trace_id_ratio sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "parentbased_trace_id_ratio"
# Set the OTEL_TRACES_SAMPLER_ARG environment variable to 0.45, it has to be a number between 0 and 1, else it will throw an error and default to 1.0
# The sampling rate is 0.45 means approximately 45% of your traces are sent

# Using rate limited sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "microsoft.rate_limited"
# Set the OTEL_TRACES_SAMPLER_ARG environment variable to the desired rate limit (e.g., 0.5 means one trace every two seconds, while 5.0 means five traces per second)

# Using fixed percentage sampler
# Set the OTEL_TRACES_SAMPLER environment variable to "microsoft.fixed_percentage"
# Set the OTEL_TRACES_SAMPLER_ARG environment variable to 0.2, it has to be a number between 0 and 1, else it will throw an error and default to 1.0

# Using trace_based_sampling configuration # cspell: ignore unsampled
# Determines whether the logger should drop log records associated with unsampled traces.
# Passing the enable_trace_based_sampling_for_logs=True argument to configure_azure_monitor ensure that log records associated with unsampled traces are dropped by the `Logger`.
# A log record is considered associated with an unsampled trace if it has a valid `SpanId` and its `TraceFlags` indicate that the trace is unsampled.
# The value of this config is False by default

"""
    configure_azure_monitor (
        "enable_trace_based_sampling_for_logs": True,
    ) 
"""

configure_azure_monitor()

tracer = trace.get_tracer(__name__)

for i in range(100):
    with tracer.start_as_current_span("hello"):
        print("Hello, World!")

input()
