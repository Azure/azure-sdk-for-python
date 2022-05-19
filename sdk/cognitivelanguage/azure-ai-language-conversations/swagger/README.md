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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/release-cognitiveservices-Language-2022-05-01-preview/specification/cognitiveservices/data-plane/Language/preview/2022-05-15-preview/analyzeconversations.json
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

### Fix `enum` error

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["CustomConversationTaskParameters"]
    transform: >
        delete $.properties["stringIndexType"]
```

## Rename Client Operations 

### CLU Analyze Operation

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversations"]["post"]
      transform: >
          $["operationId"] = "analyzeConversation";
```

### Async Analyze Operation POST

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/analyze-conversations/jobs"]["post"]
      transform: >
          $["operationId"] = "submitConversationJob";
```

### Async Analyze Operation GET

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/analyze-conversations/jobs/{jobId}"]["get"]
      transform: >
          $["operationId"] = "getConversationJobStatus";
```

## CLU Directives

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

## Temporary changes

### Change api version

```yaml
directive:
    - from: swagger-document
      where: $["info"]
      transform: >
          $["version"] = "2022-04-01-preview";
```