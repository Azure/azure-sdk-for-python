# Conda Release Process

Azure SDK for Python ships new releases to Conda on a **quarterly cadence** (March 1, June 1, September 1, December 1). Two pipelines work together to make this happen:

1. **Conda Update Pipeline** — opens a PR with updated Conda recipes, release logs, and yml files needed for building artifacts.
2. **Conda Build/Release Pipeline** — builds the conda packages and publishes them to Anaconda.

## Release Steps

This section covers instructions for managing a quarterly conda release, which require a few manual steps.

### Prerequisites
- Create an account on https://anaconda.org/
- Contact Steve Dower to join the AzureSDK group on https://anaconda.org/microsoft

### Automated PR Creation

The **[Conda Update Pipeline](https://dev.azure.com/azure-sdk/internal/_build?definitionId=8044&_a=summary)**  (`conda-update-pipeline.yml`) runs automatically about one week before each quarterly release date. It:

- Detects which packages have new GA versions since the last conda release, using the [Python Packages CSV](https://github.com/Azure/azure-sdk/blob/main/_data/releases/latest/python-packages.csv) as the source of truth.
- Updates package versions across the repo's conda configuration files.
- Opens a PR on `main` with all the necessary changes.

You can also trigger it manually from [Azure DevOps](https://dev.azure.com/azure-sdk/internal/_build?definitionId=8044&_a=summary) if needed.

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

2. **Handle new data plane packages** (if any are listed in the pipeline output):
   - Submit the [Conda placeholder form](https://forms.office.com/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR180k2XpSUFBtXHTh8-jMUlUNlA1MFpZOVhZME1aNU1EU1Y3SjZRU0JNRC4u) to create a private dummy library on Conda for **each new data plane** package (group name AzureSdk). 
      - ⚠️**This must be done before uploading to Conda / approving the upload stage.** ⚠️
      - The form triggers a pipeline to push the placeholder library. Verify from the Anaconda portal that the placeholders have been added before proceeding.
   - Create an AKA link for new release logs at [https://aka.ms/](https://aka.ms/).

3. **Merge the PR** into `main`.

4. **Build the packages.** Merging triggers the **[Conda Build/Release Pipeline](https://dev.azure.com/azure-sdk/internal/_build?definitionId=6321)** (`conda-sdk-client.yml`) automatically. You can also run it manually and select which packages to include.

5. **Approve the release.** After a successful build, the pipeline will show a pending approval gate. Approve it to publish the packages to Anaconda (under the `Microsoft` channel).

6. **Post-release cleanup in Anaconda** (for new packages only):

   Log in to [Anaconda.org](https://anaconda.org/) and navigate to the package page:

   a. **Delete placeholder:** Go to the package settings and remove the dummy placeholder library created in step 2.

   b. **Make public:** In the package settings, change the visibility from private to public.

## Developer Guide

For more detail on the Conda release infrastructure, see [`conda-release-dev.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-release-dev.md).
