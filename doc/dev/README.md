# Developer Documentation

This folder contains documentation for developers of SDKs: internal teams at Microsoft, or advanced contributors.

## Getting Started

- [Developer Set-Up](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/dev_setup.md) - How to create a development environment for this repo
- [Release](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/release.md) - How to release a package when ready
- [Packaging](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/packaging.md) - How to organize packaging information for packages under `azure`
- [Changelog](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/changelog_updates.md) - How to document package changes using Chronus (for packages with `pyproject.toml`)
- [Package Versioning](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/package_version/package_version_rule.md) - Version numbering rules

## Testing

- [Testing](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) - How to write unit and functional tests for a library
- [Advanced Testing](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests-advanced.md) - Advanced testing topics
- [Performance Testing](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/perfstress_tests.md) - How to write and run perf tests
- [Recording Migration Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md) - Migrating test recordings
- [CredScan Process](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/credscan_process.md) - Credential scanning

## Code Quality & Documentation

- [Docstrings](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/docstring.md) - How to document an SDK (API View) and our documentation at [MS Learn][ms_learn] and the [azure.github.io][azure_github_io] site
- [Type Hints and Type Checking](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md) / [Cheatsheet](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md) - How to add type hints and run type checking
- [Pylint](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md) - Pylint checking guidance
- [Sample Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/sample_guide.md) - How to write SDK samples
- [Code Snippets](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/code_snippets.md) - How to include code snippets in docs

## Troubleshooting

- [Common Issues and FAQ](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/common_issues.md) - Common SDK issues and how to resolve them
- [Test Proxy Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_troubleshooting.md) - Test proxy issues
- [Debug Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/debug_guide.md) - Debugging tips
- [Resolve Issues Effectively](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/issues/resolve_issues_effectively.md) - How to triage and resolve customer issues
- [Find SDK in CLI Command](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/find_sdk/find_sdk_in_cli_command.md) - Mapping CLI commands to SDK packages

## Code Generation

- [Dataplane SDK Generation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/dataplane_generation.md) - Generate a dataplane SDK from a TypeSpec definition
- [Management Plane](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/) - Management plane SDK documentation
- [Customize Long Running Operations](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/customize_long_running_operation.md) - LRO customization

## AI-Assisted Development

- [AI Prompt Workflow](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/ai/ai_prompt_workflow.md) - Using AI agents for SDK development
- [TypeSpec Generation with AI](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/ai/typespec_generation.md) - AI-assisted TypeSpec generation

## Conda

- [Conda Builds](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-builds.md) - Conda packaging
- [Conda Release](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-release.md) - Conda release process
- [Conda Dev Release](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-release-dev.md) - Conda dev release process

<!-- links -->
[ms_learn]: https://learn.microsoft.com/python/api/overview/azure/appconfiguration-readme?view=azure-python
[azure_github_io]: https://azure.github.io/azure-sdk-for-python/
