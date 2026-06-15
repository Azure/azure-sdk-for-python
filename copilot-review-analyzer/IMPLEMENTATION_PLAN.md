# Copilot Code-Review Effectiveness Analyzer — Implementation Plan

> Companion to `DESIGN.md`. This is the actionable, step-by-step build plan.
> It maps the de-risked order in DESIGN §12 into discrete phases, each with a
> **decision checkpoint gate** that must pass before the next phase starts.

## How to use this document
- Work phases **top to bottom**. Do not start a phase until the previous **gate**
  is green.
- Each step states **What / Where / Why / Expected outcome**.
- Each gate states **what to verify** and the **criteria to proceed**.
- A phase is "done" only when its tests pass and its gate criteria are met.

## Conventions & ground rules
- Python 3.10+, type hints everywhere, `ruff` + `black` clean, `mypy` clean on
  `analyzer/` (DESIGN §2).
- No network in unit tests — use recorded fixtures (`tests/fixtures/`).
- Deterministic stages (ingest/attribute/gaps/metrics) must be **fully testable
  without an LLM**; all model calls are isolated behind the `llm/` package.
- Every stage is **idempotent** and re-runnable; rely on `UNIQUE` constraints
  (DESIGN §6) rather than "delete + reinsert". Be explicit about run semantics:
  re-running a stage for the same `run_id` updates existing rows, while starting a
  new run for the same repo/window creates a separate comparable time-series point.
- Secrets only from env (`GH_TOKEN` / `GITHUB_TOKEN`); never logged, never committed.
- A completed trend/report must only use runs with a successful terminal status;
  half-populated or failed runs are retained for debugging but excluded by default.

---

## Plan changes (deviations recorded during implementation)

> This section is appended during implementation when a step cannot be followed
> exactly as written. Each entry states the deviation and its rationale.

### PC-1 (Phase 2) — Extend the GraphQL query with `$reviewsAfter`
- **Plan/DESIGN as written:** Phase 2 step 2 says to copy the `PRReviewData` GraphQL
  string from DESIGN §7 verbatim. That query only parametrizes `$threadsAfter` and
  `$commitsAfter`; `reviews(first: 50)` has no cursor variable.
- **Conflict:** Phase 2's own "Tests to add" and "Edge cases" require *"pagination
  cursors followed for review threads, thread comments, reviews, and commits"* and
  *">50 top-level reviews → pagination exercised"*. These cannot be satisfied while
  the query lacks a reviews cursor, and silently dropping reviews beyond the first 50
  would violate the rule that data is *"preserved … rather than silently dropped"*.
- **Deviation:** The query adds a `$reviewsAfter` variable and pages `reviews` via
  `pageInfo.endCursor`, mirroring the existing thread/commit pagination.
- **Thread comments:** Only the thread's *first* comment is the review point (DESIGN
  §7); replies are counted then skipped, so paginating beyond the first 50 thread
  comments cannot change parser output. Thread-comment pagination is therefore
  intentionally **not** implemented; this is documented rather than tested.

### PC-2 (post-plan) — `suggest-prompts` feature (Stage 6 / gap → prompt improvement)
- **Plan as written:** The original plan ends at Phase 8 (scheduled workflow) with
  Phase 9 (web viewer) optional. "Proposed prompt deltas" in the scheduled report was a
  static human-authored placeholder; nothing auto-generated prompt feedback from gaps.
- **User request (deviation driver):** For each gap, store a very specific finding of what
  the Copilot reviewer missed *there* plus a generalizable prompt-improvement idea, and
  surface both in any report CLI as a chunk of text pasteable into existing Copilot review
  prompts to close the gap.
- **Deviation:** Added an on-demand stage (`pipeline/suggest.py` + `llm/suggest.py`),
  a `gap_suggestions` table (SCHEMA_VERSION 1→2, additive), a `suggest-prompts` CLI
  command, and report surfacing (`build_prompt_addendum`, JSON_SCHEMA_VERSION 1→2,
  markdown/table sections). The LLM core mirrors the Phase-6 judge (HTTP-free behind a
  `Completer`, batched, one corrective retry, never crashes). No existing pipeline stage,
  metric, or prior schema column changed; all pre-existing tests remain green.
