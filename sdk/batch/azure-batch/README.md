# Microsoft Azure SDK for Python

[Batch][azure_batch] allows users to run large-scale parallel and high-performance computing (HPC) batch jobs efficiently in Azure. To learn more about Azure Batch, please see the [Azure Batch Overview](https://learn.microsoft.com/en-us/azure/batch/batch-technical-overview) documentation.

[Source code][batch_source_code]
| [Batch package (PyPI)][pypi_batch]
| [API reference documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/batch?view=azure-python)
| [Product documentation](https://learn.microsoft.com/en-us/azure/batch/)

>Note: v15.x and above is a newer package that has significant changes and improvements from v14.x and below. Please see our migration guide for guidance.

# Getting Started

## Install the package
Install the [azure-batch](pypi_batch) package v15.x or above for the most modern version of the package and [azure-identity](pypi_identity) with [pip](https://pypi.org/project/pip/):

```Bash
pip install azure-batch azure-identity
```
[azure-identity](pypi_identity) is used for authentication and is mentioned in the authentication section below.

### Prerequisites
* An Azure subscription. If you don't have one, [create an account for free][azure_sub]
* A [Batch account][azure_batch] with a linked [Storage account][azure_storage]
* Python 3.9 or later. For more details, please see the [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)

### Authenticate the client

>Note: For an asynchronous client, import `azure.batch.aio`'s `BatchClient`

#### Authenticate with Entra ID

We strongly recommend using Microsoft Entra ID for Batch account authentication. Some Batch capabilities require this method of authentication, including many of the security-related features discussed here. The service API authentication mechanism for a Batch account can be restricted to only Microsoft Entra ID using the [allowedAuthenticationModes](https://learn.microsoft.com/en-us/rest/api/batchmanagement/batch-account/create?view=rest-batchmanagement-2024-02-01&tabs=HTTP) property. When this property is set, API calls using Shared Key authentication will be rejected.

Azure Batch provides integration with Microsoft Entra ID for identity-based authentication of requests. With Azure AD, you can use role-based access control (RBAC) to grant access to your Azure Batch resources to users, groups, or applications. The [Azure Identity](https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/identity/Azure.Identity/README.md) library provides easy Microsoft Entra ID support for authentication.

```python
from azure.identity import DefaultAzureCredential
from azure.batch import BatchClient

credentials = DefaultAzureCredential()
client = BatchClient(
    endpoint='https://<your account>.eastus.batch.azure.com',
    credential=credentials
)
```

#### Authenticate with Shared Key Credentials

You can also use Shared Key authentication to sign into your Batch account. This method uses your Batch account access keys to authenticate Azure commands for the Batch service. 

```python
from azure.core.credentials import AzureNamedKeyCredential
from azure.batch import BatchClient

credentials = AzureNamedKeyCredential(account_name, account_key)
client = BatchClient(
    endpoint='https://<your account>.eastus.batch.azure.com',
    credential=credentials
)
```

# Examples

This section contains code snippets covering common Azure Batch operations:
* [Create a pool](#create-a-pool)
* [Create a job](#create-a-job) 
* [Submit a task](#submit-a-task)

## Pool Operations
A pool is the collection of nodes that your application runs on.

Azure Batch pools build on top of the core Azure compute platform. They provide large-scale allocation, application installation, data distribution, health monitoring, and flexible adjustment (scaling) of the number of compute nodes within a pool. For more information, see [Pools in Azure Batch](https://learn.microsoft.com/en-us/azure/batch/nodes-and-pools#pools).

### Create a pool

Azure batch has two SDKs, [azure-batch](https://learn.microsoft.com/en-us/python/api/overview/azure/batch?view=azure-python) which interacts directly the Azure Batch service, and [azure.mgmt.batch](https://learn.microsoft.com/en-us/python/api/azure-mgmt-batch/azure.mgmt.batch?view=azure-python) which interacts with the Azure Resource Manager (otherwise known as ARM). Both of these SDKs support batch pool operations such as create/get/update/list but only the `azure.mgmt.batch` SDK can create a pool with managed identities and for that reason it is the recommend way to create a pool.

This first snippet is an example of using `azure.mgmt.batch` to create a pool with managed identity. A more detailed usage of this method of creating a pool can be found in this [create pool sample](https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/batch/manage_pool.py).

```python
pool = batch_client.pool.create(
        GROUP_NAME,
        ACCOUNT,
        POOL,
        {
            "properties": {
                "vmSize": "STANDARD_D4",
                "deploymentConfiguration": {
                    "virtualMachineConfiguration": {
                        "imageReference": {
                            "publisher": "Canonical",
                            "offer": "UbuntuServer",
                            "sku": "18.04-LTS",
                            "version": "latest"
                        },
                        "nodeAgentSkuId": "batch.node.ubuntu 18.04"
                    }
                },
                "scaleSettings": {
                    "autoScale": {
                        "formula": "$TargetDedicatedNodes=1",
                        "evaluationInterval": "PT5M"
                    }
                }
            },

            "identity": {
                "type": "UserAssigned",
                "userAssignedIdentities": {
                    "/subscriptions/"+SUBSCRIPTION_ID+"/resourceGroups/"+GROUP_NAME+"/providers/Microsoft.ManagedIdentity/userAssignedIdentities/"+"Your Identity Name": {}
                }
            
            }
        }
)
```

This second snippet is using `azure-batch` for pool creation, without any support for managed identities. This example demonstrates creating a `client` using credentials and then creating the pool with `BatchPoolCreateOptions`.

```python
from azure.batch import BatchClient, models
from azure.core.credentials import AzureNamedKeyCredential

credentials = AzureNamedKeyCredential(account_name, account_key)
client = BatchClient(endpoint=batch_account_endpoint, credential=credentials)

vm_config = models.VirtualMachineConfiguration(
    image_reference=models.BatchVmImageReference(
        publisher="MicrosoftWindowsServer",
        offer="WindowsServer",
        sku="2016-Datacenter-smalldisk"
    ),
    node_agent_sku_id="batch.node.windows amd64"
)

my_pool = models.BatchPoolCreateOptions(
    id="my-pool",
    vm_size="standard_d2_v2", 
    target_dedicated_nodes=1,
    virtual_machine_configuration=vm_config
)

client.create_pool(pool=my_pool)
```

## Job Operations
A job is a collection of tasks. It manages how computation is performed by its tasks on the compute nodes in a pool.

A job specifies the pool in which the work is to be run. You can create a new pool for each job, or use one pool for many jobs. You can create a pool for each job that is associated with a job schedule, or one pool for all jobs that are associated with a job schedule. For more information see [Job and Tasks in Azure Batch](https://learn.microsoft.com/en-us/azure/batch/jobs-and-tasks).

### Create a Job
Create a job that will contain and manage your tasks. Jobs are associated with a specific pool.

```python
from azure.batch import BatchClient, models
from azure.core.credentials import AzureNamedKeyCredential

credentials = AzureNamedKeyCredential(account_name, account_key)
client = BatchClient(endpoint=batch_account_endpoint, credential=credentials)

job_spec = models.BatchJobCreateOptions(
    id="my-job",
    pool_info=models.BatchPoolInfo(pool_id="my-pool")
)

client.create_job(job=job_spec)
```

## Task Operations
A task is a unit of computation that is associated with a job. It runs on a node. Tasks are assigned to a node for execution, or are queued until a node becomes free. Put simply, a task runs one or more programs or scripts on a compute node to perform the work you need done. For more information, see [Jobs and Tasks in Azure Batch](https://learn.microsoft.com/en-us/azure/batch/jobs-and-tasks).

### Submit a task
Submit a task to run within the job. This example runs a simple shell command.

```python
from azure.batch import BatchClient, models
from azure.core.credentials import AzureNamedKeyCredential

credentials = AzureNamedKeyCredential(account_name, account_key)
client = BatchClient(endpoint=batch_account_endpoint, credential=credentials)

task_spec = models.BatchTaskCreateOptions(
    id="my-task",
    command_line='cmd /c "echo Hello World"'
)

client.create_task(job_id="my-job", task=task_spec)
```


# Usage

For code examples, see [the Batch samples repo](https://github.com/Azure/azure-batch-samples/tree/master/Python)
on GitHub or see [Batch](https://docs.microsoft.com/python/api/overview/azure/batch)
on docs.microsoft.com.


# Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project.


<!-- LINKS -->
[pypi_batch]: https://pypi.org/project/azure-batch/
[pypi_identity]: https://pypi.org/project/azure-identity/

[azure_sub]: https://azure.microsoft.com/free/
[azure_batch]: https://azure.microsoft.com/en-us/products/batch
[azure_storage]: https://azure.microsoft.com/en-us/products/category/storage

[batch_source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/batch/azure-batch