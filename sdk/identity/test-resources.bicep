@minLength(6)
@maxLength(23)
@description('The base resource name.')
param baseName string = resourceGroup().name

@description('The location of the resource. By default, this is the same as the resource group.')
param location string = resourceGroup().location

@description('The client OID to grant access to test resources.')
param testApplicationOid string

@minLength(5)
@maxLength(50)
@description('Provide a globally unique name of the Azure Container Registry')
param acrName string = 'acr${uniqueString(resourceGroup().id)}'

@description('The latest AKS version available in the region.')
param latestAksVersion string

@description('The SSH public key to use for the Linux VMs.')
param sshPubKey string

@description('The admin user name for the Linux VMs.')
param adminUserName string = 'azureuser'

// See https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
var blobContributor = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
var websiteContributor = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'de139f84-1756-47ae-9be6-808fbbe84772') // Website Contributor

// Cluster parameters
var kubernetesVersion = latestAksVersion

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
  name: baseName
  location: location
}

resource blobRoleWeb 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(resourceGroup().id, blobContributor)
  properties: {
    principalId: web.identity.principalId
    roleDefinitionId: blobContributor
    principalType: 'ServicePrincipal'
  }
}

resource blobRoleFunc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(resourceGroup().id, blobContributor, 'azureFunction')
  properties: {
    principalId: azureFunction.identity.principalId
    roleDefinitionId: blobContributor
    principalType: 'ServicePrincipal'
  }
}

resource blobRoleCluster 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(resourceGroup().id, blobContributor, 'kubernetes')
  properties: {
    principalId: kubernetesCluster.identity.principalId
    roleDefinitionId: blobContributor
    principalType: 'ServicePrincipal'
  }
}

resource blobRole2 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount2
  name: guid(resourceGroup().id, blobContributor, userAssignedIdentity.id)
  properties: {
    principalId: userAssignedIdentity.properties.principalId
    roleDefinitionId: blobContributor
    principalType: 'ServicePrincipal'
  }
}

resource webRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: web
  name: guid(resourceGroup().id, websiteContributor, 'web')
  properties: {
    principalId: testApplicationOid
    roleDefinitionId: websiteContributor
    principalType: 'ServicePrincipal'
  }
}

resource webRole2 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: azureFunction
  name: guid(resourceGroup().id, websiteContributor, 'azureFunction')
  properties: {
    principalId: testApplicationOid
    roleDefinitionId: websiteContributor
    principalType: 'ServicePrincipal'
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-08-01' = {
  name: baseName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

resource storageAccount2 'Microsoft.Storage/storageAccounts@2021-08-01' = {
  name: '${baseName}2'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

resource farm 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: '${baseName}_farm'
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
    size: 'B1'
    family: 'B'
    capacity: 1
  }
  properties: {
    reserved: true
  }
  kind: 'app,linux'
}

resource web 'Microsoft.Web/sites@2022-09-01' = {
  name: '${baseName}webapp'
  location: location
  kind: 'app'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}' : { }
    }
  }
  properties: {
    enabled: true
    serverFarmId: farm.id
    httpsOnly: true
    keyVaultReferenceIdentity: 'SystemAssigned'
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      http20Enabled: true
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'AZURE_REGIONAL_AUTHORITY_NAME'
          value: 'eastus'
        }
        {
          name: 'IDENTITY_STORAGE_NAME_1'
          value: storageAccount.name
        }
        {
          name: 'IDENTITY_STORAGE_NAME_2'
          value: storageAccount2.name
        }
        {
          name: 'IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID'
          value: userAssignedIdentity.properties.clientId
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

resource azureFunction 'Microsoft.Web/sites@2022-09-01' = {
  name: '${baseName}func'
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}' : { }
    }
  }
  properties: {
    enabled: true
    serverFarmId: farm.id
    httpsOnly: true
    keyVaultReferenceIdentity: 'SystemAssigned'
    siteConfig: {
      alwaysOn: true
      http20Enabled: true
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'IDENTITY_STORAGE_NAME_1'
          value: storageAccount.name
        }
        {
          name: 'IDENTITY_STORAGE_NAME_2'
          value: storageAccount2.name
        }
        {
          name: 'IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID'
          value: userAssignedIdentity.properties.clientId
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower('${baseName}-func')
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
      ]
    }
  }
}

resource publishPolicyWeb 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2022-09-01' = {
  kind: 'app'
  parent: web
  name: 'scm'
  properties: {
    allow: true
  }
}

resource publishPolicyFunction 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2022-09-01' = {
  kind: 'functionapp'
  parent: azureFunction
  name: 'scm'
  properties: {
    allow: true
  }
}

resource acrResource 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

resource kubernetesCluster 'Microsoft.ContainerService/managedClusters@2023-06-01' = {
  name: baseName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    kubernetesVersion: kubernetesVersion
    enableRBAC: true
    dnsPrefix: 'identitytest'
    agentPoolProfiles: [
      {
        name: 'agentpool'
        count: 1
        vmSize: 'Standard_D2s_v3'
        osDiskSizeGB: 128
        osDiskType: 'Managed'
        kubeletDiskType: 'OS'
        type: 'VirtualMachineScaleSets'
        enableAutoScaling: false
        orchestratorVersion: kubernetesVersion
        mode: 'System'
        osType: 'Linux'
        osSKU: 'Ubuntu'
      }
    ]
    linuxProfile: {
      adminUsername: adminUserName
      ssh: {
        publicKeys: [
          {
            keyData: sshPubKey
          }
        ]
      }
    }
    oidcIssuerProfile: {
      enabled: true
    }
    securityProfile: {
      workloadIdentity: {
        enabled: true
      }
    }
  }
}

output IDENTITY_WEBAPP_NAME string = web.name
output IDENTITY_USER_DEFINED_IDENTITY string = userAssignedIdentity.id
output IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID string = userAssignedIdentity.properties.clientId
output IDENTITY_USER_DEFINED_IDENTITY_NAME string = userAssignedIdentity.name
output IDENTITY_STORAGE_NAME_1 string = storageAccount.name
output IDENTITY_STORAGE_NAME_2 string = storageAccount2.name
output IDENTITY_FUNCTION_NAME string = azureFunction.name
output IDENTITY_AKS_CLUSTER_NAME string = kubernetesCluster.name
output IDENTITY_AKS_POD_NAME string = 'python-test-app'
output IDENTITY_ACR_NAME string = acrResource.name
output IDENTITY_ACR_LOGIN_SERVER string = acrResource.properties.loginServer
