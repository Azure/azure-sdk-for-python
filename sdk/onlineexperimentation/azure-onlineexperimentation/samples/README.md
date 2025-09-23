# Azure Online Experimentation SDK Samples

This directory contains samples for the Azure Online Experimentation SDK for Python. The samples demonstrate how to use the SDK to perform various operations like creating metrics, validating metrics, retrieving metrics, and more.

## Prerequisites

- Python 3.9 or later
- Azure subscription
- Online Experimentation workspace

## Setup

1. Install the Azure Online Experimentation SDK:

```bash
pip install azure-onlineexperimentation
```

2. Set environment variables:

```bash
# Replace with your Online Experimentation workspace endpoint
export AZURE_ONLINEEXPERIMENTATION_ENDPOINT="https://{workspaceId}.{region}.exp.azure.net"
```

## Running the Samples

Each sample is contained in its own script file and can be run directly:

```bash
python sample_initialize_client.py
```

## Sample Descriptions

- [**sample_initialize_client.py**](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/onlineexperimentation/azure-onlineexperimentation/samples/sample_initialize_client.py): Shows how to initialize the Online Experimentation client
- [**sample_create_experiment_metrics.py**](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/onlineexperimentation/azure-onlineexperimentation/samples/sample_create_experiment_metrics.py): Demonstrates creating different types of experiment metrics (event count, user count, event rate, user rate, sum, average, and percentile metrics)
- [**sample_validate_experiment_metrics.py**](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/onlineexperimentation/azure-onlineexperimentation/samples/sample_validate_experiment_metrics.py): Shows how to validate metrics before creation
- [**sample_retrieve_and_list_metrics.py**](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/onlineexperimentation/azure-onlineexperimentation/samples/sample_retrieve_and_list_metrics.py): Demonstrates how to retrieve individual metrics and list all metrics
- [**sample_update_experiment_metric.py**](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/onlineexperimentation/azure-onlineexperimentation/samples/sample_update_experiment_metric.py): Shows how to update an existing metric
- [**sample_delete_experiment_metric.py**](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/onlineexperimentation/azure-onlineexperimentation/samples/sample_delete_experiment_metric.py): Demonstrates how to delete a metric

## Next Steps

- Explore the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python) on GitHub
