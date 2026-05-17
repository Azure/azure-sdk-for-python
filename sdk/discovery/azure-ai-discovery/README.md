# Azure AI Discovery Client Library for Python

The Azure AI Discovery client library for Python provides two clients for interacting with Azure AI Discovery services:

- **WorkspaceClient** — manage investigations, conversations, tasks, and tools in a Discovery workspace.
- **BookshelfClient** — manage knowledge bases and knowledge base versions.

[Source code][source_code] | [Package (PyPI)][pypi] | [Samples][samples]

## Getting Started

### Install the Package

```bash
python -m pip install azure-ai-discovery
```

### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure AI Discovery workspace or bookshelf instance.

### Authenticate the Client

Both clients use Azure Active Directory (AAD) token authentication. Use the [azure-identity][azure_identity] library to obtain credentials:

```bash
pip install azure-identity
```

```python
from azure.ai.discovery import WorkspaceClient, BookshelfClient
from azure.identity import DefaultAzureCredential

workspace_client = WorkspaceClient(
    endpoint="https://<workspaceName>.workspace.discovery.azure.com",
    credential=DefaultAzureCredential(),
)

bookshelf_client = BookshelfClient(
    endpoint="https://<bookshelfName>.bookshelf.discovery.azure.com",
    credential=DefaultAzureCredential(),
)
```

## Key Concepts

### WorkspaceClient

The `WorkspaceClient` provides access to Discovery workspace operations, organized into four operation groups:

- **Investigations** — create and manage research investigations within a project. Each investigation can have a Discovery Engine that autonomously explores data and generates insights.
- **Conversations** — interact with the Discovery Engine through conversational sessions tied to an investigation.
- **Tasks** — create, assign, and track units of work within an investigation, such as research steps or follow-up actions.
- **Tools** — run compute jobs on supercomputer node pools and monitor their status and resource usage.

### BookshelfClient

The `BookshelfClient` provides access to knowledge base management:

- **Knowledge Bases** — list available knowledge bases.
- **Knowledge Base Versions** — create, update, index, and manage versions of knowledge bases backed by storage assets.

## Examples

The following sections provide code snippets covering common scenarios. For complete runnable samples, see the [Samples][samples] directory.

### Create and Manage an Investigation

```python
from azure.ai.discovery import WorkspaceClient
from azure.ai.discovery.models import Investigation
from azure.identity import DefaultAzureCredential

client = WorkspaceClient(
    endpoint="https://<workspaceName>.workspace.discovery.azure.com",
    credential=DefaultAzureCredential(),
)

# Create an investigation
investigation = client.investigations.create_or_replace(
    project_name="my-project",
    investigation_name="sample-investigation",
    resource=Investigation(
        description="Investigating anomalies in dataset X",
        display_name="Sample Investigation",
    ),
)
print(f"Created investigation: {investigation.name}")

# Start the Discovery Engine
engine = client.investigations.start_discovery_engine(
    project_name="my-project",
    investigation_name="sample-investigation",
)
print(f"Discovery Engine status: {engine.discovery_engine_status}")
```

### Create and Manage Tasks

```python
from azure.ai.discovery import WorkspaceClient
from azure.ai.discovery.models import Task, TaskAssignee, TaskComment
from azure.identity import DefaultAzureCredential

client = WorkspaceClient(
    endpoint="https://<workspaceName>.workspace.discovery.azure.com",
    credential=DefaultAzureCredential(),
)

# Create a task
task = client.tasks.create(
    project_name="my-project",
    investigation_name="sample-investigation",
    body=Task(
        title="Analyze compound interactions",
        priority="High",
        description="Review the interaction data for compounds A and B",
        assigned_to=TaskAssignee(id="researcher-agent", type="Application"),
        investigation_id="/projects/my-project/investigations/sample-investigation",
    ),
)
print(f"Created task: {task.title} ({task.status})")

# Add a comment
client.tasks.add_comment(
    project_name="my-project",
    investigation_name="sample-investigation",
    task_name=task.name,
    body=TaskComment(
            created_by="sample-user",
            created_by_type="User",
            text="Initial analysis shows promising results.",
        ),
)
```

### Run a Tool on Compute

```python
from azure.ai.discovery import WorkspaceClient
from azure.identity import DefaultAzureCredential

client = WorkspaceClient(
    endpoint="https://<workspaceName>.workspace.discovery.azure.com",
    credential=DefaultAzureCredential(),
)

poller = client.tools.begin_run(
    project_name="my-project",
    tool_id="/subscriptions/.../tools/my-tool",
    node_pool_ids=["/subscriptions/.../nodePools/my-pool"],
    command='echo "Hello from Discovery"',
)
result = poller.result()
print(f"Run completed: {result.status}")
```

### Manage Knowledge Bases

```python
from azure.ai.discovery import BookshelfClient
from azure.ai.discovery.models import KnowledgeBaseVersion, StorageAssetReference
from azure.identity import DefaultAzureCredential

client = BookshelfClient(
    endpoint="https://<bookshelfName>.bookshelf.discovery.azure.com",
    credential=DefaultAzureCredential(),
)

# List knowledge bases
for kb in client.knowledge_bases.list():
    print(f"Knowledge base: {kb.name}")

# Create a knowledge base version
version = client.knowledge_base_versions.create_or_update(
    knowledge_base_name="my-kb",
    version_name="v1",
    resource=KnowledgeBaseVersion(
        description="Research data for compound analysis",
        copilot_instruction="Use this to query information about compound interactions.",
        storage_asset_references=[
            StorageAssetReference(
                id="/subscriptions/.../storageAssets/my-asset",
                user_assigned_identity="/subscriptions/.../userAssignedIdentities/my-id",
            ),
        ],
    ),
)
print(f"Created version: {version.name}")
```

## Troubleshooting

### Logging

This library uses the standard [logging][python_logging] library for logging. HTTP session information (URLs, headers, etc.) is logged at the `DEBUG` level.

Detailed `DEBUG` level logging, including request/response bodies and unredacted headers, can be enabled on a client with the `logging_enable` argument:

```python
client = WorkspaceClient(
    endpoint="https://<workspaceName>.workspace.discovery.azure.com",
    credential=DefaultAzureCredential(),
    logging_enable=True,
)
```

Or on a single operation:

```python
investigation = client.investigations.get(
    project_name="my-project",
    investigation_name="my-investigation",
    logging_enable=True,
)
```

### General

Azure AI Discovery clients raise exceptions defined in [azure-core][azure_core_exceptions]. For example, if you try to get an investigation that does not exist, `ResourceNotFoundError` is raised:

```python
from azure.core.exceptions import ResourceNotFoundError

try:
    client.investigations.get(
        project_name="my-project",
        investigation_name="nonexistent",
    )
except ResourceNotFoundError as e:
    print(f"Investigation not found: {e.message}")
```

## Next Steps

- [Samples][samples] — runnable code examples for common scenarios.
- [Azure AI Discovery documentation][product_docs]

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com)
with any additional questions or comments.

<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free/
[azure_identity]: https://learn.microsoft.com/python/api/overview/azure/identity-readme
[azure_core_exceptions]: https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/discovery/azure-ai-discovery
[pypi]: https://pypi.org/project/azure-ai-discovery/
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/discovery/azure-ai-discovery/samples
[product_docs]: https://learn.microsoft.com/azure/ai-discovery
