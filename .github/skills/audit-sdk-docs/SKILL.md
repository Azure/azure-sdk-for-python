---
name: audit-sdk-docs
description: Use when the user wants to audit this repo's documentation and code annotations so agents get accurate, current, non-redundant info. Covers stale references (broken links / dead URLs / missing paths), code annotations that no longer match the code, duplicated or contradictory docs about the same concept, and doc simplification. Skips the auto-generated sdk/ folder and centrally-synced eng/common. Triggers on "check docs", "audit documentation", "delete/update outdated docs", "keep docs up to date", "docs don't match code".
---

# Audit SDK Docs

Audit the documentation **and code annotations** of the Azure SDK for Python repo
so that agents reading repo docs (`AGENTS.md`, `.github/copilot-instructions.md`,
`.github/skills/`, `doc/dev/`, docstrings, ...) get accurate, current, and
non-redundant information. Better docs => higher agent task-success rate (#48112).

This skill is **agent-maintained and self-improving**: the final step of every run
is to reflect on what worked, and fold any reusable pattern back into this skill
(see [Step 6](#step-6---self-improve-mandatory)).

## Global rules

- **SKIP the `sdk/` folder** - auto-generated; its docs/annotations are not
  hand-maintained. The scanner excludes it by default.
- **Do NOT edit `eng/common*`** - centrally synced from `azure-sdk-tools` and
  overwritten by automation. The scanner excludes it.
- **DO NOT edit too many files at one time.** Fix the highest-confidence items in
  a small batch; report the rest as follow-ups rather than mass-editing.
- **Every candidate needs agent judgement.** Tools surface *candidates*, not
  confirmed bugs. Legitimate, leave-alone cases include placeholders
  (`sdk/mypackage/...`), generated paths (`conda/noarch`), gitignored user files
  (`testsettings_local.cfg`), code-snippet regex noise (`{{`, `or`), and
  **historical references** - a path introduced with wording like "Previously in",
  "formerly at", "moved from", or "deprecated path" is describing history on
  purpose, so leave it even though the target no longer exists.
- **Preserve meaning.** When simplifying or de-duplicating, never drop information;
  consolidate it into a single source of truth and link to it.

## Audit dimensions

Run the dimensions that fit the request. Each is a separate concern; do them as
separate small batches, not one giant edit.

### Dimension 1 - Stale references (automated)

Broken relative links, dead in-repo GitHub URLs, and inline path refs that no
longer exist. Run the bundled read-only scanner (audits the repo it lives in):

```
python .github/skills/audit-sdk-docs/scripts/check_outdated_docs.py
```

Scans root `*.md`/`*.rst` + `doc/` + `eng/` (excluding `sdk/`, `eng/common*`,
`node_modules`). Options: `REPO_ROOT` positional, `--scan-dir DIR` (repeatable),
`--include-sdk`, `--org`/`--repo`. Output groups: `BROKEN_RELATIVE_LINK`,
`DEAD_REPO_URL`, `MISSING_PATH_REF`. For each real hit, find where the target
*moved to* (`grep` the symbol/filename, `git log -- <old-path>`) before editing.

### Dimension 2 - Annotation vs code drift

Check that code annotations describe the real code (focus on hand-maintained
tooling under `eng/`, `scripts/`, `tools/`; skip auto-generated `sdk/`).
Method (agent-driven; verify each candidate against the actual code):

- **Docstring params vs signature.** For a documented function, compare the params
  named in the docstring (`:param x:`, `Args:`) against the real signature; flag
  removed/renamed/added params.
- **Referenced symbols exist.** `grep` for class/function/module names mentioned in
  docstrings and doc prose; flag ones that no longer exist.
- **Runnable examples.** Import/run code snippets and `>>> doctest` examples where
  cheap; flag imports/attribute paths that fail.
- **CLI help drift.** When a doc quotes a command's flags/output, run the tool's
  `--help` and diff; flag divergence (e.g. `azpysdk`, `sdk_build_conda`).
- **Type-hint claims.** When prose states a return/param type, confirm against the
  annotation.

Prefer `grep`/`git log`/running the tool over guessing. Fix by correcting the
annotation to match the code (do **not** change working code to match a stale
comment unless the code is the bug).

### Dimension 3 - Duplicated or contradictory docs

Find the same concept documented in multiple places that have drifted apart.
Method:

- **Build a concept index.** For a topic (a command, config key, env var, pipeline
  id, path), `grep -rn` it across all in-scope docs to list every doc that covers
  it.
- **Duplication.** Multiple docs explaining the same procedure => pick a single
  source of truth, keep the fullest/most-correct copy, and replace the others with
  a link to it.
- **Contradiction.** Same command/flag/config with **different values** across docs
  (e.g. two different pipeline `definitionId`s, differing env-var names, conflicting
  steps) => determine the correct one from the code/pipeline, fix all copies (or
  consolidate), and note which was authoritative.

### Dimension 4 - Simplification

Where a doc is redundant, stale-by-accretion, or needlessly long:

- Remove dead sections describing removed features (verify removal first).
- Collapse duplicated prose into the single source of truth from Dimension 3.
- Tighten wording without dropping any real instruction or caveat.

Keep edits surgical and review with `git diff` before committing.

## Workflow

1. **Scope.** Decide which dimensions apply to the request.
2. **Detect.** Run the scanner (D1) and/or the grep/index methods (D2-D4) to gather
   candidates.
3. **Judge.** Read each candidate in context; discard legitimate cases per the
   global rules.
4. **Fix a small batch.** Update/delete/consolidate. Verify moved targets first.
5. **Verify.** Re-run the scanner, re-run any affected examples/`--help`, and show
   `git diff` of edited docs. Confirm no new candidates were introduced.
6. **Self-improve (see below).**
7. **Report.** Summarize fixes by dimension and list follow-ups (and why they were
   left).

### Step 6 - Self-improve (MANDATORY)

Before finishing, **review the process you just ran** and ask: did I discover a
reusable pattern or solution that isn't yet captured here? For example: a new
staleness class worth adding to the scanner, a reliable heuristic for detecting a
contradiction, a grep recipe for a concept index, a known false-positive to
whitelist, or a moved-file mapping worth recording.

If yes:
- Update this `SKILL.md` (and/or extend `scripts/check_outdated_docs.py`) with the
  new pattern/solution.
- **Commit the skill change in the SAME PR** as the doc fixes, so the skill gets
  better every time it is used.

If nothing new was learned, state that explicitly in the report and skip the edit.

## Example findings (run relating to #48112)

- `doc/dev/conda-builds.md`: `eng/conda_env.yml` -> `conda/conda-recipes/conda_env.yml`
  (moved in #31804; verified via `eng/tools/azure-sdk-tools/ci_tools/conda/conda_functions.py`
  `get_version_from_config`). *(Dimension 1)*
- `doc/dev/mgmt/tests.md`: sample `conftest.py` link pointed at the removed
  `sdk/advisor/azure-mgmt-advisor/tests/` folder; repointed to
  `sdk/apimanagement/azure-mgmt-apimanagement/tests/conftest.py`. *(Dimension 1)*
- `doc/dev/conda-builds.md`: its "CI Build Process" bullets duplicated and partly
  contradicted (manual version bump) the now-authoritative, largely-automated
  process in `conda-release.md`; consolidated to a pointer, keeping this page
  focused on local builds. *(Dimensions 3 + 4)*
- `sdk_build_conda` flags (`-c/--config`, `--channel`) in `conda-builds.md`
  verified against `ci_tools/conda/conda_functions.py` argparse - accurate, no
  change. *(Dimension 2, no fix)*
