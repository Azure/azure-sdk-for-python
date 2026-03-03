# Conda Release Process

Azure SDK for Python ships new releases to Conda on a **quarterly cadence** (March 1, June 1, September 1, December 1). Two pipelines work together to make this happen:

1. **Conda Update Pipeline** — opens a PR with updated Conda recipes, release logs, and yml files needed for building artifacts.
2. **Conda Build/Release Pipeline** — builds the conda packages and publishes them to Anaconda.

## Release Steps

This section covers instructions for managing a quarterly conda release, which require a few manual steps.

### Prerequisites
- Create an account on https://anaconda.org/ 
   - Use the "sign up with email" option with your Microsoft email
- Contact Steve Dower to join the AzureSDK group on https://anaconda.org/microsoft

### Automated PR Creation

The **[Conda Update Pipeline](https://dev.azure.com/azure-sdk/internal/_build?definitionId=8044&_a=summary)**  (`conda-update-pipeline.yml`) runs automatically about one week before each quarterly release date. It:

- Detects which packages have new GA versions since the last conda release, using the [Python Packages CSV](https://github.com/Azure/azure-sdk/blob/main/_data/releases/latest/python-packages.csv) as the source of truth.
- Updates package versions across the repo's conda configuration files.
- Opens a PR on `main` with all the necessary changes.
   - The PR link can be found in the pipeline output for the "Create pull request" step

You can also trigger it manually from [Azure DevOps](https://dev.azure.com/azure-sdk/internal/_build?definitionId=8044&_a=summary) if needed.

#### Conda File Updates

The "Update Conda Files" step of the pipeline runs a script to update Conda files. It logs changes made, and outputs packages that may need manual adjustments. It may output:
- **Deprecated packages**: 
   - Packages with existing Conda metadata that were missing from the CSV will be flagged. 
   - Check if these are really deprecated. If so, related package metadata should be kept until the package is retired, and then it can be fully deleted.
- **Unknown bundle packages**: 
   - Packages need to specify if they are released individually or as a bundle to Conda, in their `pyproject.toml`. Packages without this metadata will be flagged.
- **Other**: 
   - Packages may be flagged when encountering various unexpected behaviors or exceptions, such as failing to generate or process its metadata files, etc. Manually check these to ensure changes are correct.

#### Dry Run

The update pipeline has a **Dry Run** option. When enabled, it runs the update script and shows what would change, but skips opening the PR.

### What the PR Contains

The auto-generated PR includes:

- **Version bumps** for packages that have released new GA versions since the last conda release.
- **New package entries** for any GA packages that weren't previously included in conda.
- **Updated release logs** (`conda/conda-releaselogs/`) documenting which package versions are in this release.
- **New conda recipes** (`conda/conda-recipes/<package>/meta.yaml`) for brand-new data plane packages.

### Review, Approve, and Cleanup (manual)

1. **Review the PR.** Check the report in the pipeline output for any packages that encountered unexpected behavior and may need manual fixes.
   - The PR triggers a [public build](https://dev.azure.com/azure-sdk/public/_build?definitionId=8092) which validates the changes to the Conda recipes.

2. **Merge the PR** into `main`.

3. **Handle new data plane packages** (if any are listed in the pipeline output):
   - Submit the [Conda placeholder form](https://forms.office.com/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR180k2XpSUFBtXHTh8-jMUlUNlA1MFpZOVhZME1aNU1EU1Y3SjZRU0JNRC4u) to create a private dummy library on Conda for **each new data plane** package (group name AzureSdk). 
      - ⚠️**This must be done before uploading to Conda / approving the upload stage.** ⚠️
      - The form submits a request to create the placeholder library, which must be **manually approved** (allow enough buffer time for this).
         - Contact Steve Dower with questions related to this form. 
      - Verify from the Anaconda portal that the placeholders have been added before proceeding.
   - Create an AKA link for new release logs at [https://aka.ms/](https://aka.ms/).
      - The `meta.yaml` for the new package(s) will contain the short link to use.

4. **Build the packages.** Merging to main triggers the internal **[Conda Build/Release Pipeline](https://dev.azure.com/azure-sdk/internal/_build?definitionId=6321)** (`conda-sdk-client.yml`) automatically, but you must queue a manual run to enable the release stage. Running manually also enables customization of which packages to include.

5. **Approve the release.** After a successful build, the pipeline will show a pending approval gate. Approve it to publish the packages to Anaconda (under the `Microsoft` channel).

6. **Post-release cleanup in Anaconda** (for new packages only):

   Log in to [Anaconda.org](https://anaconda.org/) and navigate to the package page:

   a. **Delete placeholder:** Go to the package settings and remove the dummy placeholder library (version 0.0.0) created in step 3.

   b. **Make public:** In the package settings, change the visibility from private to public.

## Troubleshooting

### Release Failures

#### Not enough permission to create
```
Unauthorized: ('User "<User: _login=<...>>" has not enough permissions to create "<User: _login=microsoft>/<package>>" package', 401)
```

- This error indicates there is no existing entry in Anaconda for this package. Ensure you've submitted the form to request a placeholder for new data plane packages. 

- After resolving release issues, it is safe to rerun the build pipeline with all package parameters even if some packages were already uploaded, as the upload will just skip existing packages in Anaconda.

## Developer Guide

For more detail on the Conda release infrastructure, see [`conda-release-dev.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-release-dev.md).
