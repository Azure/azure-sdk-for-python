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
param latestAksVersion string = '1.29.8'

@description('The SSH public key to use for the Linux VMs.')
param sshPubKey string = ''

@description('The admin user name for the Linux VMs.')
param adminUserName string = 'azureuser'

@description('Whether live resources should be provisioned. Defaults to false.')
param provisionLiveResources bool = false

// See https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
var blobReader = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1') // Storage Blob Data Reader
var websiteContributor = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'de139f84-1756-47ae-9be6-808fbbe84772') // Website Contributor
var acrPull = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // ACR Pull

// Cluster parameters
var kubernetesVersion = latestAksVersion

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = if (provisionLiveResources) {
  name: baseName
  location: location
}

resource blobRoleWeb 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (provisionLiveResources) {
  scope: storageAccount
  name: guid(resourceGroup().id, blobReader)
  properties: {
    principalId: provisionLiveResources ? web.identity.principalId : ''
    roleDefinitionId: blobReader
    principalType: 'ServicePrincipal'
  }
}

resource blobRoleFunc 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (provisionLiveResources) {
  scope: storageAccount
  name: guid(resourceGroup().id, blobReader, 'azureFunction')
  properties: {
    principalId: provisionLiveResources ? azureFunction.identity.principalId : ''
    roleDefinitionId: blobReader
    principalType: 'ServicePrincipal'
  }
}

resource blobRoleCluster 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (provisionLiveResources) {
  scope: storageAccount
  name: guid(resourceGroup().id, blobReader, 'kubernetes')
  properties: {
    principalId: provisionLiveResources ? kubernetesCluster.identity.principalId : ''
    roleDefinitionId: blobReader
    principalType: 'ServicePrincipal'
  }
}

resource vmRoleCluster 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (provisionLiveResources) {
  scope: storageAccount
  name: guid(resourceGroup().id, blobReader, 'vm')
  properties: {
    principalId: provisionLiveResources ? virtualMachine.identity.principalId : ''
    roleDefinitionId: blobReader
    principalType: 'ServicePrincipal'
  }
}

resource blobRole2 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (provisionLiveResources) {
  scope: storageAccount2
  name: guid(resourceGroup().id, blobReader, userAssignedIdentity.id)
  properties: {
    principalId: provisionLiveResources ? userAssignedIdentity.properties.principalId : ''
    roleDefinitionId: blobReader
    principalType: 'ServicePrincipal'
  }
}

resource webRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (provisionLiveResources) {
  scope: web
  name: guid(resourceGroup().id, websiteContributor, 'web')
  properties: {
    principalId: testApplicationOid
    roleDefinitionId: websiteContributor
    principalType: 'ServicePrincipal'
  }
}

resource webRole2 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (provisionLiveResources) {
  scope: azureFunction
  name: guid(resourceGroup().id, websiteContributor, 'azureFunction')
  properties: {
    principalId: testApplicationOid
    roleDefinitionId: websiteContributor
    principalType: 'ServicePrincipal'
  }
}

