# Azure QnA for Python

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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/68e7988aba481206f08019d3efb585683d5bc577/specification/cognitiveservices/data-plane/Language/preview/2021-07-15-preview/questionanswering.json
output-folder: ../azure/ai/language/questionanswering
namespace: azure.ai.language.questionanswering
package-name: azure-ai-language-questionanswering
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: QuestionAnsweringClient
version-tolerant: true
models-mode: msrest
package-version: 1.0.0b2
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
```

### Rename "QuestionAnsweringKnowledgeBase_Query" -> "QueryKnowledgeBase"

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/:query-knowledgebases"]["post"]
    transform: >
        $["operationId"] = "queryKnowledgeBase";
```

### Rename "QuestionAnsweringText_Query" -> "QueryText"

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/:query-text"]["post"]
    transform: >
        $["operationId"] = "queryText";
```

### Rename `KnowledgeBasedQueryOptions` -> `Options`

```yaml
directive:
  - from: swagger-document
    where: $["parameters"]["KnowledgeBaseQueryOptions"]
    transform: >
        $["x-ms-client-name"] = "Options";
```

### Rename `TextQueryOptions` -> `Options`

```yaml
directive:
  - from: swagger-document
    where: $["parameters"]["TextQueryOptions"]
    transform: >
        $["x-ms-client-name"] = "Options";
```

### Rename `KnowledgeBaseQueryOptions` -> `QueryKnowledgeBaseOptions`

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["KnowledgeBaseQueryOptions"]
    transform: >
        $["x-ms-client-name"] = "QueryKnowledgeBaseOptions";
```

### Rename `TextQueryOptions` -> `QueryTextOptions`

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["TextQueryOptions"]
    transform: >
        $["x-ms-client-name"] = "QueryTextOptions";
```

### Delete `StringIndexType`

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["TextQueryOptions"]
    transform: >
        delete $.properties["stringIndexType"]
```