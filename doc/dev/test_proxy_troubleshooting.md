# Guide for test proxy troubleshooting

This guide details some common errors that can come up when migrating to and using the Azure SDK test proxy. For more
information about migrating existing tests to the test proxy, please refer to the
[test proxy migration guide][migration_guide].

Documentation of test proxy's underlying functionality can be found [here][detailed_docs] in the `azure-sdk-tools`
GitHub repository, but this isn't necessary to read for Python testing.

## Table of contents
- [Guide for test proxy troubleshooting](#guide-for-test-proxy-troubleshooting)
    - [Table of contents](#table-of-contents)
    - [Debugging tip](#debugging-tip)
    - [Test collection failure](#test-collection-failure)
    - [Errors in tests using resource preparers](#errors-in-tests-using-resource-preparers)
    - [Test failure during `record/start` or `playback/start` requests](#test-failure-during-recordstart-or-playbackstart-requests)
    - [Playback failures from body matching errors](#playback-failures-from-body-matching-errors)
    - [Playback failures from inconsistent line breaks](#playback-failures-from-inconsistent-line-breaks)
    - [Playback failures from URL mismatches](#playback-failures-from-url-mismatches)
    - [Recordings not being produced](#recordings-not-being-produced)
    - [ConnectionError during tests](#connectionerror-during-tests)
    - [Different error than expected when using proxy](#different-error-than-expected-when-using-proxy)
    - [Test setup failure in test pipeline](#test-setup-failure-in-test-pipeline)
    - [Fixture not found error](#fixture-not-found-error)
    - [PermissionError during startup](#permissionerror-during-startup)

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

## Test collection failure

Because tests are now using pure `pytest` conventions without `unittest.TestCase` components, discovering tests with
`pytest` is a bit more strict. Make sure that all test class names begin with "Test", and that all test method names
begin with "test_". For more information about `pytest` test collection, please refer to the [docs][pytest_collection].

## Errors in tests using resource preparers

Test suites that haven't fully migrated to using a `test-resources.json` file for test resource deployment might use
resource preparers, such as
[ResourceGroupPreparer](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py).
Resource preparers need a management client to function, so test classes that use them will need to inherit from
[AzureMgmtRecordedTestCase][mgmt_recorded_test_case] instead of AzureRecordedTestCase.

## Test failure during `record/start` or `playback/start` requests

If your library uses out-of-repo recordings and tests fail during startup, logs might indicate that POST requests to
`record/start` or `playback/start` endpoints are returning 500 responses. In a stack trace, these errors might be raised
[here][record_request_failure] or [here][playback_request_failure], respectively.

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

In the old, `vcrpy`-based testing system, request and response bodies weren't compared in playback mode by default in
most packages. The test proxy system enables body matching by default, which can introduce failures for tests that
passed in the old system. For example, if a test sends a request that includes the current Unix time in its body, the
body will contain a new value when run in playback mode at a later time. This request might still match the recording if
body matching is disabled, but not if it's enabled.

Body matching can be turned off with the test proxy by calling the `set_bodiless_matcher` method from
[devtools_testutils/sanitizers.py][py_sanitizers] at the very start of a test method. This matcher applies only to the
test method that `set_bodiless_matcher` is called from, so other tests in the `pytest` session will still have body
matching enabled by default.

## Playback failures from inconsistent line breaks

Some tests require recording content to completely match, including line breaks (for example, when sending the content of
a test file in a request body). Line breaks can vary between OSes and cause tests to fail on certain platforms, in which
case it can help to specify a particular format for test files by using [`.gitattributes`][gitattributes].

A `.gitattributes` file can be placed at the root of a directory to apply git settings to each file under that directory.
If a test directory contains files that need to have consistent line breaks, for example LF breaks instead of CRLF ones,
you can create a `.gitattributes` file in the directory with the following content:
```
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

In some cases, a value in a response body is used in the following request as part of the URL, body, or headers. If this value is sanitized, the recorded request might differ than what is expected during playback. Common culprits include sanitization of "name", "id", and "Location" fields. To resolve this, you can either opt out of specific sanitization or add another sanitizer to align with the sanitized value.

#### Opt out

You can opt out of sanitization for the fields that are used for your requests by calling the `remove_batch_sanitizer` method from `devtools_testutils` with the [sanitizer IDs][test_proxy_sanitizers] to exclude. Generally, this is done in the `conftest.py` file, in the one of the session-scoped fixtures. Example:

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
of `test setup failure`. To resolve this, follow the instructions in the
[Enable the test proxy in pipelines][proxy_pipelines] section of the [migration guide][migration_guide]. The test
proxy should be enabled for playback test pipelines and disabled for live test pipelines, since recordings are only
involved in the former scenario.

## Fixture not found error

Tests that aren't recorded should omit the `recorded_by_proxy` decorator. However, if these unrecorded tests accept
parameters that are provided by a preparer like the `devtools_testutils` [EnvironmentVariableLoader][env_var_loader],
you may see a new test setup error after migrating to the test proxy. For example, imagine a test is decorated with a
preparer that provides a Key Vault URL as a `azure_keyvault_url` parameter:

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

As noted in the [Fetch environment variables][env_var_section] section of the [migration guide][migration_guide],
reading expected variables from an accepted `**kwargs` parameter is recommended instead so that tests will run as
expected in either case.

## PermissionError during startup

While the test proxy is being invoked during the start of a test run, you may see an error such as
```
PermissionError: [Errno 13] Permission denied: '.../azure-sdk-for-python/.proxy/Azure.Sdk.Tools.TestProxy'
```

This can mean that the test proxy tool was successfully installed at the location in the error message, but we don't have
sufficient permissions to run it with the tool startup script. We can set the correct permissions on the file by using
`chmod`. Using the tool path that was provided in the `PermissionError` message, run the following command:
```
chmod +x .../azure-sdk-for-python/.proxy/Azure.Sdk.Tools.TestProxy
```

Alternatively, you can delete the installed tool and re-run your tests to automatically reinstall it correctly.

- Open Task Manager, search for a process named "Azure.Sdk.Tools.TestProxy", and end the task if one is running.
- Delete the `.proxy` folder at the root of your local `azure-sdk-for-python` clone.
- Re-run your tests; the test proxy will be reinstalled and should correctly set file permissions.


[custom_default_matcher]: https://github.com/Azure/azure-sdk-for-python/blob/497f5f3435162c4f2086d1429fc1bba4f31a4354/tools/azure-sdk-tools/devtools_testutils/sanitizers.py#L85
[detailed_docs]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md
[env_var_loader]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py
[env_var_section]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md#fetch-environment-variables
[gitattributes]: https://git-scm.com/docs/gitattributes
[mgmt_recorded_test_case]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/mgmt_recorded_testcase.py
[migration_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
[playback_request_failure]: https://github.com/Azure/azure-sdk-for-python/blob/e23d9a6b1edcc1127ded40b9993029495b4ad08c/tools/azure-sdk-tools/devtools_testutils/proxy_testcase.py#L108
[proxy_pipelines]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md#enable-the-test-proxy-in-pipelines
[proxy_startup]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/proxy_startup.py
[py_sanitizers]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/sanitizers.py
[pytest_collection]: https://docs.pytest.org/latest/goodpractices.html#test-discovery
[pytest_commands]: https://docs.pytest.org/latest/usage.html
[record_request_failure]: https://github.com/Azure/azure-sdk-for-python/blob/e23d9a6b1edcc1127ded40b9993029495b4ad08c/tools/azure-sdk-tools/devtools_testutils/proxy_testcase.py#L97
[test_proxy_sanitizers]: https://github.com/Azure/azure-sdk-tools/blob/57382d5dc00b10a2f9cfd597293eeee0c2dbd8fd/tools/test-proxy/Azure.Sdk.Tools.TestProxy/Common/SanitizerDictionary.cs#L65
[wrong_exception]: https://github.com/Azure/azure-sdk-tools/issues/2907
