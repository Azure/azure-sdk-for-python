# Metrics advisor Performance Tests

In order to run the performance tests, the `devtools_testutils` package must be installed. This is done as part of the `dev_requirements`.
Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured metrics advisor service(see [Setting up Resource for Perf test Guide](https://microsoft.sharepoint.com/teams/AzureDeveloperExperience/_layouts/15/Doc.aspx?sourcedoc={b489fb65-ef3e-410c-a69e-c23fccf5fcca}&action=edit&wd=target%28Untitled%20Section.one%7C93e23c77-5539-4c7a-9059-efa745a43f58%2FSetting%20up%20Resource%20for%20Perf%20test%20Guide%7C395ad307-9fd1-4971-bcd5-6d336dde77cd%2F%29&wdorigin=703) about how to setup the instance and ingest data). The following environment variable will need to be set for the tests to access the live resources:
```
AZURE_METRICS_ADVISOR_ENDPOINT=<service endpoint>
AZURE_METRICS_ADVISOR_SUBSCRIPTION_KEY=<service subscription key>
AZURE_METRICS_ADVISOR_API_KEY=<service api key>
AZURE_METRICS_ADVISOR_ANOMALY_ALERT_CONFIGURATION_ID=<anomaly alert configuration id>
AZURE_METRICS_ADVISOR_ALERT_ID=<alert id>
AZURE_METRICS_ADVISOR_ANOMALY_DETECTION_CONFIGURATION_ID=<anomaly detection configuration id>
AZURE_METRICS_ADVISOR_INCIDENT_ID=<incident id>
```

### Setup for perf test runs

```cmd
(env) ~/azure-ai-metricsadvisor> pip install -r dev_requirements.txt
(env) ~/azure-ai-metricsadvisor> pip install -e .
```

## Test commands

When `devtools_testutils` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-ai-metricsadvisor> cd tests
(env) ~/azure-ai-metricsadvisor/tests> perfstress
```
Using the `perfstress` command alone will list the available perf tests found. 

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warmup=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async). This flag must be used for Storage legacy tests, which do not support async.
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

## Example command
```cmd
(env) ~/azure-ai-metricsadvisor/tests> perfstress ListAnomaliesTest
(env) ~/azure-ai-metricsadvisor/tests> perfstress ListIncidentsTest
(env) ~/azure-ai-metricsadvisor/tests> perfstress ListRootCausesTest
```
