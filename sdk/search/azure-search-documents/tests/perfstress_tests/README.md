# Search Performance Tests

In order to run the performance tests, the `devtools_testutils` package must be installed. This is done as part of the `dev_requirements`.
Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.8.

### Setup for test resources

The query tests run against a pre-configured search service. See [here](https://learn.microsoft.com/azure/search/search-indexer-tutorial) about how to configure the service and import data. The following environment variable will need to be set for the tests to access the live resources:
```
AZURE_SEARCH_API_KEY=<search api key>
AZURE_SEARCH_SERVICE_ENDPOINT=<end point url>
AZURE_SEARCH_INDEX_NAME=<index name>
```

`UploadDocumentsTest` measures client-side batch construction and JSON serialization. It does not
send HTTP requests and does not require test resources or environment variables. It can be used to
investigate upload performance regressions such as [#46860](https://github.com/Azure/azure-sdk-for-python/issues/46860).

`compare_upload_documents.py` compares the `upload_documents` batch-construction overhead of two
package versions in isolated temporary virtual environments. It bypasses `index_documents` so the
result excludes HTTP and version-specific request serialization.

### Setup for perf test runs

```cmd
(env) ~/search/azure-search-documents> pip install -r dev_requirements.txt
(env) ~/search/azure-search-documents> pip install -e .
```

## Test commands

When `devtools_testutils` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/search/azure-search-documents> cd tests
(env) ~/search/azure-search-documents/tests> perfstress
```
Using the `perfstress` command alone will list the available perf tests found. 

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async). This flag must be used for Storage legacy tests, which do not support async.
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).
- `--num-documents` The number of results expect to be returned.
- `--vector-dimensions` The number of floats in each upload document vector. Defaults to 3072.
- `--text-length` The number of characters in each upload document text field. Defaults to 4000.

## Example command
```cmd
(env) ~/search/azure-search-documents/tests> perfstress SearchDocumentsTest
(env) ~/search/azure-search-documents/tests> perfstress AutoCompleteTest
(env) ~/search/azure-search-documents/tests> perfstress SuggestTest
(env) ~/search/azure-search-documents/tests> perfstress UploadDocumentsTest --sync --num-documents=100 --vector-dimensions=3072 --text-length=4000
(env) ~/search/azure-search-documents> python tests/perfstress_tests/compare_upload_documents.py --baseline azure-search-documents==11.6.0 --candidate .
```
