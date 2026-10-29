---
page_type: sample
languages:
- python
products:
- azure
name: azure-ai-agentserver-a2a samples for Python
description: Native A2A hosting, multi-protocol composition, and persistent Tasks.
---

# Azure AI Agent Server A2A samples

These examples use the official `a2a-sdk` for Agent Cards, executors, Tasks, and
artifacts. Agent Server adds the container hosting contract. No LLM, Azure
subscription, or API key is required for these deterministic local examples.

## Setup

Use Python 3.10 or later. Run these commands from this `samples` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

The requirements install A2A, core, and Invocations from sibling source
directories. Invocations is needed only for the multi-protocol example; it is
not a runtime dependency of the A2A package. Keep the current source checkouts
together, since the preview requires the core tracing fix in 2.3.0b3.
The updated A2A package requires native `a2a-sdk>=1.2.3` for caller authorization
on active-task cache lookups.

Only run one sample at a time on the default port, 8088. Stop the server before
switching examples.

## Samples

| Example | Start from this directory | What to observe |
|---------|---------------------------|-----------------|
| [Hello world](01-hello-world/hello_world.py) | `.\.venv\Scripts\python 01-hello-world\hello_world.py` | A completed Task containing `Hello from Foundry`. |
| [Multi-protocol](02-multi-protocol/multi_protocol.py) | `.\.venv\Scripts\python 02-multi-protocol\multi_protocol.py` | A2A and Invocations on the same server and port. |
| [State store](04-state-store/README.md) | `.\.venv\Scripts\python 04-state-store\state_store.py` | A completed Task can still be fetched after stopping and restarting the server. |

Every sample also exposes `GET /readiness` and the native Agent Card at
`GET /a2a/.well-known/agent-card.json`.

## Send a message

With the hello-world or multi-protocol server running, open another terminal
in this directory and run the [native client](sample_client.py):

```powershell
.\.venv\Scripts\python sample_client.py --message "hello"
```

The client discovers the Agent Card and uses native A2A types. Successful output
includes the opaque Task and context IDs, `TASK_STATE_COMPLETED`, and the
greeting artifact. The client explicitly selects A2A wire version 1.0.

For direct JSON-RPC requests:

```powershell
$request = @{
    jsonrpc = "2.0"
    id = "request-1"
    method = "SendMessage"
    params = @{
        message = @{
            messageId = "message-1"
            role = "ROLE_USER"
            parts = @(@{ text = "hello" })
        }
        configuration = @{ returnImmediately = $false }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8088/a2a" -Method Post `
    -ContentType "application/json" -Headers @{ "A2A-Version" = "1.0" } `
    -Body $request
```

## Retrieve state and reuse a context

Keep the same server process running. Copy the IDs printed by the client:

```powershell
.\.venv\Scripts\python sample_client.py --get-task "<task-id>"
.\.venv\Scripts\python sample_client.py --context-id "<context-id>" --message "hello again"
```

`GetTask` retrieves the stored Task, including its completed state and artifact.
Sending another message with the previous `contextId` creates a new greeting
Task in that context; it is not a request to resume a completed Task.

### What the examples do and do not store

- **Task ID:** identifies a native A2A Task and is used for local task lookup.
- **Context ID:** correlates related A2A messages/Tasks. Treat it as opaque.
- **TaskStore:** the hello-world and multi-protocol examples select native in-memory storage
  locally, so restarting the server loses their Tasks. Executor-based hosts
  default to Foundry-backed storage when hosted. The state-store example explicitly
  uses `FoundryTaskStore` locally so Core's file-backed store can demonstrate
  persistence across restarts.
- **Application memory:** reusing a context ID does not automatically create
  conversational memory, restore model history, or replay business operations.
  The executors here always return a fixed greeting.
- **Cancellation:** the examples do not implement cancellation; an attempted
  executor cancellation raises the native `TaskNotCancelableError`.

Custom stores and existing native request handlers are still supported and
remain caller-owned. Persistence alone does not resume executor work after a
process crash: recovery, cancellation, and application history need explicit
application design. See [the state-store example's restart walkthrough](04-state-store/README.md).

These are **local container** examples, not a claim that every native A2A
method is available through Foundry's public endpoint. When deployed, the
platform-returned Agent Card is authoritative. Foundry routes hosted sessions
using its documented context/isolation rules; an A2A context ID is not the
same thing as a platform session ID, and process-local state must not be assumed
to survive routing to a different container.

## Exercise the Invocations endpoint

With the multi-protocol server running:

```powershell
Invoke-RestMethod -Uri "http://localhost:8088/invocations" -Method Post `
    -ContentType "application/json" -Body '{"message":"hello"}'
```

Expected output: `{"message":"Hello over Invocations"}`.

## Change the local port or advertised URL

The samples derive their default Agent Card URL from core's `PORT` setting:

```powershell
$env:PORT = "8090"
.\.venv\Scripts\python 01-hello-world\hello_world.py
```

In the client terminal:

```powershell
.\.venv\Scripts\python sample_client.py --endpoint "http://localhost:8090"
```

Set `A2A_AGENT_URL` separately if a local proxy requires a different advertised
JSON-RPC URL. It changes the card, not the server's listening port. Native
clients send to the URL advertised by the card, so it must be reachable.

The examples disable the native SDK's generic instrumentation before importing
`a2a`, avoiding duplicate spans alongside Agent Server's semantic operation
spans. This can be overridden by explicitly setting
`OTEL_INSTRUMENTATION_A2A_SDK_ENABLED`. See the [package tracing guidance](../README.md#distributed-tracing)
for exporter configuration and the development-stage A2A convention.
