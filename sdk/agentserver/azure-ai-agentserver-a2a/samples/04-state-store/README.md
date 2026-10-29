# Persist A2A Tasks across server restarts

This example uses the existing generic Core state store to persist native A2A
Tasks. No LLM, subscription, or API key is needed for the local demonstration.

**Use the updated source checkout.** The previously published
`1.0.0a20261022002` A2A wheel does not include `FoundryTaskStore` or executor-based
host construction. A newly published alpha must include this feature before
using these APIs from a feed.

## Install

From the parent `samples` directory, follow the [source setup](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-a2a/samples/README.md#setup).
Its requirements install the A2A and Core packages from sibling source folders.

## 1. Start the persistent agent

From that same `samples` directory:

```powershell
$env:AGENTSERVER_STATE_ROOT = Join-Path $env:TEMP "a2a-state-store-demo"
.\.venv\Scripts\python 04-state-store\state_store.py
```

Locally, the sample explicitly supplies `FoundryTaskStore` to opt out of the
normal in-memory local default. Core stores the data in files under the chosen
state root.

## 2. Create a Task

In another terminal, from `samples`:

```powershell
.\.venv\Scripts\python sample_client.py --message "remember this"
```

The client prints:

```text
Task: <opaque-task-id>
Context: <opaque-context-id>
State: TASK_STATE_COMPLETED
Artifact: Persisted: remember this
```

Copy the Task ID.

## 3. Stop and restart the server

Stop the first process with Ctrl+C. Start it again with the **same**
`AGENTSERVER_STATE_ROOT` and store name:

```powershell
.\.venv\Scripts\python 04-state-store\state_store.py
```

Retrieve the earlier Task from the client terminal:

```powershell
.\.venv\Scripts\python sample_client.py --get-task "<opaque-task-id>"
```

The ID, context, completed state, and `Persisted: remember this` artifact remain
available even though the original server process is gone. The standard local
hello-world example does not retain Tasks across this restart.

## Hosted behavior and ownership

In a Foundry-hosted container, the sample leaves storage selection to the host:
the default is a Core-backed store scoped to the stable agent identity.
No physical session ID is used as the storage namespace. Access is isolated
by Foundry's configured caller scope, with native user/tenant scoping layered
into item keys. A trusted brokered call ID can be used when the container does
not receive a raw user-ID header. Every operation verifies server-side store
isolation; requests without usable identity/context fail rather than selecting
shared anonymous state. Core's storage identity and permission requirements
still apply.

If the preview A2A gateway does not forward platform identity or brokered
context, hosted storage fails closed. The gateway handoff must be fixed or
deployed before this sample can prove managed persistence across containers.
Local file-backed persistence does not validate that service integration.

To verify managed persistence, create two fresh hosted sessions pinned to the
same agent version and use the same authenticated caller. Send a message through
session A, then call `GetTask` and `ListTasks` through session B before sending
any message there. Compare the completed Task's ID, context, status, history,
and artifacts. Confirm session B's response session ID and distinct container
startup/runtime identity; reusing session A only tests retrieval in the original
process. JSON responses can differ in omitted protobuf defaults, so compare
decoded native Tasks when checking snapshot equality.

For local persistence, this sample owns its explicitly supplied store and closes
it through the host's shutdown handler. The host owns and closes the automatically
selected hosted store.

Native Task snapshots include status, history, and artifacts. Normal retention
and state-item size limits apply; large outputs should use artifact references.

## This is not crash recovery of work

This example proves **Task data persistence**, not that an unfinished operation
continues automatically. It does not create Core resilient tasks, replay an
executor, or restore a Python call stack. An interrupted `WORKING` Task needs
application-designed recovery. The completed Task used here can be fetched
without re-running its executor.
