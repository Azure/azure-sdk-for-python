# Release History

## 1.0.0b3 (Unreleased)

### Features Added

- Container protocol version `2.0.0` support: the toolbox MCP bridge now echoes the per-request call ID (`x-agent-foundry-call-id`) on outbound Foundry toolbox calls. `initialize` / `tools/list` (run in the request task) read it from the request context; `tools/call` (dispatched on the Copilot engine task, where the request context var is empty) resolves it out-of-band keyed by the Copilot `session_id` and echoes it as both the HTTP header and `params._meta`. Copilot sessions are bound to a single user (`x-agent-user-id`) and never reused across users. No-op under protocol version `1.0.0` or local development.

## 1.0.0b2 (2026-04-24)

### Breaking Changes

- **Re-platformed onto agentserver-core 2.0 + agentserver-responses 1.0.**
  - `CopilotAdapter` no longer extends `FoundryCBAgent` (removed in core 2.0).
  - Uses `AgentHost` + `ResponseHandler` composition model instead.
  - Hypercorn replaces uvicorn as the ASGI server.
  - `_copilot_response_converter.py` and `_copilot_request_converter.py` removed — replaced by `ResponseEventStream` builders from the responses package.

### Features Added

- SSE streaming now uses correct RAPI event ordering (`text_done → content_part.done → output_item.done → completed`). The workaround of emitting `completed` before `text_done` is no longer needed.
- Built-in SSE keep-alive via `ResponsesServerOptions(sse_keep_alive_interval_seconds=...)`. Custom heartbeat logic removed.
- `ResponseEventStream` builders provide typed, state-machine-validated RAPI event construction.
- Usage tracking (input/output tokens) included in `response.completed` event.
- Foundry model discovery with 24-hour disk cache.
- MCP OAuth consent event handling.

### Bugs Fixed

- SSE streaming truncation on ADC (Envoy proxy) — fixed by Hypercorn + correct event ordering.
- Duplicate text in streaming responses — only `ASSISTANT_MESSAGE_DELTA` events emit deltas, not the final `ASSISTANT_MESSAGE`.

## 1.0.0b1 (2026-03-31)

### Features Added

- Initial beta release of the GitHub Copilot SDK adapter for Azure AI Agent Server.
- `CopilotAdapter`: Core adapter bridging Copilot SDK sessions to the Foundry Responses API (RAPI).
- `GitHubCopilotAdapter`: Convenience subclass with skill directory discovery and conversation history bootstrap.
- `ToolAcl`: YAML-based tool permission gating (shell, read, write, url, mcp).
- BYOK authentication via `DefaultAzureCredential` (Managed Identity) or static API key.
- Streaming and non-streaming response modes.
