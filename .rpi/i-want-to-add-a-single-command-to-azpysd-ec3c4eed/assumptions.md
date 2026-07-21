# Assumptions — local pre-push CI preflight (revised after rubber-duck review)

Task (refined): give developers a local command, runnable before pushing, that
runs the checks CI would run for their change (Python linting + cross-language
content gates like cspell/verify-links) so they can catch trivial failures
without spending a push+CI cycle.

A rubber-duck review corrected several earlier assumptions; this document
reflects the revised direction. Key verified correction: CI does NOT run the
Python checks as one combined `--checks=a,b,c` invocation — it calls
`dispatch_checks.py` once per check with per-check arguments (e.g. pylint and
black pass `--filter-type="Omit_management"`; mypy/bandit do not). Verified in
`eng/pipelines/templates/steps/run_pylint.yml`, `run_black.yml`, `run_mypy.yml`,
`run_bandit.yml`.

## Framing: preflight, not a CI oracle

- The contract is "local preflight for the SUPPORTED subset of PR gates", NOT "will my PR pass CI" | rationale: build/test matrices, indirect-package targeting, feed auth, proxy, and pipeline-only gates cannot be faithfully reproduced locally | confidence: high
- Result model is tri-state: PASS / FAIL / INCOMPLETE, never a bare boolean | rationale: a skipped/unreproducible gate must be visible, not folded into "pass" | confidence: high
- Output must explicitly list: passed, failed, skipped/incomplete, and known CI gates not reproducible locally | rationale: trust depends on disclosing coverage gaps | confidence: high

## Decided architecture (revised)

Prior plan proposed three layers (`azpysdk ci` + reuse + a separate
orchestrator). The review argues `azpysdk ci` adds policy duplication without
delivering the top-level goal. Revised stance:

1. Primary deliverable = ONE repo-owned orchestrator, e.g.
   `eng/scripts/verify_changes.py`, that shells out to grouped
   `dispatch_checks.py` invocations (Python) and per-gate adapters (content).
2. `azpysdk ci` is DEFERRED / optional. If built, it is a package-developer
   convenience for the Python analyze checks only and should probably be named
   for what it is (e.g. `azpysdk analyze`), because a Python-only `ci` is
   misleading. It is not required for the primary goal.
3. `eng/common` gate scripts and `dispatch_checks.py` are reused by INVOCATION
   only — never modified (eng/common is synced) and never imported as a library.

Format below: `- <assumption> | rationale: <why> | confidence: <high|medium|low>`.

## 1. The work item

- End goal: a local pre-push preflight that catches CI-gate failures early | rationale: user "tells us whether our PR will pass CI ... before we waste time pushing" | confidence: high
- azpysdk is NOT the home for non-Python gates | rationale: user agreed; azpysdk is Python/package-scoped by design | confidence: high
- Deliver a real script/command first; an agent-skill wrapper is optional and secondary | rationale: a script is deterministic, human-usable, testable; a skill only helps agent users | confidence: high
- `azpysdk ci` as a Python-only aggregator is optional and possibly out of scope for v1 | rationale: review — it duplicates selection policy without meeting the cross-language goal | confidence: medium
- NOT changing individual checks' logic or the Azure DevOps pipeline YAML | rationale: additive tooling | confidence: medium
- Priority/deadline/stakeholders unknown | rationale: not stated | confidence: high

## 2. Orchestrator design (primary deliverable)

