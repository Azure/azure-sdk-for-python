# Implementation Summary: Azure AI ML Issue Automation

## Overview

This implementation creates an automated system for handling GitHub issues related to azure-ai-ml package linting and type checking issues (mypy, pylint, pyright). The system automatically detects, labels, and provides instructions for using Copilot to fix these issues.

## What Was Created

### 1. GitHub Actions Workflow
**File:** `.github/workflows/auto-assign-azure-ai-ml-issues.yml`

This workflow:
- Triggers on issue `opened`, `edited`, or `labeled` events
- Automatically detects issues mentioning "azure-ai-ml" + "mypy/pylint/pyright"
- Applies appropriate labels (`azure-ai-ml`, `mypy/pylint/pyright`, `Machine Learning`, `needs-copilot-action`)
- Adds a bot comment with detailed instructions for using Copilot
- Creates tracking files for monitoring

### 2. Helper Script
**File:** `scripts/copilot_fix_trigger.py`

A Python CLI tool that:
- Generates detailed fix instructions for specific issues
- Supports mypy, pylint, and pyright
- Outputs prompts that can be used with Copilot
- Can save tracking files for issue management

**Example usage:**
```bash
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy
```

### 3. Test Suite
**File:** `scripts/test_copilot_fix_trigger.py`

Comprehensive tests that verify:
- Instruction generation for all tools
- Prompt generation correctness
- Content validation
- Error handling

All tests pass successfully.

### 4. Configuration File
**File:** `.github/azure-ai-ml-automation.config.json`

JSON configuration containing:
- Automation rules and settings
- Label definitions with descriptions and colors
- Assignee settings
- Tool-specific Copilot instructions
- Reference documentation links

### 5. Documentation

#### Full Documentation
**File:** `.github/workflows/README-AZURE-AI-ML-AUTOMATION.md`
- Comprehensive guide to the automation system
- Usage instructions for all components
- Examples of issue formats
- Troubleshooting guide
- Customization instructions

#### Quick Reference
**File:** `.github/QUICKREF-AZURE-AI-ML-AUTOMATION.md`
- Condensed reference for quick lookups
- Common commands and workflows
- Troubleshooting table
- Links to full documentation

#### Architecture Documentation
**File:** `.github/ARCHITECTURE-AZURE-AI-ML-AUTOMATION.md`
- System architecture with flowcharts
- Component descriptions
- Data flow diagrams
- Extension points
- Monitoring and maintenance guidelines

#### Updated Copilot Instructions
**File:** `.github/copilot-instructions.md`
- Added section on automated issue handling
- Instructions for Copilot on how to use the system
- Quick reference links

## How It Works

### Automatic Detection Flow

1. **Issue Created**: User creates an issue with title/body mentioning "azure-ai-ml" and "mypy/pylint/pyright"

2. **Workflow Triggers**: GitHub Actions workflow detects the keywords

3. **Auto-Labeling**: Issue gets labeled automatically:
   - `azure-ai-ml` - Package identifier
   - `mypy`/`pylint`/`pyright` - Tool identifier
   - `Machine Learning` - Category
   - `needs-copilot-action` - Action flag

4. **Bot Comment**: Automated comment added with:
   - Detected tool information
   - Commands to run
   - Instructions for using Copilot
   - Links to documentation

5. **Tracking**: JSON file created in `.github/copilot-tasks/` for monitoring

### Manual Fix Process

When a team member sees a labeled issue:

**Option 1: Using Helper Script**
```bash
python scripts/copilot_fix_trigger.py --issue-number 44424 --tool mypy
# Copy the output and use it with Copilot
```

**Option 2: GitHub Copilot Workspace**
- Open Copilot Workspace
- Reference the issue number
- Follow the bot's instructions

**Option 3: IDE with Copilot**
- Open the package in VS Code
- Run the tool to see errors
- Use Copilot suggestions to fix

## Example Scenarios

