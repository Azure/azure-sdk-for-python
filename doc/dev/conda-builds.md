# Azure SDK for Python Conda Distributions

## Local Environment Setup

Follow the instructions [here](https://docs.conda.io/projects/conda-build/en/latest/install-conda-build.html) to install `conda` and `conda-build`.

**The Azure SDK Conda artifacts support `python3.8` and `python3.9` only.**

## CI Build Process

There will be a `CondaArtifact` defined in the `ci.yml` of each service directory. (`sdk/<service>`)

A Conda Artifact defines:
- The location of the `meta.yml`
- Which packages will be pulled into the combined artifact
- The name of the combined artifact
- Any other necessary details.

## How to Build an Azure SDK Conda Package Locally
#### If using powershell, you will need to prep your environment before proceeding to the next step

```
powershell -ExecutionPolicy ByPass -NoExit -Command "& '<path-to-conda-folder>\shell\condabin\conda-hook.ps1' ; conda activate '<path-to-conda-folder>' "
```

Afterwards, invoke `conda init powershell` and re-create the pshell session.

By default, your powershell environment will now load `conda`. If you want pure pip, you will need to use explicit invocations of your `python` locations to create virtual envs.
### Set up your conda environment


You will notice that all the azure-sdk conda distributions have the **same** version number and requirement set. This is due to the fact that the azure-sdk team pushes our conda packages out in waves. To support this, all versions are set via a common environment variable `AZURESDK_CONDA_VERSION`.

We keep this environment variable set properly across all our builds by using a common `conda_env.yml` when creating our build environment. This environment definition ensures that: 

1. Our channel `https://azuresdkconda.blob.core.windows.net/channel1/` is added to the set to download packages
2. The environment variable `AZURESDK_CONDA_VERSION` will be set exactly once.
  

Reference the `conda_env.yml` in your local build by pass `-f <path to conda_env.yml>` when you create your conda environment.

```
conda env create --yes --quiet --name ${{ artifact.name }} -f $(Build.SourcesDirectory)/eng/conda_env.yml
```

### Create Your Build Directory
Given how Conda packages are comprised of multiple source distributions _combined_, the buildable source does not exist directly within the azure-sdk-for-python repo. Currently, there is _some_ manual work that needs to be done.

To begin, check your `ci.yml` for a `CondaArtifact`. Each these artifacts will become a single conda package. Let's use `storage/ci.yml` as an example.

```
    - name: azure-storage
      meta_source: meta.yml
      common_root: azure/storage
      checkout:
        - package: azure-storage-blob
          checkout_path: sdk/storage
          version: 12.8.0
        - package: azure-storage-queue
          checkout_path: sdk/storage
          version: 12.1.5
        - package: azure-storage-file-share
          checkout_path: sdk/storage
          version: 12.4.1
        - package: azure-storage-file-datalake
          checkout_path: sdk/storage
          version: 12.3.0
```

- `name: azure-storage`: will be the name of the "combined" sdist package that we generate.
- `meta_source: meta.yml`: this is the path (relative to the service directory) to the target conda package meta.yml.
- `common_root: azure/storage`: when generating the combined package, where will we begin combining? This is tightly bound to folder structure within the generated sdist.
- `checkout`: the `checkout` setting is a list of target packages that will go into the combined artifact. These targets will be individually sparse cloned, and copied into the conda build directory. Currently, this is a **manual step** in your local build. Reference `eng/pipelines/templates/get-tagged-code.yml` for exact details on how CI does it.

Before we continue, you should be aware of two primary locations that are necessary, but not referenced directly in the `ci.yml`.

The `build` folder and the `output` folder. The `build` folder (`$(Conda.Build)` variable in CI) is where we will...

- store the cloned package code
- generate the combined sdist

To locally repro without magic given a specific `checkout` artifact:

```
<cd sdk-for-python>
git checkout `<package>_<version>`
grab the entire <package> directory under the <checkout_path>. place into your `build` folder.
```

Given the `storage` example. This is what your `build` folder should look like prior to invoking `build_conda_artifacts.py`.

```
<build directory>/
    azure-storage-blob/          <-- the package directly ripped from specified tag
    azure-storage-file-datalake/
    azure-storage-file-share/
    azure-storage-queue/
```

### Create the Combined SDist

Once you have a directory assembled, invoke the script to build. The below command is formatted for visibility, recombine the lines however necessary for your chosen shell environment.


```
python `build_conda_artifacts.py`
    -d "<output folder>"
    -b "<build folder>"
    -m "<resolvable path to sdk/storage/meta.yml>"
    -r "azure/storage"
    -n "azure-storage"
    -s "storage"
    -e "<resolvable path to repo root>/eng/conda_env.yml"
    -c "<resolvable path to sdk/storage/ci.yml>"
```

### Generate the Conda Package

Locally, from the anaconda prompt, set the environment variable `STORAGE_SOURCE_DISTRIBUTION` to the location of the generated sdist. After that:

```bash
export STORAGE_SOURCE_DISTRIBUTION=<path/to/generated/sdist>
cd <meta.yml directory>
conda-build . --output-folder <conda.output>
```
