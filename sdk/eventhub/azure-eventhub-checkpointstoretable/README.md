[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure EventHubs Checkpoint Store client library for Python using Tables

Azure EventHubs Checkpoint Store is used for storing checkpoints while processing events from Azure Event Hubs.
This Checkpoint Store package works as a plug-in package to `EventHubConsumerClient`. It uses Azure Tables as the persistent store for maintaining checkpoints and partition ownership information.


# Getting started

### Prerequisites

- Python2.7, Python 3.6 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Event Hubs, you'll need a subscription. If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://azure.microsoft.com/).

- **Event Hubs namespace with an Event Hub:** To interact with Azure Event Hubs, you'll also need to have a namespace and Event Hub  available.  If you are not familiar with creating Azure resources, you may wish to follow the step-by-step guide for [creating an Event Hub using the Azure portal](https://docs.microsoft.com/azure/event-hubs/event-hubs-create).  There, you can also find detailed instructions for using the Azure CLI, Azure PowerShell, or Azure Resource Manager (ARM) templates to create an Event Hub.

- **Azure Storage Account:** You'll need to have an Azure Storage Account and create a Azure Storage Table to store the checkpoint data with entities. You may follow the guide [creating an Azure Storage Table Account](https://docs.microsoft.com/azure/storage/blobs/storage-blob-create-account-block-blob).

# Key concepts

Bullet point list of your library's main concepts.

# Examples

Examples of some of the key concepts for your library.

# Troubleshooting

Running into issues? This section should contain details as to what to do there.

# Next steps

More sample code should go here, along with links out to the appropriate example tests.

# Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)
