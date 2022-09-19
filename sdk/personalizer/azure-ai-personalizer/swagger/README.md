# Azure Personalizer Client for Python

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
namespace: azure.ai.personalizer
package-name: azure-ai-personalizer
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
openapi-type: data-plane
version-tolerant: true
package-version: 1.0.0b1
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
```


## Runtime

```yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/e24bbf6a66cb0a19c072c6f15cee163acbd7acf7/specification/cognitiveservices/data-plane/Personalizer/preview/2022-09-01-preview/Personalizer.json
output-folder: ../azure/ai/personalizer
title: PersonalizerClient
```