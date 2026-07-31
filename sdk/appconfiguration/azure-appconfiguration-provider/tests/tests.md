# Azure App Configuration Python Provider tests

(This content is for `azure-appconfiguration-provider` package developer only)

The tests for this package are under the `tests/` directory and are split into two categories:

* **Unit tests** (e.g. `tests/test_azureappconfigurationproviderbase.py`, `tests/test_configuration_client_manager.py`) — exercise internal logic in isolation using mocked clients. These do not require any App Configuration store, network access, or environment variables, and can be run at any time with no setup.
* **Integration tests** (e.g. `tests/test_provider.py`, `tests/test_provider_enhanced_feature_flags.py`, and their `tests/aio/` async equivalents) — exercise the provider end-to-end against an Azure App Configuration store. These tests are built on [`devtools_testutils`](https://github.com/Azure/azure-sdk-for-python/tree/main/eng/tools/azure-sdk-tools/devtools_testutils) and each test method is decorated with `@recorded_by_proxy` / `@recorded_by_proxy_async`, which route the test's HTTP traffic through the [test proxy](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy) tool.

## Live tests vs. recorded (playback) tests

Whether an integration test makes a real network call or replays a recording is controlled entirely by the `AZURE_TEST_RUN_LIVE` environment variable, not by anything in this package's code:

* `AZURE_TEST_RUN_LIVE=true` — Tests run in **live/record mode**. The test proxy forwards requests to the real endpoint configured via your environment variables (see below), and (unless `AZURE_SKIP_LIVE_RECORDING=true` is also set) records the request/response pairs as new recording files for use in future playback runs.
* `AZURE_TEST_RUN_LIVE` unset or `false` (the default, and what CI uses) — Tests run in **playback mode**. The test proxy replays the existing recordings instead of contacting the real service, so **no network calls are made** and no live App Configuration store is required.

Recordings themselves are not stored directly in this repository — they live in the separate [`Azure/azure-sdk-assets`](https://github.com/Azure/azure-sdk-assets) repo, and this package's `assets.json` file pins the exact recordings revision (`Tag`) that CI uses. If you add or change integration tests, you need to generate new recordings and publish them:

1. Run the affected tests with `AZURE_TEST_RUN_LIVE=true` (and without `AZURE_SKIP_LIVE_RECORDING`) so the test proxy records real interactions to local recording files.
2. From the repo root, push the new/updated recordings to the assets repo:

   ```bash
   dotnet tool run test-proxy push -a sdk/appconfiguration/azure-appconfiguration-provider/assets.json
   ```

   This uploads the changed recordings and updates the `Tag` field in `assets.json`.
3. Commit the updated `assets.json` as part of your PR — this is what allows CI (which always runs in playback mode) to pick up the new recordings.

Only re-record tests you added or intentionally changed; unrelated existing recordings don't need to be regenerated.

## Environment variables for local testing

To run the integration tests locally in live mode, create a `.env` file at the repository root (it is automatically loaded by `devtools_testutils`) with the following variables:

```
AZURE_TEST_RUN_LIVE=true
APPCONFIGURATION_CONNECTION_STRING=<connection string of your App Configuration store, if you have one> 
APPCONFIGURATION_ENDPOINT_STRING=<endpoint of your App Configuration store, e.g. https://<your-store>.azconfig.io>
APPCONFIGURATION_KEY_VAULT_REFERENCE=<a Key Vault secret URI used by Key Vault reference tests>
APPCONFIGURATION_KEY_VAULT_REFERENCE2=<a second Key Vault secret URI used by Key Vault reference tests>
APPCONFIGURATION_KEYVAULT_SECRET_URL=<a Key Vault secret URI used by Key Vault reference tests>
APPCONFIGURATION_KEYVAULT_SECRET_URL2=<a second Key Vault secret URI used by Key Vault reference tests>
```

Notes:

* For key vault URI, you can create a secret in Azure Key Vault service. The key vault URI is the *Secret Identifier*, without the final version number. For example, if the secret identifier is `https://some_secret.vault.azure.net/secrets/fake-secret/30d8830ec5ed4a428d311292a826f452`, the key vault URI should be `https://some_secret.vault.azure.net/secrets/fake-secret/`. 
* Authentication for Entra ID-based tests relies on your local Azure CLI login (`az login`); make sure you're signed in to the subscription that contains your App Configuration store.
* Add `AZURE_SKIP_LIVE_RECORDING=true` if you want to run tests live against the real store without generating/overwriting recording files (useful for a quick sanity check).
* Omit `AZURE_TEST_RUN_LIVE` (or set it to `false`) to run the same tests in playback mode against existing recordings — this does not require any of the App Configuration environment variables above.

## Pre-PR validation checks (sdist, mypy, pylint, black, snippets)

Make sure all unit tests and live tests passed, test recodings updated, all tests against recordings also passed. 

Before opening or updating a PR, run the same static/build checks that CI enforces, using the `azpysdk` entrypoint from `eng/tools/azure-sdk-tools`. See [doc/tool_usage_guide.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md) for the full list of available checks and options (e.g. `--isolate`).

From this package's directory (`sdk/appconfiguration/azure-appconfiguration-provider`):

```bash
azpysdk sdist .           # builds the sdist and runs the full test suite against it
azpysdk mypy .            # static type checking
azpysdk pylint .          # lint checks
azpysdk black .           # formatting check (auto-reformats files in place)
azpysdk update_snippet .  # regenerates README code snippets from sample files
```

Notes:

* Run `black` again after making any other fixes, since it may reformat files you just edited.
* Run `update_snippet` after changing any `samples/*.py` file, then diff to confirm the regenerated snippets in `README.md` match what you expect.
* See [doc/dev/pylint_checking.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md) and [doc/dev/static_type_checking_cheat_sheet.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md) for guidance on fixing pylint/mypy issues.
