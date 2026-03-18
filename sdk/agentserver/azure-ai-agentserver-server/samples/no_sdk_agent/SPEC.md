# Invocation API Spec

This document defines the HTTP contract that an agent container must implement
to run on the platform. No SDK is required — any language or framework that
can serve HTTP is supported.

## Required

### `POST /invocations`

Execute the agent.

- **Port:** `8088`.
- **Request body:** Any content type. The schema and format are defined by your
  agent — the platform does not enforce a specific shape or media type.
- **Response body:** Any content type. The schema and format are defined by your
  agent.

## Optional Features

The following endpoints and capabilities are **not required** by the platform.
Implement them only if your agent needs the corresponding functionality.

### Async polling and cancel

The platform only calls `POST /invocations`.  If your agent needs async
polling or cancel, you can add your own endpoints under `/invocations/`
with any paths and schemas you choose.

### OpenAPI spec — `GET /invocations/docs/openapi.json`

Serve an OpenAPI spec describing your agent's request/response schema.
The platform can use this for documentation and request validation.

### Health probes — `GET /liveness` and `GET /readiness`

Standard Kubernetes health probes.  Implement these if your container
runs in a Kubernetes environment and you need the orchestrator to detect
unhealthy or unready instances.

- `/liveness` — return `200` when the process is alive.
- `/readiness` — return `200` when the agent is ready to accept requests
  (e.g. models loaded, connections established).

### Invocation ID tracking

The platform may send an `x-agent-invocation-id` request header.
If present, echo it back on the response.  If absent, generate a UUID
and include it on the response.  This enables end-to-end correlation
of requests across services.

### OpenTelemetry tracing with App Insights export

Integrate with Foundry distributed tracing by creating spans for each
invocation and exporting them to Application Insights.  See the
[Tracing](#tracing) section below for details.

## Headers

| Header | Direction | Description |
|--------|-----------|-------------|
| `x-agent-invocation-id` | Request | Platform may send an invocation ID. If absent, agent may generate a UUID. |
| `traceparent` | Request | W3C Trace Context header for distributed tracing. |
| `tracestate` | Request | W3C Trace Context header for distributed tracing. |
| `baggage` | Request | W3C Baggage for cross-service context propagation. |

## Query Parameters

| Parameter | Description |
|-----------|-------------|
| `agent_session_id` | Session or conversation ID for tracing correlation. Maps to `gen_ai.conversation.id` span attribute. |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_NAME` | | Agent name |
| `AGENT_VERSION` | | Agent version |
| `AGENT_PROJECT_NAME` | | Azure foundry project name  |

## Tracing

To integrate wtih foundry tracing, the agent should create an OpenTelemetry span for each
`POST /invocations` request and export traces to Application Insights via
`azure-monitor-opentelemetry-exporter`.

### W3C Trace Context propagation

Extract `traceparent` and `tracestate` from the incoming request headers and use
them as the parent context for the span.  This connects the agent's spans to the
platform's distributed trace.

### `leaf_customer_span_id` (baggage)

The platform may send a `baggage` header containing a `leaf_customer_span_id`
key.  When present, the agent **must** override the parent span ID from
`traceparent` with this value.  This re-parents the agent's root span under
the caller's leaf span so the trace tree renders correctly in App Insights.

The value is a 16-character lower-hex span ID.  To apply it:

1. Extract the trace context from `traceparent` normally.
2. Parse `leaf_customer_span_id` from the `baggage` header.
3. Create a new `SpanContext` with the same `trace_id` but the
   `span_id` replaced by the baggage value.
4. Use the new context as the parent when starting the span.

### Span attributes

Each span should include the following GenAI semantic convention attributes:

| Attribute | Source | Description |
|-----------|--------|-------------|
| `invocation.id` | `x-agent-invocation-id` header or generated UUID | Unique invocation identifier |
| `gen_ai.response.id` | Same as `invocation.id` | Maps response to invocation |
| `gen_ai.provider.name` | `"microsoft.foundry"` | Fixed provider name |
| `gen_ai.agent.id` | `AGENT_NAME` + `AGENT_VERSION` env vars | Agent identity, e.g. `"my-agent:1.0"` |
| `microsoft.foundry.project.id` | `AGENT_PROJECT_NAME` env var | Project identifier |
| `gen_ai.operation.name` | `"invoke_agent"` | Operation type |
| `gen_ai.conversation.id` | `agent_session_id` query parameter | Session/conversation ID |
