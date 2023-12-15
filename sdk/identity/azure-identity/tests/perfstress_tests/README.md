# azure-identity Performance Tests

In order to run the performance tests, the `devtools_testutils` package must be installed. This is done as part of the
`dev_requirements` install. Start by creating a new Python 3 virtual environment.

## Test commands

Once `devtools_testutils` is installed, you will have access to the `perfstress` command line tool, which will scan the
current module for runnable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

`perfstress` with no options will list all available tests: 
```
(env) ~/azure-identity/tests> perfstress
```

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async).
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

## Example command
```
(env) ~/azure-identity/tests> perfstress BearerTokenPolicyTest
```

## Tests
- `BearerTokenPolicyTest` Runs a single request through `BearerTokenCredentialPolicy`,
  and a mock transport
- `MemoryCacheRead` retrieves an access token from the default, in memory cache.
  This is useful primarily as a baseline for `PersistentCacheRead`.
- `PersistentCacheRead` retrives an access token from the persistent cache
