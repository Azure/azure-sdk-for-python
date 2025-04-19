# Azure Online Experimentation SDK Samples

This directory contains samples for the Azure Online Experimentation SDK for Python. The samples demonstrate how to use the SDK to perform various operations like creating metrics, validating metrics, retrieving metrics, and more.

## Prerequisites

- Python 3.6 or later
- Azure subscription
- Online Experimentation workspace

## Setup

1. Install the Azure Online Experimentation SDK:

```bash
pip install azure-analytics-onlineexperimentation
```

2. Set environment variables:

```bash
# Replace with your Online Experimentation workspace endpoint
export AZURE_ONLINE_EXPERIMENTATION_ENDPOINT="https://your-workspace.api.experimentation.azure.com"
```

## Running the Samples

Each sample is contained in its own script file and can be run directly:

```bash
python sample1_initialize_client.py
```

## Sample Descriptions

- **sample1_initialize_client.py**: Shows how to initialize the Online Experimentation client
- **sample2_create_experiment_metrics.py**: Demonstrates creating different types of experiment metrics
- **sample3_validate_experiment_metrics.py**: Shows how to validate metrics before creation
- **sample4_retrieve_and_list_metrics.py**: Demonstrates how to retrieve individual metrics and list all metrics
- **sample5_update_experiment_metric.py**: Shows how to update an existing metric
- **sample6_delete_experiment_metric.py**: Demonstrates how to delete a metric

## Next Steps

- Visit the [Azure Online Experimentation documentation](https://docs.microsoft.com/azure/online-experimentation) for more information
- Explore the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python) on GitHub
