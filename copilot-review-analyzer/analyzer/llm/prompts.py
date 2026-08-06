"""LLM judge and theme prompt templates (verbatim from DESIGN §8)."""

from __future__ import annotations

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

SUGGEST_SYSTEM = """\
You improve an automated code-reviewer (a "Copilot reviewer") by learning from issues \
it MISSED. For each gap below — a substantive, diff-detectable problem a human reviewer \
caught but the Copilot reviewer did not — produce two things:

1. "missed_finding": a precise, concrete description of exactly what the Copilot \
reviewer should have flagged in THIS diff, grounded only in the visible code. Name the \
specific construct/line/risk. No generic advice here.
2. "prompt_improvement": a single, GENERALIZABLE instruction that could be added to the \
Copilot reviewer's system prompt so it would catch this class of issue in future PRs. \
Phrase it as a reusable review rule, not tied to this PR's specifics. Imperative voice, \
one sentence (e.g. "Flag any redirect target that is not validated against an allowlist.").

Judge ONLY from the provided diff and comment. Return STRICT JSON only, no prose."""

SUGGEST_USER_TEMPLATE = """\
For each gap return a JSON object:
{{"results": [{{"id": <int>, "missed_finding": <str>, "prompt_improvement": <str>}}]}}

Gaps the Copilot reviewer missed:
{gaps_block}"""

SUGGEST_ITEM_TEMPLATE = """\
--- GAP id={id} ---
Category: {category}  Theme: {theme}
File: {file_path}  Lines: {line_start}-{line_end}
Diff hunk:
```
{diff_hunk}
```
What the human reviewer said:
\"\"\"{body}\"\"\"
Why it matters (judge note): {rationale}
"""
