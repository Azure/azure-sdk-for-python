# Release History

## 1.0.2 (Unreleased)

### Bugs Fixed
- Fixed a tracing related bug that caused an error when process was ending if messages or run steps were listed and the resulting list was not iterated completely.

## 1.0.1 (2025-06-09)

### Bugs Fixed

- `asyncio.gather` is used to make function tool calls in parallel for `async` scenario.
- Adding instrumentation for create_thread_and_run.
- Fixed a tracing related bug that caused process_thread_run span to not appear when streaming is used without event handler.

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
  
### Features Added

- Initial version - splits off Azure AI Agents functionality from the Azure AI Projects SDK.
- Azure AI Search tool, Bing Grounding tool, and Bing Custom Search tool parameters updated.
- All polling functions now support timeout keyword parameter.

### Bugs Fixed

- During automatic function calls for streaming, when the thread run is cancelled due to too many retry, now a cancelled event will be sent out.
- Add missing thread run id and message id on the process thread run span.