resource acrPullContainerInstance 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (provisionLiveResources) {
  scope: acrResource
  name: guid(resourceGroup().id, acrPull, 'containerInstance')
  properties: {
    principalId: provisionLiveResources ? userAssignedIdentity.properties.principalId : ''
    roleDefinitionId: acrPull
    principalType: 'ServicePrincipal'
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2021-08-01' = if (provisionLiveResources) {
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

resource storageAccount2 'Microsoft.Storage/storageAccounts@2021-08-01' = if (provisionLiveResources) {
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

resource farm 'Microsoft.Web/serverfarms@2021-03-01' = if (provisionLiveResources) {
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

resource web 'Microsoft.Web/sites@2022-09-01' = if (provisionLiveResources) {
  name: '${baseName}webapp'
  location: location
  kind: 'app'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${provisionLiveResources ? userAssignedIdentity.id: ''}' : { }
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
          value: provisionLiveResources ? storageAccount.name : 'null'
        }
        {
          name: 'IDENTITY_STORAGE_NAME_2'
          value: provisionLiveResources ? storageAccount2.name : null
        }
        {
          name: 'IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID'
          value: provisionLiveResources ? userAssignedIdentity.properties.clientId : null
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

resource azureFunction 'Microsoft.Web/sites@2022-09-01' = if (provisionLiveResources) {
  name: '${baseName}func'
  location: location
  kind: 'functionapp'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${provisionLiveResources ? userAssignedIdentity.id: ''}' : { }
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
          value: provisionLiveResources ? storageAccount.name : null
        }
        {
          name: 'IDENTITY_STORAGE_NAME_2'
          value: provisionLiveResources ? storageAccount2.name : null
        }
        {
          name: 'IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID'
          value: provisionLiveResources ? userAssignedIdentity.properties.clientId : null
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${provisionLiveResources ? storageAccount.name : ''};EndpointSuffix=${provisionLiveResources ? environment().suffixes.storage : ''};AccountKey=${provisionLiveResources ? storageAccount.listKeys().keys[0].value : ''}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${provisionLiveResources ? storageAccount.name : ''};EndpointSuffix=${provisionLiveResources ? environment().suffixes.storage : ''};AccountKey=${provisionLiveResources ? storageAccount.listKeys().keys[0].value: ''}'
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

resource publishPolicyWeb 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2022-09-01' = if (provisionLiveResources) {
  kind: 'app'
  parent: web
  name: 'scm'
  properties: {
    allow: true
  }
}

resource publishPolicyFunction 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2022-09-01' = if (provisionLiveResources) {
  kind: 'functionapp'
  parent: azureFunction
  name: 'scm'
  properties: {
    allow: true
  }
}

resource acrResource 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = if (provisionLiveResources) {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

resource kubernetesCluster 'Microsoft.ContainerService/managedClusters@2023-06-01' = if (provisionLiveResources) {
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

resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' = if (provisionLiveResources) {
  name: '${baseName}vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: '${baseName}subnet'
        properties: {
          addressPrefix: '10.0.0.0/24'
        }
      }
    ]
  }
}

resource networkInterface 'Microsoft.Network/networkInterfaces@2021-02-01' = if (provisionLiveResources) {
  name: '${baseName}NIC'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'myIPConfig'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          subnet: {
            id: provisionLiveResources ? vnet.properties.subnets[0].id : ''
          }
        }
      }
    ]
  }
}

resource virtualMachine 'Microsoft.Compute/virtualMachines@2020-06-01' = if (provisionLiveResources) {
  name: '${baseName}vm'
  location: location
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${provisionLiveResources ? userAssignedIdentity.id: ''}' : { }
    }
  }
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_DS1_v2'
    }
    osProfile: {
      computerName: '${baseName}vm'
      adminUsername: adminUserName
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/${adminUserName}/.ssh/authorized_keys'
              keyData: sshPubKey
            }
          ]
        }
      }
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
      osDisk: {
          createOption: 'FromImage'
      }
    }
    networkProfile: {
      networkInterfaces: [{
          id: provisionLiveResources ? networkInterface.id : ''
      }]
    }
  }
}


output IDENTITY_WEBAPP_NAME string = provisionLiveResources ? web.name : ''
output IDENTITY_USER_DEFINED_IDENTITY string = provisionLiveResources ? userAssignedIdentity.id : ''
output IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID string = provisionLiveResources ? userAssignedIdentity.properties.clientId : ''
output IDENTITY_USER_DEFINED_IDENTITY_NAME string = provisionLiveResources ? userAssignedIdentity.name : ''
output IDENTITY_STORAGE_NAME_1 string = provisionLiveResources ? storageAccount.name : ''
output IDENTITY_STORAGE_NAME_2 string = provisionLiveResources ? storageAccount2.name : ''
output IDENTITY_STORAGE_ID_1 string = provisionLiveResources ? storageAccount.id : ''
output IDENTITY_STORAGE_ID_2 string = provisionLiveResources ? storageAccount2.id : ''
output IDENTITY_FUNCTION_NAME string = provisionLiveResources ? azureFunction.name : ''
output IDENTITY_AKS_CLUSTER_NAME string = provisionLiveResources ? kubernetesCluster.name : ''
output IDENTITY_AKS_POD_NAME string = provisionLiveResources ? 'python-test-app' : ''
output IDENTITY_ACR_NAME string = provisionLiveResources ? acrResource.name : ''
output IDENTITY_CONTAINER_INSTANCE_NAME string = provisionLiveResources ? 'python-container-app' : ''
output IDENTITY_ACR_LOGIN_SERVER string = provisionLiveResources ? acrResource.properties.loginServer : ''
output IDENTITY_VM_NAME string = provisionLiveResources ? virtualMachine.name : ''
output IDENTITY_LIVE_RESOURCES_PROVISIONED string = provisionLiveResources ? 'true' : ''
