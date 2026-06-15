# Copilot Code-Review Effectiveness Analyzer — Design & Plan

## 1. Goal
Periodically mine recently closed/merged PRs, separate Copilot-reviewer comments
from human comments, use an LLM judge to find **substantive, diff-detectable
issues that humans caught but Copilot missed**, cluster those into **themes**, and
track **miss-rate / precision metrics** over time. The output feeds prompt
improvements for the Copilot reviewer — proposed automatically, approved by a human.

## 2. Tech stack
- **Language:** Python 3.10+
- **GitHub access:** GraphQL (one query per PR for reviews + threads + commits) via
  `httpx`; auth from `GH_TOKEN` / `gh auth token`.
- **LLM judge:** GitHub Models (`https://models.inference.ai.azure.com`,
  OpenAI-compatible), same token.
- **Storage:** SQLite (`stdlib sqlite3`).
- **CLI:** `typer` (or `argparse`); report rendering with `rich`.
- **Optional web viewer (later):** `datasette analyzer.db` for zero-effort, or a
  small FastAPI app reading the same DB.

## 3. Pipeline architecture (5 stages)
```
[1 Ingest] -> [2 Attribute] -> [3 Classify] -> [4 Gap/Theme] -> [5 Store] -> [Viewer]
```

1. **Ingest** — enumerate PRs in a date/state window, then per-PR GraphQL fetch of
   metadata, diff hunks, review threads (file+line), top-level reviews, and the
   commit timeline.
2. **Attribute** (deterministic, no LLM) — tag each comment author as
   `copilot` / `human` / `other_bot`; map comments to `(file, line_range)`.
3. **Classify** (LLM judge, the only LLM step) — per human comment:
   `is_substantive`, `diff_detectable`, `category`, `confidence`. Independently,
   compute `acted_on` from the commit timeline (deterministic).
4. **Gap & theme detection** — a **gap** = substantive + diff_detectable + no
   Copilot comment overlapping the same file/lines. Cluster gaps into **themes**
   via a controlled vocabulary.
5. **Store** — write to SQLite; compute per-run metrics.

## 4. File layout
```
copilot-review-analyzer/
├── pyproject.toml
├── README.md
├── DESIGN.md                    # this file
├── config.yaml                  # repos, bot logins, model, sampling, theme vocab
├── analyzer/
│   ├── __init__.py
│   ├── cli.py                   # entrypoints: run, report, themes, trend, init-db
│   ├── config.py                # load/validate config.yaml -> dataclass
│   ├── github/
│   │   ├── client.py            # httpx GraphQL/REST client, auth, pagination, retry
│   │   └── queries.py           # GraphQL query strings + response parsers
│   ├── pipeline/
│   │   ├── ingest.py            # Stage 1
│   │   ├── attribute.py         # Stage 2: author_kind, line-range mapping, overlap
│   │   ├── classify.py          # Stage 3: LLM judge + acted_on linkage
│   │   ├── gaps.py              # Stage 4a: gap detection
│   │   ├── themes.py            # Stage 4b: controlled-vocab tagging
│   │   └── metrics.py           # Stage 5: per-run metrics
│   ├── llm/
│   │   ├── judge.py             # GitHub Models call, batching, JSON validation
│   │   └── prompts.py           # judge + theme prompt templates
│   ├── store/
│   │   ├── schema.sql           # tables (see §6)
│   │   └── db.py                # connection, migrations, typed upserts/queries
│   └── report/
│       ├── render.py            # rich tables, trend sparklines, theme summaries
│       └── export.py            # JSON/CSV/markdown export for the Actions issue body
├── tests/
│   ├── fixtures/                # recorded GraphQL responses, sample diffs
│   ├── test_attribute.py
│   ├── test_gaps.py
│   └── test_metrics.py
└── .github/workflows/
    └── analyze.yml              # weekly cron: run + export + open summary issue
```

