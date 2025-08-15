# Azure AI Project client library tests for Python

The instructions below are for running tests locally, on a Windows machine, against the live service using a local build of the client library.

## Setup an Azure AI Foundry project to use for testing

If you don't already have one, follow the instructions here to create a new Foundry project with all the necessary resources to run all tests.

The foundry project should contain the following:

* The following 3 AI models deployed to the Foundry resource (not a connected Azure OpenAI resource):
  * gpt-4o model deployed using a model deployment named "gpt-4o".
  * A model deployment named "DeepSeek-V3". It can be any model.
  * Any Cohere model. The  "model publisher" should be "Cohere". Model name or deployment name does not matter.
* A connection of type "Azure OpenAI" named "connection1", that uses api key auth, with  "model_deployment_name": "gpt-4o".
* A connection of type "Azure OpenAI" named "connection2", that uses Entra ID auth, with "model_deployment_name": "gpt-4o" (it can be the same service as above).
* A connection of type "AzureStorageAccount" named "balapvbyostoragecanary".
* An Application Insights resource enabled (per "Tracing" tab in Foundry UI)

Steps to deploy a new Foundry project:

* Clone this repository
* Change directory to this folder:<br>
`cd sdk\ai\azure-ai-projects\tests\setup`
* Log in to Azure and select a subscription:<br>
`az login`
* Make sure you have the right privileges in this subscription to create a new resource group
* Create a new resource group in your subscription (update resource group name and location as needed):<br>
`az group create --name dcohen-rg-projects-sdk-tests --location eastus`
* Create a Foundry project in the resource group (update resouce group name, AI service name and AI Foundry project name as needed):<br>
`az deployment group create --resource-group dcohen-rg-projects-sdk-tests --template-file main.bicep`

The above instructions were inspired by these articles
* ["Quickstart: Create an Azure AI Foundry project using a Bicep file"](https://learn.microsoft.com/azure/ai-foundry/how-to/create-azure-ai-project-template)
* ["Azure AI Foundry Agent Service: Standard Agent Setup with Public Networking"](https://github.com/azure-ai-foundry/foundry-samples/tree/main/samples/microsoft/infrastructure-setup/41-standard-agent-setup)

## Build and install the client library

- Clone or download this sample repository.
- Open a command prompt window in the folder `sdk\ai\azure-ai-projects`
- Install development dependencies:
    ```bash
    pip install -r dev_requirements.txt
    ```
- Install package from sources:
    ```bash
    pip install -e .
    ```

## Log in to Azure

```bash
az login
```

## Setup up environment variables

Copy the file `azure_ai_projects_tests.template.env` (located in the above folder), and save it as file named `azure_ai_projects_tests.env`.
Enter appropriate values for the environment variables used for the tests you want to run.

## Configure test proxy

Configure the test proxy to run live service tests without recordings:

```bash
set AZURE_TEST_RUN_LIVE=true
set AZURE_SKIP_LIVE_RECORDING=true
set PROXY_URL=http://localhost:5000
set AZURE_TEST_USE_CLI_AUTH=true
```

## Run tests

To run all tests, type:

```bash
pytest
```

To run tests in a particular folder (`tests\connections` for example):

```bash
pytest tests\connections
```

## Additional information

See [test documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) for additional information, including how to set proxy recordings and run tests using recordings.
