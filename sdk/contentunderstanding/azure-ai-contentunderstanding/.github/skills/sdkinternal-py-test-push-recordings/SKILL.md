---
name: sdkinternal-py-test-push-recordings
description: "Push test recordings to the azure-sdk-assets repository after recording tests."
---

## Purpose

This skill pushes test recordings for the Azure AI Content Understanding SDK (`azure-ai-contentunderstanding`) to the [azure-sdk-assets](https://github.com/Azure/azure-sdk-assets) repository. After running tests in record mode, recordings must be pushed to the assets repo so they can be used for playback tests in CI.

## When to Use

Use this skill when:

- You've just recorded new tests with `AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true`
- Test recordings have been updated due to API changes
- You need to commit test changes for a PR

## Prerequisites

Before pushing recordings, ensure:

1. You have **write access** to the [Azure/azure-sdk-assets](https://github.com/Azure/azure-sdk-assets) repository
   - Requires membership in the `azure-sdk-write` GitHub group
   - See [Permissions to azure-sdk-assets](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/785/Externalizing-Recordings-(Asset-Sync)?anchor=permissions-to-%60azure/azure-sdk-assets%60)
2. **Dev dependencies installed** (required for `manage_recordings.py`):
   ```bash
   # From package directory: sdk/contentunderstanding/azure-ai-contentunderstanding/
   pip install -r dev_requirements.txt
   ```
3. Tests have been run in record mode (`AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest`)
4. The package has a valid `assets.json` file (see "New Package Setup" below)
5. Git is configured with your name and email
6. Git version > 2.30.0 is installed

## New Package Setup

First check if `assets.json` already exists:

```bash
# From repo root: azure-sdk-for-python/
cd sdk/contentunderstanding/azure-ai-contentunderstanding
cat assets.json
```

If `assets.json` already exists (has a `Tag` value), skip to the "Instructions" section.

If `assets.json` doesn't exist, you need to run the migration script. See the [Recording Migration Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md) for details.

The `assets.json` file has this structure:

```json
{
  "AssetsRepo": "Azure/azure-sdk-assets",
  "AssetsRepoPrefixPath": "python",
  "TagPrefix": "python/contentunderstanding/azure-ai-contentunderstanding",
  "Tag": "python/contentunderstanding/azure-ai-contentunderstanding_e261fca8e6"
}
```

## Instructions

1. **Record tests**: Run tests in live mode to capture recordings

   ```bash
   # From repo root: azure-sdk-for-python/
   cd sdk/contentunderstanding/azure-ai-contentunderstanding
   AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest
   ```

2. **Review recording changes** (optional but recommended): Check what recordings changed

   ```bash
   # From repo root: azure-sdk-for-python/
   # Find the local recordings directory
   python scripts/manage_recordings.py locate -p sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json
   
   # Navigate to that directory and use git to review changes
   cd <output_path>
   git status
   git diff <filename>
   ```

3. **Push recordings to assets repo**:

   ```bash
   # From repo root: azure-sdk-for-python/
   python scripts/manage_recordings.py push -p sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json
   ```

4. **Verify `assets.json` was updated**: The `Tag` field should have a new value

   ```bash
   # From repo root: azure-sdk-for-python/
   cat sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json
   ```

5. **Commit the updated `assets.json`**: Include this file in your PR

   ```bash
   # From repo root: azure-sdk-for-python/
   git add sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json
   git commit -m "Update test recording tag"
   ```

## Example

```bash
# From repo root: azure-sdk-for-python/

# Record tests first (if not already done)
cd sdk/contentunderstanding/azure-ai-contentunderstanding
AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest

# Push recordings (from repo root)
cd ../../..
python scripts/manage_recordings.py push -p sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json

# Verify the tag was updated
# From repo root: azure-sdk-for-python/
cat sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json

# Commit the change
# From repo root: azure-sdk-for-python/
git add sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json
git commit -m "Update test recording tag"
```

## Using the Script

This skill includes a script that handles pre-flight checks, git configuration verification, and the push process.

### Script Location

```bash
sdk/contentunderstanding/azure-ai-contentunderstanding/.github/skills/sdkinternal-py-test-push-recordings/scripts/push_recordings.sh
```

### Script Usage

```bash
# From script directory:
# sdk/contentunderstanding/azure-ai-contentunderstanding/.github/skills/sdkinternal-py-test-push-recordings/scripts/

# Push recordings
./push_recordings.sh

# Dry run (see what would be executed)
./push_recordings.sh --dry-run

# Save output to a custom log file
./push_recordings.sh --log my-push.log
```

### Script Features

- **Virtual environment setup**: Automatically creates and activates `.venv` if not present
- **Dependency installation**: Installs `dev_requirements.txt` if `devtools_testutils` is missing
- **Pre-flight checks**: Verifies git is configured, assets.json exists, Git version is compatible
- **Logging**: Saves output to timestamped log files
- **Dry run**: See what would be executed without running
- **Post-run guidance**: Provides next steps after push completes

## manage_recordings.py Commands

The `manage_recordings.py` script supports several verbs:

| Command | Description |
|---------|-------------|
| `locate` | Print the location of the library's locally cached recordings |
| `push` | Push recording updates to a new assets repo tag and update `assets.json` |
| `show` | Print the contents of the provided `assets.json` file |
| `restore` | Fetch recordings from the assets repo based on the tag in `assets.json` |
| `reset` | Discard any pending changes to recordings |

### Usage

```bash
# From repo root: azure-sdk-for-python/
python scripts/manage_recordings.py <verb> -p <path-to-assets.json>
```

If you run from the package directory containing `assets.json`, the `-p` flag is optional:

```bash
# From repo root: azure-sdk-for-python/
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# From package directory: sdk/contentunderstanding/azure-ai-contentunderstanding/
python ../../../scripts/manage_recordings.py push
```

## What Happens When You Push

The `manage_recordings.py push` command:

1. Scans your local recording files
2. Creates a new commit in the azure-sdk-assets repo with your recordings
3. Creates a new Git tag pointing to that commit
4. Updates `assets.json` in your package root with the new tag reference

## Finding Recording Files

### Local Recordings

Recording files are stored locally at:

```
azure-sdk-for-python/.assets/
```

To find your package's recordings:

```bash
# From repo root: azure-sdk-for-python/
python scripts/manage_recordings.py locate -p sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json
```

The output will include an absolute path to the recordings directory.

### Remote Recordings (Assets Repo)

The `Tag` in `assets.json` points to your recordings in the assets repo. View recordings at:

```
https://github.com/Azure/azure-sdk-assets/tree/<Tag>
```

For example:
```
https://github.com/Azure/azure-sdk-assets/tree/python/contentunderstanding/azure-ai-contentunderstanding_e261fca8e6
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'devtools_testutils'"**

- The `push_recordings.sh` script automatically handles this by setting up venv and installing dependencies
- To fix manually, install the dev requirements from the package directory:
  ```bash
  # From package directory: sdk/contentunderstanding/azure-ai-contentunderstanding/
  source .venv/bin/activate  # Activate venv first
  pip install -r dev_requirements.txt
  ```

**"Permission denied" or "Authentication failed"**

- Ensure you have membership in the `azure-sdk-write` GitHub group
- Check your Git credentials are configured correctly
- May need to authenticate via `gh auth login` if using GitHub CLI

**"No recordings to push"**

- Ensure you've run tests in record mode first: `AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest`
- Check recordings changed: `python scripts/manage_recordings.py locate` then `git status` in that directory

**"assets.json not found"**

- See the [Recording Migration Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md) for initial setup

**Push succeeds but `assets.json` unchanged**

- The recordings may already be up to date
- Try re-recording tests with `AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true` first

**Git user not configured**

- Run: `git config --global user.name "Your Name"`
- Run: `git config --global user.email "your.email@example.com"`
- Or set environment variables: `GIT_COMMIT_OWNER` and `GIT_COMMIT_EMAIL`

**Git version too old**

- Git version > 2.30.0 is required
- Check version: `git --version`
- Update Git if needed

**Test proxy not found**

- The test proxy will be automatically downloaded to `.proxy/` when tests run
- If issues persist, try running tests first: `AZURE_TEST_RUN_LIVE=false pytest`

## Important Notes

- **Always commit `assets.json`**: The updated tag must be in your PR for CI to use the new recordings
- **Don't commit local recordings**: The `.assets/` directory is gitignored
- **Recordings are sanitized**: Sensitive data (keys, endpoints) is automatically removed by the test proxy
- **Review before pushing**: Check recordings don't contain any leaked sensitive data
- **CI uses the tag**: If `assets.json` isn't updated, CI will use old recordings and tests may fail

## Related Skills

- `sdkinternal-py-sdk-pre-pr-check` - Run all CI checks before creating a PR
- `sdkinternal-py-env-setup-venv` - Set up virtual environment for development

## Documentation

- [Testing Guide - Update test recordings](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#update-test-recordings)
- [Recording Migration Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md)
- [Asset Sync (Externalizing Recordings)](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/785/Externalizing-Recordings-(Asset-Sync))
- [manage_recordings.py](https://github.com/Azure/azure-sdk-for-python/blob/main/scripts/manage_recordings.py)
