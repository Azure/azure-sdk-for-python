---
name: azure-ai-evaluation
description: 'Guide safe, evidence-based azure-ai-evaluation releases. WHEN: prepare azure-ai-evaluation release; check azure-ai-evaluation release readiness; diagnose skipped azure-ai-evaluation release; review azure-ai-evaluation next-version PR; plan azure-ai-evaluation hotfix. Not for SDK regeneration.'
---

# Evaluation release checklist

Complements `azsdk-common-sdk-release`; does not authorize publication. Read [release artifacts and sources](references/customizations.md) first. Follow repository setup verification before SDK MCP operations.

1. **Prepare:** [Inspect main, PyPI, changes and Chronus](references/preparation.md). Agree on classification/date. Obtain authorization for the script's DevOps write; verify version, notes and tracking independently.
2. **Review:** Follow [approvals and pipeline](references/approvals-and-pipeline.md) for the draft PR and release-enabling `auto-release` label. Readiness is not approval or a compatibility waiver. Skip a new API-review request only when there is no public API diff and an existing revision is already approved; never skip it for an actual diff or gate failure.
3. **Observe:** Verify source SHA, artifact version, resolver output and `Release_azureaievaluation`, not just a green build. [Troubleshoot](references/troubleshooting.md) skipped stages, stale links and tool failures.
4. **Close:** [Verify publication and review the next-version PR](references/completion.md). Hotfix branches are exceptional, not synonymous with patch versions. See a [dated worked example](references/worked-example.md) for concrete evidence shapes; re-derive every value for a new release.

Report **state, evidence, blocker, next authorized action**. Distinguish local edits, push, PR, merge, build, release stage and publication; never claim unobserved transitions.

Advice, "what next", or "done" does not authorize writes, live evaluations or pipeline runs. Obtain authorization for preparation, commit/push, PRs and labels. Never approve stages, merge or publish for the user. Preserve gates and released history; disclose limitations.
