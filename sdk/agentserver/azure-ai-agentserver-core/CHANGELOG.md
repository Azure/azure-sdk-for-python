# Release History

## 2.0.0b1 (Unreleased)

### Features Added

- `AgentServerHost` base class (Starlette subclass) with health probe (`/readiness`), graceful shutdown, and port binding.
- `TracingHelper` for OpenTelemetry tracing with Azure Monitor and OTLP exporters.
- Auto-enable tracing when Application Insights or OTLP endpoint is configured.
- W3C Trace Context propagation and `leaf_customer_span_id` baggage re-parenting.
- `create_error_response()` utility for standard error envelope responses.
- `get_logger()` for library-scoped logging.
- Cooperative mixin inheritance for multi-protocol composition.
- Hypercorn-based ASGI server with HTTP/1.1 support.

### Breaking Changes

- Renamed `AgentHost` → `AgentServerHost`; now inherits from `Starlette` directly.
- Removed `register_routes()` — protocol packages now subclass `AgentServerHost` and extend `self.routes` in `__init__`.
- Removed lazy `app` property — `AgentServerHost` IS the ASGI app.
- Replaced `ErrorResponse.create()` static method with module-level `create_error_response()` function.
- Replaced `AgentLogger.get()` static method with module-level `get_logger()` function.
- Removed `AGENT_LOG_LEVEL` and `AGENT_GRACEFUL_SHUTDOWN_TIMEOUT` environment variable support from `Constants`.
- Renamed health endpoint from `/healthy` to `/readiness`.
