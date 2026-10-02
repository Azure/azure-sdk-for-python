# Release History

## 1.0.0b4 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0b3 (2026-08-21)

### Features Added

- `FoundryStorage` adapter backed by `FoundryStateStore` — Implements the M365 `AsyncStorageBase` interface on top of the durable Foundry state store KV layer. Each M365 storage key maps to a per-key FoundryStateStore with user-scoped key isolation. Hosted Activity agents default to `FoundryStorage` in Foundry containers and `MemoryStorage` for local development.

### Breaking Changes

- Removed the `POST /api/messages` route alias. Inbound activities are served only at `POST /activity/messages`, which is the endpoint the Foundry platform routes to. Callers that posted to `/api/messages` must use `/activity/messages`.
- Removed public SSE keepalive helper.

### Other Changes

- Fixed activity typing and claims test compatibility with M365 SDK 1.4.0. The package now handles the new `py.typed` marker in `microsoft-agents-hosting-core` 1.4.0 and the deprecated `is_authenticated` property.
- Updated FoundryStorage compatibility with `microsoft-agents-hosting-core` 1.3.0+ (`target_cls` is now a keyword-only argument in `AsyncStorageBase.read`).

## 1.0.0b2 (2026-07-28)

### Other Changes

- Digital-worker (MAIB) outbound auth now uses the M365 Agents SDK's native `IdentityProxyManager` connection auth type instead of a custom MSAL monkeypatch (`_apply_msal_patches`), which previously overrode `MsalAuth.get_agentic_application_token` to perform the federated-identity (FMI) token exchange. The M365 SDK performs that exchange natively from `1.1.0`.
- Raised the Microsoft 365 Agents SDK dependency floors to `>=1.1.0` (`microsoft-agents-hosting-core`, `microsoft-agents-authentication-msal`, `microsoft-agents-activity`): the `IdentityProxyManager` connection auth type is only available from `1.1.0`.
- Removed the `azure-identity` runtime dependency: it was only used by the now-removed MSAL patch.

## 1.0.0b1 (2026-07-22)

### Features Added

- Initial preview release of `azure-ai-agentserver-activity`.
- `ActivityAgentServerHost` — Starlette-based host for Activity Protocol traffic.
- `POST /activity/messages` and `POST /api/messages` endpoints with the Foundry platform header contract.
- Simple Teams agent path: `ActivityAgentServerHost()` builds the M365 Agents SDK stack eagerly during construction and exposes the built `AgentApplication` as the `host.agent_app` property. Register handlers with `@host.agent_app.activity(...)` / `@host.agent_app.error`, and reach the rest of the M365 surface (`message` / `proactive` / `auth`) the same way. The adapter is available via `host.adapter`.
- Custom handler support: `ActivityAgentServerHost(request_handler=fn)` for full request/response control without the M365 SDK.
- Pre-built injection: `ActivityAgentServerHost(agent_app=app)`, plus build options on the default constructor (`digital_worker`, `storage`, `connection_manager`, `adapter`, `authorization`, `connection_config`).
- Durable hosted storage: when `storage` is omitted, `ActivityAgentServerHost` defaults to `FoundryStorage` in Foundry-hosted containers and keeps `MemoryStorage` as the local-development default.
- Container protocol version `2.0.0` support: reads `x-agent-user-id` and `x-agent-foundry-call-id` from inbound requests and binds them to the request-scoped platform context so the per-request call ID is forwarded on outbound Foundry 1P calls (`x-agent-user-id` is not forwarded to 1P). Values are available to handler and tool code via `azure.ai.agentserver.core.get_request_context()`.
- Module-level `get_hosted_agent_env(*, digital_worker=False)` helper that returns a config mapping (`os.environ` overlaid with the derived `CONNECTIONS__*` settings from the Foundry-native `FOUNDRY_AGENT_*` env vars) **without mutating the process environment**.
- MSAL auth patches for Foundry container MAIB auth (applied internally for the digital-worker model).
- Session ID resolution (query param → header → config → UUID fallback).
- Activity ID and session ID sanitization for header-injection defense.
- OpenTelemetry distributed tracing and W3C Baggage propagation.
- Error-source classification (`x-platform-error-source`) on all error responses.

### Other Changes

- Requires `azure-ai-agentserver-core>=2.0.0b8`.
