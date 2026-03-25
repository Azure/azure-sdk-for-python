# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial release of `azure-ai-agentserver-hosting`.
- `AgentServer` host framework with health probe, graceful shutdown, and port binding.
- `TracingHelper` for OpenTelemetry tracing with Azure Monitor and OTLP exporters.
- Auto-enable tracing when Application Insights or OTLP endpoint is configured.
- W3C Trace Context propagation and `leaf_customer_span_id` baggage re-parenting.
- `error_response()` utility for standard error envelope responses.
- `get_logger()` for library-scoped logging.
- `StructuredLogFilter` and `LogScope` for per-request structured logging.
- `register_routes()` for pluggable protocol composition.
- Hypercorn-based ASGI server with HTTP/1.1 support.
