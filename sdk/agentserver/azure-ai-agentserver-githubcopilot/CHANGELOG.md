# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Initial beta release of the GitHub Copilot SDK adapter for Azure AI Agent Server.
- `CopilotAdapter`: Core adapter bridging Copilot SDK sessions to the Foundry Responses API (RAPI).
- `GitHubCopilotAdapter`: Convenience subclass with skill directory discovery and conversation history bootstrap.
- `ToolAcl`: YAML-based tool permission gating (shell, read, write, url, mcp).
- BYOK authentication via `DefaultAzureCredential` (Managed Identity) or static API key.
- Streaming and non-streaming response modes.
- Robust cross-platform SDK imports (handles version/platform differences in `github-copilot-sdk`).
