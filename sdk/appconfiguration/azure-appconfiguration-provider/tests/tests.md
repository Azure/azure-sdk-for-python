# Azure App Configuration Python Provider tests

(This content is for `azure-appconfiguration-provider` package developers only)

For general repo-wide testing setup and concepts (environment setup, the test proxy, live vs. playback
mode, recordings, sanitizers), see [doc/dev/tests.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md).
This page only covers what's specific to this package, plus a checklist of what to run — and in what
order — before opening a PR.

## Running tests locally (Windows)

Use a single virtual environment for the whole repo, created at the **repo root** (`azure-sdk-for-python/.venv`)
per [doc/dev/tests.md § Set up your development environment](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#set-up-your-development-environment):

```powershell
# From the repo root
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Then install this package's `dev_requirements.txt` from *this* package directory, since it contains paths
relative to it (e.g. `../azure-appconfiguration`), and install this package itself as an editable install:

```powershell
# From sdk/appconfiguration/azure-appconfiguration-provider
..\..\..\.venv\Scripts\python.exe -m pip install -r dev_requirements.txt
..\..\..\.venv\Scripts\python.exe -m pip install -e .
```

Run tests from this package directory:

```powershell
..\..\..\.venv\Scripts\python.exe -P -m pytest tests
```

Run a single file or test the same way, e.g.:

```powershell
..\..\..\.venv\Scripts\python.exe -P -m pytest tests\aio\test_async_provider_refresh.py
```

## Environment variables for local integration testing

To run the integration tests (those using `@recorded_by_proxy` / `@recorded_by_proxy_async`) locally in live mode (interacting with app config store through network call), create a `.env` file at the repository root with the following content:

```
AZURE_TEST_RUN_LIVE=true
APPCONFIGURATION_ENDPOINT_STRING=<endpoint of your App Configuration store, e.g. https://<your-store>.azconfig.io>
APPCONFIGURATION_KEY_VAULT_REFERENCE=<a Key Vault secret URI used to seed Key Vault reference settings in the test store during session setup>
APPCONFIGURATION_KEY_VAULT_REFERENCE2=<a second Key Vault secret URI used to seed Key Vault reference settings in the test store during session setup>
APPCONFIGURATION_KEYVAULT_SECRET_URL=<a Key Vault secret URI passed directly into Key Vault reference/secret resolution tests>
APPCONFIGURATION_KEYVAULT_SECRET_URL2=<a second Key Vault secret URI passed directly into Key Vault reference/secret resolution tests>
```

* `APPCONFIGURATION_KEY_VAULT_REFERENCE` and `APPCONFIGURATION_KEYVAULT_SECRET_URL` can be the same value. `APPCONFIGURATION_KEY_VAULT_REFERENCE2` and `APPCONFIGURATION_KEYVAULT_SECRET_URL2` can be the same value. They are referencing the `Secret Identifier`.
* See [Microsoft Learn: Set and retrieve a secret from Azure Key Vault using the Azure portal](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-portal) for how to create a secret.

With `AZURE_TEST_RUN_LIVE=true` set in your `.env` file, run the integration test(s) live the same way as any
other test:

```powershell
..\..\..\.venv\Scripts\python.exe -P -m pytest tests\test_provider.py
```

See [doc/dev/tests.md § Configure live or playback testing mode](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#configure-live-or-playback-testing-mode)
and [§ Run and record tests](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#run-and-record-tests)
for how live/record/playback modes work generally.

## Before opening a PR: what to run, and in what order

1. **Run the full test suite**
   ```powershell
   ..\..\..\.venv\Scripts\python.exe -P -m pytest tests
   ```
   These should always pass.
2. **If your change adds or modifies integration tests** (those using `@recorded_by_proxy` / `@recorded_by_proxy_async`), run just those test file(s)/method(s) live
   (`AZURE_TEST_RUN_LIVE=true`) so the test proxy records real interactions
   to local recording files.
3. **Run the same integration tests again in playback mode** (unset `AZURE_TEST_RUN_LIVE`) to confirm the
   new recordings replay correctly — do this *before* pushing recordings, since it catches
   recording/sanitization issues early.
4. **Push the new/updated recordings** and commit the updated `assets.json`:
   ```bash
   python scripts/manage_recordings.py push -p sdk/appconfiguration/azure-appconfiguration-provider/assets.json
   ```
   Only re-record and push tests you added or intentionally changed. See
   [doc/dev/tests.md § Update test recordings](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#update-test-recordings)
   for background on the assets repo/`assets.json` mechanism.
5. **Run the pre-PR static/build checks**, from this package's directory:
   ```bash
   azpysdk sdist .           # builds the sdist and runs the full test suite against it
   azpysdk mypy .            # static type checking
   azpysdk pylint .          # lint checks
   azpysdk black .           # formatting check (auto-reformats files in place; re-run after other fixes)
   azpysdk update_snippet .  # regenerates README code snippets; run after changing any samples/*.py file
   ```
   See [doc/tool_usage_guide.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md)
   for the full list of `azpysdk` checks, and [doc/dev/pylint_checking.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
   / [doc/dev/static_type_checking_cheat_sheet.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
   for fixing pylint/mypy issues.

If your change only touches unit tests (no integration test changes), skip straight to steps 1 and 5.
