# Troubleshoot AI Evaluation SDK Issues

This guide walks you through how to investigate failures, common errors in the `azure-ai-evaluation` SDK, and steps to mitigate these issues.

## Table of Contents

- [Handle Evaluate API Errors](#handle-evaluate-api-errors)
  - [Troubleshoot Remote Tracking Issues](#troubleshoot-remote-tracking-issues)
  - [Troubleshoot Column Mapping Issues](#troubleshoot-column-mapping-issues)
  - [Troubleshoot Safety Evaluator Issues](#troubleshoot-safety-evaluator-issues)
  - [Troubleshoot Quality Evaluator Issues](#troubleshoot-quality-evaluator-issues)
- [Handle Simulation Errors](#handle-simulation-errors)
  - [Adversarial Simulation Supported Regions](#adversarial-simulation-supported-regions)
  - [Need to generate simulations for specific harm type](#need-to-generate-simulations-for-specific-harm-type)
  - [Simulator is slow](#simulator-is-slow)
- [Handle RedTeam Errors](#handle-redteam-errors)
  - [Target resource not found](#target-resource-not-found)
  - [Insufficient Storage Permissions](#insufficient-storage-permissions)
- [Logging](#logging)
- [Get Additional Help](#get-additional-help)

## Handle Evaluate API Errors

### Troubleshoot Remote Tracking Issues

- Before running `evaluate()`, to ensure that you can enable logging and tracing to your Azure AI project, make sure you are first logged in by running `az login`.

- Ensure that you assign the proper permissions to the storage account linked to your Azure AI Studio hub. This can be done with the following command. More information can be found [here](https://aka.ms/credentialleshub).

    ```Shell
    # <mySubscriptionID>: Subscription ID of the Azure AI Studio hub's linked storage account (available in Azure AI hub resource view in Azure Portal).
    # <myResourceGroupName>: Resource group of the Azure AI Studio hub's linked storage account.
    # <user-id>: User object ID for role assignment (retrieve with "az ad user show" command).

    az role assignment create --role "Storage Blob Data Contributor" --scope /subscriptions/<mySubscriptionID>/resourceGroups/<myResourceGroupName> --assignee-principal-type User --assignee-object-id "<user-id>"
    ```

- Additionally, if you're using a virtual network or private link, and your evaluation run upload fails because of that, check out this [guide](https://docs.microsoft.com/azure/machine-learning/how-to-enable-studio-virtual-network#access-data-using-the-studio).

### Troubleshoot Column Mapping Issues

- When using `column_mapping` parameter in evaluators, ensure all keys and values are non-empty strings and contain only alphanumeric characters. Empty strings, non-string values, or non-alphanumeric characters can cause serialization errors and issues in downstream applications. Example of valid mapping: `{"query": "${data.query}", "response": "${data.response}"}`.

### Troubleshoot Safety Evaluator Issues

- Risk and safety evaluators depend on the Azure AI Studio safety evaluation backend service. For a list of supported regions, please refer to the documentation [here](https://aka.ms/azureaisafetyeval-regionsupport).
- If you encounter a 403 Unauthorized error when using safety evaluators, verify that you have the `Contributor` role assigned to your Azure AI project. `Contributor` role is currently required to run safety evaluations.

### Troubleshoot Quality Evaluator Issues
- For `ToolCallAccuracyEvaluator`, if your input did not have a tool to evaluate, the current behavior is to output `null`.

## Handle Simulation Errors

### Adversarial Simulation Supported Regions

Adversarial simulators use Azure AI Studio safety evaluation backend service to generate an adversarial dataset against your application. For a list of supported regions, please refer to the documentation [here](https://aka.ms/azureaiadvsimulator-regionsupport).

### Need to generate simulations for specific harm type

The Adversarial simulator does not support selecting individual harms, instead we recommend running the `AdversarialSimulator` for 4x the number of specific harms as the `max_simulation_results`


### Simulator is slow

Identify the type of simulations being run (adversarial or non-adversarial).
Adjust parameters such as `api_call_retry_sleep_sec`, `api_call_delay_sec`, and `concurrent_async_task`. Please note that rate limits to llm calls can be both tokens per minute and requests per minute.

## Handle RedTeam errors

### Target resource not found
When initializing an Azure OpenAI model directly as `target` for a `RedTeam` scan, ensure `azure_endpoint` is specified in the format `https://<hub>.openai.azure.com/openai/deployments/<deployment_name>/chat/completions?api-version=2025-01-01-preview`. If using `AzureOpenAI`, `endpoint` should be specified in the format `https://<hub>.openai.azure.com/`. 

### Insufficient Storage Permissions
If you see an error like `WARNING: Failed to log artifacts to MLFlow: (UserError) Failed to upload evaluation run to the cloud due to insufficient permission to access the storage`, you need to ensure that proper permissions are assigned to the storage account linked to your Azure AI Project.

To fix this issue:
1. Open the associated resource group being used in your Azure AI Project in the Azure Portal
2. Look up the storage accounts associated with that resource group
3. Open each storage account and click on "Access control (IAM)" on the left side navigation
4. Add permissions for the desired users with the "Storage Blob Data Contributor" role

If you have Azure CLI, you can use the following command:

```Shell
# <mySubscriptionID>: Subscription ID of the Azure AI Studio hub's linked storage account (available in Azure AI hub resource view in Azure Portal).
# <myResourceGroupName>: Resource group of the Azure AI Studio hub's linked storage account.
# <user-id>: User object ID for role assignment (retrieve with "az ad user show" command).

az role assignment create --role "Storage Blob Data Contributor" --scope /subscriptions/<mySubscriptionID>/resourceGroups/<myResourceGroupName> --assignee-principal-type User --assignee-object-id "<user-id>"
```

## Logging

You can set logging level via environment variable `PF_LOGGING_LEVEL`, valid values includes `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, default to `INFO`.

## Get Additional Help

Additional information on ways to reach out for support can be found in the [SUPPORT.md](https://github.com/Azure/azure-sdk-for-python/blob/main/SUPPORT.md) at the root of the repo.
