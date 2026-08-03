# Azure Core - Design Decision History

A chronological record of **why** `azure-core` looks the way it does.

This is not a changelog and not a reference guide. [CHANGELOG.md](./CHANGELOG.md) tells you *what*
changed; [README.md](./README.md) and [CLIENT_LIBRARY_DEVELOPER.md](./CLIENT_LIBRARY_DEVELOPER.md)
tell you *what things are*. This file captures the **non-obvious context** behind decisions that
still constrain the codebase today — the reverts, the workarounds, the deliberate duplications, and
the load-bearing details that look like accidents but aren't.

Read this before you "clean up" something in `azure-core` that looks wrong.

**Audience:** new contributors to `azure-core`, and AI agents making changes here.

**Conventions used below:**

- Dates are the **merge date of the commit into `main`**, derived from `git log`, not the PR open date.
- 🪤 marks a **trap**: something that will bite you if you change it without knowing the history.

---

## Table of contents

- [The constraints that govern everything](#the-constraints-that-govern-everything)
- [2019 — Track 2 genesis](#2019--track-2-genesis)
- [2019–2020 — Hardening toward 1.0 and beyond](#20192020--hardening-toward-10-and-beyond)
- [2020 — LRO, paging, and the exception model](#2020--lro-paging-and-the-exception-model)
- [2021 — The `azure.core.rest` rewrite](#2021--the-azurecorerest-rewrite)
- [2021–2022 — Shared utility types and the dependency diet](#20212022--shared-utility-types-and-the-dependency-diet)
- [2023 — Type completeness and security hardening](#2023--type-completeness-and-security-hardening)
- [2023–2025 — Auth modernization](#20232025--auth-modernization)
- [2024–2025 — Native OpenTelemetry](#20242025--native-opentelemetry)
- [2025–2026 — Serialization extensibility and safer tokens](#20252026--serialization-extensibility-and-safer-tokens)
- [Recurring patterns worth internalizing](#recurring-patterns-worth-internalizing)

---

## The constraints that govern everything

Four facts explain most of the strange decisions in this codebase. Everything below is downstream of
these.

1. **`azure-core` is the bottom of the dependency graph.** Every Azure SDK for Python package depends
   on it. A breaking change here breaks hundreds of packages, many of which are pinned to old
   versions and shipped by teams who will not re-release quickly. This is why azure-core almost never
   removes anything, and why "deprecated" here usually means "documented as legacy but still fully
   functional forever."

2. **Most consumers are generated code, not humans.** TypeSpec and AutoRest emit code against
   azure-core's API surface. When you change a signature, you are not just breaking user code — you
   are breaking a code generator's contract, which requires cross-repo coordination to fix. This is
   why new capabilities are so often smuggled in through `**kwargs` and option dictionaries rather
   than new parameters.

3. **Dependencies are treated as a liability.** Every dependency azure-core takes is forced on every
   Azure SDK user on Earth. The default answer to "can we add a dependency?" is no. See the
   `requests`, `chardet`, and `six` entries below for how hard the team worked to remove them, and
   the `anyio` entry for what it costs when one is added.

4. **azure-core must not be biased toward any HTTP library.** This is the reason for the pervasive
   generics (`HTTPRequestType`, `HTTPResponseType`) that make the typing so heavy. If the types were
   concrete, the abstraction would be a lie.

---

## 2019 — Track 2 genesis

### The pipeline is a linked list, not a middleware stack

**2019-05 · [#5306](https://github.com/Azure/azure-sdk-for-python/pull/5306)** (initial move to Track 2 location)

`Pipeline.__init__` does not store a list it later iterates. It wires each policy to the next at
construction time and hands the transport to the last one
([`_base.py`](./azure/core/pipeline/_base.py)):

```python
for index in range(len(self._impl_policies) - 1):
    self._impl_policies[index].next = self._impl_policies[index + 1]
if self._impl_policies:
    self._impl_policies[-1].next = _TransportRunner(self._transport)
```

Each `HTTPPolicy` is responsible for calling `self.next.send(request)` itself. This chain-of-
responsibility design was chosen because it lets a policy decline to call `next` at all, or call it
many times — which is exactly what `RetryPolicy` and `RedirectPolicy` need. A middleware stack that
iterated a list could not express "loop without unwinding the stack."

🪤 **Policy instances are stateful and bound to one pipeline.** Constructing a second `Pipeline` with
the same policy objects silently rewrites their `.next` pointers and corrupts the first pipeline.
Never share policy instances across pipelines.

### `SansIOHTTPPolicy` exists so one implementation serves both sync and async

**2019-05 onward; hierarchy cleaned up 2021-01 · [#15831](https://github.com/Azure/azure-sdk-for-python/pull/15831)**

There are two policy families, and the split is not stylistic:

- `SansIOHTTPPolicy` — performs no I/O. It exposes `on_request` / `on_response` / `on_exception`
  hooks and is wrapped by `_SansIOHTTPPolicyRunner` inside *both* the sync and async pipelines. One
  class, both worlds.
- `HTTPPolicy` / `AsyncHTTPPolicy` — owns the call chain, calls `next.send()`, and may perform I/O.
  Requires two separate implementations.

#15831 untangled the inheritance so `AsyncHTTPPolicy` no longer derives from `HTTPPolicy`.

🪤 **Write new policies as `SansIOHTTPPolicy` unless you genuinely need to loop, redirect, or await.**
Choosing `HTTPPolicy` unnecessarily doubles your implementation and test burden forever.

### `settings` is a process-global singleton with env-var precedence

**2019-05 · [#5344](https://github.com/Azure/azure-sdk-for-python/pull/5344), [#5525](https://github.com/Azure/azure-sdk-for-python/pull/5525); `unset` sentinel 2019-06 · [#6090](https://github.com/Azure/azure-sdk-for-python/pull/6090)**

`PrioritizedSetting` resolves a value through a fixed precedence chain: call-time value → explicitly
set value → environment variable → system hook → default. The design intent was that operators can
change SDK behavior via environment variables without touching code, while tests and applications can
still force a value in-process.

The `unset` sentinel (#6090) exists to distinguish "the user explicitly set this to `None`" from "the
user never set this" — needed so a test can *clear* a setting rather than pin it to `None`. It was
added, per the PR, because tracing work "makes heavy use of settings."

🪤 `settings.tracing_implementation` is a `PrioritizedSetting` *descriptor*. You must **call** it —
`settings.tracing_implementation()` — to resolve a value. Reading it without parentheses returns the
descriptor object, which is truthy, so `if settings.tracing_implementation:` is always `True`. This
is a common and silent test bug.

🪤 `settings` is global. Mutating it affects every client in the process. Per-client behavior belongs
in client constructor kwargs (`logging_enable=True`), not here.

### Tracing was abstracted behind `AbstractSpan` because the industry hadn't picked a winner

**2019-07 · [#6196](https://github.com/Azure/azure-sdk-for-python/pull/6196)**

In mid-2019, OpenCensus and OpenTracing were both live and OpenTelemetry was announced but not
stable. Rather than bet on one, azure-core defined its own `AbstractSpan` protocol so that SDK
libraries would not need to change when a winner emerged.

This was a reasonable bet that has since been superseded — see
[Native OpenTelemetry](#20242025--native-opentelemetry). The cost of the bet is the dual tracing
architecture that exists today.

### Tracing context uses `contextvars`, and locks were deliberately removed

**2019-07 · [#6497](https://github.com/Azure/azure-sdk-for-python/pull/6497), [#6551](https://github.com/Azure/azure-sdk-for-python/pull/6551)**

The initial implementation copied OpenCensus's design, which used a locked registry of arbitrary
context slots. #6551 removed the locks by constraining the context to carry *only* the current span:
> "My simplification is that only `current_span` can be in the context at this point. This makes it
> so that I do not need the thread lock."

#6497 removed a `should_only_propagate` flag that duplicated what "no tracing implementation
configured" already meant. This established the still-current binary rule: tracing is either on or
off, with no intermediate propagate-only mode.

Today the decorators use `contextvars.ContextVar` (`_in_span_context` in
[`tracing/decorator.py`](./azure/core/tracing/decorator.py)), which gives correct per-task isolation
under asyncio.

🪤 `contextvars` do **not** propagate to manually spawned threads. If you `Thread(...)` out of an SDK
call, you must copy and activate the context yourself.

### `@distributed_trace` only creates a span at the outermost SDK call

**2019-07 · [#6299](https://github.com/Azure/azure-sdk-for-python/pull/6299), [#6530](https://github.com/Azure/azure-sdk-for-python/pull/6530); documented 2024-09 · [#37478](https://github.com/Azure/azure-sdk-for-python/pull/37478)**

SDK methods frequently call other decorated SDK methods internally. Without suppression this produces
a noisy forest of nested spans that means nothing to the user. The decorator checks whether an SDK
span is already active and, if so, does not push another.

🪤 **`@distributed_trace` is for Azure SDK library authors only** — #37478 added this to the docstring
explicitly. Application developers who decorate their own functions with it will usually get nothing.
They should use OpenTelemetry's own APIs.

### Paging v2 separated page iteration from item iteration

**2019-07 · [#6420](https://github.com/Azure/azure-sdk-for-python/pull/6420)**

Track 1 returned a flat iterator of items and made page boundaries inaccessible — so you could not
checkpoint, resume, or read a continuation token. Paging v2 introduced two layers:

- `PageIterator` — an iterator *of pages*, each page itself an iterator of items.
- `ItemPaged` — wraps `PageIterator` with `itertools.chain.from_iterable` to present the flat view
  most users want, and exposes the page layer via `by_page(continuation_token=...)`.

🪤 `ItemPaged` is lazy — no HTTP request is issued until you iterate. And **`by_page()` returns a
fresh `PageIterator` on every call**; mixing `by_page()` with direct iteration of the same
`ItemPaged` issues duplicate requests.

---

## 2019–2020 — Hardening toward 1.0 and beyond

### Auth policy sits *after* retry, and this ordering is load-bearing

**2019-12 · [#8997](https://github.com/Azure/azure-sdk-for-python/pull/8997)**

The default policy order places `BearerTokenCredentialPolicy` *inside* (after) `RetryPolicy`. Retry is
the outer loop; auth is inner. This means every retry attempt re-enters the auth policy, which
re-checks token validity and can acquire a fresh token.

If auth ran before retry, a 401 caused by an expired token would bubble out to retry, which would
replay the request with the same dead token until the retry budget was exhausted. The same PR added
`ProxyPolicy` to the defaults.

🪤 This is why `per_call_policies` and `per_retry_policies` are distinct
([#18406](https://github.com/Azure/azure-sdk-for-python/pull/18406), 2021-05). `per_call` runs once
per SDK call; `per_retry` runs on every attempt. **Anything that must be recomputed per attempt —
auth, request ID, logging — must be `per_retry`.**

### Bearer tokens require HTTPS, but there is a deliberate escape hatch

**2019-12 · [#8887](https://github.com/Azure/azure-sdk-for-python/pull/8887); escape hatch 2020-03 · [#9821](https://github.com/Azure/azure-sdk-for-python/pull/9821); refactored 2026-03 · [#45890](https://github.com/Azure/azure-sdk-for-python/pull/45890)**

#8887 made the auth policy raise `ServiceRequestError` on non-HTTPS URLs, because a bearer token sent
in plaintext is a leaked credential. #9821 then added `enforce_https=False` — not because anyone wanted
to send tokens over HTTP, but because **multipart/batch sub-request preparation passes schemeless
URLs** through the policy. The author's reasoning:
> "I think configuration to disable validation entirely is more generally useful and less weird than
> configuration to allow malformed URLs."

🪤 The flag is read from `context.options` but **stored onto `request.context`**, because
`context.options` is consumed on the first attempt and would vanish on retry. #45890 factored this
into a module-level `_enforce_https()`. If you touch this, preserve the options→context promotion or
retries will start failing on the second attempt.

### `ClientAuthenticationError` short-circuits retry on purpose

**2019-06 · [#6025](https://github.com/Azure/azure-sdk-for-python/pull/6025)**

`RetryPolicy` catches `AzureError` broadly, which originally swallowed credential failures and retried
them. Since the credential has already done its own internal retrying, the client request is doomed —
retrying only buries the real error under layers of exception chaining.

🪤 **A custom credential must raise `ClientAuthenticationError` for terminal auth failures.** Raise
anything else and the retry policy will dutifully retry a request that can never succeed.

### `Retry-After-Ms` is a real Azure header, and 429 needed adding explicitly

**2019-12 · [#9100](https://github.com/Azure/azure-sdk-for-python/pull/9100), [#9241](https://github.com/Azure/azure-sdk-for-python/pull/9241); body rewind [#8871](https://github.com/Azure/azure-sdk-for-python/pull/8871); float support 2024-02 · [#34253](https://github.com/Azure/azure-sdk-for-python/pull/34253)**

429 was not in the original retryable set. Separately, some Azure services return `Retry-After-Ms`
(milliseconds) instead of the standard `Retry-After` (seconds), so the policy parses both. #8871 added
body rewinding so a retried request can resend a seekable body.

🪤 **If the request body is a non-seekable stream, retry cannot resend it correctly.** This is a real
limitation, not a bug to fix casually.

### `retry_backoff_max` was silently ignored for roughly six years

**2025-08 · [#42444](https://github.com/Azure/azure-sdk-for-python/pull/42444)**

The constructor stored `retry_backoff_max` into `self.backoff_max`, but `_configure_retry` read
`options.pop("retry_backoff_max", self.backoff_factor)` — defaulting to the wrong attribute. Users who
set `retry_backoff_max` at the client level got the default backoff cap instead. It is now correct:

```python
"max_backoff": options.pop("retry_backoff_max", self.backoff_max),
```

Included here as a caution: this file's settings plumbing is repetitive and typo-prone, and a typo
here produces no error, just silently wrong behavior. Add a test whenever you touch it.

### Retry must not sleep after an operation timeout

**2021-05 · [#18548](https://github.com/Azure/azure-sdk-for-python/pull/18548)**

`_configure_timeout` raises an `AzureError` subclass when the overall operation timeout is exceeded.
The generic `except AzureError` in the retry loop caught it, slept the backoff, looped, and
immediately raised again — burning the full retry budget in sleep without ever sending a request.
Timeout exceptions are now re-raised immediately.

### `BiggerBlockSizeHTTPAdapter` is a targeted Windows perf workaround, not an abstraction

**2020-11 · [#14442](https://github.com/Azure/azure-sdk-for-python/pull/14442)**

[Issue #11044](https://github.com/Azure/azure-sdk-for-python/issues/11044) reported streaming uploads
being dramatically slower through the SDK than through raw `requests` on Windows over high-latency
cross-region links. Root cause: urllib3's default 8 KB TCP block size caused excessive syscalls. The
fix subclasses `HTTPAdapter` to set `blocksize=32768`.

🪤 [`_bigger_block_size_http_adapters.py`](./azure/core/pipeline/transport/_bigger_block_size_http_adapters.py)
reaches into urllib3 internals (`conn.conn_kw`). It is version-gated and will break silently if
urllib3 changes that API. Do not mistake it for a general extension point.

### Multipart/mixed runs a nested pipeline per sub-request

**2019-10 · [#7083](https://github.com/Azure/azure-sdk-for-python/pull/7083); options separated 2020-04 · [#10616](https://github.com/Azure/azure-sdk-for-python/pull/10616); changesets 2020-05 · [#10972](https://github.com/Azure/azure-sdk-for-python/pull/10972)**

Azure Storage batch operations require each sub-request inside a `multipart/mixed` body to be
independently authenticated and header-decorated. The implementation therefore runs each sub-request
through its own mini-pipeline. #10616 separated the sub-request pipeline options from the outer
request's, which had been bleeding into each other.

🪤 Retry and auth execute **independently per sub-request**. When debugging a batch failure, the outer
request's pipeline trace is not the whole story.

---

## 2020 — LRO, paging, and the exception model

### LRO moved out of `msrest`, and ARM-specific polling deliberately stayed out of core

**2020-03 · [#10090](https://github.com/Azure/azure-sdk-for-python/pull/10090)**

Track 1 kept LRO logic in `msrest`/`msrestazure`. When it was brought into azure-core for Track 2, the
ARM dialect — `Azure-AsyncOperation`, body `provisioningState`, the final-GET-after-location rule —
was **deliberately not included**. `azure-core` ships only the generic
`OperationResourcePolling` / `LocationPolling` / `StatusCheckPolling` chain. ARM's variants live in
`azure-mgmt-core`, which subclasses `LROBasePolling` and supplies its own ordered algorithm list.

🪤 **New ARM-only LRO behavior belongs in `azure-mgmt-core/azure/mgmt/core/polling/arm_polling.py`, not
`base_polling.py`.** Changes to `base_polling.py` affect every non-ARM data-plane service.

### Polling strategy selection is first-match, so the catch-all must stay last

**Source:** [`polling/base_polling.py`](./azure/core/polling/base_polling.py)

`initialize()` walks the algorithm list in order calling `can_poll()` and stops at the first `True`.
`StatusCheckPolling.can_poll()` returns `True` unconditionally — it is the catch-all.
`OperationResourcePolling` is ordered before `LocationPolling` because the operation-location header
carries richer status than a bare `Location` header.

🪤 Ordering *is* the algorithm. A custom `LongRunningOperation` with an unconditional `can_poll()`
placed anywhere but last silently swallows every operation.

### `final-state-via` went into an options dict to avoid breaking generator contracts

**2022-02 · [#22713](https://github.com/Azure/azure-sdk-for-python/pull/22713)**

OpenAPI's `x-ms-long-running-operation-options.final-state-via` tells the poller where the final
resource body comes from. Rather than add a parameter to the `OperationResourcePolling` constructor —
a signature shared by multiple code generators, so a breaking change requiring cross-repo
coordination — it was threaded through the pre-existing `lro_options` dict.

This is constraint #2 from the top of this file in action, and it is the standard pattern here: **new
LRO knobs go into `lro_options`, not into signatures.**

### The poller no longer sleeps before its first status check

**2022-09 · [#26376](https://github.com/Azure/azure-sdk-for-python/pull/26376); terminal-status shortcut 2023-07 · [#31019](https://github.com/Azure/azure-sdk-for-python/pull/31019)**

The original loop was `while not finished(): delay(); update_status()`, so even an already-complete
operation waited a full interval (default 30s) before its first check. #26376 hoisted an immediate
`update_status()` ahead of the loop.

#31019 went further: if the initial response used the operation-location strategy *and* its body
already contains a terminal status, no poll request is issued at all. The status parse is wrapped in a
deliberately broad `except` because the body may not even be JSON.

🪤 This only applies to `OperationResourcePolling`. `LocationPolling` keys off the HTTP status code of
subsequent responses and does not read the initial body.

### Relative polling URLs must be resolved against the original parameterized endpoint

**2020-10 · [#14097](https://github.com/Azure/azure-sdk-for-python/pull/14097)**

ARM can return a relative polling URL. If the client endpoint is parameterized (a sovereign cloud such
as `management.chinacloudapi.cn`), treating that relative URL as absolute polls the wrong host — and
does so silently, either succeeding against the wrong endpoint or failing with an opaque DNS error.
`path_format_arguments` must be threaded into the polling method.

### Exception 2.0 split OData parsing out of `HttpResponseError`

**2020-02 · [#9738](https://github.com/Azure/azure-sdk-for-python/pull/9738)**

`ODataV4Format` became a standalone representation of an OData v4 error body, and `ODataV4Error` a
subclass of `HttpResponseError`. `HttpResponseError` itself attempts OData parsing and sets
`self.error` to an `ODataV4Format` or `None`. The split was necessary because generated code must
raise `HttpResponseError` for *all* HTTP failures, but only some Azure services return OData bodies.

🪤 Do not assign `self.error` before calling `super().__init__()` in a subclass — the base
`__init__` rescues a pre-set `error` attribute for backcompat with old AutoRest output, and you will
get surprising behavior.

### `error_map` exists because error types are declared per-operation, not globally

**2020-03 · [#10456](https://github.com/Azure/azure-sdk-for-python/pull/10456)**

OpenAPI specs declare which exception corresponds to which status code *per operation*. `map_error()`
takes a `{status_code: exception_class}` dict; `ErrorMap` adds a `default_error` fallback.

🪤 **`map_error` raises or returns silently — it never returns a value to check.** If the status code
is absent from the map and there is no default, it does nothing at all. Call sites must follow it with
an explicit `raise HttpResponseError(response=response)` for the fall-through case, which is exactly
what generated code does.

### `SerializationError` and `DeserializationError` are `ValueError`, not `AzureError`

**2022-05 · [#24113](https://github.com/Azure/azure-sdk-for-python/pull/24113), [#24312](https://github.com/Azure/azure-sdk-for-python/pull/24312)**

Verified in [`exceptions.py`](./azure/core/exceptions.py):

```python
class SerializationError(ValueError): ...
class DeserializationError(ValueError): ...
```

This is intentional. They represent **client-side data errors**, not service failures. They are not
retriable and carry no HTTP response, so inheriting `AzureError` — the marker for
service/transport errors — would be semantically wrong and would make them accidentally retriable.

🪤 **`except AzureError` does not catch them.** Broad azure-core error handling needs two branches.

### Error bodies, `__str__`, and one instructive revert

**2021-12 · [#21800](https://github.com/Azure/azure-sdk-for-python/pull/21800); 2021-12 revert · [#22023](https://github.com/Azure/azure-sdk-for-python/pull/22023); 2022-01 · [#22302](https://github.com/Azure/azure-sdk-for-python/pull/22302)**

Non-OData JSON error bodies were invisible in `str(error)`, which made some services nearly
undebuggable. The first attempt to dump the raw body into `__str__` was reverted within days because
OData errors then printed twice — once via the OData formatting path and once via the raw body path.
The final design includes the raw body **only when OData parsing produced nothing**.

Related: [#31662](https://github.com/Azure/azure-sdk-for-python/pull/31662) (2023-08) forced
`AzureError.message` to never be `None`, and
[#31718](https://github.com/Azure/azure-sdk-for-python/pull/31718) fixed recursion in the
`ODataV4Error → HttpResponseError → AzureError` `__str__` chain.

🪤 Be extremely careful adding `__str__` behavior to this hierarchy. It has produced both duplicate
output and infinite recursion before.

### `AzureError.continuation_token` lets you resume a failed paging or polling operation

**2020-10 · [#14578](https://github.com/Azure/azure-sdk-for-python/pull/14578)**

> "a first draft of supporting an optional continuation token attribute on the base AzureError to
> allow for catching exceptions in operations like paging and LRO so users are able to extract the
> info needed to continue later."

`PageIterator.__next__` catches `AzureError` and, if the error has no token of its own, attaches the
iterator's current `continuation_token` before re-raising.

🪤 It is only set when the error's own token was `None`, and it may legitimately still be `None`.
Always check before using it to resume.

---

## 2021 — The `azure.core.rest` rewrite

This is the single most confusing area of azure-core: **there are two parallel request/response type
hierarchies.** Understanding why is essential before touching anything in `rest/` or
`pipeline/transport/`.

### Why a second hierarchy exists at all

**2021-06 · [#19502](https://github.com/Azure/azure-sdk-for-python/pull/19502)** (provisional)

`azure.core.pipeline.transport.HttpRequest` was never designed as a public type. It is internal
plumbing: mutable, transport-flavored, with body semantics inherited from `requests` conventions.

When code generators began emitting **protocol methods** — the `client.send_request(request)` escape
hatch where users hand-craft an HTTP request — that internal type suddenly became a user-facing API,
and it was a bad one. `azure.core.rest.HttpRequest` was built as the clean public equivalent:
keyword-only `params` / `headers` / `json` / `data` / `content` / `files`, no transport leakage.

The old types were **not deleted and not deprecated** — they remain the internal pipeline
representation. This is constraint #1 in action.

🪤 As of today there is still **no `DeprecationWarning`** on
`azure.core.pipeline.transport.HttpRequest`. Its "legacy" status is documented in guides only. Do not
assume code using it is broken.

### The backcompat mixins are the glue holding both worlds together

**2021-09 · [#20599](https://github.com/Azure/azure-sdk-for-python/pull/20599) (requests), [#20827](https://github.com/Azure/azure-sdk-for-python/pull/20827) (responses); maintained 2025-07 · [#41850](https://github.com/Azure/azure-sdk-for-python/pull/41850), 2025-12 · [#44084](https://github.com/Azure/azure-sdk-for-python/pull/44084)**

Years of generated code and hand-written SDKs used the old attribute names: `request.body`,
`request.query`, `response.body()`, `response.internal_response`. The new `rest` types use different
names. Rather than force a coordinated flag-day migration across every SDK, `HttpRequestBackcompatMixin`
and `HttpResponseBackcompatMixin` were mixed into the **new** `rest` types, intercepting attribute
access to remap old names onto new storage. The new objects quack like the old ones.

🪤 **This mixin's attribute list is a permanent public API contract.** Removing an entry is a silent
breaking change for any consumer still using the old name. Also, the mixin pads backcompat names with
a leading underscore — so adding a new public attribute named `body`, `data`, `files`, or `query` to
`rest.HttpRequest` will be silently shadowed. Read the mixin before adding attributes.

### Provisional status was used to make real breaking changes before GA

**`text` property → method 2021-08 · [#20290](https://github.com/Azure/azure-sdk-for-python/pull/20290); `iter_text`/`iter_lines` removed 2021-08 · [#20460](https://github.com/Azure/azure-sdk-for-python/pull/20460); responses → ABCs 2021-09 · [#20448](https://github.com/Azure/azure-sdk-for-python/pull/20448); headers unified 2021-08 · [#20234](https://github.com/Azure/azure-sdk-for-python/pull/20234)**

The provisional window was used deliberately and aggressively:

- **`text` became a method** so it could accept an `encoding` override — impossible for a property.
- **`iter_text` / `iter_lines` were removed** as GA scope reduction; correct streaming text iteration
  across four transports wasn't worth the cost. They were never added back.
- **Responses became ABCs** so only transport-specific subclasses are ever instantiated; the concrete
  implementation lives in `_http_response_impl.py`.
- **Header behavior was unified** across transports for `rest` responses only. The author noted they
  deliberately did *not* fix the legacy responses, being unsure whether that counted as breaking.

🪤 `response.text` without parentheses returns a bound method, which is truthy — a silent bug, not an
`AttributeError`.

🪤 **Legacy and `rest` responses have deliberately different header semantics.** Do not "fix" this
inconsistency; it was a conscious decision.

**GA landed in 1.20.0 (2021-11-04)**, per CHANGELOG, alongside `send_request` on `PipelineClient`.

### LRO had to bridge both worlds, via a private kwarg

**2021-08 · [#20483](https://github.com/Azure/azure-sdk-for-python/pull/20483)**

Polling needs the internal `PipelineResponse` (for pipeline context), not the public
`rest.HttpResponse` that `send_request` returns. The bridge is a private, undocumented kwarg:
`send_request(..., _return_pipeline_response=True)`, which changes the return type at runtime in a way
type checkers cannot follow.

`base_polling.py` also contains dual-path body access, because generated SDKs migrated incrementally
and both response shapes still flow through it.

🪤 In polling code, read bodies through the shared helper, never via `response.body()` (legacy) or
`response.content` (rest) directly — you will break one of the two transports.

### Lazy transport imports via PEP 562, and the `__bases__` bug

**2022-08 · [#25344](https://github.com/Azure/azure-sdk-for-python/pull/25344); 2022-01 · [#22470](https://github.com/Azure/azure-sdk-for-python/pull/22470)**

`requests` and `aiohttp` are optional. Importing `azure.core.pipeline.transport` eagerly would fail for
anyone missing either. The module therefore uses PEP 562 module-level `__getattr__` so concrete
transports import only on attribute access.

The first implementation returned the attribute *name* as a fallback instead of raising. So
`azure.core.pipeline.transport.__bases__` returned the string `"__bases__"`, which broke documentation
tooling that introspects `__bases__`. #22470 fixed it to raise `AttributeError` per the PEP 562
contract.

🪤 `ImportError` for a missing transport is **deferred to attribute access**, not raised at module
import. A `try/except ImportError` around the import statement will not catch it.

### `aiohttp` and `requests` were pried loose over several years

**2019-07 · [#6496](https://github.com/Azure/azure-sdk-for-python/pull/6496) · 2021-01 · [#15878](https://github.com/Azure/azure-sdk-for-python/pull/15878) · 2021-07 · [#19808](https://github.com/Azure/azure-sdk-for-python/pull/19808) · 2021-08 · [#19930](https://github.com/Azure/azure-sdk-for-python/pull/19930) · 2022-10 · [#26405](https://github.com/Azure/azure-sdk-for-python/pull/26405)**

A long campaign toward constraint #4. Highlights: `aiohttp` became lazily loaded via `getattr`;
`AioHttpTransport` was found to be importing `requests` for `PreparedRequest` and was cut loose;
`requests` stopped being a hard dependency of azure-core in 2021-08; and `aiohttp` became the
`azure-core[aio]` extra.

🪤 **Never `import requests` at module scope anywhere in azure-core except `_requests_basic.py`.**
Policy code runs on all transports.

### Charset detection: a five-year saga ending in a hot-path fix

**2021-08 · [#19962](https://github.com/Azure/azure-sdk-for-python/pull/19962) · 2021-11 · [#21520](https://github.com/Azure/azure-sdk-for-python/pull/21520), [#21521](https://github.com/Azure/azure-sdk-for-python/pull/21521) · 2025-09 · [#43092](https://github.com/Azure/azure-sdk-for-python/pull/43092)**

`chardet` was removed from `rest`, then partially re-pinned when `aiohttp` dropped it transitively and
broke callers, then `charset_normalizer` was added as an alternative. In 2025 an external contributor
found the library-detection code sitting in the hot path of `text()`, re-scanning `sys.modules` on
every single response, and hoisted it out.

🪤 Charset detection is best-effort and depends on which optional library is installed. `azure-core`
no longer guesses aggressively — pass an explicit `encoding` when it matters.

---

## 2021–2022 — Shared utility types and the dependency diet

### `CloudEvent` lives in azure-core because it is a CNCF standard, not an Azure one

**2021-03 · [#16800](https://github.com/Azure/azure-sdk-for-python/pull/16800); precision fixes [#19019](https://github.com/Azure/azure-sdk-for-python/pull/19019), [#19259](https://github.com/Azure/azure-sdk-for-python/pull/19259); docs [#25992](https://github.com/Azure/azure-sdk-for-python/pull/25992)**

CloudEvents 1.0 is a CNCF spec used by Event Grid, Service Bus, and Event Hubs. Placing it in
`azure-eventgrid` would have forced every other service SDK to depend on Event Grid. So it went into
`azure.core.messaging`.

Two follow-up fixes were needed because `datetime.fromisoformat()` handles at most 6 fractional
digits and services emit more.

### `CaseInsensitiveEnumMeta` exists because services return inconsistent casing

**2021-02 · [#16316](https://github.com/Azure/azure-sdk-for-python/pull/16316)**

Azure services sometimes return an enum value whose casing does not match the spec (`"succeeded"` vs
`"Succeeded"`). Standard `Enum` lookup is case-sensitive and would raise. The metaclass uppercases the
key in `__getitem__`/`__getattr__`.

🪤 Because lookup normalizes via `.upper()`, **members must be declared in uppercase** or
case-insensitive access will never find them.

### azure-core has its own `CaseInsensitiveDict` rather than reusing `requests`'

**2022-03 · [#23206](https://github.com/Azure/azure-sdk-for-python/pull/23206); implementation 2022-07 · [#25074](https://github.com/Azure/azure-sdk-for-python/pull/25074); typing 2022-08 · [#25537](https://github.com/Azure/azure-sdk-for-python/pull/25537)**

`requests.structures.CaseInsensitiveDict` exists but is an undocumented internal of a library
azure-core had just spent years removing as a hard dependency. Owning the type lets `azure.core.utils`
expose it publicly with no transport coupling.

### `parse_connection_string` centralized a pattern every SDK had reimplemented

**2021-03 · [#17640](https://github.com/Azure/azure-sdk-for-python/pull/17640)**

`Endpoint=...;SharedAccessKey=...` is an Azure-wide convention, and Event Hubs, Service Bus, Storage,
and IoT Hub each had their own parser with subtly different validation. This was split out of a larger
PR specifically to land the shared parser first.

### The `cgi` module was removed proactively, before Python removed it

**2022-12 · [#28099](https://github.com/Azure/azure-sdk-for-python/pull/28099)**

`cgi.parse_header()` was used for `Content-Type` parsing. `cgi` was deprecated in 3.11 and removed in
3.13. Because there is no stdlib replacement, azure-core now carries a hand-rolled parser.

🪤 Don't reach for `cgi.parse_header` in transport code — it no longer exists on supported Pythons.
Same story for `pkg_resources`, removed in
[#41701](https://github.com/Azure/azure-sdk-for-python/pull/41701) (2025-06) in favor of
`importlib.metadata`.

### `six` survived until October 2025 — and the reason is instructive

**2025-10 · [#39962](https://github.com/Azure/azure-sdk-for-python/pull/39962)**

azure-core's own code stopped using `six` years earlier, but it stayed in `install_requires` because
downstream SDKs were relying on it being transitively available without declaring it themselves.
Multiple earlier removal attempts were approved and then not merged over coordination concerns. The
maintainer comment on the final PR:
> "we are working on making sure a few libraries which still import six (but shouldn't need to) are
> not impacted by this change."

This is the clearest illustration of constraint #1 in the repository: **azure-core's dependency list is
part of its public API**, because things depend on what it drags in.

### `anyio` is the exception that proves the dependency rule

**2023-11 · [#33307](https://github.com/Azure/azure-sdk-for-python/pull/33307); lock logic 2024-01 · [#33282](https://github.com/Azure/azure-sdk-for-python/pull/33282); original deadlock 2020-06 · [#11591](https://github.com/Azure/azure-sdk-for-python/pull/11591)**

The async auth policy needs a lock so concurrent coroutines don't stampede token refresh. The history:

1. #11591 — the original `threading.Lock` **deadlocked the event loop**. It is not re-entrant, so when
   coroutine A held it and awaited, coroutine B's blocking `acquire()` froze the whole thread,
   preventing A from ever resuming.
2. Switching to `asyncio.Lock` fixed asyncio but broke trio, which azure-core also supports.
3. #33307 added `anyio` for a backend-agnostic lock.

A community reviewer objected immediately that this "forces installation of multiple additional
transitive dependencies for any and all users of azure-core," including purely synchronous ones. The
team accepted the cost.

🪤 `anyio` and `sniffio` are now unavoidable transitive dependencies of every Azure SDK for Python
install. Given constraint #3, expect any *new* dependency proposal to face this same scrutiny.

---

## 2023 — Type completeness and security hardening

### The "type complete" campaign, and why the generics are so painful

**2023-02 to 2023-09 · [#28538](https://github.com/Azure/azure-sdk-for-python/pull/28538), [#31056](https://github.com/Azure/azure-sdk-for-python/pull/31056), [#31422](https://github.com/Azure/azure-sdk-for-python/pull/31422), [#31494](https://github.com/Azure/azure-sdk-for-python/pull/31494), [#31502](https://github.com/Azure/azure-sdk-for-python/pull/31502), [#31766](https://github.com/Azure/azure-sdk-for-python/pull/31766); `py.typed` groundwork 2020-01 · [#9577](https://github.com/Azure/azure-sdk-for-python/pull/9577)**

`py.typed` was added in 2020, which told type checkers "trust our annotations" — years before those
annotations were actually complete. The 2023 campaign paid that debt down, because an incomplete
azure-core surface degrades type checking in *every* downstream SDK.

The hardest part was `Pipeline` itself. From #28538:
> "It's why there is generic everywhere, and typing allows us to confirm we're not biased against a
> particular HTTP implementation."

That is constraint #4 expressed as types: `Pipeline`, `PipelineClient`, and every policy carry both
`HTTPRequestType` and `HTTPResponseType`.

A rename to `HTTPResponseType_co` was reverted in
[#31356](https://github.com/Azure/azure-sdk-for-python/pull/31356) once it was recognized as a
breaking API change — even a TypeVar name is public surface here.

🪤 When subclassing a policy or annotating a custom one, bind **both** TypeVars. Leaving them unbound
produces `Unknown` types that silently suppress errors downstream.

### Circular imports are a permanent structural hazard

**2020-04 · [#10799](https://github.com/Azure/azure-sdk-for-python/pull/10799); recurred 2024-12 · [#38776](https://github.com/Azure/azure-sdk-for-python/pull/38776)**

`pipeline → policies → credentials → pipeline` is a real cycle. Tooling that force-sets
`TYPE_CHECKING = True` to resolve annotations turns latent cycles into hard failures. The recurrence
four years later shows this isn't solved, just managed.

🪤 Any new cross-module type-only import in `azure.core` belongs under `if TYPE_CHECKING:`. A string
forward reference alone is not sufficient if the module is also imported at runtime elsewhere in the
cycle.

### `SensitiveHeaderCleanupPolicy` strips credentials on cross-domain redirects

**2023-06 · [#28349](https://github.com/Azure/azure-sdk-for-python/pull/28349); persistence bug fixed 2026-03 · [#45518](https://github.com/Azure/azure-sdk-for-python/pull/45518)**

If a redirect crosses to a different domain, `Authorization` and `x-ms-authorization-auxiliary` must be
stripped before following it — otherwise the bearer token is handed to a third-party host. This is the
same vulnerability class that has hit HTTP clients across every language.

The coordination is a flag, not a header. `RedirectPolicy` sets it and `SensitiveHeaderCleanupPolicy`
reads it:

```python
# _redirect.py
request.context["insecure_domain_change"] = True

# _sensitive_header_cleanup_policy.py
insecure_domain_change = request.context.get("insecure_domain_change", False)
```

#45518 fixed the same class of bug described in the `enforce_https` entry: the flag was originally on
`request.context.options`, which is consumed per attempt, so it evaporated on the next one.

🪤 Two traps. First, **this policy is inert without a redirect policy setting the flag** — a custom
pipeline that follows redirects some other way gets no protection. Second, if you write a custom
redirect policy, you must set `request.context["insecure_domain_change"]` yourself.

### `format_url` does not URL-encode, by explicit decision

**2023-08 · [#31375](https://github.com/Azure/azure-sdk-for-python/pull/31375) then reverted by [#31721](https://github.com/Azure/azure-sdk-for-python/pull/31721)**

An attempt to handle URL-encoding of `path_format_arguments` inside azure-core was reverted two days
later:
> "After some discussions, we decided to put the url-encoding job into autorest/SDK developer rather
> than handling it in azure-core."

This is a deliberate layer boundary: **encoding is the generator's job, not core's.**

🪤 Then three consecutive releases in 2026 fixed trailing-slash handling:
[#45044](https://github.com/Azure/azure-sdk-for-python/pull/45044) (1.38.1) added an unconditional
`rstrip("/")`, [#45218](https://github.com/Azure/azure-sdk-for-python/pull/45218) (1.38.2) walked it
back after it broke Storage Tables, and
[#45366](https://github.com/Azure/azure-sdk-for-python/pull/45366) (1.38.3) fixed the query-string-only
template case. `format_url` has an unusually high regression rate; the Storage URL patterns
(`?restype=...` templates, meaningful trailing slashes) are the usual casualty. **Add a test for the
Storage-shaped cases with any change here.**

---

## 2023–2025 — Auth modernization

### `AccessToken` is a `NamedTuple`, which froze its schema

**2019-06 · [#5872](https://github.com/Azure/azure-sdk-for-python/pull/5872)**

Making `AccessToken` a `NamedTuple` was great for adoption — both `token.token` and
`token, expires_on = get_token(...)` work. But a `NamedTuple`'s field set is structurally frozen, and
that decision constrained the next five years of credential design.

### `get_token(**kwargs)` was an intentional extensibility hedge that later backfired

**2019-09 · [#6964](https://github.com/Azure/azure-sdk-for-python/pull/6964)**

The open `**kwargs` signature let `claims`, `tenant_id`, and `enable_cae` all be added later without
changing the `TokenCredential` protocol. But it also means **the protocol cannot tell you which
kwargs a given credential actually accepts** — which is exactly what broke during the CAE rollout.

🪤 A custom `TokenCredential.get_token` **must** accept `**kwargs` and ignore unknown ones.

### CAE: enabled, immediately walked back, then enabled again six years later

**2023-07 · [#31012](https://github.com/Azure/azure-sdk-for-python/pull/31012) → 2023-08 walk-back · [#31546](https://github.com/Azure/azure-sdk-for-python/pull/31546) → 2025-09 default on · [#42941](https://github.com/Azure/azure-sdk-for-python/pull/42941)**

Continuous Access Evaluation lets Entra ID revoke tokens mid-lifetime; the client signals support by
advertising the `cp1` capability. #31012 wired it up but defaulted it off. Two weeks later #31546
stopped passing the kwarg entirely unless explicitly requested, because the Azure CLI's credential did
not accept `**kwargs` and raised `TypeError`:
> "Changed to not pass in `enable_cae` unless it is explicitly on to make some time for cli to fix the
> code."

Only in 2025, after the ecosystem caught up, did #42941 flip the default to `True` to match .NET, Java,
JS, and Go.

🪤 This is the canonical case study for constraint #2 in this repo: **a purely additive kwarg took two
years to enable by default because one downstream credential didn't accept `**kwargs`.**

### `AccessTokenInfo` / `SupportsTokenInfo` were added *alongside* the old protocol, not instead of it

**2024-07 · [#36183](https://github.com/Azure/azure-sdk-for-python/pull/36183); 2024-09 · [#36565](https://github.com/Azure/azure-sdk-for-python/pull/36565); docs 2025-03 · [#39931](https://github.com/Azure/azure-sdk-for-python/pull/39931)**

Adding `refresh_on` to the frozen `AccessToken` tuple (#36183) was a workaround that clearly could not
scale to a third or fourth field. #36565 introduced a parallel design:

- `AccessTokenInfo` — a regular class, extensible.
- `SupportsTokenInfo.get_token_info(options: TokenRequestOptions)` — a `TypedDict` options bag instead
  of open `**kwargs`, so the accepted parameters are actually *discoverable*.

The auth policy dispatches on capability: use `get_token_info` if present, else fall back to
`get_token`. The old protocol was left untouched.

🪤 There are now **two token protocols and two token classes, both fully supported**. New credentials
should implement `SupportsTokenInfo`, but cannot drop `get_token`. See
[CLIENT_LIBRARY_DEVELOPER.md](./CLIENT_LIBRARY_DEVELOPER.md#token-credential-protocols), which
correctly labels these "preferred" and "legacy."

### Auth challenges are an overridable hook, not a separate policy

**2021-05 · [#18437](https://github.com/Azure/azure-sdk-for-python/pull/18437); default impl 2024-10 · [#37652](https://github.com/Azure/azure-sdk-for-python/pull/37652); 2025-07 · [#41857](https://github.com/Azure/azure-sdk-for-python/pull/41857); 2025-09 · [#42536](https://github.com/Azure/azure-sdk-for-python/pull/42536), [#42920](https://github.com/Azure/azure-sdk-for-python/pull/42920)**

Rather than a separate `ChallengeAuthenticationPolicy`, `BearerTokenCredentialPolicy` grew an
`on_challenge()` hook that returns `False` by default. Key Vault and others subclass and override it to
parse `WWW-Authenticate` and re-authorize with service-specific claims.

Two late fixes are worth knowing: #42536 stopped a claims-token failure from **swallowing the original
401 entirely** (leaving users with no diagnostics at all), and #42920 handles reading the error body
when the response is streamed.

🪤 In an `on_challenge` override, re-authorize through the policy's public authorization path so token
caching is preserved — bypassing it causes redundant token fetches in subclassing policies (#41857).

### Token refresh is jittered to avoid a thundering herd

**2026-03 · [#43720](https://github.com/Azure/azure-sdk-for-python/pull/43720)**

Fleet-wide simultaneous deploys produce fleet-wide simultaneous token expiry, and therefore a
synchronized stampede against Entra ID. Randomized jitter is applied to the refresh window.

🪤 Token refresh timing is now intentionally non-deterministic. Tests that assert exact refresh moments
will be flaky.

### `WWW-Authenticate` is deliberately *not* redacted

**2022-02 · [#22990](https://github.com/Azure/azure-sdk-for-python/pull/22990); more headers 2024-09 · [#37528](https://github.com/Azure/azure-sdk-for-python/pull/37528)**

It is a *response* header containing the server's challenge parameters — not a client credential. It
is on the logging allowlist because without it, diagnosing 401s and CAE claims challenges is close to
impossible.

### The cloud-selection environment variable was renamed for namespace safety

**2024-08 · [#30825](https://github.com/Azure/azure-sdk-for-python/pull/30825); renamed 2026-03 · [#45763](https://github.com/Azure/azure-sdk-for-python/pull/45763)**

The original `AZURE_CLOUD` was too generic and risked colliding with variables set by unrelated Azure
tooling in the same environment. It is now `AZURE_SDK_CLOUD_CONF`, confirmed in
[`settings.py`](./azure/core/settings.py) and
[ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md).

Relatedly, [#46668](https://github.com/Azure/azure-sdk-for-python/pull/46668) (2026-05) made invalid
values for SDK environment variables **warn and fall back** rather than raise, on the principle that a
misconfigured diagnostic setting should never crash a user's application.

🪤 That principle has a cost: a typo in `AZURE_SDK_TRACING_IMPLEMENTATION` now silently disables
tracing instead of telling you. If tracing correctness matters, assert it in your test harness.

---

## 2024–2025 — Native OpenTelemetry

### Why there are two tracing implementations

**Plugin extraction 2019-10 · [#7592](https://github.com/Azure/azure-sdk-for-python/pull/7592); OTel preferred 2024-07 · [#35050](https://github.com/Azure/azure-sdk-for-python/pull/35050); native path 2025-03 · [#39563](https://github.com/Azure/azure-sdk-for-python/pull/39563), [#39959](https://github.com/Azure/azure-sdk-for-python/pull/39959), [#40024](https://github.com/Azure/azure-sdk-for-python/pull/40024)**

The original OpenCensus implementation lived inside azure-core. #7592 extracted it —
> "Extract opencensus implementation as an external package"

— so azure-core would carry **zero mandatory tracing dependencies**. Discovery was deliberately *not*
entry-point based: the user sets `settings.tracing_implementation` or
`AZURE_SDK_TRACING_IMPLEMENTATION`. Installing a plugin package alone did nothing.

By 2025, OpenTelemetry had clearly won, and the abstraction was pure overhead. The native path
(`azure.core.tracing.opentelemetry.OpenTelemetryTracer`, reached via
`azure.core.instrumentation.get_tracer()`) works directly with OTel spans, **does not implement
`AbstractSpan`**, and auto-detects `opentelemetry-api` rather than requiring explicit configuration.

So today:

| | Legacy plugin path | Native path |
|---|---|---|
| Interface | `AbstractSpan` protocol | OTel `Span` directly |
| Lives in | `azure-core-tracing-opentelemetry` | `azure-core` itself |
| Activation | Explicit `settings.tracing_implementation` | Auto-detected when `tracing_implementation` is unset |
| Entry point | `settings.tracing_implementation` | `azure.core.instrumentation.get_tracer()` |

🪤 **These two interfaces are not interchangeable and emit subtly different span attributes.** New SDK
libraries should use `azure.core.instrumentation.get_tracer()`. Do not implement `AbstractSpan` in new
code.

🪤 The default-check order was flipped, then flipped back, then flipped again:
[#29095](https://github.com/Azure/azure-sdk-for-python/pull/29095) put OTel first,
[#29770](https://github.com/Azure/azure-sdk-for-python/pull/29770) reverted it because "the Opencensus
plugin should be checked for first since that was the previous default behavior," and #35050 finally
made OTel preferred once OpenCensus was sunset
([#37975](https://github.com/Azure/azure-sdk-for-python/pull/37975) deprecated it;
[#39453](https://github.com/Azure/azure-sdk-for-python/pull/39453) removed the dev dependencies). If
you change detection order, expect it to be user-visible.

### `traceparent` must be injected from inside the HTTP span's context

**2025-03 · [#40074](https://github.com/Azure/azure-sdk-for-python/pull/40074)**

The header was being generated against the parent operation span rather than the HTTP child span,
producing traces that didn't stitch together correctly at the service boundary. Context activation
must happen *before* injection.

### `get_tracer()` is `lru_cache`d

**2025-10 · [#43338](https://github.com/Azure/azure-sdk-for-python/pull/43338); related [#43092](https://github.com/Azure/azure-sdk-for-python/pull/43092)**

Tracer resolution was re-running import detection on every span. Both this and the charset fix are the
same lesson: **azure-core code runs once per HTTP request across the entire Azure Python ecosystem, so
per-call import probing is a real cost.**

🪤 The cache returns the same tracer instance for identical arguments. If a test replaces the global
OTel tracer provider, cached tracers keep the old one — clear the cache in test teardown.

### Query parameters were leaking into trace spans until 2026

**2026-04 · [#46482](https://github.com/Azure/azure-sdk-for-python/pull/46482)**

`HttpLoggingPolicy` had sanitized URLs in logs for years, but `DistributedTracingPolicy` was recording
full URLs — including SAS tokens and subscription keys — into span attributes shipped to Jaeger,
Grafana, and friends. Sanitization is now shared between both policies.

🪤 This is user-visible: span URL attributes are redacted by default now. Dashboards that relied on
full URLs need `additional_allowed_query_params`.

---

## 2025–2026 — Serialization extensibility and safer tokens

### azure-core knows about generated models on purpose

**2025-06 · [#41445](https://github.com/Azure/azure-sdk-for-python/pull/41445), [#41466](https://github.com/Azure/azure-sdk-for-python/pull/41466), [#41517](https://github.com/Azure/azure-sdk-for-python/pull/41517), [#41571](https://github.com/Azure/azure-sdk-for-python/pull/41571)**

Two generations of generated models coexist: legacy `msrest`-style models carrying `_attribute_map`,
and newer TypeSpec/DPG models. Rather than duplicate the branching logic in every generated SDK,
`is_generated_model` (also exported as `is_sdk_model`), `as_attribute_dict`, and `attribute_list`
centralize it in `azure.core.serialization`.

🪤 Detection is duck-typed on model-shaped attributes. A hand-written class that happens to define
`_attribute_map` will be treated as an SDK model by serialization paths. Don't name internal dicts
that.

### `TypeHandlerRegistry` opens serialization to third-party types

**2025-10 · [#43051](https://github.com/Azure/azure-sdk-for-python/pull/43051), [#43393](https://github.com/Azure/azure-sdk-for-python/pull/43393)**

Generated serialization was closed: there was no way to teach it about a `pydantic.BaseModel` or a
numpy array without patching generated code. The registry adds decorator-based registration supporting
both exact-type and predicate dispatch, with per-type caching so the predicate list is walked once.

The intended consumer is **SDK library authors**, registering handlers for third-party types their
service commonly accepts — not end users.

🪤 It is a module-level singleton. A test that registers a handler without tearing it down leaks into
every subsequent test in the process.

### Continuation tokens moved off pickle for security

**Introduced with pickle 2020-05 · [#10801](https://github.com/Azure/azure-sdk-for-python/pull/10801); replaced 2026-01 · [#44574](https://github.com/Azure/azure-sdk-for-python/pull/44574)**

The original `get_continuation_token()` base64-encoded a `pickle.dumps()` of the initial
`PipelineResponse`. Pickle was chosen because the whole response object, including aiohttp internals,
had to round-trip — which is also why aiohttp responses had to be made picklable at all.

Pickle deserialization is an arbitrary-code-execution vector. Since a continuation token is a value
applications persist to databases and queues and later feed back in, this was a genuine security
liability. #44574 replaced it with a versioned JSON format carrying only the essential fields, and
added filtering that scrubs `Authorization`, `x-ms-encryption-key`, and similar headers before
serialization.

🪤 **Tokens are not compatible across this boundary.** A token minted by an older azure-core cannot be
resumed by a newer one; the decoder raises rather than unpickling untrusted bytes. Applications that
persist long-lived tokens must handle this at upgrade time.

### `_FixedOffset` removal shows why underscore-prefixed names still hurt to remove

**2026-05 · [#46603](https://github.com/Azure/azure-sdk-for-python/pull/46603)**

`_FixedOffset` predated a usable stdlib fixed-offset timezone. Removing it in favor of
`datetime.timezone` surfaced that at least one shipped SDK was importing this underscore-prefixed
private symbol directly.

🪤 **In azure-core, even private names have de-facto downstream consumers.** Before deleting one, grep
the wider repo. And never import `_`-prefixed names *from* azure-core into a service SDK.

---

## Recurring patterns worth internalizing

If you remember nothing else from this document:

1. **Nothing gets removed; things get superseded.** Old transport types, `AccessToken`,
   `TokenCredential`, and `AbstractSpan` are all "legacy" and all still fully supported. When you find
   two ways to do something, that is usually deliberate, not debt awaiting cleanup.

2. **New capabilities arrive through option bags, not signatures.** `lro_options`, `**kwargs`,
   `TokenRequestOptions`, `context.options`. This looks like weak API design; it is a direct response
   to code generators being downstream consumers.

3. **Flags that must survive retries go on `request.context`, never `context.options`.** This exact bug
   has been fixed at least twice — `enforce_https` (#9821/#45890) and `insecure_domain_change`
   (#45518). If you add coordination state between policies, put it in the right place.

4. **Policy order encodes behavior.** Auth after retry so tokens refresh. Sensitive-header cleanup
   after redirect so the flag exists. Reordering the defaults is a behavioral change, not a cosmetic
   one.

5. **Per-request work is multiplied across the entire ecosystem.** Import probing, charset detection,
   and tracer resolution were all found in hot paths and hoisted out. Don't put lookups inside
   per-request code.

6. **Check whether it belongs in `azure-mgmt-core` or `corehttp` instead.** ARM-specific polling
   belongs in `azure-mgmt-core`. And `sdk/core/corehttp` is a separate, still-beta,
   Azure-independent pipeline with its own transports — changes to shared concepts may need mirroring
   there, though the two intentionally diverge.

7. **When something looks like an obvious bug, check whether it was already fixed and reverted.**
   `format_url` encoding, error `__str__`, and OTel detection order were all reverted at least once.

---

## Contributing to this document

When you make a decision in `azure-core` whose rationale won't be obvious from the diff — a revert, a
workaround, a deliberate duplication, a constraint imposed by generated code — add an entry. Include
the merge date, the PR link, the reasoning (quote the PR discussion where it's illuminating), and a 🪤
note if there's a trap for the next person.
