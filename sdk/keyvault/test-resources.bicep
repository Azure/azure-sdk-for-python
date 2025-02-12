param hsmLocation string = 'brazilsouth'

param baseName string = resourceGroup().name
param tenantId string = '72f988bf-86f1-41af-91ab-2d7cd011db47'
param testApplicationOid string
param provisionerApplicationOid string
param location string = resourceGroup().location
param enableHsm bool = false
param keyVaultSku string = 'premium'
param attestationImage string = 'keyvault-mock-attestation:latest'

var attestationFarm = '${baseName}farm'
var attestationSite = '${baseName}site'
var attestationImageUri = 'DOCKER|azsdkengsys.azurecr.io/${attestationImage}'
var kvName = baseName
var hsmName = '${baseName}hsm'
var blobContainerName = 'hsmbackups'
var primaryAccountName = '${replace(baseName, '-', '')}prim'
var kvAdminDefinitionId = '00482a5a-887f-4fb3-b363-3b7fe8e74483'
var kvAdminAssignmentName = guid(resourceGroup().id, kvAdminDefinitionId, testApplicationOid)
var encryption = {
  services: {
    blob: {
      enabled: true
    }
  }
  keySource: 'Microsoft.Storage'
}
var networkAcls = {
  bypass: 'AzureServices'
  virtualNetworkRules: []
  ipRules: []
  defaultAction: 'Allow'
}
var managedIdentityName = '${baseName}-managedIdentity'
var managedIdentityId = managedIdentity.id

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = if (enableHsm) {
  name: managedIdentityName
  location: location
}

resource keyVault 'Microsoft.KeyVault/vaults@2024-04-01-preview' = {
  name: kvName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: keyVaultSku
    }
    tenantId: tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    enableRbacAuthorization: true
    softDeleteRetentionInDays: 7
  }
}

resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: kvAdminAssignmentName
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', kvAdminDefinitionId)
    principalId: testApplicationOid
  }
}

resource managedHsm 'Microsoft.KeyVault/managedHSMs@2024-04-01-preview' = if (enableHsm) {
  name: hsmName
  location: hsmLocation
  sku: {
    family: 'B'
    name: 'Standard_B1'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    networkAcls: networkAcls
    tenantId: tenantId
    initialAdminObjectIds: union([testApplicationOid], [provisionerApplicationOid])
    enablePurgeProtection: false
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: primaryAccountName
  location: location
  sku: {
    name: 'Standard_RAGRS'
  }
  kind: 'StorageV2'
  properties: {
    networkAcls: networkAcls
    supportsHttpsTrafficOnly: true
    encryption: encryption
    accessTier: 'Hot'
    allowSharedKeyAccess: false
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      enabled: false
    }
  }
  parent: storageAccount
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: blobContainerName
  properties: {
    publicAccess: 'None'
  }
  parent: blobService
}

resource managedIdentityRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enableHsm) {
  name: guid(resourceGroup().id, 'StorageBlobContributor', managedIdentityId)
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )
    principalId: managedIdentity.properties.principalId
    scope: resourceGroup().id
    principalType: 'ServicePrincipal'
  }
}

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: attestationFarm
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
  }
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: attestationSite
  location: location
  properties: {
    httpsOnly: true
    serverFarmId: appServicePlan.id
    siteConfig: {
      alwaysOn: true
      linuxFxVersion: attestationImageUri
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
      ]
    }
  }
}

output AZURE_KEYVAULT_URL string = keyVault.properties.vaultUri
output AZURE_MANAGEDHSM_URL string = (enableHsm) ? managedHsm.properties.hsmUri : ''
output KEYVAULT_SKU string = keyVault.properties.sku.name
output CLIENT_OBJECTID string = testApplicationOid
output BLOB_STORAGE_URL string = storageAccount.properties.primaryEndpoints.blob
output BLOB_CONTAINER_NAME string = blobContainerName
output AZURE_KEYVAULT_ATTESTATION_URL string = 'https://${webApp.properties.defaultHostName}/'
output MANAGED_IDENTITY_CLIENT_ID string = managedIdentityId
