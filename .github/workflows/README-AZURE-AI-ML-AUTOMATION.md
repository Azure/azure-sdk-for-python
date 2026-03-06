# Azure AI ML Linting and Type Checking Issue Automation

This directory contains automation workflows for handling azure-ai-ml package issues related to mypy, pylint, and pyright.

## Overview

When issues are created in the Azure/azure-sdk-for-python repository that mention `azure-ai-ml` along with `mypy`, `pylint`, or `pyright`, the automation will:

1. **Auto-detect** the issue based on title and body content
2. **Auto-label** the issue with appropriate labels (azure-ai-ml, mypy/pylint/pyright, Machine Learning, needs-copilot-action)
3. **Add a comment** with instructions for using Copilot to fix the issue
4. **Create a tracking file** for monitoring the issue status

## Workflow Files

### `.github/workflows/auto-assign-azure-ai-ml-issues.yml`

Main workflow that:
- Triggers on issue `opened`, `edited`, or `labeled` events
- Checks if the issue mentions azure-ai-ml and a linting/type checking tool
- Automatically labels the issue
- Adds a comment with next steps
- Creates a tracking file

## Helper Scripts

### `scripts/copilot_fix_trigger.py`

Python script to generate detailed instructions for Copilot to fix specific issues.

**Usage:**
```bash
# Generate instructions for fixing mypy issues
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy

# Generate instructions for fixing pylint issues
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool pylint

# Generate instructions for fixing pyright issues
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool pyright

# Save task file for tracking
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy --save-task

# Output in JSON format
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy --output-format json
```

## How to Use Copilot to Fix Issues

Once an issue is auto-detected and labeled:

### Option 1: GitHub Copilot Workspace

1. Open GitHub Copilot Workspace
2. Reference the issue number
3. Use the generated prompt from the bot comment or run:
   ```bash
   python scripts/copilot_fix_trigger.py --issue-number <issue-number> --tool <tool>
   ```
4. Follow Copilot's suggestions to fix the issues
5. Create a PR linked to the issue

### Option 2: Manual Fix with Copilot CLI

1. Use the GitHub Copilot CLI to get fix suggestions:
   ```bash
   gh copilot suggest "Fix mypy issues in azure-ai-ml package for issue #<issue-number>"
   ```

2. Follow the suggested commands and fixes

### Option 3: Copilot in VS Code/IDE

1. Open the azure-ai-ml package in your IDE
2. Run the linting/type checking tool to see errors
3. Use Copilot inline suggestions to fix each error
4. Verify fixes and create a PR

## Example Issue Format

The automation detects issues like:

**Example 1:**
- **Title:** "azure-ai-ml fails mypy type checking"
- **Body:** "The azure-ai-ml package has mypy errors that need to be fixed..."

**Example 2:**
- **Title:** "Update needed: pylint warnings in azure-ai-ml"
- **Body:** "Multiple pylint warnings found in azure-ai-ml..."

**Example 3:**
- **Title:** "azure-ai-ml pyright errors"
- **Body:** "Pyright is reporting type errors in azure-ai-ml..."

## Labels Applied

When an issue matches the criteria, these labels are automatically applied:

- `azure-ai-ml` - Identifies the package
- `mypy` / `pylint` / `pyright` - Identifies the specific tool
- `Machine Learning` - Category label
- `needs-copilot-action` - Indicates Copilot action is needed

## Tracking Files

Tracking files are created in `.github/copilot-tasks/` directory:

```json
{
  "issue_number": 44424,
  "issue_title": "azure-ai-ml mypy issues",
  "package": "azure-ai-ml",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "pending"
}
```

These files help track which issues have been detected and their current status.

## Customization

### Adding More Packages

To extend this automation to other packages, modify the workflow file:

1. Update the package check in `.github/workflows/auto-assign-azure-ai-ml-issues.yml`
2. Add the new package name to the detection logic
3. Update labels as needed

### Adding More Tools

To support additional linting/type checking tools:

1. Add the tool name to the detection regex in the workflow
2. Update the `copilot_fix_trigger.py` script with instructions for the new tool
3. Add appropriate labels

## Maintenance

### Monitoring

Check the Actions tab in GitHub to see workflow runs:
- `https://github.com/Azure/azure-sdk-for-python/actions/workflows/auto-assign-azure-ai-ml-issues.yml`

### Updating Instructions

If the fix process changes, update:
1. The `get_fix_instructions()` function in `scripts/copilot_fix_trigger.py`
2. The comment template in the workflow file

## References

- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Pylint Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Static Type Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)

## Troubleshooting

### Issue not being detected

Check that:
- Issue title or body mentions "azure-ai-ml"
- Issue title or body mentions "mypy", "pylint", or "pyright"
- The workflow has proper permissions in GitHub Actions settings

### Labels not being applied

Ensure the workflow has `issues: write` permission in the repository settings.

### Tracking files not created

The tracking files are created in the workflow but not committed. They are for runtime tracking only.

## Contributing

To improve this automation:

1. Test changes in a fork first
2. Ensure backward compatibility
3. Update documentation
4. Submit a PR with clear description of changes
