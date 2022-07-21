# Azure Conversations Client for Python

> see https://aka.ms/autorest

### Setup

Install Autorest v3

```ps
npm install -g autorest
```

### Generation

```ps
cd <swagger-folder>
autorest
```

### Settings

```yaml
namespace: azure.ai.language.conversations
package-name: azure-ai-language-conversations
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
tag: release_2022_05_15_preview
openapi-type: data-plane
version-tolerant: true
package-version: 1.1.0b2
add-credential: true
credential-scopes: https://cognitiveservices.azure.com/.default
black: true
modelerfour:
  lenient-model-deduplication: true
```

## Batch Execution

```yaml
batch:
  - tag: release_runtime_1_1_preview
  - tag: release_authoring_1_1_preview
```

## Runtime

These settings apply only when `--tag=release_runtime_1_1_preview` is specified on the command line.

```yaml $(tag) == 'release_runtime_1_1_preview'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/e7f37e4e43b1d12fd1988fda3ed39624c4b23303/specification/cognitiveservices/data-plane/Language/preview/2022-05-15-preview/analyzeconversations.json
output-folder: ../azure/ai/language/conversations
title: ConversationAnalysisClient
```

## Authoring

These settings apply only when `--tag=release_authoring_1_1_preview` is specified on the command line.

```yaml $(tag) == 'release_authoring_1_1_preview'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/e7f37e4e43b1d12fd1988fda3ed39624c4b23303/specification/cognitiveservices/data-plane/Language/preview/2022-05-15-preview/analyzeconversations-authoring.json
output-folder: ../azure/ai/language/conversations/authoring
title: ConversationAuthoringClient
```

## Customizations

Customizations that should eventually be added to central autorest configuration.

### General customizations

```yaml
directive:
# Support automatically generating code for key credentials.
- from: swagger-document
  where: $.securityDefinitions
  transform: |
    $["AzureKey"] = $["apim_key"];
    delete $["apim_key"];

- from: swagger-document
  where: $.security
  transform: |
    $ = [
        {
          "AzureKey": []
        }
    ];

# Fix Endpoint parameter description and format.
- from: swagger-document
  where: $.parameters.Endpoint
  transform: |
    $["description"] = "Supported Cognitive Services endpoint (e.g., https://<resource-name>.cognitiveservices.azure.com).";
    $["format"] = "url";

# Define multilingual parameter as a boolean.
- where-operation: ConversationalAnalysisAuthoring_GetSupportedPrebuiltEntities
  transform: |
    var multilingualParam = $.parameters.find(param => param.name === "multilingual");
    multilingualParam.type = "boolean";
```

### Python customizations

```yaml
directive:
# Always default to UnicodeCodePoint string indices.
- from: swagger-document
  where: $.definitions.StringIndexType
  transform: |
    $["description"] = "Specifies the method used to interpret string offsets. Set to \"UnicodeCodePoint\" for Python strings.";
    $["x-ms-client-default"] = "UnicodeCodePoint";

# Only Utf16CodeUnit is supported for these types right now. Once UnicodeCodePoint is supported we can default to that.
# - from: swagger-document
#   where: $.definitions.ConversationalAnalysisAuthoringStringIndexType
#   transform: |
#     $["description"] = "Specifies the method used to interpret string offsets. Set to \"UnicodeCodePoint\" for Python strings.";
#     $["x-ms-client-default"] = "UnicodeCodePoint";

# - from: swagger-document
#   where: $.parameters.ConversationalAnalysisAuthoringStringIndexTypeQueryParameter
#   transform: |
#     $["description"] = "Specifies the method used to interpret string offsets. Set to \"UnicodeCodePoint\" for Python strings.";
#     $["x-ms-client-default"] = "UnicodeCodePoint";
```


### Runtime API Directives

```yaml $(tag) == 'release_runtime_1_1_preview'
# Give analyze job LRO a return type
directive:
  - where-operation: AnalyzeConversation_SubmitJob
    transform: >
      $["responses"]["200"] = {
          "description": "dummy schema to get poller response when calling .result()",
          "schema": {
              "$ref": "#/definitions/AnalyzeConversationJobState"
          }
      };
```

```yaml $(tag) == 'release_runtime_1_1_preview'
# Rename Runtime client operation
directive:
  - rename-operation:
      from: ConversationAnalysis_AnalyzeConversation
      to: AnalyzeConversation
```

```yaml $(tag) == 'release_runtime_1_1_preview'
# Rename Runtime client async operation
directive:
  - rename-operation:
      from: AnalyzeConversation_SubmitJob
      to: ConversationAnalysis
```

```yaml $(tag) == 'release_runtime_1_1_preview'
# Rename analyze_conversation `body` to `tasks`
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversations"]["post"]
      transform: >
        $["parameters"][1]["x-ms-client-name"] = "task";
```

```yaml $(tag) == 'release_runtime_1_1_preview'
# Rename begin_conversation_analysis `body` to `tasks`
directive:
    - from: swagger-document
      where: $["paths"]["/analyze-conversations/jobs"]["post"]
      transform: >
        $["parameters"][1]["x-ms-client-name"] = "task";
```

