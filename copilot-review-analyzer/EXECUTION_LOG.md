# Execution Log — Copilot Code-Review Effectiveness Analyzer

This log records every change made while implementing `IMPLEMENTATION_PLAN.md`,
with a one-line scope justification per entry. Entries are append-only and grouped
by phase.

## Phase 0 — Project scaffolding & tooling
- `pyproject.toml` — pin runtime/dev deps, tooling config, console entrypoint (scaffold packaging).
- `analyzer/__init__.py` + subpackage `__init__.py` (github/pipeline/llm/store/report) — establish importable module tree per DESIGN §4.
- `analyzer/config.py` — frozen validated Config dataclass with `load`/`from_dict`/`config_hash` (centralized validated config).
- `config.yaml` — example configuration (referenced by every stage).
- `analyzer/cli.py` — typer app skeleton; commands added per phase.
- `README.md` — install/usage/config overview.
- `.github/workflows/ci.yml` — ruff/black/mypy/pytest guardrails from commit #1.
- `tests/test_config.py` — config load/validation coverage.

**Gate 0 PASS:** `pip install -e ".[dev]"` ok; `import analyzer` + `Config.load` ok; ruff/black/mypy clean; 9 tests pass.

## Phase 1 — Storage layer (store/)
- `analyzer/store/schema.sql` — v1 schema: DESIGN §6 tables + integrity additions (runs.status/error_summary, comments.source_key UNIQUE, gaps UNIQUE(run_id,comment_id), metrics judged/unjudged/low_confidence counters). Also added `comments.coord_space` (current|original) to materialize coordinate-space tracking required by Phase 2/3 and avoid a later migration.
- `analyzer/store/db.py` — connect/init_db (idempotent, PRAGMA user_version), typed idempotent upserts for runs/prs/comments/gaps/themes/metrics + judgement/overlap/acted_on updaters (centralized SQL honoring UNIQUE constraints).
- `analyzer/cli.py` — wired `analyzer init-db --db PATH` (smallest end-to-end DB slice).
- `tests/test_db.py` — idempotency, FK enforcement+cascade, upsert-on-conflict, source_key dedup, gaps uniqueness, metrics idempotency, latest_completed_run.

**Gate 1 PASS:** test_db.py + all suites green (20 tests); manual /tmp/a.db has six tables, user_version=1. Schema frozen as v1.

