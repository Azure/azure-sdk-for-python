# Release History

## 1.0.0b2 (Unreleased)

### Features Added

- Container protocol version `2.0.0` support: reads `x-agent-user-id` and `x-agent-foundry-call-id` from inbound requests and binds them to the request-scoped platform context so the per-request call ID is forwarded on outbound Foundry 1P calls (`x-agent-user-id` is not forwarded to 1P). The values are available to handler and tool code via `azure.ai.agentserver.core.get_request_context()`.
- Added the `ActivityAgentServerHost.seed_connection_env(*, digital_worker=False)` static helper, which seeds the `CONNECTIONS__*` env vars the M365 connection manager reads from the Foundry-native `FOUNDRY_AGENT_*` env vars. The default construction path calls it for you; call it yourself only when you build the `MsalConnectionManager` (or a pre-built `AgentApplication`) manually, before constructing the connection manager.

### Breaking Changes

- Custom handlers and pre-built `AgentApplication` injection now use dedicated
  factory classmethods instead of `__init__` keyword arguments, so an invalid
  combination of construction options cannot be expressed:
  - `ActivityAgentServerHost(handler=fn)` → `ActivityAgentServerHost.from_request_handler(fn)`
  - `ActivityAgentServerHost(agent_app=app)` → `ActivityAgentServerHost.from_agent_application(app)`
  The default constructor now accepts only the build-the-M365-stack options
  (`digital_worker`, `storage`, `connection_manager`, `adapter`,
  `authorization`, `config`). `ActivityAgentServerHost()` (simple Teams
  agent) is unchanged.
- Removed the lazy M365 initialization and the ``@app.activity(...)`` / ``@app.error`` host decorators in their old form. When constructed directly (no `from_request_handler`), the M365 Agents SDK is now initialized eagerly during `ActivityAgentServerHost(...)` construction and the host acts as the underlying `AgentApplication` itself (via attribute delegation) — register handlers directly on the host with `@app.activity(...)` / `@app.error`, and reach the rest of the M365 surface (`message`/`proactive`/`auth` ...) the same way. The adapter is available via `app.adapter`.
- Removed the public `apply_msal_patches()` export. The MSAL/FMI patch is now applied internally (digital-worker model only) during construction.
- Replaced the `request.state.user_isolation_key` / `request.state.chat_isolation_key` request-state fields with the request-scoped platform context (`get_request_context()` exposes `user_id` / `call_id`) per container protocol version `2.0.0`. Requires `azure-ai-agentserver-core>=2.0.0b7`.

## 1.0.0b1 (2026-06-09)

### Features Added

- Initial preview release of `azure-ai-agentserver-activity`.
- `ActivityAgentServerHost` — Starlette-based host for Activity Protocol traffic.
- `POST /activity/messages` and `POST /api/messages` endpoints with Foundry platform header contract.
- Decorator API: `@app.activity(type)` and `@app.error` for zero-config handler registration.
- Custom handler support: `ActivityAgentServerHost(handler=fn)` for full M365 SDK control.
- Auto-initialization of M365 Agents SDK from environment variables (decorator mode).
- MSAL auth patches for Foundry container MAIB auth (`apply_msal_patches()`).
- Session ID resolution (query param → header → config → UUID fallback).
- Activity ID and session ID sanitization for header injection defense.
- OpenTelemetry distributed tracing and W3C Baggage propagation.
- Error-source classification (`x-platform-error-source`) on all error responses.
