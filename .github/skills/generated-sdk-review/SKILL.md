---
name: generated-sdk-review
description: "Review a Python package generated from an open TypeSpec spec pull request. USE FOR: generated SDK review, spec PR still open, management-plane API findings, schema version 1 review report. DO NOT USE FOR: editing the spec, regenerating the SDK, posting pull request comments, data-plane packages, or telling the author where to fix a finding."
---

# Generated SDK review

Use this skill while a TypeSpec spec pull request is still open.
The central workflow has already generated the Python package.
Read that package and write a short report of real API problems.

The report uses one fixed JSON shape, schema version 1, from [azure-rest-api-specs#48168](https://github.com/Azure/azure-rest-api-specs/issues/48168).
An empty `findings` list is a valid report.
This skill does not edit files, regenerate code, or post comments.

## Supported libraries

| Plane | Packages | Pilot | Evidence |
| --- | --- | --- | --- |
| Management | `azure-mgmt-*` under `sdk/*/azure-mgmt-*/` | `sdk/compute/azure-mgmt-compute` | `tsp-location.yaml` points at `specification/compute/resource-manager/Microsoft.Compute/Compute` in `Azure/azure-rest-api-specs`, commit `d218330c5a3b727df9504ba852e97259479e8fef`. Known finding: [spec PR 40203](https://github.com/Azure/azure-rest-api-specs/pull/40203) and [SDK PR 48997](https://github.com/Azure/azure-sdk-for-python/pull/48997). |
| Data | Not supported yet | Not selected | There is no data-plane rule file comparable to `.github/instructions/reviewer/management.instructions.md`. Follow-up owner: the CODEOWNERS of this skill folder. |

Do not review a data-plane package with this skill.
Do not emit a clean report for one.
The checker rejects package names that do not start with `azure-mgmt-`.

## Input

The central workflow supplies a read-only workspace, the spec pull request number, the spec head SHA, the SDK baseline commit, the package name, and the changed files.
Build this context JSON before running the checker.

```json
{
  "specPrNumber": 40203,
  "specHeadSha": "<spec head sha>",
  "skillRevision": "<commit of this skill>",
  "baselineCommitSha": "<sdk baseline sha>",
  "packageName": "azure-mgmt-compute",
  "firstRelease": false,
  "changedFiles": ["sdk/compute/azure-mgmt-compute/_metadata.json"],
  "files": {
    "sdk/compute/azure-mgmt-compute/_metadata.json": {
      "baseline": "<file text at the baseline commit>",
      "head": "<file text in the generated workspace>"
    }
  }
}
```

Set `firstRelease` to true only when the package directory is absent at the SDK baseline and the changelog has no earlier release.
Leave it false for an existing release.
Do not infer a first release from a missing baseline.

`files` may include unchanged files as context.
A finding can name only a path listed in `changedFiles`.

## Report

Return exactly these fields.

```json
{
  "schemaVersion": 1,
  "status": "completed",
  "skillRevision": "<commit of this skill>",
  "source": {
    "specPrNumber": 40203,
    "specHeadSha": "<spec head sha>"
  },
  "reviews": [
    {
      "baselineCommitSha": "<sdk baseline sha>",
      "packages": ["azure-mgmt-compute"],
      "findings": [
        {
          "severity": "high",
          "file": "sdk/compute/azure-mgmt-compute/_metadata.json",
          "line": 5,
          "title": "API versions changed",
          "description": "The apiVersions map changed. ComputeGallery changed from 2025-12-03 to 2026-03-03."
        }
      ]
    }
  ]
}
```

Use one review for the one baseline.
`packages` is the package name from the input.
`severity` is `high`, `medium`, or `low`.
`file` is one of `changedFiles`.
`line` is a 1-based line in the head text of that file.
Use one finding per root cause.
Do not repeat the same problem for every file it touches.

## Steps

1. Confirm the package name starts with `azure-mgmt-`.
   Stop when it does not.
2. Read `.github/instructions/reviewer/management.instructions.md`.
   Skip `generated_samples/` and `generated_tests/`.
   Under `azure/mgmt/**/`, review `_client.py` for the client rules, and read other generated files only as evidence for version, metadata, and documentation checks.
3. Run the checker from the repository root:

```bash
python .github/skills/generated-sdk-review/scripts/review_report.py context.json
```

The checker reads the context and prints the report.
It does not modify the workspace.
4. Keep every finding the checker printed.
5. Add a finding only when the checker did not already report that root cause and the evidence is on a changed line.
   Use `high` for a problem the management rules call blocking.
   Use `medium` for a changelog date more than three weeks in the future.
   Leave style comments out.
6. Check the finished report against the shape above before returning it.

The checker covers five rules:

- `apiVersions` map drift between the baseline and head `_metadata.json`.
  The singular `apiVersion` field is ignored.
  A service name that contains `preview` is not a preview API.
- A preview value in `apiVersions` requires a beta `VERSION` such as `1.0.0b1`.
- A changelog whose latest notes are `tool can't generate changelog for this release, please update manually.`
- On a confirmed first release, each public client class in a changed `_client.py` ends with `MgmtClient`.
- A changed client `__init__` starts with `credential`, `subscription_id`, `base_url`.

Apply the remaining management rules yourself when the files are present: version matches the changelog, stability classifiers, client name matches the README and `pyproject.toml` title, `no_sub` when `subscription_id` is absent, and README snippets that match the real signature.
Also apply the [Python design guidelines](https://azure.github.io/azure-sdk/python_design.html) to changed public API.
Point at the TypeSpec or `client.tsp` cause in the description when the generated file is not the place to edit.

## Evals

`evals/cases/` holds three published findings:

- [SDK PR 48997](https://github.com/Azure/azure-sdk-for-python/pull/48997) / [spec PR 40203](https://github.com/Azure/azure-rest-api-specs/pull/40203): `ComputeGallery` changed from `2025-12-03` to `2026-03-03`.
- The same SDK PR, at revision `df767e9732548bc103d7a571b711b36155a1bcab`: the 38.4.0 changelog was still the generator placeholder.
  The spec commit on that revision is [spec PR 46328](https://github.com/Azure/azure-rest-api-specs/pull/46328).
- [SDK PR 48637](https://github.com/Azure/azure-sdk-for-python/pull/48637) / [spec PR 46621](https://github.com/Azure/azure-rest-api-specs/pull/46621): the API version changed from `2026-07-01-preview` to `2026-08-01-preview`.
  The beta version `1.0.0b1` and the client name `PlatformValidationMgmtClient` were accepted and must not be reported.

CI runs `python -m unittest discover -s evals -p 'test_*.py'` from this skill folder, with `PYTHONPATH` set to `scripts`.

## Maintenance

CODEOWNERS for this folder are @laiapat, @l0lawrence, and @Azure/azsdk-cli, the same owners as `/.github/skills/`.
Update this skill when `.github/instructions/reviewer/management.instructions.md` or the Python emitter changes a rule the checker or the steps above rely on.
Add a new file under `evals/cases/` when a later review finds an important miss, using the published pull request as the expected outcome.
The Python language team still needs to confirm a named person for the issue checklist.