## Phase 2 — Ingest one PR end-to-end (github/)
- **PC-1 recorded in IMPLEMENTATION_PLAN.md** — extended GraphQL query with `$reviewsAfter` to paginate reviews (plan's tests/edge-cases require it; DESIGN §7 query lacked it).
- `analyzer/github/queries.py` — PR_REVIEW_DATA_QUERY (+reviewsAfter) and pure parsers → normalized dataclasses (PRMeta/NormalizedComment/Commit/PR); current→original line fallback with coord_space; first-comment-as-review-point; source_key (databaseId or hash). (Parsing isolated/testable.)
- `analyzer/github/client.py` — httpx client: bearer auth (env/`gh auth token`), retry on 5xx + secondary rate limit (Retry-After), GraphQL POST, REST PR enumeration filtered by merged_at/closed_at over [start,end), full thread/review/commit cursor pagination in fetch_pr. (Single funnel for GitHub I/O.)
- `analyzer/pipeline/ingest.py` — window/since parsing, fetch_window orchestration, normalized_pr_to_dict for dry-run. (Stage 1 deterministic window math.)
- `analyzer/cli.py` — `analyzer run --repo --since --state --max-prs --dry-run`; dry-run prints normalized JSON, writes nothing. (Phase-2 vertical slice.)
- `tests/fixtures/pr_page1.json`, `pr_page2.json` — scrubbed/synthetic paginated GraphQL fixtures (outdated thread, deleted author, reply, empty review body).
- `tests/test_queries.py`, `tests/test_client.py` — parser + mocked-HTTP coverage (pagination, null-line fallback, 401/502/secondary-limit, enumeration state/window).

**Gate 2 PASS:** 38 tests green offline; live `--dry-run` against octocat/Hello-World and real fetch of Azure/azure-sdk-for-python#47461 confirmed correct ranges, Copilot login, review body, commits, rate limit.

## Phase 3 — Attribution (pipeline/attribute.py)
- `config.yaml` — added GraphQL-form Copilot login `copilot-pull-request-reviewer` (no `[bot]`); normalizer strips `[bot]` so both forms match.
- `analyzer/pipeline/attribute.py` — pure `classify_author` (normalizes `[bot]`, None→other_bot), `overlaps` (same path+coord_space, ±line_fuzz), and `persist_pr_comments` writing author_kind/copilot_overlap/normalized range into comments. (Stage 2 deterministic facts.)
- `analyzer/store/db.py` — `set_comment_overlap` now accepts Optional[bool] (NULL when overlap undeterminable).
- `tests/test_attribute.py` — author matrix + overlap truth table (disjoint/touching/nested/fuzz boundary/cross-file/incomparable coords).
- `tests/test_attribute_persist.py` — DB integration: every comment row has non-null author_kind; overlap True/False/NULL cases.

**Gate 3 PASS:** 55 tests green; real PR #47461 Copilot/human split hand-verified (3 copilot, correctly classified).

## Phase 4 — Gap plumbing without LLM (pipeline/gaps.py, metrics.py) + run orchestrator
- `analyzer/pipeline/gaps.py` — pure `is_gap` (substantive∧diff_detectable∧¬overlap; treats SQLite int overlap correctly) + `detect_gaps` partitioning judged/unjudged/low-confidence and persisting gaps idempotently. (Stage 4a.)
- `analyzer/pipeline/metrics.py` — DESIGN §9 formulas with explicit denominators; divide-by-zero→NULL; data-quality counters. (Stage 5.)
- `analyzer/pipeline/orchestrate.py` — full run pipeline (ingest→attribute→stub/LLM judge→gaps→metrics) with run status tracking; `apply_stub_judgements` marks all human comments substantive (Phase-4 stub, replaced in Phase 6).
- `analyzer/pipeline/classify.py` — Phase-6 placeholder (judge_run raises NotImplementedError) so orchestrator `--use-llm` path imports.
- `analyzer/cli.py` — `run` (non-dry-run) now invokes the orchestrator; dry-run unchanged.
- `tests/test_gaps.py`, `tests/test_metrics.py` — gap rule, overlap exclusion, unjudged/low-confidence, idempotency, divide-by-zero→NULL.

**Gate 4 PASS:** 63 tests green; real run on Azure/azure-sdk-for-python (3 PRs) wrote runs/prs/comments(72)/gaps(19)/metrics; status=completed; miss_rate=19/19=1.0, burden=19/3 hand-verified under all-substantive stub; all comments have non-null author_kind.

## Phase 5 — Reporting (report/)
- `analyzer/report/data.py` — read-only queries; resolve_run_id ('latest'→newest completed unless --include-incomplete), themes/metrics/trend queries; RECALL_CAVEAT; NoDataError. (Completed-runs-only by default.)
- `analyzer/report/export.py` — deterministic markdown/JSON/CSV; documented JSON schema (schema_version); data-quality counters + caveat in every report.
- `analyzer/report/render.py` — rich tables for report/themes, trend sparkline.
- `analyzer/cli.py` — `report`/`themes`/`trend` commands (+ `--include-incomplete`); empty/missing data → friendly message, exit 0.
- `tests/test_export.py` — golden JSON/markdown/CSV, latest-resolves-to-completed, failed-run requires flag, sparkline, deterministic output.

**Gate 5 PASS:** 71 tests green; on real DB /tmp/g4.db report (table+markdown), trend, and empty-DB ("No data", exit 0) all correct; markdown issue-ready; caveat present.

## Phase 6 — LLM judge (llm/prompts.py, llm/judge.py, classify.py)
- `analyzer/llm/prompts.py` — verbatim DESIGN §8 judge/theme prompt templates (system, user, per-comment, theme). (Single source of prompt truth.)
- `analyzer/llm/client.py` — GitHub Models OpenAI-compatible HTTP client (JSON mode, temperature=0, Bearer token via resolve_token, retry/backoff on 429/5xx) + `make_completer` factory; judge stays HTTP-free behind a `Completer` callable. (Centralizes all model I/O.)
- `analyzer/llm/judge.py` — HTTP-free judge core: batch/chunk comments, render prompts, strict schema validation, ONE corrective retry for missing/invalid ids, never crashes (failed parses → unjudged); body/diff truncation to bound tokens; confidence clamp + category fallback. (Hardened classification per DESIGN §8.)
- `analyzer/pipeline/classify.py` — replaced placeholder: real `judge_run` persists judgements & leaves unjudged NULL, raises `JudgeError` when unjudged ratio > max_unjudged_ratio; pure `acted_on(path,created,commits)` + best-effort `link_acted_on` (REST commit-files; NULL when path data unavailable, capped at 50 commits). (Stage 3 judge + deterministic acted_on.)
- `analyzer/github/client.py` — added `fetch_commit_files` (REST per-commit paths; None on any error). (Path source for acted_on.)
- `analyzer/pipeline/orchestrate.py` — `--use-llm` branch now builds a Models completer, runs real judge, then links acted_on over collected (pr, pr_id) pairs. (Wires Phase-6 into the run.)
- `tests/test_judge.py`, `tests/test_acted_on.py` — valid/missing-id-retry/malformed/invalid-field/category-fallback/confidence-clamp/batching/exception cases; acted_on truth table; judge_run persistence + excessive-unjudged→JudgeError.

**Gate 6 PASS:** 87 tests green; ruff/black/mypy clean. Live GitHub Models (gpt-4o-mini) smoke test: ZeroDivisionError comment → substantive/bug, typo comment → non-substantive/nit; malformed-JSON survival proven by unit tests (unjudged, no crash); corrective retry exercised.

## Phase 7 — Themes & final metrics (pipeline/themes.py, metrics.py finalize)
- `analyzer/pipeline/themes.py` — HTTP-free theme tagger behind `Completer`: pure `normalize_label` (vocab-constrained, unknown→`other`), batched `assign_themes` (every gap gets exactly one label; per-gap miss→`other`; all-batches-fail → themes unavailable), `tag_run` upserts `themes` with aggregated `gap_count` and links `gaps.theme_id`. (Trendable taxonomy — headline output.)
- `analyzer/store/db.py` — added `set_gap_theme(gap_id, theme_id)` helper for linking. (Theme→gap linkage.)
- `analyzer/pipeline/orchestrate.py` — `--use-llm` path now runs `themes.tag_run` after gap detection using the same Models completer. (Wires theming into the run.)
- `analyzer/cli.py` — added `run --use-llm` flag (real judge + theme tagging; default still stub). (User/gate entry point for the LLM pipeline.)
- `analyzer/pipeline/metrics.py` — already computes real `copilot_acted_on_rate` from `acted_on` (known-denominator); now exercised by populated data. (Completes DESIGN §9 time series.)
- `tests/test_themes.py` — vocab constraint, out-of-vocab→other, missing-id→other, total-failure→unavailable, gap_count aggregation + linkage, zero-gaps no-write, unavailable leaves themes empty. `tests/test_metrics.py` extended for `copilot_acted_on_rate` (known-denominator) + all-unknown→NULL.

**Gate 7 PASS:** 97 tests green; ruff/black/mypy clean. Live end-to-end (gpt-4o-mini) on Azure/azure-sdk-for-python: run 1 (4 PRs) judged 18/18, acted_on set for 1 Copilot comment, themes {api-design:2, other:1}, miss_rate=1.0/burden=0.75; run 3 likewise. `themes --min-count 2` renders (api-design=2, min-count correctly hides other=1); `trend --metric miss_rate` renders across runs 1 & 3 with sparkline + recall caveat. Transient GitHub GraphQL 504 on one wider run was correctly recorded as status=failed (error handling verified), then re-run succeeded.

## Phase 8 — Scheduled workflow (.github/workflows/analyze.yml)
- `.github/workflows/analyze.yml` — weekly `schedule` + `workflow_dispatch` job: checkout → setup-python → `pip install -e .` → restore DB from `analyzer-data` branch → `analyzer run --use-llm` → render markdown report → upload DB artifact → commit DB to `analyzer-data` branch → open/update one labelled summary issue (idempotent edit, not new-issue spam). Least-privilege `permissions: contents/issues write`; `concurrency` serializes runs. (Automates periodic mining, human-in-the-loop for prompt changes.)
- DB persistence strategy CHOSEN & documented: durable orphan `analyzer-data` branch (trend continuity across weekly runs) PLUS per-run artifact (audit). Cache rejected (eviction breaks trends).
- Token wiring: `GITHUB_TOKEN` for repo/issues/data-branch; optional `ANALYZER_PAT` secret preferred for cross-repo + higher Models limits; tokens never echoed (`set -euo pipefail`, no `set -x`; token only in clone URL).
- `analyzer/cli.py` — `run --use-llm` flag (added in Phase 7) is the workflow entry point.
- Empty-window handling: report emits "No data" → summary step substitutes a "no new data" body; issue still updated. Prompt-delta appendix appended for human approval (no auto prompt edits).
- `README.md` — documented `--use-llm`, the scheduled workflow, persistence strategy, and token/secret wiring.

**Workflow location note (not a plan change):** placed under the self-contained subproject `copilot-review-analyzer/.github/workflows/` consistent with the Phase-0 `ci.yml`; the analyzer is designed as a self-contained project (its `.github/` is the project root when split out).

**Gate 8 — verified by proxy (environment limitation):** a real `workflow_dispatch` green run cannot be executed inside this sandbox (no GitHub Actions runner; would require pushing the branch and dispatching on github.com). Verified instead: YAML parses (triggers schedule+workflow_dispatch, perms contents/issues:write); every embedded shell step passes `bash -n` and `shellcheck` clean; the full command chain runs locally — `analyzer run --use-llm` + `analyzer report --format markdown` produce a correct issue-ready summary (metrics, data-quality counters, top themes, recall caveat, human-approval prompt-delta appendix); the empty-data path substitutes a "no new data" body. Final green must be confirmed once pushed to GitHub.

## Post-Phase-8 fix — resilient ingest (pipeline/ingest.py)
- `analyzer/pipeline/ingest.py` — `fetch_window` now catches `GitHubError` per PR and skips the offending PR (logging "Skipping PR #N" + a "Skipped k/n" summary) instead of aborting the whole run; added `skip_errors: bool = True` param (set false to surface the first error). (Robustness: one pathological PR must not sink a run — consistent with the judge/themes never-crash design.)
  - **Trigger:** live `analyzer run --since 7d --use-llm` repeatedly failed because PR #47467's `reviewThreads` GraphQL query returned a persistent server-side HTTP 502 that survived the client's 4 retries; all other PRs fetched fine. Verified fix with a real run (run 4): 11 PRs analyzed, #47467 skipped, status=completed.
  - Scope justification: surgical change to a single function; no schema/metric/API change; lint+type+97 tests still green.

## Post-plan feature — suggest-prompts (gap → prompt-improvement guidance)
User request (beyond the original 9-phase plan): for each gap, store a very specific "what Copilot missed here" finding AND a generalizable prompt-improvement idea; surface both in any report CLI as a pasteable chunk to drop into existing Copilot review prompts.
- `analyzer/store/schema.sql` + `store/db.py` — added `gap_suggestions` table (UNIQUE(run_id,gap_id)) + `upsert_gap_suggestion`; bumped `SCHEMA_VERSION` 1→2 (additive `CREATE TABLE IF NOT EXISTS`, applies on next init_db). (Persist per-gap suggestions keyed to a run.)
- `analyzer/llm/prompts.py` — added `SUGGEST_SYSTEM`/`SUGGEST_USER_TEMPLATE`/`SUGGEST_ITEM_TEMPLATE`. (Prompt the model for one missed_finding + prompt_improvement per gap.)
- `analyzer/llm/suggest.py` — HTTP-free `suggest_for_gaps(items, *, complete, batch_size)` mirroring `llm/judge.py`: batches gaps, validates JSON, one corrective retry for missing ids, never crashes (failures → `unsuggested_ids`). (Testable LLM core behind a Completer.)
- `analyzer/pipeline/suggest.py` — `suggest_run(conn, run_id, config, *, complete)`: loads gap contexts (gaps⋈comments⋈prs⋈themes), persists suggestions, returns `SuggestStats`. (Orchestration entry point for the CLI.)
- `analyzer/report/data.py` — `get_gap_suggestions(conn, run_id)` join query. (Read suggestions for reporting.)
- `analyzer/report/export.py` — pure `build_prompt_addendum(suggestions)` (group prompt_improvement by theme, case-insensitive dedup, cite PRs → pasteable markdown); `build_report_dict` now includes `suggestions` + `prompt_addendum`; `to_markdown` adds "What Copilot missed (per gap)" + addendum sections; `JSON_SCHEMA_VERSION` 1→2. (Surface suggestions in every report format.)
- `analyzer/report/render.py` — rich table "What Copilot missed → prompt fixes" + printed addendum. (Surface in the default table view.)
- `analyzer/cli.py` — new `suggest-prompts` command (resolve run, init_db, build completer, run suggest, print addendum); `report` already shows suggestions via build_report_dict. (User-facing entry point.)
- `tests/test_suggest.py` (new) + `tests/test_export.py` (suggestion-surfacing test). (Cover valid/retry/malformed/invalid-fields/exception/batching + addendum grouping/dedup/empty + end-to-end report surfacing.)
- `README.md` — documented `suggest-prompts`, added it to the getting-started/usage/architecture (new "Suggest" stage + diagram node, re-validated Mermaid render).
- **Gate PASS:** 106 tests green; ruff/black/mypy clean. Live: `analyzer suggest-prompts --run 4` (gpt-4o) generated 5/5 suggestions (0 skipped) and printed a themed, PR-cited pasteable addendum; `analyzer report --run 4` surfaces per-gap missed_finding + addendum.
- Scope justification: additive feature only — new table/module/command and new optional report fields; no change to existing pipeline stages, metrics, or prior schema columns; all pre-existing tests still green.
