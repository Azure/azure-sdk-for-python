@minLength(6)
@maxLength(50)
@description('The base resource name.')
param baseName string = resourceGroup().name

@description('The location of the resources. By default, this is the same as the resource group.')
param location string = resourceGroup().location

@description('The client OID to grant access to test resources.')
param testApplicationOid string

@description('A new GUID used to identify the role assignment')
param roleNameGuid string = newGuid()

resource digitaltwin 'Microsoft.DigitalTwins/digitalTwinsInstances@2022-05-31' = {
  name: baseName
  location: location
  identity: {
    type: 'None'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

resource digitaltwinRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: roleNameGuid
  properties: {
      roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'bcd981a7-7f74-457b-83e1-cceb9e632ffe')
      principalId: testApplicationOid
  }
  scope: digitaltwin
}

output AZURE_DIGITALTWINS_URL string = 'https://${digitaltwin.properties.hostName}'
