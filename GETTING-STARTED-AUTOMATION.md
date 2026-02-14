# Getting Started with Azure AI ML Issue Automation

## Quick Start (5 minutes)

### For Issue Reporters

Just create an issue with a title like:
```
"azure-ai-ml has mypy errors"
"Fix pylint warnings in azure-ai-ml" 
"azure-ai-ml pyright type checking issues"
```

The automation will handle the rest!

### For Maintainers

When you see an issue with the `needs-copilot-action` label:

**Step 1:** Generate fix instructions
```bash
cd /path/to/azure-sdk-for-python
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy
```

**Step 2:** Copy the output and use it with GitHub Copilot

**Step 3:** Create a PR with the fixes

That's it!

## Example Walkthrough

### Scenario: Issue #44424 - "azure-ai-ml mypy errors"

#### 1. Issue Created
User creates an issue:
- **Title:** "azure-ai-ml has mypy type checking errors"
- **Body:** "The azure-ai-ml package has several mypy errors that need to be fixed..."

#### 2. Automation Triggers (Automatic)
Within seconds:
- ✓ Issue labeled: `azure-ai-ml`, `mypy`, `Machine Learning`, `needs-copilot-action`
- ✓ Bot comment added with instructions
- ✓ Tracking file created

#### 3. Maintainer Action
```bash
# Generate detailed fix instructions
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy

# Output shows:
# - Package location: sdk/ml/azure-ai-ml
# - Command to run: tox -e mypy -- sdk/ml/azure-ai-ml
# - Fix guidelines
# - Testing requirements
```

#### 4. Use Copilot
Copy the generated prompt and use it with:
- GitHub Copilot Workspace
- VS Code Copilot
- GitHub Copilot CLI

#### 5. Create PR
Copilot helps fix the issues, then:
```bash
# Create PR and link to issue
gh pr create --title "Fix mypy errors in azure-ai-ml" --body "Fixes #44424"
```

Done! ✓

## Command Reference

### Generate Instructions
```bash
# For mypy issues
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool mypy

# For pylint issues
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool pylint

# For pyright issues
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool pyright

# Get JSON output
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool mypy --output-format json

# Save tracking file
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool mypy --save-task
```

### Check Workflow Status
```bash
# View recent workflow runs
gh run list --workflow=auto-assign-azure-ai-ml-issues.yml

# View specific run details
gh run view <run-id>

# Check workflow logs
gh run view <run-id> --log
```

### Manual Label Addition (if needed)
```bash
# If automation didn't trigger, manually add labels
gh issue edit <NUM> --add-label "azure-ai-ml,mypy,needs-copilot-action,Machine Learning"
```

## Tips and Tricks

### For Best Results

1. **Be Specific in Issue Titles**
   - ✓ Good: "azure-ai-ml mypy errors in authentication module"
   - ✗ Poor: "Type checking issues"

2. **Mention Both Package and Tool**
   - Must include: "azure-ai-ml"
   - Must include: "mypy" OR "pylint" OR "pyright"

3. **Use the Helper Script**
   - Don't guess at commands
   - Let the script generate proper instructions
   - It includes all necessary context

4. **Run Tests**
   - Always run tests after fixes
   - Verify no regressions
   - Check that the specific tool passes

### Common Workflows

#### Workflow 1: Quick Fix
```bash
# See issue with needs-copilot-action label
# Generate instructions
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool mypy
# Use Copilot to fix
# Create PR
```

#### Workflow 2: Multiple Issues
```bash
# If issue mentions multiple tools
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool mypy
python scripts/copilot_fix_trigger.py --issue-number <NUM> --tool pylint
# Fix one at a time or combine in single PR
```

#### Workflow 3: Manual Override
```bash
# If automation didn't trigger
gh issue edit <NUM> --add-label "needs-copilot-action"
# Then proceed with normal workflow
```

## Troubleshooting

### Issue Not Detected
**Problem:** Issue created but no labels added

**Solution:**
1. Check issue title/body contains "azure-ai-ml"
2. Check issue title/body contains "mypy" OR "pylint" OR "pyright"
3. Check workflow run logs: `gh run list --workflow=auto-assign-azure-ai-ml-issues.yml`
4. Manually add labels if needed

### Script Error
**Problem:** Script fails to run

**Solution:**
```bash
# Check Python version (need 3.9+)
python3 --version

# Run tests
python3 scripts/test_copilot_fix_trigger.py

# Verify syntax
python3 -m py_compile scripts/copilot_fix_trigger.py
```

### Copilot Not Responding
**Problem:** Copilot doesn't understand instructions

**Solution:**
1. Use exact output from helper script
2. Ensure you're in correct directory
3. Try different Copilot interface (Workspace vs CLI vs IDE)

## Next Steps

After the PR is merged:

1. **Test with Real Issue**
   ```bash
   # Create a test issue to verify automation
   gh issue create --title "azure-ai-ml mypy test" --body "Testing automation"
   ```

2. **Monitor for a Week**
   - Check workflow runs daily
   - Gather feedback from team
   - Note any issues or improvements

3. **Iterate and Improve**
   - Add more packages if needed
   - Adjust instructions based on feedback
   - Add more tools if requested

## Resources

- **Full Documentation:** `.github/workflows/README-AZURE-AI-ML-AUTOMATION.md`
- **Quick Reference:** `.github/QUICKREF-AZURE-AI-ML-AUTOMATION.md`
- **Architecture:** `.github/ARCHITECTURE-AZURE-AI-ML-AUTOMATION.md`
- **Implementation Details:** `IMPLEMENTATION-SUMMARY.md`

## Support

Need help?
1. Check the documentation
2. Run the test suite
3. Review workflow logs
4. Contact repository maintainers

---

**Ready to go!** Start by creating a test issue or waiting for the next real issue to see the automation in action.
