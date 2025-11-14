# Release History

## 2.0.0b2 (Unreleased)

### Features Added
* Tracing: support for workflow agent tracing.

### Breaking changes

* `get_openai_client()` method on the asynchronous AIProjectClient is no longer an "async" method.
* Tracing: tool call output event content format updated to be in line with other events.

### Bugs Fixed
* Tracing: operation name attribute added to create agent span, token usage added to streaming response generation span.

### Sample updates
* Added `finetuning` samples for operations create, retrieve, list, list_events, list_checkpoints, cancel, pause and resume. Also, these samples includes various finetuning techniques like Supervised (SFT), Reinforcement (RFT) and Direct performance optimization (DPO).
* In all most samples, credential, project client, and openai client are combined into one context manager.
* Remove `await` while calling `get_openai_client()` for samples using asynchronous clients. 

## 2.0.0b1 (2025-11-11)

### Features added

* The client library now uses version `2025-11-15-preview` of the Microsoft Foundry [data plane REST APIs](https://aka.ms/azsdk/azure-ai-projects-v2/api-reference-2025-11-15-preview).
* New Agent operations (now built on top of OpenAI's `Responses` protocol) were added to the `AIProjectClient`.
This package no longer depends on `azure-ai-agents` package. See `samples\agents` folder.
* New Evaluation operations. See methods on properties `.evaluation_rules`, `.evaluation_taxonomies`, `.evaluators`, `.insights`, and `.schedules`.
* New Memory Store operations. See methods on the property `.memory_store`.

### Breaking changes

* The implementation of `.get_openai_client()` method was updated to return an authenticated
OpenAI client from the openai package, configure to run Responses operations on your Foundry Project endpoint.

### Sample updates

* Added new Agent samples. See `samples\agents` folder.
* Added new Evaluation samples. See `samples\evaluations` folder.
* Added `files` samples for operations create, delete, list, retrieve and content. See `samples\files` folder.

## 1.1.0b4 (2025-09-12)

### Bugs Fixed

* Fix getting secret keys for connections of type "Custom Keys" ([GitHub issue 52355](https://github.com/Azure/azure-sdk-for-net/issues/52355))

## 1.1.0b3 (2025-08-26)

### Features added

* File `setup.py` was updated to indicate the dependency `azure-ai-agents>=1.2.0b3`
instead of `azure-ai-agents>=1.0.0`. This means that in a clean environment, installing
via `pip install --pre azure-ai-projects` will install latest beta version of `azure-ai-agents`
(which has features in preview) instead of latest stable version (which does
not include preview features).

## 1.1.0b2 (2025-08-05)

### Bugs Fixed

Fix regression in Red-Team operations, in the definition of the class `AzureOpenAIModelConfiguration`.

## 1.1.0b1 (2025-08-01)

First beta version following the 1.0.0 stable release. It brings back the Evaluation and Red-Team operations which are still in preview.

### Features added

* Evaluation and Red-Team operations (in preview) were restored.

## 1.0.0 (2025-07-31)

First stable version of the client library. The client library now uses version `v1` of the
AI Foundry [data plane REST APIs](https://aka.ms/azsdk/azure-ai-projects/ga-rest-api-reference).

### Breaking changes

* Features that are still in preview were removed from this stable release. This includes:
  * Evaluation operations (property `.evaluations`)
  * Red-Team operations (property `.red_teams`)
  * Class `PromptTemplate`.
  * Package function `enable_telemetry()`
* Classes were renamed:
  * Class `Sku` was renamed `ModelDeploymentSku`
  * Class `SasCredential` was renamed `BlobReferenceSasCredential`
  * Class `AssetCredentialResponse` was renamed `DatasetCredential`
* Method `.inference.get_azure_openai_client()` was renamed `.get_openai_client()`. The `.inference` property was removed.
  The method is documented as returning an object of type `OpenAI`, but it still returns an object of the derived type `AzureOpenAI`.
  The function implementation has not changed.
* Method `.telemetry.get_connection_string()` was renamed `.telemetry.get_application_insights_connection_string()`

### Sample updates

* Added a new Dataset sample named `sample_datasets_download.py` to show how you can download all files referenced by a certain Dataset (following a question in [this GitHub issue](https://github.com/Azure/azure-sdk-for-python/issues/41960))
* Two samples added showing how to do a `responses` operation using an authenticated Azure OpenAI client created
using `get_openai_client()`.
* Existing inference samples that used the package function `enable_telemetry()` were updated to remove this call,
and instead add the necessary tracing configuration calls to the sample.

## 1.0.0b12 (2025-06-23)

### Breaking changes

* These 3 methods on `AIProjectClient` were removed: `.inference.get_chat_completions_client()`,
`.inference.get_embeddings_client()` and `.inference.get_image_embeddings_client()`.
For guidance on obtaining an authenticated `azure-ai-inference` client for your AI Foundry Project,
refer to the updated samples in the `samples\inference` directory. For example,
`sample_chat_completions_with_azure_ai_inference_client.py`. Alternatively, use the `.inference.get_azure_openai_client()` method to perform chat completions with an Azure OpenAI client.
* Method argument name changes:
  * In method `.indexes.create_or_update()` argument `body` was renamed `index`.
  * In method `.datasets.create_or_update()` argument `body` was renamed `dataset_version`.
  * In method `.datasets.pending_upload()` argument `body` was renamed `pending_upload_request`.

### Bugs Fixed

* Fix to package function `enable_telemetry()` to correctly instrument `azure-ai-agents`.
* Updated RedTeam target type visibility to allow for type being sent in the JSON for redteam run creation.

### Other

* Set dependency on `azure-ai-agents` version `1.0.0` or above,
now that we have a stable release of the Agents package.

## 1.0.0b11 (2025-05-15)

There have been significant updates with the release of version 1.0.0b11, including breaking changes.
Please see new samples and package README.md file.

### Features added

* `.deployments` methods to enumerate AI models deployed to your AI Foundry Project.
* `.datasets` methods to upload documents and reference them. To be used with Evaluations.
* `.indexes` methods to handle your Search Indexes.

### Breaking changes

* Azure AI Foundry Project endpoint is now required to construct the `AIProjectClient`. It has the form
`https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>`. Find it in your AI Foundry Project
Overview page. The factory method `from_connection_string` was removed. Support for project connection string and hub-based projects has been discontinued. We recommend creating a new Azure AI Foundry resource utilizing project endpoint. If this is not possible, please pin the version of or pin the version of `azure-ai-projects` to `1.0.0b10` or earlier.
* Agents are now implemented in a separate package `azure-ai-agents`. Continue using the ".agents" operations on the
`AIProjectsClient` to create, run and delete agents, as before. However there have been some breaking changes in these operations.
See [Agents package document and samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents) for more details.
* Several changes to the `.connections` methods, including the response object (now simply called `Connection`)
* The method `.inference.get_azure_openai_client()` now supports returning an authenticated `AzureOpenAI` client to be used with
AI models deployed to the Project's AI Services. This is in addition to the existing option to get an `AzureOpenAI` client for one of the connected Azure OpenAI services.
* Import `PromptTemplate` from `azure.ai.projects` instead of `azure.ai.projects.prompts`.
* The class ConnectionProperties was renamed to Connection, and its properties have changed.
* The method `.to_evaluator_model_config` on `ConnectionProperties` is no longer required and does not have an equivalent method on `Connection`. When constructing the EvaluatorConfiguration class, the `init_params` element now requires `deployment_name` instead of `model_config`.
* The method `upload_file` on `AIProjectClient` had been removed, use `datasets.upload_file` instead.
* Evaluator Ids are available using the Enum `EvaluatorIds` and no longer require `azure-ai-evaluation` package to be installed.
* Property `scope` on `AIProjectClient` is removed, use AI Foundry Project endpoint instead.
* Property `id` on Evaluation is replaced with `name`.
* Please see the [agents migration guide](https://github.com/Azure/azure-sdk-for-python/blob/release/azure-ai-projects/1.0.0/sdk/ai/azure-ai-projects/AGENTS_MIGRATION_GUIDE.md) on how to use the new `azure-ai-projects` with `azure-ai-agents` package.

### Sample updates

* All samples have been updated. New ones added for Deployments, Datasets and Indexes.

## 1.0.0b10 (2025-04-23)

### Features added

* Added `ConnectedAgentTool` class for better connected Agent support.
* Added Agent tool call tracing for all tool call types when streaming with `AgentEventHandler` based event handler.
* Added tracing for listing Agent run steps.
* Add a `max_retry` argument to the Agent's `enable_auto_function_calls` function to cancel the run if the maximum number of retries for auto function calls is reached.

### Sample updates

* Added connected Agent tool sample.

### Bugs Fixed

* Fix for filtering of Agent messages by run ID (see [GitHub issue 49513](https://github.com/Azure/azure-sdk-for-net/issues/49513)).

## 1.0.0b9 (2025-04-16)

### Features added

* Utilities to load prompt template strings and Prompty file content
* Added BingCustomSearchTool class with sample
* Added list_threads API to agents namespace
* Added image input support for agents create_message

### Sample updates

* Added `project_client.agents.enable_auto_function_calls(toolset=toolset)` to all samples that has `toolcalls` executed by `azure-ai-project` SDK
* New BingCustomSearchTool sample
* New samples added for image input from url, file and base64

### Breaking Changes

Redesigned automatic function calls because agents retrieved by `update_agent` and `get_agent` do not support them.  With the new design, the toolset parameter in `create_agent` no longer executes toolcalls automatically during `create_and_process_run` or `create_stream`. To retain this behavior, call `enable_auto_function_calls` without additional changes.

## 1.0.0b8 (2025-03-28)

### Features added

* New parameters added for Azure AI Search tool, with corresponding sample update.
* Fabric tool REST name updated, along with convenience code.

### Sample updates

* Sample update demonstrating new parameters added for Azure AI Search tool.
* Sample added using OpenAPI tool against authenticated TripAdvisor API spec.

### Bugs Fixed

* Fix for a bug in Agent tracing causing event handler return values to not be returned when tracing is enabled.
* Fix for a bug in Agent tracing causing tool calls not to be recorded in traces.
* Fix for a bug in Agent tracing causing function tool calls to not work properly when tracing is enabled.
* Fix for a bug in Agent streaming, where `agent_id` was not included in the response. This caused the SDK not to make function calls when the thread run status is `requires_action`.

## 1.0.0b7 (2025-03-06)

### Features added

* Add support for parsing URL citations in Agent text messages. See new classes `MessageTextUrlCitationAnnotation` and `MessageDeltaTextUrlCitationAnnotation`.
* Add enum value `ConnectionType.API_KEY` to support enumeration of generic connections that uses API Key authentication.

### Sample updates

* Update sample `sample_agents_bing_grounding.py` with printout of URL citation.
* Add new samples `sample_agents_stream_eventhandler_with_bing_grounding.py` and `sample_agents_stream_iteration_with_bing_grounding.py` with printout of URL citation.

### Bugs Fixed

* Fix a bug in deserialization of `RunStepDeltaFileSearchToolCall` returned during Agent streaming (see [GitHub issue 48333](https://github.com/Azure/azure-sdk-for-net/issues/48333)).
* Fix for Exception raised while parsing Agent streaming response, in some rare cases, for multibyte UTF-8 languages like Chinese.

### Breaking Changes

* Rename input argument `assistant_id` to `agent_id` in all Agent methods to align with the "Agent" terminology. Similarly, rename all `assistant_id` properties on classes.

## 1.0.0b6 (2025-02-14)

### Features added

* Added `trace_function` decorator for conveniently tracing function calls in Agents using OpenTelemetry. Please see the README.md for updated documentation.

### Sample updates

* Added AzureLogicAppTool utility and Logic App sample under `samples/agents`, folder to make Azure Logic App integration with Agents easier.
* Added better observability for Azure AI Search sample for Agents via improved run steps information from the service.
* Added sample to demonstrate how to add custom attributes to telemetry span.

### Bugs Fixed

* Lowered the logging level of "Toolset is not available in the client" from `warning` to `debug` to prevent unnecessary log entries in agent application runs.

## 1.0.0b5 (2025-01-17)

### Features added

* Add method `.inference.get_image_embeddings_client` on `AIProjectClient` to get an authenticated
`ImageEmbeddingsClient` (from the package azure-ai-inference). You need to have azure-ai-inference package
version 1.0.0b7 or above installed for this method to work.

### Bugs Fixed

* Fix for events dropped in streamed Agent response (see [GitHub issue 39028](https://github.com/Azure/azure-sdk-for-python/issues/39028)).
* In Agents, incomplete status thread run event is now deserialized into a ThreadRun object, during stream iteration, and invokes the correct function `on_thread_run` (instead of the wrong function `on_unhandled_event`).
* Fix an error when calling the `to_evaluator_model_config` method of class `ConnectionProperties`. See new input
argument `include_credentials`.

### Breaking Changes

* `submit_tool_outputs_to_run` returns `None` instead of `ThreadRun` (see [GitHub issue 39028](https://github.com/Azure/azure-sdk-for-python/issues/39028)).

## 1.0.0b4 (2024-12-20)

### Bugs Fixed

* Fix for Agent streaming issue (see [GitHub issue 38918](https://github.com/Azure/azure-sdk-for-python/issues/38918))
* Fix for Agent async function `send_email_async` is not called (see [GitHub issue 38898](https://github.com/Azure/azure-sdk-for-python/issues/38898))
* Fix for Agent streaming with event handler fails with "AttributeError: 'MyEventHandler' object has no attribute 'buffer'" (see [GitHub issue 38897](https://github.com/Azure/azure-sdk-for-python/issues/38897))

### Features Added

* Add optional input argument `connection_name` to methods `.inference.get_chat_completions_client`,
 `.inference.get_embeddings_client` and `.inference.get_azure_openai_client`.

## 1.0.0b3 (2024-12-13)

### Features Added

* Add support for Structured Outputs for Agents.
* Add option to include file contents, when index search is used for Agents.
* Added objects to inform Agents about Azure Functions.
* Redesigned streaming and event handlers for agents.
* Add `parallel_tool_calls` parameter to allow parallel tool execution for Agents.
* Added `BingGroundingTool` for Agents to use against a Bing API Key connection.
* Added `AzureAiSearchTool` for Agents to use against an Azure AI Search resource.
* Added `OpenApiTool` for Agents, which creates and executes a REST function defined by an OpenAPI spec.
* Added new helper properties in `OpenAIPageableListOfThreadMessage`, `MessageDeltaChunk`, and `ThreadMessage`.
* Rename "AI Studio" to "AI Foundry" in package documents and samples, following recent rebranding.

### Breaking Changes

* The method `.agents.get_messages` was removed. Please use `.agents.list_messages` instead.

## 1.0.0b2 (2024-12-03)

### Bugs Fixed

* Fix a bug in the `.inference` operations when Entra ID authentication is used by the default connection.
* Fixed bugs occurring during streaming in function tool calls by asynchronous agents.
* Fixed bugs that were causing issues with tracing agent asynchronous functionality.
* Fix a bug causing warning about unclosed session, shown when using asynchronous credentials to create agent.
* Fix a bug that would cause agent function tool related function names and parameters to be included in traces even when content recording is not enabled.

## 1.0.0b1 (2024-11-15)

### Features Added

First beta version
