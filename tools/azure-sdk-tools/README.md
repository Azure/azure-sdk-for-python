# Azure SDK Tools

This package is intended for usage in direct combination with the azure-sdk-for-python repo. It provides:

- Common test classes and functionality
  - `AzureTestCase` used for common record/playback functionality
  - `EnvironmentVariablePreparer`  
  - Test-Proxy Shim
- `Build` entrypoint
  - Previously in `scripts/devops_tasks/build_packages.py`
- `Versioning` entrypoints

Overview

<insert markdown table containing modules>

For the "script" entrypoints provided by the package, all should either be run from somewhere within the azure-sdk-for-python repository. If not that, an argument `--repo` should be provided that points to the repo root.

## Building Azure SDK Packages

Script entrypoint: `sdk_build`


## Azure SD