- **Why additive, not a new mandatory phase:** suggestion generation is opt-in (its own
  command) and read-only against the analysis DB, preserving the deterministic
  ingest→metrics pipeline and its no-LLM testability guarantee.

---

## Phase 0 — Project scaffolding & tooling

### Steps
1. **Create the package skeleton.**
   - *Where:* `copilot-review-analyzer/` — `pyproject.toml`, `analyzer/__init__.py`,
     and the empty module tree from DESIGN §4 (`github/`, `pipeline/`, `llm/`,
     `store/`, `report/`), plus `tests/` and `tests/fixtures/`.
   - *Why:* Establish an importable package and a place for every later module so
     imports never churn.
   - *Expected:* `pip install -e .` succeeds; `import analyzer` works.
2. **Pin dependencies & dev tooling.**
   - *Where:* `pyproject.toml` — runtime deps (`httpx`, `typer`, `rich`, `pyyaml`)
     and dev deps (`pytest`, `pytest-cov`, `mypy`, `ruff`, `black`,
     `respx`/`pytest-httpx` for HTTP mocking).
   - *Why:* Reproducible env; HTTP mocking enables offline tests.
   - *Expected:* `pip install -e ".[dev]"` resolves cleanly.
3. **Add config scaffolding.**
   - *Where:* `config.yaml` (example) + `analyzer/config.py` loading it into a
     frozen dataclass with validation (repos, `copilot_logins`, model, sampling
     `max_prs`, overlap `line_fuzz`, theme `vocab`, confidence threshold).
   - *Why:* Centralized, validated config is referenced by nearly every stage.
   - *Expected:* `Config.load("config.yaml")` returns a typed object; invalid keys
     and missing required fields raise a clear error.
4. **Add CI lint/test stub.**
   - *Where:* `.github/workflows/ci.yml` — `ruff`, `black --check`, `mypy`, `pytest`.
   - *Why:* Guardrails from commit #1.
   - *Expected:* CI runs (red is fine until tests exist).

### 🚦 Gate 0 — "Scaffold compiles"
- **Verify:** `pip install -e ".[dev]"` succeeds; `import analyzer`,
  `Config.load` on the sample config works; `ruff`/`black --check`/`mypy` pass on
  the (empty) package.
- **Proceed when:** all of the above are green and the module tree matches DESIGN §4.

---

## Phase 1 — Storage layer (`store/`)  — *DESIGN §12.1*

### Steps
1. **Author the schema.**
   - *Where:* `analyzer/store/schema.sql` — start from DESIGN §6 (`runs`, `prs`,
     `comments`, `themes`, `gaps`, `metrics`) and add the implementation-required
     integrity fields before freezing v1:
     - `runs.status` (`started|completed|failed`) and `runs.error_summary` so
       incomplete runs are not reported as valid trend points.
     - `comments.source_key TEXT NOT NULL` as a stable fallback key when GitHub
       `databaseId` is missing; use `UNIQUE(run_id, source_key)` instead of relying
       on nullable `external_id`.
     - `gaps` constraint `UNIQUE(run_id, comment_id)` so re-running gap detection
       cannot double count the same comment.
     - metrics counters for `judged_human_count`, `unjudged_human_count`, and
       `low_confidence_human_count` so LLM outages or threshold filters are visible.
   - *Why:* The schema is the contract every later stage writes against.
   - *Expected:* File loads via `executescript` with `PRAGMA foreign_keys = ON`.
2. **Build the DB access layer.**
   - *Where:* `analyzer/store/db.py` — `connect(path)`, `init_db()` (idempotent
     `CREATE TABLE IF NOT EXISTS`), typed `upsert_*` / `insert_*` helpers, and a
     thin migration check (store `schema_version` in a `PRAGMA user_version`).
   - *Why:* Centralizes SQL so stages don't hand-write queries; idempotent upserts
     honor the `UNIQUE` constraints for safe re-runs.
   - *Expected:* `init-db` creates a fresh DB; re-running it is a no-op; inserting
     a duplicate `(run_id, source_key)` updates rather than errors.
