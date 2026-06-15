-- Schema v1 for the Copilot Code-Review Effectiveness Analyzer.
-- Base tables from DESIGN §6 plus implementation-required integrity fields
-- (see IMPLEMENTATION_PLAN Phase 1).

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
    model         TEXT    NOT NULL,
    config_hash   TEXT,
    status        TEXT    NOT NULL DEFAULT 'started',  -- started | completed | failed
    error_summary TEXT
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
    external_id     INTEGER,                    -- GitHub databaseId (may be NULL)
    source_key      TEXT    NOT NULL,           -- stable dedup key (fallback when databaseId missing)
    author          TEXT,
    author_kind     TEXT    NOT NULL,           -- human | copilot | other_bot
    is_review_body  INTEGER NOT NULL DEFAULT 0, -- 1 = top-level review summary
    file_path       TEXT,
    line_start      INTEGER,
    line_end        INTEGER,
    coord_space     TEXT,                       -- current | original (line coordinate origin)
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

    UNIQUE (run_id, source_key)
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
    theme_id    INTEGER REFERENCES themes(id) ON DELETE SET NULL,
    UNIQUE (run_id, comment_id)
);

CREATE TABLE IF NOT EXISTS metrics (
    run_id                    INTEGER PRIMARY KEY REFERENCES runs(id) ON DELETE CASCADE,
    substantive_human_count   INTEGER NOT NULL DEFAULT 0,
    copilot_comment_count     INTEGER NOT NULL DEFAULT 0,
    gap_count                 INTEGER NOT NULL DEFAULT 0,
    judged_human_count        INTEGER NOT NULL DEFAULT 0,
    unjudged_human_count      INTEGER NOT NULL DEFAULT 0,
    low_confidence_human_count INTEGER NOT NULL DEFAULT 0,
    miss_rate                 REAL,
    copilot_overlap_rate      REAL,
    copilot_acted_on_rate     REAL,
    human_burden_per_pr       REAL
);

-- Per-gap prompt-improvement suggestions (schema v2; populated by `suggest-prompts`).
-- One row per gap: a PR-specific finding for what the Copilot reviewer missed there,
-- plus a generalizable idea for improving the review prompt to catch it next time.
CREATE TABLE IF NOT EXISTS gap_suggestions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id             INTEGER NOT NULL REFERENCES runs(id)  ON DELETE CASCADE,
    gap_id             INTEGER NOT NULL REFERENCES gaps(id)  ON DELETE CASCADE,
    comment_id         INTEGER NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    missed_finding     TEXT,                   -- specific: what Copilot missed in this PR
    prompt_improvement TEXT,                   -- generalizable prompt guidance
    created_at         TEXT,
    UNIQUE (run_id, gap_id)
);

CREATE INDEX IF NOT EXISTS idx_comments_run     ON comments(run_id);
CREATE INDEX IF NOT EXISTS idx_comments_kind    ON comments(run_id, author_kind);
CREATE INDEX IF NOT EXISTS idx_comments_pr      ON comments(pr_id);
CREATE INDEX IF NOT EXISTS idx_gaps_run         ON gaps(run_id);
CREATE INDEX IF NOT EXISTS idx_themes_run       ON themes(run_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_run  ON gap_suggestions(run_id);
