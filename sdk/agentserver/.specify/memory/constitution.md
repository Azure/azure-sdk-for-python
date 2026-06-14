# Azure AI AgentServer SDK Constitution

## Core Principles

### I. Modular Package Architecture

Every feature belongs to a clearly scoped package within the `sdk/agentserver` family. Packages are independently versioned, installable, and testable. The four packages form a layered architecture:

- **azure-ai-agentserver-core** (v2.x) — Foundation utilities, ASGI host framework, config, tracing, middleware.
- **azure-ai-agentserver-invocations** (v1.x) — Invocation protocol (execute, poll, cancel).
- **azure-ai-agentserver-responses** (v1.x) — Responses protocol (streaming SSE, storage, models).
- **azure-ai-agentserver-githubcopilot** (v1.x) — GitHub Copilot SDK adapter layer.

Dependencies flow downward only: `githubcopilot` → `responses` → `core`; `invocations` → `core`. No circular or lateral dependencies between protocol packages. Adding new cross-package dependencies requires justification and review.

### II. Strong Type Safety (NON-NEGOTIABLE)

All code must use precise, explicit type annotations. This is enforced by mypy (`disallow_untyped_defs: true`), pyright, and verifytypes.

- **Prefer concrete types over `Any` and `dict`**. Use dataclasses, `TypedDict`, `NamedTuple`, `Protocol`, or custom model classes instead of raw `dict[str, Any]`.
- **Use `collections.abc` for abstract types**: `Callable`, `Awaitable`, `AsyncIterator`, `AsyncIterable`, `Sequence`, `Mapping` — not their mutable concrete counterparts unless mutation is required.
- **Use `str | None` (PEP 604)** over `Optional[str]` in new code. Both are acceptable in existing code.
- **All public functions, methods, and class attributes** must have complete type annotations including return types (use `-> None` for void).
- **Use `Literal[...]`** for fixed string values (status codes, mode flags, event types).
- **Use `TYPE_CHECKING` guards** only for circular import resolution or expensive imports — not as a general pattern.
- **Include `py.typed`** (PEP 561) marker in every package.
- **Type ignore comments** must include specific error codes and a brief justification: `# type: ignore[assignment]  # reason`.
- **TypeVar naming**: Covariant suffixed `_co`, contravariant suffixed `_contra`.
- **Mark Protocols `@runtime_checkable`** when used for duck-typing checks.
- **PEP 484 inline style only**: Never use comment-style type hints (`# type:`).

```python
# ✅ GOOD — precise types
from collections.abc import AsyncIterator, Callable, Awaitable
from typing import Literal

Status = Literal["created", "in_progress", "completed", "failed"]

class ResponseExecution:
    status: Status
    output_items: list[OutputItem]

async def process(items: Sequence[InputItem]) -> AsyncIterator[Event]: ...

# ❌ BAD — vague types
def process(items: list) -> dict: ...
def handle(data: Any) -> Any: ...
config: dict = {}
```

### III. Azure SDK Design Guidelines Compliance

All packages follow the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html) and this repo's AGENTS.md / CONTRIBUTING.md conventions:

- **Naming**: Packages use `azure-ai-agentserver-{component}` format. Namespace: `azure.ai.agentserver.{component}`. Namespace `__init__.py` files use `pkgutil.extend_path()`.
- **Versioning**: Semantic versioning (`MAJOR.MINOR.PATCH`). Preview: `X.Y.ZbN`. Version stored in `_version.py`, read dynamically by `pyproject.toml` via `[tool.setuptools.dynamic]`.
  - `_version.py` must match the latest version in `CHANGELOG.md`.
  - Preview packages: `is_stable = false` and classifier `Development Status :: 4 - Beta` in `pyproject.toml`.
  - Stable packages: `is_stable = true` and classifier `Development Status :: 5 - Production/Stable`.
