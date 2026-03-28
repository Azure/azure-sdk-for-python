# Release History

## 2.0.0b1 (Unreleased)

### Features Added

- `AgentHost` host framework with health probe, graceful shutdown, and port binding.
- `TracingHelper` for OpenTelemetry tracing with Azure Monitor and OTLP exporters.
- Auto-enable tracing when Application Insights or OTLP endpoint is configured.
- W3C Trace Context propagation and `leaf_customer_span_id` baggage re-parenting.
- `ErrorResponse.create()` utility for standard error envelope responses.
<<<<<<< HEAD
- `Agent` for library-scoped logging.
- `StructuredLogFilter` and `LogScope` for per-request structured logging.
=======
- `AgentLogger.get()` for library-scoped logging.
>>>>>>> 7445ddd3de7ce8364cc8c1fb703685e02a6cbd1a
- `register_routes()` for pluggable protocol composition.
- Hypercorn-based ASGI server with HTTP/1.1 support.
