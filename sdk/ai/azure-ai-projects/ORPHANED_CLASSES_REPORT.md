# Orphaned Classes Analysis Report

## Azure AI Projects Python SDK

**Date:** December 23, 2025  
**Repository:** Azure/azure-sdk-for-python  
**Package:** azure-ai-projects  
**Branch:** main

---

## Executive Summary

This report identifies all model classes in the `azure-ai-projects` package that are **not used by any AIProjectClient operations**. These classes were emitted from TypeSpec source files but have no corresponding client methods to utilize them.

### Key Findings

- **Total Orphaned Classes:** 95
- **Total Exported Classes:** 387 (from `__all__`)
- **Total Used Classes:** 292 (including transitive dependencies)
- **Percentage Orphaned:** ~24.5%

---

## Methodology

### Analysis Approach

1. **Identified Operation Types**: Extracted all model types directly used in AIProjectClient operation signatures (return types and parameters)
2. **Transitive Dependency Analysis**: Used breadth-first search to trace all dependencies:
   - Property type references (e.g., `tools: list[Tool]`)
   - Base class hierarchies
   - Discriminated subtypes
   - Generic type parameters (`Optional[X]`, `list[X]`, `dict[str, X]`, `Union[X, Y]`)
3. **Comparison**: Identified classes in `__all__` that are not in the transitive dependency set

### Starting Point: Direct Operation Types (33 types)

Operations from AIProjectClient use these types directly:

- `AgentDefinition`, `AgentDetails`, `AgentVersionDetails`
- `Connection`, `DatasetCredential`, `DatasetVersion`
- `Deployment`, `EvaluationRule`, `EvaluationTaxonomy`
- `EvaluatorVersion`, `Index`, `Insight`
- `ItemParam`, `MemorySearchOptions`, `MemoryStoreDefinition`
- `MemoryStoreDetails`, `MemoryStoreSearchResult`, `PendingUploadRequest`
- `RedTeam`, `Schedule`, `ScheduleRun`
- And 11 more...

---

## Orphaned Classes by Category

### 1. Response-Related Classes (64 classes)

All classes associated with the OpenAI Responses API, which has **no corresponding operations** in AIProjectClient:

#### Core Response Class

- `Response`

#### Response Event Classes (44 streaming events)

- `ResponseCodeInterpreterCallCodeDeltaEvent`
- `ResponseCodeInterpreterCallCodeDoneEvent`
- `ResponseCodeInterpreterCallCompletedEvent`
- `ResponseCodeInterpreterCallInProgressEvent`
- `ResponseCodeInterpreterCallInterpretingEvent`
- `ResponseCompletedEvent`
- `ResponseContentPartAddedEvent`
- `ResponseContentPartDoneEvent`
- `ResponseCreatedEvent`
- `ResponseErrorEvent`
- `ResponseFailedEvent`
- `ResponseFileSearchCallCompletedEvent`
- `ResponseFileSearchCallInProgressEvent`
- `ResponseFileSearchCallSearchingEvent`
- `ResponseFunctionCallArgumentsDeltaEvent`
- `ResponseFunctionCallArgumentsDoneEvent`
- `ResponseImageGenCallCompletedEvent`
- `ResponseImageGenCallGeneratingEvent`
- `ResponseImageGenCallInProgressEvent`
- `ResponseImageGenCallPartialImageEvent`
- `ResponseInProgressEvent`
- `ResponseIncompleteEvent`
- `ResponseMCPCallArgumentsDeltaEvent`
- `ResponseMCPCallArgumentsDoneEvent`
- `ResponseMCPCallCompletedEvent`
- `ResponseMCPCallFailedEvent`
- `ResponseMCPCallInProgressEvent`
- `ResponseMCPListToolsCompletedEvent`
- `ResponseMCPListToolsFailedEvent`
- `ResponseMCPListToolsInProgressEvent`
- `ResponseOutputItemAddedEvent`
- `ResponseOutputItemDoneEvent`
- `ResponseQueuedEvent`
- `ResponseReasoningDeltaEvent`
- `ResponseReasoningDoneEvent`
- `ResponseReasoningSummaryDeltaEvent`
- `ResponseReasoningSummaryDoneEvent`
- `ResponseReasoningSummaryPartAddedEvent`
- `ResponseReasoningSummaryPartDoneEvent`
- `ResponseReasoningSummaryTextDeltaEvent`
- `ResponseReasoningSummaryTextDoneEvent`
- `ResponseRefusalDeltaEvent`
- `ResponseRefusalDoneEvent`
- `ResponseStreamEvent`
- `ResponseTextDeltaEvent`
- `ResponseTextDoneEvent`
- `ResponseWebSearchCallCompletedEvent`
- `ResponseWebSearchCallInProgressEvent`
- `ResponseWebSearchCallSearchingEvent`

