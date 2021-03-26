# Azure SDK for Python Conda Distributions

## Local Environment Setup

Follow the instructions [here](https://docs.conda.io/projects/conda-build/en/latest/install-conda-build.html) to install `conda` and `conda-build`.

## CI Build Process

There will be a `CondaArtifact` defined in the `ci.yml` of each service directory. (`sdk/<service>`)

A Conda Artifact defines:
- The location of the `meta.yml`
- 

## How to Build an Azure SDK Conda Package Locally

Given how Conda packages are comprised of multiple source distributions _combined_, the buildable source does not exist directly within the azure-sdk-for-python repo. Instead, you will need to invoke the `build-conda-package.py` abstraction layer that the EngSys team has created to automate this work.

The elements within your `ci.yml` that define the `CondaArtifact` will be used directly in your local invocation of this script.