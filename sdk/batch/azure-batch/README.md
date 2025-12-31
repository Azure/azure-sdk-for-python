# Microsoft Azure SDK for Python

[Batch][azure_batch] allows users to run large-scale parallel and high-performance computing (HPC) batch jobs efficiently in Azure. To learn more about Azure Batch, please see the [Azure Batch Overview](https://learn.microsoft.com/azure/batch/batch-technical-overview) documentation.

[Source code][batch_source_code]
| [Batch package (PyPI)](https://pypi.org/project/azure-batch)
| [API reference documentation](https://learn.microsoft.com/python/api/overview/azure/batch?view=azure-python)
| [Product documentation](https://learn.microsoft.com/azure/batch)

>Note: v15.x and above is a newer package that has significant changes and improvements from v14.x and below. Please see our migration guide for guidance.

# Getting Started

## Install the package
Install the [azure-batch](https://pypi.org/project/azure-batch) package v15.x or above for the most modern version of the package and [azure-identity](https://pypi.org/project/azure-identity) with [pip](https://pypi.org/project/pip):

```Bash
pip install azure-batch azure-identity
```
[azure-identity](https://pypi.org/project/azure-identity) is used for authentication and is mentioned in the authentication section below.

### Prerequisites
* An Azure subscription. If you don't have one, [create an account for free][azure_sub]
* A [Batch account][azure_batch] with a linked [Storage account][azure_storage]
* Python 3.9 or later. For more details, please see the [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)

### Authenticate the client

>Note: For an asynchronous client, import `azure.batch.aio`'s `BatchClient`

#### Authenticate with Entra ID

We strongly recommend using Microsoft Entra ID for Batch account authentication. Some Batch capabilities require this method of authentication, including many of the security-related features discussed here. The service API authentication mechanism for a Batch account can be restricted to only Microsoft Entra ID using the [allowedAuthenticationModes](https://learn.microsoft.com/rest/api/batchmanagement/batch-account/create?view=rest-batchmanagement-2024-02-01&tabs=HTTP) property. When this property is set, API calls using Shared Key authentication will be rejected.

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
* [Pool Operations](#pool-operations)
  * [Create a pool](#create-a-pool)
  * [Get pool](#get-pool)
  * [List pool](#list-pool)
  * [Delete pool](#delete-pool)
* [Job Operations](#job-operations)
  * [Create a job](#create-a-job)
  * [Get job](#get-job)
  * [List job](#list-job)
  * [Delete job](#delete-job)
* [Job Schedule Operations](#job-schedule-operations)
  * [Create job schedule](#create-job-schedule)
  * [Get job schedule](#get-job-schedule)
  * [List job schedule](#list-job-schedule)
  * [Replace job schedule](#replace-job-schedule)
  * [Update job schedule](#update-job-schedule)
  * [Get job task count](#get-job-task-count)
* [Task Operations](#task-operations)
  * [Create a task](#create-a-task)
  * [Get task](#get-task)
  * [List tasks](#list-tasks)
  * [Delete task](#delete-task)
* [Retrieve output file from task](#retrieve-output-file-from-task)
  * [List task files](#list-task-files)
* [Node Operations](#node-operations)
  * [Get node](#get-node)
  * [List nodes](#list-nodes)
  * [Reboot node](#reboot-node)

## Pool Operations
A pool is the collection of nodes that your application runs on.

Azure Batch pools build on top of the core Azure compute platform. They provide large-scale allocation, application installation, data distribution, health monitoring, and flexible adjustment (scaling) of the number of compute nodes within a pool. For more information, see [Pools in Azure Batch](https://learn.microsoft.com/azure/batch/nodes-and-pools#pools).

### Create a pool

Azure batch has two SDKs, [azure-batch](https://learn.microsoft.com/python/api/overview/azure/batch?view=azure-python) which interacts directly the Azure Batch service, and [azure.mgmt.batch](https://learn.microsoft.com/python/api/azure-mgmt-batch/azure.mgmt.batch?view=azure-python) which interacts with the Azure Resource Manager (otherwise known as ARM). Both of these SDKs support batch pool operations such as create/get/update/list but only the `azure.mgmt.batch` SDK can create a pool with managed identities and for that reason it is the recommend way to create a pool.

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

pool_spec = models.BatchPoolCreateOptions(
    id="my-pool",
    vm_size="standard_d2_v2", 
    target_dedicated_nodes=1,
    virtual_machine_configuration=vm_config
)

client.create_pool(pool=pool_spec)
```

### Get pool
The `get_pool` method can be used to retrieve an already created pool.

```python
my_pool = client.get_pool(my_pool.id)
```

### List pool
The `list_pool` method can be used to list all the pools under a Batch account.

```python
pools = client.list_pools()
```

This method can also be used with filters to specify specific pools that you are looking for:

```python
pools = client.list_pools(
            filter="startswith(id,'batch_abc_')",
            select=["id,state"],
            expand=["stats"],
        )
```

### Delete pool
The `begin_delete_pool` method can be used to delete a pool. This `begin` keyword is an example of our Long Running Operations where an operation that usually executes synchronously will execute asynchronously to avoid connection and load-balancer timeouts. This requires the client to poll the service repeatedly to track progress and completion.

**Synchronous approach** - Wait for the operation to complete:

```python
poller = client.begin_delete_pool(pool_id="my-pool")
result = poller.result()
print(f"Pool deleted successfully")
```

**Asynchronous approach** - Start the operation and check status later:

```python
poller = client.begin_delete_pool(pool_id="my-pool", polling_interval=5)

if poller.done():
    print("Pool deletion completed")
else:
    print("Pool deletion still in progress")
    poller.wait()
```

## Job Operations
A job is a collection of tasks. It manages how computation is performed by its tasks on the compute nodes in a pool.

A job specifies the pool in which the work is to be run. You can create a new pool for each job, or use one pool for many jobs. You can create a pool for each job that is associated with a job schedule, or one pool for all jobs that are associated with a job schedule. For more information see [Job and Tasks in Azure Batch](https://learn.microsoft.com/azure/batch/jobs-and-tasks).

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

### Get job
The `get_job` method retrieves details about a specific job that has already been created.

```python
my_job = client.get_job(job_id="my-job")
```

### List job
The `list_jobs` method lists all jobs under a Batch account.

```python
jobs = client.list_jobs()
```

### Delete job
The `begin_delete_job` method is a Long Running Operation (LRO) that deletes a job asynchronously to avoid connection and load-balancer timeouts.

**Synchronous approach** - Wait for the operation to complete:

```python
poller = client.begin_delete_job(job_id="my-job")
result = poller.result()
print("Job deleted successfully")
```

**Asynchronous approach** - Start the operation and check status later:

```python
poller = client.begin_delete_job(job_id="my-job", polling_interval=5)

if poller.done():
    print("Job deletion completed")
else:
    print("Job deletion still in progress")
    poller.wait()
```

## Job Schedule Operations
Job schedules enable you to create recurring jobs within the Batch service. A job schedule specifies when to run jobs and includes the specifications for the jobs to be run. You can specify the duration of the schedule (how long and when the schedule is in effect) and how frequently jobs are created during the scheduled period. For more information, see [Scheduled Jobs in Azure Batch](https://learn.microsoft.com/en-us/azure/batch/jobs-and-tasks#scheduled-jobs).

### Create job schedule
The `create_job_schedule` method creates a new job schedule that automatically creates jobs based on the specified schedule.

```python
from azure.batch import BatchClient, models
from azure.core.credentials import AzureNamedKeyCredential

credentials = AzureNamedKeyCredential(account_name, account_key)
client = BatchClient(endpoint=batch_account_endpoint, credential=credentials)

schedule_spec = models.BatchJobScheduleCreateOptions(
    id="my-job-schedule",
    schedule = models.BatchJobScheduleConfiguration(
        start_window=datetime.timedelta(hours=1),
        recurrence_interval=datetime.timedelta(days=1),
    )
    job_specification=models.BatchJobSpecification(
        pool_info=models.BatchPoolInfo(pool_id="my-pool")
    )
)

client.create_job_schedule(job_schedule=schedule_spec)
```

### Get job schedule
The `get_job_schedule` method retrieves details about a specific job schedule.

```python
my_schedule = client.get_job_schedule(job_schedule_id="my-job-schedule")
```

### List job schedule
The `list_job_schedules` method lists all job schedules under a Batch account.

```python
schedules = client.list_job_schedules()
```

### Replace job schedule
The `replace_job_schedule` method replaces the entire job schedule configuration with new values.

```python
schedule_replace = models.BatchJobSchedule(
    schedule=models.BatchJobScheduleConfiguration(
        recurrence_interval=datetime.timedelta(hours=10)
    ),
    job_specification=models.BatchJobSpecification(
        pool_info=models.BatchPoolInfo(pool_id="my-pool")
    )
)

client.replace_job_schedule(
    job_schedule_id="my-job-schedule",
    job_schedule=schedule_replace
)
```

### Update job schedule
The `update_job_schedule` method updates specific properties of an existing job schedule without replacing the entire configuration.

```python
schedule_update = models.BatchJobScheduleUpdateOptions(
    schedule=models.BatchJobScheduleConfiguration(
        recurrence_interval=datetime.timedelta(hours=5)
    )
)

client.update_job_schedule(
    job_schedule_id="my-job-schedule",
    job_schedule=schedule_update
)
```

### Get job task count
The `get_job_task_counts` method provides summary counts of tasks in different states for a specific job, including active, running, and completed tasks.

```python
task_counts = client.get_job_task_counts(job_id="my-job")

print(f"Completed tasks: {task_counts.completed}")
print(f"Succeeded tasks: {task_counts.succeeded}")
print(f"Failed tasks: {task_counts.failed}")
```

## Task Operations
A task is a unit of computation that is associated with a job. It runs on a node. Tasks are assigned to a node for execution, or are queued until a node becomes free. Put simply, a task runs one or more programs or scripts on a compute node to perform the work you need done. For more information, see [Jobs and Tasks in Azure Batch](https://learn.microsoft.com/azure/batch/jobs-and-tasks).

### Create a task
There are three ways that a task can be created using this package. This first example shows how to create a single task on a job using `create_task` with the parameter type `BatchTaskCreateOptions`.

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

This second example demonstrates creating multiple tasks in a group using `BatchTaskGroup` with the `create_task_collection` method. A `BatchTaskGroup` can contain up to 100 tasks.

```python
task1 = models.BatchTaskCreateOptions(id="task1", command_line='cmd /c "echo hello world"')
task2 = models.BatchTaskCreateOptions(id="task2", command_line='cmd /c "echo hello world"')
task3 = models.BatchTaskCreateOptions(id="task3", command_line='cmd /c "echo hello world"')

task_group = models.BatchTaskGroup(values_property=[task1, task2, task3])
result = client.create_task_collection(job_id="my-job", task_collection=task_group)
```

Finally, you can use `create_tasks` for creating multiple tasks with no limit. This method will package up the list of `BatchTaskCreateOptions` tasks passed in and repeatly call the `create_task_collection` method with groups of tasks bundled into `BatchTaskGroup` objects. This utility method allows you to select the number of parallel calls to the `create_task_collection` method.

```python
tasks_to_add = []
for i in range(1000):
    task = models.BatchTaskCreateOptions(
        id=task_id + str(i),
        command_line='cmd /c "echo hello world"',
    )
    tasks_to_add.append(task)
result = client.create_tasks(job_id="my-job", task_collection=tasks_to_add)
```

### Get task
The `get_task` method retrieves details about a specific task.

```python
my_task = client.get_task(job_id="my-job", task_id="my-task")
```

### List tasks
The `list_tasks` method lists all tasks associated with a specific job.

```python
tasks = client.list_tasks(job_id="my-job")
```

### Delete task
The `delete_task` method deletes a task from a job.

```python
client.delete_task(job_id="my-job", task_id="my-task")
```

## Retrieve output file from task

In Azure Batch, each task has a working directory under which it can create files and directories. This working directory can be used for storing the program that is run by the task, the data that it processes, and the output of the processing it performs. All files and directories of a task are owned by the task user.

The Batch service exposes a portion of the file system on a node as the root directory. This root directory is located on the temporary storage drive of the VM, not directly on the OS drive. For more information, see [Files and Directories in Azure Batch](https://learn.microsoft.com/en-us/azure/batch/files-and-directories).

### List task files
List all files available in a task's directory using the `list_task_files` method:

```python
all_files = client.list_task_files(job_id="my-job", task_id="my-task")
only_files = [f for f in all_files if not f.is_directory]

for file in only_files:
    print(f"File: {file.name}")
```

## Node Operations
A node is an Azure virtual machine (VM) or cloud service VM that is dedicated to processing a portion of your application's workload. The size of a node determines the number of CPU cores, memory capacity, and local file system size that is allocated to the node. For more information, please see [Nodes and Pools in Azure Batch](https://learn.microsoft.com/en-us/azure/batch/nodes-and-pools#nodes).

### Get node
The `get_node` method retrieves details about a specific compute node in a pool.

```python
node = client.get_node(pool_id="my-pool", node_id="node1")

print(f"Node state: {node.state}")
print(f"Scheduling state: {node.scheduling_state}")
print(f"Node agent version: {node.node_agent_info.version}")
```

### List nodes
The `list_nodes` method lists all compute nodes in a specific pool.

```python
nodes = client.list_nodes(pool_id="my-pool")

for node in nodes:
    print(f"Node ID: {node.id}, State: {node.state}")
```

### Reboot node
The `begin_reboot_node` method is a Long Running Operation (LRO) that reboots a compute node in a pool. You can specify the reboot kind to control how running tasks are handled during the reboot.

**Synchronous approach** - Wait for the reboot to complete:

```python
poller = client.begin_reboot_node(
    pool_id="my-pool",
    node_id="node1",
    models.BatchNodeRebootOptions(
        node_reboot_kind=models.BatchNodeRebootKind.TERMINATE
    )
)
result = poller.result()
print("Node rebooted successfully")
```

**Asynchronous approach** - Start the reboot and check status later:

```python
poller = client.begin_reboot_node(
    pool_id="my-pool",
    node_id="node1",
    models.BatchNodeRebootOptions(
        node_reboot_kind=models.BatchNodeRebootKind.REQUEUE
    ),
    polling_interval=5
)

if poller.done():
    print("Node reboot completed")
else:
    print("Node reboot still in progress")
    poller.wait()
```

# Error Handling
We adopted the Azure Core exception framework, which provides a variety of exception types that map directly to HTTP status codes and common error scenarios. The base `HttpResponseError` is the foundation, with specialized exceptions like `ClientAuthenticationError`, `ResourceNotFoundError`, `ResourceExistsError`, and more providing specific error categorization. This system also provides direct access to HTTP status codes, response headers, and request information.

```python
from azure.batch import BatchClient
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)

try:
    client = BatchClient(endpoint, credentials)
    pools = client.list_pools()
except ResourceNotFoundError as not_found_error:
    print(f"Service could not find resource {not_found_error.status_code}: {not_found_error.error.message.value}")
    create_missing_resource()
except HttpResponseError as error:
    print(f"HTTP Status: {error.status_code}")
    print(f"Error Code: {error.error.code}")
    print(f"Message: {error.error.message.value}")
```

# Usage

>**Note:** Comprehensive code samples for the v15.x package are currently in development and will be available soon. In the meantime, the examples provided throughout this README demonstrate common operations for the latest version.

For code examples using the v14.x package, see [the Batch samples repo](https://github.com/Azure/azure-batch-samples/tree/master/Python)
on GitHub or see [Batch](https://docs.microsoft.com/python/api/overview/azure/batch)
on docs.microsoft.com.


# Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project.


<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free
[azure_batch]: https://azure.microsoft.com/products/batch
[azure_storage]: https://azure.microsoft.com/products/category/storage

[batch_source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/batch/azure-batch