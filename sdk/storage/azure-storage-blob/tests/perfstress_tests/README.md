# Blob Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.
Note that tests for T1 and T2 SDKs cannot be run from the same environment, and will need to be setup separately.

### Setup for test resources

These tests will run against a pre-configured Storage account. The following environment variable will need to be set for the tests to access the live resources:
```
AZURE_STORAGE_CONNECTION_STRING=<live storage account connection string>
```

### Setup for T2 perf test runs

```cmd
(env) ~/azure-storage-blob> pip install -r dev_requirements.txt
(env) ~/azure-storage-blob> pip install -e .
```

### Setup for T1 perf test runs

```cmd
(env) ~/azure-storage-blob> pip install -r dev_requirements.txt
(env) ~/azure-storage-blob> pip install tests/perfstress_tests/T1_legacy_tests/t1_test_requirements.txt
```

## Test commands

When `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-storage-blob> cd tests
(env) ~/azure-storage-blob/tests> perfstress
```
Using the `perfstress` command alone will list the available perf tests found. Note that the available tests discovered will vary depending on whether your environment is configured for the T1 or T2 SDK.

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--no-client-share` Whether each parallel test instance should share a single client, or use their own. Default is False (sharing).
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async). This flag must be used for Storage legacy tests, which do not support async.
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

### Common Blob command line options
The options are available for all Blob perf tests:
- `--size=10240` Size in bytes of data to be transferred in upload or download tests. Default is 10240.
- `--max-concurrency=1` Number of threads to concurrently upload/download a single operation using the SDK API parameter. Default is 1.
- `--max-put-size` Maximum size of data uploading in single HTTP PUT. Default is 64*1024*1024.
- `--max-block-size` Maximum size of data in a block within a blob. Defaults to 4*1024*1024.
- `--buffer-threshold` Minimum block size to prevent full block buffering. Defaults to 4*1024*1024+1.

#### List Blobs command line options
This option is only available to the List Blobs test (T1 and T2).
- `--num-blobs` Number of blobs to list. Defaults to 100.

### T2 Tests
The tests currently written for the T2 SDK:
- `UploadTest` Uploads a stream of `size` bytes to a new Blob.
- `UploadFromFileTest` Uploads a local file of `size` bytes to a new Blob.
- `UploadBlockTest` Upload a single block of `size` bytes within a Blob.
- `DownloadTest` Download a stream of `size` bytes. 
- `ListBlobsTest` List a speficied number of blobs.

### T1 Tests
The tests currently written for the T1 SDK:
- `LegacyUploadTest` Uploads a stream of `size` bytes to a new Blob.
- `LegacyUploadFromFileTest` Uploads a local file of `size` bytes to a new Blob.
- `LegacyUploadBlockTest` Upload a single block of `size` bytes within a Blob.
- `LegacyDownloadTest` Download a stream of `size` bytes. 
- `LegacyListBlobsTest` List a speficied number of blobs.

## Example command
```cmd
(env) ~/azure-storage-blob/tests> perfstress UploadTest --parallel=2 --size=10240
```