- Lives in repo-owned `eng/scripts/` (e.g. `verify_changes.py`), NOT in `eng/common` and NOT inside azpysdk | rationale: `eng/common/README.md` forbids local edits; azpysdk stays Python-only | confidence: high
- Python checks are modeled as EXECUTION GROUPS, each with its exact CI arguments (e.g. filter-type), invoked as a SEPARATE `dispatch_checks.py` subprocess per group — not one combined comma list | rationale: verified per-check arg divergence in run_*.yml; one filter_type per dispatch invocation | confidence: high
- Content gates each get a small per-gate ADAPTER that reproduces the corresponding pipeline template's args/preprocessing — a generic "changed files → script" abstraction will not work | rationale: review — cspell computes its own 3-dot diff, Verify-Links needs URLs+cache/branch args, Verify-Readme needs package dirs + installs DocWarden from a feed, Verify-ChangeLogs needs generated PackageInfo JSON | confidence: high
- `dispatch_checks.py` is invoked as a SUBPROCESS, never imported | rationale: review + code — it owns argparse/`sys.exit`/signal handlers/asyncio/env mutation/cleanup globals and behaves differently under `in_ci()`; it can also rewrite `dev_requirements.txt` | confidence: high
- Two target notions maintained: a package set (Python checks) and a changed-file/dir set (content gates) | rationale: package-scoped vs file-scoped gates differ | confidence: high
- Runtime-selection flags: `--all` (default), `--python`, `--pwsh`; plus `--quick`/`--full` modes and a conservative concurrency default | rationale: user asked for python/pwsh selectors; review flags runtime blow-up (many checks × packages × per-package venvs, dispatch defaults to CPU-count parallelism) | confidence: medium
- Emits one aggregated tri-state verdict plus a per-gate summary and the executed plan | rationale: preflight framing + disclosure of coverage | confidence: high

## 3. Fidelity risks (highest-priority concern)

- Selection/argument DRIFT is the biggest risk and can stay invisible indefinitely | rationale: check selection+args already span analyze.yml/build-test.yml/set_checks.py; a second local list will silently diverge | confidence: high
- Environment differences (Azure Artifacts feed auth, prebuilt wheels, proxy/recording restore, caches, `in_ci()` branches) can flip local vs CI outcomes | rationale: review + Check.py `create_venv`/`in_ci` behavior | confidence: high
- Strongest mitigation: have CI invoke the SAME preflight execution plan for the supported subset, so local success predicts one named CI job rather than reverse-engineering all jobs | rationale: review; removes drift by construction | confidence: medium
- Minimum mitigation if CI is not wired to it: keep a single declarative execution plan, test it against expected CI check groups, print the plan + skipped coverage, and separate infra failures from check failures | rationale: review | confidence: medium

## 4. Missing-runtime behavior

- Missing required tooling (pwsh, Node/npx) yields INCOMPLETE + a DISTINCT nonzero exit (e.g. 2), NOT a silent skip-as-pass | rationale: review — silently skipping cspell hides exactly the trivial failure the tool exists to catch; the cspell script itself errors on missing npx | confidence: high
- Skipping a gate is allowed only via an explicit opt-out (e.g. `--allow-incomplete`) or by selecting a narrower mode (`--python`) | rationale: preserves signal integrity | confidence: medium

## 5. Diff detection & package targeting

- Default base = resolved MERGE-BASE with a configurable base ref; fail clearly (do not silently fall back to `origin/main..HEAD`) when it cannot be resolved | rationale: review — stale/fork `origin/main`, shallow clones missing merge base | confidence: high
- For a pre-push working-tree check, the changed set combines: committed changes since merge base + staged + unstaged + untracked non-ignored files | rationale: review — 3-dot `base...HEAD` omits working-tree work, the most common user surprise | confidence: high
- Print the chosen base SHA and full file list before running | rationale: transparency/debuggability | confidence: medium
- Deleted/renamed files need different handling than existing files | rationale: review; content gates may choke on missing paths | confidence: medium
- Package targeting must distinguish (1) changed services, (2) directly changed packages, (3) indirectly affected packages; `sdk/([^/]+)` only gives (1) | rationale: review — CI `TargetingString` derives from package-property artifacts and can include indirect packages, so a naive direct map under-runs vs CI | confidence: high
- Reuse CI package-resolution logic where practical, or build a tested equivalent, and disclose whether indirect expansion happened | rationale: review | confidence: medium
- Content gates that compute their own diff (cspell) must be given consistent refs so they check the same set the orchestrator reports | rationale: review — otherwise divergent file sets | confidence: medium