3. **Wire the first CLI command.**
   - *Where:* `analyzer/cli.py` — `analyzer init-db [--db PATH]` (typer app).
   - *Why:* Smallest end-to-end vertical slice; proves packaging + DB together.
   - *Expected:* `analyzer init-db --db /tmp/a.db` creates a valid SQLite file.

### Tests to add
- `tests/test_db.py`: `init_db` idempotency; FK cascade (deleting a `run`
  cascades `prs`/`comments`/`gaps`/`metrics`); upsert-on-conflict updates a row;
  nullable `external_id` rows do not duplicate because `source_key` is unique;
  `gaps` cannot duplicate `(run_id, comment_id)`; `user_version` set.

### Edge cases
- DB file in a non-existent directory → clear error.
- Re-init over an existing populated DB must not drop data.
- `foreign_keys` actually enforced (SQLite requires the pragma per-connection).
- Failed/partial runs remain queryable for audit but are excluded from `latest`,
  `trend`, and default reports.

### Observability
- `db.py` logs the DB path and `user_version` at `init` (INFO).

### 🚦 Gate 1 — "DB is real and idempotent"
- **Verify:** `tests/test_db.py` passes; a manually inspected `/tmp/a.db` has all
  six tables, the DESIGN §6 indexes, and the v1 integrity additions listed above.
- **Proceed when:** schema is frozen as v1, idempotency + uniqueness + FK-cascade
  tests are green.

---

## Phase 2 — Ingest one PR end-to-end (`github/`) — *DESIGN §12.2*

### Steps
1. **HTTP client with auth, retry, pagination.**
   - *Where:* `analyzer/github/client.py` — `httpx` client; bearer auth from
     `GH_TOKEN`/`gh auth token`; retry with backoff on 5xx + secondary rate
     limits; helper to follow `pageInfo.endCursor`; surfaces `rateLimit` from
     responses (DESIGN §7); handles GraphQL responses with partial `data` plus
     `errors` by preserving usable data and recording warnings.
   - *Why:* All GitHub I/O funnels through one place for retry/throttle/testing.
   - *Expected:* A GraphQL POST returns parsed JSON; transient 502 retried; 401
     raises a clear auth error.
2. **Queries + parsers.**
   - *Where:* `analyzer/github/queries.py` — the `PRReviewData` GraphQL string from
     DESIGN §7 and pure parser functions: PR metadata, review threads →
     `(path, line_start, line_end, first-comment-as-review-point)`, top-level
     reviews, commit timeline. Implement the **range fallback** rules from DESIGN
     §7 parser notes (`line||originalLine`, `startLine||originalStartLine`) while
     preserving whether coordinates came from current or original positions.
   - *Why:* Parsing is pure/testable; isolates the GraphQL shape from the rest.
   - *Expected:* Given a recorded response, parsers emit normalized dataclasses.
3. **PR enumeration.**
   - *Where:* `github/client.py` — REST `GET /repos/{o}/{r}/pulls?state=…&sort=updated`
     (or search API) to list candidates, then filter by `merged_at`/`closed_at`
     according to `--state`. Define the window as `[window_start, window_end)` in
     UTC. Avoid using `updated_at` as the final inclusion criterion because labels,
     comments, or edits can move old PRs into the window.
   - *Why:* GraphQL is per-PR; we need the candidate list first (DESIGN §7).
   - *Expected:* Returns PR numbers filtered by `--state` (`merged`, `closed`,
     `all`) and the normalized date window.
4. **`run` skeleton + raw dump.**
   - *Where:* `analyzer/pipeline/ingest.py` + `cli.py run … --dry-run`.
   - *Why:* Verify against a **real PR** before any processing (DESIGN §12.2).
   - *Expected:* `analyzer run --repo o/n --since 7d --max-prs 1 --dry-run` prints
     normalized JSON for one PR without writing the DB.

