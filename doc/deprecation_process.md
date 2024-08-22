This page can be linked using: [aka.ms/azsdk/python/deprecation-process](https://aka.ms/azsdk/python/deprecation-process)

# Overview

This guide describes the step-by-step process for deprecating an `azure-*` package. You likely need to read this if you are a package owner and need to explain to your customers that the package should no longer be used.

The overall idea is that PyPI does not support an official deprecation logic. We concluded that the best way is:
- Change the classifier as `Inactive`, to showcase in metadata that this package is longer worked on.
- Add a disclaimer on the main Readme file to explain deprecation, and provide a migration guide as necessary.
- Push a new release to PyPI.
- Update the API reference docs to show the deprecated status of the package.

# Step 1: Updates to the package files

Clone the `azure-sdk-for-python` repository and update the following files of your package.

## README.md

A disclaimer should be added directing to a replacement package and migration guide as necessary.
  - The link to the replacement package should be a PyPI link: `https://pypi.org/project/azure-mynewpackage/`.
  - The link to the migration guide should be an `aka.ms` link in the format `https://aka.ms/azsdk/python/migrate/my-new-package`. To create this link, go to [https://aka.ms/](https://aka.ms/).
  - **NOTE**: While a migration guide should always be written, you may decide to postpone this work based on downloads numbers (found on [pypistats](https://pypistats.org/), [pype.tech](https://www.pepy.tech/), etc.) and internal knowledge of the usage of the package. 


Replace the existing text with a disclaimer in the following format.

  - If a replacement package and migration guide exist.

    > # Microsoft Azure SDK for Python
    >
    > This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
    >
    > For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

  - If a migration guide will not be provided.

    > # Microsoft Azure SDK for Python
    >
    > This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.

  - If the service has been retired and no replacement package exists.

    > # Microsoft Azure SDK for Python
    >
    > This package is no longer being maintained, as the service has been retired. There is no replacement package for this package.

## CHANGELOG.md and _version.py

- Update the version in the `azure/mypackage/_version.py` file to the next beta or patch version. This file may be called `version.py` if your package is very old. For example:
  - If the last released version was 1.2.3b1, the new version should be 1.2.3b2.
  - If the last released version was 1.2.3, the new version should be 1.2.4.
- In `CHANGELOG.md`, add the new version with the same disclaimer as in the `README.md`. For example:
  > ## 1.2.4 (2023-03-31)
  >
  > ### Other Changes
  >
  > - This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
  > - For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

## sdk_packaging.toml

- Add `auto_update = false` if not already present to avoid the bot overriding your changes.

## pyproject.toml

- Ensure `ci_enabled = false` is NOT present in pyproject.toml. If it is, remove the line, as this will prevent you from releasing the package.

## setup.py

- Update the `Development Status` classifier in `setup.py` to `Development Status :: 7 - Inactive`.
  - `Inactive` packages are disabled from most CI verification such as tests/mypy/pylint/etc., therefore the CI should be faster and have fewer requirements.

# Step 2: Resolve all open issues/PRs corresponding to the library.

If there is a replacement library, provide a link to the new library or an existing migration guide before closing.

# Step 3: Create a PR

Create a PR targeting the `main` branch.

Example PR to deprecate azure-cognitiveservices-language-luis [here.](https://github.com/Azure/azure-sdk-for-python/pull/36893/files)

## Fix any CI issues

Wait for the CI to run. Fix any issues related to deprecation in the PR, such as CHANGELOG.md or README.md formatting.

There should not be any tests or mypy/pylint/etc. failures as these checks are disabled on `Inactive` packages.

## Post your PR in the Python review channel

Post your PR in the [review channel for Python](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) for verification that all requirements for deprecation have been met. If you are not the codeowner, please explicitly tag the codeowner in the post for approval.

## Merge PR

Once the PR is approved, merge.

# Step 4: Trigger a release 

A release here is the same as usual, triggering the release pipeline of your SDK. This release DOES NOT need to be done during during release week and can be done any time. More instructions on release can be found at: https://aka.ms/azsdk/release-checklist

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

Check for your package in the [azure.github.io docs](https://azure.github.io/azure-sdk-for-python/). If an entry for your package exists, reach out to Scott Beddall (scbedd) to delete the entry with the following information:
 - Mention that you have deprecated your package (`azure-mypackage`) and you want the entry removed from the azure.github.io docs.
 - Include a link to the package entry in the azure.github.io docs.

**Note: If you are deprecating multiple packages, please wait until all deprecated packages have been released and send one message including all the packages' info.**

## Update MS Learn docs

- Clone the [azure-sdk](https://github.com/Azure/azure-sdk) repo, if you haven't already.
- Create a branch in your local copy of the repo: `> git checkout -b python/azure-mypackage_deprecation`
- Open the `_data/releases/latest/python-packages.csv` file.
  - If using Visual Studio Code, the `Edit CSV` extension may be helpful for editing the file.
- Find the entry for your package and update the following fields.
  - `EOLDate`: Date your package will officially be deprecated in mm/dd/yyyy format. If the SDK deprecation is due to a service retirement, this date should match the service final retirement date.
  - `Support`: Change the value to `deprecated`.
  - `Replace`: If it exists, set the value to the name of the package meant to replace the package being deprecated. If not, set the value to `NA`.
  - `ReplaceGuide`: If it exists, link to a migration guide in the following format: `aka.ms/azsdk/<language>/migrate/<library>`. If not, set the value to `NA`.
- **Note: If you are deprecating multiple packages, please wait until all deprecated packages have been released and update all entries necessary in one PR.**
- Create a PR to push these changes. Checks will run to notify the repo owners to review your commit.
- If your PR has not been reviewed within a couple of days, please ping Xiang Yan (xiangyan) for a review and include a link to your PR.
- Once the PR has been approved, merge.

The Microsoft Learn API reference docs for your package will be updated to Legacy on the following Wednesday.

Example of deprecated MS Learn API reference docs for Text Analytics [here](https://learn.microsoft.com/python/api/overview/azure/cognitiveservices-language-textanalytics-readme?view=azure-python-previous).

More detailed instructions on updating the CSV file can be found [here](https://eng.ms/docs/products/azure-developer-experience/develop/sdk-deprecation).

## Update overview/conceptual documentation that points to deprecated packages

TODO: The process for this section is still a WIP. Guidance will be updated here once we have concrete steps.

- These will be on the MS Learn page. You can search in the search bar for mentions of the deprecated packages.
