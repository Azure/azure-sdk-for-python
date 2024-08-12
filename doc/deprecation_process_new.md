This page can be linked using: [aka.ms/azsdk/python/deprecation-process](https://aka.ms/azsdk/python/deprecation-process)

# Overview

This guide describes the step-by-step process for deprecating an `azure-*` package. You likely need to read this if you are a package owner and need to explain to your customers that the package should no longer be used.

The overall idea is that PyPI does not support an official deprecation logic. We concluded that the best way is:
- Change the classifier as `Inactive`, to showcase in metadata that this package is longer worked on.
- Add a disclaimer on the main Readme file to explain deprecation, and provide a migration guide as necessary.
- Push a new release to PyPI.

# Step 1: Determine package that needs deprecation

## OPTIONAL - Run the script to list packages that may need deprecation

If you know the package that you want to deprecate, skip to step 1b.

TODO: Test out script + merge Krista's PR.

If you would like to check for packages that have not been released in over 2 years as part of a periodic cleanup, you can run the following script locally.

This script (scripts/old_packages/output_old_packages.py) can be run locally to generate an excel/csv with a list of packages that have not been released in over two years.

The CSV provides the following information:
- Package name
- Last released version
- Last released date
- Development Status
- Action: This can be manually updated to track whether or not to deprecate. 
- Notes: Additional notes, such as instructions on the new service/REST API to refer the customer to.
- Status: This can be manually updated to track whether the deprecation of the package is done.

To run the script:
```
azure-sdk-for-python> cd scripts/old_packages
azure-sdk-for-python/scripts/old_packages> python output_old_packages.py
```

## Verify deprecated status of the package

TODO: How to verify? Provide examples. azurecharts is disabled: https://azurecharts.com/timeboards/deprecations?ref=blog.tomkerkhove.be

To confirm that they need deprecation, you can:
- Refer to [this chart](https://azurecharts.com/timeboards/deprecations?ref=blog.tomkerkhove.be) to see whether the service has been deprecated/end-of-life

# Step 2: Updates to the package files

Clone the `azure-sdk-for-python` repository and update the following files of your package.

## Update README.md

Add a disclaimer using this syntax, with migration guide provided as necessary:

> This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
>
> For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

**NOTE**: While a migration guide should always be written, you may decide to postpone this work based on downloads numbers (found on [pypistats](https://pypistats.org/), [pype.tech](https://www.pepy.tech/), etc.) and internal knowledge of the usage of the package.

## Update CHANGELOG.md and _version.py

In `CHANGELOG.MD`, add a new version with the release date and a disclaimer. The version should be the next beta or patch version. For example, if the last released version was 1.2.3, the version should be 1.2.4.

More information on specifics of versioning can be found at [the bottom of the guide under "More details - Versioning"].

> ## 1.2.3b2 (2023-03-31)
>
> This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
>
> For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).
   
If the last released version was 1.2.3b1, the version should be 1.2.3b2.

> ## 1.2.4 (2023-03-31)
>
> This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
>
> For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

- `azure/mypackage/_version.py` : Change the version to the one used in the changelog (for instance `"1.2.3.post1"` or `"1.2.4"`). This file may be called `version.py` if your package is very old.

## Update sdk_package.toml

- Add `auto_update = false` if not already present to avoid the bot overriding your changes.

## Update pyproject.toml

- Add `ci_enabled = false` if not already present.

# Step 3: Resolve all open issues/PRs corresponding to the library.

If there is a Track 2, provide a link to the new package or an existing migration guide before closing.

# Step 4: Create a PR

Create a PR targeting the `main` branch. Follow steps listed below.

An example PR to deprecate application insights can be found [here.](https://github.com/Azure/azure-sdk-for-python/pull/23024/files)

## Fix any CI issues

Wait for the CI to run. Fix any issues related to the PR.

## Update Development Status classifier in setup.py

Update `setup.py` to change the `Development Status` classifier to `Development Status :: 7 - Inactive`.

**Note: This needs to be your LAST commit on the PR. More information can be found at [the bottom of the guide under "More details - Order of Development Status commit in PR"].**

`Inactive` packages are disabled from most CI verificiation, therefore the CI should be faster and have fewer requirements.

## Post your PR in the Python review channel

Post your PR in the [review channel for Python.](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47)

## Merge PR

Once the PR is merged, move to the next step.

# Step 5: Trigger a release 

A release here is the same as usual, triggering the release pipeline of your SDK. This release DOES NOT need to be done during during release week and can be done any time.

More instruction can be found at: https://aka.ms/azsdk/release-checklist

**Note: Check to make sure that the new version of the package has been released on PyPI, even if the `Publish package to feed` step fails in the CI.**

# Step 6: Create a new PR to remove package from ci.yml

Remove the package artifact from `azure-mypackage/ci.yml`. This would look like removing the `name` and corresponding `safeName` lines from under `Artifacts` here:

```
extends:
  parameters:
    Artifacts:
    - name: azure-mypackage    
      safeName: azuremypackage
```

Create a new PR targeting the `main` branch of the repository. Post the PR in the [review channel for Python](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47). You're responsible for fixing any CI issue related to this PR.

# Step 7: Update API Documentation

## Update github.io docs

- Remove all documentation related to the deprecated package on github.io.
- **Note**: Be careful with deletion in this account.

Follow this guide to Manually release Github.IO docs
- https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/1087/Manually-Releasing-Github.IO-Docs

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
