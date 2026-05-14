param baseName string = resourceGroup().name
param testApplicationOid string
param location string = resourceGroup().location
param supportsSafeSecretStandard bool = false

var webpubsubName = 'e2e-${baseName}'
var socketioName = 'e2e-socketio-${baseName}'
// Web PubSub Service Owner
var ownerRoleId = '12cf5a90-567b-43ae-8102-96cf46c7d9b4'

resource webPubSubSocketIO 'Microsoft.SignalRService/webPubSub@2024-10-01-preview' = {
  name: socketioName
  location: location
  kind: 'SocketIO'
  sku: {
    name: 'Standard_S1'
    tier: 'Standard'
    capacity: 1
  }
  properties: {
    tls: {
      clientCertEnabled: false
    }
    disableLocalAuth: supportsSafeSecretStandard
  }
}

resource webPubSub 'Microsoft.SignalRService/webPubSub@2024-10-01-preview' = {
  name: webpubsubName
  location: location
  kind: 'WebPubSub'
  sku: {
    name: 'Standard_S1'
    tier: 'Standard'
    capacity: 1
  }
  properties: {
    tls: {
      clientCertEnabled: false
    }
    disableLocalAuth: supportsSafeSecretStandard
  }
}

resource ownerRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('ownerRoleId', webPubSub.id, testApplicationOid)
  scope: webPubSub
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', ownerRoleId)
    principalId: testApplicationOid
  }
}

resource socketIOOwnerRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('ownerRoleId', webPubSubSocketIO.id, testApplicationOid)
  scope: webPubSubSocketIO
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', ownerRoleId)
    principalId: testApplicationOid
  }
}

output AZURE_SUBSCRIPTION_ID string = subscription().subscriptionId
output AZURE_RESOURCE_GROUP string = resourceGroup().name
output WEBPUBSUB_ENDPOINT string = 'https://${webPubSub.properties.hostName}'
output WEBPUBSUB_REVERSE_PROXY_ENDPOINT string = 'https://${webPubSub.properties.hostName}'
output WEBPUBSUBCLIENT_ENDPOINT string = 'https://${webPubSub.properties.hostName}'
output WEBPUBSUB_SOCKETIO_ENDPOINT string = 'https://${webPubSubSocketIO.properties.hostName}'
