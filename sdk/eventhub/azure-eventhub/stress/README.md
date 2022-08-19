# Azure Event Hubs Stress Tests PyAMQP

## Components

* values.yaml:
    * In this file we can specify a list of stress test scenarios to run. The run will then be configured within the testjob.yaml file.
* test_job.yaml
    * In this file we specify the pod spec for our stress test run. Within the python-eh-stress container we have a set of conditional statements where we set what each stress scenario is running. 

## How to Run

To run stress tests locally:
* Deploy stress test resources using the stress-test-resources.bicep file (rename to test-resources.bicep).
    At the azure-eventhub folder level run the following command:

    `..\..\..\eng\common\TestResources\New-TestResources.ps1 -ServiceDirectory 'eventhub/azure-eventhub/stress' -BaseName 'your-base-name' `

* After setting up the enviornment variables in a .env file, the stress tests can be run as python commands. Run the desired scenario's python commands in the terminal.

To deploy stress tests to Azure: 

* At the azure-eventhub folder level run the following command:

    `./..\..\..\eng\common\scripts/stress-testing/deploy-stress-tests.ps1  -Login   -PushImages  -Repository 'name-of-your-repository'`

## Adding Tests

To add tests, create a scenario in values.yaml and create a corresponding if statement and command set up in test_job.yaml. 