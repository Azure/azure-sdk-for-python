---
name: azure-ai-projects-cloud-regeneration
description: 'Regenerate only azure-ai-projects from TypeSpec in a GitHub Copilot cloud-agent session, using a package-specific Actions runner to install pinned npm and Python dependencies outside the agent firewall. Use for cloud regeneration scoped to sdk/ai/azure-ai-projects, including packagefeedproxy DNS blockers. Do not use for other packages or local interactive emission.'
---

# Cloud regeneration for azure-ai-projects

Run this workflow only for `sdk/ai/azure-ai-projects`. The repository-wide
`copilot-setup-steps.yml` is deliberately unchanged. GitHub does not support a
directory-local pre-agent setup file or selecting setup steps from a scoped prompt.

Instead, the manually dispatched `azure-ai-projects-regenerate.yml` workflow
installs dependencies, emits this package, runs `PostEmitter.ps1`, and validates
on a normal Actions runner. The cloud agent downloads and applies the validated
patch; it does not need to install npm packages or the development wheel inside
its restricted environment. Runtime emitter downloads also happen on that runner.

## 1. Select the source

Confirm the SDK working directory with `git rev-parse --show-prefix`; it must be
`sdk/ai/azure-ai-projects/`. Record `git rev-parse HEAD` as `SDK_COMMIT`.
If there are uncommitted changes that generation must include, preserve them on
the cloud agent's own task branch before dispatching. Do not overwrite user edits.
The SDK commit must be available in `Azure/azure-sdk-for-python`. The runner uses
the orchestration script from the workflow's own revision, so the selected SDK
revision does not have to contain that script.

Use the full 40-character TypeSpec SHA requested by the user. Otherwise retain
the commit in `tsp-location.yaml`; do not silently advance to another branch.
If the user requests the latest Foundry source, resolve the latest commit touching
`specification/ai-foundry/data-plane/Foundry` on `feature/foundry-release` in
`Azure/azure-rest-api-specs`, then pass its full SHA.

## 2. Dispatch the package workflow

The workflow must be present on the repository's default branch. Dispatch needs
a GitHub credential with **Actions: write** for this repository; reading logs and
downloading artifacts needs **Actions: read**. A cloud agent's default credential
may not allow dispatch. Do not assume that permission, print credentials, or try
to change administrator settings. If dispatch is denied, report the exact command
for an authorized maintainer to run, then use the run ID they provide.

From the package directory, create a unique request ID, then dispatch:

```bash
SDK_COMMIT="$(git rev-parse HEAD)"
REQUEST_ID="$(python -c 'import uuid; print(uuid.uuid4())')"
gh workflow run azure-ai-projects-regenerate.yml \
  --repo Azure/azure-sdk-for-python \
  -f sdk_ref="$SDK_COMMIT" \
  -f typespec_commit="<full-TypeSpec-SHA-or-empty>" \
  -f request_id="$REQUEST_ID"
```

These commands target the default-branch workflow, which checks out `sdk_ref`.
Do not submit a PR URL or abbreviated commit as `typespec_commit`.

Find the newly dispatched run by its **exact** display title
`azure-ai-projects regeneration (<REQUEST_ID>)`, not simply the newest run:

```bash
gh run list --repo Azure/azure-sdk-for-python \
  --workflow azure-ai-projects-regenerate.yml --event workflow_dispatch \
  --limit 20 --json databaseId,displayTitle,status,conclusion
gh run watch <RUN_ID> --repo Azure/azure-sdk-for-python --exit-status
```

If the run fails, inspect `gh run view <RUN_ID> --log-failed`. Do not apply an
artifact from another run or report a failed validation as successful. The workflow
publishes its patch only after generation and all configured checks pass.

## 3. Download and apply the result

Download to a fresh temporary directory outside the repository:

```bash
gh run download <RUN_ID> --repo Azure/azure-sdk-for-python \
  --name azure-ai-projects-regeneration-<RUN_ID> --dir <temporary-directory>
WORKFLOW_SHA="$(gh run view <RUN_ID> --repo Azure/azure-sdk-for-python \
  --json headSha --jq '.headSha')" &&
gh api -H 'Accept: application/vnd.github.raw+json' \
  "repos/Azure/azure-sdk-for-python/contents/sdk/ai/azure-ai-projects/.github/skills/azure-ai-projects-cloud-regeneration/scripts/regenerate.py?ref=$WORKFLOW_SHA" \
  > <temporary-directory>/regenerate.py &&
python <temporary-directory>/regenerate.py \
  apply --artifact-dir <temporary-directory> \
  --typespec-commit "<full-TypeSpec-SHA-or-empty>"
```

Before applying, inspect `result.json`. Pass the same TypeSpec SHA used at dispatch,
or an empty value to retain the local pin. The apply command checks both source
commits, the patch digest, validation results, and every patch path, then runs
`git apply --check`. It refuses a changed baseline, failed checks, out-of-package
edits, or conflicts; do not force it.
An empty patch is a valid no-change result, not a reason to invent edits.

Inspect the applied diff. Follow the existing package sample/test/changelog skills
for additional API changes the task calls for; successful generation does not
replace review of patched clients, preview feature headers, or sample behavior.
Any subsequent code edits need their own validation. Let the cloud agent's normal
task-branch and draft-PR flow handle publication, and preserve the repository PR
template.

Report the Actions run URL, SDK and TypeSpec commits, and the actual checks from
`result.json`. The workflow covers syntax, Black, Pylint, MyPy, and recorded
`devtest` playback; it does not run live tests, samples, or Sphinx, and is not a
release-readiness assertion. Remove the downloaded temporary files when finished.

Black uses the repository's pinned formatter helper in check-only mode, because
`azpysdk black .` can opt out under CI. Revisions that opt out of Pylint or MyPy
are rejected rather than recorded as passing checks.

## Feed failures

The runner uses the repository's documented Azure SDK npm/Python feeds and the
exact wheel URL in `dev_requirements.txt`, not an invented replacement feed.
The CLI is installed with `npm ci` from `eng/common/tsp-client`; emitter dependencies
remain governed by `eng/emitter-package.json` and its lockfile.

If dependency installation still fails on the Actions runner, keep the failure
visible. An administrator must restore the runner's DNS/HTTPS access to the feed
hosts and their actual redirected download hosts. Do not fall back to an unpinned
global CLI, public registries, omitted wheels, or direct-IP downloads.

References:
- [GitHub cloud-agent environment setup](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment)
- [GitHub cloud-agent Internet access](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall)
- [Repository tool and approved Python feed guide](../../../../../../doc/tool_usage_guide.md)
- [Azure SDK Python design guidelines](https://azure.github.io/azure-sdk/python_design.html)
