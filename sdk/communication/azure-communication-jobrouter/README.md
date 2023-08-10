# Azure Communication JobRouter Package client library for Python

This package contains a Python SDK for Azure Communication Services for JobRouter.
Read more about Azure Communication Services [here][product_docs]

[Source code][source] | [Package (Pypi)][pypi] | [Product documentation][product_docs]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites
You need an [Azure subscription][azure_sub] and a [Communication Service Resource][communication_resource_docs] to use this package.

- Python 3.7 or later is required to use this package. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).
- To create a new Communication Service, you can use the [Azure Portal][communication_resource_create_portal], the [Azure PowerShell][communication_resource_create_power_shell]

### Install the package

Install the Azure Communication JobRouter client library for Python with [pip][pip]:

```bash
pip install azure-communication-jobrouter
```

## Key concepts

### Job
A Job represents the unit of work, which needs to be routed to an available Worker.
A real-world example of this may be an incoming call or chat in the context of a call center.

### Worker
A Worker represents the supply available to handle a Job. Each worker registers with or more queues to receive jobs.
A real-world example of this may be an agent working in a call center.

### Queue
A Queue represents an ordered list of jobs waiting to be served by a worker.  Workers will register with a queue to receive work from it.
A real-world example of this may be a call queue in a call center.

## Channel
A Channel represents a grouping of jobs by some type.  When a worker registers to receive work, they must also specify for which channels they can handle work, and how much of each can they handle concurrently.
A real-world example of this may be `voice calls` or `chats` in a call center.

### Offer
An Offer is extended by JobRouter to a worker to handle a particular job when it determines a match, this notification is normally delivered via [EventGrid][subscribe_events].  The worker can either accept or decline the offer using th JobRouter API, or it will expire according to the time to live configured on the distribution policy.
A real-world example of this may be the ringing of an agent in a call center.

### Distribution Policy
A Distribution Policy represents a configuration set that governs how jobs in a queue are distributed to workers registered with that queue.
This configuration includes how long an Offer is valid before it expires and the distribution mode, which define the order in which workers are picked when there are multiple available.

#### Distribution Mode
The 3 types of modes are
- **Round Robin**: Workers are ordered by `Id` and the next worker after the previous one that got an offer is picked.
- **Longest Idle**: The worker that has not been working on a job for the longest.
- **Best Worker**: You can specify an expression to compare 2 workers to determine which one to pick.

### Labels
You can attach labels to workers, jobs and queues.  These are key value pairs that can be of `string`, `number` or `boolean` data types.
A real-world example of this may be the skill level of a particular worker or the team or geographic location.

### Label Selectors
Label selectors can be attached to a job in order to target a subset of workers serving the queue.
A real-world example of this may be a condition on an incoming call that the agent must have a minimum level of knowledge of a particular product.

### Classification policy
A classification policy can be used to dynamically select a queue, determine job priority and attach worker label selectors to a job by leveraging a rules engine.

### Exception policy
An exception policy controls the behavior of a Job based on a trigger and executes a desired action. The exception policy is attached to a Queue so it can control the behavior of Jobs in the Queue.

## Examples

### Client Initialization
To initialize the SMS Client, the connection string can be used to instantiate.
Alternatively, you can also use Active Directory authentication using DefaultAzureCredential.

```python
from azure.communication.jobrouter import (
    JobRouterClient,
    JobRouterAdministrationClient
)

connection_string = "endpoint=ENDPOINT;accessKey=KEY"
router_client = JobRouterClient.from_connection_string(conn_str = connection_string)
router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
```

### Distribution Policy
Before we can create a Queue, we need a Distribution Policy.

```python
from azure.communication.jobrouter import (
    LongestIdleMode,
    DistributionPolicy
)

distribution_policy: DistributionPolicy = DistributionPolicy(
    offer_expires_after_seconds = 24 * 60 * 60,
    mode = LongestIdleMode(
        min_concurrent_offers = 1,
        max_concurrent_offers = 1
    )
)

distribution_policy: DistributionPolicy = router_admin_client.create_distribution_policy(
    distribution_policy_id = "distribution-policy-1",
    distribution_policy = distribution_policy
)
```
### Queue
Next, we can create the queue.

```python
from azure.communication.jobrouter import (
    RouterQueue
)

queue: RouterQueue = RouterQueue(
    distribution_policy_id = "distribution-policy-1"
)

queue: RouterQueue = router_admin_client.create_queue(
    queue_id = "queue-1",
    queue = queue
)
```

### Job
Now, we can submit a job directly to that queue, with a worker selector the requires the worker to have the label `Some-Skill` greater than 10.
```python
from azure.communication.jobrouter import (
    RouterJob,
    RouterWorkerSelector,
    LabelOperator
)

router_job: RouterJob = RouterJob(
    channel_id = "my-channel",
    queue_id = "queue-1",
    channel_reference = "12345",
    priority = 1,
    requested_worker_selectors = [
        RouterWorkerSelector(key = "Some-Skill", label_operator = LabelOperator.EQUAL, value = 10)
    ]
)

job: RouterJob = router_client.create_job(
    job_id = "jobId-1",
    router_job = router_job
)
```

### Worker
Now, we register a worker to receive work from that queue, with a label of `Some-Skill` equal to 11.
```python
from azure.communication.jobrouter import (
    RouterWorker,
    ChannelConfiguration
)

router_worker: RouterWorker = RouterWorker(
    total_capacity = 1,
    queue_assignments = {
        "queue-1": {}
    },
    labels = {
        "Some-Skill": 11
    },
    channel_configurations = {
        "my-channel": ChannelConfiguration(capacity_cost_per_job = 1)
    },
    available_for_offers = True
)

worker = router_client.create_worker(
    worker_id = "worker-1",
    router_worker = router_worker
)
```

