# Azure Communication Configuration for Python

> see https://aka.ms/autorest

### Setup

```ps
npm install -g autorest
```

### Generation

```ps
cd <swagger-folder>
autorest SWAGGER.md
```

### Settings

``` yaml
tag: package-sms-2026-01-23
require: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/ee1579c284a9d032eaa70b1a183b661813decd41/specification/communication/data-plane/Sms/readme.md
output-folder: ../azure/communication/sms/_generated
namespace: azure.communication.sms
no-namespace-folders: true
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication SMS Service
models-mode: msrest
```

### Directive to exclude error responses

``` yaml
directive:
  - from: swagger-document
    where: $.definitions
    transform: >
      delete $.BadRequestErrorResponse;
      delete $.ErrorDetail;
      delete $.ErrorResponse;
      delete $.StandardErrorResponse;
```

``` yaml
directive:
  # Update SMS send operation to only expect 202 (success) responses
  # Remove 400 and 401 error responses so they become unexpected and throw HttpResponseException
  - from: swagger-document
    where: '$.paths["/sms"].post.responses'
    transform: >
        const successResponse = $["202"];
        return { "202": successResponse };
  
  # Update OptOuts add operation to only expect 200 (success) responses
  # Remove 400 and 401 error responses so they become unexpected and throw HttpResponseException
  - from: swagger-document
    where: '$.paths["/sms/optouts:add"].post.responses'
    transform: >
        const successResponse = $["200"];
        return { "200": successResponse };
  
  # Update OptOuts remove operation to only expect 200 (success) responses
  # Remove 400 and 401 error responses so they become unexpected and throw HttpResponseException
  - from: swagger-document
    where: '$.paths["/sms/optouts:remove"].post.responses'
    transform: >
        const successResponse = $["200"];
        return { "200": successResponse };
  
  # Update OptOuts check operation to only expect 200 (success) responses
  # Remove 400 and 401 error responses so they become unexpected and throw HttpResponseException
  - from: swagger-document
    where: '$.paths["/sms/optouts:check"].post.responses'
    transform: >
        const successResponse = $["200"];
        return { "200": successResponse };
  
  # Update Delivery Reports get operation to only expect 200 (success) responses
  # Remove 404 error responses so they become unexpected and throw HttpResponseException
  - from: swagger-document
    where: '$.paths["/deliveryReports/{outgoingMessageId}"].get.responses'
    transform: >
        const successResponse = $["200"];
        return { "200": successResponse };
```