#### Response Message Classes (10 message types)

- `ResponsesAssistantMessageItemParam`
- `ResponsesAssistantMessageItemResource`
- `ResponsesDeveloperMessageItemParam`
- `ResponsesDeveloperMessageItemResource`
- `ResponsesMessageItemParam`
- `ResponsesMessageItemResource`
- `ResponsesSystemMessageItemParam`
- `ResponsesSystemMessageItemResource`
- `ResponsesUserMessageItemParam`
- `ResponsesUserMessageItemResource`

#### Response Supporting Classes (9 classes)

- `ResponseConversation1`
- `ResponseError`
- `ResponseIncompleteDetails1`
- `ResponsePromptVariables`
- `ResponseText`
- `ResponseTextFormatConfiguration`
- `ResponseTextFormatConfigurationJsonObject`
- `ResponseTextFormatConfigurationJsonSchema`
- `ResponseTextFormatConfigurationText`
- `ResponseUsage`

**Why Orphaned:** The TypeSpec specification has `@@scope(Responses.createResponse, "!(csharp, python, java, javascript)")` on operations, which prevents Python SDK from generating response-related methods. However, the models lack corresponding scope restrictions.

---

### 2. Insight/Evaluation-Related Classes (17 classes)

Advanced evaluation and insights features that may not be fully exposed:

#### Agent Cluster Insights

- `AgentClusterInsightResult`
- `AgentClusterInsightsRequest`
- `ClusterInsightResult`
- `ClusterTokenUsage`
- `InsightCluster`
- `InsightSample`
- `InsightSummary`
- `InsightsMetadata`

#### Evaluation Comparison & Results

- `EvalCompareReport`
- `EvalResult`
- `EvalRunResultCompareItem`
- `EvalRunResultComparison`
- `EvalRunResultSummary`
- `EvaluationComparisonRequest`
- `EvaluationResultSample`
- `EvaluationRunClusterInsightResult`
- `EvaluationRunClusterInsightsRequest`

**Why Orphaned:** These are likely part of insights operations that may exist in TypeSpec but are scoped out or not yet fully implemented in the client.

---

### 3. Location/Target/Coordinate Classes (7 classes)

Spatial and targeting-related classes:

- `ApproximateLocation`
- `AzureAIAgentTarget`
- `ChartCoordinate`
- `Coordinate`
- `Location`
- `Target`
- `TargetConfig`

**Why Orphaned:** These may be used for red team operations or other features that reference targets but are not exposed through current operation signatures.

---

### 4. Filter Classes (2 classes)

Query/filtering classes:

- `ComparisonFilter`
- `CompoundFilter`

**Why Orphaned:** Likely used for advanced querying capabilities that are not exposed in current operations.

---

### 5. Other Orphaned Classes (10 classes)

Miscellaneous classes without clear categorization:

- `AISearchIndexResource`
- `AgentId`
- `AgentReference`
- `AgentTaxonomyInput`
- `EmbeddingConfiguration`
- `Prompt` (prompt template reference)
- `RankingOptions`
- `TaxonomyCategory`
- `TaxonomySubCategory`
- `WorkflowActionOutputItemResource`

**Why Orphaned:** Various reasons including incomplete feature implementation, scoped-out operations, or internal/future use.

---

## Classes That Are NOT Orphaned (Examples)

To clarify the analysis methodology, here are examples of classes that **appear** to be unused but are actually required:

