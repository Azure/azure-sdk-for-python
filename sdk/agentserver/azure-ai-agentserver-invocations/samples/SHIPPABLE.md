# Shippable Durable Samples — Manifest

This file is the **source of truth** for which durable invocation
samples ship with this package. A sample appears here only if it
passes every entry in the FR-013 / FR-020 shippable bar:

- Handler contract compliance: uses only the supported public API
  surface of `azure-ai-agentserver-core.durable` (no retired names,
  no internal modules).
- Real-crash e2e green: covered by a test in
  `tests/e2e/sample_*` or the structural/shippable-bar meta-tests in
  `tests/`.
- `README.md` present and covers prereqs, quick start, invocation
  example, crash induction, recovery observation, troubleshooting.
- `requirements.txt` present and lists this sample's upstream-SDK
  dependencies (FR-014 install-independence).
- Follows the FR-010 patterns documented in
  [`DURABLE_SAMPLES.md`](DURABLE_SAMPLES.md).

## Shipped samples

| Sample                | Pattern                                | Streaming | Steerable |
|-----------------------|----------------------------------------|-----------|-----------|
| `durable_copilot`     | Steerable Copilot session              | Yes (SSE) | Yes       |
| `durable_langgraph`   | LangGraph state-graph + fork-on-steer  | No        | Yes       |
| `durable_multiturn`   | Named-namespace metadata multi-turn    | No        | No        |
| `durable_research`    | Long-running checkpoint-and-resume     | Yes (SSE) | No        |

## Not shipped (reference only)

- `durable-agent-demo/` — a deeper foundry-hosted research agent demo
  that includes supervisor/entrypoint scaffolding. Kept in tree as a
  reference for users who want to see the full hosting layout, but it
  is **not** part of the per-sample shippable surface and is exempt
  from the per-sample bar.

## Removed samples

- `durable_claude` — removed in spec 015 Phase 8 (T072). Its
  consumer-driven design was not a good fit for the invocations
  protocol surface.
