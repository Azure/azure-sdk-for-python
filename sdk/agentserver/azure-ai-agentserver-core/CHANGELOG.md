# Release History

## 2.0.0b1 (Unreleased)

### Features Added

- `AgentHost` host framework with health probe (`/readiness`), graceful shutdown, and port binding.
- `TracingHelper` for OpenTelemetry tracing with Azure Monitor and OTLP exporters.
- Auto-enable tracing when Application Insights or OTLP endpoint is configured.
- W3C Trace Context propagation and `leaf_customer_span_id` baggage re-parenting.
- `create_error_response()` utility for standard error envelope responses.
- `get_logger()` for library-scoped logging.
- `register_routes()` for pluggable protocol composition.
- Hypercorn-based ASGI server with HTTP/1.1 support.

### Breaking Changes

- Replaced `ErrorResponse.create()` static method with module-level `create_error_response()` function.
- Replaced `AgentLogger.get()` static method with module-level `get_logger()` function.
- Removed `AGENT_LOG_LEVEL` and `AGENT_GRACEFUL_SHUTDOWN_TIMEOUT` environment variable support from `Constants`.
- Renamed health endpoint from `/healthy` to `/readiness`.
