# Tool Usage Guide

As part of shipping SDKs that can be trusted by customers, the azure-sdk-for-python dev team maintains a suite of `checks` that can be utilized by developers to ensure predictable quality measures. These checks help determine whether a package meets the required quality standards for release or needs further work before it can be shipped. These `checks` are implemented in a single entrypoint within the local development package `eng/tools/azure-sdk-tools`. This package provides:
 
 - Templated package generation for mgmt packages
 -  The test-framework that all packages within this monorepo use (including record/playback integration)
 - A ton of CI related tasks and boilerplate
 - Static analysis code

A `tool` in this context is merely a single entrypoint provided by the `azpysdk` entrypoint in the `eng/tools/azure-sdk-tools` package.

## Available Tools

This repo is currently migrating all checks from a slower `tox`-based framework, to a lightweight implementation that uses `asyncio` to simultaneously run checks. This tools list is the current set that has been migrated from `tox` to the `azpysdk` entrypoint.

|tool|description|invocation|
|---|---|---|
|`pylint`| Runs `pylint` checks or `next-pylint` checks. (based on presence of `--next` argument)  | `azpysdk pylint .` |
|`mypy`| Runs `mypy` checks or `next-mypy` checks. (based on presence of `--next` argument)  | `azpysdk mypy --next=True  .` |
|`sphinx`| Generates a documentation website for the targeted packages. Runs `sphinx` or `next-sphinx` (based on presence of `--next` argument). | `azpysdk sphinx .` |
|`pyright`| Runs `pyright` checks or `next-pyright` checks. (based on presence of `--next` argument) | `azpysdk pyright .` |
|`black`| Runs `black` checks. | `azpysdk black .` |
|`verifytypes`| Runs `verifytypes` checks. | `azpysdk verifytypes .` |
|`ruff`| Runs `ruff` checks. | `azpysdk ruff .` |
|`apistub`| Generates an api stub for the package. | `azpysdk apistub .` |
|`bandit`| Runs `bandit` checks, which detect common security issues. | `azpysdk bandit .` |
|`verifywhl`| Verifies that the root directory in whl is azure, and verifies manifest so that all directories in source are included in sdist. | `azpysdk verifywhl .` |
|`verifysdist`| Verify directories included in sdist and contents in manifest file. Also ensures that py.typed configuration is correct within the setup.py. | `azpysdk verifysdist .` |
|`verify_keywords`| Verify that the keyword 'azure sdk' is present in the targeted package's keywords. | `azpysdk verify_keywords .` |
|`import_all`| Installs the package w/ default dependencies, then attempts to `import *` from the base namespace. Ensures that all imports will resolve after a base install and import. | `azpysdk import_all .` |
|`generate`| Regenerates the code. | `azpysdk generate .` |
|`breaking`| Checks for breaking changes. | `azpysdk breaking .` |

## Common arguments

### Globbing
The azpysdk is intended to be used from within the azure-sdk-for-python repository. A user can invoke

```
/azure-sdk-for-python/> azpysdk import_all azure-storage* # will run import_all for all packages starting with `azure-storage`

/azure-sdk-for-python/> azpysdk import_all azure-storage-blob,azure-core # invoke import_all for two packages

/azure-sdk-for-python/sdk/core/azure-core/> azpysdk import_all . # invoke import_all for the local package only
```

### Automatically isolating the environment

The targeted tool should be able to run in an isolated environment for a couple reasons:
-  When attempting to diagnose an issue, sometimes a user is best served by completely wiping their `venv` and starting over from scratch. Issues may stem from having additional deps downloaded that normally wouldn't be installed with the package.
- In `CI`, we _have_ to run in isolated virtual environments for some checks to allow processes like `multiple pytest` runs to invoke without accidentally stomping on each other's progress or hitting file contention errors. CI passes this flag by default from `dispatch_checks.py`.

To utilize this feature, add `--isolate` to any `azpysdk` invocation:

```bash
/> azpysdk import_all azure-storage-blob --isolate
# will install and run within a venv in `sdk/storage/azure-storage-blob/.venv_import_all/
```

## Prerequisite

- You need to have Python installed
- The monorepo requires a minimum of `python 3.9`, but `>=3.11` is required for the `sphinx` check due to compatibility constraints with external processes.
- You may optionally use the ["uv"](https://docs.astral.sh/uv/) tool, which is fast and handles Python version and venv creation automatically.

## Initial setup

- Go to the folder of the package you're working on, for instance `sdk/contoso/azure-contoso`

### Setup with uv

`uv venv`

```bash
# for WSL
source .venv/bin/activate 

# for Windows
.venv\Scripts\activate 
```

`uv pip install -r dev_requirements.txt`

### Setup with pip/python

`python -m venv .venv`

```bash
# for WSL
source .venv/bin/activate 

# for Windows
.venv\Scripts\activate 
```

`pip install -r dev_requirements.txt`

## Using the CLI

```bash
# You can call the command directly if you activated the venv
azpysdk <tool_name>
```

## Advanced scenario

### Using different Python version

You can locally test different Python versions to check compatibility with all the required Python versions.

Note that this is optional, and you can rely on CI to test python versions.

#### With uv

You can specify a Python version upon venv creation:
`uv venv --python 3.11`

#### With Python

You need to install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation), which lets you easily switch between multiple versions of Python.

To switch Python versions:
```
pyenv install 3.10
pyenv global 3.10
```