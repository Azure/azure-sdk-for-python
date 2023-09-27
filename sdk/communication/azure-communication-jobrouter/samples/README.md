---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-communication-services
urlFragment: communication-jobrouter-samples 
name: azure-communication-jobrouter samples for Python
description: Samples for the azure-communication-jobrouter client library
---
  
# Azure Communication JobRouter client SDK Samples

- Authentication
  - [JobRouterClient and JobRouterAdministrationClient][sample_authentication]([async version][sample_authentication_async])
    - Create client from connection string

- Crud operations
  - [Classification Policy][classificationPolicyCrudOps]([async version][classificationPolicyCrudOpsAsync])
  - [Distribution Policy][distributionPolicyCrudOps]([async version][distributionPolicyCrudOpsAsync])
  - [Exception Policy][exceptionPolicyCrudOps]([async version][exceptionPolicyCrudOpsAsync])
  - [Job Queue][jobQueueCrudOps]([async version][jobQueueCrudOpsAsync])
  - [Router Worker][routerWorkerCrudOps]([async version][routerWorkerCrudOpsAsync])
  - [Router Job][routerJobCrudOps]([async version][routerJobCrudOpsAsync])

[//]: # (- Routing Scenarios)

[//]: # (  - Basic Scenario)

[//]: # (    - [Create Distribution Policy, Queue, Worker and Job | Accept Job Offer | Close and Complete job][basicScenario]&#40;[async version][basicScenarioAsync]&#41;)

[//]: # (    - [Requested worker selectors with job][requestedWorkerSelectorWithJobAsync])

[//]: # (  - Using Classification Policy)

[//]: # (    - [Queue selection with QueueSelectors][queueSelectionWithClassificationPolicyAsync])

[//]: # (    - [Dynamically assigning priority to job][prioritizationWithClassificationPolicyAsync])

[//]: # (    - [Dynamically attach WorkerSelectors to job][attachedWorkerSelectorWithClassificationPolicyAsync])

[//]: # (  - Using Distribution Policy)

[//]: # (    - [Basic Scenario][distributingOffersSimpleAsync])

[//]: # (    - [Multiple offers for a job][distributingOffersAdvancedAsync])

[//]: # (  - Using Exception Policy)

[//]: # (    - [Trigger exception with WaitTimeExceptionTrigger][waitTimeExceptionTriggerAsync])

[//]: # (    - [Trigger exception with QueueLengthExceptionTrigger][queueLengthExceptionTriggerAsync])

<!-- LINKS -->

[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/sample_authentication.py

[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/sample_authentication_async.py

[classificationPolicyCrudOps]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/classification_policy_crud_ops.py

[classificationPolicyCrudOpsAsync]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/classification_policy_crud_ops_async.py

[distributionPolicyCrudOps]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/distribution_policy_crud_ops.py

[distributionPolicyCrudOpsAsync]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/classification_policy_crud_ops_async.py

[exceptionPolicyCrudOps]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/exception_policy_crud_ops.py

[exceptionPolicyCrudOpsAsync]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/exception_policy_crud_ops_async.py

[jobQueueCrudOps]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/job_queue_crud_ops.py

[jobQueueCrudOpsAsync]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/job_queue_crud_ops_async.py

[routerWorkerCrudOps]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/router_worker_crud_ops.py

[routerWorkerCrudOpsAsync]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/router_worker_crud_ops_async.py

[routerJobCrudOps]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/router_job_crud_ops.py

[routerJobCrudOpsAsync]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-jobrouter/samples/router_job_crud_ops_async.py

[//]: # ([basicScenario]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample1_HelloWorld.md)

[//]: # ([basicScenarioAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample1_HelloWorldAsync.md)

[//]: # ([requestedWorkerSelectorWithJobAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample1_RequestedWorkerSelectorAsync.md)

[//]: # ([queueSelectionWithClassificationPolicyAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample2_ClassificationWithQueueSelectorAsync.md)

[//]: # ([prioritizationWithClassificationPolicyAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample2_ClassificationWithPriorityRuleAsync.md)

[//]: # ([attachedWorkerSelectorWithClassificationPolicyAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample2_ClassificationWithWorkerSelectorAsync.md)

[//]: # ([distributingOffersSimpleAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample3_SimpleDistributionAsync.md)

[//]: # ([distributingOffersAdvancedAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample3_AdvancedDistributionAsync.md)

[//]: # ([waitTimeExceptionTriggerAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample4_WaitTimeExceptionAsync.md)

[//]: # ([queueLengthExceptionTriggerAsync]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication/Azure.Communication.JobRouter/samples/Sample4_QueueLengthExceptionTriggerAsync.md)