```yaml $(tag) == 'release_runtime_1_1_preview'
# Remove async GET operation status
directive:
    - from: swagger-document
      where: $["paths"]
      transform: >
          delete $["/analyze-conversations/jobs/{jobId}"];
```

```yaml $(tag) == 'release_runtime_1_1_preview'
# Remove async cancel operation
directive:
    - from: swagger-document
      where: $["paths"]
      transform: >
          delete $["/analyze-conversations/jobs/{jobId}:cancel"];
```

### Authoring API Directives

```yaml $(tag) == 'release_authoring_1_1_preview'
# Give LROs return types
directive:
  - where-operation: ConversationalAnalysisAuthoring_CancelTrainingJob
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/ConversationalAnalysisAuthoringTrainingJobState"
        }
      };
  - where-operation: ConversationalAnalysisAuthoring_DeleteDeployment
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/ConversationalAnalysisAuthoringDeploymentJobState"
        }
      };
  - where-operation: ConversationalAnalysisAuthoring_DeleteProject
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/ConversationalAnalysisAuthoringProjectDeletionJobState"
        }
      };
  - where-operation: ConversationalAnalysisAuthoring_DeployProject
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/ConversationalAnalysisAuthoringProjectDeployment"
        }
      };
  - where-operation: ConversationalAnalysisAuthoring_Export
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/ConversationalAnalysisAuthoringExportProjectJobState"
        }
      };
  - where-operation: ConversationalAnalysisAuthoring_Import
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/ConversationalAnalysisAuthoringImportProjectJobState"
        }
      };
  - where-operation: ConversationalAnalysisAuthoring_SwapDeployments
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/ConversationalAnalysisAuthoringDeploymentJobState"
        }
      };
  - where-operation: ConversationalAnalysisAuthoring_Train
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/ConversationalAnalysisAuthoringTrainingJobState"
        }
      };
```

```yaml $(tag) == 'release_authoring_1_1_preview'
# Rename `body` param for operations
directive:
  - where-operation: ConversationalAnalysisAuthoring_DeployProject
    transform: >
        $.parameters[2]["x-ms-client-name"] = "deployment";
  - where-operation: ConversationalAnalysisAuthoring_Import
    transform: >
        $.parameters[2]["x-ms-client-name"] = "project";
  - where-operation: ConversationalAnalysisAuthoring_SwapDeployments
    transform: >
        $.parameters[1]["x-ms-client-name"] = "deployments";
  - where-operation: ConversationalAnalysisAuthoring_Train
    transform: >
        $.parameters[1]["x-ms-client-name"] = "configuration";
  - where-operation: ConversationalAnalysisAuthoring_CreateProject
    transform: >
        $.parameters[1]["x-ms-client-name"] = "project";
```

```yaml $(tag) == 'release_authoring_1_1_preview'
# Rename Authoring client operations
directive:
  - rename-operation:
      from: ConversationalAnalysisAuthoring_ListProjects
      to: ListProjects
  - rename-operation:
      from: ConversationalAnalysisAuthoring_CreateProject
      to: CreateProject
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetProject
      to: GetProject
  - rename-operation:
      from: ConversationalAnalysisAuthoring_DeleteProject
      to: DeleteProject
  - rename-operation:
      from: ConversationalAnalysisAuthoring_Export
      to: ExportProject
  - rename-operation:
      from: ConversationalAnalysisAuthoring_Import
      to: ImportProject
  - rename-operation:
      from: ConversationalAnalysisAuthoring_Train
      to: Train
  - rename-operation:
      from: ConversationalAnalysisAuthoring_ListDeployments
      to: ListDeployments
  - rename-operation:
      from: ConversationalAnalysisAuthoring_SwapDeployments
      to: SwapDeployments
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetDeployment
      to: GetDeployment
  - rename-operation:
      from: ConversationalAnalysisAuthoring_DeployProject
      to: DeployProject
  - rename-operation:
      from: ConversationalAnalysisAuthoring_DeleteDeployment
      to: DeleteDeployment
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetDeploymentStatus
      to: GetDeploymentJobStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetSwapDeploymentsStatus
      to: GetSwapDeploymentsJobStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetExportStatus
      to: GetExportProjectJobStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetImportStatus
      to: GetImportProjectJobStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_ListTrainedModels
      to: ListTrainedModels
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetTrainedModel
      to: GetTrainedModel
  - rename-operation:
      from: ConversationalAnalysisAuthoring_DeleteTrainedModel
      to: DeleteTrainedModel
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetModelEvaluationResults
      to: ListModelEvaluationResults
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetModelEvaluationSummary
      to: GetModelEvaluationSummary
  - rename-operation:
      from: ConversationalAnalysisAuthoring_ListTrainingJobs
      to: ListTrainingJobs
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetTrainingStatus
      to: GetTrainingJobStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_CancelTrainingJob
      to: CancelTrainingJob
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetProjectDeletionStatus
      to: GetProjectDeletionJobStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetSupportedLanguages
      to: ListSupportedLanguages
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetSupportedPrebuiltEntities
      to: ListSupportedPrebuiltEntities
  - rename-operation:
      from: ConversationalAnalysisAuthoring_ListTrainingConfigVersions
      to: ListTrainingConfigVersions
```