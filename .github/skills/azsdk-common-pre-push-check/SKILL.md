---
name: azsdk-common-pre-push-check
description: 'Run locally available CI static checks before publishing changes, including documentation and non-SDK tools. WHEN: "pre-push checks", "validate changes before pushing", "check spelling and links", "run local static checks", "ready to push".'
license: MIT
metadata:
  version: "1.0.0"
  distribution: shared
compatibility: "Git, repository check prerequisites; PowerShell and Node.js for shared checks"
---

# Pre-push Checks

Run this workflow before pushing or publishing changed files, including through an agent's commit/push tool. Documentation-only and non-SDK changes are not exempt.

1. **Scope** — Locate the repository root and PR target branch. Verify the base ref exists; fetch missing history if permitted, otherwise report validation as blocked. Include the whole branch diff from the merge base, staged and unstaged changes, and untracked non-ignored files. Exclude deleted files; retain rename destinations. Never substitute only the latest commit or assume `origin/main`.
2. **Discover** — Read repository instructions, applicable CI workflows/templates, and affected projects' manifests. Identify existing spelling, link, formatting, lint, and type-check commands and their prerequisites/configuration. Follow the [check guide](references/checks.md). SDK package checks alone do not cover docs or tooling.
3. **Run** — Execute every applicable locally runnable static check against the current files, using CI's versions, configuration, and ignore lists. Scope to changed files where supported, otherwise check the affected project. Do not run remote pipelines, publish packages, install hooks, or regenerate SDKs as part of this workflow.
4. **Resolve** — Fix failures caused by these changes and rerun affected checks. Do not disable checks, broaden ignore lists, or weaken rules to obtain a pass. After any further edits, rerun the affected checks before publishing.
5. **Gate** — Report each check's exact command, scope, exit code, and result: passed, failed, blocked, or not applicable with a reason. Missing prerequisites, network failures, and unavailable base history are **blocked**, not passed. Do not push with failed or blocked required checks; report the blocker and ask the user how to proceed. If no checks apply, explain why.

This is an agent validation gate, not an installed Git hook. It does not replace CI, builds, or behavioral tests.
