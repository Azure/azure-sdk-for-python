# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial release of `azure-ai-agentserver`.
- Generic `AgentServer` base class with pluggable protocol heads.
- `/invoke` protocol head with all 4 operations: create, get, cancel, and OpenAPI spec.
- OpenAPI spec-based request/response validation via `jsonschema`.
- Health check endpoints (`/liveness`, `/readiness`).
- Streaming and non-streaming invocation support.
