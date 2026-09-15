# Request-local work reuse

History ID lookups are reused only within a response request and only for the
same provider instance, previous response ID, conversation ID, limit, and
platform identity. Callers receive independent lists. Concurrent successful
lookups share a result; failures and cancellation do not populate the cache.
Concurrent input-reference readers similarly share one successful
materialization, while an unsuccessful owner releases the lock for retry.

Streaming requests close their request-owned iterators and await telemetry
flushing before the final HTTP body message. Flushing runs off the event loop,
not before the first stream event. Disconnects and cancellation still perform
cleanup and await the Core flush; no exporter work is fire-and-forget.
Non-streaming requests continue to await flushing before returning.

For non-stored streams, the request owns one producer task, including when
keep-alives are disabled. It closes the pipeline and developer iterator and
awaits asynchronous handler cleanup before orchestration finalization and
flushing. Handler iteration advances only after the preceding event is sent.
Stored and background producers remain independent of the HTTP connection;
closing a disconnected request must not close those producers.

Event normalization can reuse a privately owned coerced event. Validation still
runs before the event is appended. Public events and response snapshots remain
detached from handler input, completed items, and recovery seeds. Builder
initialization copies the mutable fields it retains rather than unrelated
request fields.

## Generated model loading

Public generated models remain real `TypedDict` classes with their canonical
module, name, annotations, dictionary constructors, and pickle identity. Model
classes and aliases are constructed on first access under a shared reentrant
lock. Explicit imports, introspection, and star imports can therefore construct
additional types; internal annotations use module references without requiring
those types at import time.

`make generate-models` invokes `_scripts/extract_model_contracts.py`, whose
finalization stage runs `_scripts/lazy_model_emitter.py`. The checked-in output
retains the canonical emitter declarations in a `TYPE_CHECKING` block. Do not
edit generated factories directly. After generation, verify deterministic
post-emitter output from the package directory:

```console
python _scripts/lazy_model_emitter.py --generated-root azure/ai/agentserver/responses/models/_generated --check
```

The generator tests cover extraction integration and reproducibility. The
model contract tests cover lazy access, exports, type hints, dictionary
construction, and pickle resolution.
