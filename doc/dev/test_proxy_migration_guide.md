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
RecordedByProxy decorator:

```py
from devtools_testutils import AzureRecordedTestCase, RecordedByProxy

class TestExample(AzureRecordedTestCase):

    @RecordedByProxy
    def test_example(self):
        ...

    @ExamplePreparer()
    @RecordedByProxy
    def test_example_with_preparer(self):
        ...
```

For async tests, import the RecordedByProxyAsync decorator from `devtools_testutils.aio` and use it in the same
way as RecordedByProxy.

> **Note:** since AzureRecordedTestCase doesn't inherit from `unittest.TestCase`, test class names need to start
> with "Test" in order to be properly collected by pytest by default. For more information, please refer to
> [pytest's documentation][pytest_collection].

## Run the tests

### Perform one-time setup

The test proxy is made available for your tests via a Docker container. Run the following command to build this
container, providing the full path to the root of your local `azure-sdk-for-python` repo in place of `{path}`:

```cmd
docker container create -v C:\\{path}\\azure-sdk-for-python:/etc/testproxy -p 5001:5001 -p 5000:5000 --name ambitious_azsdk_test_proxy azsdkengsys.azurecr.io/engsys/testproxy-lin:1035186
```

Some tests require an SSL connection to work, so the Docker image used for the container has a certificate imported
that you need to trust on your machine. Instructions on how to do so can be found [here][proxy_cert_docs].

### Start the proxy server

Run the following command to start the container whenever you want to make the test proxy available:

```cmd
docker container start ambitious_azsdk_test_proxy
```

Note that the proxy is available as long as the container is running. In other words, you don't need to start and
stop the container for each test run or between tests for different SDKs. You can run the above command in the morning
and just stop the container whenever you'd like. In the future, the proxy container will be set up and started
automatically when tests are run, and starting it manually will be optional.

For more details on proxy startup, please refer to the [proxy documentation][detailed_docs].

### Record or play back tests

Configuring live and playback tests is done with the `AZURE_TEST_RUN_LIVE` environment variable. When this variable is
set to "true" or "yes", live tests will run and produce recordings. When this variable is set to "false" or "no", or
not set at all, tests will run in playback mode and attempt to match existing recordings.

Recordings for a given package will end up in that package's `/tests/recordings` directory, just like they currently
do.

> **Note:** At this time, support for configuring live or playback tests with a `testsettings_local.cfg` file has been
> deprecated in favor of using just `AZURE_TEST_RUN_LIVE`.

### Register sanitizers

Since the test proxy doesn't use [`vcrpy`][vcrpy], tests don't use a scrubber to sanitize values in recordings.
Instead, sanitizers (as well as matchers and transforms) can be registered on the proxy as detailed in
[this][sanitizers] section of the proxy documentation. At the time of writing, sanitizers can be registered via
the `add_sanitizer` method in `devtools_testutils`. For example, at the start of a test file, you can set up a URI
sanitizer for all tests by doing something like the following:

```python
from devtools_testutils import add_sanitizer, AzureRecordedTestCase, ProxyRecordingSanitizer

add_sanitizer(ProxyRecordingSanitizer.URI, value="fakeendpoint")

class TestExample(AzureRecordedTestCase):
    ...
```

`add_sanitizer` accepts a sanitizer type from the ProxyRecordingSanitizer enum as a required parameter. A regular
expression to match and a value to use in recordings can be optionally provided as `regex` and `value` arguments,
respectively. In the above example, any request URIs that match the default regular expression will have their
domain name replaced with "fakeendpoint". A request made to `https://tableaccount.table.core.windows.net` will be
recorded as being made to `https://fakeendpoint.table.core.windows.net`.

Sanitizers, matchers, and transforms remain registered until the proxy container is stopped, so adding a sanitizer
at the top of a test file (like in the example) will make that sanitizer available for all test cases in the file.

## Implementation details

### What does the test proxy do?

The gist of the test proxy is that it stands in between your tests and the service. What this means is that test
requests which would usually go straight to the service should instead point to the locally-hosted test proxy.

For example, if an operation would typically make a GET request to
`https://fakeazsdktestaccount.table.core.windows.net/Tables`, that operation should now be sent to
`https://localhost:5001/Tables` instead. The original endpoint should be stored in an `x-recording-upstream-base-uri` --
the proxy will send the original request and record the result.

The RecordedByProxy and RecordedByProxyAsync decorators patch test requests to do this for you.

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

The RecordedByProxy and RecordedByProxyAsync decorators send the appropriate requests at the start and end of each test
case.

[detailed_docs]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md
[general_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/README.md
[proxy_cert_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/documentation/trusting-cert-per-language.md
[pytest_collection]: https://docs.pytest.org/en/latest/explanation/goodpractices.html#test-discovery
[sanitizers]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md#session-and-test-level-transforms-sanitiziers-and-matchers
[vcrpy]: https://vcrpy.readthedocs.io/en/latest/
