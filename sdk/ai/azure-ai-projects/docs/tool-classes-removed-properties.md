# Tool Classes: Removed Properties (v2.2.0 → v2.3.0)

The following Tool-derived classes had properties **removed** in v2.3.0 compared to v2.2.0. These properties (`name`, `description`, `tool_configs`) now only exist on the corresponding `ToolboxTool` subclasses.

## General Availability Tools

| Class Name | Removed Properties |
|------------|-------------------|
| `AzureAISearchTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `AzureFunctionTool` | `tool_configs: Optional[dict[str, ToolConfig]]` |
| `BingGroundingTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `CaptureStructuredOutputsTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `CodeInterpreterTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `FileSearchTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `FunctionShellToolParam` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `FunctionTool` | *(no changes)* |
| `ImageGenTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `LocalShellToolParam` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `MCPTool` | `tool_configs: Optional[dict[str, ToolConfig]]` |
| `OpenApiTool` | `tool_configs: Optional[dict[str, ToolConfig]]` |
| `WebSearchTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
v
## Preview Tools

| Class Name | Removed Properties |
|------------|-------------------|
| `A2APreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `BingCustomSearchPreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `BrowserAutomationPreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `ComputerUsePreviewTool` | *(no changes)* |
| `FabricIQPreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `MemorySearchPreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `MicrosoftFabricPreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `SharepointPreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `ToolboxSearchPreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |
| `WebSearchPreviewTool` | *(no changes)* |
| `WorkIQPreviewTool` | `name: Optional[str]`, `description: Optional[str]`, `tool_configs: Optional[dict[str, ToolConfig]]` |

## Summary

- **Total Tool classes analyzed:** 24
- **Classes with removed properties:** 19
- **Common pattern:** `name`, `description`, and `tool_configs` were moved exclusively to `ToolboxTool` subclasses
