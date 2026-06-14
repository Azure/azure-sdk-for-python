# Release History

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
