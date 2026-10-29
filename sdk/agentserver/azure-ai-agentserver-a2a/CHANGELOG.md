# Release History

## 1.0.0b1 (Unreleased)

### Features Added

- Added `FoundryTaskStore`, implementing native Task persistence with Core's
  generic state store, caller isolation, and native list/filter/page semantics.
- Added executor-based `A2AAgentServerHost` construction with hosted Foundry
  storage/local in-memory defaults and explicit task-store overrides. Existing
  caller-supplied request handlers keep their storage unchanged.
- Added a state-store sample demonstrating Task retrieval after a server restart;
  task persistence does not enable automatic execution recovery.
- Initial preview release of `azure-ai-agentserver-a2a`.
- Added `A2AAgentServerHost` for hosting native A2A v1.0 `AgentCard` and
  `RequestHandler` objects on the canonical Foundry container routes.
- Added request-scoped capture of `x-agent-foundry-call-id` and
  `x-agent-user-id`.
- Added `x-platform-error-source` classification for transport-level HTTP
  errors.
- Added cooperative composition with other Agent Server protocol hosts.
- Added development-stage OpenTelemetry A2A server spans for JSON-RPC
  operations, including Agent Card metadata, request task
  and conversation correlation, and unary JSON-RPC error classification.
- Added non-advertised compatibility aliases at `POST /invocations/a2a` and
  `GET /invocations/a2a/.well-known/agent-card.json` for older Foundry
  passthrough services and clients.

### Other Changes

- Marked the public A2A host and task-store APIs as experimental.
- Added Python 3.15 metadata and migrated sample/test HTTP clients to `httpx2`.
- Simplified A2A tracing to reuse Core's span lifecycle helpers. Response inspection
  captures only a missing Task ID for correlation, without collecting response-only
  context IDs or task states.
- Consolidated tracing into one response wrapper and one span cleanup path for
  endpoint execution and response transmission, with shared JSON decoding.
- Requires `azure-ai-agentserver-core>=2.3.0b1,<3.0.0` for preservation of Agent
  Card metadata and the non-blocking span flush helper used by A2A tracing.
- Added an opt-in internal manual pipeline mode to publish A2A and core alpha
  packages together to the Azure SDK dev feed.
- Added sample setup instructions, a native local client, and explicit in-memory
  state and durability guidance.

### Bugs Fixed

- Select native Task-list pages from lightweight metadata before reading full
  snapshots, avoiding history/artifact downloads for every retained Task.
- Preserve explicit request conversation IDs on both A2A request spans when
  inbound baggage contains a conflicting conversation ID.
- Use an identifier-safe owner tag for managed state-store queries so hosted
  `ListTasks` succeeds as well as `GetTask`.
- Add a deployment-aware `invoke_agent` parent for hosted A2A message sends so
  trace discovery does not depend on model calls or native implementation spans.
  Keep Agent Card metadata on the child A2A span and preserve Task-ID correlation
  and error classification on both spans.
- Support validated brokered storage context when the A2A gateway omits the
  optional raw user-ID header; verify actual server-side user isolation before
  every item operation and keep per-request call IDs out of storage keys.
- Require native `a2a-sdk>=1.2.3` so active-task subscription/cancellation
  cache hits authorize through the caller-scoped task store. Earlier native
  implementations can bypass storage isolation on these paths.
- Preserve shared request ID and server-version headers on exception-generated
  error responses.
- Read telemetry identifiers only from A2A protocol fields,
  without interpreting application metadata or data-part contents.
- Omit A2A from the tracing-only live-test pipeline until it has a marked
  `tracing_e2e` suite; normal CI validation remains enabled.
- Keep pipeline artifact entries compatible with raw YAML namespace metadata
  extraction while limiting manual A2A alpha uploads to A2A and core.
- Align manual A2A alpha documentation updates with the packages actually
  published, register the native SDK dependency for shared analysis, and add
  the required README troubleshooting and next-steps sections.
