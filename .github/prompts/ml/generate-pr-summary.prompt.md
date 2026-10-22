---
agent: agent
description: Create a PR summary for azure-ai-ml changes in the current branch
name: generate-pr-summary
---

Analyze changes in the `sdk/ml/azure-ai-ml` package ONLY. Check both committed changes (if any) and uncommitted changes. Generate a clear PR summary highlighting key features, bug fixes, type safety improvements, and other significant changes for reviewers. Focus exclusively on azure-ai-ml - ignore all other packages.

## Git Commands for Gathering Information

Use these commands to analyze azure-ai-ml changes:

```powershell
# Check uncommitted changes in azure-ai-ml (staged and unstaged)
git status -- sdk/ml/azure-ai-ml/
git diff --name-status -- sdk/ml/azure-ai-ml/
git diff --cached --name-status -- sdk/ml/azure-ai-ml/

# Get committed changes in azure-ai-ml compared to main
git diff main..HEAD --name-status -- sdk/ml/azure-ai-ml/

# Get commit messages for azure-ai-ml changes
git log main..HEAD --oneline -- sdk/ml/azure-ai-ml/

# Get change statistics for azure-ai-ml only
git diff --shortstat -- sdk/ml/azure-ai-ml/
git diff main..HEAD --shortstat -- sdk/ml/azure-ai-ml/

# View sample diff for analysis
git diff -- sdk/ml/azure-ai-ml/ | Select-Object -First 100
```

**Priority**: If uncommitted changes exist in azure-ai-ml, use those for the summary. Otherwise use committed changes.

## PR Summary Template

Keep the summary concise and focused:

```markdown
## PR Summary

**Title:** [Brief description of the changes]

[Brief 1-2 sentence description of what changed and why]

**Changes:**
- [Key change 1]
- [Key change 2]
- [Key change 3]

**Files:** [N] files in [affected areas: operations/entities/tests/docs]

**Testing:** [Brief status - e.g., "tests passing, mypy/pylint compliant"]
```

### Guidelines

- **Title**: Brief description in lowercase, imperative mood, no period
- **Keep it brief**: 3-5 bullet points max, focus on what matters
- **No tables**: Simple list format only