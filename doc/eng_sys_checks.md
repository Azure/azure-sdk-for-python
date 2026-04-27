# Azure SDK for Python - Engineering System

- [Azure SDK for Python - Engineering System](#azure-sdk-for-python---engineering-system)
  - [Targeting a specific package at build queue time](#targeting-a-specific-package-at-build-queue-time)
  - [Skipping a check at build queue time](#skipping-a-check-at-build-queue-time)
  - [Skipping entire sections of builds](#skipping-entire-sections-of-builds)
  - [The pyproject.toml](#the-pyprojecttoml)
    - [Required Metadata](#required-metadata)
    - [Coverage Enforcement](#coverage-enforcement)
    - [Overriding the Python Version for Analyze Checks](#overriding-the-python-version-for-analyze-checks)
  - [Environment variables important to CI](#environment-variables-important-to-ci)
    - [Atomic Overrides](#atomic-overrides)
    - [Enable test logging in CI pipelines](#enable-test-logging-in-ci-pipelines)
  - [How CI Checks Are Organized](#how-ci-checks-are-organized)
  - [Static Analysis Checks](#static-analysis-checks)
    - [MyPy](#mypy)
    - [Pyright](#pyright)
    - [Verifytypes](#verifytypes)
    - [Pylint](#pylint)
    - [Sphinx and docstring checker](#sphinx-and-docstring-checker)
    - [Bandit](#bandit)
    - [ApiStubGen](#apistubgen)
    - [black](#black)
    - [Change log verification](#change-log-verification)
    - [CSpell](#cspell)
    - [verifywhl](#verifywhl)
    - [verifysdist](#verifysdist)
    - [verify\_keywords](#verify_keywords)
  - [Install and Test Checks](#install-and-test-checks)
    - [PR Validation](#pr-validation)
      - [whl](#whl)
      - [sdist](#sdist)
      - [mindependency](#mindependency)
    - [Nightly and Release](#nightly-and-release)
      - [import\_all](#import_all)
      - [whl\_no\_aio](#whl_no_aio)
      - [Latest Dependency Test](#latest-dependency-test)
    - [Nightly Scheduled Only](#nightly-scheduled-only)
      - [Dev Feed Test](#dev-feed-test)
      - [Regression Test](#regression-test)
      - [Autorest Automation](#autorest-automation)
  - [Weekly Analyze Checks](#weekly-analyze-checks)
    - [Ruff](#ruff)
    - [Next-Generation Checks](#next-generation-checks)

This document describes every CI check run against Azure SDK for Python packages — what each one does, when it runs, and how to reproduce it locally.

See the [contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md#building-and-testing) for an introduction to `azpysdk`, and the [Tool Usage Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md) for a deeper look at the underlying tooling and local build reproduction.

Every build runs in one of two modes: `Pull Request` or `Nightly Scheduled`. Both modes share the same build definition — nightly builds simply enable additional, longer-running checks on top of everything that runs in PR validation.

Example PR build:

![res/job_snippet.png](res/job_snippet.png)

| Job | When it runs |
|---|---|
| `Analyze` | Every PR and every nightly build |
| `Test <platform>_<pyversion>` | Every PR (reduced matrix) and every nightly build (full matrix) |

## Targeting a specific package at build queue time

In both `public` and `internal` projects, all builds allow a filter to be introduced at build time to narrow the set of packages build/tested.

1. Click `Run New` on your target build.
2. Before clicking `run` against `main` or your target commit, click `Variables` and add a variable. Add variable `BuildTargetingString` with value of a valid glob string.
   1. For example, setting filter string `azure-mgmt-*` will filter a build to only management packages. A value of `azure-keyvault-secrets` will result in only building THAT specific package.
3. Once it's set, run the build!

## Skipping a check at build queue time

All build definitions allow choice at queue time as to which checks actually run during the test phase.

1. Find your target service `internal` build.
2. Click `Run New`.
3. Before clicking `run` against `main` or your target commit, click `Variables` and add a variable of name `ChecksOverride`. The value should be a comma separated list of checks that you want to run in the test phase.
4. Once it's set, run the build!

The screenshot above narrows the default PR build set (`whl`, `sdist`, `mindependency`) to a specific subset.

![res/queue_time_variable.png](res/queue_time_variable.png)

Any combination of valid check names will work. Reference either this document, `azpysdk -h`, or the [Tool Usage Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md) to find what options are available.

## Skipping entire sections of builds

Setting any of the following variables to `true` at queue time suppresses the corresponding job or step. Suppressing `Skip.CreateApiReview` before a release should be cleared with your lead first.

| Variable | Effect |
|---|---|
| `Skip.CreateApiReview` | Suppress APIView stub creation in the `build` job. |
| `Skip.Analyze` | Skip the `analyze` job entirely. |
| `Skip.Test` | Skip all `test` jobs. |
| `Skip.TestConda` | Skip the Conda `test` job. |
| `Skip.ApiStubGen` | Omit API stub generation in the `build` job. |
| `Skip.VerifySdist` | Omit `twine check` of source distributions in the `build` job. |
| `Skip.VerifyWhl` | Omit `twine check` of wheels in the `build` job. |
| `Skip.Bandit` | Omit `bandit` in the `analyze` job. |
| `Skip.Pylint` | Omit `pylint` in the `analyze` job. |
| `Skip.VerifyTypes` | Omit `verifytypes` in the `analyze` job. |
| `Skip.Pyright` | Omit `pyright` in the `analyze` job. |
| `Skip.BreakingChanges` | Skip the breaking-change detection step. |
| `Skip.MyPy` | Omit `mypy` in the `analyze` job. |
| `Skip.AnalyzeDependencies` | Omit the dependency analysis step in the `analyze` job. |
| `Skip.VerifyDependencies` | Omit the PyPI pre-release dependency check in the `build` job. |
| `Skip.KeywordCheck` | Omit keyword validation in the `build` job. |
| `Skip.Black` | Omit `black` formatting check in the `analyze` job. |
| `Skip.SpellCheck` | Omit CSpell spell-checking in the `analyze` job. |

## The pyproject.toml

Starting with [this pr](https://github.com/Azure/azure-sdk-for-python/pull/28345), which checks apply to which packages are now **established** in a `pyproject.toml`, right next to each package's `setup.py`. This not only allows devs to fine-tune which checks that are applied at a package-level, but also seriously reduces confusion as to which checks apply when.

We default to **enabling** most of our checks like `pylint`, `mypy`, etc. Due to that, most `pyproject.toml` settings will likely be **disabling** checks.

Here's an example:

```toml
# from sdk/core/azure-common/pyproject.toml, which is a legacy package
# as a result, all of these checks are disabled
[tool.azure-sdk-build]
type_check_samples = false
verifytypes = false
pyright = false
mypy = false
pylint = false
regression = false
black = false
```

If a package does not yet have a `pyproject.toml`, creating one with just the section `[tool.azure-sdk-build]` will do no harm to the release of the package in question.

### Required Metadata

Packages with a stable GA release must have a `[tool.azure-sdk-conda]` section in their `pyproject.toml`.
- This section defines if the package is released individually to Conda, or grouped with other packages in one release bundle (see [conda-release.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-release.md)).
- The `[tool.azure-sdk-conda]` table **must** include an `in_bundle` key (boolean) indicating whether the package is part of a bundle. When `in_bundle = true`, a `bundle_name` key is also **required** so the conda tooling can map the package into the correct bundle.
- The presence and correctness of these keys is enforced by the `verifywhl` CI check. Service teams are responsible for updating this metadata.

Here are examples:

```toml
# Package is released to Conda individually
[tool.azure-sdk-conda]
in_bundle = false
```

```toml
# Package is released within the `azure-communication` bundle
[tool.azure-sdk-conda]
in_bundle = true
bundle_name = "azure-communication"
```

### Coverage Enforcement

This repository supports enforcement of an absolute coverage % per package. Set:

```
[tool.azure-sdk-build]
absolute_cov = true
absolute_cov_percent = 75.00
```

After it is implemented, the `relative_cov` key will enable the prevention of **negative** code coverage contributions.

### Overriding the Python Version for Analyze Checks

<a name="analyze-python-version"></a>

By default, the analyze checks (mypy, pylint, pyright, etc.) run against an agreed minimum Python version (currently 3.10). A package can request a different Python version for its analyze checks by setting `analyze_python_version` in its `pyproject.toml`:

```toml
[tool.azure-sdk-build]
analyze_python_version = "3.11"
```

This setting is read by `eng/scripts/dispatch_checks.py` and is passed to `azpysdk` via the `--python` flag (which requires `--isolate` and `uv`). This is useful for packages that use newer syntax or type features that require a more recent Python interpreter.

> **Note:** This setting only affects the Python interpreter version used for the analyze venv; it does not change the minimum supported Python version declared in `setup.py`/`pyproject.toml`.
>
> **Warning:** This override applies to _all_ analyze checks dispatched by `dispatch_checks.py`, including `apistub`. The `apistub` tool currently requires Python < 3.11 (`PYTHON_VERSION_LIMIT = (3, 11)` in `azpysdk/apistub.py`). Do not set `analyze_python_version` to `3.11` or higher for packages that still run `apistub` through the standard dispatched analyze flow.

## Environment variables important to CI

A handful of environment variables influence how `azpysdk` behaves both in CI and locally. The tooling reads these automatically — no extra flags are required.

| Variable | Effect |
|---|---|
| `TF_BUILD` | Signals that the build is running in CI. When set, all relative dev dependencies are pre-built before checks run. |
| `PREBUILT_WHEEL_DIR` | When set, checks look in this directory for a pre-built wheel instead of building one fresh. |
| `PIP_INDEX_URL` / `UV_DEFAULT_INDEX` | Standard pip/uv index override. Set to the public dev feed during nightly alpha builds. |

### Atomic Overrides

Packages with classifier `Development Status :: 7 - Inactive`, are **not** built by default and as such normal `checks` like `mypy` and `pylint` are also not run against them. Older "core" packages like `azure-common` and `azure-servicemanagement-legacy` are present, but excluded from the build due to this restriction.

Additionally, packages with the pyproject.toml option `ci_enabled = false` will **skip** normal checks and tests. This is used for packages that are not yet compliant with certain CI checks. If `ci_enabled = false` is present in the package's pyproject.toml, it will be blocked from releasing until it is removed and all required CI checks pass.

To temporarily **override** this restriction, a dev need only set the queue time variable: `ENABLE_PACKAGE_NAME`. The `-` in package names should be replaced by an `_`, as that is how the environment variable will be set on the actual CI machine anyway.

- `ENABLE_AZURE_COMMON=true`
- `ENABLE_AZURE_SERVICEMANAGEMENT_LEGACY=true`

This same methodology also applies to _individual checks_ that run during various phases of CI. Developers can use a queue time variable of format `PACKAGE_NAME_CHECK=true/false`.

The name that you should use is visible based on the check name. Here are a few examples of enabling/disabling checks:

- `AZURE_SERVICEBUS_PYRIGHT=true` <-- enable a check that normally is disabled in `pyproject.toml`
- `AZURE_CORE_PYLINT=false` <-- disable a check that normally runs

### Enable test logging in CI pipelines

You can enable test logging in a pipeline by setting the queue time variable `PYTEST_LOG_LEVEL` to the desired logging [level](https://docs.python.org/3/library/logging.html#logging-levels). For example,

`PYTEST_LOG_LEVEL=INFO`

This also works locally by setting the `PYTEST_LOG_LEVEL` environment variable.

Note that if you want DEBUG level logging with sensitive information unredacted in the test logs, then you still must pass `logging_enable=True` into the client(s) being used in tests.

## How CI Checks Are Organized

Azure SDK for Python CI checks fall into two distinct categories with different triggering behavior.

**Static analysis** runs on every package directly touched by a pull request, on every PR and every nightly build. These checks are stateless — they inspect source code and packaging metadata without building or installing anything — and are fast enough to run universally without gating the rest of the pipeline.

**Install and test checks** build a distribution of the package, install it into a clean virtual environment, and drive the test suite with `pytest`. These are resource-intensive and slower, so the set that runs depends on the build trigger.

There are three distinct build modes, each with different behavior:

**PR Validation** — triggered by pull requests against the public project. Runs static analysis on all changed packages and a reduced install-and-test set (`PR_BUILD_SET`). Packages use their current in-repo versions.

**Nightly CI** — triggered on a schedule against the internal project (`Build.Reason == Schedule`). The `SetDevVersion` variable is set to `true`, which stamps all package versions with a dev/alpha suffix and publishes them to the internal dev feed. Runs the full install-and-test set plus additional scheduled-only checks (`devtest`, `regression`).

**Release** — manually queued against the internal project. `SetDevVersion` is `false`/unset, so packages use release versions and no dev feed publish occurs. Runs the same full install-and-test set as nightly CI, but skips the dev-only checks (`devtest`, `regression`).

In all three modes, pip (and uv) are authenticated against the Azure Artifacts dev feed via `auth-dev-feed.yml`, which configures `PIP_INDEX_URL` and `UV_DEFAULT_INDEX` to the feed with PyPI as an upstream source. All package installs go through this feed regardless of build mode.

The canonical definition of which install-and-test checks run in each mode lives in [`eng/scripts/set_checks.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/scripts/set_checks.py):

| Check | PR | Nightly CI | Release |
|---|---|---|---|
| `whl` | ✓ | ✓ | ✓ |
| `sdist` | ✓ | ✓ | ✓ |
| `mindependency` | ✓ | ✓ | ✓ |
| `import_all` | — | ✓ | ✓ |
| `whl_no_aio` | — | ✓ | ✓ |
| `latestdependency` | — | ✓ | ✓ |
| `devtest` | — | ✓ | — |
| `regression` | — | ✓ | — |

Static analysis checks always run against **Python 3.10** (configured via `PythonVersion` in `eng/pipelines/templates/variables/globals.yml`).

The install-and-test checks run across the Python version and platform matrix defined in [`platform-matrix.json`](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/pipelines/templates/stages/platform-matrix.json).

## Static Analysis Checks

Static analysis runs on every changed package in every PR and every nightly build. The checks in this section primarily inspect source code and packaging metadata, and also include distribution verification checks (`verifywhl`, `verifysdist`) that build and inspect package artifacts without installing them. Together they cover type correctness, code style, security, documentation quality, and distribution hygiene.

### MyPy

<a name="mypy"></a>

[`MyPy`](https://pypi.org/project/mypy/) performs static type checking across the package, flagging annotation inconsistencies and type mismatches that would cause runtime errors. It runs against Python 3.10 by default and respects `py.typed` markers and stub files.

To run locally:

```bash
azpysdk mypy .
```

### Pyright

<a name="pyright"></a>

[`Pyright`](https://github.com/microsoft/pyright/) is Microsoft's static type checker. It offers faster incremental analysis and stricter inference than MyPy, and the two tools catch different classes of type errors — running both provides broader coverage.

To run locally:

```bash
azpysdk pyright .
```

### Verifytypes

<a name="verifytypes"></a>

[`Verifytypes`](https://github.com/microsoft/pyright/blob/main/docs/typed-libraries.md#verifying-type-completeness) uses Pyright to score a package's _type completeness_ — the percentage of the public API surface that is fully annotated. Packages marked `py.typed` are expected to maintain a high completeness score; regressions here will fail this check.

To run locally:

```bash
azpysdk verifytypes .
```

### Pylint

<a name="pylint"></a>

[`Pylint`](https://pypi.org/project/pylint/) enforces the Azure SDK [custom lint rules](https://github.com/Azure/azure-sdk-tools/tree/main/tools/pylint-extensions/azure-pylint-guidelines-checker) on top of standard Python style guidelines. In CI it runs using the Python version configured for analyze checks (3.10 by default, or the value of `analyze_python_version` if set), so that version must be available locally to reproduce the check.

To run locally:

```bash
azpysdk pylint .
```

### Sphinx and docstring checker

<a name="sphinx-and-docstring-checker"></a>

[`Sphinx`](https://www.sphinx-doc.org/en/master/) builds the package documentation and attaches the output to every PR. The build runs in strict mode, so any invalid or malformed docstring causes the job to fail — this keeps the published reference documentation well-formed and consistent.

> **Note:** Sphinx requires Python >= 3.11 due to compatibility constraints with external processes.

To run locally:

```bash
azpysdk sphinx .
```

### Bandit

<a name="bandit"></a>

[`Bandit`](https://bandit.readthedocs.io/en/latest/) scans Python source code for common security vulnerabilities — hard-coded credentials, use of weak hash functions, unsafe deserialization patterns, and similar issues. It runs against every package in the analyze job.

To run locally:

```bash
azpysdk bandit .
```

### ApiStubGen

<a name="apistubgen"></a>

`ApiStubGen` generates an API stub from package source code and uploads it to [`APIView`](https://apiview.dev/) for reviewer sign-off. Running it in the analyze job ensures that every change produces a valid, reviewable stub and that the public API surface is visible before merging. The tool also applies a set of built-in lint rules specific to Azure SDK API conventions.

To run locally:

```bash
azpysdk apistub .
```

### black

<a name="black"></a>

[`black`](https://pypi.org/project/black) is an opinionated, deterministic code formatter for Python. It is **opt-in** — packages must explicitly enable it.

#### Opt-in to formatting validation

Add `black = true` to the `[tool.azure-sdk-build]` section of your `pyproject.toml`:

```toml
[tool.azure-sdk-build]
black = true
```

#### Running locally

```bash
azpysdk black .
```

### Change log verification

<a name="change-log-verification"></a>

Validates that a changelog entry exists for the package's current version and that it follows the required format. Any package missing a changelog entry for its declared version will fail this check. Guidelines for maintaining the changelog are documented [here](https://azure.github.io/azure-sdk/policies_releases.html#change-logs/).

### CSpell

<a name="cspell"></a>

[`CSpell`](https://cspell.org/) is a spell checker that runs against package source code to catch common spelling errors. It checks Python source files, documentation, and other text content in the package. For more details, see the [Spelling Check Scripts README](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/common/spelling/README.md).

Spell check configuration can be customized at two levels. Repository-wide terms can be added to [`.vscode/cspell.json`](https://github.com/Azure/azure-sdk-for-python/blob/main/.vscode/cspell.json), while service-specific terms can be added to a `cspell.json` or `cspell.yaml` file in the service directory. In either case, words that are domain-specific or intentionally spelled differently can be added to the `words` list.

If you encounter a CSpell failure in CI, you can resolve it by:

1. Fixing the spelling error in your code or documentation.
2. Adding the word to your service-level `cspell.json` or `cspell.yaml` file if the word is intentional (e.g., a domain-specific term). If this file does not exist, you can create it.
3. Adding the word to [`.vscode/cspell.json`](https://github.com/Azure/azure-sdk-for-python/blob/main/.vscode/cspell.json) if it is a common term that applies across the repository.
4. Adding an inline `cspell:ignore` comment for one-off exceptions:
   ```python
   # cspell:ignore specialword
   ```

### verifywhl

<a name="verifywhl"></a>

Verifies that the root directory in the wheel is `azure`, and validates the wheel manifest to ensure all expected directories and files are included. Also checks that `[tool.azure-sdk-conda]` metadata is present and correct in `pyproject.toml` for packages with stable releases.

To run locally:

```bash
azpysdk verifywhl .
```

### verifysdist

<a name="verifysdist"></a>

Verifies that directories included in the sdist match the manifest file, and ensures that `py.typed` configuration is correct within `setup.py`.

To run locally:

```bash
azpysdk verifysdist .
```

### verify\_keywords

<a name="verify-keywords"></a>

Verifies that the keyword `azure sdk` is present in the targeted package's `keywords` field (in `setup.py` or `pyproject.toml`). This ensures consistent discovery on PyPI.

To run locally:

```bash
azpysdk verify_keywords .
```

## Install and Test Checks

Install and test checks build a distribution of the package (or are provided an artifact from the `Build` phase),  install it into a clean virtual environment, and drive the test suite with `pytest`. The set that runs is gated on the build trigger — PRs run a lean subset while nightly builds run the full set (see the [CI organization table](#how-ci-checks-are-organized) above).

### PR Validation

The following checks run on every pull request (`PR_BUILD_SET` in `eng/scripts/set_checks.py`). They also run on nightly CI and release builds as part of the full check set. PR builds use a reduced check set, but still run the full platform set against any _directly_ changed packages. Packages that are triggered as canary - EG triggering `azure-template` due to changes in `eng/` folder - will run on a reduced platform set.

#### whl

<a name="whl"></a>

Builds a wheel from the package, installs it into a clean environment, and runs the full test suite with `pytest`.

To run locally:

```bash
azpysdk whl .
```

#### sdist

<a name="sdist"></a>

Builds a source distribution, installs it into a clean environment, and runs the full test suite with `pytest`. Ensures that `MANIFEST.in` and the sdist packaging are correct in addition to the tests passing.

To run locally:

```bash
azpysdk sdist .
```

#### mindependency

<a name="mindependency"></a>

For each Azure SDK dependency declared in `setup.py` (dev-only requirements are excluded), this check resolves the **oldest** published version available on PyPI that satisfies the requirement range, installs it in place of the in-repo dev version, and then runs the full test suite. This confirms that the package works across the full declared version range — not just against the latest release.

To run locally:

```bash
azpysdk mindependency .
```

### Nightly and Release

The following checks are the additional entries in `FULL_BUILD_SET` beyond the PR set. They run on both nightly CI and release builds — any build targeting the internal project — but not on PR validation.

#### import\_all

<a name="import-all"></a>

The `import_all` check ensures all modules in a target package can be successfully imported. Installing and importing verifies that all package requirements are properly set in `setup.py`/`pyproject.toml` and that the `__all__` for the package is properly defined. This test installs the package and its required packages, then executes `from <package-root-namespace> import *`. For example from `azure-core`, the following would be invoked: `from azure.core import *`.

To run locally:

```bash
azpysdk import_all .
```

#### whl\_no\_aio

<a name="whl-no-aio"></a>

This check installs the package wheel and runs tests in an environment that does **not** include any `aio` (async I/O) extras. It verifies that a package's sync surface works correctly even without the async dependencies installed. Particularly important for packages that have an optional `aio` sub-package.

To run locally:

```bash
azpysdk whl_no_aio .
```

#### Latest Dependency Test

<a name="latest-dependency-test"></a>

For each Azure SDK dependency declared in `setup.py`/`pyproject.toml` (dev-only requirements are excluded), this check resolves the **latest** published version available on PyPI that satisfies the requirement range, installs it in place of the in-repo dev version, and then runs the full test suite. This confirms that the package works with the newest available version of each of its dependencies.

To run locally:

```bash
azpysdk latestdependency .
```

### Nightly Scheduled Only

The following checks run only on the nightly scheduled pipeline and are not part of release or PR builds. They either depend on dev-versioned packages being present on the dev feed (`devtest`) or are too broad to run on every manually queued build (`regression`, autorest).

#### Dev Feed Test

<a name="dev-feed-test"></a>

The `devtest` check installs dependencies from the nightly dev feed instead of PyPI and runs the full test suite against them. Because it explicitly validates that the installed packages carry dev/alpha version numbers, it only makes sense to run when `SetDevVersion = true` — i.e., on the nightly scheduled pipeline where packages have been stamped and published to the dev feed.

Daily dev-build packages are available on the Azure DevOps feed:
[`https://dev.azure.com/azure-sdk/public/_packaging?_a=feed&feed=azure-sdk-for-python`](https://dev.azure.com/azure-sdk/public/_packaging?_a=feed&feed=azure-sdk-for-python)

To run locally:

```bash
azpysdk devtest .
```

#### Regression Test

<a name="regression-test"></a>

The regression test (also called the reverse dependency test) verifies that changes to a shared package do not break any package that depends on it. For example, when `azure-core` is modified, the regression job identifies all packages that declare `azure-core` as a dependency, then runs their test suites against the newly modified code to confirm backward compatibility.

The framework discovers dependent packages automatically — no list is manually maintained. The packages that most commonly trigger regression runs are:

| Package |
|---|
| `azure-core` |
| `azure-eventhub` |
| `azure-storage-blob` |

Two regression variants bracket the full compatibility range:

| Variant | Dependent package version installed |
|---|---|
| Latest regression | Most recently published release on PyPI |
| Oldest regression | Oldest release that satisfies the requirement range |

Unlike the forward dependency checks (`latestdependency`, `mindependency`), regression tests run the test suite **from the dependent package's release tag** rather than the current repo state. This reflects what customers are actually running.

![res/regression.png](res/regression.png)

Regression tests run on the scheduled nightly pipeline by default. To trigger them on a non-scheduled run, set queue-time variable `Run.Regression = true`.

To run locally (from the repo root):

```bash
python scripts/devops_tasks/test_regression.py azure-* --service=<service-name>
```

#### Autorest Automation

Automatically opens PRs with updated generated code whenever an autorest version bump produces a diff in a package's generated layer.

##### Opt-in to autorest automation

Add `VerifyAutorest: true` to the `parameters` block in your package's `ci.yml`:

```yml
extends:
    template: ../../eng/pipelines/templates/stages/archetype-sdk-client.yml
    parameters:
        ...
        VerifyAutorest: true
        ...
```

##### Running locally

```bash
python scripts/devops_tasks/verify_autorest.py --service_directory <your_service_directory>
```

## Weekly Analyze Checks

<a name="weekly-analyze-checks"></a>

The following checks run on a weekly cadence (not on every PR or nightly) via the `python-analyze-weekly` pipeline. They are exploratory/informational and use `continueOnError: true`, meaning failures are surfaced as warnings but do not block merges.

### Ruff

<a name="ruff"></a>

[`Ruff`](https://docs.astral.sh/ruff/) is a fast Python linter and formatter written in Rust. It runs only during the weekly analyze job, not on every PR.

To run locally:

```bash
azpysdk ruff .
```

### Next-Generation Checks

<a name="next-generation-checks"></a>

The weekly pipeline also runs "next" variants of mypy, pylint, pyright, and sphinx. These variants (`next-mypy`, `next-pylint`, `next-pyright`, `next-sphinx`) pin the *upcoming* pinned tool version so teams can preview and prepare for upcoming version bumps before they land in the regular analyze job.

Results are posted as GitHub issues in the repository. These checks run with `continueOnError: true` and do not block PRs.

To test a "next" check locally, use `--next`:

```bash
azpysdk mypy . --next
azpysdk pylint . --next
azpysdk pyright . --next
azpysdk sphinx . --next
```

See [`doc/analyze_check_versions.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/analyze_check_versions.md) for the currently pinned and upcoming versions.
