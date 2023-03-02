# Azure Purview for Python

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
package-name: "@azure-rest/purview-sharing"
title: Purview Sharing
description: Purview Sharing Client
generate-metadata: false
license-header: MICROSOFT_MIT_NO_VERSION
input-file: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/purview/data-plane/Azure.Analytics.Purview.Share/preview/2023-02-15-preview/share.json
output-folder: ../azure/purview/sharing
namespace: azure.purview.sharing
clear-output-folder: true
no-namespace-folders: true
python: true
package-version: 1.0.0-beta.1
rest-level-client: true
add-credential: true
credential-scopes: "https://purview.azure.net/.default"
generate-test: false
generate-samples: true
modelerfour:
  lenient-model-deduplication: true
only-path-params-positional: true
version-tolerant: true
directive: rename-operation:[ from:"SentShares_Get", to:"SentShares_GetSentShare", from:"SentShares_Create", to:"SentShares_CreateOrReplaceSentShare", from:"SentShares_Delete", to:"SentShares_DeleteSentShare", from:"SentShares_List", to:"SentShares_GetAllSentShares", from:"SentShares_GetInvitation", to:"SentShares_GetSentShareInvitation", from:"SentShares_CreateInvitation", to:"SentShares_CreateSentShareInvitation", from:"SentShares_DeleteInvitation", to:"SentShares_DeleteSentShareInvitation", from:"SentShares_ListInvitations", to:"SentShares_GetAllSentShareInvitations", from:"SentShares_NotifyUserInvitation", to:"SentShares_NotifyUserSentShareInvitation", from:"ReceivedShares_Get", to:"ReceivedShares_GetReceivedShare", from:"ReceivedShares_Create", to:"ReceivedShares_CreateOrReplaceReceivedShare", from:"ReceivedShares_Delete", to:"ReceivedShares_DeleteReceivedShare", from:"ReceivedShares_ListAttached", to:"ReceivedShares_GetAllAttachedReceivedShares", from:"ReceivedShares_ListDetached", to:"ReceivedShares_GetAllDetachedReceivedShares", ]
```