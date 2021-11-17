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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/34a2c0723155d134311419fd997925ce96b85bec/specification/cognitiveservices/data-plane/Language/stable/2021-10-01/questionanswering-authoring.json
output-folder: ../../azure/ai/language/questionanswering/projects
namespace: azure.ai.language.questionanswering.projects
package-name: azure-ai-language-questionanswering
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: QuestionAnsweringProjectsClient
version-tolerant: true
models-mode: msrest
keep-version-file: true
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
```
