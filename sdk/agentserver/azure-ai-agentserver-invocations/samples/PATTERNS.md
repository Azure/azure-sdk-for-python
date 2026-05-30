# Invocations Durable Sample Patterns

This file collects the small set of invocations-protocol-native patterns that
durable invocation samples should follow when they use the
`azure-ai-agentserver-core` durable-task primitive. It complements
`azure-ai-agentserver-responses/docs/handler-implementation-guide.md` —
which is the canonical guide for the responses layer — by translating the
patterns that responses presents through its `DurabilityContext` wrapper into
the primitive-direct shape that invocation samples use.

If a pattern is documented in both places, the responses guide is the
authoritative source for *why*; this file is the authoritative source for
*how it looks in an invocations sample*.

## 1. Use `@task` directly, not a wrapped context

Invocation samples build on the primitive directly. There is no
`DurabilityContext` adapter. Pass `TaskContext` straight through:

```python
from azure.ai.agentserver.core.durable import task, TaskContext

@task(name="my_agent")
async def my_agent(ctx: TaskContext) -> str:
    ...
```

## 2. Cross-lifetime retry semantics

`ctx.retry_attempt` is **durable across crash/recovery**. It increments only
when the handler raises a retryable failure; crash recovery does NOT consume
the budget. Resets to 0 on successful completion and on steering drain. Use
`ctx.entry_mode == "recovered"` to detect "we were re-entered after a crash"
specifically.

## 3. Metadata namespaces

`ctx.metadata` is a callable namespace facade:

```python
# Default namespace
ctx.metadata["my_checkpoint"] = "abc-123"

# Sibling namespace (independent flush state and persistence slot)
session_ns = ctx.metadata("session")
session_ns["upstream_id"] = "sess-xyz"
await session_ns.flush()
```

Each namespace tracks dirty state independently and is snapshotted at
lifecycle boundaries. Persistence layout: `payload["metadata"]` for the
default namespace, `payload["metadata:<name>"]` for named namespaces.

Invocations samples talk to the primitive directly, so **the primitive does
not enforce `_*`-prefix rejection** on namespace names or keys (that rule
applies only to the responses-layer wrapper). Even so, the `_*` convention
is reserved for framework-internal namespaces — invocation sample authors
should avoid those prefixes for their own state.

## 4. At-most-once side effect pattern

Identical to the responses-side pattern, just expressed through the raw
primitive:

```python
@task(name="agent_with_side_effect")
async def my_agent(ctx: TaskContext) -> None:
    if ctx.metadata.get("emitted_token") is None:
        token = generate_dedup_token()
        ctx.metadata["emitted_token"] = token
        await ctx.metadata.flush()  # fence BEFORE the side effect
        await call_external_service(token=token)
    else:
        # Recovered after we already issued the side effect — skip.
        ...
```

## 5. Steering / multi-turn

Use `ctx.pending_inputs` to drain queued inputs in steerable-conversation
patterns. See the `multiturn_invoke_agent` and `durable_multiturn` samples
for the canonical shape.

## 6. What this is NOT

- **Not** a tutorial — see the `azure-ai-agentserver-core` durable-task
  developer guide for the full mental model.
- **Not** a replacement for the responses-layer
  `handler-implementation-guide.md` — invocation samples and responses
  handlers have different runtime shapes, and the responses guide carries
  details (stream events, response object lifecycle, resumption response)
  that do not apply to invocations.
