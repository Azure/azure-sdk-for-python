# Azure QnA for Python

> see https://aka.ms/autorest

### Setup

Install Autorest v3

```ps
npm install -g autorest
```

### Generation

```ps
cd <swagger-folder>/authoring
autorest
```

### Settings

```yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/Language/stable/2021-10-01/questionanswering-authoring.json
output-folder: ../../azure/ai/language/questionanswering/projects
namespace: azure.ai.language.questionanswering.projects
package-name: azure-ai-language-questionanswering
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
python3-only: false
title: QuestionAnsweringProjectsClient
version-tolerant: true
keep-version-file: false
package-version: 1.1.0b1
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
```

### Remove operation group

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

### Remove status operations

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

### Rename body parameter

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