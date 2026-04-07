# Missing Constructs: Python SDK vs .NET SDK

This document catalogs functionality gaps between the Python
`azure-ai-agentserver-responses` SDK and the .NET
`Microsoft.AI.AgentServer.Responses` SDK to guide future work.

---

## 1. `TextResponse` convenience class

| | |
|---|---|
| **Priority** | **High** |
| **Verdict** | Gap that should be filled |

### .NET

A single-expression helper that wraps the full response lifecycle
(created → in_progress → output item(s) → completed) for the most
common case — returning text:

```csharp
return new TextResponse(context, request, createText: ct => Task.FromResult("Hello"));
return new TextResponse(context, request, createTextStream: GenerateTokensAsync);
```

### Python today

Users must manually emit every lifecycle event:

```python
stream = ResponseEventStream(response_id=context.response_id, model=request.model)
yield stream.emit_created()
yield stream.emit_in_progress()
yield from stream.output_item_message("Echo: " + text)
yield stream.emit_completed()
```

`output_item_message()` / `aoutput_item_message()` handle the output
item itself, but the surrounding created/in_progress/completed envelope
is still boilerplate.

### Recommendation

Add a `TextResponse` (or `text_response()` generator function) that
yields the full event sequence. Sync and async variants, accepting
either a `str` or an `AsyncIterable[str]` for streaming. This is the
single highest-impact convenience for new users.

---

## 2. `ResponsesServer.Run<T>()` / `ResponseHandler` subclass pattern

| | |
|---|---|
| **Priority** | **Low** |
| **Verdict** | Acceptable difference — idiomatic Python already covered |

### .NET (Tier 1)

Zero-config one-liner using a generic host and handler subclass:

```csharp
ResponsesServer.Run<EchoHandler>();

class EchoHandler : ResponseHandler {
    public override Task HandleAsync(...) { ... }
}
```

### Python today

Decorator-based registration on a host object:

```python
app = ResponsesAgentServerHost()

@app.create_handler
def handler(request, context, cancellation_signal):
    ...

app.run(host="127.0.0.1", port=5200)
```

### Recommendation

The `@create_handler` decorator pattern is idiomatic Python and
achieves the same conciseness. No action needed.

---

## 3. `ResponsesClient` for upstream integration

| | |
|---|---|
| **Priority** | **Medium** |
| **Verdict** | Acceptable difference, but consider a thin helper |

### .NET

Ships a `ResponsesClient` for calling upstream Responses API servers:

```csharp
var client = new ResponsesClient("https://upstream/responses");
var response = await client.CreateResponseAsync(request);
```

### Python today

Users call upstream servers with the `openai` client library directly:

```python
from openai import OpenAI
client = OpenAI(base_url="https://upstream/responses")
```

### Recommendation

Because the OpenAI Python SDK natively speaks the Responses API, a
dedicated client class would duplicate functionality. A short recipe
in the samples showing how to call an upstream server with the `openai`
library is likely sufficient.

If the Responses wire format diverges from OpenAI in the future,
revisit adding a thin `ResponsesClient` wrapper.

---

## 4. `Translate().To<T>()` type conversion

| | |
|---|---|
| **Priority** | **Low** |
| **Verdict** | Acceptable difference — not idiomatic in Python |

### .NET

Automatic translation between strongly-typed client/server model
classes:

```csharp
var serverModel = clientModel.Translate().To<ServerCreateResponse>();
```

### Python today

Events are `dict[str, Any]` throughout the pipeline. Generated models
(`CreateResponse`, `ResponseObject`) are dict-compatible and
constructible from dicts. No type translation layer is needed because
everything is already the same representation.

### Recommendation

No action needed. The dict-based approach is the standard pattern in
Azure SDK for Python and avoids the complexity of maintaining parallel
type hierarchies. The generated models already support
`dict ↔ model` round-tripping via their constructors and
serialisation helpers.

---

