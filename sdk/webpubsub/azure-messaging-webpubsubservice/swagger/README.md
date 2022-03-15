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
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/73a0fa453a93bdbe8885f87b9e4e9fef4f0452d0/specification/webpubsub/data-plane/WebPubSub/stable/2021-10-01/webpubsub.json
output-folder: ../azure/messaging/webpubsubservice
namespace: azure.messaging.webpubsubservice
package-name: azure-messaging-webpubsubservice
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: WebPubSubServiceClient
version-tolerant: true
head-as-boolean: true
package-version: 1.0.1
add-credential: true
credential-scopes: https://webpubsub.azure.com/.default
black: true
```


Here's the directive to delete the health api operation that we don't need / want
```yaml

directive:
  - from: swagger-document
    where: $["paths"]["/api/health"]
    transform: >
        delete $["head"];
```

Here's the directive to move the operations from the webpubsub operation group directly onto the client

```yaml

directive:
  - from: swagger-document
    where: $["paths"][*]
    transform: >
        for (var op of Object.values($)) {
          if (op["operationId"].includes("WebPubSub_")) {
            op["operationId"] = op["operationId"].replace("WebPubSub_", "");
          }
        }
```

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/api/hubs/{hub}/:generateToken"].post.parameters
    transform: >
        $[2]["x-ms-client-name"] = "roles"
```

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/api/hubs/{hub}/permissions/{permission}/connections/{connectionId}"].head
    transform: $["operationId"] = "HasPermission"
```

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/api/hubs/{hub}/:generateToken"].post
    transform: $["operationId"] = "GetClientAccessToken"
```

### Add hub to client on generate token

``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/:generateToken"].post.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### SendToAll

``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/:send"].post.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### ConnectionExistsImpl
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/connections/{connectionId}"].head.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### CloseConnection
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/connections/{connectionId}"].delete.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### SendToConnection
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/connections/{connectionId}/:send"].post.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### GroupExistsImpl
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/groups/{group}"].head.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### SendToGroup
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/groups/{group}/:send"].post.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### AddConnectionToGroup
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/groups/{group}/connections/{connectionId}"].put.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### RemoveConnectionFromGroup
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/groups/{group}/connections/{connectionId}"].delete.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### UserExistsImpl
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/users/{userId}"].head.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### SendToUser
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/users/{userId}/:send"].post.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### AddUserToGroup
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/users/{userId}/groups/{group}"].put.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### RemoveUserFromGroup
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/users/{userId}/groups/{group}"].delete.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### RemoveUserFromAllGroups
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/users/{userId}/groups"].delete.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### GrantPermission
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/permissions/{permission}/connections/{connectionId}"].put.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### RevokePermission
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/permissions/{permission}/connections/{connectionId}"].delete.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### CheckPermission
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/permissions/{permission}/connections/{connectionId}"].head.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### CloseAllConnections
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/:closeConnections"].post.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### CloseGroupConnections
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/groups/{group}/:closeConnections"].post.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```

### CloseUserConnections
``` yaml
directive:
- from: swagger-document
  where: $.paths["/api/hubs/{hub}/users/{userId}/:closeConnections"].post.parameters["0"]
  transform: $["x-ms-parameter-location"] = "client"
```
