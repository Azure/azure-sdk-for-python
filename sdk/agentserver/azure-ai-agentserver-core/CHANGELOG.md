# Release History

## 2.0.0b1 (Unreleased)

### Features Added

- `AgentHost` host framework with health probe, graceful shutdown, and port binding.
- `TracingHelper` for OpenTelemetry tracing with Azure Monitor and OTLP exporters.
- Auto-enable tracing when Application Insights or OTLP endpoint is configured.
- W3C Trace Context propagation and `leaf_customer_span_id` baggage re-parenting.
- `ErrorResponse.create()` utility for standard error envelope responses.
- `AgentLogger.get()` for library-scoped logging.
- `register_routes()` for pluggable protocol composition.
- Hypercorn-based ASGI server with HTTP/1.1 support.
