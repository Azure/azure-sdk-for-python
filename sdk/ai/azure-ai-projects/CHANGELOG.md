# Release History

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
