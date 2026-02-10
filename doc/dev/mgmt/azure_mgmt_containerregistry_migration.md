# Azure SDK Migration Guide: `azure-mgmt-containerregistry`

The direct link to this page can be found at aka.ms/azsdk/python/migrate/azure-mgmt-containerregistry

This guide is for developers using `azure-mgmt-containerregistry` who need to migrate to the latest version.

## Summary of Changes

To improve the user experience, some APIs formerly in `azure-mgmt-containerregistry` have been moved to two new, more focused packages:
- `azure-mgmt-containerregistrytasks`

**Most APIs are still available in `azure-mgmt-containerregistry`**. Only a small subset of operations and models related to container registry tasks have been relocated.

This guide covers the two main changes you'll encounter:
1.  **Client Instantiation**: Operations that moved now require a client instance from their new package.
2.  **Model Imports**: Models that moved must be imported from their new package.

## Detailed Changes

### 1. Operation Changes

Below operations are now accessed through client from `azure-mgmt-containerregistrytasks`:
- AgentPoolsOperations
- RunsOperations
- TaskRunsOperations
- TasksOperations
- RegistriesOperations

**Before**:
Previously, all operations were accessed through `ContainerRegistryManagementClient`.

```python
from azure.mgmt.containerregistry import ContainerRegistryManagementClient

client = ContainerRegistryManagementClient(...)

# Operations abount tasks were on the main client
client.agent_pools.list(...)
client.runs.list(...)
client.task_runs.list(...)
client.tasks.list(...)
client.registries.schedule_run(...)
```

**After**:
Now, you'll need to create clients from the new packages for those specific operations.

```python
from azure.mgmt.containerregistrytasks import ContainerRegistryTasksMgmtClient

# Client for task-related operations
tasks_client = ContainerRegistryTasksMgmtClient(...)
tasks_client.agent_pools.list(...)
tasks_client.runs.list(...)
tasks_client.task_runs.list(...)
tasks_client.tasks.list(...)
tasks_client.registries.schedule_run(...)
```

### 2. Model Import Changes

Similarly, models used by the moved operations must be imported from their new packages.

**Before**:
All models were imported from `azure.mgmt.containerregistry.models`.

```python
from azure.mgmt.containerregistry.models import AgentPool, Run, TaskRun, Task
```

**After**:
Import the moved models from their new locations.

```python
from azure.mgmt.containerregistrytasks.models import AgentPool, Run, TaskRun, Task
```

## Why These Changes?

These changes were made to create a more intuitive and organized SDK. By separating distinct functionalities into their own packages, we aim to:
- Make it easier to find the APIs you need.
- Reduce the size of the `azure-mgmt-containerregistry` package.
- Align with the principle of having smaller, service-focused packages.

If you have any questions or feedback, please open an issue on [GitHub](https://github.com/Azure/azure-sdk-for-python/issues).