### Tool Hierarchy (19 tool classes)

- `Tool` (base class)
- `A2ATool`, `AzureAISearchAgentTool`, `AzureFunctionAgentTool`, `BingCustomSearchAgentTool`, `BingGroundingAgentTool`, `BrowserAutomationAgentTool`, `CaptureStructuredOutputsTool`, `CodeInterpreterTool`, `ComputerUsePreviewTool`, `FileSearchTool`, `FunctionTool`, `ImageGenTool`, `LocalShellTool`, `MCPTool`, `MemorySearchTool`, `MicrosoftFabricAgentTool`, `OpenApiAgentTool`, `SharepointAgentTool`, `WebSearchPreviewTool`

**Why Used:** `AgentDefinition` → `PromptAgentDefinition.tools: list[Tool]` → All Tool subtypes

### ItemParam Hierarchy (18 item classes)

- `ItemParam` (base class)
- `CodeInterpreterToolCallItemParam`, `ComputerToolCallItemParam`, `FileSearchToolCallItemParam`, `FunctionToolCallItemParam`, and 14 more subtypes

**Why Used:** Multiple agent properties reference `list[ItemParam]` or specific subtypes

### ItemResource Hierarchy (20 resource classes)
Similar transitive dependency through resource properties in agents and operations.

---

## Impact Analysis

### Storage & Distribution Impact

- **Package Size**: 95 unused classes add unnecessary code to the distributed package
- **Documentation**: Confusing for users who see classes with no corresponding usage patterns
- **Maintenance**: Extra code to maintain despite no functional usage

### Developer Experience Impact

- **Confusion**: Developers may attempt to use these classes and find no supporting operations
- **Documentation**: Need to document classes that have no practical use in the SDK
- **Type Hints**: Classes appear in IDE autocomplete but lead to dead ends

---

## Root Cause

The TypeSpec-to-Python code generator:

1. **Scopes operations** but not models by default
2. **Emits models conservatively** - includes any model defined in TypeSpec unless explicitly scoped out
3. **Doesn't analyze reachability** - doesn't check if models are actually used by any operation

The TypeSpec source files (in `azure-rest-api-specs`) have decorators like:

```typescript
@@scope(Responses.createResponse, "!(csharp, python, java, javascript)")
```

This prevents operations from being generated, but the associated models lack similar restrictions.

---

## Recommendations

### Short-term: TypeSpec Source Updates

Add `@@scope` decorators to orphaned model definitions in TypeSpec:

```typescript
// For Response-related models
@@scope(Response, "!(csharp, python, java, javascript)")
@@scope(ResponseError, "!(csharp, python, java, javascript)")
@@scope(ResponseUsage, "!(csharp, python, java, javascript)")
// ... and all other Response* models

// For Insight-related models
@@scope(AgentClusterInsightResult, "!(csharp, python, java, javascript)")
@@scope(EvaluationComparisonRequest, "!(csharp, python, java, javascript)")
// ... and so on
```

Or scope entire namespaces:

```typescript
@@scope(ResponseModels, "!(csharp, python, java, javascript)")
namespace ResponseModels {
  model Response { ... }
  model ResponseError { ... }
  // etc.
}
```

### Long-term: Generator Improvements

Enhance the TypeSpec-to-Python generator to:

1. **Analyze reachability** before emitting models
2. **Warn about orphaned models** during generation
3. **Provide automatic scoping** for unreachable models
4. **Generate dependency graphs** for verification

---

## Appendix: Complete Lists

### All 95 Orphaned Classes (Alphabetical)

