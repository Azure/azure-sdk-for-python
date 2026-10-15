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
