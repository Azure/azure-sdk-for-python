# Azure AI ML Issue Automation - Architecture

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Issue Created                      │
│   Title/Body mentions: "azure-ai-ml" + "mypy/pylint/pyright"│
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           GitHub Actions Workflow Triggered                  │
│    (.github/workflows/auto-assign-azure-ai-ml-issues.yml)   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Issue Text Analysis                         │
│   • Check for "azure-ai-ml" keyword                          │
│   • Check for "mypy" OR "pylint" OR "pyright" keyword        │
└────────────────────────┬────────────────────────────────────┘
                         │
                 ┌───────┴────────┐
                 │                │
         Matches │                │ No Match
                 ▼                ▼
┌─────────────────────────┐   ┌──────────────┐
│   Auto-Label Issue      │   │  No Action   │
│   • azure-ai-ml         │   └──────────────┘
│   • mypy/pylint/pyright │
│   • Machine Learning    │
│   • needs-copilot-action│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│              Add Bot Comment with Instructions               │
│   • Detected tool (mypy/pylint/pyright)                      │
│   • Commands to run                                          │
│   • How to use Copilot for fix                              │
└────────────────────────┬────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                Create Tracking File                          │
│     (.github/copilot-tasks/issue-<NUM>.json)                │
└────────────────────────┬────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Manual Steps                               │
│   1. Team member sees labeled issue                          │
│   2. Runs: python scripts/copilot_fix_trigger.py            │
│   3. Uses Copilot with generated prompt                      │
│   4. Creates PR with fixes                                   │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. GitHub Actions Workflow
**File:** `.github/workflows/auto-assign-azure-ai-ml-issues.yml`

**Triggers:**
- `issues.opened`
- `issues.edited`
- `issues.labeled`

**Jobs:**
- Check issue text for keywords
- Add labels programmatically
- Create bot comment
- Generate tracking file

### 2. Helper Script
**File:** `scripts/copilot_fix_trigger.py`

**Functions:**
- `get_fix_instructions(tool)` - Returns tool-specific fix steps
- `generate_copilot_prompt(issue_number, tool)` - Creates Copilot prompt
- `save_copilot_task(issue_number, tool)` - Saves tracking data

**Usage:**
```bash
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy
```

### 3. Configuration
**File:** `.github/azure-ai-ml-automation.config.json`

Contains:
- Enabled rules
- Label definitions
- Assignee settings
- Copilot instructions per tool
- Reference documentation links

### 4. Documentation
- **Full docs:** `.github/workflows/README-AZURE-AI-ML-AUTOMATION.md`
- **Quick reference:** `.github/QUICKREF-AZURE-AI-ML-AUTOMATION.md`
- **Copilot instructions:** `.github/copilot-instructions.md`

## Data Flow

```
Issue Created
    ↓
Workflow detects keywords
    ↓
Labels added automatically
    ↓
Bot comments with instructions
    ↓
Tracking file created
    ↓
Human/Copilot reads issue
    ↓
Generates fix prompt
    ↓
Copilot creates PR
    ↓
PR linked to issue
    ↓
Issue resolved
```

## Label Taxonomy

```
azure-ai-ml ────────── Package identifier
    │
    ├─ mypy ─────────── Type checker (MyPy)
    ├─ pylint ───────── Linter (Pylint)
    └─ pyright ──────── Type checker (Pyright)
         │
         └─ needs-copilot-action ─── Action required
                 │
                 └─ Machine Learning ─── Category
```

## Example Flows

### Flow 1: MyPy Issue
```
Issue: "azure-ai-ml has mypy errors"
    ↓
Workflow detects: azure-ai-ml + mypy
    ↓
Labels: [azure-ai-ml, mypy, Machine Learning, needs-copilot-action]
    ↓
Bot comments with mypy fix instructions
    ↓
Maintainer runs: python scripts/copilot_fix_trigger.py --issue-number N --tool mypy
    ↓
Copilot fixes type errors
    ↓
PR created and linked
```

### Flow 2: Pylint Issue
```
Issue: "Fix pylint warnings in azure-ai-ml"
    ↓
Workflow detects: azure-ai-ml + pylint
    ↓
Labels: [azure-ai-ml, pylint, Machine Learning, needs-copilot-action]
    ↓
Bot comments with pylint fix instructions
    ↓
Maintainer uses Copilot Workspace
    ↓
Copilot fixes style issues
    ↓
PR created and linked
```

### Flow 3: Multiple Tools
```
Issue: "azure-ai-ml needs mypy and pylint fixes"
    ↓
Workflow detects: azure-ai-ml + mypy + pylint
    ↓
Labels: [azure-ai-ml, mypy, pylint, Machine Learning, needs-copilot-action]
    ↓
Bot comments with instructions for both
    ↓
Maintainer fixes one at a time
    ↓
Multiple PRs created or one combined PR
```

## Extension Points

### Adding New Packages
1. Modify workflow keyword detection
2. Add package-specific labels
3. Update config.json
4. Add to copilot_fix_trigger.py

### Adding New Tools
1. Add tool to workflow regex
2. Create label for tool
3. Add instructions to copilot_fix_trigger.py
4. Update documentation

### Integration with Other Systems
- Slack/Teams notifications (webhook in config)
- Jira/Azure DevOps integration
- Metrics/analytics dashboard
- Auto-assignment to specific users

## Monitoring

### Success Metrics
- Number of issues auto-detected
- Time to first response
- Number of PRs created via Copilot
- Issue resolution time

### Logging
- Workflow runs: GitHub Actions UI
- Issue labels: Issue tracker
- Tracking files: `.github/copilot-tasks/`

## Security Considerations

- Workflow uses `issues: write` permission only
- No secrets required for basic operation
- Scripts run in sandboxed environment
- No automatic code execution

## Maintenance

### Regular Tasks
- Monitor workflow success rate
- Update tool-specific instructions
- Review and archive tracking files
- Update documentation

### Troubleshooting
1. Check workflow run logs
2. Verify issue format
3. Test script locally
4. Review permissions

---

**Version:** 1.0.0  
**Last Updated:** 2024-02-10  
**Maintainers:** Azure SDK Python Team
