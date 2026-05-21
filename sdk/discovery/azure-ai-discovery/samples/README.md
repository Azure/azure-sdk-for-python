# Azure AI Discovery Samples for Python

Sample code demonstrating key features of the Azure AI Discovery client library for Python.

## Prerequisites

- Python 3.9 or later
- An Azure subscription
- An Azure AI Discovery Workspace and/or Bookshelf instance
- Install the package: `pip install azure-ai-discovery`
- Install Azure Identity: `pip install azure-identity`

## Setup

Azure Discovery resources used in these samples are defined via environment variables. Before running sample code, be sure to set the appropriate environment variable(s) to point to the resources that the sample(s) will use. Refer to the comments in each individual sample file for which resources and associated environment variables that it needs to run.  

All samples use `DefaultAzureCredential` for authentication — see [azure-identity](https://learn.microsoft.com/python/api/overview/azure/identity-readme) for details.

### Environment Variables for WorkspaceClient Samples

| Variable | Description |
|----------|-------------|
| `AZURE_DISCOVERY_WORKSPACE_ENDPOINT` | Workspace endpoint URL |
| `AZURE_DISCOVERY_PROJECT_NAME` | Project name |
| `AZURE_DISCOVERY_INVESTIGATION_NAME` | Investigation name (for conversations, tasks) |
| `AZURE_DISCOVERY_TOOL_ID` | ARM resource ID of the tool (for tools sample) |
| `AZURE_DISCOVERY_NODE_POOL_ID` | ARM resource ID of the node pool |

### Environment Variables for BookshelfClient Samples

| Variable | Description |
|----------|-------------|
| `AZURE_DISCOVERY_BOOKSHELF_ENDPOINT` | Bookshelf endpoint URL |
| `AZURE_DISCOVERY_KNOWLEDGE_BASE_NAME` | Knowledge base name |
| `AZURE_DISCOVERY_STORAGE_ASSET_ID` | ARM resource ID of the storage asset |
| `AZURE_DISCOVERY_USER_ASSIGNED_IDENTITY` | ARM resource ID of the managed identity |
| `AZURE_DISCOVERY_NODE_POOL_ID` | ARM resource ID of the node pool used for indexing |
| `AZURE_DISCOVERY_PROJECT_ARM_ID` | ARM resource ID of the project |
| `AZURE_DISCOVERY_NODE_POOL_ID` | ARM resource ID of the node pool |

## Samples

| Sample | Description |
|--------|-------------|
| [sample_investigations.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/discovery/azure-ai-discovery/samples/sample_investigations.py) | Create, list, get, and delete investigations; manage the Discovery Engine |
| [sample_conversations.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/discovery/azure-ai-discovery/samples/sample_conversations.py) | Create, list, get, and delete conversations |
| [sample_tasks.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/discovery/azure-ai-discovery/samples/sample_tasks.py) | Create, list, filter, comment on, start, and delete tasks |
| [sample_tools.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/discovery/azure-ai-discovery/samples/sample_tools.py) | Run tools on compute, check run status, and monitor usage |
| [sample_knowledge_bases.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/discovery/azure-ai-discovery/samples/sample_knowledge_bases.py) | Manage knowledge bases, versions, and indexing |
