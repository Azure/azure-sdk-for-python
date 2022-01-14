# azure-containerregistry Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the
`dev_requirements` install. Start by creating a new virtual environment for your perf tests. This will need to be a
Python 3 environment, preferably >=3.6.

### Setup for test resources

The following environment variables will need to be set for the tests to access the live resources:

```
AZURE_TENANT_ID=<tenant ID of testing service principal>
AZURE_CLIENT_ID=<client ID of testing service principal>
AZURE_CLIENT_SECRET=<client secret of testing service principal>
CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT=<account URL of testing container registry>
```

### Import docker images into the newly created registry
An artifact should be prepared in the repository before running list_artifacts.py.
```
az acr login -n <registry-name>
az acr import --name <registry-name> --source docker.io/library/node:latest --image node:latest
az acr update --name <registry-name> --anonymous-pull-enabled
```

### Setup for perf test runs

```cmd
(env) ~/azure-containerregistry> pip install -r dev_requirements.txt
(env) ~/azure-containerregistry> pip install -e .
```

## Test commands

Once `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the
current module for runnable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-containerregistry> cd tests
(env) ~/azure-containerregistry/tests> perfstress
```
Using the `perfstress` command alone will list the available perf tests found. 

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async).
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

## Example command
```cmd
(env) ~/azure-containerregistry/tests> perfstress ListArtifactsTest --parallel=50 --duration=15
```