### Tests to add
- `tests/fixtures/`: record 1–2 real GraphQL responses (incl. a paginated thread
  set and an **outdated/resolved** thread) + a multi-commit timeline.
- `tests/test_queries.py`: parser maps threads → ranges; pagination cursors
  followed for review threads, thread comments, reviews, and commits; reviews/commits
  parsed; rate-limit surfaced; partial GraphQL errors recorded without losing valid
  data.
- HTTP tests use `pytest-httpx`/`respx` (no live calls).

### Edge cases
- Outdated thread where `line` is null → fall back to `originalLine`.
- Thread with only replies / empty `comments` nodes.
- PR with >50 review threads or >100 commits → pagination exercised.
- Thread with >50 comments and PR with >50 top-level reviews → pagination exercised.
- Deleted author (`author: null`) → treated as `other`/`unknown`, never crash.
- Secondary rate-limit (HTTP 403 + `Retry-After`) honored.
- Search/REST enumeration over many PRs, including GitHub search's 1,000-result cap
  if the search API is used.
- Closed-unmerged PRs vs merged PRs are classified according to `--state`.
- Renamed/deleted/binary/generated files are preserved in normalized data with a
  policy flag for later inclusion/exclusion rather than silently dropped.
- Recorded fixtures are scrubbed/anonymized if they contain proprietary code,
  review text, or personal data.

### Observability
- Per-PR INFO log: number, thread count, comment count, `rateLimit.remaining/cost`.
- `--dry-run` writes nothing; clearly labeled output.

### 🚦 Gate 2 — "Real PR ingests correctly"
- **Verify:** Run `--dry-run` against a known real PR; manually confirm thread
  ranges, the Copilot review body, and commit dates match the PR on GitHub.
  Parser tests green; pagination + null-line fallback covered.
- **Proceed when:** the normalized dump for a real PR is correct and
  fixture-based parser tests pass offline.

---

## Phase 3 — Attribution (`pipeline/attribute.py`) — *DESIGN §12.3*

### Steps
1. **Author classification.**
   - *Where:* `attribute.py::classify_author(login) -> "copilot"|"human"|"other_bot"`
     using `config.copilot_logins` + `login.endswith("[bot]")` (DESIGN §5).
   - *Why:* Every downstream metric depends on splitting Copilot vs human.
   - *Expected:* Configured Copilot logins → `copilot`; other `[bot]` → `other_bot`;
     else `human`; `None`/empty → `other_bot`/`unknown` (documented).
2. **Line-range mapping + overlap.**
   - *Where:* `attribute.py::overlaps(human_range, copilot_ranges, line_fuzz) -> bool`
     — same normalized `path`, same coordinate space (`current` vs `original`),
     intersecting `[start,end]` ranges with ±`line_fuzz` (DESIGN §5).
   - *Why:* Overlap is the core of gap detection (a human point Copilot also flagged).
   - *Expected:* Touching/contained/fuzz-adjacent ranges overlap; different files
     never overlap.
3. **Persist enrichments.**
   - *Where:* `attribute.py` writes `author_kind`, `copilot_overlap`, normalized
     `(file_path, line_start, line_end)` into `comments` (DESIGN §6).
   - *Why:* Materialize deterministic facts so Stage 3/4 read from the DB.
   - *Expected:* After attribute, every comment row has non-null `author_kind`.

### Tests to add
- `tests/test_attribute.py`: author matrix (copilot login, `x[bot]`, human, null);
  overlap truth table (disjoint, touching, nested, fuzz=±N boundary, cross-file).

### Edge cases
- `line_fuzz = 0` exact-touch behavior; large single-line vs range hunks.
- Copilot comment with null range (review body) excluded from overlap set.
- Case/owner sensitivity of logins (normalize to lower-case).
- Renamed paths compare against a canonical path when GitHub exposes one; otherwise
  do not claim overlap across old/new paths.
- If human and Copilot comments only have incomparable coordinate spaces, mark
  overlap as unknown/false and include the count in observability.
- Explicitly decide whether thread replies are candidate human comments. Default:
  classify first review-point comments only, but count skipped replies so the choice
  is visible.

