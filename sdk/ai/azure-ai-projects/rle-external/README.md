# External RLE SDK preview distribution

The public distribution contains only packaged `azure-ai-projects` wheels, this
documentation, [`install_rle_sdk.py`](./install_rle_sdk.py), and a
[`registry.json`](./registry.json) manifest. It requires no source repository
access or credentials. Wheels contain Python code: publishing them is public
distribution of the implementation, not a way to keep shipped code confidential.

## Install

Download the installer from the maintained `rle-external-releases` branch of
`Azure/azure-sdk-for-python`, then run:

```powershell
python install_rle_sdk.py
$env:AZURE_AI_PROJECTS_RLE_VERSION = "2.7.0.dev20261012000000"
python install_rle_sdk.py
```

The example version is illustrative; use a version listed in the registry.
Selection order is `--version`, `AZURE_AI_PROJECTS_RLE_VERSION`, `--version-file`,
then `latest`. An empty, invalid, or unavailable explicit version fails. The
installer verifies the wheel's SHA-256, package version, RLE extra and environment
module before pip installs the wheel with its `rle` dependencies. Dependencies
use the normal pip index or `--index-url`; the SDK itself never resolves through
that index. `--requirements` installs other requirements in the same transaction.

## Manifest contract

The manifest is a JSON object with `schema_version: 1`, `package:
"azure-ai-projects"`, `channel: "rle-external"`, `latest`, and `versions`. Each
version maps to a wheel `filename`, immutable commit-pinned public `url`, and
lowercase hexadecimal `sha256`. Only universal `py3-none-any` wheels with unique
`MAJOR.MINOR.PATCH.devNUMBER` versions are supported. `latest` means the most
recent deliberately published RLE build, not the latest package on PyPI.
Existing version entries and artifacts must never be overwritten.

## Container builds

Use a remote Docker `ADD` of the registry before SDK installation. Its content
participates in the build cache, so a changed latest pointer invalidates the SDK
installation layer. `pip --no-cache-dir` alone does not invalidate Docker layers.
Do not bake a snapshot of the registry into the sample.

Use `ARG AZURE_AI_PROJECTS_RLE_VERSION` for builders that accept build arguments.
Host environment variables must be explicitly forwarded as build arguments;
setting a runtime container variable cannot replace an already installed SDK.
For builders without argument forwarding, copy a sample-local
`sdk-version.txt` containing `latest` or the exact version into the build.

## Maintainer release process

Release tooling lives in the source checkout at
`sdk/ai/azure-ai-projects/scripts/rle-external/release.py`, not in this public
distribution. Install the `build` package in a dedicated maintainer environment.
Commit SDK implementation changes before building.

```powershell
python sdk\ai\azure-ai-projects\scripts\rle-external\release.py `
  --public-checkout C:\work\azure-sdk-for-python-rle-external

# After inspecting the prepared artifacts:
python sdk\ai\azure-ai-projects\scripts\rle-external\release.py `
  --public-checkout C:\work\azure-sdk-for-python-rle-external --publish-only
```

Use `--publish` to build and publish in one invocation, and `--version` to choose
an explicit unique development version. Otherwise a UTC timestamp is appended to
the SDK base version. The source package version is never modified in place.

The public checkout is separate from the source checkout and based on upstream
`main`. First use creates it automatically. Only wheel artifacts, installer,
manifest and this documentation may differ from upstream. Artifact and manifest
updates use separate commits so manifest URLs pin immutable artifact commits.
Publishing uses `GH_TOKEN`, `GITHUB_TOKEN`, or Git's GitHub credentials; it requires
write permission on the upstream distribution branch and permission to open PRs.
No credentials are written into repository files or remote URLs.
If Git Credential Manager has multiple accounts, pass `--github-user <account>`
to select the existing GitHub login without changing global Git settings.

Publishing verifies the manifest and every retained wheel anonymously, then
creates or reuses a draft PR. If upload or verification fails, the command fails;
retry the prepared release with `--publish-only`. Keep the branch available even
if the PR is closed. Deleting it breaks latest discovery.
