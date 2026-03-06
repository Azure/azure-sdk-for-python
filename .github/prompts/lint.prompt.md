---
mode: 'agent'
tools: ['azsdk_verify_setup', 'azsdk_package_run_check', 'azsdk_analyze_log_file']
description: 'This agent runs linting and validation checks on Azure SDK for Python packages using the azpysdk tools.'
---

## Goal

Run linting and validation checks on the user's changed code in Azure SDK for Python packages.

## Instructions

1. **Verify Environment Setup**:
   - First, run `azsdk_verify_setup` to check the user's development environment
   - Ensure Python and required tools are properly configured
   - If setup is not complete, provide guidance on resolving any issues

2. **Identify the Package Path**:
   - Ask the user for the package path if not already provided
   - The package path should be the absolute path to the SDK package directory (e.g., `/path/to/azure-sdk-for-python/sdk/storage/azure-storage-blob`)
   - If the user provides a relative path, help construct the absolute path

3. **Run Linting Checks**:
   - Use `azsdk_package_run_check` with the appropriate check type
   - Available check types:
     - `All` - Run all validation checks
     - `Linting` - Run linting checks (pylint, ruff)
     - `Format` - Check code formatting
     - `Changelog` - Validate changelog
     - `Dependency` - Check dependencies
     - `Readme` - Validate README
     - `Cspell` - Check spelling
     - `Snippets` - Validate code snippets
     - `Samples` - Validate samples
     - `CheckAotCompat` - Check AOT compatibility
     - `GeneratedCodeChecks` - Check generated code

4. **Present Results**:
   - Display the linting results clearly
   - If there are errors or warnings, explain what they mean
   - Provide guidance on how to fix common issues

5. **Offer to Fix Issues**:
   - Some check types support automatic fixing via the `fixCheckErrors` parameter in `azsdk_package_run_check`
   - When running checks, you can set `fixCheckErrors: true` to automatically fix certain issues (e.g., formatting issues)
   - For issues that cannot be auto-fixed, provide clear instructions on manual fixes based on the linting output

## Expected User Interaction Flow

1. Verify environment is set up correctly
2. Ask: "What is the path to the package you want to lint?"
3. Ask: "Which checks would you like to run? (All, Linting, Format, Changelog, Dependency, Readme, Cspell, Snippets, Samples, CheckAotCompat, GeneratedCodeChecks)"
4. Execute the linting checks
5. Display results and provide guidance on fixing any issues

## Reference Documentation

- [Python SDK Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Azure pylint guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)
- [Tox testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)
- [MyPy fixing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
