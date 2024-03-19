# Core Python client performance tests

In order to run the performance tests, the `devtools_testutils` package must be installed. This is done as part of the `dev_requirements.txt` installation. Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources
The following environment variables will need to be set for the tests to access the live resources:

```
AZURE_STORAGE_CONN_STR=<the connection string to the Storage account>
AZURE_STORAGE_ACCOUNT_NAME=<the Storage account name>
AZURE_STORAGE_ACCOUNT_KEY=<the Storage account key>

AZURE_STORAGE_CONTAINER_NAME=<the container name>
AZURE_STORAGE_BLOBS_ENDPOINT=<The Storage Blobs endpoint in the format 'https://{storageAccountName}.blob.core.windows.net'>

AZURE_STORAGE_TABLE_NAME=<The name to use for the Storage Table>
AZURE_STORAGE_TABLES_ENDPOINT=<The Storage Tables endpoint in the format 'https://{storageAccountName}.table.core.windows.net'>
```

### Setup for perf test runs

```cmd
(env) ~/core/corehttp> pip install -r dev_requirements.txt
(env) ~/core/corehttp> pip install .
```

## Test commands

When `devtools_testutils` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/core/corehttp> cd tests
(env) ~/core/corehttp/tests> perfstress
```

Using the `perfstress` command alone will list the available perf tests found.

### Tests

The tests currently available:

- `UploadBinaryDataTest` - Puts binary data of `size` in a Storage Blob (corresponds to the `upload_blob` Blob operation).
- `DownloadBinaryDataTest` - Gets binary data of `size` from a Storage Blob (corresponds to the `download_blob` Blob operation).
- `UpdateEntityJSONTest` - Puts JSON data of `size` in a Storage Table (corresponds to the `update_entity` Tables operation).
- `QueryEntitiesJSONTest` - Gets JSON data of `size` from a Storage Table (corresponds to the `query_entities` Tables operation).
- `ListEntitiesPageableTest` - Gets pageable data from a Storage Table (corresponds to the `list_entities` Tables operation).

### Common perf command line options

The `perfstress` framework has a series of common command line options built in. View them [here](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/perfstress_tests.md#default-command-options).

- `--sync` Whether to run the tests in sync or async. Default is False (async).
- `-d --duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `-i --iterations=1` Number of test iterations to run. Default is 1.
- `-p --parallel=1` Number of tests to run in parallel. Default is 1.
- `-w --warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.

#### Core perf test common command line options

The options that are available for all Core perf tests:

- `--transport` - By default, uses AiohttpTransport ("aiohttp") for async. By default, uses RequestsTransport ("requests") for sync. All options:
  - For async:
    - `"aiohttp"`: AiohttpTransport (default)
    - `"httpx"`: AsyncHttpXTransport
  - For sync:
    - `"requests"`: RequestsTransport (default)
    - `"httpx"`: HttpXTransport
- `--use-entra-id` - Flag to pass in to use Microsoft Entra ID as the authentication. By default, set to False.
- `--size=10240` - Size of request content (in bytes). Defaults to 10240. (Not used by `ListEntitiesPageableTest`.)
- `--policies` - List of policies to pass in to the pipeline. Options:
  - None: No extra policies passed in, except for authentication policy. This is the default.
  - 'all': All policies added automatically by autorest.
  - 'policy1,policy2': Comma-separated list of policies, such as 'RetryPolicy,UserAgentPolicy'"

#### Additional ListEntitiesPageableTest command line options

The options that are additionally available for `ListEntitiesPageableTest`:

- `--count=100` - Number of table entities to list. Defaults to 100.
- `--page-size=None` - Maximum number of entities to list per page. Default is None, which will return all possible results per page.

## Example command

```cmd
(env) ~/core/corehttp> perfstress DownloadBinaryDataTest --use-entra-id --transport httpx --size=20480 --parallel=2
```
