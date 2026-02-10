---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - language-service
urlFragment: conversationsauthoring-samples
---

# Samples for Azure Conversational Language Understanding Authoring client library for Python

These code samples show common **Conversation Authoring** operations with the Azure `azure-ai-language-conversations-authoring` client library.

You can authenticate your client with a Conversation Authoring API key:

- See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Conversation Authoring client’s offerings.

| **File Name** | **Description** |
|-|-|
| [sample_assign_project_resources.py][sample_assign_project_resources] and [sample_assign_project_resources_async.py][sample_assign_project_resources_async] | Assign deployment resources to a project. |
| [sample_cancel_training_job.py][sample_cancel_training_job] and [sample_cancel_training_job_async.py][sample_cancel_training_job_async] | Cancel an ongoing training job. |
| [sample_create_project.py][sample_create_project] and [sample_create_project_async.py][sample_create_project_async] | Create a new conversation project. |
| [sample_delete_deployment.py][sample_delete_deployment] and [sample_delete_deployment_async.py][sample_delete_deployment_async] | Delete a specific deployment from a project. |
| [sample_delete_project.py][sample_delete_project] and [sample_delete_project_async.py][sample_delete_project_async] | Delete an existing project. |
| [sample_delete_trained_model.py][sample_delete_trained_model] and [sample_delete_trained_model_async.py][sample_delete_trained_model_async] | Delete a trained model from the project. |
| [sample_deploy_project.py][sample_deploy_project] and [sample_deploy_project_async.py][sample_deploy_project_async] | Deploy a trained model to an endpoint. |
| [sample_export_project.py][sample_export_project] and [sample_export_project_async.py][sample_export_project_async] | Export a project into JSON format for versioning or reuse. |
| [sample_get_deployment.py][sample_get_deployment] and [sample_get_deployment_async.py][sample_get_deployment_async] | Retrieve details about a deployment. |
| [sample_get_model_evaluation_results.py][sample_get_model_evaluation_results] and [sample_get_model_evaluation_results_async.py][sample_get_model_evaluation_results_async] | Get detailed model evaluation results for analysis. |
| [sample_get_model_evaluation_summary.py][sample_get_model_evaluation_summary] and [sample_get_model_evaluation_summary_async.py][sample_get_model_evaluation_summary_async] | Retrieve summary of model evaluation metrics. |
| [sample_get_project.py][sample_get_project] and [sample_get_project_async.py][sample_get_project_async] | Get details of a specific project. |
| [sample_import_project.py][sample_import_project] and [sample_import_project_async.py][sample_import_project_async] | Import labeled assets and metadata into a project. |
| [sample_load_snapshot.py][sample_load_snapshot] and [sample_load_snapshot_async.py][sample_load_snapshot_async] | Load a snapshot of a trained model. |
| [sample_swap_deployments.py][sample_swap_deployments] and [sample_swap_deployments_async.py][sample_swap_deployments_async] | Swap two deployments within a project. |
| [sample_train.py][sample_train] and [sample_train_async.py][sample_train_async] | Train a model within a project. |
| [sample_unassign_project_resources.py][sample_unassign_project_resources] and [sample_unassign_project_resources_async.py][sample_unassign_project_resources_async] | Unassign deployment resources from a project. |
| [sample_list_project_resources.py][sample_list_project_resources] and [sample_list_project_resources_async.py][sample_list_project_resources_async] | List all deployment-level resources currently assigned to a project. |
| [sample_get_assign_project_resources_status.py][sample_get_assign_project_resources_status] and [sample_get_assign_project_resources_status_async.py][sample_get_assign_project_resources_status_async] | Get the operation status of a resource-assignment request. |
| [sample_get_unassign_project_resources_status.py][sample_get_unassign_project_resources_status] and [sample_get_unassign_project_resources_status_async.py][sample_get_unassign_project_resources_status_async] | Get the operation status of a resource-unassignment request. |
| [sample_list_assigned_resource_deployments.py][sample_list_assigned_resource_deployments] and [sample_list_assigned_resource_deployments_async.py][sample_list_assigned_resource_deployments_async] | List all deployments associated with a specific assigned resource. |
| [sample_delete_deployment_from_resources.py][sample_delete_deployment_from_resources] and [sample_delete_deployment_from_resources_async.py][sample_delete_deployment_from_resources_async] | Delete a deployment from the project’s assigned resources. |
| [sample_get_deployment_delete_from_resources_status.py][sample_get_deployment_delete_from_resources_status] and [sample_get_deployment_delete_from_resources_status_async.py][sample_get_deployment_delete_from_resources_status_async] | Get the status of a deployment-deletion operation from project resources. |

