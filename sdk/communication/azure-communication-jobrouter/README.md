# Azure Communication JobRouter Package client library for Python

This package contains a Python SDK for Azure Communication Services for JobRouter.
Read more about Azure Communication Services [here](https://docs.microsoft.com/azure/communication-services/overview)

[//]: # ([Source code]&#40;https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter&#41; | [Package &#40;Pypi&#41;]&#40;https://pypi.org/project/azure-communication-sms/&#41; | [API reference documentation]&#40;https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-sms&#41; | [Product documentation]&#40;https://docs.microsoft.com/azure/communication-services/quickstarts/telephony-sms/send?pivots=programming-language-python&#41;)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites

- Python 3.6 or later is required to use this package.
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
- You must have a phone number configured that is associated with an Azure subscription

### Install the package

Install the Azure Communication JobRouter client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-jobrouter
```

## Key concepts

### Job

A Job is a unit of work (demand), which must be routed to an available Worker (supply). A real-world example is an incoming call or chat in the context of a call center.

### Worker

A Worker is the supply available to handle a Job. When you use the SDK to register a Worker to receive jobs, you can specify:

 - One or more queues to listen on.
 - The number of concurrent jobs per Channel that the Worker can handle.
 - A set of Labels that can be used to group and select workers. 

A real-world example is an agent in a call center.

### Queue

A Queue is an ordered list of jobs, that are waiting to be served to a worker. Workers register with a queue to receive work from it.

A real-world example is a call queue in a call center.

### Channel

A Channel is a grouping of jobs by some type. When a worker registers to receive work, they must also specify for which channels they can handle work, and how much of each can they handle concurrently. Channels are just a string discriminator and aren't explicitly created.

Real-world examples are `voice calls` or `chats` in a call center.

### Offer

An Offer is extended by Job Router to a worker to handle a particular job when it determines a match. You can either accept or decline the offer with the JobRouter SDK. If you ignore the offer, it expires according to the time to live configured on the Distribution Policy.

A real-world example is the ringing of an agent in a call center.


### Distribution Policy

A Distribution Policy is a configuration set that controls how jobs in a queue are distributed to workers registered with that queue. This configuration includes:

 - How long an Offer is valid before it expires.
 - The distribution mode, which define the order in which workers are picked when there are multiple available.
 - How many concurrent offers can there be for a given job.

### Labels

You can attach labels to workers, jobs, and queues. Labels are key value pairs that can be of `string`, `number`, or `boolean` data types.

A real-world example is the skill level of a particular worker or the team or geographic location.

### Worker selectors

Worker selectors can be attached to a job in order to target a subset of workers on the queue.

A real-world example is a condition on an incoming call that the agent must have a minimum level of knowledge of a particular product.

### Classification policy

A classification policy can be used to programmatically select a queue, determine job priority, or attach worker label selectors to a job.

### Queue selectors

Queue selectors can be attached to a classification policy in order to target a queue which fulfills certain conditions.
This queue is used enqueueing an incoming job.

A real-world example is a condition on an incoming call that the call has to get queued to a queue which supports `chat`.


### Exception policy

An exception policy controls the behavior of a Job based on a trigger and executes a desired action. The exception policy is attached to a Queue so it can control the behavior of Jobs in the Queue.


## Examples

### Client Initialization
To initialize the SMS Client, the connection string can be used to instantiate.
Alternatively, you can also use Active Directory authentication using DefaultAzureCredential.

```python
from azure.communication.jobrouter import RouterClient
from azure.identity import DefaultAzureCredential

connection_string = "endpoint=ENDPOINT;accessKey=KEY"
router_client = RouterClient.from_connection_string(conn_str = connection_string)

# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
endpoint = "https://<RESOURCE_NAME>.communication.azure.com"
router_client = RouterClient(endpoint, DefaultAzureCredential())
```

### Create or update exception policy

Once the client is initialized, the `upsert_exception_policy` method can be invoked to create or update exception policy.

```python
from azure.communication.jobrouter import (
    RouterClient,
    WaitTimeExceptionTrigger,
    QueueLengthExceptionTrigger,
    CancelExceptionAction,
    ExceptionRule
)

# set `connection_string` to an existing ACS endpoint
connection_string = "endpoint=ENDPOINT;accessKey=KEY"
router_client = RouterClient.from_connection_string(conn_str = connection_string)
print("RouterClient created successfully!")

# define an exception trigger
# set up a QueueLengthExceptionTrigger with a threshold of 10,
# i.e., kick off exception if there are already 10 jobs in a queue
exception_trigger = QueueLengthExceptionTrigger(threshold = 10)

# define an exception action
# this sets up what action to take when an exception trigger condition is fulfilled
# for this scenario, we simply cancel job
exception_action = CancelExceptionAction()

# define the exception rule combining the trigger and action
# you can chain multiple rules together, so it is important to give a unique
# `id` to the exception rule. For this use-case, the exception rule will be the following

exception_rule = {
    "CancelJobWhenQueueThresholdIs10": ExceptionRule(
        trigger = exception_trigger,
        actions = {
            "CancelJobActionWhenQueueIsFull": exception_action
        }
    )
}

# create the exception policy
# set a unique value to `policy_id`
policy_id = "exception_policy"

exception_policy = router_client.upsert_exception_policy(
    identifier = policy_id,
    name = "TriggerJobCancellationWhenQueueLenIs10",
    exception_rules = exception_rule
)

print(f"Exception policy has been successfully created with id: {exception_policy.id}")

# add additional exception rule to policy
new_exception_trigger = WaitTimeExceptionTrigger(threshold = "PT1H")
new_exception_rule = ExceptionRule(
    trigger = new_exception_trigger,
    actions = {
        "CancelJobActionWhenJobInQFor1Hr": exception_action
    }
)
exception_policy.exception_rules["CancelJobWhenInQueueFor1Hr"] = new_exception_rule

updated_exception_policy = router_client.upsert_exception_policy(
    identifier = policy_id,
    exception_policy = exception_policy
)

print(f"Exception policy updated with rules: {[k for k,v in updated_exception_policy.exception_rules.items()]}")
print("Exception policy has been successfully updated")
```

- `identifier`: Id of the exception policy.
- `exception_rules`: (Optional) A dictionary collection of exception rules on the exception policy. Key is the Id of each exception rule.
- `name`: (Optional) An user-friendly name of the policy.
- `exception_policy`: (Optional) An instance of exception policy. If this is provided, then upsert request will be made using this. Generally it is expected to be used when updating an existing policy.

### Get an exception policy

Use `get_exception_policy` to retrieve an existing exception policy.

```python
policy_id = "exception_policy"

exception_policy = router_client.get_exception_policy(identifier = policy_id)

print(f"Successfully fetched exception policy with id: {exception_policy.id}")
```

- `identifier`: Id of the exception policy.

### List exception policies

Use `list_exception_policies` to retrieve a list of exception policies that have been already created.

```python
exception_policy_iterator = router_client.list_exception_policies(results_per_page = 10)

for policy_page in exception_policy_iterator.by_page():
    policies_in_page = list(policy_page)
    print(f"Retrieved {len(policies_in_page)} policies in current page")

    for ep in policies_in_page:
        print(f"Retrieved exception policy with id: {ep.id}")

print(f"Successfully completed fetching exception policies")
```
- `results_per_page`: (Optional) The maximum number of policies to be returned per page.

### Delete an exception policy

Use `delete_exception_policy` to delete an exception policy.

```python
router_client.delete_exception_policy(identifier = policy_id)
```

- `identifier`: Id of the exception policy.

## Next steps
- [Read more about Router in Azure Communication Services][router_concepts]

### More sample code
Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/communication/azure-communication-jobrouter/samples) directory for detailed examples of how to use this library.

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[router_concepts]: https://docs.microsoft.com/azure/communication-services/concepts/router/concepts