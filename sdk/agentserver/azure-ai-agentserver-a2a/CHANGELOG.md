# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial preview release of `azure-ai-agentserver-a2a`.
- Added `A2AAgentServerHost` for hosting native A2A v1.0 `AgentCard` and
  `RequestHandler` objects on the canonical Foundry container routes.
- Added request-scoped capture of `x-agent-foundry-call-id`,
  `x-agent-user-id`, and `x-agent-session-id`.
- Added cooperative composition with other Agent Server protocol hosts.