## 5. `AddResponsesServer()` / `MapResponsesServer()` self-hosting middleware

| | |
|---|---|
| **Priority** | **Low** |
| **Verdict** | Acceptable difference |

### .NET

Explicit DI registration and endpoint mapping for ASP.NET Core:

```csharp
builder.Services.AddResponsesServer<EchoHandler>();
app.MapResponsesServer();
```

### Python today

The host creates a Starlette ASGI app mounted directly:

```python
app = ResponsesAgentServerHost()
# Starlette Mount() is used internally
app.run(host="127.0.0.1", port=5200)
```

The host object itself *is* an ASGI app and can be composed with
other Starlette/FastAPI routes via standard `Mount()`.

### Recommendation

No action needed. Python's ASGI ecosystem (Starlette, FastAPI) already
provides the equivalent of `Map*` with `Mount()` / `include_router()`.
Adding dedicated registration helpers would be non-idiomatic.

---

## 6. `AgentHost.CreateBuilder()` builder pattern

| | |
|---|---|
| **Priority** | **Medium** |
| **Verdict** | Gap — but a Python-idiomatic solution is preferred |

### .NET (Tier 2)

Fluent builder for advanced host configuration:

```csharp
var builder = AgentHost.CreateBuilder();
builder.AddResponsesServer<EchoHandler>();
builder.AddResponseStorage<InMemoryStore>();
builder.Build().Run();
```

### Python today

Configuration via constructor kwargs and mixin inheritance:

```python
class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
    pass

app = MyHost(
    options=ResponsesServerOptions(response_provider=InMemoryResponseProvider()),
)
```

### Recommendation

The kwargs + mixin pattern works but becomes unwieldy as the number of
options grows. Consider a lightweight builder or factory function:

```python
app = (
    AgentServerHostBuilder()
    .with_responses(handler=my_handler)
    .with_storage(InMemoryResponseProvider())
    .build()
)
```

This is lower priority than `TextResponse` — the current approach is
functional and documented.

---

## 7. DI / IoC container integration

| | |
|---|---|
| **Priority** | **Low** |
| **Verdict** | Acceptable difference |

### .NET

First-class dependency injection via the built-in DI container:

```csharp
builder.Services.AddSingleton<IMyService, MyService>();
```

Handlers receive dependencies through constructor injection.

### Python today

Dependencies are passed through closures, module-level state, or
explicit constructor arguments:

```python
db = Database(...)           # module-level

@app.create_handler
def handler(request, context, cancellation_signal):
    db.query(...)            # captured via closure
```

### Recommendation

No action needed. Python does not have a standard IoC container
convention. Closures and module-level state are the idiomatic
equivalent and are well-understood by Python developers. Libraries
like `dependency-injector` exist but would add a heavy dependency
for little benefit in this context.

---

## Summary

| # | Construct | Priority | Verdict |
|---|-----------|----------|---------|
| 1 | `TextResponse` convenience | **High** | Fill the gap |
| 2 | `Run<T>()` / handler subclass | Low | Acceptable — `@create_handler` is idiomatic |
| 3 | `ResponsesClient` | Medium | Acceptable — `openai` SDK covers this |
| 4 | `Translate().To<T>()` | Low | Acceptable — dict-based approach |
| 5 | `AddResponsesServer()` / `MapResponsesServer()` | Low | Acceptable — Starlette `Mount()` |
| 6 | `AgentHost.CreateBuilder()` | Medium | Consider Python-idiomatic builder |
| 7 | DI / IoC container | Low | Acceptable — closures / module state |

### Next steps

1. **Implement `TextResponse`** — highest impact, lowest effort.
   Wraps `emit_created()` + `emit_in_progress()` +
   `output_item_message()` + `emit_completed()` into a single call.
2. **Evaluate a builder/factory** for host construction once the
   number of configuration options warrants it.
3. **Add a sample** showing upstream server calls via the `openai`
   library to close the documentation gap for item 3.
