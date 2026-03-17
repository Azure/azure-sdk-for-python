# Documentation

This folder contains documentation for the Azure SDK for Python repository.

## General

- [Python Version Support Policy](python_version_support_policy.md) - Supported Python versions and end-of-support dates
- [Engineering System Checks](eng_sys_checks.md) - What a standard `ci.yml` will execute
- [Deprecation Process](deprecation_process.md) - How to deprecate a package
- [Repository Health Status](repo_health_status.md) - Library health status definitions
- [ESRP Release](esrp_release.md) - ESRP release process
- [Request Builders](request_builders.md) - Request builder pattern documentation
- [Send Request](send_request.md) - Send request pattern documentation
- [Analyze Check Versions](analyze_check_versions.md) - Check version analysis
- [Tool Usage Guide](tool_usage_guide.md) - How to use the `azpysdk` CLI tool

## Developer Documentation

See the [dev](dev/) folder for documentation aimed at developers of SDK libraries:

- [Developer Setup](dev/dev_setup.md) - How to create a development environment
- [Release](dev/release.md) - How to release a package
- [Packaging](dev/packaging.md) - How to organize packaging information
- [Changelog Updates](dev/changelog_updates.md) - How to document package changes
- [Testing](dev/tests.md) - How to write unit and functional tests
- [Advanced Testing](dev/tests-advanced.md) - Advanced testing topics
- [Docstrings](dev/docstring.md) - How to document an SDK
- [Type Checking](dev/static_type_checking.md) - Type hints and type checking ([Cheatsheet](dev/static_type_checking_cheat_sheet.md))
- [Pylint](dev/pylint_checking.md) - Pylint checking guidance
- [Sample Guide](dev/sample_guide.md) - How to write SDK samples
- [Performance Testing](dev/perfstress_tests.md) - How to write and run perf tests
- [Debug Guide](dev/debug_guide.md) - Debugging tips
- [Code Snippets](dev/code_snippets.md) - How to include code snippets in docs

### Troubleshooting & Common Issues

- [Common Issues and FAQ](dev/common_issues.md) - Common SDK issues and how to resolve them
- [Test Proxy Troubleshooting](dev/test_proxy_troubleshooting.md) - Test proxy issues

### Code Generation

- [Dataplane SDK Generation](dev/dataplane_generation.md) - Generate a dataplane SDK from a TypeSpec definition
- [Management Plane](dev/mgmt/) - Management plane SDK documentation

### Additional Topics

- [Customize Long Running Operations](dev/customize_long_running_operation.md) - LRO customization
- [CredScan Process](dev/credscan_process.md) - Credential scanning
- [Recording Migration Guide](dev/recording_migration_guide.md) - Migrating test recordings
- [Engineering Assumptions](dev/engineering_assumptions.md) - SDK engineering assumptions
- [Conda Builds](dev/conda-builds.md) / [Release](dev/conda-release.md) / [Dev Release](dev/conda-release-dev.md) - Conda packaging

## Sphinx Reference Documentation

The [sphinx](sphinx/) folder contains the documentation source for https://azure.github.io/azure-sdk-for-python/.
