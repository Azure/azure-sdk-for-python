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
input-file: https://raw.githubusercontent.com/mshaban-msft/azure-rest-api-specs/mshaban/cognitive-language-2022-05-15-swagger-fixes/specification/cognitiveservices/data-plane/Language/preview/2022-05-15-preview/analyzeconversations.json
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
models-mode: msrest
package-version: 1.0.0b4
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
modelerfour:
  lenient-model-deduplication: true
```

## Fix generation errors

### Fix `duplicate schema` errors in `Task State`

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["TaskState"]["properties"]
      transform: >
        $["status"]["x-ms-enum"]["name"] = "TaskStateEnum";
```

### Fix `duplicate schema` errors in `Job State`

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["JobState"]["properties"]
      transform: >
        $["status"]["x-ms-enum"]["name"] = "JobStateEnum";
```

## Rename Client Operations 

### CLU Analyze Operation

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversation"]["post"]
      transform: >
          $["operationId"] = "analyzeConversation";
```

### Async Analyze Operation POST

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/analyze-conversation/jobs"]["post"]
      transform: >
          $["operationId"] = "submitConversationJob";
```

### Async Analyze Operation GET

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/analyze-conversation/jobs/{jobId}"]["get"]
      transform: >
          $["operationId"] = "getConversationJobStatus";
```

## Sync API Directives

### Rename `body` to `tasks`

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversation"]["post"]
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

```yaml
directive:
  - from: swagger-document
    where: '$.paths["/analyze-conversation/jobs"].post'
    transform: >
      $["responses"]["200"] = {
          "description": "dummy schema to get poller response when calling .result()",
          "schema": {
              "$ref": "#/definitions/AnalyzeConversationJobState"
          }
      };
```

## Fix Swagger/API mismatch errors

### Change api version

```yaml
directive:
    - from: swagger-document
      where: $["info"]
      transform: >
          $["version"] = "2022-04-01-preview";
```

<!-- ### Invalid urls -->

### Fix mis-matching task types

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["AnalyzeConversationSummarizationTask"]
      transform: >
        $["x-ms-discriminator-value"] = "IssueResolutionSummarization";
```

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["AnalyzeConversationPIITask"]
      transform: >
        $["x-ms-discriminator-value"] = "ConversationPII";
```

### Fix `modality` required errors and default values

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["ConversationItemBase"]
      transform: >
        $["required"] = ["id", "participantId", "modality"];
```

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]
      transform: >
        $["ConversationItemBase"]["discriminator"] = "modality";
```

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]
      transform: >
        $["TextConversationItem"]["x-ms-discriminator-value"] = "text";
```

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]
      transform: >
        $["TranscriptConversationItem"]["x-ms-discriminator-value"] = "transcript";
```

### Fix `summary aspects` to be string instead of enum

```yaml
directive:
    - from: swagger-document
      where: $["definitions"]["ConversationSummarizationTaskParameters"]
      transform: >
        $["properties"]["summaryAspects"] = {
            "type": "string",
            "enum": [
              "Issue",
              "Resolution",
              "Issue, Resolution"
            ],
            "x-ms-enum": {
              "name": "SummaryAspectEnum",
              "modelAsString": true
            }
          };
```
