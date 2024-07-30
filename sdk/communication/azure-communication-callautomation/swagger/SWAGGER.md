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

```yaml
tag: package-2023-10-03-preview
require: https://github.com/Azure/azure-rest-api-specs/blob/30137c8fce3cc0974cf3fc7c234215bc27e88001/specification/communication/data-plane/CallAutomation/readme.md
output-folder: ../azure/communication/callautomation/_generated
models-mode: msrest
namespace: azure.communication.callautomation
package-name: azure-communication-callautomation
license-header: MICROSOFT_MIT_NO_VERSION
enable-xml: true
clear-output-folder: true
no-namespace-folders: true
python: true
v3: true
no-async: false
add-credential: false
title: Azure Communication Call Automation Service
```

### Rename response to result
```yaml
directive:
- from: swagger-document
  where: $.definitions.RecordingContentType.x-ms-enum
  transform: >
    $["name"] = "RecordingContent";
- from: swagger-document
  where: $.definitions.RecordingChannelType.x-ms-enum
  transform: >
    $["name"] = "RecordingChannel";
- from: swagger-document
  where: $.definitions.RecordingFormatType.x-ms-enum
  transform: >
    $["name"] = "RecordingFormat";
- from: swagger-document
  where: $.definitions.RecordingStorageType.x-ms-enum
  transform: >
    $["name"] = "RecordingStorageKind";
- from: swagger-document
  where: $.definitions.Tone.x-ms-enum
  transform: >
    $["name"] = "DtmfTone";
- from: swagger-document
  where: $.definitions.CallConnectionStateModel.x-ms-enum
  transform: >
    $["name"] = "CallConnectionState";
```