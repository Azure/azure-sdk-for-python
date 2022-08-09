# Azure Text Analytics Authoring Client for Python

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

## Configuration

```yaml
namespace: azure.ai.language.text
package-name: azure-ai-language-text
license-header: MICROSOFT_MIT_NO_VERSION
no-namespace-folders: true
python: true
tag: release_2022_05_01
openapi-type: data-plane
clear-output-folder: true
version-tolerant: true
package-version: 1.0.0b1
add-credential: true
credential-scopes: https://cognitiveservices.azure.com/.default
black: true
modelerfour:
  lenient-model-deduplication: true
```

## Batch Execution

```yaml
batch:
  - tag: release_authoring_1_0
```

## Authoring

These settings apply only when `--tag=release_authoring_1_0` is specified on the command line.

```yaml $(tag) == 'release_authoring_1_0'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/Language/stable/2022-05-01/analyzetext-authoring.json
output-folder: ../azure/ai/language/text/authoring
title: TextAuthoringClient
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
```

### Authoring API Directives

```yaml $(tag) == 'release_authoring_1_0'
# Give LROs return types
directive:
  - where-operation: TextAnalysisAuthoring_DeleteProject
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/TextAnalysisAuthoringProjectDeletionJobState"
        }
      };
  - where-operation: TextAnalysisAuthoring_Export
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/TextAnalysisAuthoringExportProjectJobState"
        }
      };
  - where-operation: TextAnalysisAuthoring_Import
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/TextAnalysisAuthoringImportProjectJobState"
        }
      };
  - where-operation: TextAnalysisAuthoring_Train
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/TextAnalysisAuthoringTrainingJobState"
        }
      };
  - where-operation: TextAnalysisAuthoring_DeployProject
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/TextAnalysisAuthoringDeploymentJobState"
        }
      };
  - where-operation: TextAnalysisAuthoring_SwapDeployments
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/TextAnalysisAuthoringDeploymentJobState"
        }
      };
  - where-operation: TextAnalysisAuthoring_DeleteDeployment
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/TextAnalysisAuthoringDeploymentJobState"
        }
      };
  - where-operation: TextAnalysisAuthoring_CancelTrainingJob
    transform: >
      $["responses"]["200"] = {
        "description": "dummy schema to get poller response when calling .result()",
        "schema": {
          "$ref": "#/definitions/TextAnalysisAuthoringTrainingJobState"
        }
      };
```

```yaml $(tag) == 'release_authoring_1_0'
# Rename Authoring client operations
directive:
  - rename-operation:
      from: TextAnalysisAuthoring_ListProjects
      to: ListProjects
  - rename-operation:
      from: TextAnalysisAuthoring_CreateProject
      to: CreateProject
  - rename-operation:
      from: TextAnalysisAuthoring_GetProject
      to: GetProject
  - rename-operation:
      from: TextAnalysisAuthoring_DeleteProject
      to: DeleteProject
  - rename-operation:
      from: TextAnalysisAuthoring_Export
      to: Export
  - rename-operation:
      from: TextAnalysisAuthoring_Import
      to: Import
  - rename-operation:
      from: TextAnalysisAuthoring_Train
      to: Train
  - rename-operation:
      from: TextAnalysisAuthoring_ListDeployments
      to: ListDeployments
  - rename-operation:
      from: TextAnalysisAuthoring_SwapDeployments
      to: SwapDeployments
  - rename-operation:
      from: TextAnalysisAuthoring_GetDeployment
      to: GetDeployment
  - rename-operation:
      from: TextAnalysisAuthoring_DeployProject
      to: DeployProject
  - rename-operation:
      from: TextAnalysisAuthoring_DeleteDeployment
      to: DeleteDeployment
  - rename-operation:
      from: TextAnalysisAuthoring_GetDeploymentStatus
      to: GetDeploymentStatus
  - rename-operation:
      from: TextAnalysisAuthoring_GetSwapDeploymentsStatus
      to: GetSwapDeploymentsStatus
  - rename-operation:
      from: TextAnalysisAuthoring_GetExportStatus
      to: GetExportStatus
  - rename-operation:
      from: TextAnalysisAuthoring_GetImportStatus
      to: GetImportStatus
  - rename-operation:
      from: TextAnalysisAuthoring_ListTrainedModels
      to: ListTrainedModels
  - rename-operation:
      from: TextAnalysisAuthoring_GetTrainedModel
      to: GetTrainedModel
  - rename-operation:
      from: TextAnalysisAuthoring_DeleteTrainedModel
      to: DeleteTrainedModel
  - rename-operation:
      from: TextAnalysisAuthoring_GetModelEvaluationResults
      to: ListModelEvaluationResults
  - rename-operation:
      from: TextAnalysisAuthoring_GetModelEvaluationSummary
      to: GetModelEvaluationSummary
  - rename-operation:
      from: TextAnalysisAuthoring_ListTrainingJobs
      to: ListTrainingJobs
  - rename-operation:
      from: TextAnalysisAuthoring_GetTrainingStatus
      to: GetTrainingStatus
  - rename-operation:
      from: TextAnalysisAuthoring_CancelTrainingJob
      to: CancelTrainingJob
  - rename-operation:
      from: TextAnalysisAuthoring_GetProjectDeletionStatus
      to: GetProjectDeletionStatus
  - rename-operation:
      from: TextAnalysisAuthoring_GetSupportedLanguages
      to: ListSupportedLanguages
  - rename-operation:
      from: TextAnalysisAuthoring_ListTrainingConfigVersions
      to: ListTrainingConfigVersions
  
```