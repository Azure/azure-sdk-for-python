# Devtools Testutils

## Objects in this package for use with Azure Testing

* [`AzureMgmtPreparer`][azure_mgmt_preparer]: Base class for Management-plane resource preparers
* [`is_live`][is_live]: Helper method for determining whether a test run is in live or playback mode
* [`get_region_override`][get_region_override]: Helper method for determining resource region
* [`EnvironmentVariableLoader`][env_loader]: Preparer for sanitizing secrets from environment variables and delivering them to individual tests
* [`RetryCounter`][retry_counter]: Object for counting retries on a request.
* [`ResponseCallback`][response_callback]: Object for mocking response callbacks.
* [`FakeCredential`][fake_credentials]: Fake credential used for authenticating in playback mode.
* [`AsyncFakeCredential`][fake_credentials_async]: Fake async credential used for authenticating in playback mode.

## Fake test credentials

`devtools_testutils` also provides a central location for storing and fetching fake credentials for use in tests:
[`fake_credentials.py`][fake_credentials]. Using credentials from this file helps us keep the repository free from
credential leaks and false warnings from the [Credential Scanner (CredScan)][credscan] tool. For more information about
the `azure-sdk-for-python`'s use of CredScan, please refer to the [CredScan monitoring guide][credscan_guide].

## Use the `EnvironmentVariableLoader`

Fetching environment variables, passing them directly to tests, and sanitizing their real values can be done all at once
by using the `devtools_testutils` [`EnvironmentVariableLoader`][env_loader] (formerly known as the
`PowerShellPreparer`).

This loader is meant to be paired with the PowerShell test resource management commands that are documented in
[/eng/common/TestResources][test_resources]. It's recommended that all test suites use these scripts for live test
resource management.

The `EnvironmentVariableLoader` accepts a positional `directory` argument and arbitrary keyword-only arguments:

* `directory` is the name of your package's service as it appears in the Python repository; i.e. `service` in `azure-sdk-for-python/sdk/service/azure-service-package`.
  * For example, for `azure-keyvault-keys`, the value of `directory` is `keyvault`.
* For each environment variable you want to provide to tests, pass in a keyword argument with the pattern `environment_variable_name="sanitized-value"`.
  * For example, to fetch the value of `STORAGE_ENDPOINT` and sanitize this value in recordings as `fake-endpoint`, provide `storage_endpoint="fake-endpoint"` to the `EnvironmentVariableLoader` constructor.

