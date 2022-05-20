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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/d1716d13b0814a9d0785eda9a74529a315212f53/specification/cognitiveservices/data-plane/Language/preview/2022-05-15-preview/analyzeconversations.json
output-folder: ../azure/ai/language/conversations
namespace: azure.ai.language.conversations
package-name: azure-ai-language-conversations
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: ConversationAnalysisClient
tag: release_2022_05_01_preview
openapi-type: data-plane
version-tolerant: true
package-version: 1.0.0b4
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
modelerfour:
  lenient-model-deduplication: true
```

## Fix generation errors

### Fix `duplicate-schema` errors in `TaskState`

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["TaskState"]["properties"]
      transform: >
        $["status"]["x-ms-enum"]["name"] = "TaskStateEnum";
```

### Fix `duplicate-schema` errors in `JobState`

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["JobState"]["properties"]
      transform: >
        $["status"]["x-ms-enum"]["name"] = "JobStateEnum";
```

## Rename client operations 
<!-- 
### Sync `analyze operation - POST`

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversations"]["post"]
      transform: >
          $["operationId"] = "analyzeConversation";
```
 -->
### Async `analyze operation - POST`

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/analyze-conversations/jobs"]["post"]
      transform: >
          $["operationId"] = "conversationAnalysis";
```

### Remove unnecessary async `analyze operation - GET`

```yaml
directive:
    - from: swagger-document
      where: $["paths"]
      transform: >
          delete $["/analyze-conversations/jobs/{jobId}"];
```

## Sync API Directives

### Rename `body` to `tasks`

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversations"]["post"]
      transform: >
        $["parameters"][1]["x-ms-client-name"] = "task";
```

### Unify `confidenceScore` in Qna intent result

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["KnowledgeBaseAnswer"]["properties"]["confidenceScore"]
      transform: >
        $["x-ms-client-name"] = "confidence";
```

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["AnswerSpan"]["properties"]["confidenceScore"]
      transform: >
        $["x-ms-client-name"] = "confidence";
```

### Set default values for `ParticipantID`, and `ConversationID`

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["ConversationItemBase"]["properties"]["participantId"]
      transform: >
        $["x-ms-client-default"] = 1;
```

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["ConversationItemBase"]["properties"]["id"]
      transform: >
        $["x-ms-client-default"] = 1;
```

### Fix `enum` error

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["CustomConversationTaskParameters"]
    transform: >
        delete $.properties["stringIndexType"]
```

## Async APIs Directives

### Make LRO poller for analyze operation get result
```yaml
directive:
  - from: swagger-document
    where: '$.paths["/analyze-conversations/jobs"].post'
    transform: >
      $["responses"]["200"] = {
          "description": "dummy schema to get poller response when calling .result()",
          "schema": {
              "$ref": "#/definitions/AnalyzeConversationJobState"
          }
      };
```

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/analyze-conversations/jobs"]["post"]
      transform: >
        $["parameters"][1]["x-ms-client-name"] = "jobs";
```

### Rename `body` to `tasks`

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/analyze-conversations/jobs"]["post"]
      transform: >
        $["parameters"][1]["x-ms-client-name"] = "task";
```

## Fix Swagger/API mismatch errors

### Fix task types - `async POST analyze api`

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["AnalyzeConversationResultsKind"]
      transform: >
        $["enum"] = ["conversationalSummarizationResults", "conversationalPIIResults"];
```

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["AnalyzeConversationSummarizationResult"]
      transform: >
        $["x-ms-discriminator-value"] = "conversationalSummarizationResults";
```

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["AnalyzeConversationConversationPIIResult"]
      transform: >
        $["x-ms-discriminator-value"] = "conversationalPIIResults";
```