### Observability
- INFO summary per PR: `#copilot / #human / #other_bot`, `#human_with_overlap`.

### 🚦 Gate 3 — "Attribution is deterministic & correct"
- **Verify:** `test_attribute.py` passes including fuzz boundaries; on the Phase-2
  real PR, spot-check that Copilot vs human split is right.
- **Proceed when:** pure-function tests green and real-PR split is hand-verified.

---

## Phase 4 — Gap plumbing without LLM (`pipeline/gaps.py`) — *DESIGN §12.4*

### Steps
1. **Gap rule (LLM-stubbed).**
   - *Where:* `gaps.py::is_gap = is_substantive and diff_detectable and not copilot_overlap`
     (DESIGN §5). For this phase, **treat all human comments as substantive +
     diff_detectable** to validate plumbing only.
   - *Why:* Prove gap detection, DB writes, and metrics wiring before paying for
     an LLM (DESIGN §12.4). Use the configured confidence threshold only after
     Phase 6; in this phase record that all stubbed comments are "judged" for
     plumbing but not for final-quality conclusions.
   - *Expected:* Gaps = human comments with no Copilot overlap.
2. **Persist gaps.**
   - *Where:* `gaps.py` inserts into `gaps` (`run_id, pr_id, comment_id, category`)
     (DESIGN §6).
   - *Why:* Downstream report/metrics read the `gaps` table.
   - *Expected:* Gap rows reference real comments; FK integrity holds.
3. **Provisional metrics (`metrics.py`).**
   - *Where:* `metrics.py` computes the DESIGN §9 formulas (`miss_rate`,
     `copilot_overlap_rate`, `human_burden_per_pr`) — `acted_on` may be NULL for
     now. Define denominators explicitly:
     - `miss_rate = gaps / judged_substantive_diff_detectable_human_comments`.
     - `copilot_overlap_rate = overlapped_substantive_human_comments /
       judged_substantive_human_comments`.
     - `human_burden_per_pr = judged_substantive_human_comments / pr_count`.
     - unjudged or low-confidence comments are excluded from denominators and
       surfaced as separate counters.
   - *Why:* See real numbers early; lock the formula shapes.
   - *Expected:* One `metrics` row per run; rates in `[0,1]` or NULL when divide-by-zero.

### Tests to add
- `tests/test_gaps.py`: overlap → not a gap; no-overlap → gap; empty inputs.
- `tests/test_metrics.py`: each formula incl. divide-by-zero → NULL, not error.

### Edge cases
- Run with zero human comments → metrics NULL/0, no crash.
- All human comments overlapped → `gap_count = 0`.
- Same comment counted once (no double insert on re-run).
- No completed runs → reports do not accidentally read a failed/partial run.
- Low-confidence/unjudged comments are counted and reported, not silently ignored.

### Observability
- INFO: gap_count, substantive_count, miss_rate at end of run.

### 🚦 Gate 4 — "End-to-end plumbing works (no LLM)"
- **Verify:** Full `analyzer run` on the real PR writes `runs/prs/comments/gaps/
  metrics`; `test_gaps.py` + `test_metrics.py` pass; metrics math hand-checked.
- **Proceed when:** a real run populates all tables and metrics are arithmetically
  correct under the "all-substantive" stub.

---

## Phase 5 — Reporting (`report/`) — *DESIGN §12.5*

### Steps
1. **Rich rendering.**
   - *Where:* `report/render.py` — `rich` tables for per-run metrics, top themes,
     and trend sparklines across runs (DESIGN §4).
   - *Why:* Inspect real data early; drives intuition before adding the LLM.
   - *Expected:* `analyzer report --run latest` prints a readable summary.
2. **Export formats.**
   - *Where:* `report/export.py` — markdown/JSON/CSV (markdown feeds the Actions
     issue body, DESIGN §11).
   - *Why:* The workflow posts a markdown summary; JSON/CSV for downstream tools.
   - *Expected:* `analyzer report --format markdown` emits valid markdown;
     `--format json` validates against a documented schema.
