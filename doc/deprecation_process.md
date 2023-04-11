This page can be linked using: [aka.ms/azsdk/python/deprecation-process](https://aka.ms/azsdk/python/deprecation-process)

# Overview

This page describes how to mark a package deprecated on PyPI. You likely need to read this if you are a package owner, and need to explain to your customers 
they shouldn't use the package you used to release anymore.

The overall idea is that PyPI do not support an official deprecation logic. We concluded that the best way was:
- Change the classifier as Inactive, to showcase in metadata that this package is longer worked on
- Add a disclaimer on the main Readme file to explain deprecation, and guide to migration guide to other package as necessary
- Push a [post release](https://peps.python.org/pep-0440/#post-releases) to PyPI

# Step 1: Update in the repository

Clone the repository and udpate the following files of your package:
- `README.MD` add a disclaimer using this syntax:

   > This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
   >
   > For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

- `CHANGELOG.MD` add a new post version with the current date, and the same disclaimer. For instance

   > ## 1.2.3.post1 (2023-03-31)
   >
   > This package is no longer being maintained. Use the [azure-mynewpackage](https://pypi.org/project/azure-mynewpackage/) package instead.
   >
   > For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/my-new-package).

- `azure/mypackage/_version.py` : Change the version to the one used in the changelog (for instance `"1.2.3.post1"`). This file may be called `version.py` if your package is very old.
- `sdk_packaging.toml` : You need to add `auto_update = false` if not already present to avoid the bot overriding your changes
- `setup.py` change the `Development Status` classifier to `Development Status :: 7 - Inactive`. **Important: This needs to be your LAST commit on the PR. More on this at the bottom of this page if you want details.**.

Do a PR targeting the `main` branch. Post your PR in our [review channel for Python](https://teams.microsoft.com/l/channel/19%3a4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%2520-%2520Python%2520-%2520Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47)

You're responsible to fix any CI issue related to this PR, if any. Note that `Inactive` packages are disabled from most CI verificiation, therefore the CI should be faster and
have less requirements.

An example of PR can be found the [deprecation of application insights](https://github.com/Azure/azure-sdk-for-python/pull/23024/files)

Once the PR is merged, move to the next step.

# Step 2: Trigger a release 

A release here is the same as usual, triggering the release pipeline of you SDK. More instruction can be found at: https://aka.ms/azsdk/release-checklist

**Important Note**: As CI don't build Inactive projects right now, you can't build and release. This is a classical chicken and egg problem: we don't want to lose time on testing Inactive projects, but you need at least have one run of build to release the Inactive project. It's important then to pass the variable "BUILD_INACTIVE=true" while triggering the release pipeline. But doing this may uncover issues that were not seen in your initial PR as the CI was disabled. To avoid most of those problems, it's highly recommended that you put the commit with "Inactive" LAST in your PR. In other words, push all changes to Readme and ChangeLog, wait to confirm the CI is green, and when everything is clean, push finally "Inactive" in the `setup.py`

