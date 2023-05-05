# Guide for migrating test recordings out of the `azure-sdk-for-python` repository

The Azure SDK test proxy enables tests to run recorded tests, even when these test recordings are outside the
`azure-sdk-for-python` repository. Migrating to this out-of-repo recording setup requires an initial recording move,
and after this the flow to update recordings will be slightly different. This guide describes the first stage of this
process and links to updated recording instructions.

More technical documentation of the test proxy's out-of-repo recording support can be found [here][detailed_docs] in
the `azure-sdk-tools` repository.

## Table of contents

- [Current recording setup](#current-recording-setup)
- [New recording setup](#new-recording-setup)
- [Initial recording migration](#initial-recording-migration)
  - [Migration script prerequisites](#migration-script-prerequisites)
  - [Execute the migration script](#execute-the-migration-script)
- [Run tests with out-of-repo recordings](#run-tests-with-out-of-repo-recordings)

## Current recording setup

Currently, test recordings live in the `azure-sdk-for-python` repository (or "language repo"), under a given package's
`/tests/recordings` directory. The test proxy loads recordings from this local directory -- this can be done entirely
offline.

However, the main drawback of storing recordings in the language repo is bloat; a huge percentage of all language repo
files are actually test recordings. Recording file updates are also included in pull requests, which can make them more
tedious to review and difficult to load.

## New recording setup

With the test proxy, we can instead store recordings in a completely different git repository (called
[`azure-sdk-assets`][azure_sdk_assets], or the "assets repo"). The test proxy creates a sparse clone of only the
recordings for the package being tested, stores them locally in a git-excluded language repo directory, and runs
playback tests in the same way as before.

The out-of-repo recording system requires a connection to fetch recordings but frees up considerable space in the
language repo. Additionally, pull requests that update recordings now update a single pointer to new recordings instead
of full recording files.

The pointer to test recordings is stored in a new `assets.json` file that will be created for each package during the
initial migration.

## Initial recording migration

A [PowerShell script][transition_script] in the `azure-sdk-tools` repository will assist in pushing recordings to the
assets repo, removing recordings from the language repo, and creating an `assets.json` file for the package you're
migrating.

This script -- [`generate-assets-json.ps1`][generate_assets_json] -- should be run once per package, and can be used
either directly from an `azure-sdk-tools` repo clone or with a local download of the script. To download the script to
your current working directory, use the following PowerShell command:

```PowerShell
Invoke-WebRequest -OutFile "generate-assets-json.ps1" https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/eng/common/testproxy/transition-scripts/generate-assets-json.ps1
```

### Migration script prerequisites

- The targeted library is already migrated to use the test proxy.
- Git version > 2.30.0 is to on the machine and in the path. Git is used by the script and test proxy.
- [PowerShell Core][powershell] >= 7.0 is installed.
- [Docker][docker] or [Podman][podman] is installed.
- Global [git config settings][git_setup] are configured for `user.name` and `user.email`.
  - These settings can be overridden with environment variables `GIT_COMMIT_OWNER` and `GIT_COMMIT_EMAIL`, respectively.
- The environment variable `GIT_TOKEN` is set to a valid [personal access token][git_token] for your user.
  - This token is necessary for authenticating git requests made in a Docker/Podman container.
- Membership in the `azure-sdk-write` GitHub group.

### Execute the migration script

In a PowerShell window:

1. Set your working directory to the root of the package you're migrating (`sdk/{service}/{package}`) -- for example:

```PowerShell
cd C:\azure-sdk-for-python\sdk\keyvault\azure-keyvault-keys
```

2. Run the following command:

```PowerShell
<path-to-script>/generate-assets-json.ps1 -TestProxyExe "docker" -InitialPush
```

If you run `git status` from within the language repo, you should see:

- Deleted files for each test recording in the package
- A new `assets.json` file under the root of your package

The `assets.json` file will have the form:

```json
{
  "AssetsRepo": "Azure/azure-sdk-assets",
  "AssetsRepoPrefixPath": "python",
  "TagPrefix": "python/{service}/{package}",
  "Tag": "python/{service}/{package}_<10-character-commit-SHA>"
}
```

The `Tag` field matches the name of a tag that's been created in the assets repo and contains the uploaded recordings.
Before creating a PR to cement the recording move, it's a good idea to check out that tag in the assets repo and make
sure the recordings that you expect to see are there.

## Run tests with out-of-repo recordings

After moving recordings to the asset repo, live and playback testing will be the same as it was in the past. The test
proxy automatically pulls down the correct set of recordings based on the `Tag` in your package's `assets.json` file.

The process for updating test recordings is slightly different than it was with in-repo recordings, and differs in two
primary ways:

1. When tests are run in recording mode, recording changes won't be visible in the language repo and will instead be
   tracked in a separate directory.
2. When updated recordings are pushed to the assets repo, the `Tag` field in your package's `assets.json` file will be
   updated to point to these new recordings. This `assets.json` change is what you'll include in a pull request to update
   recordings in the language repo.

For more details, refer to the documentation in [tests.md][recording_updates].

[azure_sdk_assets]: https://github.com/Azure/azure-sdk-assets
[detailed_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/documentation/asset-sync/README.md
[docker]: https://docs.docker.com/engine/install/
[generate_assets_json]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/common/testproxy/transition-scripts/generate-assets-json.ps1
[git_setup]: https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
[git_token]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
[podman]: https://podman.io/getting-started/installation.html
[powershell]: https://learn.microsoft.com/powershell/scripting/install/installing-powershell?view=powershell-latest
[recording_updates]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#run-tests-with-out-of-repo-recordings
[transition_script]: https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/testproxy/transition-scripts