## 5. Module contracts (key)
- `github/queries.py` — per-PR GraphQL (see §7); page `reviewThreads` & `commits`.
- `pipeline/attribute.py` — pure functions:
  - `classify_author(login) -> "copilot" | "human" | "other_bot"` using
    `config.copilot_logins` + `login.endswith("[bot]")` heuristic.
  - `overlaps(human_range, copilot_ranges) -> bool` — same file, intersecting line
    ranges (±N line fuzz, configurable).
- `pipeline/classify.py`:
  - `judge_comments(human_comments, diff) -> [Judgement]` (batched).
  - `acted_on(comment, commits) -> bool` — any commit to same `path` with
    `committedDate > comment.createdAt` (coarse; documented soft signal).
- `pipeline/gaps.py`: `gap = is_substantive and diff_detectable and not copilot_overlap`.
- `pipeline/themes.py`: LLM tags each gap into a controlled vocabulary from
  `config.yaml` (`null-handling`, `error-handling`, `test-coverage`, `security`,
  `api-design`, `concurrency`, `perf`, `docs`, ... + `other`).

## 6. SQLite schema (`analyzer/store/schema.sql`)
```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    repo          TEXT    NOT NULL,
    started_at    TEXT    NOT NULL,             -- ISO8601
    finished_at   TEXT,
    window_start  TEXT    NOT NULL,
    window_end    TEXT    NOT NULL,
    pr_state      TEXT    NOT NULL,             -- merged | closed | all
    pr_count      INTEGER NOT NULL DEFAULT 0,
    model         TEXT    NOT NULL,             -- e.g. github-models/gpt-4o
    config_hash   TEXT                          -- for reproducibility
);

CREATE TABLE IF NOT EXISTS prs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    number      INTEGER NOT NULL,
    title       TEXT,
    author      TEXT,
    state       TEXT,
    url         TEXT,
    created_at  TEXT,
    merged_at   TEXT,
    closed_at   TEXT,
    additions   INTEGER,
    deletions   INTEGER,
    UNIQUE (run_id, number)
);

CREATE TABLE IF NOT EXISTS comments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    pr_id           INTEGER NOT NULL REFERENCES prs(id)  ON DELETE CASCADE,
    external_id     INTEGER,                    -- GitHub databaseId
    author          TEXT,
    author_kind     TEXT    NOT NULL,           -- human | copilot | other_bot
    is_review_body  INTEGER NOT NULL DEFAULT 0, -- 1 = top-level review summary
    file_path       TEXT,
    line_start      INTEGER,
    line_end        INTEGER,
    body            TEXT,
    diff_hunk       TEXT,
    created_at      TEXT,
    url             TEXT,

    -- Stage 3 (LLM judge); NULL until classified
    is_substantive    INTEGER,
    diff_detectable   INTEGER,
    category          TEXT,
    judge_rationale   TEXT,
    judge_confidence  REAL,

    -- Deterministic enrichments
    acted_on          INTEGER,                  -- commit to same path after comment
    copilot_overlap   INTEGER,                  -- human comment overlapped by Copilot

    UNIQUE (run_id, external_id)
);

CREATE TABLE IF NOT EXISTS themes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id        INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    label         TEXT    NOT NULL,             -- controlled vocab term
    description   TEXT,
    gap_count     INTEGER NOT NULL DEFAULT 0,
    UNIQUE (run_id, label)
);

CREATE TABLE IF NOT EXISTS gaps (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    pr_id       INTEGER NOT NULL REFERENCES prs(id)  ON DELETE CASCADE,
    comment_id  INTEGER NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    category    TEXT,
    theme_id    INTEGER REFERENCES themes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS metrics (
    run_id                  INTEGER PRIMARY KEY REFERENCES runs(id) ON DELETE CASCADE,
    substantive_human_count INTEGER NOT NULL DEFAULT 0,
    copilot_comment_count   INTEGER NOT NULL DEFAULT 0,
    gap_count               INTEGER NOT NULL DEFAULT 0,
    miss_rate               REAL,
    copilot_overlap_rate    REAL,
    copilot_acted_on_rate   REAL,
    human_burden_per_pr     REAL
);

CREATE INDEX IF NOT EXISTS idx_comments_run     ON comments(run_id);
CREATE INDEX IF NOT EXISTS idx_comments_kind    ON comments(run_id, author_kind);
CREATE INDEX IF NOT EXISTS idx_comments_pr      ON comments(pr_id);
CREATE INDEX IF NOT EXISTS idx_gaps_run         ON gaps(run_id);
CREATE INDEX IF NOT EXISTS idx_themes_run       ON themes(run_id);
```

