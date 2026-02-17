## Technical Reference

This section is for developers who need to understand or modify the conda release infrastructure specified in `conda-release.md`.

### Repository Layout

| Path | Purpose |
|------|---------|
| `conda/conda-recipes/<package>/meta.yaml` | Conda recipe for each package (or bundle). Defines build, dependencies, and tests. |
| `conda/conda-recipes/conda_env.yml` | Stores `AZURESDK_CONDA_VERSION` — the version string used for all conda packages in a release (e.g., `2025.12.01`). |
| `conda/conda-releaselogs/<package>.md` | Per-package release log listing which PyPI package versions are included in each conda release. |
| `conda/update_conda_files.py` | The main automation script. Updates versions, creates recipes, and generates release logs. |
| `conda/conda_helper_functions.py` | Shared helpers for CSV parsing, bundle detection, PyPI queries, etc. |
| `eng/pipelines/conda-update-pipeline.yml` | Pipeline definition for the update/PR workflow. |
| `eng/pipelines/templates/stages/conda-sdk-client.yml` | Pipeline definition for building and releasing conda packages. Contains the `CondaArtifacts` list and per-package release toggles. |
| `eng/pipelines/templates/stages/archetype-conda-release.yml` | Release stage template — uploads `.conda` artifacts to Anaconda. |
| `eng/pipelines/templates/steps/build-conda-artifacts.yml` | Build step template — installs tooling and invokes `sdk_build_conda`. |

### How `update_conda_files.py` Works

The script is the core of the update pipeline. When invoked (with an optional `--release-date MM.DD` argument), it performs these steps in order:

1. **Bumps `AZURESDK_CONDA_VERSION`** in `conda_env.yml` to the target release date (or auto-increments by 3 months).

2. **Parses the package CSV** (via `conda_helper_functions.parse_csv()`) to get the latest GA versions and release dates for all Azure SDK packages.

3. **Categorizes packages** into:
   - **Outdated** — already in conda but with a newer GA version available.
   - **New** — GA packages not yet included in conda.
   - Data plane vs. management plane.

4. **Updates `conda-sdk-client.yml`:**
   - Bumps `version` fields for outdated packages in the `CondaArtifacts` list.
   - Adds new `CondaArtifacts` entries and release toggle parameters for new data plane packages.
   - Appends new management plane packages to the `azure-mgmt` bundle's checkout list.
   - Updates `download_uri` for packages sourced directly from PyPI (e.g., `msal`, `msal-extensions`).

5. **Creates `meta.yaml` recipes** for new data plane packages (under `conda/conda-recipes/<package>/`). For bundled packages (determined by `[tool.azure-sdk-conda]` in `pyproject.toml`), a single recipe covers the entire bundle.

6. **Updates `azure-mgmt/meta.yaml`** import tests for new management plane packages.

7. **Updates/creates release logs** in `conda/conda-releaselogs/`.

8. **Prints a report** of any packages that couldn't be automatically processed and may need manual attention.

### Package Bundles

Some packages are grouped into a single conda package (a "bundle"). For example, `azure-storage` bundles `azure-storage-blob`, `azure-storage-queue`, etc. Bundle membership is determined by the `[tool.azure-sdk-conda]` section in each package's `pyproject.toml`. The `get_bundle_name()` helper reads this configuration.

Bundled packages share:
- A single `meta.yaml` recipe (with combined dependencies and imports).
- A single release log file.
- A single release toggle in `conda-sdk-client.yml`.

### Build Pipeline (`conda-sdk-client.yml`)

The build pipeline is triggered on PR or push to `main` when files under `conda/conda-recipes/`, `conda/conda-releaselogs/`, or the pipeline file itself change.

**Build stage:**
1. Installs `azure-sdk-tools[conda]` which provides the `sdk_build_conda` CLI.
2. Serializes the `CondaArtifacts` parameter list to JSON and passes it to `sdk_build_conda`.
3. For each artifact, the CLI:
   - Downloads source distributions from PyPI.
   - Assembles combined source distributions for bundles.
   - Generates a `meta.yaml` referencing the source distribution.
   - Runs `conda-build` to produce `.conda` packages.
4. Publishes three artifact sets: `distributions` (assembled sources), `conda` (final packages), and `broken` (any failed builds).

**Release stage (`archetype-conda-release.yml`):**
- Only runs on manual builds from the `internal` project.
- Requires deployment approval (environment: `package-publish`).
- Uploads all `.conda` files from the `conda/noarch` artifact to Anaconda using `anaconda-client`, under the `Microsoft` user, with retry logic (up to 3 attempts per package).

### Versioning

All conda packages in a release share the same version string: `YYYY.MM.DD` (e.g., `2025.12.01`). This is set in `conda/conda-recipes/conda_env.yml` and referenced by every `meta.yaml` via `environ.get('AZURESDK_CONDA_VERSION')`.

### Building Locally

See [conda-builds.md](conda-builds.md) for instructions on building conda packages locally using `sdk_build_conda`.

### Adding a New Package to Conda Manually

If the automation doesn't handle a package correctly, you can add it manually:

1. **Add a release toggle** parameter in `conda-sdk-client.yml`.
2. **Add a `CondaArtifacts` entry** with `name`, `service`, `common_root`, `in_batch`, and `checkout` fields.
3. **Create a `meta.yaml`** under `conda/conda-recipes/<package>/` (use an existing recipe as a template).
4. **Create a release log** under `conda/conda-releaselogs/<package>.md`.
5. For bundles, ensure each member package has `[tool.azure-sdk-conda]` in its `pyproject.toml` with the bundle name.
