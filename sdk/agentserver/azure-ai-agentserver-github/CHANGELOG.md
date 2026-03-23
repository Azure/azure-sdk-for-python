# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial beta release of the GitHub Copilot SDK adapter for Azure AI Agent Server.
- `CopilotAdapter`: Core adapter bridging Copilot SDK sessions to the Foundry Responses API (RAPI).
- `GitHubCopilotAdapter`: Convenience subclass with skill directory discovery and conversation history bootstrap.
- `ToolAcl`: YAML-based tool permission gating (shell, read, write, url, mcp).
- BYOK authentication via `DefaultAzureCredential` (Managed Identity) or static API key.
- Full OpenTelemetry integration (agent invocation spans + per-tool execution spans).
- Streaming and non-streaming response modes.
- Deferred done-events to avoid SSE burst-then-close race at ingress.
- Session idle safety net for forced completion.