## 7. GraphQL query (`analyzer/github/queries.py`)
```graphql
query PRReviewData(
  $owner: String!
  $name: String!
  $number: Int!
  $threadsAfter: String
  $commitsAfter: String
) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      number
      title
      state
      url
      createdAt
      mergedAt
      closedAt
      additions
      deletions
      author { login }

      reviewThreads(first: 50, after: $threadsAfter) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved
          isOutdated
          path
          line
          originalLine
          startLine
          originalStartLine
          comments(first: 50) {
            nodes {
              databaseId
              author { login }
              authorAssociation
              body
              createdAt
              url
              diffHunk
            }
          }
        }
      }

      reviews(first: 50) {
        nodes {
          databaseId
          author { login }
          state
          body
          submittedAt
          url
        }
      }

      commits(first: 100, after: $commitsAfter) {
        pageInfo { hasNextPage endCursor }
        nodes {
          commit {
            oid
            committedDate
            changedFilesIfAvailable
          }
        }
      }
    }
  }
  rateLimit { remaining resetAt cost }
}
```

**Parser notes**
- Enumerate PR numbers first via REST `GET /repos/{o}/{r}/pulls?state=closed&sort=updated`
  or the search API, then call this query per PR.
- Thread range = `(path, startLine|originalStartLine .. line|originalLine)`; fall back
  to `originalLine` when `line` is null (outdated threads).
- The thread's **first comment** is the review point; replies are conversation.
- Page `reviewThreads` and `commits` via `pageInfo.endCursor` until `hasNextPage=false`.
- Use `rateLimit.cost` to throttle proactively.

## 8. LLM judge & theme prompts (`analyzer/llm/prompts.py`)
```python
JUDGE_SYSTEM = """\
You are an expert software code reviewer evaluating the review comments left on \
a pull request. Your job is to classify each human review comment objectively.

Rules:
- Judge ONLY from the information visible in the provided diff hunk(s). Do NOT \
assume external context (chat, issues, runtime behavior, tribal knowledge).
- "substantive" means the comment identifies a real code-quality issue: a bug, \
security flaw, performance problem, design/API concern, or a missing test. \
Style nitpicks, typos, praise, questions, and process/social chatter are NOT \
substantive.
- "diff_detectable" means a competent automated reviewer could plausibly raise \
this issue from the diff alone, without external context.
- Be conservative: if a comment relies on knowledge not present in the diff, set \
diff_detectable = false.

Return STRICT JSON only, matching the schema. No prose, no markdown."""

JUDGE_USER_TEMPLATE = """\
Classify each comment below. Return a JSON object:
{{"results": [{{"id": <int>, "is_substantive": <bool>, "category": <str>, \
"diff_detectable": <bool>, "rationale": <str, one sentence>, \
"confidence": <float 0..1>}}]}}

"category" must be exactly one of:
["bug", "security", "perf", "design", "test-gap", "docs", "nit", "style", \
"question", "social"].

Comments to classify:
{comments_block}"""

COMMENT_ITEM_TEMPLATE = """\
--- COMMENT id={id} ---
File: {file_path}  Lines: {line_start}-{line_end}
Diff hunk:
```
{diff_hunk}
```
Reviewer comment:
\"\"\"{body}\"\"\"
"""

THEME_SYSTEM = """\
You map code-review issues to a fixed taxonomy of recurring themes so they can \
be trended over time. Use ONLY labels from the provided vocabulary; if none fit, \
use "other". Return strict JSON."""

THEME_USER_TEMPLATE = """\
Allowed theme labels: {vocab}

For each gap, assign exactly one label. Return:
{{"results": [{{"id": <int>, "theme": <label>, "why": <str, one sentence>}}]}}

Gaps:
{gaps_block}"""
```

