# App config Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured application configuration service. The following environment variable will need to be set for the tests to access the live resources:
```
AZURE_APP_CONFIG_CONNECTION_STRING=<app config connection string>
```

### Setup for perf test runs

```cmd
(env) ~/azure-appconfiguration> pip install -r dev_requirements.txt
(env) ~/azure-appconfiguration> pip install -e .
```

## Test commands

When `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-appconfiguration> cd tests
(env) ~/azure-appconfiguration/tests> perfstress
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

## Example command
```cmd
(env) ~/azure-appconfiguration/tests> perfstress GetTest
```
