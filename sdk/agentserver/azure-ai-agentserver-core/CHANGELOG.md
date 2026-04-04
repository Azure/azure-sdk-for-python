# Release History

## 2.0.0b1 (Unreleased)

### Features Added

- `AgentServerHost` base class (Starlette subclass) with health probe (`/readiness`), graceful shutdown, and port binding.
- Automatic OpenTelemetry tracing with Azure Monitor and OTLP exporters (included as primary dependencies).
- `request_span()` host method and `end_span()` / `record_error()` / `trace_stream()` public functions for protocol SDK tracing.
- Overridable tracing setup via `configure_tracing` constructor parameter.
- `create_error_response()` utility for standard error envelope responses.
- Cooperative mixin inheritance for multi-protocol composition.
- Hypercorn-based ASGI server with HTTP/1.1 support.

### Breaking Changes

- Renamed `AgentHost` → `AgentServerHost`; now inherits from `Starlette` directly.
- Removed `register_routes()` — protocol packages now subclass `AgentServerHost` and pass routes via `super().__init__()`.
- Removed lazy `app` property — `AgentServerHost` IS the ASGI app.
- Replaced `TracingHelper` class with module-level functions (`request_span`, `end_span`, `record_error`, `trace_stream`, `configure_tracing`).
- Replaced `ErrorResponse.create()` static method with module-level `create_error_response()` function.
- Removed `AgentLogger` / `get_logger()` — use `logging.getLogger("azure.ai.agentserver")` directly.
- Removed `AGENT_LOG_LEVEL` and `AGENT_GRACEFUL_SHUTDOWN_TIMEOUT` environment variable support from `Constants`.
- Removed `leaf_customer_span_id` baggage mechanism and W3C Baggage propagation.
- OpenTelemetry is now a required dependency (was optional `[tracing]` extras).
- Renamed health endpoint from `/healthy` to `/readiness`.

## 1.0.0b1 (2025-11-07)

### Features Added

First version
