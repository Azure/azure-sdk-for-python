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