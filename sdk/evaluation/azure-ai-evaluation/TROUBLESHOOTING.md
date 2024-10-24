# Troubleshoot AI Evaluation SDK Issues

This guide walks you through how to investigate failures, common errors in the `azure-ai-evaluation` SDK, and steps to mitigate these issues.

## Table of Contents

- [Handle Evaluate API Errors](#handle-evaluate-api-errors)
  - [Troubleshoot Remote Tracking Issues](#troubleshoot-remote-tracking-issues)
  - [Safety Metric Supported Regions](#safety-metric-supported-regions)
- [Handle Simulation Errors](#handle-simulation-errors)
  - [Adversarial Simulation Supported Regions](#adversarial-simulation-supported-regions)
- [Logging](#logging)
- [Get additional help](#get-additional-help)

## Handle Evaluate API Errors

### Troubleshoot Remote Tracking Issues

- Before running `evaluate()`, to ensure that you can enable logging and tracing to your Azure AI project, make sure you are first logged in by running `az login`.
- Then install the following sub-package:

    ```Shell
    pip install azure-ai-evaluation[remote]
    ```

- Ensure that you assign the proper permissions to the storage account linked to your Azure AI Studio hub. This can be done with the following command. More information can be found [here](https://review.learn.microsoft.com/azure/ai-studio/how-to/disable-local-auth).

    ```Shell
    az role assignment create --role "Storage Blob Data Contributor" --scope /subscriptions/<mySubscriptionID>/resourceGroups/<myResourceGroupName> --assignee-principal-type User --assignee-object-id "<user-id>"
    ```

- Additionally, if you're using a virtual network or private link, and your evaluation run upload fails because of that, check out this [guide](https://docs.microsoft.com/azure/machine-learning/how-to-enable-studio-virtual-network#access-data-using-the-studio).

### Safety Metric Supported Regions

Risk and safety evaluators depend on the Azure AI Studio safety evaluation backend service. For a list of supported regions, please refer to the documentation [here](https://aka.ms/azureaisafetyeval-regionsupport).

## Handle Simulation Errors

### Adversarial Simulation Supported Regions

Adversarial simulators use Azure AI Studio safety evaluation backend service to generate an adversarial dataset against your application. For a list of supported regions, please refer to the documentation [here](https://aka.ms/azureaiadvsimulator-regionsupport).

## Logging

You can set logging level via environment variable `PF_LOGGING_LEVEL`, valid values includes `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, default to `INFO`.

## Get Additional Help

Additional information on ways to reach out for support can be found in the [SUPPORT.md](https://github.com/Azure/azure-sdk-for-python/blob/main/SUPPORT.md) at the root of the repo.
