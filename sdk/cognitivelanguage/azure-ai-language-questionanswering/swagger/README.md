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
namespace: azure.ai.language.questionanswering
package-name: azure-ai-language-questionanswering
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
version-tolerant: true
package-version: 1.1.0b3
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/34a2c0723155d134311419fd997925ce96b85bec/specification/cognitiveservices/data-plane/Language/stable/2021-10-01/questionanswering.json
output-folder: ../azure/ai/language/questionanswering
models-mode: msrest
title: QuestionAnsweringClient
```

## Authoring

These settings apply only when `--tag=release_authoring_1_1_preview` is specified on the command line.

```yaml $(tag) == 'release_authoring_1_1_preview'
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/Language/stable/2021-10-01/questionanswering-authoring.json
output-folder: ../azure/ai/language/questionanswering/projects
title: QuestionAnsweringProjectsClient
```



## Customizations

### Runtime


#### Rename "QuestionAnsweringKnowledgeBase_Query" -> "GetAnswers"

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/:query-knowledgebases"]["post"]
    transform: >
        $["operationId"] = "getAnswers";
```

#### Rename "QuestionAnsweringText_Query" -> "GetAnswersFromText"

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/:query-text"]["post"]
    transform: >
        $["operationId"] = "getAnswersFromText";
```

#### Rename `KnowledgeBasedQueryOptions` -> `Options`

```yaml
directive:
  - from: swagger-document
    where: $["parameters"]["AnswersOptions"]
    transform: >
        $["x-ms-client-name"] = "Options";
```

#### Rename `TextQueryOptions` -> `Options`

```yaml
directive:
  - from: swagger-document
    where: $["parameters"]["AnswersFromTextOptions"]
    transform: >
        $["x-ms-client-name"] = "Options";
```

#### Delete `StringIndexType`

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AnswersFromTextOptions"]
    transform: >
        delete $.properties["stringIndexType"]
```

#### Delete `RankerKind` and `LogicalOperationKind` enums

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

#### Make `MetadataFilter`'s `metadata` property a list of string

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
        delete $["MetadataFilter"]["properties"]["metadata"]["items"]["$ref"];
        $["MetadataFilter"]["properties"]["metadata"]["items"]["type"] = "object";
        delete $["MetadataRecord"];
```

### Authoring


#### Remove operation group

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects"]["get"]
    transform: >
        $["operationId"] = "listProjects";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}"]["get"]
    transform: >
        $["operationId"] = "getProjectDetails";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}"]["patch"]
    transform: >
        $["operationId"] = "createProject";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}"]["delete"]
    transform: >
        $["operationId"] = "deleteProject";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/:export"]["post"]
    transform: >
        $["operationId"] = "export";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/:import"]["post"]
    transform: >
        $["operationId"] = "importAssets";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/deployments/{deploymentName}"]["put"]
    transform: >
        $["operationId"] = "deployProject";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/deployments"]["get"]
    transform: >
        $["operationId"] = "listDeployments";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/synonyms"]["get"]
    transform: >
        $["operationId"] = "listSynonyms";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/synonyms"]["put"]
    transform: >
        $["operationId"] = "updateSynonyms";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/sources"]["get"]
    transform: >
        $["operationId"] = "listSources";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/sources"]["patch"]
    transform: >
        $["operationId"] = "updateSources";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/qnas"]["get"]
    transform: >
        $["operationId"] = "listQnas";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/qnas"]["patch"]
    transform: >
        $["operationId"] = "updateQnas";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/feedback"]["post"]
    transform: >
        $["operationId"] = "addFeedback";
```

#### Remove status operations

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/deletion-jobs/{jobId}"]
    transform: >
        delete $["get"];
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/export/jobs/{jobId}"]
    transform: >
        delete $["get"];
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/import/jobs/{jobId}"]
    transform: >
        delete $["get"];
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/deployments/{deploymentName}/jobs/{jobId}"]
    transform: >
        delete $["get"];
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/sources/jobs/{jobId}"]
    transform: >
        delete $["get"];
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/qnas/jobs/{jobId}"]
    transform: >
        delete $["get"];
```

#### Rename body parameter

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/feedback"]["post"]
    transform: >
        $["parameters"][2]["x-ms-client-name"] = "feedback";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/qnas"]["patch"]
    transform: >
        $["parameters"][2]["x-ms-client-name"] = "qnas";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/sources"]["patch"]
    transform: >
        $["parameters"][2]["x-ms-client-name"] = "sources";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/synonyms"]["put"]
    transform: >
        $["parameters"][2]["x-ms-client-name"] = "synonyms";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}/:import"]["post"]
    transform: >
        $["parameters"][2]["x-ms-client-name"] = "options";
  - from: swagger-document
    where: $["paths"]["/query-knowledgebases/projects/{projectName}"]["patch"]
    transform: >
        $["parameters"][1]["x-ms-client-name"] = "options";
```
