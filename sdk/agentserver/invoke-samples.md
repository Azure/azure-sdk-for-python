# Agent Invocation API — Sample Requests

Sample HTTP requests for the four operations in the `AgentInvocations` interface
defined in [invoke.tsp](./invoke.tsp).

> **Prerequisites** — every request requires a bearer token and the preview feature header:
>
> ```
> Authorization: Bearer <token>
> x-ms-foundry-preview: hosted_agents_v1_preview
> ```

Base URL pattern:

```
https://<foundry-endpoint>/agents/{agent_name}/versions/{agent_version}/invocations
```

> **Raw-bytes proxy.** Both request and response bodies are **opaque bytes**
> forwarded between the caller and the agent container. The `Content-Type` on
> each side is determined by the caller / container — not by the API itself.
> The examples below show *typical* container payloads; your agent may use
> entirely different formats.

---

## 1. Create invocation — simple text

```http
POST /agents/revenue-analyst/versions/1.0/invocations HTTP/1.1
Host: myproject.services.ai.azure.com
Authorization: Bearer <token>
x-ms-foundry-preview: hosted_agents_v1_preview
Content-Type: application/json

{
  "input": "Summarize Q4 earnings"
}
```

**Response** (raw bytes from container — shown here as JSON):

```http
HTTP/1.1 200 OK
Content-Type: application/json
x-agent-invocation-id: inv_a1b2c3
x-agent-session-id: sess_d4e5f6

{
  "output": "Q4 revenue was $4.2 B, up 12 % year-over-year."
}
```

---

## 2. Create invocation — with session

Continue a conversation by passing `agent_session_id` as a query parameter.

```http
POST /agents/revenue-analyst/versions/1.0/invocations?agent_session_id=sess_d4e5f6 HTTP/1.1
Host: myproject.services.ai.azure.com
Authorization: Bearer <token>
x-ms-foundry-preview: hosted_agents_v1_preview
Content-Type: application/json

{
  "input": "Now break it down by region"
}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
x-agent-invocation-id: inv_g7h8i9
x-agent-session-id: sess_d4e5f6

{
  "output": "North America: $2.1 B, EMEA: $1.3 B, APAC: $0.8 B."
}
```

---

## 3. Create invocation — streaming (container chooses SSE)

If the container returns `text/event-stream`, the raw SSE bytes are proxied
through unchanged. The event names below are a *container-level* convention,
**not** defined by the public API.

```http
POST /agents/revenue-analyst/versions/1.0/invocations HTTP/1.1
Host: myproject.services.ai.azure.com
Authorization: Bearer <token>
x-ms-foundry-preview: hosted_agents_v1_preview
Content-Type: application/json

{
  "input": "Summarize Q4 earnings in detail"
}
```

**Response** (raw bytes — container chose `text/event-stream`):

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
x-agent-invocation-id: inv_j1k2l3
x-agent-session-id: sess_m4n5o6

data: {"delta": "Q4 revenue was $4.2 B, "}

data: {"delta": "up 12 % year-over-year. "}

data: {"delta": "North America led with $2.1 B."}

data: [DONE]
```

---

## 5. Get invocation

Retrieve status / result by invocation ID. The response body is raw bytes
from the container.

```http
GET /agents/revenue-analyst/versions/1.0/invocations/inv_a1b2c3 HTTP/1.1
Host: myproject.services.ai.azure.com
Authorization: Bearer <token>
x-ms-foundry-preview: hosted_agents_v1_preview
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "completed",
  "output": "Q4 revenue was $4.2 B, up 12 % year-over-year."
}
```

---

## 6. Cancel invocation

Cancel a running invocation. Both request body and response body are optional
raw bytes forwarded to/from the container.

```http
POST /agents/revenue-analyst/versions/1.0/invocations/inv_g7h8i9/cancel HTTP/1.1
Host: myproject.services.ai.azure.com
Authorization: Bearer <token>
x-ms-foundry-preview: hosted_agents_v1_preview
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "cancelled"
}
```

### Cancel with a body

The container may accept a reason or metadata in the cancel request:

```http
POST /agents/revenue-analyst/versions/1.0/invocations/inv_g7h8i9/cancel HTTP/1.1
Host: myproject.services.ai.azure.com
Authorization: Bearer <token>
x-ms-foundry-preview: hosted_agents_v1_preview
Content-Type: application/json

{
  "reason": "User navigated away"
}
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "cancelled",
  "reason": "User navigated away"
}
```

---

## 7. Get OpenAPI spec

Discover the agent container's invocation contract. Returns `404` if the
container doesn't expose a spec.

```http
GET /agents/revenue-analyst/versions/1.0/invocations/docs/openapi.json HTTP/1.1
Host: myproject.services.ai.azure.com
Authorization: Bearer <token>
x-ms-foundry-preview: hosted_agents_v1_preview
```

**Response (200):**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "openapi": "3.0.3",
  "info": {
    "title": "revenue-analyst invocation API",
    "version": "1.0"
  },
  "paths": {
    "/invoke": {
      "post": {
        "summary": "Invoke the agent",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["input"],
                "properties": {
                  "input": { "type": "string" },
                  "metadata": { "type": "object" }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Response (404 — no spec):**

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": {
    "code": "NotFound",
    "message": "This agent does not expose an OpenAPI specification."
  }
}
```
