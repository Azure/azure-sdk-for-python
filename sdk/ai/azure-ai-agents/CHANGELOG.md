
# Release History

## 1.2.0b3 (2025-08-22)

### Features Added

- Added delete operation for `ThreadMessages`.
- Add `RunStepDetailsActivity`, describing MCP function parameters.
- Add `RunStepDeltaCustomBingGroundingToolCall`, describing `BingCustomSearchTool` updates in streaming scenario.
- Add `RunStepDeltaMicrosoftFabricToolCall`, describing `FabricTool` updates in streaming scenario.
- Add `RunStepDeltaSharepointToolCall`, describing `SharepointTool` updates in streaming scenario.
- Improve code interpreter tool to take the list of `VectorStoreDataSource` as an input for enterprise file search.

### Bugs Fixed

- Fixed the issue when the `create_and_process` call hangs if MCP tool approval is required.

### Sample updates

- The file search samples were updated to demonstrate retrieving text associated with citations.
- The SharePoint tool sample was updated to demonstrate retrieving text associated with citations and render references correctly.
- Added samples for file search citation with streaming.
- Bing Grounding and Bing Custom Search samples were fixed to correctly present references.

## 1.2.0b2 (2025-08-12)

### Features Added

- Add support for Browser Automation tool.
- Add support for environment variable `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` as defined by
[OpenTelemetry](https://opentelemetry.io/), to control tracing of user and Agent messages.

### Bugs Fixed

- Added `RunStepConnectedAgentToolCall` and `RunStepDeltaConnectedAgentToolCall` for deserializing Connected
Agent tool updates in non-streaming and streaming scenarios.

### Sample updates

- Add new Browser Automation tool samples, named `sample_agents_browser_automation.py`
and `sample_agents_browser_automation_async.py`.

## 1.2.0b1 (2025-08-05)

**Beta Features Restored**: This release reintroduces all experimental features that were available in the 1.1.0b series but removed in the 1.1.0 stable release.

### Features Added
- API version is changed to 2025-05-15-preview.
- Support `tool_resources` for run async operations.
- MCP tool support (restored from 1.1.0b4).
- Deep Research tool support (restored from 1.1.0b3).
- FabricTool, SharepointTool, and BingCustomSearchTool classes (restored from 1.1.0b1).

### Bugs Fixed
- Fixed issues where the `runs.create_and_process` API call did not correctly handle the `AzureAISearchTool`, `FileSearchTool`, and `CodeInterpreterTool` when specified in the toolset parameter.
- Added classes for deserialization of `RunStepDeltaAzureAISearchToolCall`, `RunStepDeltaOpenAPIToolCall` and `RunStepDeltaDeepResearchToolCall`, required to get the real time updates when Azure AI Search, OpenAPI or Deep Research tools are being used during streaming scenarios.

### Sample updates
- Updated `sample_agents_deep_research.py` and `sample_agents_deep_research_async.py` for citations.
- **Restored samples**: MCP tool samples, Deep Research tool samples, and FabricTool/SharepointTool/BingCustomSearchTool samples that were removed in 1.1.0.
  
## 1.1.0 (2025-08-05)

**Beta Features Removed**: All experimental features from 1.1.0b1-1.1.0b4 have been removed to provide a stable release.

### Breaking Changes
- Removed MCP tool support (was in 1.1.0b4).
- Removed Deep Research tool support (was in 1.1.0b3).
- Removed FabricTool, SharepointTool, and BingCustomSearchTool classes (was in 1.1.0b1).
- **Samples Removed**: All samples related to the above experimental features have been removed.

### Features Added
- API version is changed to V1.
- New `tool_resources` parameter added to `runs.create` and `run.stream` method. This parameter represents overridden enabled tool resources that the agent should use to run the thread. Default value is None.

### Bugs Fixed
- `AgentsResponseFormatOption`, `MessageInputContent`, `MessageAttachmentToolDefinition`, `AgentsToolChoiceOption` are now public.
- Fixed `update_agents` to execute with body as a keyword parameter.
  
## 1.1.0b4 (2025-07-11)

**Beta Features Continued**: This release continues the experimental features from previous beta versions and adds new MCP tool support.

### Features Added
- API version is changed to 2025-05-15-preview.
- Added support for MCP tool. For more information, see https://aka.ms/FoundryAgentMCPDoc.
- New tool_resources parameter added to runs.create method. This parameter represents overridden enabled tool resources that the agent should use to run the thread. Default value is None.

### Bugs Fixed
- `_AgentsClientOperationsMixin` is now private.

### Sample updates
- Added a sample showing usage of MCP tool, [`sample_agents_mcp.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_tools/sample_agents_mcp.py).
- Added a sample showing auto function call for a synchronous client, [`sample_agents_auto_function_call.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_tools/sample_agents_auto_function_call.py)
- Added a sample showing auto function call for an asynchronous client, [`sample_agents_auto_function_call_async.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-agents/samples/agents_async/sample_agents_auto_function_call_async.py).

## 1.0.2 (2025-07-01)

**Beta Features Not Included**: This stable release does not include the experimental features from 1.1.0b1-1.1.0b3 (FabricTool, SharepointTool, BingCustomSearchTool, and DeepResearchTool) and corresponded samples.

### Features Added
- API version is changed to V1.

### Bugs Fixed
- Fixed a tracing related bug that caused an error when process was ending if messages or run steps were listed and the resulting list was not iterated completely.

## 1.1.0b3 (2025-06-30)

### Features Added
- Added support for Deep Research tool. For more information, see https://aka.ms/agents-deep-research.

### Bugs Fixed
- Fixed a tracing related bug that caused an error when process was ending if messages or run steps were listed and the resulting list was not iterated completely.

### Sample updates
- The file search samples were updated to demonstrate retrieving text associated with citations.
- Added samples for file search citation with streaming.
- Added samples showing usage of Deep Research tool (sync and async).

## 1.1.0b2 (2025-06-09)

### Features Added
- API version is changed to 2025-05-15-preview.

### Sample updates
- Changed all samples to use `AIProjectClient` which is recommended to specify endpoint and credential.
- Added `sample_agents_stream_iteration_with_functions.py`

## 1.0.1 (2025-06-09)

**Beta Features Not Included**: This stable release does not include the experimental features introduced in 1.1.0b1.

### Features Added
- API version is changed to V1.

### Breaking Changes
- FabricTool, SharepointTool, and BingCustomSearchTool classes are not available in this stable release.

### Bugs Fixed
- `asyncio.gather` is used to make function tool calls in parallel for `async` scenario.
- Adding instrumentation for create_thread_and_run.
- Fixed a tracing related bug that caused process_thread_run span to not appear when streaming is used without event handler.

## 1.1.0b1 (2025-05-20)

**Beta Features Introduced**: This release introduces experimental features that may change in future versions.

### Features Added
- API version is changed to 2025-05-15-preview.
- Add FabricTool, SharepointTool, and BingCustomSearchTool classes along with samples.

### Bugs Fixed
- Adding instrumentation for create_thread_and_run

## 1.0.0 (2025-05-15)

### Features Added
- First stable release of Azure AI Agents client library.

## 1.0.0b3 (2025-05-14)

### Features Added
- Internal updates based on TypeSpec finalization.

## 1.0.0b2 (2025-05-13)

### Breaking Changes
- Rename `get_last_text_message_by_role` to `get_last_message_text_by_role`.

## 1.0.0b1 (2025-05-07)

### Breaking Changes
- enable_auto_function_calls supports positional arguments instead of keyword arguments.
- Please see the [agents migration guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/AGENTS_MIGRATION_GUIDE.md) on how to use `azure-ai-projects` with `azure-ai-agents` package.
  
### Features Added
- Initial version - splits off Azure AI Agents functionality from the Azure AI Projects SDK.
- Azure AI Search tool, Bing Grounding tool, and Bing Custom Search tool parameters updated.
- All polling functions now support timeout keyword parameter.

### Bugs Fixed
- During automatic function calls for streaming, when the thread run is cancelled due to too many retry, now a cancelled event will be sent out.
- Add missing thread run id and message id on the process thread run span.
