# Quick Reference: Azure AI ML Issue Automation

## For Issue Reporters

When reporting issues related to azure-ai-ml linting/type checking:

1. **Include keywords in title or body:**
   - Package: `azure-ai-ml`
   - Tool: `mypy`, `pylint`, or `pyright`

2. **Example titles:**
   - ✅ "azure-ai-ml mypy errors need fixing"
   - ✅ "Fix pylint warnings in azure-ai-ml"
   - ✅ "azure-ai-ml fails pyright type checking"

3. **What happens automatically:**
   - Issue gets labeled with relevant tags
   - Bot adds comment with fix instructions
   - Issue marked for Copilot action

## For Maintainers

### Quick Commands

```bash
# Generate fix instructions for an issue
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool <mypy|pylint|pyright>

# Example: Fix mypy issues in issue #44424
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy
```

### Using Copilot to Fix Issues

**Method 1: Copy-paste the generated prompt**
```bash
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy
# Copy output and paste into Copilot Workspace
```

**Method 2: Direct Copilot command**
```
@github Fix mypy issues in azure-ai-ml for issue #44424
```

**Method 3: VS Code/IDE**
1. Open `sdk/ml/azure-ai-ml` 
2. Run the tool (mypy/pylint/pyright)
3. Use Copilot inline suggestions to fix errors
4. Create PR

### Workflow Monitoring

**View workflow runs:**
```
https://github.com/Azure/azure-sdk-for-python/actions/workflows/auto-assign-azure-ai-ml-issues.yml
```

**Check if issue was detected:**
- Look for the `needs-copilot-action` label
- Check for bot comment with instructions

### Manual Override

If automation doesn't trigger:

```bash
# Manually add labels
gh issue edit <NUM> --add-label "azure-ai-ml,mypy,needs-copilot-action"

# Generate instructions
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool <TOOL>
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Issue not detected | Ensure title/body contains both "azure-ai-ml" and tool name |
| Labels not applied | Check workflow permissions in repository settings |
| Copilot not responding | Use manual Copilot command or VS Code extension |
| Script error | Verify Python 3.11+ installed |

## Configuration

**Workflow:** `.github/workflows/auto-assign-azure-ai-ml-issues.yml`  
**Script:** `scripts/copilot_fix_trigger.py`  
**Config:** `.github/azure-ai-ml-automation.config.json`  
**Docs:** `.github/workflows/README-AZURE-AI-ML-AUTOMATION.md`

## Support

For issues with the automation:
1. Check workflow run logs
2. Verify issue format matches examples
3. Contact repository maintainers

---

**Last Updated:** 2024-02-10  
**Version:** 1.0.0
