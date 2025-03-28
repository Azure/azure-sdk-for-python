# Release History

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
