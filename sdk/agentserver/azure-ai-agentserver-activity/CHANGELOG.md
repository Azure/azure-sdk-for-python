# Release History

## 1.0.0b2 (Unreleased)

### Features Added

- Container protocol version `2.0.0` support: reads `x-agent-user-id` and `x-agent-foundry-call-id` from inbound requests and binds them to the request-scoped platform context so the per-request call ID is forwarded on outbound Foundry 1P calls (`x-agent-user-id` is not forwarded to 1P). The values are also exposed on `request.state.user_id` and `request.state.call_id`.

### Breaking Changes

- Replaced `request.state.user_isolation_key` / `request.state.chat_isolation_key` with `request.state.user_id` / `request.state.call_id` per container protocol version `2.0.0`. Requires `azure-ai-agentserver-core>=2.0.0b7`.

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
