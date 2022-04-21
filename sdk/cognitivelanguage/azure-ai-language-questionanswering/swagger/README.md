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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/34a2c0723155d134311419fd997925ce96b85bec/specification/cognitiveservices/data-plane/Language/stable/2021-10-01/questionanswering.json
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
package-version: 1.1.0b1
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
```

### Rename "QuestionAnsweringKnowledgeBase_Query" -> "GetAnswers"

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/:query-knowledgebases"]["post"]
    transform: >
        $["operationId"] = "getAnswers";
```

### Rename "QuestionAnsweringText_Query" -> "GetAnswersFromText"

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/:query-text"]["post"]
    transform: >
        $["operationId"] = "getAnswersFromText";
```

### Rename `KnowledgeBasedQueryOptions` -> `Options`

```yaml
directive:
  - from: swagger-document
    where: $["parameters"]["AnswersOptions"]
    transform: >
        $["x-ms-client-name"] = "Options";
```

### Rename `TextQueryOptions` -> `Options`

```yaml
directive:
  - from: swagger-document
    where: $["parameters"]["AnswersFromTextOptions"]
    transform: >
        $["x-ms-client-name"] = "Options";
```

### Delete `StringIndexType`

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AnswersFromTextOptions"]
    transform: >
        delete $.properties["stringIndexType"]
```

### Delete `RankerKind` and `LogicalOperationKind` enums

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
        delete $["AnswersOptions"]["properties"]["rankerType"]["x-ms-enum"];
        delete $["AnswersOptions"]["properties"]["rankerType"]["enum"];
        delete $["LogicalOperationKind"]["x-ms-enum"];
        delete $["LogicalOperationKind"]["enum"];
```

### Make `MetadataFilter`'s `metadata` property a list of string

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
        delete $["MetadataFilter"]["properties"]["metadata"]["items"]["$ref"];
        $["MetadataFilter"]["properties"]["metadata"]["items"]["type"] = "object";
        delete $["MetadataRecord"];
```