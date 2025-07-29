This page can be linked using: [aka.ms/azsdk/python/deprecation-process](https://aka.ms/azsdk/python/deprecation-process)

# Overview

This guide describes the step-by-step process for deprecating an `azure-*` package. You likely need to read this if you are a package owner and need to explain to your customers that the package should no longer be used.

Note that a deprecated package is a signal to customers that they are *strongly encouraged* to stop using it and migrate to another package. The package is *still available* to install and is not unpublished, and we still have the ability to publish critical security fixes as necessary.

The overall idea is that PyPI does not support an official deprecation logic. We concluded that the best way is:
- Change the classifier as `Inactive`, to showcase in metadata that this package is longer worked on.
- Add a disclaimer on the main Readme file to explain deprecation, and provide a migration guide as necessary.
- Push a new release to PyPI.
- Update the API reference docs to show the deprecated status of the package.

## Pre-deprecation: Blog Post

If applicable, consider adding a post to the Azure Blog stating that:
 - a new package is available which replaces the old package
 - the old package is scheduled to be deprecated on a specific date
 - guidance on adjusting code to use the new package.

Reach out to the Python Azure SDK PM, Rohit Ganguly (rohitganguly), if you have any questions about creating a blog post.

# Step 1: Updates to the package files

Clone the `azure-sdk-for-python` repository and update the following files of your package.

## README.md

A disclaimer should be added indicating end-of-life date (EOLDate) of the package and directing to a replacement package and migration guide as necessary.
  - The EOLDate should be in the format `MM-DD-YYYY`.
    - If there is no replacement package, the package EOLDate should be the service retirement date.
    - If there is a replacement package (or repo), the EOLDate should be the same as the deprecation release date of the old package in the CHANGELOG.md.
    - Service retirement dates MAY be listed [here](https://aka.ms/servicesretirementworkbook), where retiring feature says 'Entire service'.
  - The link to the replacement package should be a PyPI link: `https://pypi.org/project/azure-mynewpackage/`.
  - The link to the migration guide should be a link in the format `https://aka.ms/azsdk/python/migrate/my-new-package`. To create this aka.ms link, follow the "How to create aka.ms links" section [here](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/233/Azure-SDK-AKA.ms-Links?anchor=how-to-create-aka.ms-links).
    - **NOTE**: You may decide to postpone or skip writing a migration guide based on downloads numbers (found on [pypistats](https://pypistats.org/), [pepy.tech](https://www.pepy.tech/), etc.) and internal knowledge of the usage of the package.

Replace ALL existing text with a disclaimer in the following format.

  - If a replacement package and migration guide exist:

    ```md
     This package has been deprecated and will no longer be maintained after <EOLDate>. This package will only receive security fixes until <EOLDate>. To receive updates on new features and non-security bug fixes, upgrade to the replacement package, [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/). Refer to the migration guide (https://aka.ms/azsdk/python/migrate/my-new-package) for guidance on upgrading.
    ```

  - If a migration guide is not provided:

    ```md
     This package has been deprecated and will no longer be maintained after <EOLDate>. This package will only receive security fixes until <EOLDate>. To receive updates on new features and non-security bug fixes, upgrade to the replacement package, [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/).
    ```

  - If a replacement package does not exist:

    ```md
     This package has been deprecated and will no longer be maintained after <EOLDate>. This package will only receive security fixes until <EOLDate>.
    ```

  - If a new service has replaced the service, and existing customers should be directed to the new service's Rest API docs/repo:

    ```md
     This package has been deprecated and will no longer be maintained after <EOLDate>. This package will only receive security fixes until <EOLDate>. Refer to the samples in the [My New Service repo](https://github.com/microsoft/my-new-service/tree/main) instead.
    
    For additional support, open a new issue in the [Issues](https://github.com/microsoft/my-new-service/issues) section of the My New Service repo.
    ```

## CHANGELOG.md and _version.py

- Update the version in the `azure/mypackage/_version.py` file to the next patch version if the package has had a stable release, or the next beta version if the package has only been in beta. This file may be called `version.py` if your package is very old. For example:
  - If a stable version WAS NEVER RELEASED and the last released version was 1.0.0b1, the new version should be 1.0.0b2.
  - If a stable version HAS BEEN RELEASED and the last released version was 1.2.3b1, the new version should be 1.2.4.
  - If the last released version was 1.2.3, the new version should be 1.2.4.
- In `CHANGELOG.md`, add the new version with the same disclaimer as in the `README.md`, along with a release date. No other changes/features added/breaking changes should be included for this version. For example:
  ```md
  ## 1.2.4 (2023-03-31)
  
  ### Other Changes

  - This package has been deprecated and will no longer be maintained after <EOLDate>. This package will only receive security fixes until <EOLDate>. To receive updates on new features and non-security bug fixes, upgrade to the replacement package, [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/). Refer to the migration guide (https://aka.ms/azsdk/python/migrate/my-new-package) for guidance on upgrading.
  ```

## sdk_packaging.toml

- Add `auto_update = false` if not already present to avoid the bot overriding your changes.

## pyproject.toml

- Ensure `ci_enabled = false` is NOT present in pyproject.toml. If it is, remove the line, as this will prevent you from releasing the package.

## setup.py

- Update the `Development Status` classifier in `setup.py` to `Development Status :: 7 - Inactive`.
  - `Inactive` packages are disabled from most CI verification such as tests/mypy/pylint/etc., therefore the CI should be faster and have fewer requirements.
 
## ci.yml

- Ensure the package is listed under `Artifacts` so that the artifact is generated for release. If not listed, add it.

 ```yml
  extends:
    parameters:
      ...
      Artifacts:
      - name: azure-mypackage
        safeName: azuremypackage
  ```

# Step 2: Resolve all open issues/PRs corresponding to the library.

If there is a replacement library, provide a link to the new library or an existing migration guide before closing.

# Step 3: Create a PR

Create a PR targeting the `main` branch.

Example PR to deprecate azure-cognitiveservices-language-spellcheck [here.](https://github.com/Azure/azure-sdk-for-python/pull/37456/files)

## Fix any CI issues

Wait for the CI to run. Fix any issues related to deprecation in the PR, such as CHANGELOG.md or README.md formatting.

There should not be any tests or mypy/pylint/etc. failures as these checks are disabled on `Inactive` packages.

### Verify Readmes Failure

If you see the "Verify Readmes" task in the "Analyze" job failing with `There were README verification failures, scroll up to see the issue(s)`, add a line to ignore the package in [`eng/.docsettings.yml` under `known_content_issues`](https://github.com/Azure/azure-sdk-for-python/blob/5136a43ac2c841e6ffe36f55df6c94f1ddd00a9d/eng/.docsettings.yml#L41). For example:

```yml
known_content_issues:
  ...
  - ['sdk/mypackage/azure-mypackage/README.md', '#4554']
```

## Post your PR in the Python review channel

Post your PR in the [review channel for Python](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) for verification that all requirements for deprecation have been met. If you are not the codeowner, please explicitly tag the codeowner in the post for approval.

## Merge PR

Once the PR is approved, merge.

# Step 4: Trigger a release 

## Pre-Release

Before releasing, you must update the DevOps release work items in the DevOps Release dashboard.

- To do this, run the following in a PowerShell terminal, replacing 'mypackage' with your package:
```pwsh
azure-sdk-for-python> cd eng/common/scripts
azure-sdk-for-python/eng/common/scripts> ./Prepare-Release.ps1 -PackageName azure-mypackage -ServiceDirectory mypackage -ReleaseDate MM/DD/YYYY
```
- Follow the command prompts.
- You may see a `WARNING: API Review is not approved for package azure-mypackage. Release pipeline will fail if API review is not approved for a GA version release.` This can be ignored as the API Review check will not be run on `Inactive` packages.
- Discard any automatic changes made to the CHANGELOG.md/README.md by the script.

## Release the Package

A release here is the same as usual, triggering the release pipeline of your SDK. Note that local smoke testing and mypy/pylint/sphinx/etc. checks are not needed. More instructions on release can be found at: https://aka.ms/azsdk/release-checklist

**Note: This release DOES NOT need to be done during during release week and can be done any time.**

### Checks Failing on Other Packages

You may see tests/mypy/pylint or other checks failing on other packages in the CI when releasing. To unblock the release of the deprecated package, you may add one or more `Skip.*` variables when you 'Run pipeline' to skip these checks. The `Skip.*` variables for all checks are listed [here](https://github.com/Azure/azure-sdk-for-python/blob/dc283ae7e8f7fe3bb1db8f27315d589e88bdf453/doc/eng_sys_checks.md?plain=1#L76).

## Post-Release

Check to make sure that the new version of the package has been released on PyPI and that the release has been tagged in the `azure-sdk-for-python` repo with `azure-mypackage_<version>`.

**NOTE: If your package has been released, there should be a corresponding [GitHub release tag](https://github.com/Azure/azure-sdk-for-python/tags). If there is not, create a post in the [Engineering System channel](https://teams.microsoft.com/l/channel/19%3A59dbfadafb5e41c4890e2cd3d74cc7ba%40thread.skype/Engineering%20System%20%F0%9F%9B%A0%EF%B8%8F?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) that the release tag cannot be found and add a link to the release build.**

Example release tag: [azure-cognitiveservices-language-spellcheck_2.0.1](https://github.com/Azure/azure-sdk-for-python/releases/tag/azure-cognitiveservices-language-spellcheck_2.0.1)

# Step 5: Create a new PR to remove the package from the main branch

Append a note to the README.md deprecation message stating the package has been removed from the main branch, a link to the latest GitHub release tag and package on PyPI, and contact info for questions. The full README text should now look like the following:

  ```md
  # Microsoft Azure SDK for Python

  This package has been deprecated and will no longer be maintained after <EOLDate>. This package will only receive security fixes until <EOLDate>.

  Package source code and samples have been removed from the `main` branch and can be found under the release tag for the latest version. See [azure-mypackage_<version>](https://github.com/Azure/azure-sdk-for-python/tree/azure-mypackage_<version>/sdk/mypackage/azure-mypackage). The latest release can be found on [PyPI](https://pypi.org/project/azure-mypackage/).

  If you have any questions, please open a [GitHub Issue](https://github.com/Azure/azure-sdk-for-python/issues) or email `azpysdkhelp@microsoft.com`.
  ```

- Delete all files in the package directory `sdk/mypackage/azure-mypackage` EXCEPT for the README.md at the package directory root.
- You will see an `Artifacts` parameter in `mypackage/ci.yml`.
  ```yml
  extends:
    parameters:
      ...
      Artifacts:
      - name: azure-mypackage
        safeName: azuremypackage
  ```
  - If there are multiple packages listed, remove the `name` and corresponding `safeName` lines for only `azure-mypackage`.
    ```yml
    extends:
      parameters:
        ...
        Artifacts:
          ...
    ```
  - If the only package listed is `azure-mypackage`, delete `ci.yml` and all other files -- _not package subdirectories_-- in the `mypackage` service directory (i.e. `tests.yml`, `test-resources.bicep`, etc.).

- Create a new PR targeting the `main` branch of the repository.
- Post the PR in the [review channel for Python](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47).
- Once the PR has been approved by codeowner, merge.
- You're responsible for fixing any CI issues related to this PR.

# Step 6: Update API Documentation

## Remove the entry in the github.io docs

Check for your package in the [azure.github.io docs](https://azure.github.io/azure-sdk-for-python/). If an entry for your package exists, reach out to Scott Beddall (scbedd) to delete the entry with the following information:
 - Mention that you have deprecated your package (`azure-mypackage`) and you want the entry removed from the azure.github.io docs.
 - Include a link to the package entry in the azure.github.io docs.

**Note: If you are deprecating multiple packages, please wait until all deprecated packages have been released and send one message including all the packages' info.**

## Update MS Learn docs

- Create your own fork of the [azure-sdk](https://github.com/Azure/azure-sdk) repo and clone it, if you haven't already.
- Create a branch in your local copy of the repo: `> git checkout -b python/azure-mypackage_deprecation`
- Open the `_data/releases/latest/python-packages.csv` file.
  - If using Visual Studio Code, the `Edit CSV` extension may be helpful for editing the file.
- Find the entry for your package and update the following fields.
  - `EOLDate`: In MM/DD/YYYY format. If the SDK deprecation is due to a service retirement, this date should match the service final retirement date. If there is a replacement package (or repo), this should match the release date of the deprecated package.
  - `Support`: Change the value to `deprecated`.
  - `Replace`: If it exists, set the value to the name of the Azure SDK for Python package meant to replace the package being deprecated. If not, set the value to `NA`.
  - `ReplaceGuide`: If it exists, link to a migration guide in the following format: `aka.ms/azsdk/<language>/migrate/<library>`. If not, set the value to `NA`.
- **Note: If you are deprecating multiple packages, please wait until all deprecated packages have been released and update all entries necessary in one PR.**
- Create a PR to push these changes. Checks will run to notify the repo owners to review your commit.
  - Example PR for azure-cognitiveservices-language-spellcheck [here](https://github.com/Azure/azure-sdk/pull/8012/files).
- Ping Xiang Yan (xiangyan) for a review and include a link to your PR. If he is unavailable, ping Ronnie Geraghty (rgeraghty) or Wes Haggard (wesh).
- Once the PR has been approved, merge.

The Microsoft Learn API reference docs for your package will be updated to Legacy on the following Wednesday.

Example of deprecated MS Learn API reference docs for Text Analytics [here](https://learn.microsoft.com/python/api/overview/azure/cognitiveservices-language-textanalytics-readme?view=azure-python-previous).

More detailed instructions on updating the CSV file can be found [here](https://eng.ms/docs/products/azure-developer-experience/develop/sdk-deprecation).

## Archive the project in PyPI

If the service is retired and customers should not expect to receive any future updates, including security fixes or maintenance, [your project can be marked as archived](https://blog.pypi.org/posts/2025-01-30-archival/). Before doing so, publish a final release with any necessary updates to the README/CHANGELOG/docs to warn customers that the project will not receive further updates.

To archive your project, reach out to Laurent Mazuel (lmazuel). You cannot complete this step yourself.

Note: Project archival is not deletion. Archiving a project does not remove it from the index, and does not prevent users from installing it.

## Update overview/conceptual documentation that points to deprecated packages

TODO: The process for this section is still a WIP. Guidance will be updated here once we have concrete steps.

- These will be on the MS Learn page. You can search for mentions of the deprecated packages.
