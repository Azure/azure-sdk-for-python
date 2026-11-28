---
name: code-review
description: "Review pull requests and code changes in the Azure SDK for Python repository. USE FOR: GitHub Copilot code review; CCR; review pull request; review PR; review diff; find bugs or regressions introduced by a PR; cross-package SDK review. Finds high-confidence correctness, security, API compatibility, dependency, documentation, and test issues. DO NOT USE FOR: implementing fixes; running tests; fixing CI; releases; APIView feedback."
---

# Azure SDK for Python Code Review

Use this skill for GitHub Copilot code review (CCR) and other broad pull request reviews. If the task already assigns a narrower specialist role, that scope remains authoritative; use this skill's evidence and quality gates without expanding the specialist review.

## Review Process

1. Read the pull request description and identify the intended behavior.
2. Categorize the changed files and apply only the relevant guidance below.
3. Review correctness and behavioral regressions first, then apply the relevant SDK-specific checks.
4. Trace changes through callers, exports, tests, API reports, documentation, and package metadata when those relationships affect correctness.
5. Inspect enough unchanged context to verify existing guards, invariants, and behavior before reporting a finding.

For changes outside `sdk/`, review correctness, security, and test coverage
without imposing SDK-specific conventions.

## Load Guidance Progressively

| Changed surface or risk | Guidance |
| --- | --- |
| SDK source or public API | `.github/instructions/reviewer/sdk-source.instructions.md` and the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html) |
| Tests or coverage implications | `.github/instructions/reviewer/testing.instructions.md` |
| README, CHANGELOG, docstrings, or samples | `.github/instructions/reviewer/documentation.instructions.md` |
| Packaging or dependencies | `.github/instructions/reviewer/dependencies.instructions.md` |
| `sdk/*/azure-mgmt-*/` | `.github/instructions/reviewer/management.instructions.md` |

Management-specific review scope and rules take precedence over generic SDK
guidance: skip `generated_samples/` and `generated_tests/`, and review only
`_client.py` under `azure/mgmt/**/`. Read metadata and documentation needed to
check the management rules. Do not apply the JavaScript repo's TypeScript,
pnpm, or API-report conventions to Python packages.

Generated output is usually not the fix location: identify the actionable
TypeSpec, customization, or generator cause when evidence supports it. Do not
speculate about the upstream fix or mistake a preview-only API change for a
breaking change in a released stable API.

## Findings

- Report actionable, high-confidence issues with changed file/line, the
  observed behavior, the scenario in which it fails, and a concrete remedy.
- Prioritize correctness, compatibility, and security over stylistic
  preferences. Do not claim a tool or test failure without running it.
- Do not duplicate the same root cause across multiple files. If evidence is
  incomplete, state what could not be verified instead of guessing.
- If there are no findings, say so briefly; do not pad the review with passing
  checks or generic suggestions.
