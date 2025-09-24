mode: 'agent'
tools: ['azsdk_package_run_check']
---

## Goal:
Validate generated and custom code in local SDK repositories. Assist users in fixing any issues found.

## Step 1: Run Validation
Use `azsdk_package_run_check` to validate the package. This tool checks for common issues in the package. To fix issues found, pass in the appropriate argument to the command.

- If no issues are found: Success - No further action needed.
- If issues are found: Follow the instructions provided by the tool to fix them.
