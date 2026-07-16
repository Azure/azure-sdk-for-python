# Release History

## 1.0.0b4 (Unreleased)

### Other Changes

- Internal refactor only; no public API changes. Consolidated the default storage
  backend resolution to a single place (`ActivityAgentServerHost._resolve_storage`)
  and made the internal M365 stack builder require a resolved `storage`. Renamed
  internal symbols for naming consistency (framework adapter and bridge helpers).

## 1.0.0b2 (Unreleased)

### Features Added

- Container protocol version `2.0.0` support: reads `x-agent-user-id` and `x-agent-foundry-call-id` from inbound requests and binds them to the request-scoped platform context so the per-request call ID is forwarded on outbound Foundry 1P calls (`x-agent-user-id` is not forwarded to 1P). The values are available to handler and tool code via `azure.ai.agentserver.core.get_request_context()`.
- Added the module-level `get_hosted_agent_env(*, digital_worker=False)` helper, which returns a config mapping (`os.environ` overlaid with the derived `CONNECTIONS__*` settings from the Foundry-native `FOUNDRY_AGENT_*` env vars) **without mutating the process environment**. Pass its result to `load_configuration_from_env(...)`. The default construction path derives this for you; call it yourself only when you build the `MsalConnectionManager` (or a pre-built `AgentApplication`) manually. The outbound-auth client id and hosting flag are now captured once at build time and threaded into request handling, so per-request auth never reads process-global environment state.

### Breaking Changes

- Custom handlers and pre-built `AgentApplication` injection use dedicated
  keyword-only constructor arguments (renamed from the `1.0.0b1` `handler=`):
  - `ActivityAgentServerHost(handler=fn)` → `ActivityAgentServerHost(request_handler=fn)`
  - Pre-built injection: `ActivityAgentServerHost(agent_app=app)`
  The default constructor accepts the build-the-M365-stack options
  (`digital_worker`, `storage`, `connection_manager`, `adapter`,
  `authorization`, `connection_config`). `ActivityAgentServerHost()` (simple
  Teams agent) is unchanged.
- Removed the lazy M365 initialization and the ``@app.activity(...)`` / ``@app.error`` host decorators in their old form. When constructed directly (no `request_handler`), the M365 Agents SDK is now initialized eagerly during `ActivityAgentServerHost(...)` construction and the built `AgentApplication` is exposed as the `host.agent_app` property. Register handlers on it with `@host.agent_app.activity(...)` / `@host.agent_app.error`, and reach the rest of the M365 surface (`message`/`proactive`/`auth` ...) the same way; you can also capture it (`app = host.agent_app`) and use it standalone. The adapter is available via `host.adapter`.
  - The previous implicit attribute delegation (`__getattr__` forwarding `app.activity` to the underlying `AgentApplication`) was removed in favor of the explicit, statically-typed `host.agent_app` property. Update `@app.activity(...)` → `@host.agent_app.activity(...)` and `@app.error` → `@host.agent_app.error`.
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
