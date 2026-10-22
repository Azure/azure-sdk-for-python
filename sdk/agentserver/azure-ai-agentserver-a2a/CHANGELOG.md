# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial preview release of `azure-ai-agentserver-a2a`.
- Added `A2AAgentServerHost` for hosting native A2A v1.0 `AgentCard` and
  `RequestHandler` objects on the canonical Foundry container routes.
- Added request-scoped capture of `x-agent-foundry-call-id` and
  `x-agent-user-id`.
- Added `x-platform-error-source` classification for transport-level HTTP
  errors.
- Added JSON-RPC streaming support on the canonical `/a2a` route.
- Added cooperative composition with other Agent Server protocol hosts.
- Added development-stage OpenTelemetry A2A server spans for JSON-RPC
  operations, including streaming lifetime, Agent Card metadata, task and
  conversation correlation, and JSON-RPC error classification.
- Added non-advertised compatibility aliases at `POST /invocations/a2a` and
  `GET /invocations/a2a/.well-known/agent-card.json` for older Foundry
  passthrough services and clients.

### Other Changes

- Requires `azure-ai-agentserver-core>=2.2.1,<3.0.0` for preservation of Agent
  Card metadata and the non-blocking span flush helper used by A2A tracing.
- Added an opt-in internal manual pipeline mode to publish A2A and core alpha
  packages together to the Azure SDK dev feed.
- Added sample setup instructions, a native local client, an incremental
  streaming Task example, and explicit in-memory state and durability guidance.

### Bugs Fixed

- Preserve shared request ID and server-version headers on exception-generated
  error responses.
- Read telemetry identifiers and task state only from A2A protocol fields,
  without interpreting application metadata or data-part contents.
- Omit A2A from the tracing-only live-test pipeline until it has a marked
  `tracing_e2e` suite; normal CI validation remains enabled.
- Keep pipeline artifact entries compatible with raw YAML namespace metadata
  extraction while limiting manual A2A alpha uploads to A2A and core.
