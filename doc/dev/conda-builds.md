# Azure SDK for Python Conda Distributions

The azure-sdk team maintains a suite of conda recipes built from combinations of other official pypi packages released from this repository. These packages are released on a 3-month cadence, built from a single configuration present in `eng/pipelines/templates/stages/conda-sdk-client.yml`.

The value of `CondaArtifacts` parameter is serialized to json, then consumed by the tooling CLI to create a set of conda packages.

## Local Environment Setup

Follow the instructions [here](https://docs.conda.io/projects/conda-build/en/latest/install-conda-build.html) to install `conda` and `conda-build`.

## CI Build Process

The quarterly CI build/release process is documented in full in
[conda-release.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-release.md) —
the recipe/version updates are produced automatically by the Conda Update
Pipeline, and the packages are built and published by the Conda Build/Release
Pipeline. Refer to that document as the single source of truth for releasing;
this page focuses on building a conda package locally.

## How to Build an Azure SDK Conda Package Locally

### Install the required tooling

```bash
# cd <repo root>
pip install "eng/tools/azure-sdk-tools[conda]"
```

### Get the configuration blob

To generate a configuration blob, I personally just use [this site.](https://jsonformatter.org/yaml-to-json)

Paste a snippet copy-pasted from `conda-sdk-client.yml`. Use the output json as an argument to `sdk_build_conda` as described below.

### Generate the Conda Package

```bash
# you will probably need to escape the json quotes
sdk_build_conda -c "<json config blob>" --channel "additional/channel/if/you/want/one"
```
