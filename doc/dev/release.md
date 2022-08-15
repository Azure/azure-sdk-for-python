# Release process

### Disclaimer
This article assumes you have code on `main` that is ready to publish:
- Version is accurate
- ChangeLog is updated
- Readme is accurate, etc.

If you don't, and you are working with Management packages, start with this page:
https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/mgmt_release.md


## Python Package Index

Python packages are uploaded to [PyPI](https://pypi.org/). Once you've uploaded to PyPI, there's no way to overwrite the package. In case of problems, you'll need to increment the version number. Be sure that before going forward your package has passed all the necessary testing.

### Production - Deploy with Azure Dev Ops

To avoid "accidental" pushes to our target repositories, [approval](https://docs.microsoft.com/azure/devops/pipelines/release/approvals/approvals?view=azure-devops) will be requested directly prior to the final PyPI publish. Reference this [wiki page](https://aka.ms/python-approval-groups) and click on `Release to PyPI Approvers` to add yourself to the group for PyPI publishing.

Instead of a single central pipeline, the python SDK has moved to `service directory` associated build pipelines. These are driven by yml templates at the root of each service folder. [Example for storage service folder.](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/ci.yml#L44)

As an aside, please note that the preview feature `multi-stage pipelines` must be enabled to properly interact with unified pipelines. If you aren't aware, find out how to enable by visiting [this link.](https://docs.microsoft.com/azure/devops/project/navigation/preview-features?view=azure-devops)

#### Releasing Through Unified Pipelines

1. Begin by locating your pipeline on the `internal` project under the `python` folder. Naming convention is `python - <servicedir>`.
    1. To release any package under the folder `sdk/core`, you would queue a build against [python - core](https://dev.azure.com/azure-sdk/internal/_build?definitionId=983&_a=summary) pipeline.
2. After queuing the build, a last test pass will execute prior to splitting into a release job per defined artifact.
3. Click `approve` only on packages that you wish to release to pypi. Reject all others.
    1. [A partially approved build will look like this](https://dev.azure.com/azure-sdk/internal/_build/results?buildId=176564&view=results)

Validate artifacts prior to clicking `approve` on the release stage for the package you wish to release.

[Additional Internal Wiki Walkthrough](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/69/Package-release-via-Unified-Pipelines)

### Production - Deploy manually

To build a package manually:
```
python .\build_package.py azure-mgmt-myservice
```

This will a sdist and a wheel file. This requires `wheel` package installed in your environment.

If you want to manually release on a regular basis, you should create a .pypirc:
```
[pypi]
repository = https://pypi.python.org/pypi
username = <yourusername>
password = <yourpassword>
```

To upload to production:
```
twine upload dist\*.zip
twine upload dist\*.whl
```

It's recommended that you create a Github tag using the format "packagename_version". Example: `azure-mgmt-compute_2.0.0`

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

# IMPORTANT NOTE

If this is a new package (i.e. first release), the "microsoft" account MUST be added as owner of your package. Please contact the engineering system team to do so.
