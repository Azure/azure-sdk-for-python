---
name: local-dev-environment
description: Describes the local development environment for THIS repo (azure-sdk-for-python) — the repo-scoped Python virtual environment at .venv and the environment variables defined in .env. USE WHEN: you need to run azpysdk/pylint/mypy/pytest/black/sphinx, activate the virtual environment, locate the Python interpreter, or reference local test/auth environment variables for the appconfiguration packages. Scoped to this repository only; other repos have their own .venv.
---

# Local Development Environment (azure-sdk-for-python)

This skill documents the local dev environment that lives in **this** workspace so you
don't need to be told about it each time. It is repo-scoped — this `.venv` and `.env`
belong only to `c:\Users\mametcal\Projects\SDKs\azure-sdk-for-python`.

## Virtual Environment (`.venv`)

- **Location:** `.venv/` at the repo root.
- **Python version:** 3.14.3 (base interpreter: `C:\Users\mametcal\AppData\Local\Programs\Python\Python314`).
- **Interpreter path:** `.venv\Scripts\python.exe`
- **Activate (PowerShell):** `.\.venv\Scripts\Activate.ps1`
- **Activate (cmd):** `.\.venv\Scripts\activate.bat`

### Key tools already installed on PATH (in `.venv\Scripts`)
- `azpysdk.exe` — primary test/validation runner (e.g. `azpysdk pylint .`, `azpysdk mypy .`, `azpysdk black .`)
- `pylint.exe`, `mypy.exe` / `dmypy.exe`, `black.exe`, `pytest.exe`, `sphinx-build.exe`, `isort.exe`
- SDK engineering tools: `sdk_build.exe`, `sdk_changelog.exe`, `sdk_set_version.exe`, `generate_sdk.exe`, `apistubgen.exe`, `dotenv.exe`, and related `sdk_*` / `generate_*` utilities.

### Per-package check environments
`azpysdk` creates isolated per-check virtual environments under `.venv\<package-name>\`.
Currently present:
- `.venv\azure-appconfiguration\` — `.venv_apistub`, `.venv_black`, `.venv_mindependency`, `.venv_mypy`, `.venv_pylint`, `.venv_sphinx`, `.venv_update_snippet`
- `.venv\azure-appconfiguration-provider\`

You normally do not invoke these directly; `azpysdk` manages them.

## Environment Variables (`.env`)

A repo-root `.env` file provides test/auth configuration, primarily for the
**appconfiguration** packages. Load it with `dotenv` or rely on the test harness.

### Active settings
- **Test mode / auth**
  - `AZURE_TEST_RUN_LIVE=true` — tests run in **live** mode (not playback).
  - `AZURE_TEST_USE_CLI_AUTH=true` — authenticate via Azure CLI (`az login`) credentials.
  - `PYLINTRC=./pylintrc`
- **App Configuration endpoints** (staging)
  - `APPCONFIGURATION_ENDPOINT` / `APPCONFIGURATION_ENDPOINT_STRING` → `https://java-sdk-feature-flag-endpoint.appconfig-staging.azure.com`
- **Key Vault references** (placeholder/fake secret URLs under `keyvault-theclassics.vault.azure.net`):
  `APPCONFIGURATION_KEYVAULT_SECRET_URL`, `APPCONFIGURATION_KEYVAULT_SECRET_URL2`,
  `KEYVAULT_URL`, `APPCONFIGURATION_KEY_VAULT_REFERENCE`, `APPCONFIGURATION_KEY_VAULT_REFERENCE2`,
  `KEYVAULT_SECRET_URL`
- **ARM / subscription context**
  - `APPCONFIGURATION_SUBSCRIPTION_ID`, `APPCONFIGURATION_RESOURCE_GROUP=rg-mametcalappconfiguration`
  - `APPCONFIGURATION_LOCATION=eastus`, `APPCONFIGURATION_ENVIRONMENT=AzureCloud`
  - `APPCONFIGURATION_RESOURCE_MANAGER_URL=https://management.azure.com/`
  - `APPCONFIGURATION_SERVICE_MANAGEMENT_URL=https://management.core.windows.net/`
  - `APPCONFIGURATION_AZURE_AUTHORITY_HOST=https://login.microsoftonline.com`
  - `AZURE_SERVICE_DIRECTORY=APPCONFIGURATION`

### Commented-out / alternate profiles (inactive)
The `.env` also keeps several disabled blocks for switching contexts: a Flask sample
endpoint, old test endpoints with connection strings, ARM template deployment values,
and a service-principal auth block for "Bleu Cloud" (`AZURE_TENANT_ID`,
`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_AUTHORITY_HOST`). These are commented
out; uncomment only when intentionally switching environments.

## Notes & cautions
- **Secrets:** `.env` may contain connection strings, secrets, and client secrets. Never
  print, echo, or commit these values. Reference variable names, not their contents.
- The active configuration targets the **App Configuration staging** environment with
  **live** test runs using **Azure CLI** auth — make sure `az login` is current before
  running live tests.
- This environment is specific to this repo; do not assume the same `.venv` path or
  `.env` values apply in other workspaces.
