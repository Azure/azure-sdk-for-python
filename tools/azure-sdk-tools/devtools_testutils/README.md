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
- `directory` is the name of your package's service as it appears in the Python repository; i.e. `service` in `azure-sdk-for-python/sdk/service/azure-service-package`.
  - For example, for `azure-keyvault-keys`, the value of `directory` is `keyvault`.
- For each environment variable you want to provide to tests, pass in a keyword argument with the pattern `environment_variable_name="sanitized-value"`.
  - For example, to fetch the value of `STORAGE_ENDPOINT` and sanitize this value in recordings as `fake-endpoint`, provide `storage_endpoint="fake-endpoint"` to the `EnvironmentVariableLoader` constructor.

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


<!-- LINKS -->
[azure_mgmt_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/mgmt_testcase.py#L128
[credscan]: https://aka.ms/credscan
[credscan_guide]: https://github.com/Azure/azure-sdk-for-python/blob/18611efee7ecf4e591d59b61ba3762d6bdd86304/doc/dev/credscan_process.md
[env_loader]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py
[fake_credentials]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/fake_credentials.py
[fake_credentials_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/fake_credentials_async.py
[get_region_override]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L87
[is_live]: https://github.com/Azure/azure-sdk-for-python/blob/520ea7175e10a971eae9d3e6cd0735efd80447b1/tools/azure-sdk-tools/devtools_testutils/azure_testcase.py#L77
[retry_counter]: https://github.com/Azure/azure-sdk-for-python/blob/ab7e7f1a7b2a6d7255abdc77a40e2d6a86c9de0a/tools/azure-sdk-tools/devtools_testutils/helpers.py#L6
[response_callback]: https://github.com/Azure/azure-sdk-for-python/blob/ab7e7f1a7b2a6d7255abdc77a40e2d6a86c9de0a/tools/azure-sdk-tools/devtools_testutils/helpers.py#L14
[test_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/TestResources#readme
