# How a Cosmos operation flows through the v5 SDK — an overview


This document explains the shape of the v5
Azure Cosmos DB SDK from the outside — in particular, anyone looking at the
**binding layer** where Python meets the shared Rust driver — without needing
the internal, line-by-line detail.

It answers one question end to end: **when an application calls an operation on
a container, what does that call pass through on its way to the service and
back, and what is each of those layers actually for?** It deliberately stays at
the level of *responsibilities and boundaries*. 


## Contents

- [The one idea to take away](#the-one-idea-to-take-away)
- [The path a call takes](#the-path-a-call-takes)
- [What each layer is for](#what-each-layer-is-for)
  - [Layer 1 — The public surface](#layer-1--the-public-surface)
  - [Layer 2 — The per-call orchestrator](#layer-2--the-per-call-orchestrator)
  - [Layer 3 — Shared request preparation](#layer-3--shared-request-preparation)
  - [Layer 4 — The backend boundary](#layer-4--the-backend-boundary)
  - [Layer 5 — The binding and the Rust driver](#layer-5--the-binding-and-the-rust-driver)
  - [Layer 6 — Response handling](#layer-6--response-handling)
- [The binding layer in focus](#the-binding-layer-in-focus)
- [What the Rust driver owns](#what-the-rust-driver-owns)
- [Why the SDK is shaped this way](#why-the-sdk-is-shaped-this-way)
- [What this document intentionally leaves out](#what-this-document-intentionally-leaves-out)

## The one idea to take away

A call travels **top-down** through a fixed set of layers, each with exactly
one job, and the response comes **back up** the same layers. The single most
important structural fact is *where the language boundary sits*: everything
above the binding is Python that decides **what** request to make; everything
from the Rust driver down is shared, cross-language code that decides **how**
to talk to the service — signing, region selection, retries, session
consistency, and the network itself.

That split is the whole point of the design. The Python side is thin and
predictable; the hard, correctness-critical networking logic lives in one place
that every language SDK can share.

## The path a call takes

```
Application code
    │  calls an operation on a container
    ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ 1. Public surface        the container object the app calls       │
 │                          (same shape for sync and async)          │
 └──────────────────────────────────────────────────────────────────┘
    │   fills in the few things only the container knows, then hands
    │   the call to the orchestrator
    ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ 2. Per-call orchestrator drives one whole operation               │
 └──────────────────────────────────────────────────────────────────┘
    │   gathers what the request needs, asks Layer 3 to build it,
    │   hands it to the backend, then asks Layer 6 to parse the reply
    ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ 3. Shared request prep   one immutable description of the request │
 └──────────────────────────────────────────────────────────────────┘
    │   produces a single frozen record — exactly what will go on the
    │   wire — so nothing below can second-guess the request
    ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ 4. Backend boundary      "where the request is sent"              │
 └──────────────────────────────────────────────────────────────────┘
    │   selects the matching driver entry point and carries the
    │   request across the line from Python into Rust
    ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ 5a. Binding             Python ↔ Rust type translation            │
 │ 5b. Rust driver core    the shared, cross-language networking core │
 └──────────────────────────────────────────────────────────────────┘
    │   the binding only translates types; the driver actually talks
    │   to the service — signs, picks the region, retries, keeps the
    │   session token current, terminates TLS
    ▲
    │   (the response travels back up)
 ┌──────────────────────────────────────────────────────────────────┐
 │ 6. Response handling     a readable result, or a typed error      │
 └──────────────────────────────────────────────────────────────────┘
    │   turns the raw reply into the value the app gets back — either
    │   data it can read, or an exception it can catch
    ▼
Application code (return value, or error handler)
```

A subtle but important detail: this is **not** a relay where each layer hands
off and forgets the call. Layer 2, the orchestrator, stays in charge for the
whole operation. It *calls down* into Layers 3, 4, and 6 as helpers and gets
their answers back, rather than passing the request along and disappearing.
That is why correctness lives in a predictable place: one component owns the
lifetime of each call.

## What each layer is for

**A 5,000-foot view: where each layer lives.** Before the per-layer detail,
here is which part of the codebase implements each layer, so a reviewer can map
the concepts onto the source tree. The whole Python side ships in the
`azure-cosmos` package under `azure/cosmos/`; the shared driver lives in a
separate Rust codebase.

| Layer | Where it lives |
| --- | --- |
| **1. Public surface** | The top of `azure/cosmos/` — the container, client, and database modules for the synchronous surface, and the parallel `azure/cosmos/aio/` subpackage for the asynchronous one. |
| **2. Per-call orchestrator** | The `azure/cosmos/_helpers/` package — the item-helper and dispatch modules that drive one operation end to end (one helper variant for sync, one for async, sharing the logic beneath). |
| **3. Shared request preparation** | Also `azure/cosmos/_helpers/` — the option-building, request-freezing, partition-key/body encoding, and metadata/id-lookup modules. These are pure functions, which is what makes them testable without a live account. |
| **4. Backend boundary** | The `azure/cosmos/_backend/` package — the uniform "send this request" contract, the factory that picks a backend when the client is built, and the Rust-backed implementation. |
| **5a. Binding** | A PyO3 binding crate, **`azure_cosmos_rust`**, whose source sits beside the Python package (`azure-cosmos/azure_cosmos_rust/src/` — e.g. `wire.rs` for translating requests/responses to and from the driver's types, `credential.rs` for bridging Python credentials, `runtime.rs` for the async runtime, `lib.rs` for the module entry point). It compiles to the native `_rust` extension that ships inside `azure/cosmos/`; only the backend package is allowed to import it, which keeps the language boundary in one narrow place. |
| **5b. Rust driver core** | A shared, cross-language Rust driver — the **`azure_data_cosmos_driver`** crate — maintained in the separate Azure SDK for Rust repository. The binding crate statically links it **into the same native extension** — so what looks like one `_rust` module on disk actually contains both halves of Layer 5. |
| **6. Response handling** | Again `azure/cosmos/_helpers/` — the response-parsing and typed-exception modules; successful results are surfaced through the response types in `azure/cosmos/`. |

Two things are worth noticing from this table. First, **Layers 2, 3, and 6 all
live together in the `_helpers` package** — that is deliberate: they are the
Python-side "what request to make / what did we get back" logic, and keeping
them in one package is what lets sync and async share identical behavior.
Second, **the binding and the driver are a single compiled artifact** — the
`azure_cosmos_rust` binding crate statically links the `azure_data_cosmos_driver`
crate, so a reviewer will see one native module, but it is the seam (5a) and the
shared engine (5b) packaged together.

The rest of this section explains what each layer is *for*.

### Layer 1 — The public surface

**What it is:** the container object the application calls — the same methods,
with the same shape, whether the app uses the synchronous or the asynchronous
client.

**What it's for:** to accept the application's parameters and fill in the few
pieces that only the container itself knows — for example, how to address the
specific data the operation targets, and where the partition-key value comes
from. It does the smallest amount of work needed to turn "the app's request" into
"a fully specified request," then hands off.

**What would break without it:** applications would have to know
container-internal addressing details to make even a basic call, and the sync
and async surfaces would drift apart.

### Layer 2 — The per-call orchestrator

**What it is:** the component that drives a single operation from start to
finish. It is the hub of the whole flow.

**What it's for:** to gather the metadata a request needs, ask the lower layers
to build the request and send it, and then ask the response layer to interpret
the reply. It stays on the stack for the entire call and coordinates
everything.

**What would break without it:** the steps of a call would be scattered, and
there would be no single place that owns "what does *this one call* do from
beginning to end" — exactly the kind of fragmentation that lets sync and async
behavior diverge.

### Layer 3 — Shared request preparation

**What it is:** a set of pure, side-effect-free functions that fold everything
gathered so far into **one immutable record** describing the entire request.

**What it's for:** to produce a single, frozen description of *exactly* what
will go on the wire — the target, the headers, the options, the body. Because
the record is immutable and built in one place, nothing downstream can quietly
reinterpret or re-derive what the application asked for.

**What would break without it:** small inconsistencies — a header computed one
way here and another way there — could send a request to the wrong place or
change its meaning. Centralizing this into one frozen record is what makes the
request predictable and testable without a live account.

### Layer 4 — The backend boundary

**What it is:** a thin dispatch layer with a single, uniform contract: "send
this prepared request."

**What it's for:** to look at which operation is being performed, select the
matching entry point in the driver, and carry the prepared request across the
boundary from Python into the shared driver. It is the seam where a request
stops being "a Python object" and becomes "an operation for the driver to
execute."

**What would break without it:** every layer above would need to know about the
driver's internals, and swapping or sharing the underlying driver would ripple
through the whole stack. The uniform "send this request" contract keeps that
coupling in one narrow place.

### Layer 5 — The binding and the Rust driver

This is the language boundary, and it has two distinct halves that are easy to
conflate but do very different jobs.

**5a — The binding.** Its only job is **type translation**: converting the
Python-side request description into the types the Rust driver expects, and
converting the driver's response back into something Python can use. It contains
no networking logic and makes no decisions about how to talk to the service. It
is intentionally thin — the less it does, the fewer places behavior can differ
between languages.

**5b — The Rust driver core.** This is the shared, cross-language engine that
actually communicates with Cosmos DB. It owns the genuinely hard,
correctness-critical work: authenticating and signing each request, choosing
which region to talk to, retrying transient failures, keeping session-consistency
state current, and terminating TLS. Because it is shared, this logic is written
and hardened once and reused across language SDKs rather than reimplemented per
language.

**What would break without this split:** if type translation and networking
were tangled together, every language binding would risk subtly different retry,
routing, or consistency behavior — the precise class of bug that is hardest to
reproduce and most damaging in production.

### Layer 6 — Response handling

**What it is:** the layer that turns the driver's raw reply into the value the
application receives.

**What it's for:** to present one of two clean outcomes — a result the
application can read its data from, or a **typed error** its error handler can
catch and reason about. It hides the raw wire response behind a stable,
language-appropriate surface.

**What would break without it:** applications would have to interpret raw
protocol responses and status codes themselves, and error handling would be
inconsistent and brittle.

## The binding layer in focus


The binding is a **translator, not a decision-maker**. Everything that decides
*what* the request is has already happened above it, and is captured in the one
immutable request record. Everything that decides *how* to talk to the service
happens below it, inside the shared driver. The binding sits exactly on the
line and moves data across it: Python types in, driver types out on the way
down; driver results in, Python-friendly values out on the way back up.

Keeping the binding this thin is a deliberate correctness choice. The more
behavior a binding carries, the more opportunity there is for one language's
SDK to behave differently from another's. By pushing all real logic either up
(request shaping, in Python) or down (networking, in the shared driver), the
binding becomes a small, predictable, easily audited seam.

For a reader who wants to read that seam, it is the `azure_cosmos_rust` crate
(`azure-cosmos/azure_cosmos_rust/src/`). Its modules follow the translator role
directly: request/response type conversion (`wire.rs`), credential bridging so
the driver can obtain tokens through Python's credential objects
(`credential.rs`), the async runtime that drives calls (`runtime.rs`), and the
module entry point that exposes it to Python as `_rust` (`lib.rs`). None of these
contain retry, routing, or consistency logic — that all lives below, in the
driver.


## Why the SDK is shaped this way

Three goals explain the whole structure:

1. **One behavior for sync and async.** The two client styles share the same
   layers and the same request preparation, so they behave identically instead
   of drifting apart over time.
2. **Correctness by construction.** Folding a request into a single immutable
   description, in one place, removes the small inconsistencies that used to let
   a request go to the wrong partition or change meaning between code paths.
3. **Testable without a live service.** Because request preparation is pure and
   self-contained, the great majority of the SDK's behavior can be exercised on
   a developer's machine, without provisioning a real account.

The Python/Rust split serves all three: it keeps the language-specific surface
thin and predictable, and it moves the hard, shared networking logic into a
single engine that every language SDK can rely on.

