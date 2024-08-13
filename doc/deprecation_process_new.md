This page can be linked using: [aka.ms/azsdk/python/deprecation-process](https://aka.ms/azsdk/python/deprecation-process)

# Overview

This guide describes the step-by-step process for deprecating an `azure-*` package. You likely need to read this if you are a package owner and need to explain to your customers that the package should no longer be used.

The overall idea is that PyPI does not support an official deprecation logic. We concluded that the best way is:
- Change the classifier as `Inactive`, to showcase in metadata that this package is longer worked on.
- Add a disclaimer on the main Readme file to explain deprecation, and provide a migration guide as necessary.
- Push a new release to PyPI.

# Step 1: Updates to the package files

Clone the `azure-sdk-for-python` repository and update the following files of your package.

## README.md

Replace the existing text with a disclaimer in the following format, with migration guide provided as necessary:

> # Microsoft Azure SDK for Python
>
> This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
>
> For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

**NOTE**: While a migration guide should always be written, you may decide to postpone this work based on downloads numbers (found on [pypistats](https://pypistats.org/), [pype.tech](https://www.pepy.tech/), etc.) and internal knowledge of the usage of the package.

## CHANGELOG.md and _version.py

In `CHANGELOG.md`, add a new version with a disclaimer in the following format. The version should be the next beta or patch version. For example:

If the last released version was 1.2.3b1, the version should be 1.2.3b2.

> ## 1.2.3b2 (2023-03-31)
>
> ### Other Changes
>
> - This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
>
> - For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).
   
If the last released version was 1.2.3, the version should be 1.2.4.

> ## 1.2.4 (2023-03-31)
>
> ### Other Changes
>
> - This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
>
> - For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

Update the version in the `azure/mypackage/_version.py` file. This file may be called `version.py` if your package is very old.

More information on specifics of versioning can be found at [the bottom of the guide under "More details - Versioning"](TODO: add link).

## sdk_package.toml

- Add `auto_update = false` if not already present to avoid the bot overriding your changes.

## pyproject.toml

- Add `ci_enabled = false` if not already present.

# Step 2: Resolve all open issues/PRs corresponding to the library.

If there is a Track 2, provide a link to the new package or an existing migration guide before closing.

# Step 3: Create a PR

Create a PR targeting the `main` branch. Follow steps listed below.

An example PR to deprecate application insights can be found [here.](https://github.com/Azure/azure-sdk-for-python/pull/23024/files)

## Fix any CI issues

Wait for the CI to run. Fix any issues related to the PR.

## Update Development Status classifier in setup.py

Update `setup.py` to change the `Development Status` classifier to `Development Status :: 7 - Inactive`.

**Note: This needs to be your LAST commit on the PR. More information can be found at [the bottom of the guide under "More details - Order of Development Status commit in PR"].**

`Inactive` packages are disabled from most CI verification, therefore the CI should be faster and have fewer requirements.

## Post your PR in the Python review channel

Post your PR in the [review channel for Python.](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47)

## Merge PR

Once the PR is approved by the codeowner and merged, move to the next step.

# Step 4: Trigger a release 

A release here is the same as usual, triggering the release pipeline of your SDK. This release DOES NOT need to be done during during release week and can be done any time.

More instruction can be found at: https://aka.ms/azsdk/release-checklist

**Note: Check to make sure that the new version of the package has been released on PyPI, even if the `Publish package to feed` step fails in the CI.**

# Step 5: Create a new PR to remove package from ci.yml

Remove the package artifact from `azure-mypackage/ci.yml`. This would look like removing the `name` and corresponding `safeName` lines from under `Artifacts` here:

```
extends:
  parameters:
    Artifacts:
    - name: azure-mypackage    
      safeName: azuremypackage
```

Create a new PR targeting the `main` branch of the repository. Post the PR in the [review channel for Python](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47). You're responsible for fixing any CI issue related to this PR.

# Step 6: Update API Documentation

## Remove the entry in the github.io docs

- Check for your package in the [azure.github.io docs](https://azure.github.io/azure-sdk-for-python/). If the reference exists, move to the next step.
- Clone the [azure-sdk](https://github.com/Azure/azure-sdk) repo.
- Remove the line entry for the Python `azure-mypackage` in the releases [inventory.csv](https://github.com/Azure/azure-sdk/blob/main/_data/releases/inventory/inventory.csv). (Example)
- Create a PR and leave it in the Python reviews channel.
- Leave the PR in the Python reviews channel.

## Update docs.microsoft.com

- Instructions on deprecating packages: [Azure SDK deprecation guidelines (eng.ms)](https://eng.ms/docs/products/azure-developer-experience/develop/sdk-deprecation-guidelines)
- For ref docs: mark the package as deprecated in the [appropriate metadata file](https://github.com/Azure/azure-sdk/blob/main/_data/releases/latest/python-packages.csv). This will put packages under the Legacy moniker. Text analytics and anomaly detector are already there.

## Update overview/conceptual documentation that points to deprecated packages

- These will be on the docs.microsoft.com page. You can search in the search bar for mentions of the deprecated packages.

# More details

## Versioning

The best versioning approach would be to do a [post release](https://peps.python.org/pep-0440/#post-releases). However, due to some tooling issues at the moment, the version should be the next beta or the next patch version ([example](https://github.com/Azure/azure-sdk-for-python/commit/cf3bfed65a65fcbb4b5c93db89a221c2959c5bb4)). Follow these issues for more details https://github.com/Azure/azure-sdk/issues/7479 and https://github.com/Azure/azure-sdk-tools/issues/5916.

## Order of Development Status commit in PR

As CI don't build Inactive projects right now, you can't build and release. This is a classical chicken and egg problem: we don't want to lose time on testing Inactive projects, but you need at least have one run of build to release the Inactive project. It's important then to pass the variable `"BUILD_INACTIVE=true"` while triggering the release pipeline. But doing this may uncover issues that were not seen in your initial PR as the CI was disabled. To avoid most of those problems, it's highly recommended that you put the commit with "Inactive" LAST in your PR. In other words, push all changes to Readme and ChangeLog, wait to confirm the CI is green, and when everything is clean, push finally "Inactive" in the `setup.py`
