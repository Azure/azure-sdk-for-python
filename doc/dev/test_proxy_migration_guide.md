# Guide for migrating to the test proxy from vcrpy

This guide describes the changes that service SDKs should make to their test frameworks in order to take advantage of
the Azure SDK test proxy.

Documentation of the motivations and goals of the test proxy can be found [here][general_docs] in the azure-sdk-tools
GitHub repository, and documentation of how to set up and use the proxy can be found [here][detailed_docs].

## Update existing tests

### Current test structure

Test classes currently inherit from AzureTestCase, and test methods can optionally use decorators:

```py
from devtools_testutils import AzureTestCase

class TestExample(AzureTestCase):

    def test_example(self):
        ...

    @ExamplePreparer()
    def test_example_with_preparer(self):
        ...
```

### New test structure

To use the proxy, test classes should inherit from AzureRecordedTestCase and recorded test methods should use a
`recorded_by_proxy` decorator:

```py
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

class TestExample(AzureRecordedTestCase):

    @recorded_by_proxy
    def test_example(self):
        ...

    @ExamplePreparer()
    @recorded_by_proxy
    def test_example_with_preparer(self):
        ...
```

For async tests, import the `recorded_by_proxy_async` decorator from `devtools_testutils.aio` and use it in the same
way as `recorded_by_proxy`.