## 6. Feasibility tiering of non-Python (pwsh/Node) gates

Approach: per-gate adapter shelling out to the existing `eng/common` script.

Tier A — high feasibility:
- cspell — `check-spelling-in-changed-files.ps1`; computes its own changed-file diff; deps `pwsh`+Node/`npx`; config `.vscode/cspell.json` | confidence: high
- verify-links — `Verify-Links.ps1`; pure pwsh; needs URL list + optional cache/branch args | confidence: high
- verify-changelog — `Verify-ChangeLog.ps1`; pwsh; but `Verify-ChangeLogs` (plural, pipeline) expects generated PackageInfo JSON | confidence: medium

Tier B — medium (need arg construction, repo helpers, or feed installs):
- verify-readme (installs DocWarden from a feed), verify-codeowners/-sections, verify-samples, verify-path-length, verify-restapi-spec-location, verify-agent-os | confidence: medium

Tier C — low / not locally runnable (pipeline-only infra/services) — OUT of scope:
- create-apireview, detect-api-changes, validate-all-packages, policheck, 1ES publish | confidence: high

## 7. Constraints

- `eng/common` is synced from `azure-sdk-tools`; invoke, never edit | rationale: `eng/common/README.md` | confidence: high
- Content gates require `pwsh` (+ Node/npx for cspell), not guaranteed locally | rationale: `.ps1`/Node scripts; pipeline uses `pwsh:true` | confidence: high
- Some `eng/common` scripts default env vars to pipeline values (`SYSTEM_PULLREQUEST_*`, `BUILD_SOURCESDIRECTORY`); adapters must pass local equivalents | rationale: read from scripts | confidence: medium
- Linux dev env, Python 3.10+ | rationale: repo requirement | confidence: high
- No new third-party Python deps without justification | rationale: AGENTS.md convention | confidence: medium
- Backward compatibility: existing azpysdk subcommands and dispatch_checks/eng-common scripts unchanged | rationale: additive/reuse | confidence: high
- Runtime must stay tolerable or developers stop using it; needs conservative concurrency + quick/full modes | rationale: review | confidence: medium

## 8. Validation

- On a mixed change (sdk + docs), the orchestrator runs the right Python groups AND the content gates and reports a tri-state verdict with per-gate detail and disclosed non-reproducible gates | rationale: the core goal + preflight framing | confidence: medium
- Evidence: local run logs + unit tests for: diff/base-ref resolution (incl. working-tree + untracked), package targeting (direct + indirect), execution-plan/group selection matching CI args, and INCOMPLETE behavior when pwsh/Node absent | rationale: these are the drift/fidelity-critical paths | confidence: medium
- Existing protective test: `eng/tools/azure-sdk-tools/tests/test_dispatch_checks.py` | rationale: found in research | confidence: high

## 9. Open questions (non-blocking)

- Should CI be wired to invoke the same preflight execution plan (best anti-drift mitigation), or is the tool best-effort local-only for now?
- Which supported subset ships in v1 (Python groups + which Tier A/B content gates), and in what priority order?
- Is `azpysdk ci`/`azpysdk analyze` (Python-only aggregator) in scope at all, or fully deferred?
- Default base ref and merge-base resolution policy; behavior on shallow clones.
- For non-sdk changes, do content gates run on changed files, changed dirs, or repo-wide?
- How much CI package-resolution (indirect dependency expansion) do we replicate vs. approximate + disclose?
- Confirm: missing pwsh/Node ⇒ INCOMPLETE+nonzero by default (assumed), with explicit opt-out.
- Deliver the agent-skill wrapper now or later?

## Out-of-scope observations (not part of this work item)

- The "CI check set" and its per-check args are spread across `analyze.yml`, `build-test.yml`, and `set_checks.py` with no single source of truth; this is the root cause of the drift risk and a candidate for future consolidation.
- Content/spell/link verification living only in PowerShell/Node (outside the Python tooling) is a general cross-language gap independent of this task.
