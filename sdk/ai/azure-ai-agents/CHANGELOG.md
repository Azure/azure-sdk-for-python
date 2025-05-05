# Release History

## 1.0.0b1 (2025-05-07)

### Breaking Changes

- enable_auto_function_calls supports positional arguments instead of keyword arguments.
  
### Features Added

- Initial version - splits off Azure AI Agents functionality from the Azure AI Projects SDK
- Azure AI Search tool, Bing Grounding tool, and Bing Custom Search tool parameters updated
- All polling functions now support timeout keyword parameter.

### Bugs Fixed

- During automatic function calls for streaming, when the thread run is cancelled due to too many retry, now a cancelled event will be sent out.
- Add missing thread run id and message id on the process thread run span