3. **CLI commands.**
   - *Where:* `cli.py` — `report`, `themes`, `trend` (DESIGN §10).
   - *Expected:* All three run against a populated DB.

### Tests to add
- `tests/test_export.py`: golden markdown/JSON snapshot for a seeded DB;
  `--run latest` resolves to the newest completed run id; output ordering is
  deterministic.

### Edge cases
- Empty DB / no runs → friendly "no data" message, exit 0.
- Trend with a single run → renders without sparkline error.
- Failed/partial runs are visible only when explicitly requested.
- Reports include data-quality counters: PRs skipped, comments truncated, comments
  unjudged, low-confidence comments, partial API errors, and pagination counts.

### Observability
- Report includes the **recall-is-relative caveat** text (DESIGN §9) so consumers
  never read `miss_rate` as absolute.

### 🚦 Gate 5 — "Operators can read results"
- **Verify:** `report`/`themes`/`trend` produce correct output on seeded data;
  export snapshots stable; caveat present.
- **Proceed when:** markdown export is good enough to paste into an issue.

---

## Phase 6 — LLM judge (`llm/judge.py`, `llm/prompts.py`) — *DESIGN §12.6*

### Steps
1. **Prompt templates.**
   - *Where:* `llm/prompts.py` — copy `JUDGE_SYSTEM`, `JUDGE_USER_TEMPLATE`,
     `COMMENT_ITEM_TEMPLATE` from DESIGN §8 verbatim.
   - *Why:* The prompts are the spec for "substantive / diff_detectable".
   - *Expected:* Templates render with sample comments.
2. **Hardened judge call.**
   - *Where:* `llm/judge.py` — GitHub Models endpoint
     `https://models.inference.ai.azure.com/chat/completions`,
     `Authorization: Bearer $GITHUB_TOKEN`, model from config, `temperature=0`,
     `response_format={"type":"json_object"}`. `json.loads` + **schema-validate**;
     batch ~10 comments/call; chunk under context; one corrective retry on
     malformed/missing ids, then mark `judge_confidence = NULL`, increment
     `unjudged_human_count`, and skip that comment (never crash the whole run) —
     all per DESIGN §8. If a configured maximum unjudged ratio is exceeded, mark
     the run `failed` so it is excluded from trends.
   - *Why:* LLM output is untrusted; the run must survive bad JSON.
   - *Expected:* Returns `[Judgement]`; injects `is_substantive`, `diff_detectable`,
     `category`, `judge_rationale`, `judge_confidence` into `comments`.
3. **Replace the Phase-4 stub.**
   - *Where:* `classify.py` calls the judge; `gaps.py` now uses real
     `is_substantive`/`diff_detectable`.
   - *Why:* Real classification turns plumbing into the actual product.
   - *Expected:* Gaps reflect genuine substantive+detectable+unoverlapped comments.
4. **`acted_on` linkage (deterministic).**
   - *Where:* `classify.py::acted_on(comment, commits)` — any commit to same `path`
     with `committedDate > comment.createdAt` (DESIGN §5/§8); document as soft.
     The existing GraphQL `changedFilesIfAvailable` count is not enough: add the
     required file-path source before implementing this metric (for example PR file
     pagination, commit-file REST calls, or another GraphQL shape that returns
     changed paths). If path data is unavailable, leave `acted_on = NULL` and
     report the metric as unavailable rather than guessing.
   - *Why:* Precision proxy `copilot_acted_on_rate` (DESIGN §9).
   - *Expected:* `acted_on` populated; documented as coarse.

### Tests to add
- `tests/test_judge.py`: **mock** the Models HTTP call — valid JSON parsed;
  malformed JSON → one retry → skip with NULL confidence (no crash); missing id
  handled; batching/chunking boundaries; excessive unjudged ratio marks the run
  failed/excluded.
- `tests/test_acted_on.py`: commit-after-comment true; commit-before false;
  different path false; unavailable path data yields NULL/unavailable, not false.
- Keep a **held-out benchmark PR set** with expected judgements for prompt
  regression (DESIGN §13).

