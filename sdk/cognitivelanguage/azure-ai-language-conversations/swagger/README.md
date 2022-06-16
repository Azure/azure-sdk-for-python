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
tag: release_2022_05_01
openapi-type: data-plane
version-tolerant: true
package-version: 1.0.0
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
modelerfour:
  lenient-model-deduplication: true
```

## Batch Execution

```yaml
batch:
  - tag: release_runtime_1_0
  - tag: release_authoring_1_0
```

## Runtime

These settings apply only when `--tag=release_runtime_1_0` is specified on the command line.

```yaml $(tag) == 'release_runtime_1_0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/Language/stable/2022-05-01/analyzeconversations.json
output-folder: ../azure/ai/language/conversations
title: ConversationAnalysisClient
```

## Authoring

These settings apply only when `--tag=release_authoring_1_0` is specified on the command line.

```yaml $(tag) == 'release_authoring_1_0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/Language/stable/2022-05-01/analyzeconversations-authoring.json
output-folder: ../azure/ai/language/conversations/projects
title: ConversationAnalysisProjectsClient
```

## Runtime API Directives

### Rename Runtime client operation

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversations"]["post"]
      transform: >
          $["operationId"] = "AnalyzeConversation";
```

### Rename `body` to `tasks`

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversations"]["post"]
      transform: >
        $["parameters"][1]["x-ms-client-name"] = "task";
```

## Authoring API Directives

### Give LROs return types

```yaml $(tag) == 'release_authoring_1_0'
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
          "$ref": "#/definitions/ConversationalAnalysisAuthoringDeploymentJobState"
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


### Rename Authoring client operations

```yaml $(tag) == 'release_authoring_1_0'
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
      to: GetDeploymentStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetSwapDeploymentsStatus
      to: GetSwapDeploymentsStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetExportStatus
      to: GetExportStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetImportStatus
      to: GetImportStatus
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
      to: GetModelEvaluationResults
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetModelEvaluationSummary
      to: GetModelEvaluationSummary
  - rename-operation:
      from: ConversationalAnalysisAuthoring_ListTrainingJobs
      to: ListTrainingJobs
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetTrainingStatus
      to: GetTrainingStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_CancelTrainingJob
      to: CancelTrainingJob
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetProjectDeletionStatus
      to: GetProjectDeletionStatus
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetSupportedLanguages
      to: GetSupportedLanguages
  - rename-operation:
      from: ConversationalAnalysisAuthoring_GetSupportedPrebuiltEntities
      to: GetSupportedPrebuiltEntities
  - rename-operation:
      from: ConversationalAnalysisAuthoring_ListTrainingConfigVersions
      to: ListTrainingConfigVersions
```