# Release process

## Prerequisites
First, ensure your code on `main` is ready to publish.

For management (control plane) packages, start with this page: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/mgmt_release.md

For client (data plane) packages, ensure that:
- The version at `sdk/path-to-your-package/_version.py` has been updated following [these guidelines](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/package_version/package_version_rule.md).
- The changelog has been updated following [these guidelines](https://azure.github.io/azure-sdk/policies_releases.html#change-logs).
- Package README has been updated following [these guidelines](https://azure.github.io/azure-sdk/python_documentation.html).
- Samples have been updated following [these guidelines](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/sample_guide.md).

## Python Package Index

Python packages are uploaded to [PyPI](https://pypi.org/). Once you've uploaded to PyPI, there's no way to overwrite the package. In case of problems, you'll need to increment the version number. Be sure that before going forward your package has passed all the necessary testing.

### Production - Deploy with Azure DevOps

To avoid "accidental" pushes to our target repositories, [approval](https://learn.microsoft.com/azure/devops/pipelines/release/approvals/approvals?view=azure-devops) will be requested directly prior to the final PyPI publish. Reference this [page](https://aka.ms/azsdk/access) to learn how to request access to Azure SDK DevOps for release approval.

Instead of a single central pipeline, the python SDK has moved to `service directory` associated build pipelines. These are driven by yml templates at the root of each service folder. [Example for storage service folder.](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/ci.yml#L44)

#### Releasing Through Unified Pipelines

1. Begin by locating your pipeline on the `internal` project under the `python` folder. Naming convention is `python - <servicedir>`.
    1. To release any package under the folder `sdk/core`, you would queue a build against [python - core](https://dev.azure.com/azure-sdk/internal/_build?definitionId=983&_a=summary) pipeline.
2. After queuing the build, a last test pass will execute prior to splitting into a release job per defined artifact.
3. Click `approve` only on packages that you wish to release to pypi. Reject all others.
    1. [A partially approved build will look like this](https://dev.azure.com/azure-sdk/internal/_build/results?buildId=176564&view=results)

Validate artifacts prior to clicking `approve` on the release stage for the package you wish to release.

[Additional Internal Wiki Walkthrough](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/69/Package-release-via-Unified-Pipelines)

> **Note:** All releases to PyPI are handled through the ESRP release process. Manual uploads via `twine` are no longer permitted. See [ESRP Release Process](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/esrp_release.md) for details.

# NOTE REGARDING ARTIFACTS
Note that the unified pipeline will maintain a separate release step for each defined artifact in the `Artifacts` parameter in the relevant `ci.yml` file. [Example](https://github.com/Azure/azure-sdk-for-python/blob/cffaa424f4198bae99033c8ab2474fe87fb2451a/sdk/storage/ci.yml#L44)

The `name` parameter is **required** to be the exact package name with `_` in place of `-`. `safeName` must be unique.

Example Artifact List in `ci.yml`:

```
    Artifacts:
    - name: azure_core
      safeName: azurecore
    - name: azure_core_tracing_opencensus
      safeName: azurecorecoretracingopencensus
```

Resulting Release Stages:

![Example Release Stages](./release_stage.png "Example Release Stages")

This means that new `mgmt` packages **_must_**  be added to this list of artifacts manually.