### Edge cases
- Model returns extra/duplicate ids → ignore unknown, keep known.
- Comment body with code fences / huge diff hunk → truncation under token budget.
- Network failure mid-batch → batch retried, partial results preserved.
- Rate/usage limits on Models endpoint → backoff, surfaced in logs.
- Low-confidence judgements below `config.confidence_threshold` are excluded from
  final gap denominators and counted separately.
- Prompt/schema version is recorded with each run so benchmark changes are auditable.

### Observability
- Per-run: #comments judged, #skipped (NULL confidence), #retries, model name,
  token usage estimate, confidence-threshold exclusions, prompt/schema version;
  **never log full PR bodies at INFO** (privacy, DESIGN §13).

### 🚦 Gate 6 — "Judge is trustworthy & non-fatal"
- **Verify:** On a **small real batch**, judgements look sane; malformed-JSON
  test forces the skip path without crashing; benchmark set matches expected
  labels within tolerance.
- **Proceed when:** the run completes on real data with the LLM, bad output is
  survived, and benchmark regression is green.

---

## Phase 7 — Themes & final metrics (`themes.py`, `metrics.py`) — *DESIGN §12.7*

### Steps
1. **Theme tagging.**
   - *Where:* `themes.py` + `llm/judge.py`/shared `llm/client.py` — keep all model
     calls behind the `llm/` package even though this is a second LLM-assisted task.
     The theme classifier tags each gap into the controlled vocab from
     `config.yaml` using `THEME_SYSTEM`/`THEME_USER_TEMPLATE` (DESIGN §5/§8);
     unknown → `other`. Upsert `themes` and link `gaps.theme_id`.
   - *Why:* Trendable taxonomy is the product's headline output.
   - *Expected:* Each gap has exactly one theme; `themes.gap_count` aggregated.
2. **Finalize metrics.**
   - *Where:* `metrics.py` — all four DESIGN §9 formulas incl. real
     `copilot_acted_on_rate`.
   - *Why:* Complete the per-run time series.
   - *Expected:* `metrics` row fully populated; rates valid or NULL.

### Tests to add
- `tests/test_themes.py` (mocked LLM): label constrained to vocab; out-of-vocab
  coerced to `other`; `gap_count` aggregation correct.
- Extend `test_metrics.py` for `copilot_acted_on_rate`.

### Edge cases
- Zero gaps → no themes, metrics still write.
- Vocab change between runs → old runs unaffected (per-run `themes` rows).
- Theme LLM failure marks themes unavailable for that run without changing already
  computed gap metrics.

### Observability
- INFO: theme histogram (label → count) per run.

### 🚦 Gate 7 — "Trends are meaningful"
- **Verify:** `analyzer themes --min-count 2` and `trend --metric miss_rate`
  render across ≥2 runs; theme/metric tests green.
- **Proceed when:** multi-run trends render and all metrics are correct.

---

## Phase 8 — Scheduled workflow (`.github/workflows/analyze.yml`) — *DESIGN §12.8*

### Steps
1. **Workflow.**
   - *Where:* `.github/workflows/analyze.yml` — `schedule` (weekly) +
     `workflow_dispatch`; steps: checkout → setup-python → `pip install -e .` →
     `analyzer run --since 7d` → `analyzer report --format markdown > summary.md`
     → persist `analyzer.db` using the chosen strategy → open/update
     an issue with `summary.md` **and proposed prompt deltas for human approval**
     (DESIGN §11).
   - *Why:* Automate periodic mining; keep human-in-the-loop for prompt changes.
   - *Expected:* Manual `workflow_dispatch` produces an issue and persists the DB
      according to the selected strategy.
2. **Choose DB persistence before automating.**
   - *Where:* workflow design docs + `analyze.yml` — choose one strategy:
      artifact-only for audit snapshots, or a protected `data` branch/cache if
      cross-run trends must accumulate automatically.
   - *Why:* Trend correctness depends on durable DB continuity across weekly runs.
   - *Expected:* Manual and scheduled runs read/write the same intended history.
