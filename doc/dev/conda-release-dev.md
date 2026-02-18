# Conda Release Infrastructure

This doc is for developers who need to understand or modify the conda release infrastructure specified in [`conda-release.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-release.md).

## Key Files

| Path | Purpose |
|------|---------|
| `conda/conda-recipes/<package>/meta.yaml` | Conda recipe for each package (or bundle). Defines build, dependencies, and tests. |
| `conda/conda-recipes/conda_env.yml` | Stores `AZURESDK_CONDA_VERSION` — the version string used for all conda packages in a release (e.g., `2025.12.01`). |
| `conda/conda-releaselogs/<package>.md` | Per-package (or bundle) release log listing which PyPI package versions are included in each conda release. |
| `conda/update_conda_files.py` | The main automation script. Updates versions, creates recipes, and generates release logs. |
| `conda/conda_helper_functions.py` | Shared helpers for CSV parsing, bundle detection, PyPI queries, etc. |
| `eng/pipelines/conda-update-pipeline.yml` | Pipeline definition for the update/PR workflow. |
| `eng/pipelines/templates/stages/conda-sdk-client.yml` | Pipeline definition for building and releasing conda packages. Contains the `CondaArtifacts` list and per-package release toggles. |
| `eng/pipelines/templates/stages/archetype-conda-release.yml` | Release stage template — uploads `.conda` artifacts to Anaconda. |
| `eng/pipelines/templates/steps/build-conda-artifacts.yml` | Build step template — installs tooling and invokes `sdk_build_conda`. |

## How `update_conda_files.py` Works

The script is the core of the update pipeline. When invoked (with an optional `--release-date MM.DD` argument), it performs these steps in order:

1. **Bumps `AZURESDK_CONDA_VERSION`** in `conda_env.yml` to the target release date (or auto-increments by 3 months).

2. **Parses the [Python package CSV](https://github.com/Azure/azure-sdk/blob/main/_data/releases/latest/python-packages.csv)** to get the latest GA versions and release dates for all Azure SDK packages.

3. **Categorizes packages** into:
   - **Outdated** — already in conda but with a newer GA version available.
   - **New** — GA packages not yet included in conda.
   - Data plane vs. management plane (management plane packages are all bundled together).

4. **Updates `conda-sdk-client.yml`:**
   - Bumps `version` fields for outdated packages in the `CondaArtifacts` list.
   - Adds new `CondaArtifacts` entries and release toggle parameters for new data plane packages.
   - Appends new management plane packages to the `azure-mgmt` bundle's `checkout` list (the list of package paths the pipeline checks out and includes in the bundle).

5. **Creates `meta.yaml` recipes** for new data plane packages (under `conda/conda-recipes/<package>/`). For bundled packages (determined by `[tool.azure-sdk-conda]` in `pyproject.toml`), a single recipe covers the entire bundle.

6. **Updates `azure-mgmt/meta.yaml`** import tests for new management plane packages.

7. **Updates/creates release logs** in `conda/conda-releaselogs/`.

8. **Prints a report** of any packages that couldn't be automatically processed and may need manual attention.

## Package Bundles

Some packages are grouped into a single conda package (a "bundle"). For example, `azure-storage` bundles `azure-storage-blob`, `azure-storage-queue`, etc. Bundle membership is determined by the `[tool.azure-sdk-conda]` section in each package's `pyproject.toml`. 

Bundled packages share:
- A single `meta.yaml` recipe (with combined dependencies and imports).
- A single release log file.
- A single release toggle in `conda-sdk-client.yml`.

Service teams are responsible for updating this metadata, and it is enforced in CI.

## Build Pipeline (`conda-sdk-client.yml`)

**Build stage:**

See [`conda-builds.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-builds.md).

**Release stage (`archetype-conda-release.yml`):**
- Requires deployment approval (environment: `package-publish`).
- Uploads all `.conda` files from the `conda/noarch` artifact to Anaconda using `anaconda-client`, under the `Microsoft` user.

## Versioning

All conda packages in a release share the same version string: `YYYY.MM.DD` (e.g., `2025.12.01`). This is set in `conda/conda-recipes/conda_env.yml` and referenced by every `meta.yaml` via `environ.get('AZURESDK_CONDA_VERSION')`.

## Building Locally

See [`conda-builds.md`](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/conda-builds.md) for instructions on building conda packages locally using `sdk_build_conda`.

## Adding a New Package to Conda Manually

If the automation doesn't handle a new package correctly, the manual steps are:

1. **Add a release toggle** parameter in `conda-sdk-client.yml`.
2. **Add a `CondaArtifacts` entry** with `name`, `service`, `common_root`, `in_batch`, and `checkout` fields.
3. **Create a `meta.yaml`** under `conda/conda-recipes/<package>/` (use an existing recipe as a template).
4. **Create a release log** under `conda/conda-releaselogs/<package>.md`.
5. For bundles, ensure each member package has `[tool.azure-sdk-conda]` in its `pyproject.toml` with the bundle name:

   ```toml
   [tool.azure-sdk-conda]
   in_bundle = true
   bundle_name = "azure-storage"  # The name of the conda bundle this package belongs to
   ```
