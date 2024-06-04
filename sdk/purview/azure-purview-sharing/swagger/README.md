# Azure Purview for Python

### Settings

```yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/40a953243ea428918de6e63758e853b7a24aa59a/specification/purview/data-plane/Azure.Analytics.Purview.Share/preview/2023-05-30-preview/share.json
output-folder: ../
namespace: azure.purview.sharing
package-name: azure-purview-sharing
license-header: MICROSOFT_MIT_NO_VERSION
title: Purview Sharing Client
package-version: 1.0.0b1
package-mode: dataplane
package-pprint-name: Azure Purview Sharing
security: AADToken
security-scopes: https://purview.azure.net/.default
modelerfour:
  lenient-model-deduplication: true
only-path-params-positional: true
directive: 
  - rename-operation: [ from:"SentShares_Get", to:"SentShares_GetSentShare", from:"SentShares_Create", to:"SentShares_CreateOrReplaceSentShare", from:"SentShares_Delete", to:"SentShares_DeleteSentShare", from:"SentShares_List", to:"SentShares_GetAllSentShares", from:"SentShares_GetInvitation", to:"SentShares_GetSentShareInvitation", from:"SentShares_CreateInvitation", to:"SentShares_CreateSentShareInvitation", from:"SentShares_DeleteInvitation", to:"SentShares_DeleteSentShareInvitation", from:"SentShares_ListInvitations", to:"SentShares_GetAllSentShareInvitations", from:"SentShares_NotifyUserInvitation", to:"SentShares_NotifyUserSentShareInvitation", from:"ReceivedShares_Get", to:"ReceivedShares_GetReceivedShare", from:"ReceivedShares_Create", to:"ReceivedShares_CreateOrReplaceReceivedShare", from:"ReceivedShares_Delete", to:"ReceivedShares_DeleteReceivedShare", from:"ReceivedShares_ListAttached", to:"ReceivedShares_GetAllAttachedReceivedShares", from:"ReceivedShares_ListDetached", to:"ReceivedShares_GetAllDetachedReceivedShares", from:"ShareResources_List", to:"ShareResources_GetAllShareResources", ]
```

```yaml
directive:
  from: swagger-document
  where: '$.parameters["orderby"]'
  transform: >
    $["x-ms-client-name"] = "order_by";
```