3. **Token wiring.**
   - *Where:* workflow env — `GITHUB_TOKEN` for repo data; PAT secret for
     cross-repo / higher Models limits (DESIGN §11).
   - *Expected:* Run authenticates without leaking the token to logs.

### Edge cases
- Empty window (no closed PRs) → run succeeds, issue notes "no new data".
- DB persistence strategy chosen (artifact vs `data` branch) and documented.
- Idempotent issue update (update existing weekly issue vs spam new ones).
- Workflow `permissions` explicitly allow only required scopes (`contents`,
  `issues`, `actions` artifacts as needed); forked PRs cannot exfiltrate tokens.
- Cross-repo reads and Models access fail with actionable errors when the token lacks
  permission.

### Observability
- Workflow summary surfaces metrics; artifact retains `analyzer.db` for audit.
- Workflow summary includes run status and data-quality counters so a green workflow
  with degraded analysis is obvious.

### 🚦 Gate 8 — "Hands-off weekly run"
- **Verify:** `workflow_dispatch` completes green; issue body + DB artifact
  correct; token never printed.
- **Proceed when:** one full automated run produces a correct summary issue.

---

## Phase 9 (optional) — Web viewer — *DESIGN §12.9 / §14*

### Steps
- **Where:** `datasette analyzer.db` for near-zero effort, or a small FastAPI app
  reading the same DB (DESIGN §14).
- **Why:** Always-on trend dashboard if leads want it; SQLite is the seam.
- **Expected:** Read-only views of runs/metrics/themes; no new write path.

### 🚦 Gate 9 — "Viewer is read-only & correct"
- **Verify:** Dashboard numbers match `analyzer report` for the same run.
- **Proceed when:** viewer agrees with the CLI (no divergent logic).

---

## Cross-cutting validation plan
- **Unit:** pure functions (`attribute`, `gaps`, `metrics`, parsers) — fast, offline.
- **Integration:** seeded SQLite + mocked HTTP (`pytest-httpx`) for `ingest` and
  `judge`; golden snapshots for `export`.
- **Contract:** parser tests pinned to recorded GraphQL fixtures; refresh fixtures
  when the GraphQL shape changes.
- **Regression:** held-out benchmark PR set for prompt changes (DESIGN §13) — run
  before/after any prompt edit; require label stability within tolerance.
- **Manual acceptance:** at each gate, hand-verify one real PR against GitHub.
- **Coverage target:** ≥90% on deterministic modules (`attribute/gaps/metrics/
  parsers`); LLM module covered via mocks (success + retry + skip paths).
- **Fixture safety:** recorded real responses must be scrubbed/anonymized before
  commit; prefer minimized fixtures that preserve GraphQL shape and edge cases.
- **Acceptance fixture set:** include PRs with outdated comments, renamed files,
  review replies, heavy pagination, closed-unmerged state, no Copilot comments, no
  human comments, and partial GraphQL errors.

## Observability summary
- Structured INFO logs per stage with counts (PRs, comments by kind, gaps, themes,
  retries, skips, unjudged/low-confidence comments, partial API errors, pagination
  counts) and `rateLimit` usage.
- `runs.config_hash` for reproducibility; `model` recorded per run (DESIGN §6).
- **Privacy:** aggregate themes only; do not grade individuals; never log full PR
  bodies; confirm Models policy before sending content (DESIGN §13).

## Risk-driven test checklist (from DESIGN §13)
- Recall-is-relative caveat rendered in every report.
- Attribution fuzziness → confidence threshold filter has a test.
- Goodhart/overfitting → automation only *proposes* prompt deltas (human approves).
- Cost/rate limits → `--max-prs`, batching, `temperature=0`, idempotent re-runs.
- `acted_on` false positives → documented soft signal, tested boundaries.
- LLM degradation → unjudged/low-confidence counters shown; excessive unjudged ratio
  fails/excludes the run rather than improving metrics silently.
- PR selection drift → tests lock merged/closed/window boundary semantics.
- Line-coordinate drift → tests cover current/original positions, renamed paths, and
  incomparable coordinates.