### Offer
We should get a [RouterWorkerOfferIssued][offer_issued_event_schema] from our [EventGrid subscription][subscribe_events].

There are several different Azure services that act as a [event handler][event_grid_event_handlers].
For this scenario, we are going to assume Webhooks for event delivery. [Learn more about Webhook event delivery][webhook_event_grid_event_delivery]

Once events are delivered to the event handler, we can deserialize the JSON payload into a list of events.

```python
# Parse the JSON payload into a list of events
from azure.eventgrid import EventGridEvent
import json

## deserialize payload into a list of typed Events
events = [EventGridEvent.from_json(json.loads(msg)) for msg in payload]
```

```python
offer_id = ""
for event in events:
    if event.event_type == "Microsoft.Communication.RouterWorkerOfferIssued":
        offer_id = event.data.offer_id
    else:
        continue
```

However, we could also wait a few seconds and then query the worker directly against the JobRouter API to see if an offer was issued to it.
```python
from azure.communication.jobrouter import (
    RouterWorker,
)

router_worker: RouterWorker = router_client.get_worker(worker_id = "worker-1")

for offer in router_worker.offers:
    print(f"Worker {router_worker.id} has an active offer for job {offer.job_id}")
```
### Accept an offer
Once a worker receives an offer, it can take two possible actions: accept or decline. We are going to accept the offer.
```python
from azure.communication.jobrouter import (
    RouterJobOffer,
    AcceptJobOfferResult,
    RouterJobStatus
)

# fetching the offer id
job_offer: RouterJobOffer = [offer for offer in router_worker.offers if offer.job_id == "jobId-1"][0]
offer_id = job_offer.offer_id

# accepting the offer sent to `worker-1`
accept_job_offer_result: AcceptJobOfferResult = router_client.accept_job_offer(
    worker_id = "worker-1",
    offer_id = offer_id
)

print(f"Offer: {job_offer.offer_id} sent to worker: {router_worker.id} has been accepted")
print(f"Job has been assigned to worker: {router_worker.id} with assignment: {accept_job_offer_result.assignment_id}")

# verify job assignment is populated when querying job
updated_job = router_client.get_job(job_id = "jobId-1")
print(f"Job assignment has been successful: {updated_job.job_status == RouterJobStatus.Assigned and accept_job_offer_result.assignment_id in updated_job.assignments}")
```

### Completing a job
Once the worker is done with the job, the worker has to mark the job as `completed`.
```python
import datetime

complete_job_result = router_client.complete_job(
    job_id = "jobId-1",
    assignment_id = accept_job_offer_result.assignment_id,
    note = f"Job has been completed by {router_worker.id} at {datetime.datetime.utcnow()}"
)

print(f"Job has been successfully completed.")
```

### Closing a job
After a job has been completed, the worker can perform wrap up actions to the job before closing the job and finally releasing its capacity to accept more incoming jobs
```python
from azure.communication.jobrouter import (
    RouterJob,
    RouterJobStatus
)

close_job_result = router_client.close_job(
    job_id = "jobId-1",
    assignment_id = accept_job_offer_result.assignment_id,
    note = f"Job has been closed by {router_worker.id} at {datetime.datetime.utcnow()}"
)

print(f"Job has been successfully closed.")

update_job: RouterJob = router_client.get_job(job_id = "jobId-1")
print(f"Updated job status: {update_job.job_status == RouterJobStatus.CLOSED}")
```

```python
import time
from datetime import datetime, timedelta
from azure.communication.jobrouter import (
    RouterJob,
    RouterJobStatus
)

close_job_in_future_result = router_client.close_job(
    job_id = "jobId-1",
    assignment_id = accept_job_offer_result.assignment_id,
    note = f"Job has been closed by {router_worker.id} at {datetime.utcnow()}",
    close_at = datetime.utcnow() + timedelta(seconds = 2)
)

print(f"Job has been marked to close")
time.sleep(secs = 2)
update_job: RouterJob = router_client.get_job(job_id = "jobId-1")
print(f"Updated job status: {update_job.job_status == RouterJobStatus.CLOSED}")
```

## Troubleshooting

Running into issues? This section should contain details as to what to do there.

## Next steps
- [Read more about Router in Azure Communication Services][nextsteps]

### More sample code
Please take a look at the [samples][job_router_samples] directory for detailed examples of how to use this library.

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][coc]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/python/
[cla]: https://cla.microsoft.com
[coc]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[communication_resource_docs]: https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp
[communication_resource_create_portal]:  https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp
[communication_resource_create_power_shell]: https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice
[communication_resource_create_net]: https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-net
[nextsteps]:https://docs.microsoft.com/azure/communication-services/concepts/router/concepts

[//]: # ([source]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter)
[product_docs]: https://docs.microsoft.com/azure/communication-services/overview
[classification_concepts]: https://docs.microsoft.com/azure/communication-services/concepts/router/classification-concepts
[subscribe_events]: https://docs.microsoft.com/azure/communication-services/how-tos/router-sdk/subscribe-events
[offer_issued_event_schema]: https://docs.microsoft.com/azure/communication-services/how-tos/router-sdk/subscribe-events#microsoftcommunicationrouterworkerofferissued
[deserialize_event_grid_event_data]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventgrid/azure-eventgrid#consume-from-servicebus
[event_grid_event_handlers]: https://docs.microsoft.com/azure/event-grid/event-handlers
[webhook_event_grid_event_delivery]: https://docs.microsoft.com/azure/event-grid/webhook-event-delivery
[pypi]: https://pypi.org
[pip]: https://pypi.org/project/pip/

[//]: # ([job_router_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/communication/azure-communication-jobrouter/samples)