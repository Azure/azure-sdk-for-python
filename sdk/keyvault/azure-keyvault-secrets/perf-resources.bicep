@description('The base resource name.')
param baseName string = resourceGroup().name

@description('The tenant ID to which the application and resources belong.')
param tenantId string = subscription().tenantId

@description('The client OID to grant access to test resources.')
param testApplicationOid string

@description('The location of the resource. By default, this is the same as the resource group.')
param location string = resourceGroup().location

@description('Key Vault SKU to deploy. The default is \'Premium\'')
@allowed([
  'standard'
  'premium'
])
param keyVaultSku string = 'premium'
param testApplicationId string

var kvName = baseName
var networkAcls = {
  bypass: 'AzureServices'
  virtualNetworkRules: []
  ipRules: []
  defaultAction: 'Allow'
}
var secretsOfficerRoleAssignmentId = 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7'
var kvAdminRoleAssignmentId = '00482a5a-887f-4fb3-b363-3b7fe8e74483'

resource kv 'Microsoft.KeyVault/vaults@2021-04-01-preview' = {
  name: kvName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: keyVaultSku
    }
    tenantId: tenantId
    enableSoftDelete: true
    enableRbacAuthorization: true
    softDeleteRetentionInDays: 7
    networkAcls: networkAcls
  }
}

resource kvAdminRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(kvAdminRoleAssignmentId,testApplicationOid,kv.id)
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', kvAdminRoleAssignmentId)
    principalId: testApplicationOid
    principalType: 'ServicePrincipal'
  }
}

resource kvSecretsRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(secretsOfficerRoleAssignmentId,testApplicationOid,kv.id)
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', secretsOfficerRoleAssignmentId)
    principalId: testApplicationOid
    principalType: 'ServicePrincipal'
  }
}

output AZURE_KEYVAULT_URL string = kv.properties.vaultUri
