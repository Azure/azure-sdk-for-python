# Azure SDK Conda Recipes

The conda recipes contained within this folder are used in conjunction with the azure-sdk-tools command `sdk_build_conda`.

This script accepts a json blob which defines a set of workloads (defined in `eng/pipelines/templates/stages/conda-sdk-client.yml`), then for each one:

- Download the necessary source distribution code
- Assemble a combined source distribution (in `azure-storage` case combining `queue`, `blob`, `file`, and `datalake`)
- Generate a `meta.yml` that references the newly created source distribution
- Assemble the final conda package using the `meta.yml`

If a json blob workload is not provided, a default one is generated from a `yml` configuration. Again, this file is located at `eng/pipelines/templates/stages/conda-sdk-client.yml`.

Within, there is a parameter defined called `CondaArtifacts` being passed to template `build-conda-artifacts`. That is the value that is parsed out, defaulting the `in_batch` variables to `True`. If you don't specify, you get everything!
