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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/Language/preview/2022-03-01-preview/analyzeconversations.json
output-folder: ../azure/ai/language/conversations
namespace: azure.ai.language.conversations
package-name: azure-ai-language-conversations
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: ConversationAnalysisClient
version-tolerant: true
models-mode: msrest
package-version: 1.0.0b3
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
```

### Remove intermediary object from analyze operation call

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversations"]["post"]
      transform: >
          $["operationId"] = "analyzeConversation";
```

### Rename body to tasks

```yaml
directive:
    - from: swagger-document
      where: $["paths"]["/:analyze-conversations"]["post"]
      transform: >
        $["parameters"][1]["x-ms-client-name"] = "task";
```

### Rename 'confidenceScore' in Qna intent result

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

### Set default values for ParticipantID, and ConversationID

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

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["CustomConversationTaskParameters"]
    transform: >
        delete $.properties["stringIndexType"]
```