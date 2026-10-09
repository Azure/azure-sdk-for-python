---
description: "Required local static validation before publishing changes"
applyTo: "**"
---

# Pre-push Validation

- Before every push or agent tool that commits and pushes changes, load and follow `.github/skills/azsdk-common-pre-push-check/SKILL.md`.
- Include documentation-only and non-SDK changes. Validate the whole branch diff against the PR target and any staged, unstaged, and untracked non-ignored files, not just the latest commit.
- Run applicable existing spelling, link, formatting, lint, and type checks with CI's configuration. After fixes or further edits, rerun affected checks before publishing.
- Report exact commands and results. Do not publish with failed or blocked required checks; missing tools, configuration, base history, or network access are not successful validation.
