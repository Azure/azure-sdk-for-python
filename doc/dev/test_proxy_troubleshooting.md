# Guide for test proxy troubleshooting

This guide details some common errors that can come up when migrating to and using the Azure SDK test proxy. For more
information about migrating existing tests to the test proxy, please refer to the
[test proxy migration guide][migration_guide].

Documentation of the motivations and goals of the test proxy can be found [here][general_docs] in the azure-sdk-tools
GitHub repository, and documentation of how to set up and use the proxy can be found [here][detailed_docs].

## Table of contents
- [General troubleshooting tip](#general-troubleshooting-tip)
- [Test collection failure](#test-collection-failure)
- [Errors in tests using resource preparers](#errors-in-tests-using-resource-preparers)
- [Playback failures from body matching errors](#playback-failures-from-body-matching-errors)
- [Recordings not being produced](#recordings-not-being-produced)
- [KeyError during container startup](#keyerror-during-container-startup)
- [ConnectionError during test startup](#connectionerror-during-test-startup)
- [Different error than expected when using proxy](#different-error-than-expected-when-using-proxy)
- [Test setup failure in test pipeline](#test-setup-failure-in-test-pipeline)

## General troubleshooting tip

For any issue that may come up, it's generally a good idea to first try deleting any existing proxy container (which
will be called `ambitious_azsdk_test_proxy`) and creating a new one by running tests. This will fetch the latest tag of
the test proxy Docker container, meaning the latest version of the proxy tool will be used.

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

## Recordings not being produced

First, make sure that the environment variable `AZURE_SKIP_LIVE_RECORDING` isn't set to "true". If it's not and live
tests still aren't producing recordings, try deleting the `ambitious_azsdk_test_proxy` Docker container and re-running
tests. The recording storage location is determined when the test proxy Docker container is created. If there are
multiple local copies of the `azure-sdk-for-python` repo on your machine, the container could be storing recordings in
the wrong repo.

## KeyError during container startup

Try updating your machine's version of Docker. Older versions of Docker may not return a status to indicate whether or
not the proxy container is running, which the [proxy_startup.py][proxy_startup] script needs to determine.

## ConnectionError during test startup

For example, you may see a `requests.exceptions.ConnectionError` when trying to contact URL `/Info/Available`. This
means that the test proxy tool wasn't started up properly, so requests to the tool are failing. Make sure Docker is
installed and is up to date, and ensure that Linux containers are being used.

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


[detailed_docs]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy/Azure.Sdk.Tools.TestProxy/README.md
[general_docs]: https://github.com/Azure/azure-sdk-tools/blob/main/tools/test-proxy/README.md
[mgmt_recorded_test_case]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/mgmt_recorded_testcase.py
[migration_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
[proxy_pipelines]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md#enable-the-test-proxy-in-pipelines
[proxy_startup]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/proxy_startup.py
[py_sanitizers]: https://github.com/Azure/azure-sdk-for-python/blob/main/tools/azure-sdk-tools/devtools_testutils/sanitizers.py
[pytest_collection]: https://docs.pytest.org/latest/goodpractices.html#test-discovery
[wrong_exception]: https://github.com/Azure/azure-sdk-tools/issues/2907