Additionally, the loader accepts an `EnvironmentVariableOptions` object via the `options` kwarg. This should be used
whenever fetching sensitive environment variables like connection strings or account keys. See
[Hide secret environment variables in test logs](#hide-secret-environment-variables-in-test-logs) for details and usage
examples.

Decorated test methods will have the values of environment variables passed to them as keyword arguments, and these
values will automatically have sanitizers registered with the test proxy. More specifically, the true values of
requested variables will be provided to tests in live mode, and the sanitized values of these variables will be provided
in playback mode.

The most common way to use the `EnvironmentVariableLoader` is to declare a callable specifying arguments by using
`functools.partial` and then decorate test methods with that callable. For example:

```python
import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

ServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "service",
    service_endpoint="fake-endpoint",
    service_account_name="fake-account-name",
)

class TestExample(AzureRecordedTestCase):

    @ServicePreparer()
    @recorded_by_proxy
    def test_example_with_preparer(self, **kwargs):
        service_endpoint = kwargs.pop("service_endpoint")
        ...
```

**Be sure to match the formatting of live values in playback values.** For example, if the actual service endpoint in
your `.env` file doesn't end with a trailing slash (`/`), adding a trailing slash to your playback endpoint value will
result in playback errors. The exact value of your live variables will be replaced with the exact value of your playback
variables in recordings.

> **Note:** The `EnvironmentVariableLoader` expects environment variables for service tests to be prefixed with the
> service name (e.g. `KEYVAULT_` for Key Vault tests). You'll need to set environment variables for
> `{SERVICE}_TENANT_ID`, `{SERVICE}_CLIENT_ID`, and `{SERVICE}_CLIENT_SECRET` for a service principal when using this
> class.

### Hide secret environment variables in test logs

Pytest will log local test variables, including test method parameters, whenever a test fails. This can lead to secret
leak warnings in pipelines even if test resources are transient or mocked. To avoid leaks, you should shield sensitive
variables with the `options` keyword argument.

`options` accepts an [EnvironmentVariableOptions][options] instance, with which you can provide a case insensitive list
of environment variables that should be hidden in tests. [For example:][options_use]

```python
DataLakePreparer = functools.partial(
    EnvironmentVariableLoader, "storage",
    datalake_storage_account_name="storagename",
    datalake_storage_account_key=STORAGE_ACCOUNT_FAKE_KEY,
    storage_data_lake_soft_delete_account_name="storagesoftdelname",
    storage_data_lake_soft_delete_account_key=STORAGE_ACCOUNT_FAKE_KEY,
    options=EnvironmentVariableOptions(
        hide_secrets=["datalake_storage_account_key", "storage_data_lake_soft_delete_account_key"]
    ),
)
```

The loader will raise an error if a variable specified in `hide_secrets` doesn't match any of the variables requested
for loading.

Hidden variables will be passed to tests as an [EnvironmentVariable][environmentvariable] instance instead of a plain
string; the variable's value should be fetched with the `.secret` string attribute. **It's important to avoid assigning
the secret to a local variable.** As mentioned in the start of this section, Pytest logs the values of local variables
upon test failure. Instead, `<variable>.secret` should be accessed only when the value is used; e.g.
[when providing the secret to a credential constructor][environmentvariable_use].

```python
class TestDatalakeCpk(StorageRecordedTestCase):
    def _setup(self, account_name: str, account_key: EnvironmentVariable):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=account_key.secret)
        ...

    # Note that DataLakePreparer passes account name as a plain string, but hides account key in an EnvironmentVariable
    @DataLakePreparer()
    @recorded_by_proxy
    def test_create_directory_cpk(
        self, datalake_storage_account_name: str, datalake_storage_account_key: EnvironmentVariable
    ):
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        ...
```

<!-- LINKS -->
[azure_mgmt_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/4df650d2ce4c292942009ed648cae21eb9c2121d/eng/tools/azure-sdk-tools/devtools_testutils/mgmt_testcase.py#L42
[credscan]: https://aka.ms/credscan
[credscan_guide]: https://github.com/Azure/azure-sdk-for-python/blob/18611efee7ecf4e591d59b61ba3762d6bdd86304/doc/dev/credscan_process.md
[env_loader]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py
[environmentvariable]: https://github.com/Azure/azure-sdk-for-python/blob/b6b227edbe318ee79a6a987d063e9823608f3c0a/eng/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py#L209
[environmentvariable_use]: https://github.com/Azure/azure-sdk-for-python/blob/b6b227edbe318ee79a6a987d063e9823608f3c0a/sdk/storage/azure-storage-file-datalake/tests/test_cpk.py#L27
[fake_credentials]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/tools/azure-sdk-tools/devtools_testutils/fake_credentials.py
[fake_credentials_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/tools/azure-sdk-tools/devtools_testutils/fake_credentials_async.py
[get_region_override]: https://github.com/Azure/azure-sdk-for-python/blob/4df650d2ce4c292942009ed648cae21eb9c2121d/eng/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L52
[is_live]: https://github.com/Azure/azure-sdk-for-python/blob/4df650d2ce4c292942009ed648cae21eb9c2121d/eng/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L42
[options]: https://github.com/Azure/azure-sdk-for-python/blob/b6b227edbe318ee79a6a987d063e9823608f3c0a/eng/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py#L20
[options_use]: https://github.com/Azure/azure-sdk-for-python/blob/b6b227edbe318ee79a6a987d063e9823608f3c0a/sdk/storage/azure-storage-file-datalake/tests/settings/testcase.py#L45
[retry_counter]: https://github.com/Azure/azure-sdk-for-python/blob/4df650d2ce4c292942009ed648cae21eb9c2121d/eng/tools/azure-sdk-tools/devtools_testutils/helpers.py#L119
[response_callback]: https://github.com/Azure/azure-sdk-for-python/blob/4df650d2ce4c292942009ed648cae21eb9c2121d/eng/tools/azure-sdk-tools/devtools_testutils/helpers.py#L127
[test_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/TestResources#readme
