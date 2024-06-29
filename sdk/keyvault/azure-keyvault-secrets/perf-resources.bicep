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

var kvName = baseName
var networkAcls = {
  bypass: 'AzureServices'
  virtualNetworkRules: []
  ipRules: []
  defaultAction: 'Allow'
}

resource kv 'Microsoft.KeyVault/vaults@2021-04-01-preview' = {
  name: kvName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: keyVaultSku
    }
    tenantId: tenantId
    accessPolicies: [
      {
        tenantId: tenantId
        objectId: testApplicationOid
        permissions: {
          secrets: [
            'Get'
            'List'
            'Set'
            'Delete'
            'Recover'
            'Backup'
            'Restore'
            'Purge'
          ]
        }
      }
    ]
    enableSoftDelete: true
    enableRbacAuthorization: false
    softDeleteRetentionInDays: 7
    networkAcls: networkAcls
  }
}

output AZURE_KEYVAULT_URL string = kv.properties.vaultUri
