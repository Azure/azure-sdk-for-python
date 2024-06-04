# Guide for migrating to the test proxy from vcrpy

This guide describes the changes that service SDKs should make to their test frameworks in order to take advantage of
the Azure SDK test proxy.

Documentation of test proxy's underlying functionality can be found [here][detailed_docs] in the `azure-sdk-tools`
GitHub repository, but this isn't necessary to read for Python testing.

Please refer to the [troubleshooting guide][troubleshooting] if you have any issues migrating a package.

## Table of contents
- [Update existing tests](#update-existing-tests)
  - [Using resource preparers](#using-resource-preparers)
- [Run tests](#run-tests)
  - [Start the proxy server](#start-the-proxy-server)
  - [Record or play back tests](#record-or-play-back-tests)
  - [Register sanitizers](#register-sanitizers)
  - [Enable the test proxy in pipelines](#enable-the-test-proxy-in-pipelines)
  - [Fetch environment variables](#fetch-environment-variables)
  - [Record test variables](#record-test-variables)
- [Migrate management-plane tests](#migrate-management-plane-tests)
- [Next steps](#next-steps)
- [Advanced details](#advanced-details)
  - [What does the test proxy do?](#what-does-the-test-proxy-do)
  - [How does the test proxy know when and what to record or play back?](#how-does-the-test-proxy-know-when-and-what-to-record-or-play-back)
  - [Use pytest.mark.parametrize with migrated tests](#use-pytestmarkparametrize-with-migrated-tests)

## Update existing tests

### Current test structure

Test classes currently inherit from AzureTestCase, and test methods can optionally use decorators:

```py
from devtools_testutils import AzureTestCase

class TestExample(AzureTestCase):

    def test_example(self):
        ...

    @ExamplePreparer()
    def test_example_with_preparer(self, example_variable, **kwargs):
        ...
```

### New test structure

To use the proxy, test classes should inherit from AzureRecordedTestCase and recorded test methods should use a
`recorded_by_proxy` decorator directly on top of the test method:

```py
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

class TestExample(AzureRecordedTestCase):

    @recorded_by_proxy
    def test_example(self):
        ...

    @ExamplePreparer()
    @recorded_by_proxy
    def test_example_with_preparer(self, **kwargs):
        example_variable = kwargs.pop("example_variable")
        ...
```

For async tests, import the `recorded_by_proxy_async` decorator from `devtools_testutils.aio` and use it in the same
way as `recorded_by_proxy`.

Because test proxy tests use pure `pytest`, any positional parameter in a test method is assumed to be a reference to
a fixture (see `pytest`'s [How to use fixtures][pytest_using_fixtures] documentation). So, arguments that are passed
to a test by a preparer -- for example, `example_variable` in `test_example_with_preparer` above -- should be
accepted via `**kwargs` and popped off at the start of a test.

> **Note:** since AzureRecordedTestCase doesn't inherit from `unittest.TestCase`, test class names need to start
> with "Test" in order to be properly collected by pytest by default. For more information, please refer to
> [pytest's documentation][pytest_collection].

> **Note:** pure-`pytest` test cases aren't allowed to use an `__init__` constructor. Test classes should instead use
> other methods of persisting state during a test run; for some `pytest` built-in options, please refer to
> [pytest's documentation][pytest_setup].

### Using resource preparers

Test suites that haven't fully migrated to using a `test-resources.json` file for test resource deployment might use
resource preparers, such as [ResourceGroupPreparer][rg_preparer]. Migrating to
[PowerShell test resource deployment][test_resources] is recommended (and test proxy migration might be a good
opportunity to look into this), but the test proxy can work with resource preparers.

Resource preparers need a management client to function, so test classes that use them will need to inherit from
[AzureMgmtRecordedTestCase][mgmt_recorded_test_case] instead of AzureRecordedTestCase.

## Run tests

### Start the proxy server

The test proxy has to be available in order for tests to work in live or playback mode. There's a
[section](#manually-start-the-proxy) under [Advanced details](#advanced-details) that describes how to do this manually,
but it's recommended that tests use a `pytest` fixture to start and stop the proxy automatically when running tests.

In a `conftest.py` file for your package's tests, add a session-level fixture that accepts
`devtools_testutils.test_proxy` as a parameter (and has `autouse` set to `True`):

```python
import pytest
from devtools_testutils import test_proxy

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
```

The `test_proxy` fixture will download a test proxy executable if one isn't available locally, start the tool, and stop
it after tests complete.

If your tests already use an `autouse`d, session-level fixture for tests, you can accept the `test_proxy` parameter in
that existing fixture instead of adding a new one. For an example, see the [Register sanitizers](#register-sanitizers)
section of this document.

In general, if any fixture requires the test proxy to be available by the time it's used, that fixture should accept
this `test_proxy` parameter.

### Record or play back tests

Configuring live and playback tests is done with the `AZURE_TEST_RUN_LIVE` environment variable. When this variable is
set to "true" or "yes", live tests will run and produce recordings unless the `AZURE_SKIP_LIVE_RECORDING` environment
variable is set to "true". When `AZURE_TEST_RUN_LIVE` is set to "false" or "no", or not set at all, tests will run in
playback mode and attempt to match existing recordings.

Recordings for a given package will end up in that package's `/tests/recordings` directory, just like they currently
do. Recordings that use the test proxy are `.json` files instead of `.yml` files, so migrated test suites no longer
need old `.yml` recordings.

After migrating to use the test proxy, libraries can and are encouraged to use out-of-repo recordings. For more
information, refer to the [recording migration guide][recording_migration].

> **Note:** support for configuring live or playback tests with a `testsettings_local.cfg` file has been
> deprecated in favor of using just `AZURE_TEST_RUN_LIVE`.

### Register sanitizers

Since the test proxy doesn't use [`vcrpy`][vcrpy], tests don't use a scrubber to sanitize values in recordings.
Instead, sanitizers (as well as matchers and transforms) can be registered on the proxy as detailed in
[this][sanitizers] section of the proxy documentation. Sanitizers can be registered via `add_*_sanitizer` methods in
`devtools_testutils`. For example, the general-use method for sanitizing recording bodies, headers, and URIs is
`add_general_string_sanitizer`. Other sanitizers are available for more specific scenarios and can be found at
[devtools_testutils/sanitizers.py][py_sanitizers].

Sanitizers, matchers, and transforms remain registered until the proxy tool is stopped, so for any sanitizers that
are shared by different tests, using a session fixture declared in a `conftest.py` file is recommended. Please refer to
[pytest's scoped fixture documentation][pytest_fixtures] for more details.

As a simple example, to emulate the effect registering a name pair with a `vcrpy` scrubber, you can provide the exact
value you want to sanitize from recordings as the `target` in the general string sanitizer. With `vcrpy`, you would
likely do something like the following:

```python
import os
from devtools_testutils import AzureTestCase

class TestExample(AzureTestCase):
    def __init__(self):
        # scrub the value of AZURE_KEYVAULT_NAME with a fake vault name
        self.scrubber.register_name_pair(os.getenv("AZURE_KEYVAULT_NAME"), "fake-vault")
```

To do the same sanitization with the test proxy, you could add something like the following in the package's
`conftest.py` file:

```python
import os
from devtools_testutils import add_general_string_sanitizer, test_proxy

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # The default value for the environment variable should be the value you use in playback
    vault_name = os.getenv("AZURE_KEYVAULT_NAME", "fake-vault")
    add_general_string_sanitizer(target=vault_name, value="fake-vault")
```

Note that the sanitizer fixture accepts the `test_proxy` fixture as a parameter to ensure the proxy is started
beforehand.

For a more advanced scenario, where we want to sanitize the account names of all Tables endpoints in recordings, we
could instead use the `add_general_regex_sanitizer` method:

```python
add_general_regex_sanitizer(
    regex="(?<=\\/\\/)[a-z]+(?=(?:|-secondary)\\.table\\.core\\.windows\\.net)",
    value="fakeendpoint",
)
```

`add_general_regex_sanitizer` accepts a regex, replacement value, and capture group as keyword-only arguments. In the
snippet above, any storage endpoint URIs that match the specified URI regex will have their account name replaced with
"fakeendpoint". A request made to `https://tableaccount-secondary.table.core.windows.net` will be recorded as being
made to `https://fakeendpoint-secondary.table.core.windows.net`, and URIs will also be sanitized in bodies and headers.

For more details about sanitizers and their options, please refer to [devtools_testutils/sanitizers.py][py_sanitizers].

#### Note regarding body matching

In the old, `vcrpy`-based testing system, request and response bodies weren't compared in playback mode by default in
most packages. The test proxy system enables body matching by default, which can introduce failures for tests that
passed in the old system. For example, if a test sends a request that includes the current Unix time in its body, the
body will contain a new value when run in playback mode at a later time. This request might still match the recording if
body matching is disabled, but not if it's enabled.

Body matching can be turned off with the test proxy by calling the `set_bodiless_matcher` method from
[devtools_testutils/sanitizers.py][py_sanitizers] at the very start of a test method. This matcher applies only to the
test method that `set_bodiless_matcher` is called from, so other tests in the `pytest` session will still have body
matching enabled by default.

### Enable the test proxy in pipelines

#### CI pipelines

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

#### Live test pipelines

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

### Fetch environment variables

Refer to the [documentation in `devtools_testutils`][env_var_docs] and use the
[`devtools_testutils.EnvironmentVariableLoader`][env_var_loader] to fetch environment variables and provide them to
tests.

### Record test variables

To run recorded tests successfully when there's an element of non-secret randomness to them, the test proxy provides a
[`variables` API][variables_api]. This makes it possible for a test to record the values of variables that were used
during recording and use the same values in playback mode without a sanitizer.

For example, imagine that a test uses a randomized `table_name` variable when creating resources. The same random value
for `table_name` can be used in playback mode by using this `variables` API.

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
        # In playback mode, the value of variables is {"table_name": "random-value"}
        variables = kwargs.pop("variables", {})
 
        # To fetch variable values, use the `setdefault` method to look for a key ("table_name")
        # and set a real value for that key if it's not present ("random-value")
        table_name = variables.setdefault("table_name", "random-value")

        # use variables["table_name"] when using the table name throughout the test
        ...

        # return the variables at the end of the test to record them
        return variables
```

> **Note:** `variables` will be passed as a named argument to any test that accepts `kwargs` by the test proxy. In
> environments that don't use the test proxy, though -- like live test pipelines -- `variables` won't be provided.
> To avoid a KeyError, providing an empty dictionary as the default value to `kwargs.pop` is recommended.

## Migrate management-plane tests

For management-plane packages, test classes should inherit from [AzureMgmtRecordedTestCase][mgmt_recorded_test_case]
instead of AzureRecordedTestCase.

The rest of the information in this guide applies to management-plane packages as well, except for possible specifics
regarding test resource deployment.

## Next steps

Once your tests have been migrated to the test proxy, they can also have their recordings moved out of the
`azure-sdk-for-python` repo. Refer to the [recording migration guide][recording_migration] for more details.

After recordings are moved, you can refer to the instructions in [`tests.md`][tests_md] to manage them.

## Advanced details

### What does the test proxy do?

The gist of the test proxy is that it stands in between your tests and the service. What this means is that test
requests which would usually go straight to the service should instead point to the locally-hosted test proxy.

For example, if an operation would typically make a GET request to
`https://fakeazsdktestaccount.table.core.windows.net/Tables`, that operation should now be sent to
`https://localhost:5001/Tables` instead. The original endpoint should be stored in an `x-recording-upstream-base-uri` --
the proxy will send the original request and record the result.

The `recorded_by_proxy` and `recorded_by_proxy_async` decorators patch test requests to do this for you.

### How does the test proxy know when and what to record or play back?

This is achieved by making POST requests to the proxy server that say whether to start or stop recording or playing
back, as well as what test is being run.

To start recording a test, the server should be primed with a POST request:

```
URL: https://localhost:5001/record/start
headers {
    "x-recording-file": "<path-to-test>/recordings/<testfile>.<testname>"
}
```

This will return a recording ID in an `x-recording-id` header. This ID should be sent as an `x-recording-id` header in
all further requests during the test.

After the test has finished, a POST request should be sent to indicate that recording is complete:

```
URL: https://localhost:5001/record/stop
headers {
    "x-recording-id": "<x-recording-id>"
}
```

Running tests in playback follows the same pattern, except that requests will be sent to `/playback/start` and
`/playback/stop` instead. A header, `x-recording-mode`, should be set to `record` for all requests when recording and
`playback` when playing recordings back. More details can be found [here][detailed_docs].

The `recorded_by_proxy` and `recorded_by_proxy_async` decorators send the appropriate requests at the start and end of
each test case.

### Use `pytest.mark.parametrize` with migrated tests

Migrating tests to use basic `pytest` tools allows us to take advantage of helpful features such as
[parametrization][parametrize]. Parametrization allows you to share test code by re-running the same test with varying
inputs. For example, [`azure-keyvault-keys` tests][parametrize_example] are parametrized to run with multiple API
versions and multiple Key Vault configurations.

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
@pytest.mark.parameterize("a, b", test_values)
def test_function(a, b, **kwargs):
    ...

# Doesn't work; raises collection error
# `recorded_by_proxy`'s wrapping function doesn't accept positional `a` and `b` parameters
@pytest.mark.parameterize("a, b", test_values)
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
@pytest.mark.parameterize("a, b", test_values)
@ArgumentPasser()
@recorded_by_proxy
def test_recorded_function(a, b, **kwargs):
    ...
```

You can also introduce additional logic into the `__call__` method of your intermediate decorator. In the aforementioned
[`azure-keyvault-keys` test example][parametrize_example], the decorator between `parametrize` and `recorded_by_proxy`
is actually a [client preparer][parametrize_class] that creates a client based on the parametrized input and passes this
client to the test.


[detailed_docs]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md

[env_var_docs]: https://github.com/Azure/azure-sdk-for-python/tree/main/tools/azure-sdk-tools/devtools_testutils#use-the-environmentvariableloader
[env_var_loader]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/envvariable_loader.py

[mgmt_recorded_test_case]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/mgmt_recorded_testcase.py

[parametrize]: https://docs.pytest.org/latest/example/parametrize.html
[parametrize_example]: https://github.com/Azure/azure-sdk-for-python/blob/d92b63b9976b0025b274016c49a250fb7c4d7333/sdk/keyvault/azure-keyvault-keys/tests/test_key_client.py#L182
[parametrize_class]: https://github.com/Azure/azure-sdk-for-python/blob/d92b63b9976b0025b274016c49a250fb7c4d7333/sdk/keyvault/azure-keyvault-keys/tests/_test_case.py#L59
[pipelines_ci]: https://github.com/Azure/azure-sdk-for-python/blob/5ba894966ed6b0e1ee8d854871f8c2da36a73d79/sdk/eventgrid/ci.yml#L30
[pipelines_live]: https://github.com/Azure/azure-sdk-for-python/blob/e2b5852deaef04752c1323d2ab0958f83b98858f/sdk/textanalytics/tests.yml#L26-L27
[proxy_cert_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/documentation/test-proxy/trusting-cert-per-language.md
[py_sanitizers]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/sanitizers.py
[pytest_collection]: https://docs.pytest.org/latest/goodpractices.html#test-discovery
[pytest_fixtures]: https://docs.pytest.org/latest/fixture.html#scope-sharing-fixtures-across-classes-modules-packages-or-session
[pytest_setup]: https://docs.pytest.org/xunit_setup.html
[pytest_using_fixtures]: https://docs.pytest.org/latest/how-to/fixtures.html#how-to-fixtures

[recording_migration]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md
[rg_preparer]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/resource_testcase.py

[sanitizers]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md#session-and-test-level-transforms-sanitiziers-and-matchers
[start_test_proxy]: https://github.com/Azure/azure-sdk-for-python/blob/63a35890a0188dfcac094aa7dc1ec7cc730945cd/tools/azure-sdk-tools/devtools_testutils/proxy_docker_startup.py#L111
[stop_test_proxy]: https://github.com/Azure/azure-sdk-for-python/blob/63a35890a0188dfcac094aa7dc1ec7cc730945cd/tools/azure-sdk-tools/devtools_testutils/proxy_docker_startup.py#L149

[tables_preparers]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/tests/preparers.py
[test_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/TestResources#readme
[tests_md]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#run-tests-with-out-of-repo-recordings
[troubleshooting]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_troubleshooting.md

[variables_api]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy#storing-variables
[vcrpy]: https://vcrpy.readthedocs.io