> **Note:** since AzureRecordedTestCase doesn't inherit from `unittest.TestCase`, test class names need to start
> with "Test" in order to be properly collected by pytest by default. For more information, please refer to
> [pytest's documentation][pytest_collection].

## Run the tests

### Perform one-time setup

The test proxy is made available for your tests via a Docker container. Some tests require an SSL connection to work, so
the Docker image used for the container has a certificate imported that you need to trust on your machine. Instructions
on how to do so can be found [here][proxy_cert_docs].

### Start the proxy server

The test proxy has to be available in order for tests to work in live or playback mode. There's a
[section](#manually-start-the-proxy) under [Advanced details](#advanced-details) that describes how to do this manually,
but it's recommended that tests use a `pytest` fixture to start and stop the proxy automatically when running tests.

In a `conftest.py` file for your package's tests, add a session-level fixture that accepts `devtools_testutils.test_proxy`
as a parameter (and has `autouse` set to `True`):

```python
from devtools_testutils import test_proxy

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
```

If your tests already use an `autouse`d, session-level fixture for tests, you can accept the `test_proxy` parameter in
that existing fixture instead of adding a new one. For an example, see the [Register sanitizers](#register-sanitizers)
section of this document.

In general, if any fixture requires the test proxy to be available by the time it's used, that fixture should accept this
`test_proxy` parameter.

### Record or play back tests

Configuring live and playback tests is done with the `AZURE_TEST_RUN_LIVE` environment variable. When this variable is
set to "true" or "yes", live tests will run and produce recordings. When this variable is set to "false" or "no", or
not set at all, tests will run in playback mode and attempt to match existing recordings.

Recordings for a given package will end up in that package's `/tests/recordings` directory, just like they currently
do. Recordings that use the test proxy are `.json` files instead of `.yml` files, so migrated test suites no longer
need old `.yml` recordings.

> **Note:** at this time, support for configuring live or playback tests with a `testsettings_local.cfg` file has been
> deprecated in favor of using just `AZURE_TEST_RUN_LIVE`.

### Register sanitizers

Since the test proxy doesn't use [`vcrpy`][vcrpy], tests don't use a scrubber to sanitize values in recordings.
Instead, sanitizers (as well as matchers and transforms) can be registered on the proxy as detailed in
[this][sanitizers] section of the proxy documentation. Sanitizers can be registered via `add_*_sanitizer` methods in
`devtools_testutils`. For example, the general-use method for sanitizing recording bodies, headers, and URIs is
`add_general_regex_sanitizer`. Other sanitizers are available for more specific scenarios and can be found at
[devtools_testutils/sanitizers.py][py_sanitizers].

Sanitizers, matchers, and transforms remain registered until the proxy container is stopped, so for any sanitizers that
are shared by different tests, using a session fixture declared in a `conftest.py` file is recommended. Please refer to
[pytest's scoped fixture documentation][pytest_fixtures] for more details.

As a simple example, to emulate the effect registering a name pair with a `vcrpy` scrubber, you can provide the exact
value you want to sanitize from recordings as the `regex` in the general regex sanitizer. To replace all instances of
the string "my-key-vault" with "fake-vault" in recordings, you could add something like the following in the package's
`conftest.py` file:

```python
from devtools_testutils import add_general_regex_sanitizer, test_proxy

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_general_regex_sanitizer(regex="my-key-vault", value="fake-vault")
```

Note that the sanitizer fixture accepts the `test_proxy` fixture as a parameter to ensure the proxy is started
beforehand.

For a more advanced scenario, where we want to sanitize the account names of all storage endpoints in recordings, we
could instead call

```python
add_general_regex_sanitizer(
    regex="(?<=\\/\\/)[a-z]+(?=(?:|-secondary)\\.(?:table|blob|queue)\\.core\\.windows\\.net)",
    value="fakeendpoint",
)
```

`add_general_regex_sanitizer` accepts a regex, replacement value, and capture group as keyword-only arguments. In the
snippet above, any storage endpoint URIs that match the specified URI regex will have their account name replaced with
"fakeendpoint". A request made to `https://tableaccount-secondary.table.core.windows.net` will be recorded as being
made to `https://fakeendpoint-secondary.table.core.windows.net`, and URIs will also be sanitized in bodies and headers.

For more details about sanitizers and their options, please refer to [devtools_testutils/sanitizers.py][py_sanitizers].

### Enabling the test proxy in CI

To enable using the test proxy in CI, you need to set the parameter `TestProxy: true` in the `ci.yml` and `tests.yml`
files in the service level folder. For example, in `sdk/eventgrid/ci.yml`:

![image](https://user-images.githubusercontent.com/45376673/142270668-5be58bca-87e5-45f5-b593-44f8b1f757bc.png)
### Record test variables

To run recorded tests successfully when there's an element of non-secret randomness to them, the test proxy provides a
[`variables` API](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy#storing-variables).
This makes it possible for a test to record the values of variables that were used during recording and use the same
values in playback mode without a sanitizer.

For example, imagine that a test uses a randomized `table_name` variable when creating resources. The same random value
for `table_name` can be used in playback mode by using this `variables` API.

There are two requirements for a test to use recorded variables. First, the test method should accept `**kwargs` and/or
a `variables` parameter. Second, the test method should `return` a dictionary with any test variables that it wants to
record. This dictionary will be stored in the recording when the test is run live, and will be passed to the test as a
`variables` keyword argument when the test is run in playback.

Below is a code example of how a test method could use recorded variables:

```python
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

class TestExample(AzureRecordedTestCase):

    @recorded_by_proxy
    def test_example(self, variables):
        # in live mode, variables is an empty dictionary
        # in playback mode, the value of variables is {"table_name": "random-value"}
        if self.is_live:
            table_name = "random-value"
            variables = {"table_name": table_name}
        
        # use variables["table_name"] when using the table name throughout the test
        ...

        # return the variables at the end of the test
        return variables
```

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

### Manually start the proxy

There are two options for manually starting and stopping the test proxy: one uses a PowerShell command, and one uses
methods from `devtools_testutils`.

#### PowerShell

There is a [PowerShell script][docker_start_proxy] in `eng/common/testproxy` that will fetch the proxy Docker image if
you don't already have it, and will start or stop a container running the image for you. You can run the following
command from the root of the `azure-sdk-for-python` directory to start the container whenever you want to make the test
proxy available for running tests:

```powershell
.\eng\common\testproxy\docker-start-proxy.ps1 "start"
```

Note that the proxy is available as long as the container is running. In other words, you don't need to start and
stop the container for each test run or between tests for different SDKs. You can run the above command in the morning
and just stop the container whenever you'd like. To stop the container, run the same command but with `"stop"` in place
of `"start"`.

#### Python

There are two methods in `devtools_testutils`,
[start_test_proxy](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/proxy_docker_startup.py#L97)
and
[stop_test_proxy](https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/proxy_docker_startup.py#L135),
that can be used to manually start and stop the test proxy. Like `docker-start-proxy.ps1`, `start_test_proxy` will
automatically fetch the proxy Docker image for you and start the container if it's not already running.

For more details on proxy startup, please refer to the [proxy documentation][detailed_docs].

[detailed_docs]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md
[docker_start_proxy]: https://github.com/Azure/azure-sdk-for-python/blob/main/eng/common/testproxy/docker-start-proxy.ps1
[general_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/README.md
[proxy_cert_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/documentation/trusting-cert-per-language.md
[py_sanitizers]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/sanitizers.py
[pytest_collection]: https://docs.pytest.org/latest/goodpractices.html#test-discovery
[pytest_fixtures]: https://docs.pytest.org/latest/fixture.html#scope-sharing-fixtures-across-classes-modules-packages-or-session
[sanitizers]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md#session-and-test-level-transforms-sanitiziers-and-matchers
[vcrpy]: https://vcrpy.readthedocs.io
