# Azure Batch Data Plane Migration Guide from <= v14.x to v15.x

This guide assists you in the migration from [azure-batch](https://pypi.org/project/azure-batch/) v14.x to [azure-batch](https://pypi.org/project/azure-batch/15.0.0b1/) v15.x. Side-by-side comparisons are provided for similar operations between the two packages.

Familiarity with the `azure-batch` v14.x package is assumed. If you're new to the Azure Batch client library for Python, see the [README for `azure-batch`](https://learn.microsoft.com/python/api/overview/azure/batch?view=azure-python) and samples instead of this guide.

## Table of Contents

- [Overview](#overview)
    - [Migration Benefits](#migration-benefits)
    - [Package Differences](#package-differences)
- [Constructing the Clients](#constructing-the-clients)
    - [Authenticate with Entra ID](#authenticate-with-entra-id)
    - [Authenticate with Shared Key Credentials](#authenticate-with-shared-key-credentials)
- [Error Handling](#error-handling)
- [Operation Examples](#operation-examples)
    - [Create Pool](#create-pool)
    - [Create Jobs](#create-jobs)
    - [Submit Tasks](#submit-tasks)

## Overview

### Migration Benefits

> Note: `azure-batch` `<= v14.x` have been deprecated. Please upgrade to `azure-batch` `v15.x` for continued support.

A natural question to ask when considering whether to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we've focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

Several areas of consistent feedback were expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services haven't had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was too steep. The APIs didn't offer an approachable and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines.

The new Batch version `v15.x` provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as using the new Azure.Identity library to share a single authentication between clients and a unified diagnostics pipeline offering a common view of the activities across each of the client libraries.

We strongly encourage moving to `azure-batch` `v15.x`. It is important to be aware that any version `<= v14.x` is officially deprecated. Though they will continue to be supported with critical security and bug fixes, they are no longer under active development and will not receive new features or minor fixes. There is no guarantee of feature parity between versions below `v14.x` and `v15.x`.

### Package Differences

The Azure Batch Python SDK has gone through significant architectural changes between v14.x and v15.x

| v14.x                           | v15.x                     | Change               |
| ------------------------------- | ------------------------- | -------------------- |
| `azure.batchBatchServiceClient` | `azure.batch.BatchClient` | Client class renamed | 
| `azure.batch.operations.*Operations` | Operations integrated into `BatchClient` | Operations consolidated |
| `azure.batch.models.*`          | `azure.batch.models.*`    | Models namespace remains the same |

Many model classes have been renamed to have `Batch` as the prefix for consistency. The table below has a few example of these changes:

| v14.x Model | v15.x Model |
| ----------- | ----------- |
| CloudPool   | BatchPool   |
| CloudJob    | BatchJob    |
| CloudTask   | BatchTask   |
| ComputeNode | BatchNode   |
| PoolSpecification | BatchPoolSpecification |
| JobSpecification  | BatchJobSpecification  |

## Constructing the Clients

### Authenticate with Entra ID

We strongly recommend using Microsoft Entra ID for Batch account authentication, as some Batch capabilities require this authentication method, particularly security-related features.

Previously in v14.x, to create a `BatchServiceClient` developers would rely on the `ServicePrincipalCredentials` class from `azure.common.credentials`:

```python
# v14.x - Service Principal Authentication
from azure.common.credentials import ServicePrincipalCredentials
from azure.batch import BatchServiceClient

credentials = ServicePrincipalCredentials(
    client_id='your-client-id',
    secret='your-client-secret',
    tenant='your-tenant-id',
    resource='https://batch.core.windows.net/'
)

client = BatchServiceClient(credentials, 'https://<your account>.eastus.batch.azure.com')
```

Now, the v15.x approach consolidates all authentication scenarios under the [Azure Identity library](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md), using a modern `BatchClient` class that aligns with the current Azure SDK design guidelines. The most significant improvement is the elimination of manual resource specification requirements and the introduction of automatic credential discovery through `DefaultAzureCredential`:

```python
# v15.x - Azure Identity Authentication  
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.batch import BatchClient

credentials = DefaultAzureCredential()
client = BatchClient(
    endpoint='https://<your account>.eastus.batch.azure.com',
    credential=credentials
)
```

### Authenticate with Shared Key Credentials

For scenarios where shared key authentication is still required, v15.x uses the standardized `AzureNamedKeyCredential` from `azure-core` instead of the batch-specific implementation:

```python
# v15.x - Shared Key Authentication
from azure.core.credentials import AzureNamedKeyCredential
from azure.batch import BatchClient

credentials = AzureNamedKeyCredential(account_name, account_key)
client = BatchClient(
    endpoint='https://<your account>.eastus.batch.azure.com',
    credential=credentials
)
```

## Error Handling

The error handling has been updated, moving from custom Batch-specific exception handling to a more standardized Azure Core exception handling process. This change helps bring consistency across Azure services and provides the same error information for debugging and troubleshooting.

In version v15.x, we adopt the Azure Core exception framework, which provides a variety of exception types that map directly to HTTP status codes and common error scenarios. The base `HTTPResponseError` is the foundation, wich specialized exceptions like `ClientAuthenticationError`, `ResourceNotFoundError`, `ResourceExistsError`, and more, providing more specific error categorization. This system also provides direct access to HTTP status codes, response headers, and request information which we didn't have before.

```python
# v15.x - Standardized Azure Exceptions
from azure.batch import BatchClient
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)

try:
    client = BatchClient(endpoint, credentials)
    pools = client.list_pools()
except ResourceNotFoundError as not_found_error:
    # 404 resource not found
    print(f"Service could not find resource {not_found_error.status_code}: {not_found_error.error.message.value}")
    create_missing_resource()
except HttpResponseError as error:
    # Other HTTP errors with detailed information
    print(f"HTTP Status: {error.status_code}")
    print(f"Error Code: {error.error.code}")
    print(f"Message: {error.error.message.value}")
```

In versions v14.x and below, we used a `BatchErrorException` class to do custom error handling. When operations failed, `BatchErrorException` would be caught and we'd access error details through nested properties for the error code and message. The error structure was primarily focuzed on Batch service-specific information without direct access to the underlying HTTP details.

```python
# v14.x - Custom Batch Exceptions
from azure.batch.batch_service_client import BatchServiceClient
from azure.batch.models import BatchErrorException

try:
    client = BatchServiceClient(credentials, batch_url)
    pools = client.pool.list()
except BatchErrorException as error:
    print(f"Batch Error: {error.error.code}")
    print(f"Message: {error.error.message}")
```


## Operation Examples

The operations for `azure-batch` have moved from a compartmentalized approach with separate operation classes to a unified client interface that consolidates all functionality. In v14.x, developers needed to use specific operation classes like `PoolOperations`, `JobOperations`, and `TaskOperations`, each accessed as properties of the main BatchServiceClient (e.g., `client.pool.add()`, `client.job.create()`, `client.task.add()`). This required familiarity with the specific organizational structure of the Azure Batch SDK. In v15.x, this is simplified by integrating all operations directly into the main BatchClient. Now, method names like `create_pool()`, `create_job()`, and `create_task()` directly reflect the intended action.

### Create Pool

Previously in v14.x, pool creation was handled through a `PoolOperations` class that was accessed as a property of the main `BatchServiceClient`. The pool specifications would be made using the `CloudPool` model, a deprecated naming pattern. 

```python
# v14.x - Pool Creation
from azure.batch import BatchServiceClient
from azure.batch.models import CloudPool, VirtualMachineConfiguration, ImageReference

client = BatchServiceClient(credentials, batch_url)

vm_config = VirtualMachineConfiguration(
    image_reference=ImageReference(
        publisher="MicrosoftWindowsServer",
        offer="WindowsServer", 
        sku="2016-Datacenter-smalldisk"
    ),
    node_agent_sku_id="batch.node.windows amd64"
)

pool_spec = CloudPool(
    id="my-pool",
    vm_size="standard_d2_v2",
    target_dedicated_nodes=1,
    virtual_machine_configuration=vm_config
)

client.pool.add(pool_spec)
```

Now in v15.x, the `BatchPoolCreateOptions` model replaced the `CloudPool` model. There is a consistent use of the "Batch" prefix for our model names throughout the v15.x API. 

```python
# v15.x - Pool Creation  
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

### Create Jobs

Previously in v14.x, job creation was handeled through the `JobOperations` class and used the `CloudJob` model. 

```python
# v14.x - Job Creation
from azure.batch import BatchServiceClient
from azure.batch.models import CloudJob, PoolInformation

client = BatchServiceClient(credentials, batch_url)

pool_info = PoolInformation(pool_id="my-pool")

job_spec = CloudJob(
    id="my-job",
    pool_info=pool_info
)

client.job.add(job_spec)
```

Now in v15.x, `BatchJobCreateOptions` replaces the deprecated `CloudJob` model while maintaining the consistent "Batch" prefix that is used through the new API. Creating the job can be done by calling the `create_job()` method on `BatchClient`.

```python
# v15.x - Job Creation  
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

### Submit Tasks

Previously in v14.x, task submission was handled through the `TaskOperations` class and used the `CloudTask` model. Tasks were added to jobs using the `add()` method through the task operations.

```python
# v14.x - Task Submission
from azure.batch import BatchServiceClient
from azure.batch.models import CloudTask

client = BatchServiceClient(credentials, batch_url)

task_spec = CloudTask(
    id="my-task",
    command_line='cmd /c "echo Hello World"'
)

client.task.add(job_id="my-job", task=task_spec)
```

Now in v15.x, `BatchTaskCreateOptions` replaces the deprecated `CloudTask` model, maintaining the consistent "Batch" prefix used throughout the API. Tasks are now submitted using the `create_task()` method directly on the `BatchClient`.

```python
# v15.x - Task Submission
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

The v15.x API also supports efficient bulk task submission through the `create_tasks()` method, which allows you to submit multiple tasks at once with optional concurrency control for improved performance:

```python
# v15.x - Bulk Task Submission
from azure.batch import BatchClient, models

tasks = []
for i in range(10):
    task_spec = models.BatchTaskCreateOptions(
        id=f"task-{i}",
        command_line=f'cmd /c "echo Processing item {i}"'
    )
    tasks.append(task_spec)

result = client.create_tasks(
    job_id="my-job", 
    task_collection=tasks,
    concurrencies=4  # Use 4 parallel threads for submission
)
```

This bulk submission approach is more efficient than submitting tasks individually and provides better error handling and retry capabilities for large-scale task creation scenarios.
