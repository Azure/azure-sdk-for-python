# Azure SDK Tools

This package is intended for usage in direct combination with the azure-sdk-for-python repo. It provides:

- Common test classes and functionality
  - `AzureRecordedTestCase` used for common record/playback functionality
  - `EnvironmentVariablePreparer` to allow recorded tests access to `New-TestResources.ps1`-created resources.
  - Test-Proxy Shim/Startup capabilities
- `Build` entrypoint
  - Previously in `scripts/devops_tasks/build_packages.py`
- `Versioning` entrypoints
  - Previously in `eng/scripts/versioning/*.py`

- [Azure SDK Tools](#azure-sdk-tools)
  - [Overview](#overview)
  - [Building Azure SDK Packages](#building-azure-sdk-packages)
  - [Using "versioning" modules](#using-versioning-modules)
    - [`sdk_set_dev_version`](#sdk_set_dev_version)
    - [sdk_set_version](#sdk_set_version)
    - [sdk_increment_version](#sdk_increment_version)
  - [Relevant Environment Variables](#relevant-environment-variables)

## Overview

| Module | Description |
|---|---|
| `azpysdk` | CI check entrypoints and accompanying implementations. |
| `ci_tools` | Various azure-sdk-for-python specific build and test abstractions. Heavily used in CI functionality. |
| `devtools_testutils` | Primary location for test classes, pytest fixtures, and test-proxy integration. |
| `packaging_tools` | Templated package generator for management packages. |
| `parsing` | Parse information _about_ python packages at rest on disk. Used to interrogate the monorepo to find relevant packages. |
| `pypi_tools` | Helper functionality build upon interactions with PyPI. |
| `scenario` | Functionality to do with installing packages constrained by environmental and input factors. Heavily used in `mindependency` and `latestdependency` CI checks. |
| `testutils` | Backwards compatible extension of test classes. |

**PLEASE NOTE.** For the "script" entrypoints provided by the package, all should either be run from somewhere **within** the azure-sdk-for-python repository. Barring that, an argument `--repo` should be provided that points to the repo root if a user must start the command from a different CWD.

## Usage in automation

This package is used externally in two places. Changes to `azure-sdk-tools`, especially location, should follow-up to ensure these usages are NOT broken.

- In `typespec` package generation.
  - [This PR](https://github.com/microsoft/typespec/pull/8281) updates `packages/http-client-python/generator/pygen/codegen/templates/packaging_templates/dev_requirements.txt.jinja2` to match the expected location of `azure-sdk-tools`.
- As part of `azure-rest-api-specs` verification automation.
  - [This build](https://dev.azure.com/azure-sdk/internal/_build?definitionId=7423) calls the azure-sdk-for-python script `scripts/automation_generate.sh`, which calls into `scripts/dev_setup.py`.

## Building Azure SDK Packages

After installing azure-sdk-tools, package build functionality is available through `sdk_build`.

```text
usage: sdk_build [-h] [-d DISTRIBUTION_DIRECTORY] [--service SERVICE] [--pkgfilter PACKAGE_FILTER_STRING]
                 [--devbuild IS_DEV_BUILD] [--inactive] [--produce_apiview_artifact] [--repo REPO] [--build_id BUILD_ID]
                 [glob_string]

This is the primary entrypoint for the "build" action. This command is used to build any package within the azure-sdk-for-
python repository.

positional arguments:
  glob_string           A comma separated list of glob strings that will target the top level directories that contain
                        packages. Examples: All == "azure-*", Single = "azure-keyvault"

options:
  -h, --help            show this help message and exit
  -d DISTRIBUTION_DIRECTORY, --distribution-directory DISTRIBUTION_DIRECTORY
                        The path to the distribution directory. Should be passed $(Build.ArtifactStagingDirectory) from the
                        devops yaml definition.If that is not provided, will default to env variable SDK_ARTIFACT_DIRECTORY
                        -> <calculated_repo_root>/.artifacts.
  --service SERVICE     Name of service directory (under sdk/) to build.Example: --service applicationinsights
  --pkgfilter PACKAGE_FILTER_STRING
                        An additional string used to filter the set of artifacts by a simple CONTAINS clause. This filters
                        packages AFTER the set is built with compatibility and omission lists accounted.
  --devbuild IS_DEV_BUILD
                        Set build type to dev build so package requirements will be updated if required package is not
                        available on PyPI
  --inactive            Include inactive packages when assembling artifacts. CI builds will include inactive packages as a
                        way to ensure that the yml controlled artifacts can be associated with a wheel/sdist.
  --produce_apiview_artifact
                        Should an additional build artifact that contains the targeted package + its direct dependencies be
                        produced?
  --repo REPO           Where is the start directory that we are building against? If not provided, the current working
                        directory will be used. Please ensure you are within the azure-sdk-for-python repository.
  --build_id BUILD_ID   The current build id. It not provided, will default through environment variables in the following
                        order: GITHUB_RUN_ID -> BUILD_BUILDID -> SDK_BUILD_ID -> default value.
```

Some common invocations.

```bash

# build all package that have form azure-storage*. Set dev version for file + requirements before building.
sdk_build azure-storage* --devbuild=True

# build everything under sdk/core, dump into target directory
sdk_build azure* --service=core -d "<artifact_folder>"
```

## Using "versioning" modules

On top of assembling packages, azure-sdk-tools also can be used to complete various tasks with respect to version "maintenance". There are three primary entrypoints, and each fulfills a purpose in the repository.

### `sdk_set_dev_version`

```text
usage: sdk_set_dev_version [-h] [--service SERVICE] -b BUILD_ID [--repo REPO] [glob_string]

Increments version for a given package name based on the released version

positional arguments:
  glob_string           A comma separated list of glob strings that will target the top level directories that contain packages.Examples: All = "azure-*",
                        Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"

optional arguments:
  -h, --help            show this help message and exit
  --service SERVICE     name of the service for which to set the dev build id (e.g. keyvault)
  -b BUILD_ID, --build-id BUILD_ID
                        id of the build (generally of the form YYYYMMDD.r) dot characters(.) will be removed
  --repo REPO           Where is the start directory that we are building against? If not provided, the current working directory will be used. Please
                        ensure you are within the azure-sdk-for-python repository.
```

### sdk_set_version

```text
usage: sdk_set_version [-h] --package-name PACKAGE_NAME --new-version NEW_VERSION --service SERVICE [--release-date RELEASE_DATE]
                       [--replace-latest-entry-title REPLACE_LATEST_ENTRY_TITLE] [--repo REPO]
                       [glob_string]

Increments version for a given package name based on the released version

positional arguments:
  glob_string           A comma separated list of glob strings that will target the top level directories that contain packages.Examples: All = "azure-*",
                        Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"

optional arguments:
  -h, --help            show this help message and exit
  --package-name PACKAGE_NAME
                        name of package (accepts both formats: azure-service-package and azure_service_package)
  --new-version NEW_VERSION
                        new package version
  --service SERVICE     name of the service for which to set the dev build id (e.g. keyvault)
  --release-date RELEASE_DATE
                        date in the format "yyyy-MM-dd"
  --replace-latest-entry-title REPLACE_LATEST_ENTRY_TITLE
                        indicate if to replace the latest changelog entry
  --repo REPO           Where is the start directory that we are building against? If not provided, the current working directory will be used. Please
                        ensure you are within the azure-sdk-for-python repository.
```

### sdk_increment_version

```text
usage: sdk_increment_version [-h] --package-name PACKAGE_NAME --service SERVICE [--repo REPO] [glob_string]

Increments version for a given package name based on the released version

positional arguments:
  glob_string           A comma separated list of glob strings that will target the top level directories that contain packages.Examples: All = "azure-*",
                        Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"

optional arguments:
  -h, --help            show this help message and exit
  --package-name PACKAGE_NAME
                        name of package (accepts both formats: azure-service-package and azure_service_package)
  --service SERVICE     name of the service for which to set the dev build id (e.g. keyvault)
  --repo REPO           Where is the start directory that we are building against? If not provided, the current working directory will be used. Please
                        ensure you are within the azure-sdk-for-python repository.
```

## Using `Parsing` Modules

```python
from ci_tools.parsing import ParsedSetup

path_to_package = "path/to/your/possible/python/package"

pkg_metadata = ParsedSetup.from_path(path_to_package)

# pkg_metadata will contain all metadata about the package, EG "name", "version", "python_requires", "dependencies"
# any information that any of our checks would need to operate properly.
```

## Writing additional `checks` within `azpysdk`

To add a new check to `azpysdk`, follow these steps.

- Create a new file within `azpysdk`. Name it after what your check will be.
- When creating a class for your new check, you should inherit from the class `Check` within the `azpysdk` namespace.
- Implement the required functions within the `Check` abstract class in your new check class.

This is a commented implementation providing the reasoning for implementation alongside the code.

```python
class my_check(Check):
    def __init__(self) -> None:
        super().__init__()


    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register `my_check`. `my_check` does X and Y while doing Z.

        This function will be used to add your command to the set of commands being shown through the `azpysdk` entrypoint.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("whl", parents=parents, help="Run the `my_check` check")
        p.set_defaults(func=self.run)
        # Add any additional arguments specific to your check here (do not re-add common handled by parents. See `main.py` build_parser to see the common parents provided to the checks)

    def run(self, args: argparse.Namespace) -> int:
        """This is the recommended """
        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            pkg_dir = parsed.folder
            pkg_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, pkg)
            # the rest of the check should use executable, not sys.executable
            # if a staging area is needed use staging_directory
            print(f"Processing {pkg_name} for my_check")
```

- Once the new check has been created, register it in `azpysdk/main.py` on line 58. This will likely be automated by decorator in the near future but this is out how it should be done for now.

```python
# ...other registrations above
my_check().register(subparsers, [common])
```

- Your command will now be available through `azpysdk`

```bash
/> `azpysdk mycheck azure-storage*`

/> cd sdk/storage/azure-storage
sdk/storage/azure-storage/> azpysdk mycheck
```

## Relevant Environment Variables

This package honors a few different environment variables as far as logging, artifact placement, etc.

| Environment Variable | Description |
|---|---|
| `SDK_DEV_BUILD_IDENTIFIER` | Defaults to value "a". The character prefix before the build number when setting dev build versions. |
| `SDK_BUILD_ID` | When setting dev version, the current build number is passed to the function as an argument. For a local repro, that can be unwieldy, so the value from this environment variable is fallen back on. |
| `SDK_ARTIFACT_DIRECTORY` | If a given command invocation outputs to an artifact directory, and that directory is NOT provided via CLI args, azure-sdk-tools will fall back to this variable value. |

This set of environment variables will grow as more of the common functionality from azure-sdk-for-python is refactored into azure-sdk-tools.
