# Release History

## 1.0.0b4 (2026-05-21)

### Samples

- **Durable-task sample suite rewritten** (per spec 015). The 4 shipped durable samples now conform to the refined `@task` primitive contract and demonstrate the full crash-recovery surface:
  - `samples/durable_copilot` — rewritten end-to-end to close 5 streaming/recovery gaps (`streaming=True` on session create/resume; `AssistantMessageDeltaData` → live `text_delta` chunks; `SessionIdleData` → `session_idle` chunk that unblocks the idle event; upstream-history dedup so a resumed turn does not re-send the user message; recovery replay of the last assistant text on `entry_mode == "recovered"`).
  - `samples/durable_multiturn` — rewritten to demonstrate the new callable namespace facility (`ctx.metadata("session")` for session-level state vs. the default per-invocation namespace). External `FileStore`-based checkpointing dropped; the primitive now owns persistence.
  - `samples/durable_langgraph` — verified compliant with the spec-015 design (one `@task` body + LangGraph `SqliteSaver` + `thread_id`, no `DurabilityContext`).
  - `samples/durable_research` — **new** peer-sample distilled from the foundry-hosted `durable-agent-demo/src/durable-research-agent` reference. 12-stage research loop with checkpoint-and-resume via `ctx.metadata()`, SSE streaming, async-poll fallback. ~280-line `agent.py` + ~115-line `app.py` — fits the standard sample shape.
  - `samples/durable_claude` — **removed**. Consumer-only design no longer fit the invocations surface; the consolidated developer guide in `azure-ai-agentserver-core/docs/durable-task-guide.md` now carries the conceptual material.
  - Reference-only `samples/durable-agent-demo/` is untouched — it remains the foundry-hosted-agent reference deployment.
- **New per-sample documentation**:
  - Each of the 4 shipped durable samples now has a `README.md` covering setup, run, observability, and crash-recovery checklist.
  - `samples/SHIPPABLE.md` — source-of-truth manifest enumerating shipped samples, reference-only exemptions, and removed-sample notes.
  - `samples/DURABLE_SAMPLES.md` — cross-sample operational guide with a selector matrix, concept primer (entry mode, metadata namespaces, recovery replay, steering), and production checklist.
- **CI gate**: `tests/test_samples_shippable_bar.py` enforces the per-sample README sections, manifest presence, and `requirements.txt` install-independence on every PR.

### Features Added

- **Durable invocation samples** — Added `durable_langgraph` and `durable_multiturn` sample applications demonstrating crash-resilient long-running agents using `@task` with the invocations protocol.
- Error source classification headers: All HTTP error responses now include `x-platform-error-source` with a value of `user`, `platform`, or `upstream` to indicate which component caused the error. Developer handler exceptions and missing handler registrations are classified as `upstream`. Exceptions tagged with the platform error tag are classified as `platform` and additionally include `x-platform-error-detail` with truncated exception details (max 2048 characters) for diagnostics.
- WebSocket protocol support — `InvocationAgentServerHost` now hosts `/invocations_ws` alongside `POST /invocations`. Register the handler with the new `@app.ws_handler` decorator. The route is registered lazily on first decoration, so hosts without a registered handler return HTTP 404.
- WebSocket Ping/Pong keep-alive — disabled by default; enable by setting the `WS_KEEPALIVE_INTERVAL` env var (auto-injected by AgentService into hosted-agent containers; surfaced on `app.config.ws_ping_interval` in `azure-ai-agentserver-core>=2.0.0b4`). `0` (or unset) disables keep-alive. Wired through to Hypercorn's `websocket_ping_interval` by `AgentServerHost._build_hypercorn_config`.
- WebSocket telemetry — structured close-event log line carrying `azure.ai.agentserver.invocations_ws.session_id`, `close_code`, and `duration_ms` (via the standard `logging` `extra` dict). Session ID honours the `FOUNDRY_AGENT_SESSION_ID` env var for HTTP/WS correlation.
- New samples: `samples/ws_invoke_agent/` (echo) and `samples/ws_bidirectional_streaming_agent/` (concurrent token streaming with cancel/bye control messages).

### Breaking Changes

- Removed the automatic `invoke_agent` server span that was created on each `/invocations` request. Trace context propagation is now handled by the core `TraceContextMiddleware`, and user-created spans inside handlers are correctly parented without framework-generated spans.
- Removed `_safe_set_attrs` and `_wrap_streaming_response` internal helpers (no longer needed without framework-level span management).

### Other Changes

- Bumped minimum `azure-ai-agentserver-core` dependency to `>=2.0.0b4`.
- Platform header name constants (e.g. `x-platform-error-source`, `x-platform-error-detail`) are now imported from `azure-ai-agentserver-core` (`_platform_headers` module) instead of being defined locally. Error source classification helpers remain internal to this package.
- Simplified request handling: baggage entries (`invocation_id`, `session_id`) are still set on each request, but span creation and lifecycle management are left to downstream frameworks.

## 1.0.0b3 (2026-04-22)

### Features Added

- All HTTP responses now include an `x-request-id` header for request correlation, inherited from `RequestIdMiddleware` in `azure-ai-agentserver-core>=2.0.0b3`. The value is resolved from the OpenTelemetry trace ID, an incoming `x-request-id` header, or a generated UUID.

### Other Changes

- Bumped minimum `azure-ai-agentserver-core` dependency to `>=2.0.0b3`.

## 1.0.0b2 (2026-04-17)

### Features Added

- Startup configuration logging — `InvocationAgentServerHost` logs whether an OpenAPI spec is configured at INFO level during construction.
- Inbound request logging — `InboundRequestLoggingMiddleware` from `azure-ai-agentserver-core` is now wired automatically by `AgentServerHost`. All inbound HTTP requests are logged at INFO level (start) and at INFO or WARNING level (completion) with method, path, status code, duration, and correlation headers.

## 1.0.0b1 (2026-04-14)

### Features Added

- Initial release of `azure-ai-agentserver-invocations`.
- `InvocationAgentServerHost` — a Starlette-based host subclass for the invocations protocol.
- Decorator-based handler registration (`@app.invoke_handler`, `@app.get_invocation_handler`, `@app.cancel_invocation_handler`).
- Optional `GET /invocations/{id}` and `POST /invocations/{id}/cancel` endpoints.
- `GET /invocations/docs/openapi.json` for OpenAPI spec serving.
- Invocation ID tracking and session correlation via `agent_session_id` query parameter.
- Distributed tracing with GenAI semantic convention span attributes.
- W3C Baggage propagation of `invocation_id` and `session_id` for cross-service correlation.
- Structured logging with `invocation_id` and `session_id` via `contextvars`.
- Streaming response support with span lifecycle management.
- Cooperative mixin inheritance for multi-protocol composition.