### Scenario 1: MyPy Issue
```
User creates issue: "azure-ai-ml has mypy type checking errors"
    ↓
Workflow automatically:
  - Labels: [azure-ai-ml, mypy, Machine Learning, needs-copilot-action]
  - Comments with mypy fix instructions
  - Creates tracking file
    ↓
Maintainer uses helper script to get detailed prompt
    ↓
Copilot fixes type errors
    ↓
PR created and linked to issue
```

### Scenario 2: Pylint Issue
```
User creates issue: "Fix pylint warnings in azure-ai-ml package"
    ↓
Workflow automatically:
  - Labels: [azure-ai-ml, pylint, Machine Learning, needs-copilot-action]
  - Comments with pylint fix instructions
  - Creates tracking file
    ↓
Maintainer uses Copilot Workspace with generated instructions
    ↓
Copilot fixes style issues
    ↓
PR created and linked to issue
```

## Key Features

### 1. Zero Manual Triage
Issues are automatically detected and labeled without human intervention.

### 2. Intelligent Detection
Uses keyword matching to identify relevant issues accurately.

### 3. Tool-Specific Instructions
Different instructions for mypy, pylint, and pyright based on best practices.

### 4. Copilot Integration
Generates prompts specifically designed for GitHub Copilot to fix issues efficiently.

### 5. Comprehensive Documentation
Multiple levels of documentation from quick reference to detailed architecture.

### 6. Extensible Design
Easy to add support for:
- Additional packages beyond azure-ai-ml
- New linting/type checking tools
- Custom workflows
- Integration with other systems

### 7. Monitoring and Tracking
- Tracking files for issue status
- Workflow run logs
- Label-based filtering

## Benefits

### For Issue Reporters
- Clear feedback that their issue was detected
- Automated labeling helps with visibility
- Faster response times

### For Maintainers
- Automatic triage saves time
- Clear instructions for fixing issues
- Standardized approach to common problems
- Easy Copilot integration

### For Copilot
- Structured prompts with all necessary context
- References to official documentation
- Clear success criteria
- Minimal change philosophy

## Files Added/Modified

### Added Files
1. `.github/workflows/auto-assign-azure-ai-ml-issues.yml` - Main workflow
2. `.github/azure-ai-ml-automation.config.json` - Configuration
3. `.github/workflows/README-AZURE-AI-ML-AUTOMATION.md` - Full documentation
4. `.github/QUICKREF-AZURE-AI-ML-AUTOMATION.md` - Quick reference
5. `.github/ARCHITECTURE-AZURE-AI-ML-AUTOMATION.md` - Architecture docs
6. `scripts/copilot_fix_trigger.py` - Helper script
7. `scripts/test_copilot_fix_trigger.py` - Test suite

### Modified Files
1. `.github/copilot-instructions.md` - Added automation section
2. `.gitignore` - Added scripts/__pycache__/

## Testing

### Script Tests
All unit tests pass:
```bash
python scripts/test_copilot_fix_trigger.py
# ✓ All tests passed!
```

### Manual Validation
- YAML syntax validated
- Python syntax validated
- All scripts are executable
- Documentation links verified

## Next Steps

### To Deploy
1. Merge this PR to enable the automation
2. Test with a real issue (create test issue)
3. Monitor workflow runs
4. Gather feedback from team

### To Extend
1. Add more packages by updating the workflow
2. Add more tools by updating the script
3. Integrate with Slack/Teams for notifications
4. Add metrics dashboard

## Maintenance

### Regular Tasks
- Monitor workflow success rate
- Update tool-specific instructions as needed
- Review and clean up tracking files
- Update documentation

### Monitoring
- GitHub Actions runs: `https://github.com/Azure/azure-sdk-for-python/actions/workflows/auto-assign-azure-ai-ml-issues.yml`
- Issue labels: Filter by `needs-copilot-action`
- Tracking files: `.github/copilot-tasks/`

## Support

For questions or issues with the automation:
1. Check the documentation files
2. Review workflow run logs
3. Test the script locally
4. Contact repository maintainers

## References

- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Pylint Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Static Type Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)

---

**Implementation Date:** 2024-02-10  
**Version:** 1.0.0  
**Status:** Complete and Ready for Testing
