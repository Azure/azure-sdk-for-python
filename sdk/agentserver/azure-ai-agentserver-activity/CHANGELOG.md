# Release History

## 1.0.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0b1 (2026-07-22)

### Features Added

- Initial preview release of `azure-ai-agentserver-activity`.
- `ActivityAgentServerHost` — Starlette-based host for Activity Protocol traffic.
- `POST /activity/messages` and `POST /api/messages` endpoints with the Foundry platform header contract.
- Simple Teams agent path: `ActivityAgentServerHost()` builds the M365 Agents SDK stack eagerly during construction and exposes the built `AgentApplication` as the `host.agent_app` property. Register handlers with `@host.agent_app.activity(...)` / `@host.agent_app.error`, and reach the rest of the M365 surface (`message` / `proactive` / `auth`) the same way. The adapter is available via `host.adapter`.
- Custom handler support: `ActivityAgentServerHost(request_handler=fn)` for full request/response control without the M365 SDK.
- Pre-built injection: `ActivityAgentServerHost(agent_app=app)`, plus build options on the default constructor (`digital_worker`, `storage`, `connection_manager`, `adapter`, `authorization`, `connection_config`).
- Container protocol version `2.0.0` support: reads `x-agent-user-id` and `x-agent-foundry-call-id` from inbound requests and binds them to the request-scoped platform context so the per-request call ID is forwarded on outbound Foundry 1P calls (`x-agent-user-id` is not forwarded to 1P). Values are available to handler and tool code via `azure.ai.agentserver.core.get_request_context()`.
- Module-level `get_hosted_agent_env(*, digital_worker=False)` helper that returns a config mapping (`os.environ` overlaid with the derived `CONNECTIONS__*` settings from the Foundry-native `FOUNDRY_AGENT_*` env vars) **without mutating the process environment**.
- MSAL auth patches for Foundry container MAIB auth (applied internally for the digital-worker model).
- Session ID resolution (query param → header → config → UUID fallback).
- Activity ID and session ID sanitization for header-injection defense.
- OpenTelemetry distributed tracing and W3C Baggage propagation.
- Error-source classification (`x-platform-error-source`) on all error responses.

### Other Changes

- Requires `azure-ai-agentserver-core>=2.0.0b8`.