AgentClusterInsightResult, AgentClusterInsightsRequest, AgentId, AgentReference, AgentTaxonomyInput, AISearchIndexResource, ApproximateLocation, AzureAIAgentTarget, ChartCoordinate, ClusterInsightResult, ClusterTokenUsage, ComparisonFilter, CompoundFilter, Coordinate, EmbeddingConfiguration, EvalCompareReport, EvalResult, EvalRunResultCompareItem, EvalRunResultComparison, EvalRunResultSummary, EvaluationComparisonRequest, EvaluationResultSample, EvaluationRunClusterInsightResult, EvaluationRunClusterInsightsRequest, InsightCluster, InsightSample, InsightSummary, InsightsMetadata, Location, Prompt, RankingOptions, Response, ResponseCodeInterpreterCallCodeDeltaEvent, ResponseCodeInterpreterCallCodeDoneEvent, ResponseCodeInterpreterCallCompletedEvent, ResponseCodeInterpreterCallInProgressEvent, ResponseCodeInterpreterCallInterpretingEvent, ResponseCompletedEvent, ResponseContentPartAddedEvent, ResponseContentPartDoneEvent, ResponseConversation1, ResponseCreatedEvent, ResponseError, ResponseErrorEvent, ResponseFailedEvent, ResponseFileSearchCallCompletedEvent, ResponseFileSearchCallInProgressEvent, ResponseFileSearchCallSearchingEvent, ResponseFunctionCallArgumentsDeltaEvent, ResponseFunctionCallArgumentsDoneEvent, ResponseImageGenCallCompletedEvent, ResponseImageGenCallGeneratingEvent, ResponseImageGenCallInProgressEvent, ResponseImageGenCallPartialImageEvent, ResponseInProgressEvent, ResponseIncompleteDetails1, ResponseIncompleteEvent, ResponseMCPCallArgumentsDeltaEvent, ResponseMCPCallArgumentsDoneEvent, ResponseMCPCallCompletedEvent, ResponseMCPCallFailedEvent, ResponseMCPCallInProgressEvent, ResponseMCPListToolsCompletedEvent, ResponseMCPListToolsFailedEvent, ResponseMCPListToolsInProgressEvent, ResponseOutputItemAddedEvent, ResponseOutputItemDoneEvent, ResponsePromptVariables, ResponseQueuedEvent, ResponseReasoningDeltaEvent, ResponseReasoningDoneEvent, ResponseReasoningSummaryDeltaEvent, ResponseReasoningSummaryDoneEvent, ResponseReasoningSummaryPartAddedEvent, ResponseReasoningSummaryPartDoneEvent, ResponseReasoningSummaryTextDeltaEvent, ResponseReasoningSummaryTextDoneEvent, ResponseRefusalDeltaEvent, ResponseRefusalDoneEvent, ResponseStreamEvent, ResponsesAssistantMessageItemParam, ResponsesAssistantMessageItemResource, ResponsesDeveloperMessageItemParam, ResponsesDeveloperMessageItemResource, ResponsesMessageItemParam, ResponsesMessageItemResource, ResponsesSystemMessageItemParam, ResponsesSystemMessageItemResource, ResponsesUserMessageItemParam, ResponsesUserMessageItemResource, ResponseText, ResponseTextDeltaEvent, ResponseTextDoneEvent, ResponseTextFormatConfiguration, ResponseTextFormatConfigurationJsonObject, ResponseTextFormatConfigurationJsonSchema, ResponseTextFormatConfigurationText, ResponseUsage, ResponseWebSearchCallCompletedEvent, ResponseWebSearchCallInProgressEvent, ResponseWebSearchCallSearchingEvent, Target, TargetConfig, TaxonomyCategory, TaxonomySubCategory, WorkflowActionOutputItemResource

### TypeSpec Repository Reference

**TypeSpec Source Location:**  
https://github.com/Azure/azure-rest-api-specs/tree/feature/foundry/specification/ai/Foundry

**Key File:**  
`client.tsp` - Contains operation scope decorators like:

```typescript
@@scope(Responses.createResponse, "!(csharp, python, java, javascript)")
```

---

## Conclusion

This analysis identified 95 orphaned model classes in the azure-ai-projects Python SDK that are not used by any client operations. The primary cause is that TypeSpec operation scope decorators prevent method generation, but model definitions lack corresponding scope restrictions.

The recommended solution is to add `@@scope` decorators to these model definitions in the TypeSpec source files to prevent their emission in Python (and other) SDKs where the operations are not supported.

---

**Report Generated By:** GitHub Copilot  
**Analysis Tool:** Transitive dependency graph analysis with breadth-first search  
**Validation:** Cross-referenced with operation signatures in `_operations.py`
