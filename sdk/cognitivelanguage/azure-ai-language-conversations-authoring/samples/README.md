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
| [sample_create_project.py][sample_create_project] and [sample_create_project_async.py][sample_create_project_async] | Create a new conversation project. |
| [sample_import_project.py][sample_import_project] and [sample_import_project_async.py][sample_import_project_async] | Import labeled assets and metadata into a conversation project. |
| [sample_export_project.py][sample_export_project] and [sample_export_project_async.py][sample_export_project_async] | Export a project into JSON format for versioning or reuse. |
| [sample_train.py][sample_train] and [sample_train_async.py][sample_train_async] | Train a model within a project. |
| [sample_get_model_evaluation_summary.py][sample_get_model_evaluation_summary] | Retrieve evaluation summary statistics for a trained model. |
| [sample_get_model_evaluation_results.py][sample_get_model_evaluation_results] and [sample_get_model_evaluation_results_async.py][sample_get_model_evaluation_results_async] | Retrieve detailed evaluation results for a trained model. |
| [sample_deploy_project.py][sample_deploy_project] | Deploy a trained model to a named deployment. |
| [sample_get_deployment.py][sample_get_deployment] | Get details about an existing deployment. |
| [sample_swap_deployments.py][sample_swap_deployments] and [sample_swap_deployments_async.py][sample_swap_deployments_async] | Swap two deployments (e.g., staging ↔ production). |
| [sample_load_snapshot.py][sample_load_snapshot] and [sample_load_snapshot_async.py][sample_load_snapshot_async] | Load a trained model snapshot into a project. |
| [sample_delete_project.py][sample_delete_project] | Delete a project. |
| [sample_delete_deployment.py][sample_delete_deployment] | Delete a deployment. |
| [sample_delete_trained_model.py][sample_delete_trained_model] | Delete a trained model from a project. |
| [sample_assign_deployment_resources.py][sample_assign_deployment_resources] | Assign Azure resources to a project deployment. |
| [sample_cancel_training_job.py][sample_cancel_training_job] | Cancel an in-progress training job. |

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
3. Run the sample with:  

```bash
python sample_train.py
```

## Next steps

Check out the [API reference documentation][api_reference_authoring] to explore the full set of operations available in the Azure Conversational Language Understanding **Authoring** client library for Python.

You may also want to review:

- [Product documentation][conversation_authoring_docs] for a conceptual overview of conversation authoring.  
- [REST API documentation][conversation_authoring_restdocs] for details on the underlying REST endpoints.  
- The [main README][conversation_authoring_root_readme] for installation instructions, authentication, and key concepts.  

---

## Next Steps

Check out the [API reference documentation][api_reference_authoring] to learn more about
what you can do with the Azure Conversational Language Understanding **Authoring** client library.

[azure_subscription]: https://azure.microsoft.com/free/
[language_resource]: https://portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[pip]: https://pypi.org/project/pip/

[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_authentication_async.py

[sample_create_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_create_project.py
[sample_create_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_create_project_async.py

[sample_import_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_import_project.py
[sample_import_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_import_project_async.py

[sample_export_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_export_project.py
[sample_export_project_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_export_project_async.py

[sample_train]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_train.py
[sample_train_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_train_async.py

[sample_get_model_evaluation_summary]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_model_evaluation_summary.py
[sample_get_model_evaluation_results]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_model_evaluation_results.py
[sample_get_model_evaluation_results_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_get_model_evaluation_results_async.py

[sample_deploy_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_deploy_project.py
[sample_get_deployment]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_get_deployment.py

[sample_swap_deployments]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_swap_deployments.py
[sample_swap_deployments_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_swap_deployments_async.py

[sample_load_snapshot]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_load_snapshot.py
[sample_load_snapshot_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/async/sample_load_snapshot_async.py

[sample_delete_project]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_delete_project.py
[sample_delete_deployment]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_delete_deployment.py
[sample_delete_trained_model]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_delete_trained_model.py

[sample_assign_deployment_resources]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_assign_deployment_resources.py
[sample_cancel_training_job]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/sample_cancel_training_job.py

[api_reference_authoring]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-conversations-authoring/latest/azure.ai.language.conversations.authoring.html
[versioning_story_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring#install-the-package