---

## Prerequisites

- Python 3.7 or later is required to use this package.  
- You must have an [Azure subscription][azure_subscription] and a [Language Service resource][language_resource] to run these samples.

## Setup

1. Install the Azure Conversation Authoring client library for Python with [pip][pip]:

```bash
pip install azure-ai-language-conversations-authoring
```
For more information about how the versioning of the SDK corresponds to the versioning of the service's API, see [here][versioning_story_readme].

2. Clone or download this sample repository.  
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory where the samples are located.  
2. Set the environment variables specified in the sample file you wish to run.  
   - Typically, you will need to set:  
     - `AZURE_CONVERSATIONS_AUTHORING_ENDPOINT`  
     - `AZURE_CONVERSATIONS_AUTHORING_KEY`  
3. Follow the usage described in the file, e.g. `python sample_train.py`

## Next steps

Check out the [API reference documentation][api_reference_authoring] to explore the full set of operations available in the Azure Conversational Language Understanding **Authoring** client library for Python.

[azure_subscription]: https://azure.microsoft.com/free/
[language_resource]: https://portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[pip]: https://pypi.org/project/pip/
[api_reference_authoring]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring
<!-- TODO: change api_reference_documentation to azuresdkdocs link after first publish -->
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_authentication_async.py

[sample_assign_project_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_assign_project_resources.py
[sample_assign_project_resources_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_assign_project_resources_async.py

[sample_cancel_training_job]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_cancel_training_job.py
[sample_cancel_training_job_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_cancel_training_job_async.py

[sample_create_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_create_project.py
[sample_create_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_create_project_async.py

[sample_delete_deployment]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_delete_deployment.py
[sample_delete_deployment_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_delete_deployment_async.py

[sample_delete_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_delete_project.py
[sample_delete_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_delete_project_async.py

[sample_delete_trained_model]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_delete_trained_model.py
[sample_delete_trained_model_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_delete_trained_model_async.py

[sample_deploy_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_deploy_project.py
[sample_deploy_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_deploy_project_async.py

[sample_export_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_export_project.py
[sample_export_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_export_project_async.py

[sample_get_deployment]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_deployment.py
[sample_get_deployment_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_get_deployment_async.py

[sample_get_model_evaluation_results]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_model_evaluation_results.py
[sample_get_model_evaluation_results_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_get_model_evaluation_results_async.py

[sample_get_model_evaluation_summary]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_model_evaluation_summary.py
[sample_get_model_evaluation_summary_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_get_model_evaluation_summary_async.py

[sample_get_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_project.py
[sample_get_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_get_project_async.py

[sample_import_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_import_project.py
[sample_import_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_import_project_async.py

[sample_load_snapshot]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_load_snapshot.py
[sample_load_snapshot_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_load_snapshot_async.py

[sample_swap_deployments]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_swap_deployments.py
[sample_swap_deployments_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_swap_deployments_async.py

[sample_train]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_train.py
[sample_train_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_train_async.py

[sample_unassign_project_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_unassign_project_resources.py
[sample_unassign_project_resources_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_unassign_project_resources_async.py

[sample_list_project_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_list_project_resources.py
[sample_list_project_resources_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_list_project_resources_async.py

[sample_get_assign_project_resources_status]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_assign_project_resources_status.py
[sample_get_assign_project_resources_status_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_get_assign_project_resources_status_async.py

[sample_get_unassign_project_resources_status]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_unassign_project_resources_status.py
[sample_get_unassign_project_resources_status_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_get_unassign_project_resources_status_async.py

[sample_list_assigned_resource_deployments]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_list_assigned_resource_deployments.py
[sample_list_assigned_resource_deployments_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_list_assigned_resource_deployments_async.py

[sample_delete_deployment_from_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_delete_deployment_from_resources.py
[sample_delete_deployment_from_resources_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_delete_deployment_from_resources_async.py

[sample_get_deployment_delete_from_resources_status]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_deployment_delete_from_resources_status.py
[sample_get_deployment_delete_from_resources_status_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_get_deployment_delete_from_resources_status_async.py

[versioning_story_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring#install-the-package