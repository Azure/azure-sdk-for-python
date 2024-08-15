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
> - For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).
   
If the last released version was 1.2.3, the version should be 1.2.4.

> ## 1.2.4 (2023-03-31)
>
> ### Other Changes
>
> - This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
> - For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

Update the version in the `azure/mypackage/_version.py` file. This file may be called `version.py` if your package is very old.

More information on specifics of versioning can be found at [the bottom of the guide under "More details - Versioning"](TODO: add link).

## sdk_packaging.toml

- Add `auto_update = false` if not already present to avoid the bot overriding your changes.

## pyproject.toml

- Ensure `ci_enabled = false` is NOT present in pyproject.toml. If it is, remove the line, as this will prevent you from releasing the package.

# Step 2: Resolve all open issues/PRs corresponding to the library.

If there is a Track 2, provide a link to the new package or an existing migration guide before closing.

# Step 3: Create a PR

Create a PR targeting the `main` branch. Follow steps listed below.

Example PR to deprecate azure-cognitiveservices-language-luis [here.](https://github.com/Azure/azure-sdk-for-python/pull/36893/files)

## Fix any CI issues

Wait for the CI to run. Fix any issues related to the PR.

## Update Development Status classifier in setup.py

Update `setup.py` to change the `Development Status` classifier to `Development Status :: 7 - Inactive`.

**Note: This needs to be your LAST commit on the PR.**

`Inactive` packages are disabled from most CI verification, therefore the CI should be faster and have fewer requirements.

## Post your PR in the Python review channel

Post your PR in the [review channel for Python](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) and request a review from the codeowner, as the PR will be blocked from merging until approved by the codeowner.

## Merge PR

Once the PR is approved, merge and move to the next step.

# Step 4: Trigger a release 

A release here is the same as usual, triggering the release pipeline of your SDK. This release DOES NOT need to be done during during release week and can be done any time. Note that you will need to pass in BUILD_INACTIVE=true to variables when triggering the pipeline. To do this:

- As per usual, under the build pipeline for your package, click 'Run pipeline'.
- Click on 'Variables' under 'Advanced options'.
- Then 'Add variable'.
- Pass `BUILD_INACTIVE` to 'Name' and `true` to 'Value', and 'Create'.
- Then, 'Run' the pipeline.

More information on why this is done is in the [More details - Why set BUILD_INACTIVE?](TODO) section at the bottom of the page.

More instructions on general release can be found at: https://aka.ms/azsdk/release-checklist

## Post-Release

Check to make sure that the new version of the package has been released on PyPI.

# Step 5: Create a new PR to remove package from CI

- Remove the package artifact from `mypackage/ci.yml`. More specifically, remove the `name` and corresponding `safeName` lines from under `Artifacts` here:

```
extends:
  parameters:
    Artifacts:
    - name: azure-mypackage    
      safeName: azuremypackage
```

- Add the line `ci_enabled = false` to `azure-mypackage/pyproject.toml`.
- Create a new PR targeting the `main` branch of the repository.
- Post the PR in the [review channel for Python](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47).
- Once the PR has been approved by codeowner, merge.
- You're responsible for fixing any CI issues related to this PR.

Example post-deprecation PR for azure-cognitiveservices-language-luis [here](https://github.com/Azure/azure-sdk-for-python/pull/36908).

# Step 6: Update API Documentation

## Remove the entry in the github.io docs

- Check for your package in the [azure.github.io docs](https://azure.github.io/azure-sdk-for-python/). If an entry for your package does not exist, skip to the `Update docs.microsoft.com` section.
- Clone the [azure-sdk](https://github.com/Azure/azure-sdk) repo.
- Remove the entry line for the Python `azure-mypackage` in the releases [inventory.csv](https://github.com/Azure/azure-sdk/blob/main/_data/releases/inventory/inventory.csv). (Example)[TODO: link]
- Create a PR and leave it in the (TODO: add where the PR should be left for review) for review.
- Once approved, merge. The updated index without reference to `azure-mypackage` should be updated within (TODO: insert time frame for updates to populate).

## Update docs.microsoft.com

TODO: WIP section

- If the docs have not been updated to say deprecated, which you can check by going to docs.microsoft.com, clicking on the overview section of your service, click on the Legacy in the dropdown, and check that your package says (Deprecated) next to the name. For example, text analytics here: (TODO).
- If the docs have not been updated within 2 days, this needs to be done manually.
- Clone the [azure-sdk](https://github.com/Azure/azure-sdk) repo, if you haven't already.
- Mark the package as deprecated in the [appropriate metadata file](https://github.com/Azure/azure-sdk/blob/main/_data/releases/latest/python-packages.csv). This will put packages under the Legacy moniker.

## Update overview/conceptual documentation that points to deprecated packages

- These will be on the docs.microsoft.com page. You can search in the search bar for mentions of the deprecated packages.

# More details

## Versioning

The best versioning approach would be to do a [post release](https://peps.python.org/pep-0440/#post-releases). However, due to some tooling issues at the moment, the version should be the next beta or the next patch version ([example](https://github.com/Azure/azure-sdk-for-python/commit/cf3bfed65a65fcbb4b5c93db89a221c2959c5bb4)). Follow these issues for more details https://github.com/Azure/azure-sdk/issues/7479 and https://github.com/Azure/azure-sdk-tools/issues/5916.

## Why set BUILD_INACTIVE?

TODO: double check the following
Passing in BUILD_INACTIVE=true to variables when triggering the pipeline will ensure the package API documentation under docs.microsoft.com is labeled as (Deprecated).**