- **Line length**: 120 characters max.
- **Formatting**: Black-formatted (`azpysdk black .`). No exceptions.
- **Code style**: Follow [PEP 8](https://peps.python.org/pep-0008/). Naming: modules `snake_case`, classes `PascalCase`, functions/methods/variables `snake_case`, constants `UPPER_CASE`.
- **Imports**: Standard library → third-party → local (relative). Use `from __future__ import annotations` in modules with complex type annotations. No star imports except from `_generated` subpackages.
- **CHANGELOG**: Maintained per package. Unreleased section uses explicit version header (e.g., `## 1.0.0b5 (Unreleased)`) with standard subsections: `### Features Added`, `### Breaking Changes`, `### Bugs Fixed`, `### Other Changes`.
- **MANIFEST.in**: Must include `py.typed`, `azure/__init__.py`, and recursively include samples, tests, and docs.

### IV. Async-First Design

The AgentServer SDK is inherently asynchronous. All I/O-bound operations use `async def` / `await`.

- **ASGI-native**: Server hosts are Starlette subclasses. Middleware must be pure ASGI (no `BaseHTTPMiddleware`).
- **Streaming**: Use `AsyncIterator` with `yield` for SSE event streams. Wrap with `StreamingResponse`.
- **Cancellation**: Use `asyncio.Event` for cooperative cancellation signals.
- **Background tasks**: Use `asyncio.Task` for fire-and-forget work with proper error logging.
- **Handler validation**: All registered handlers must be coroutine functions. Validate with `inspect.iscoroutinefunction()` and raise `TypeError` if not.
- **Context propagation**: Use `contextvars.ContextVar` for request-scoped state (request IDs, invocation IDs).

### V. Fail-Fast Configuration, Graceful Runtime

- **Startup**: Validate all required environment variables (`PORT`, `FOUNDRY_AGENT_NAME`, `FOUNDRY_AGENT_VERSION`, etc.) and configuration at initialization. Raise immediately on missing or invalid config — do not defer failures to request time.
- **Observability failures**: Log warnings but never crash the server. Tracing/telemetry is best-effort.
- **Handler errors**: Return structured error responses via `create_error_response(code=..., message=..., status_code=...)`. Never leak stack traces to clients.
- **Custom exceptions**: Define domain-specific exceptions (e.g., `FoundryStorageError`, `FoundryResourceNotFoundError`) with clear error codes.
- **Broad catches**: `except Exception` is permitted only at top-level dispatch boundaries with explicit `# pylint: disable=broad-exception-caught` and proper logging.
- **Azure Core exceptions**: Use `azure.core.exceptions` hierarchy (e.g., `HttpResponseError`) for client-facing errors where applicable.

### VI. Observability & Correlation

- **Logging**: Module-level logger via `logging.getLogger("azure.ai.agentserver.{component}")`. Use structured key-value logging. No print statements.
- **Tracing**: OpenTelemetry integration via `azure-ai-agentserver-core`. GenAI semantic conventions for spans (`gen_ai.system`, `gen_ai.operation.name`, `gen_ai.agent.name`).
- **Correlation**: Propagate `x-request-id` and `x-ms-client-request-id` headers. Auto-generate from trace ID, header, or UUID. Use `contextvars` for in-process correlation.
- **Metrics**: Export via Azure Monitor (`APPLICATIONINSIGHTS_CONNECTION_STRING`) or OTLP (`OTEL_EXPORTER_OTLP_ENDPOINT`). Expose health endpoints (`/health/live`, `/health/ready`).
- **Graceful shutdown**: Handle `SIGTERM` with configurable drain timeout (default 30s).

### VII. Test-Driven Development (TDD)

All new feature code follows test-driven development:

- **Write tests first**: Before implementing any feature or fixing a bug, write a failing test that defines the expected behavior.
- **Red → Green → Refactor**: Tests must fail before implementation (Red), pass with minimal code (Green), then be cleaned up (Refactor).
- **Acceptance tests from spec**: User story acceptance scenarios in the spec translate directly into test cases during the tasks phase. These are written before implementation begins.
- **Contract tests for interfaces**: When a spec defines a new interface, protocol, or API surface, write contract tests that validate the interface shape before implementing the internals.
- **No untested features**: A feature is not complete until its tests pass. Code without corresponding tests is considered incomplete regardless of whether it "works."
- **Tests drive design**: Let the test-writing process inform API ergonomics. If something is hard to test, it's likely hard to use — simplify the design.

```python
# ✅ GOOD — test written first, defines expected behavior
async def test_durable_task_resumes_after_crash():
    """Handler is re-invoked with metadata intact after simulated crash."""
    app = create_test_app(durable_background=True)
    # ... setup, crash simulation, assertion ...
    assert response.status == "completed"
    assert response.output[0].content == "resumed result"

# ❌ BAD — implementation without a test
# "I'll add tests later" → tests never get added
```

### VIII. Minimal Surface, Maximum Composability

- **Decorator-based registration**: Handlers registered via `@app.invoke_handler`, `@app.response_handler`. Decorators return the function unmodified.
- **Cooperative MRO**: Multi-protocol hosts compose via multiple inheritance: `class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost)`. Each protocol class merges its routes with `super().__init__()`.
- **Builder patterns**: Streaming APIs use fluent builders (`ResponseEventStream.emit_created().emit_in_progress()...`).
- **Lazy resolution**: Expensive computations (input resolution, history loading) use async-cached properties.
- **No unnecessary abstractions**: Prefer simple functions over class hierarchies. Use `Protocol` for structural typing rather than deep inheritance trees.

### IX. Docs ↔ Samples Feedback Loop (NON-NEGOTIABLE)

Developer-facing guides are the authoritative source of guidance — samples are validation that the guidance produces correct outcomes when followed mechanically.

This principle is adjacent to TDD (Principle VII) but distinct: TDD validates behaviour via tests; this principle validates *guidance* via samples.

**The loop:**

1. **Write or update the guide first.** Before writing or rewriting a sample, write or update the relevant section of the developer guide (e.g. `handler-implementation-guide.md`, `durable-responses-developer-guide.md`). The guide defines the mental model, rules, and layered responsibilities (library ↔ handler ↔ upstream framework). The guide does NOT teach individual upstream frameworks; it teaches the contract.
2. **Write the sample by mechanically applying the guide.** Pretend you are a developer reading the guide for the first time. Implement the sample using *only* the guidance in the guide. Do not import knowledge that isn't in the guide.
3. **If the sample comes out wrong, the guide is wrong.** Fix the guide first. Do not patch the sample to work around guide gaps.
4. **Re-derive the sample from the corrected guide.** Repeat until both guide and sample are internally consistent.
5. **Test the guide via samples.** Every guide section that prescribes a pattern must have at least one sample that demonstrates that pattern end-to-end, with an automated test asserting the prescribed outcome.
6. **Run the applicable review checklist.** Before marking a sample done, run the relevant checklist from `.specify/templates/` against it. For durable response samples, that is `durability-sample-checklist-template.md`. A sample with any failing checklist item is incomplete — triage the failure (guide gap / sample bug / test gap / spec gap) and loop back to the earliest applicable step.

**Guide responsibilities:**

- Define the mental model (what each layer owns).
- State the contract between layers (what each layer guarantees and requires).
- Prescribe patterns for the canonical cases.
- Document fallback behaviour for the no-opt-in case.
- **Stay framework-agnostic in the body.** Reference upstream frameworks (Claude SDK, Copilot SDK, LangGraph, etc.) only as concrete examples illustrating an already-stated rule.

**Sample responsibilities:**

- Demonstrate the guide's patterns end-to-end against a real upstream framework.
- Carry the framework-specific reconciliation steps the guide deliberately omits.
- Include an automated test that proves the prescribed outcome holds.
- Pass the applicable review checklist before being marked done.

**Review checklists:**

Mechanical review of samples uses checklists stored under `.specify/templates/`:

- `durability-sample-checklist-template.md` — for any durable response handler sample (covers crash, shutdown, steering, client cancel). Required before any durable sample is shipped.

New canonical sample categories MUST get a matching checklist template. Each checklist item references the constitutional principle or spec FR it enforces, so a checklist failure is traceable to a specific contract.

**What this means for specs:**

Every spec that touches developer-facing samples MUST include a "Docs ↔ Samples Loop" section spelling out:

- Which guide(s) own the contract being specified.
- The sequence: guide changes first, then samples, then re-validation via the applicable checklist.
- The acceptance criterion: a developer following the guide alone (without reading framework source) can produce a sample that passes the checklist.

```python
# ✅ GOOD — guide first, sample derived from guide, checklist closes the loop
# 1. handler-implementation-guide.md updated with recovery contract.
# 2. sample_17_durable_claude.py implemented by following the guide.
# 3. Sample's test fails → guide is missing the "claude_query_in_flight watermark" pattern.
# 4. Guide updated with the watermark pattern.
# 5. Sample re-derived from updated guide → test passes.
# 6. durability-sample-checklist run against sample → 30/30 pass → sample marked done.

# ❌ BAD — sample first, guide retro-fitted, no checklist
# 1. sample_17 written by reading Claude SDK source.
# 2. Guide updated to vaguely match what the sample does.
# 3. A developer reading the guide cannot reproduce the sample's correctness.
# 4. Three weeks later, a different reviewer finds the same crash-recovery
#    gap that was already "fixed" — because no checklist ever caught it.
```

### X. Durability Contract Conformance (NON-NEGOTIABLE)

The durability behavior of `azure-ai-agentserver-responses` is specified in the source-of-truth durability contract. Every row of its matrix has an observable contract; every contract MUST be backed by a behavioral test that exercises it end-to-end through real signals.

**Why this principle exists**: the framework's documented durability matrix once diverged silently from its implementation for three rows. Five overlapping failure modes let those divergences ship: tests asserted helper behavior instead of contract behavior, crash-injection tests were deferred and never picked up, helpers were built without wiring, no single contract validated the matrix as an end-to-end seam, and no structural guard required matrix coverage. This principle is the structural guard.

**The rule:**

1. **Every row of `durability-contract.md` §The matrix MUST have a behavioral test in `tests/e2e/durability_contract/` exercising every applicable termination path via real signals:**
   - **Path A** (graceful shutdown, handler completes within grace): SIGTERM with grace period set sufficiently long for the handler to complete naturally.
   - **Path B** (graceful shutdown, grace exhausted): SIGTERM with grace period set deliberately short so the handler is still running at grace expiry, forcing the in-process marker / hand-off to fire before subprocess exit.
   - **Path C** (crash, or Path-B failure): SIGKILL via `_crash_harness` mid-handler, followed by subprocess restart.
2. **Where the matrix collapses `stream`, the test MUST run its assertions for both `stream=False` and `stream=True`** (parametrized).
3. **The `test_contract_completeness.py` meta-test** parses `durability-contract.md` and fails CI if any (row, applicable path) is missing a paired test module, OR if any module is missing one of the parametrize ids the matrix requires.
4. **Any spec or pull request that affects code in the durability surface** (orchestrator routing, in-process shutdown loop, durable-task primitive integration, stream provider, response store terminal-persist hooks) **MUST land its conformance tests RED before the implementation commit goes green.** The reviewer verifies test-first ordering from the commit history.
5. **Synthetic-crash shortcuts are explicitly disallowed for conformance tests:**
   - MUST NOT mock `_crash_harness`.
   - MUST NOT fabricate a `DurabilityContext` to simulate recovery.
   - MUST NOT call internal failure-marker functions (e.g. `_persist_crash_failed`) directly to simulate Path B or Path C.
   - MUST NOT use a test-only injection to control grace timing; use the framework's real `shutdown_grace_period_seconds` configuration.

**Adding or modifying a row:** any spec that adds a new row to the matrix, or modifies the contract on an existing row, MUST follow `durability-contract.md` §Change control: amend the contract doc, update the conformance suite (RED first, then GREEN after implementation), and update the dev guide / handler guide in the same PR as the implementation.

**Reviewer checklist for PRs touching durability:**

- [ ] Which rows of `durability-contract.md` §The matrix does this change affect?
- [ ] Are the conformance tests for those rows in the PR?
- [ ] Did those tests land RED before the implementation commit (verifiable from git history)?
- [ ] Did the dev guide / handler guide need updates? Are they in this PR?

This principle is referenced by `durability-contract.md` §Test discipline; the two stay in sync via cross-reference. The durability test suite, meta-test, Constitution principle, and template gate implement the structural pieces.

### XI. Contract-Surface Test Depth (NON-NEGOTIABLE)

Conformance tests MUST verify the row's full contract surface, not just terminal status. Shape-only assertions (e.g. `response.status == "completed"`) are necessary but not sufficient; they pass whenever any code path reaches a terminal of the right type and miss content-level drift entirely.

**Why this principle exists**: a streaming-recovery-continuity bug (fix `1e69dba385`) slipped through Principle X's structural gate. Every (row × path) cell had a paired test, all GREEN, but the tests asserted only on `terminal["status"]`. The bug — that pre-crash SSE events were being erased by the recovered handler's terminal-time `save_stream_events` — was invisible because:

- The conformance handler emitted a single `"ok"` delta. Pre-crash content and recovered content were byte-identical, so cross-attempt drift was indistinguishable.
- The tests asked "did recovery happen?" (yes, `status="completed"`) but never asked "did the persisted stream contain the right events in the right order?".

Principle X (every cell has a paired test) was satisfied. Principle XI is the depth complement.

**The rule:**

1. **Per-cell tests MUST verify the contract surface that the cell's mode flags expose to clients:**
   - **For cells with `stream=true`:** event sequence ordering, per-event content (delta text, item shape, content-part fields), sequence-number monotonicity across recovery attempts, and the final terminal event's `response` payload. Pre-crash events MUST be verified to survive in the persisted stream for cells where the contract claims cross-attempt continuity (Row 1).
   - **For cells with `stream=false`:** `response.status`, `response.output` (the assembled output items including their content text), and `response.error` (for failure cells). For polled / background cells, the polled snapshot IS the contract surface; the test MUST assert on its content, not just its terminal type.

2. **The conformance test handler MUST emit per-lifetime-identifiable content** so cross-attempt assertions are sensitive to drift. The current handler at `tests/e2e/durability_contract/_test_handler.py` tags every delta with `f"L{lifetime}_..."` and the final text with a composite `f"L{lifetime}_done|pre=N|chain=…|visited=…"` — tests parse these markers to confirm which lifetime produced which event. Content like `"ok"` that's identical across lifetimes is DISALLOWED in this handler.

3. **The contract coverage matrix at `tests/e2e/durability_contract/CONTRACT_COVERAGE.md` MUST map every normative clause in `durability-contract.md` to the test(s) that verify it.** Cells marked `**GAP**` are explicit findings; they MUST be filled or explicitly justified (with a `n/a` rationale) before the next contract amendment ships.

4. **The `test_contract_coverage_matrix_exists_and_is_non_trivial` meta-test** enforces that every conformance test file is referenced in the matrix. New tests added without a matrix entry fail CI.

5. **The `test_per_cell_tests_assert_more_than_just_status` meta-test** is a SHOULD-gate (warning, not hard fail) that surfaces per-cell tests asserting only on `terminal["status"]` without any other depth signal (event content, response.output, sequence numbers, etc.). It guides reviewers toward adding depth assertions when the cross-cutting tests don't already cover them.

**Adding a new contract clause** (per `durability-contract.md` § Change control):

1. Add the clause to the contract doc.
2. Add a coverage matrix entry mapping the clause to the test(s) that verify it.
3. Add or extend tests with the depth assertions the clause requires.
4. Land all three (contract + matrix + tests) in a single PR.

This principle was added as a follow-up to the conformance-depth reflection. The reflection that motivated it is in `~/.copilot/session-state/.../files/conformance_gap_analysis.md` and summarized in the source-of-truth contract discussion of conformance test depth.

### XII. Core-Primitive TDD Discipline (NON-NEGOTIABLE)

The public surface of the core durable-task primitive (`azure-ai-agentserver-core/azure/ai/agentserver/core/durable/`) is consumed by every higher layer (invocations samples, responses framework, future end-user durable handlers). Drift between the primitive's documented contract and its actual behavior cascades silently into all consumers. This principle is the test-first gate against that drift.

**Why this principle exists**: Principle X locks the responses-layer durability matrix against drift. The core primitive has the same shape of problem one layer down — its `TaskContext` fields, decorator arguments, exception types, and metadata namespaces are a public contract whose drift produces silent miscompiles in consumer code. Prior hardening surfaced concrete examples: `run_attempt` semantics ambiguous between in-process retries and durable failure-retry budget; `previous_input` shipped without being populated; `TaskSuspended` exported but unused; `_FilteredMetadata` filtering the wrong direction. None of these were caught by the existing suite because the suite asserted helper behavior, not the primitive's contract surface. This principle is the structural fix.

**The rule:**

1. **Every public symbol in `azure-ai-agentserver-core/azure/ai/agentserver/core/durable/__init__.py` MUST have at least one paired test in `azure-ai-agentserver-core/tests/durable/` asserting:**
   - The symbol's exact name, location, and presence in `__all__`.
   - Each field's name, type, and behavior under the modes the contract documents (e.g. `TaskContext.retry_attempt` durability across process restart; `TaskContext.recovery_count` increment-on-recovery semantics).
   - Each decorator argument's behavior (accepted-and-honored vs rejected-with-TypeError).
   - Each exception type's raise sites and message shape.

2. **The `test_contract_completeness.py` meta-test** (in `tests/durable/`) parses the consolidated developer guide for the durable-task primitive AND the test directory, and fails CI if any documented contract clause lacks a paired test reference, OR if any public symbol lacks a surface-test entry.

3. **Any spec or pull request that affects the public surface of the core durable-task primitive** (decorator signature, `TaskContext` fields, exception types, metadata namespaces, retry policy) **MUST land its conformance tests RED before the implementation commit goes green.** The reviewer verifies test-first ordering from the commit history.

4. **The non-duplication rule:** when an existing test in `tests/durable/` already covers the surface area being changed, the new conformance must EXTEND the existing test file rather than creating a parallel test file. A new test file is justified only when no existing home exists for the contract surface; the justification MUST be recorded in the conformance tracking document.

5. **Synthetic-bypass shortcuts are explicitly disallowed for conformance tests:**
   - MUST NOT monkey-patch `TaskContext` fields to simulate values that the runtime would produce.
   - MUST NOT instantiate `TaskContext` directly outside the framework's wiring to test behavior that the framework provides.
   - MUST NOT call internal `_` -prefixed APIs to bypass public-surface contract enforcement.

**Adding or modifying a public-surface symbol:** any spec that adds, renames, drops, or changes the semantics of a public symbol in the core durable-task primitive MUST: amend the consolidated dev guide, update the conformance suite (RED first, then GREEN after implementation), and update the spec template's exit checklist verification in the same PR as the implementation.

**Reviewer checklist for PRs touching the core durable-task primitive's public surface:**

- [ ] Which public symbols (decorator args, `TaskContext` fields, exception types, metadata namespaces) does this change affect?
- [ ] Are the conformance tests for those symbols in the PR?
- [ ] Did those tests land RED before the implementation commit (verifiable from git history)?
- [ ] Was an existing test file extended (per non-duplication rule), or is the new file's justification recorded in the conformance tracking document?
- [ ] Did the consolidated dev guide need updates? Are they in this PR?

This principle is the core-layer mirror of Principle X. The two stay in sync via cross-reference. The conformance tracking, non-duplication test discipline, and Constitution amendment implement the structural pieces.

### XIII. Continuous Code Review Discipline (NON-NEGOTIABLE)

Multi-phase implementations land hacks. Each phase, working in isolation, will accept a workaround that LOOKS LOCAL but degrades the overall code shape — a premature abstraction the next phase has to fight, an under-design that propagates scaffolding forward, a silent drift from the spec's design invariants that no per-phase reviewer would catch. This principle is the structural guard: code review is a sequencing fence, not an end-of-PR check.

**Why this principle exists**: durable-task primitive contract hardening surfaced this risk during task planning. The implementation had multiple user stories landing across many phases on one cohesive PR; the user observed that without continuous review, each phase would "just focus on solving its own problem" while collectively shipping a degraded surface. The fix — interleaved per-phase, cross-phase, and final reviews via the `code-review` agent — must apply to every multi-phase contract change. This principle is that generalization.

**The rule:**

1. **Every spec with three or more implementation phases (or three or more user stories) MUST include code review tasks in its task list.** The review tasks are sequencing fences interleaved with implementation, not a single end-of-PR step.

2. **The review structure MUST include:**
   - **Per-phase reviews** at the end of each implementation phase or user-story phase. Scope: catches phase-local quality issues (FR coverage, RED-first commit ordering, no hacks, no scope creep, no shape-only test assertions, dev-guide alignment for that phase's contracts).
   - **Cross-phase seam reviews** at the boundary between any two implementation phases whose hand-off is architecturally significant (e.g., a phase that introduces an API surface another phase will consume; a phase that mutates a hot-path another phase will further mutate). Scope: catches premature abstraction, under-design, and seam quality issues that no single-phase review will catch.
   - **Final whole-PR holistic review** at the end of the polish phase. Scope: catches end-to-end properties no per-phase review can verify alone — spec coverage symbol-for-symbol, documentation truth, plan-phase-decision resolution, constitution exit checklists complete, no regression, commit-history RED-first hygiene, lint/type/build clean.

3. **Each review task dispatches the `code-review` agent (or equivalent) with a precise SCOPE statement tailored to the phase.** Generic "review this code" prompts are insufficient. The scope statement MUST name: (a) the specific FRs / SCs the phase implements; (b) the specific files and commits in the phase's diff; (c) the specific quality risks the phase is most likely to introduce; (d) the cross-phase coupling concerns the next phase will inherit; (e) constitution principles whose violation would be a BLOCKING finding.

4. **Review tasks are blocking GATES.** A phase's review task MUST complete before the next phase begins. BLOCKING and HIGH findings MUST be addressed before the gate clears. MEDIUM and LOW findings MUST be logged to the conformance tracking artifact for the final-review sweep to verify they're either resolved or explicitly accepted with reviewer sign-off.

5. **The `/speckit.tasks` template generates the review tasks automatically.** When the spec has three or more phases or stories, the tasks template MUST emit a "Continuous Code Review" phase as the last phase (with per-phase, cross-phase, and final review tasks), AND each Checkpoint marker in the intervening phases MUST be annotated with a `→ Run TXXX before moving to Phase Y` arrow pointing at its gating review task. The `/speckit.plan` template MUST include a "Code Review Cadence" subsection under the Constitution Check that names which review tasks the implementation will produce.

**What review tasks catch (the recurring failure modes):**

- **Phase-local hacks**: a `# TODO: revisit in next PR`-style shortcut, a one-off helper that should be generalized, an `# type: ignore` without justification, a `# pylint: disable` without justification, a test that monkey-patches an internal symbol to avoid wiring the public surface correctly.
- **Spec drift**: an FR partially implemented, an SC test that asserts shape instead of behavior, a new internal symbol introduced beyond what the spec / data-model authorized.
- **Premature abstraction**: a Phase A factory that the Phase B consumer doesn't actually need, a generic interface that papers over a single-concrete-use.
- **Under-design**: a Phase A seam that Phase B has to monkey-patch around because the original shape doesn't fit, an internal data-format choice that propagates into every later-phase test as a workaround.
- **Documentation drift**: a public-surface change without a corresponding dev guide update, a CHANGELOG entry that misrepresents the change, a docstring that contradicts the spec's contract claim.
- **Pre-existing test deletion**: a pre-existing test that exercised the surface this phase is changing was DELETED instead of PORTED per the spec's "Hardening pre-existing tests" subsection (deletion is allowed only with SOT conformance list justification).
- **RED-first violation**: an implementation commit precedes its paired conformance-test commit in git history (Constitution Principle XII §3 violation).

**Reviewer checklist for PRs touching multi-phase spec implementations:**

- [ ] Does the task list include a "Continuous Code Review" phase with per-phase, cross-phase, and final reviews?
- [ ] Did each per-phase review run at its Checkpoint and complete (with BLOCKING / HIGH findings addressed) before the next phase began?
- [ ] Did the cross-phase seam reviews run at the architectural boundaries the plan identified?
- [ ] Did the final holistic review verify all cross-cutting properties (spec coverage, public surface match, documentation truth, plan-phase-decision resolution, constitution exit checklists, no regression, commit-history RED-first, lint/type/build clean)?
- [ ] Were MEDIUM / LOW findings either resolved or accepted with reviewer sign-off in the conformance tracking artifact?

This principle is referenced by `.specify/templates/plan-template.md` (Constitution Check gate for the Code Review Cadence subsection) and `.specify/templates/tasks-template.md` (auto-generated Phase N: Continuous Code Review section when the spec has ≥3 phases/stories). The two stay in sync via cross-reference.

## Code Standards

### File & Module Organization

```
azure/ai/agentserver/{component}/
├── __init__.py          # Public API exports only
├── _version.py          # VERSION = "X.Y.ZbN"
├── _public_class.py     # One primary class per module
├── _internal_helper.py  # Underscore prefix = private
├── models/              # Data models (generated + runtime)
│   ├── _generated/      # Auto-generated — NEVER hand-edit
│   └── runtime.py       # Runtime model extensions
├── py.typed             # PEP 561 marker
└── tests/               # pytest-based tests
```

- **Public API**: Export only from `__init__.py`. Internal modules prefixed with `_`.
- **One concept per module**: Each `_*.py` file owns one class or closely related set of functions.
- **Generated code**: Lives in `models/_generated/` — never hand-edit. Runtime extensions in `models/runtime.py` or `models/_helpers.py`.

### Docstrings (Sphinx RST Format)

All public classes, methods, and functions require docstrings:

```python
def create_response(
    self,
    input_items: Sequence[InputItem],
    *,
    mode: ResponseMode = "streaming",
) -> ResponseExecution:
    """Create a new response execution.

    :param input_items: The input items to process.
    :type input_items: ~collections.abc.Sequence[~azure.ai.agentserver.responses.InputItem]
    :keyword mode: The response mode. Default is "streaming".
    :paramtype mode: str
    :return: The response execution object.
    :rtype: ~azure.ai.agentserver.responses.ResponseExecution
    :raises ValueError: If input_items is empty.
    :raises ~azure.core.exceptions.HttpResponseError: If the service returns an error.

    .. versionadded:: 1.0.0b5
    """
```

- Use `:param:` + `:type:` (two-line) or `:param type name:` (one-line) format.
- Use `:keyword:` + `:paramtype:` for keyword-only arguments.
- Use `~` prefix to shorten display paths in Sphinx output.
- Document all raised exceptions with `:raises ExceptionType: description`.
- Use `.. versionadded::` for new APIs.

### Testing Requirements

- **Framework**: pytest with pytest-asyncio (`asyncio_mode = "auto"`).
- **HTTP testing**: Use httpx `AsyncClient` with ASGI transport for in-process server testing.
- **Coverage**: All public APIs must have tests. All handler dispatch paths must be tested.
- **Test proxy**: Use the Azure SDK test proxy (`devtools_testutils`) for integration tests requiring live services. Inherit from `AzureRecordedTestCase` and use `@recorded_by_proxy` / `@recorded_by_proxy_async` decorators.
- **Recordings**: Stored in `tests/recordings/` or migrated to `azure-sdk-assets` repo.
- **No credentials in code**: Use environment variables, `self.get_credential()` from test base, or `devtools_testutils.fake_credentials` for CredScan compliance.
- **Samples testing**: Samples must be runnable (`python sample_name.py`). Async samples in `/samples/async_samples/` with `_async.py` suffix.
- **Sample E2E tests (NON-NEGOTIABLE)**: Every sample MUST have a corresponding end-to-end test that exercises the sample's handler/task logic programmatically. Tests replicate the sample logic inline (do NOT import from sample files), run the full lifecycle, and assert outputs. This follows the pattern established in `azure-ai-agentserver-responses/tests/e2e/test_sample_e2e.py`. A sample without an e2e test is considered incomplete.

### Samples Conventions

- **Location**: `/samples/` for sync, `/samples/async_samples/` for async.
- **Naming**: `sample_<scenario>.py` and `sample_<scenario>_async.py`.
- **Snippet markers**: Use `# [START keyword]` and `# [END keyword]` for Sphinx `literalinclude` references.
- **Headers**: Each sample requires a docstring with description and setup instructions.
- **Dependencies**: Only OSI-approved licensed dependencies. Prefer permissive licenses (MIT, Apache 2).

### Pylint Directives

Allowed suppressions (with justification comments):
- `broad-exception-caught` — top-level dispatch only
- `too-many-instance-attributes` — large config/state objects
- `do-not-import-asyncio` — required for signal handling / tasks
- `logging-fstring-interpolation` — when performance is not critical

Pylint design limits (from repo `pylintrc`): max-locals=25, max-branches=20, max-attributes=10, max-parents=15, min-similarity-lines=10.

## Validation & Quality Gates

### Pre-Push Validation (NON-NEGOTIABLE)

**Before pushing any code to remote**, the following checks MUST be run locally on every modified package and MUST pass. Do not push code that fails any of these checks — fix issues locally first.

For each modified package under `sdk/agentserver/`, run from the repo root:

```bash
# Release-blocking checks (MUST pass before push)
python -m azpysdk.main pylint sdk/agentserver/<package>
python -m azpysdk.main mypy sdk/agentserver/<package>
python -m azpysdk.main sphinx sdk/agentserver/<package>
cd sdk/agentserver/<package> && python -m pytest tests/ -x -q

# Also recommended before push
python -m azpysdk.main pyright sdk/agentserver/<package>
python -m azpysdk.main black sdk/agentserver/<package>
```

If a change touches multiple packages, validate ALL of them. Do not assume a change to one package won't break another — especially when modifying `__init__.py` exports or shared types.

### Required Checks (azpysdk)

All checks run via `azpysdk` from the repo root (or `azpysdk <check> .` from the package directory). Every check must pass before merge:

| Check | Command | Purpose |
|-------|---------|---------|
| Pylint | `azpysdk pylint .` | Code quality + Azure SDK custom rules |
| MyPy | `azpysdk mypy .` | Type correctness |
| Pyright | `azpysdk pyright .` | Type completeness |
| Verifytypes | `azpysdk verifytypes .` | Public API type coverage |
| Sphinx | `azpysdk sphinx .` | Documentation builds cleanly |
| Bandit | `azpysdk bandit .` | Security analysis |
| Black | `azpysdk black .` | Code formatting |
| Verifywhl | `azpysdk verifywhl .` | Wheel packaging correctness |
| Verifysdist | `azpysdk verifysdist .` | Source dist packaging correctness |

### Release Blocking Checks

These four checks **must PASS** for any release:
1. **MyPy** — PASS
2. **Pylint** — PASS
3. **Sphinx** — PASS
4. **Tests - CI** — PASS

Failure of any release-blocking check means the package cannot be published.

### Fixing Guidelines

When fixing validation warnings:
- ✅ Fix with 100% confidence using existing patterns in the codebase
- ✅ Reference [Azure pylint guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md) and [MyPy cheat sheet](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
- ✅ Make minimal, surgical changes
- ❌ Never fix warnings without complete confidence
- ❌ Never add new dependencies or imports to fix warnings
- ❌ Never create new files solely to fix warnings
- ❌ Never make large refactoring changes to fix warnings

## Security

- **No hardcoded secrets**: Never commit credentials, connection strings, SAS tokens, or API keys.
- **Bandit scanning**: All code must pass `azpysdk bandit .` static security analysis.
- **CredScan compliance**: Use `devtools_testutils.fake_credentials` in tests. Test proxy sanitizes secrets in recordings automatically.
- **Environment variables**: All credentials and connection strings via environment variables (`FOUNDRY_PROJECT_ENDPOINT`, `APPLICATIONINSIGHTS_CONNECTION_STRING`, etc.).

## Automation Boundaries

### Safe Operations (AI agents and automation)
✅ Generate SDK code from TypeSpec specifications
✅ Run linting and static analysis tools
✅ Fix code quality warnings (with high confidence)
✅ Update documentation (CHANGELOG, README)
✅ Create and update PRs in draft mode
✅ Run existing test suites

### Restricted Operations (require review)
⚠️ Modifying generated code in `_generated/`
⚠️ Adding new dependencies
⚠️ Changing API signatures
⚠️ Disabling or removing tests
⚠️ Large-scale refactoring

### Prohibited Operations
❌ Merging PRs without human review
❌ Releasing packages to PyPI without approval
❌ Committing secrets or credentials
❌ Force pushing to protected branches
❌ Modifying CI/CD pipeline definitions
❌ Changing security or authentication logic without security review

## Governance

This constitution governs all development within `sdk/agentserver`. All code changes (PRs, reviews, AI-generated code) must comply with these principles. Amendments require documentation and team review.

- Principle II (Strong Type Safety) is non-negotiable — no exceptions for convenience.
- All release-blocking quality gates (pylint, mypy, sphinx, tests) must pass before merge.
- Breaking API changes require a version bump and CHANGELOG entry.
- Reference the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html) as the authoritative source for any questions not covered here.
- For detailed tooling instructions, see the [Tool Usage Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md) and [CONTRIBUTING.md](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md).

**Version**: 1.6.0 | **Ratified**: 2026-05-22 | **Amended**: 2026-06-01 (Principle XIII — Continuous Code Review Discipline; minor version bump for the new principle)
