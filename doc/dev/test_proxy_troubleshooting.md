# Guide for test proxy troubleshooting

This guide details some common errors that can come up when migrating to and using the Azure SDK test proxy.

Documentation of test proxy's underlying functionality can be found [here][detailed_docs] in the `azure-sdk-tools`
GitHub repository, but this isn't necessary to read for Python testing.

## Table of contents

- [Debugging tip](#debugging-tip)
- [ResourceNotFoundError: Playback failure](#resourcenotfounderror-playback-failure)
- [Test collection failure](#test-collection-failure)
- [Errors in tests using resource preparers](#errors-in-tests-using-resource-preparers)
- [Test failure during `record/start` or `playback/start` requests](#test-failure-during-recordstart-or-playbackstart-requests)
- [Playback failures from body matching errors](#playback-failures-from-body-matching-errors)
- [Playback failures from inconsistent line breaks](#playback-failures-from-inconsistent-line-breaks)
- [Playback failures from URL mismatches](#playback-failures-from-url-mismatches)
- [Playback failures from inconsistent test values](#playback-failures-from-inconsistent-test-values)
- [Recordings not being produced](#recordings-not-being-produced)
- [ConnectionError during tests](#connectionerror-during-tests)
- [Different error than expected when using proxy](#different-error-than-expected-when-using-proxy)
- [Test setup failure in test pipeline](#test-setup-failure-in-test-pipeline)
- [Fixture not found error](#fixture-not-found-error)
- [PermissionError during startup](#permissionerror-during-startup)
- [ServiceRequestError: Cannot connect to host](#servicerequesterror-cannot-connect-to-host)

## Debugging tip

To see more detailed output from tests, you can run `pytest` commands with the flags `-s` and `--log-cli-level=DEBUG`.
The former will output print statements and more logging, and the latter will expose `DEBUG`-level logs that are hidden
by default. For example:

```cmd
pytest .\tests\test_client.py -s --log-cli-level=DEBUG
```

Additionally, the `-k` flag can be used to collect and run tests that have a specific name. For example, providing
`-k "test_delete or test_upload"` to the `pytest` command will only collect and execute tests that have method names
containing the strings `test_delete` or `test_upload`.

For more information about `pytest` invocations, refer to [Usage and Invocations][pytest_commands].

## ResourceNotFoundError: Playback failure

Test playback errors typically raise with a message similar to the following:

```text
FAILED test_client.py::TestClient::test_client_method - azure.core.exceptions.ResourceNotFoundError:
Playback failure -- for help resolving, see https://aka.ms/azsdk/python/test-proxy/troubleshoot. Error details:
Unable to find a record for the request POST https://fake_resource.service.azure.net?api-version=2025-09-01
```

This means that the test recording didn't contain a match for the incoming playback request. This usually just means
that the test needs to be re-recorded to pick up library updates (e.g. a new service API version).

If playback errors persist after re-recording, you may need to modify session sanitizers or matchers. The following
sections of this guide describe common scenarios:

- [Playback failures from body matching errors](#playback-failures-from-body-matching-errors)
- [Playback failures from inconsistent line breaks](#playback-failures-from-inconsistent-line-breaks)
- [Playback failures from URL mismatches](#playback-failures-from-url-mismatches)
- [Playback failures from inconsistent test values](#playback-failures-from-inconsistent-test-values)

## Test collection failure

Make sure that all test class names begin with "Test", and that all test method names begin with "test_". For more
information about `pytest` test collection, please refer to the [docs][pytest_collection].

### Special case: using `pytest.mark.parametrize` with recorded tests

[Parametrization][parametrize] allows you to share test code by re-running the same test with varying inputs. For
example, [`azure-keyvault-keys` tests][parametrize_example] are parametrized to run with multiple API versions and
multiple Key Vault configurations.

Because of how the `pytest.mark.parametrize` mechanism works, the `recorded_by_proxy(_async)` decorators aren't
compatible without an additional decorator that handles the arguments we want to parametrize. The callable that
`pytest.mark.parametrize` decorates needs to have positional parameters that match the arguments we're parametrizing;
for example:

```python
import pytest
from devtools_testutils import recorded_by_proxy

test_values = [
    ("first_value_a", "first_value_b"),
    ("second_value_a", "second_value_b"),
]

# Works because `parametrize` decorates a method with positional `a` and `b` parameters
@pytest.mark.parametrize("a, b", test_values)
def test_function(a, b, **kwargs):
    ...

# Doesn't work; raises collection error
# `recorded_by_proxy`'s wrapping function doesn't accept positional `a` and `b` parameters
@pytest.mark.parametrize("a, b", test_values)
@recorded_by_proxy
def test_recorded_function(a, b, **kwargs):
    ...
```

To parametrize recorded tests, we need a decorator between `pytest.mark.parametrize` and `recorded_by_proxy` that
accepts the expected arguments. We can do this by declaring a class with a custom `__call__` method:

```python
class ArgumentPasser:
    def __call__(self, fn):
        # _wrapper accepts the `a` and `b` arguments we want to parametrize with
        def _wrapper(test_class, a, b, **kwargs):
            fn(test_class, a, b, **kwargs)
        return _wrapper

# Works because `ArgumentPasser.__call__`'s return value has the expected parameters
@pytest.mark.parametrize("a, b", test_values)
@ArgumentPasser()
@recorded_by_proxy
def test_recorded_function(a, b, **kwargs):
    ...
```

You can also introduce additional logic into the `__call__` method of your intermediate decorator. In the aforementioned
[`azure-keyvault-keys` test example][parametrize_example], the decorator between `parametrize` and `recorded_by_proxy`
is actually a [client preparer][parametrize_class] that creates a client based on the parametrized input and passes this
client to the test.

## Errors in tests using resource preparers

Test suites that haven't fully migrated to using a `test-resources.json` file for test resource deployment might use
resource preparers, such as
[ResourceGroupPreparer](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py).
Resource preparers need a management client to function, so test classes that use them will need to inherit from
[AzureMgmtRecordedTestCase][mgmt_recorded_test_case] instead of AzureRecordedTestCase.

## Test failure during `record/start` or `playback/start` requests

If tests fail during startup, logs might indicate that POST requests to `record/start` or `playback/start` endpoints
are returning 500 responses. In a stack trace, these errors might be raised [here][record_request_failure] or
[here][playback_request_failure], respectively.

This suggests that the test proxy failed to fetch recordings from the assets repository. This likely comes from a
corrupted `git` configuration in `azure-sdk-for-python/.assets`. To resolve this:

1. Upgrade your local version of `git` to at least 2.30.0
2. Remove the `.assets` directory completely. To do this easily, `cd` into the root of `azure-sdk-for-python` with PowerShell >= 7.0.0 and run

```powershell
Remove-Item -Recurse -Force .\.assets\
```

After running tests again, a new `.assets` directory will be created and tests should run normally.

If the problem persists, try removing both the `.assets` folder and your local test proxy tool. `cd` into the root of
`azure-sdk-for-python` and run the following PowerShell commands:

```powershell
Remove-Item -Recurse -Force .\.assets\
Remove-Item -Recurse -Force .\.proxy\
```

These folders will be freshly recreated the next time you run tests.

## Playback failures from body matching errors

The test proxy system enables body matching by default. For example, if a test sends a request that includes the
current Unix time in its body, the body will contain a new value when run in playback mode at a later time -- this
request won't match the recording if body matching is enabled.

Body matching can be turned off with the test proxy by calling the `set_bodiless_matcher` method from
[devtools_testutils/sanitizers.py][py_sanitizers] at the very start of a test method. This matcher applies only to the
test method that `set_bodiless_matcher` is called from, so other tests in the `pytest` session will still have body
matching enabled by default.

## Playback failures from inconsistent line breaks

Line breaks can vary between OSes and cause tests to fail on certain platforms, in which case it can help to specify a
particular format for test files by using [`.gitattributes`][gitattributes].

A `.gitattributes` file can be placed at the root of a directory to apply git settings to each file under that
directory. If a test directory contains files that need to have consistent line breaks, for example LF breaks instead
of CRLF ones, you can create a `.gitattributes` file in the directory with the following content:

```text
# Force git to checkout text files with LF (line feed) as the ending (vs CRLF)
# This allows us to consistently run tests that depend on the exact contents of a file
* text=auto eol=lf
```

For a real example, refer to https://github.com/Azure/azure-sdk-for-python/pull/29955.

## Playback failures from URL mismatches

URL matching errors in playback tests can come from a variety of issues. This section lists common ones and how to
resolve them.

### Duplicated slash(es) in URLs

This most often appears at the end of the URL domain; for example:

```text
Uri doesn't match:
    request: https://fake_resource.service.azure.net/path
    record:  https://fake_resource.service.azure.net//path
```

This most often comes from an `EnvironmentVariableLoader` playback endpoint ending with a trailing slash (e.g.
`https://fake_resource.service.azure.net/`) while the live-mode URL doesn't (e.g.
`https://fake_resource.service.azure.net`). A slash gets added to the real endpoint during tests, and then the domain
-- without a trailing slash -- is sanitized with a URL that has an additional trailing slash.

Check the real values of endpoints in your `.env` file, and ensure the formatting of corresponding playback endpoint
values match in any sanitizer or `EnvironmentVariableLoader` uses.

### Inconsistent query parameter ordering

By default, the test proxy tries to match URLs exactly. If there's a section of the URL that's indeterminately ordered,
you may intermittently see matching errors. This often happens with query parameters; for example:

```text
Uri doesn't match:
    request: https://fake_resource.service.azure.net/?a=value1&b=value2
    record:  https://fake_resource.service.azure.net/?b=value2&a=value1
```

To match requests for query parameter content instead of exact ordering, you can use the
[`set_custom_default_matcher`][custom_default_matcher] method from `devtools_testutils` with the keyword argument
`ignore_query_ordering=True`. Calling this method inside the body of a test function will update the matcher for only
that test, which is recommended.

### Sanitization impacting request URL/body/headers

In some cases, a value in a response body is used in the following request as part of the URL, body, or headers. If
this value is sanitized, the recorded request might differ than what is expected during playback. Common culprits
include sanitization of "name", "id", and "Location" fields. To resolve this, you can either opt out of specific
sanitization or add another sanitizer to align with the sanitized value.

#### Opt out

You can opt out of sanitization for the fields that are used for your requests by calling the `remove_batch_sanitizer`
method from `devtools_testutils` with the [sanitizer IDs][test_proxy_sanitizers] to exclude. Generally, this is done in
the `conftest.py` file, in the one of the session-scoped fixtures. Example:

```python
from devtools_testutils import remove_batch_sanitizers, test_proxy


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    ...
    #  Remove the following body key sanitizer: AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3493"])
```

Some sanitizer IDs that are often opted out of are:

- `AZSDK2003`: `Location` - Header regex sanitizer
- `AZSDK3430`: `$..id` - Body key sanitizer
- `AZSDK3493`: `$..name` - Body key sanitizer

However, **please be mindful when opting out of a sanitizer, and ensure that no sensitive data is being exposed**.

#### Add another sanitizer

Alternatively, you can add another sanitizer to align the recorded request with the expected request, modifying the URL, body, or headers as needed. Example:

```python
from devtools_testutils import add_uri_regex_sanitizer


add_uri_regex_sanitizer(regex="(?<=https://.+/foo/bar/)(?<id>[^/?\\.]+)", group_for_replace="id", value="Sanitized")
```

## Playback failures from inconsistent test values

To run recorded tests successfully when recorded values are inconsistent or random and can't be sanitized, the test
proxy provides a `variables` API. This makes it possible for a test to record the values of variables that were used
during recording and use the same values in playback mode without a sanitizer.

Note that the recorded variables **must** have string values. For example, trying to record an integer value for a
variable will cause a test proxy error.

For example, imagine that a test uses a randomized `table_uuid` variable when creating resources. The same random value
for `table_uuid` can be used in playback mode by using this `variables` API.

There are two requirements for a test to use recorded variables. First, the test method should accept `**kwargs`.
Second, the test method should `return` a dictionary with any test variables that it wants to record. This dictionary
will be stored in the recording when the test is run live, and will be passed to the test as a `variables` keyword
argument when the test is run in playback.

Below is a code example of how a test method could use recorded variables:

```python
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

class TestExample(AzureRecordedTestCase):

    @recorded_by_proxy
    def test_example(self, **kwargs):
        # In live mode, variables is an empty dictionary
        # In playback mode, the value of variables is {"current_time": "<previously recorded time>"}
        variables = kwargs.pop("variables", {})

        # To fetch variable values, use the `setdefault` method to look for a key ("current_time")
        # and set a real value for that key if it's not present (str(time.time()))
        # Note that time.time() is converted from a float to a string to record it properly
        current_time = variables.setdefault("current_time", str(time.time()))

        ...

        # return the variables at the end of the test to record them
        return variables
```

> **Note:** `variables` will be passed as a named argument to any test that accepts `kwargs` by the test proxy. In
> environments that don't use the test proxy, though -- like live test pipelines -- `variables` won't be provided.
> To avoid a KeyError, providing an empty dictionary as the default value to `kwargs.pop` is recommended.

## Recordings not being produced

Ensure the environment variable `AZURE_SKIP_LIVE_RECORDING` **isn't** set to "true", and that `AZURE_TEST_RUN_LIVE`
**is** set to "true".

## ConnectionError during tests

For example, you may see a `requests.exceptions.ConnectionError` when trying to make service or sanitizer setup
requests. This means that the test proxy tool never started correctly; ensure the `test_proxy` fixture is being invoked
during test startup so that the tool is available during tests.

## Different error than expected when using proxy

Some tests intentionally trigger exceptions in order to validate error behavior. There are a few known cases where
the exception returned will be different when using the test proxy vs. when sending requests to the service directly.

One such instance is in the case of a DNS lookup failure, which can occur when trying to contact a nonexistent
endpoint. [This issue][wrong_exception] describes an instance of this behavior. As described in the issue, the best
way to work around this for the time being is to have tests expect either of two potential errors, to cover both
cases. For example:

```python
with pytest.raises((ServiceRequestError, HttpResponseError)) as exc_info:
    # This request will raise a ServiceRequestError when sent directly
    # When using the test proxy, we get an HttpResponseError instead
    ...  # Request that triggers DNS lookup failure

# Make sure the HttpResponseError is raised for the same reason: DNS lookup failure
if exc_info.type is HttpResponseError:
    response_content = json.loads(exc_info.value.response.content)
    assert "Name does not resolve" in response_content["Message"]
```

## Test setup failure in test pipeline

If the test proxy isn't configured correctly for pipeline tests, you may see each test fail with an error message
of `test setup failure`.

### CI pipelines

To enable using the test proxy in CI, you need to set the parameter `TestProxy: true` in the `ci.yml` file in the
service-level folder. For example, in [sdk/eventgrid/ci.yml][pipelines_ci]:

```diff
extends:
  template: ../../eng/pipelines/templates/stages/archetype-sdk-client.yml
  parameters:
    ServiceDirectory: eventgrid
+   TestProxy: true
    ...
```

### Live test pipelines

For tests to succeed in live test pipelines, make sure environment variables `AZURE_SKIP_LIVE_RECORDING` and
`AZURE_TEST_RUN_LIVE` are set to True in the `tests.yml` file in the service-level folder. For example, in
[sdk/textanalytics/tests.yml][pipelines_live]:

```diff
stages:
  - template: ../../eng/pipelines/templates/stages/archetype-sdk-tests.yml
    parameters:
      ...
      EnvVars:
        ...
+       AZURE_SKIP_LIVE_RECORDING: 'True'
+       AZURE_TEST_RUN_LIVE: 'true'
```

Requests are made directly to the service instead of going through the proxy when live tests are run with recording
skipped, so the `TestProxy` parameter doesn't need to be set in `tests.yml`.

## Fixture not found error

Tests that aren't recorded should omit the `recorded_by_proxy` decorator. However, if these unrecorded tests accept
parameters that are provided by a preparer like the `devtools_testutils` [EnvironmentVariableLoader][env_var_loader],
you may see a test setup error. For example, imagine a test is decorated with a preparer that provides a Key Vault URL
as a `azure_keyvault_url` parameter:

```python
class TestExample(AzureRecordedTestCase):

    @EnvironmentVariableLoader("keyvault", azure_keyvault_url="https://vaultname.vault.azure.net")
    def test_example(self, azure_keyvault_url):
```

The above would work in the old test setup, but with the test proxy, running the test will yield

```text
_______ ERROR at setup of TestExample.test_example _______
...
E  fixture 'azure_keyvault_url' not found
```

This is because `AzureRecordedTestCase` doesn't inherit from `unittest.TestCase`; `pytest` assumes that any named
parameter in a test method is a reference to a fixture unless the test method is wrapped in a particular way. Wrapping
a test with the `recorded_by_proxy` decorator will permit using named parameters, but wrapping with decorators like
[EnvironmentVariableLoader][env_var_loader] alone will not.

## PermissionError during startup

While the test proxy is being invoked during the start of a test run, you may see an error such as

```text
PermissionError: [Errno 13] Permission denied: '.../azure-sdk-for-python/.proxy/Azure.Sdk.Tools.TestProxy'
```

This can mean that the test proxy tool was successfully installed at the location in the error message, but we don't
have sufficient permissions to run it with the tool startup script. We can set the correct permissions on the file by
using `chmod`. (This is done automatically during tool setup, but could conceivably fail.) Using the tool path that was
provided in the `PermissionError` message, run the following command:

```text
chmod +x .../azure-sdk-for-python/.proxy/Azure.Sdk.Tools.TestProxy
```

Alternatively, you can delete the installed tool and re-run your tests to automatically reinstall it correctly.

- Open Task Manager, search for a process named "Azure.Sdk.Tools.TestProxy", and end the task if one is running.
- Delete the `.proxy` folder at the root of your local `azure-sdk-for-python` clone.
- Re-run your tests; the test proxy will be reinstalled and should correctly set file permissions.

## ServiceRequestError: Cannot connect to host

When [using HTTPS][proxy_https] via `PROXY_URL='https://localhost:5001'`, tests may fail during startup with the
following exception:

```text
azure.core.exceptions.ServiceRequestError: Cannot connect to host localhost:5001
ssl:True [SSLCertVerificationError: (1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate
verify failed: self signed certificate (_ssl.c:1123)')]
```

This is caused by the test proxy's certificate being incorrectly configured. First, update your branch to include the
latest changes from `main` -- this ensures you have the latest certificate version (it needs to be occasionally
rotated).

If tests continue to fail, this is likely due to an async-specific environment issue. The certificate is
[automatically configured][cert_setup] during proxy startup, but async environments can still nondeterministically fail.

To work around this, unset the `PROXY_URL` environment variable to default to HTTP, which doesn't require a certificate.
If your tests require an HTTPS endpoint, reach out to the Azure SDK team for assistance.

<!-- Links -->

[cert_setup]: https://github.com/Azure/azure-sdk-for-python/blob/9958caf6269247f940c697a3f982bbbf0a47a19b/eng/tools/azure-sdk-tools/devtools_testutils/proxy_startup.py#L210
[custom_default_matcher]: https://github.com/Azure/azure-sdk-for-python/blob/9958caf6269247f940c697a3f982bbbf0a47a19b/eng/tools/azure-sdk-tools/devtools_testutils/sanitizers.py#L90
[detailed_docs]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md
[env_var_loader]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py
[gitattributes]: https://git-scm.com/docs/gitattributes
[mgmt_recorded_test_case]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/tools/azure-sdk-tools/devtools_testutils/mgmt_recorded_testcase.py
[parametrize]: https://docs.pytest.org/latest/example/parametrize.html
[parametrize_class]: https://github.com/Azure/azure-sdk-for-python/blob/aa607b3b8c3e646928375ebcc6339d68e4e90a49/sdk/keyvault/azure-keyvault-keys/tests/_test_case.py#L61
[parametrize_example]: https://github.com/Azure/azure-sdk-for-python/blob/aa607b3b8c3e646928375ebcc6339d68e4e90a49/sdk/keyvault/azure-keyvault-keys/tests/test_key_client.py#L190
[pipelines_ci]: https://github.com/Azure/azure-sdk-for-python/blob/5ba894966ed6b0e1ee8d854871f8c2da36a73d79/sdk/eventgrid/ci.yml#L30
[pipelines_live]: https://github.com/Azure/azure-sdk-for-python/blob/e2b5852deaef04752c1323d2ab0958f83b98858f/sdk/textanalytics/tests.yml#L26-L27
[playback_request_failure]: https://github.com/Azure/azure-sdk-for-python/blob/9958caf6269247f940c697a3f982bbbf0a47a19b/eng/tools/azure-sdk-tools/devtools_testutils/proxy_testcase.py#L102
[proxy_https]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests-advanced.md#use-https-test-proxy-endpoint
[py_sanitizers]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/tools/azure-sdk-tools/devtools_testutils/sanitizers.py
[pytest_collection]: https://docs.pytest.org/latest/goodpractices.html#test-discovery
[pytest_commands]: https://docs.pytest.org/latest/usage.html
[record_request_failure]: https://github.com/Azure/azure-sdk-for-python/blob/9958caf6269247f940c697a3f982bbbf0a47a19b/eng/tools/azure-sdk-tools/devtools_testutils/proxy_testcase.py#L91
[test_proxy_sanitizers]: https://github.com/Azure/azure-sdk-tools/blob/57382d5dc00b10a2f9cfd597293eeee0c2dbd8fd/tools/test-proxy/Azure.Sdk.Tools.TestProxy/Common/SanitizerDictionary.cs#L65
[wrong_exception]: https://github.com/Azure/azure-sdk-tools/issues/2907