**Judge-call hardening (`judge.py`)**
- `temperature=0`, `response_format={"type": "json_object"}`; still `json.loads` +
  schema-validate.
- On malformed/missing ids: one retry with a corrective nudge, then mark those
  comments `judge_confidence = NULL` and skip (never crash the run).
- Batch ~10 comments/call; chunk so total tokens stay well under the model context.
- Endpoint `https://models.inference.ai.azure.com/chat/completions`,
  header `Authorization: Bearer $GITHUB_TOKEN`, model from `config.yaml`.

## 9. Metrics (formulas)
- **miss_rate** = `gaps / substantive_diff_detectable_human_comments` (primary recall proxy)
- **copilot_acted_on_rate** = `acted_on_copilot_comments / total_copilot_comments` (precision proxy)
- **copilot_overlap_rate** = `human_comments_with_copilot_overlap / substantive_human_comments`
- **human_burden_per_pr** = `substantive_human_comments / pr_count` (trend down = success)
- One `metrics` row per run → everything is a time series.

> Caveat to document: recall is **relative to what humans caught**, not ground truth.
> Never present miss_rate as an absolute. Track precision and recall separately.

## 10. CLI surface
```
analyzer init-db
analyzer run --repo owner/name --since 7d [--state merged] [--max-prs 50] [--dry-run]
analyzer report [--run latest] [--format table|markdown|json]
analyzer themes [--run latest] [--min-count 2]
analyzer trend --metric miss_rate
```

## 11. Periodic execution (`.github/workflows/analyze.yml`)
- `on: schedule` (weekly cron) + `workflow_dispatch`.
- Steps: checkout → setup-python → `pip install -e .` → `analyzer run --since 7d` →
  `analyzer report --format markdown > summary.md` → upload `analyzer.db` artifact
  (or commit to a `data` branch) → open/update an issue with `summary.md` and
  **proposed prompt deltas for human approval**.
- Token: `GITHUB_TOKEN` for repo data; a PAT secret for cross-repo or higher Models limits.

## 12. Implementation order (de-risked)
1. `store/` schema + `db.py` (+ `init-db`).
2. `github/` ingest one PR end-to-end → dump raw JSON. Verify against a real PR.
3. `attribute.py` + tests (pure, fast).
4. `gaps.py` overlap logic + tests (no LLM yet — treat all human comments as
   substantive to validate plumbing).
5. `report/render.py` — see tables from real data early.
6. `llm/judge.py` against GitHub Models on a small batch; validate JSON.
7. `themes.py` + `metrics.py`.
8. `analyze.yml` scheduled workflow.
9. (Optional) `datasette` / FastAPI web viewer over the same DB.

## 13. Risks & mitigations
- **Recall is relative, not absolute** — issues nobody commented on are invisible.
  Frame metrics as "relative to humans".
- **Attribution fuzziness** — keep `rationale` + `confidence`; report filters by a
  confidence threshold.
- **Prompt overfitting / Goodhart** — automation only *proposes* prompt deltas; a
  human approves. Keep a held-out benchmark PR set to regression-test prompt changes.
- **Cost / rate limits** — sampling (`--max-prs`), batching, `temperature=0`,
  idempotent re-runs (`UNIQUE (run_id, external_id)`).
- **`acted_on` false positives** — coarse signal; document and treat as soft.
- **Privacy** — aggregate themes only; do not grade individual reviewers. Confirm
  sending PR content to GitHub Models is within policy.

## 14. Viewer decision
SQLite is the seam. Ship the **CLI** first (fast, reuses `gh` auth, easy in Actions).
Add a **lightweight web dashboard** later that reads the same DB — `datasette` for
near-zero effort, or a small FastAPI + charts page if leads need always-on trends.
