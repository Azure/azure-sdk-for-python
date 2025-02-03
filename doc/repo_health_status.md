# Python SDK Health Status Report

The Python health status report is used to get a quick glance of our SDK health and whether a library can pass CI checks to release the package.

[aka.ms/azsdk/python/health](https://www.aka.ms/azsdk/python/health)

## Need help?

If this document does not answer your question, please post on the [Language - Python](https://teams.microsoft.com/l/channel/19%3Ab97d98e6d22c41e0970a1150b484d935%40thread.skype/Language%20-%20Python?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) Teams channel.

## Overview

The health report collects statuses from the most recent scheduled pipelines for your library. This includes your release pipeline (`python - {service-directory}`), your live tests pipeline (`python - {service-directory} - tests`), and your live tests-weekly pipeline (`python - {service-directory} - tests-weekly`). If a pipeline result is available, you can click on the status in the report to view the build result.

The following are required, release-blocking checks: `MyPy`, `Pylint`, `Sphinx`, and `Tests - CI`. If any of these checks are failing, your library will be blocked from releasing. If any of these checks are disabled, your library may be blocked from release in the future. If any of these are in a warning state, your library is not blocked from release today, but may be blocked in the near future. See below for more information on each check.

> Note: A check can be re-enabled by removing the `check = false` from the library's pyproject.toml file. See [eng_sys_checks.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#the-pyprojecttoml) for more information on how we use pyproject.toml in this repo.

## Explained

The health report is broken down into the following sections:

- [Status](#status)
- [MyPy](#mypy-required-check)
- [Pylint](#pylint-required-check)
- [Sphinx](#sphinx-required-check)
- [Tests - CI](#tests---ci-required-check)
- [Tests - Live](#tests---live)
- [Tests - Samples](#tests---samples)
- [Pyright](#pyright)
- [Type check samples](#type-check-samples)
- [SLA - Bugs](#sla---bugs)
- [SLA - Questions](#sla---questions)
- [Total customer-reported issues](#total-customer-reported-issues)

### Status:

This is the overall status of your library and indicates whether you can release your library today.

- $${\color{red}BLOCKED}$$ - your library is currently blocked from release. It is failing required/mandatory checks (marked in red) or has its CI disabled due to non-compliance with required checks.

    If your CI has been disabled, please take action to re-enable and fix all checks highlighted in yellow. Once all checks are fixed, you can remove the `ci_enabled=false` from your library's pyproject.toml file.

- $${\color{yellow}NEEDS \space ACTION}$$ - your library is not blocked from release today, but if action(s) are not taken, it may be blocked in the near future. Please take action to fix/re-enable any checks highlighted in yellow.

- $${\color{green}GOOD}$$ - your library is passing and in compliance with all required checks and can release without issues.

### MyPy (required check):

[MyPy](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#mypy) is a static type checker, and is mandatory to run on the source code of all libraries. To learn more about static type checking in our repo, see our [Static Type Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md). Possible statuses include:

- $${\color{red}FAIL}$$ - The library is failing the MyPy check. Check the build result and address the errors present. This will block the release of your library and should be fixed immediately.
- $${\color{yellow}DISABLED}$$ - MyPy is not enabled for your library in the pyproject.toml file. This is a required check and must be enabled. If not enabled, your library will be blocked from release in the near future.
- $${\color{yellow}WARNING}$$ - The library passes the currently pinned version of MyPy in the repo, but is failing the next-mypy check (the next version of MyPy the repo will be bumped to in the near future). Please fix these errors before the merge date of the next version of MyPy or the errors will begin to fail the build (See [analyze_check_versions.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/analyze_check_versions.md)) to understand target dates for version bumps.
- $${\color{green}PASS}$$ - The library passes both current MyPy and next-MyPy.
- $${\color{black}UNKNOWN}$$ - A result was not available for the most recent scheduled build. This could be due to an upstream pipeline failure preventing this particular check from running or a missing pipeline. Please ensure your pipeline builds are free of errors so that a Status for your library can be determined.

### Pylint (required check):

[Pylint](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#pylint) is a linter, and is mandatory to run on all libraries. To learn more about linting in our repo, see our [Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md). Possible statuses include:

- $${\color{red}FAIL}$$ - The library is failing the Pylint check. Check the build result and address the errors present. This will block the release of your library and should be fixed immediately.
- $${\color{yellow}DISABLED}$$ - Pylint is not enabled for your library in the pyproject.toml file. This is a required check and must be enabled. If not enabled, your library will be blocked from release in the near future.
- $${\color{yellow}WARNING}$$ - The library passes the currently pinned version of Pylint in the repo, but is failing the next-pylint check (the next version of Pylint the repo will be bumped to in the near future). Please fix these errors before the merge date of the next version of Pylint or the errors will begin to fail the build (See [analyze_check_versions.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/analyze_check_versions.md)) to understand target dates for version bumps.
- $${\color{green}PASS}$$ - The library passes both current Pylint and next-Pylint.
- $${\color{black}UNKNOWN}$$ - A result was not available for the most recent scheduled build. This could be due to an upstream pipeline failure preventing this particular check from running or a missing pipeline. Please ensure your pipeline builds are free of errors so that a Status for your library can be determined.

### Sphinx (required check):

[Sphinx](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#sphinx-and-docstring-checker) is a tool which builds/validates our documentation, and is mandatory to run on all libraries. To learn more about Sphinx/docstrings in our repo, see [Docstrings](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/docstring.md). Possible statuses include:

- $${\color{red}FAIL}$$ - The library is failing the Sphinx check. Check the build result and address the errors present. This will block the release of your library and should be fixed immediately.
- $${\color{yellow}DISABLED}$$ - Sphinx is not enabled for your library in the pyproject.toml file. This is a required check and must be enabled. If not enabled, your library will be blocked from release in the near future.
- $${\color{green}PASS}$$ - The library passes Sphinx.
- $${\color{black}UNKNOWN}$$ - A result was not available for the most recent scheduled build. This could be due to an upstream pipeline failure preventing this particular check from running or a missing pipeline. Please ensure your pipeline builds are free of errors so that a Status for your library can be determined.

### Tests - CI (required check):

[Tests - CI](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#pr-validation-tox-test-environments) checks the status of the most recent (python - {service-directory})scheduled build of your library's recorded tests. This is the same CI that will run when triggering a release build. To learn more about tests in our repo, see our [Testing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md). Possible statuses include:

- $${\color{red}FAIL}$$ - The library is failing CI recorded tests. Check the build result and address the errors present. This will block the release of your library and should be fixed immediately.
- $${\color{yellow}DISABLED}$$ - The library has its CI disabled due to non-compliance with required checks. Please take action to re-enable and fix all checks highlighted in yellow. Once all checks are fixed, you can remove the `ci_enabled=false` from your library's pyproject.toml file.
- $${\color{green}PASS}$$ - The library passes CI recorded tests.
- $${\color{black}UNKNOWN}$$ - A result was not available for the most recent scheduled build. This could be due to an upstream pipeline failure preventing this particular check from running or a missing pipeline. Please ensure your pipeline builds are free of errors so that a Status for your library can be determined.

### Tests - Live:

[Tests - Live](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#nightly-live-checks) checks the status of the most recent (python - {service-directory} - tests) scheduled build of your library's live tests. To learn more about setting up live tests in our repo, see our [Testing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md). Possible statuses include:

- $${\color{red}FAIL}$$ - The library is failing live tests. Errors should be investigated and fixed promptly to ensure there are no issues with releasing the current state of your library.
- $${\color{yellow}DISABLED}$$ - The library has its CI disabled due to non-compliance with required checks. Please take action to re-enable and fix all checks highlighted in yellow. Once all checks are fixed, you can remove the `ci_enabled=false` from your library's pyproject.toml file.
- $${\color{green}PASS}$$ - The library passes live tests.
- $${\color{black}UNKNOWN}$$ - A result was not available for the most recent scheduled build. This could be due to an upstream pipeline failure preventing this particular check from running or a missing pipeline. Please ensure your pipeline builds are free of errors so that a Status for your library can be determined.

### Tests - Samples:

[Tests - Samples](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/sample_guide.md#test-run-samples-in-ci-live-tests) checks the status of the most recent (python - {service-directory} - tests) scheduled build of your library's live run against the samples directory. To learn more about setting up sample tests in our repo, see our [Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#running-samples). Possible statuses include:

- $${\color{red}FAIL}$$ - The library is failing sample tests. Errors should be investigated and fixed promptly to ensure there are no issues with releasing the current state of your library.
- $${\color{yellow}DISABLED}$$ - The library has its CI disabled due to non-compliance with required checks. Please take action to re-enable and fix all checks highlighted in yellow. Once all checks are fixed, you can remove the `ci_enabled=false` from your library's pyproject.toml file.
- $${\color{green}PASS}$$ - The library passes sample tests.
- $${\color{black}UNKNOWN}$$ - A result was not available for the most recent scheduled build. This could be due to an upstream pipeline failure preventing this particular check from running or a missing pipeline. Please ensure your pipeline builds are free of errors so that a Status for your library can be determined.

### Pyright:

[Pyright](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#pyright) is a static type checker, and is recommended to run on the source code of all libraries. To learn more about static type checking in our repo, see our [Static Type Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md). Possible statuses include:

- $${\color{red}FAIL}$$ - Pyright is enabled for the library and the library is failing the check. This will block the release of your library and should be fixed immediately.
- $${\color{yellow}DISABLED}$$ - Pyright is not enabled for your library in the pyproject.toml file.
- $${\color{yellow}WARNING}$$ -  Pyright is enabled for the library and the library passes the currently pinned version of Pyright in the repo, but is failing the next-pyright check (the next version of Pyright the repo will be bumped to in the near future). Please fix these errors before the merge date of the next version of Pyright or the errors will begin to fail the build (See [analyze_check_versions.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/analyze_check_versions.md)) to understand target dates for version bumps.
- $${\color{green}PASS}$$ - The library passes both current Pyright and next-pyright.
- $${\color{black}UNKNOWN}$$ - A result was not available for the most recent scheduled build. This could be due to an upstream pipeline failure preventing this particular check from running or a missing pipeline. Please ensure your pipeline builds are free of errors so that a Status for your library can be determined.

### Type check samples:

This `type_check_samples` option in the pyproject.toml is a recommended check that indicates whether type checkers should run on the library's samples/ directory. The actual status of the check is reported with the MyPy and Pyright (if enabled) status. Possible values include:

- $${\color{black}ENABLED}$$ - The library opts-in to running type checking on the samples directory.
- $${\color{black}DISABLED}$$ - The library does not run type checking on the samples directory.

### SLA - Bugs

`SLA - Bugs` reports a count of the total number of customer-reported bugs that have been open for the library for greater than 90 days. It uses this filter:

> is:open is:issue label:customer-reported label:Client -label:issue-addressed -label:question -label:needs-author-feedback -label:feature-request label:"[library-label]" created:"[<90days]"

Any number greater than zero indicates that the SLA has been violated. Please investigate and address these bugs immediately.

### SLA - Questions

`SLA - Questions` reports a count of the total number of customer-reported questions that have been open for the library for greater than 30 days. It uses this filter:

> is:open is:issue label:customer-reported label:Client -label:issue-addressed -label:bug -label:needs-author-feedback -label:feature-request label:"[library-label]" created:"[<30days]"

Any number greater than zero indicates that the SLA has been violated. Please investigate and address these questions immediately.

### Total customer-reported issues

This the total number of `customer-reported` labeled issues that are currently open for the library. This includes bugs, questions, and other types of issues. Please investigate and address these issues promptly.
