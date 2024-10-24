# Troubleshoot AI Evaluation SDK Issues

This guide walks you through how to investigate failures, common errors in the `azure-ai-evaluation` SDK, and steps to mitigate these issues.

## Table of Contents

- [Handle Evaluate API Errors](#handle-evaluate-api-errors)
  - [Troubleshoot Remote Tracking Issues](#troubleshoot-remote-tracking-issues)
  - [Safety Metric Supported Regions](#safety-metric-supported-regions)
- [Handle Simulator Errors](#handle-simulator-errors)
- [Logging](#logging)
- [Get additional help](#get-additional-help)

## Handle Evaluate API Errors

### Troubleshoot Remote Tracking Issues

- If your AI Studio hub is set to identity-based storage access and you're unable to upload data because of permission issues, check whether the `Storage Blob Data Contributor` role is assigned to the storage account linked to your Azure AI Studio hub. You can find more details [here](https://review.learn.microsoft.com/en-us/azure/ai-studio/how-to/disable-local-auth).

- Additionally, if you're using a virtual network or private link, and your evaluation run upload fails because of that, check out this [guide](https://docs.microsoft.com/azure/machine-learning/how-to-enable-studio-virtual-network#access-data-using-the-studio).

### Safety Metric Supported Regions

Risk and safety evaluators depend on the Azure AI Studio safety evaluation backend service. For a list of supported regions, please refer to the documentation [here](https://learn.microsoft.com/azure/ai-studio/how-to/develop/evaluate-sdk#risk-and-safety-evaluators).

## Handle Simulator Errors

Coming soon...

## Logging

You can set logging level via environment variable `PF_LOGGING_LEVEL`, valid values includes `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, default to `INFO`.

## Get Additional Help

Additional information on ways to reach out for support can be found in the [SUPPORT.md](https://github.com/Azure/azure-sdk-for-python/blob/main/SUPPORT.md) at the root of the repo.
