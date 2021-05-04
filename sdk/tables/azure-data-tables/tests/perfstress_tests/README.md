# Tables Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.
T1 perf tests are not available at this time.

### Setup for test resources

These tests will run against an existing Storage or Cosmos account. The following environment variable will need to be set for the tests to access the live resources:
```
AZURE_TABLES_CONNECTION_STRING=<live tables account connection string>
```

### Setup for T2 perf test runs

```cmd
(env) ~/azure-data-tables> pip install -r dev_requirements.txt
(env) ~/azure-data-tables> pip install -e .
```

## Test commands

When `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-data-tables> cd tests
(env) ~/azure-data-tables/tests> perfstress
```
Using the `perfstress` command alone will list the available perf tests found. Note that the available tests discovered will vary depending on whether your environment is configured for the T1 or T2 SDK.

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--no-client-share` Whether each parallel test instance should share a single client, or use their own. Default is False (sharing).
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async). This flag must be used for legacy tests, which do not support async.
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

### Tables command line options
- `--full-edm` Whether to use entities that utilize all EDM types for serialization/deserialization, or only strings. Default is `False` (only strings).
- `--count` Number of entities. Defaults to 100. This option is only available to the ListEntities and CreateEntityBatch tests.

### T2 Tests
The tests currently written for the T2 SDK:
- `CreateEntityTest` Upsert a single entity.
- `CreateEntityBatchTest` Upsert a transaction of entities.
- `ListEntitiesTest` List entities in a table.


## Example command
```cmd
(env) ~/azure-data-tables/tests> perfstress ListEntitiesTest --parallel=2 --count=1250 --full-edm
```