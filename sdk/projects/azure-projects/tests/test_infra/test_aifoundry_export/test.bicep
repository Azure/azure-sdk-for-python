param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  location: location
  tags: azdTags
  name: defaultName
}



resource aiservices_account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  kind: 'AIServices'
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
    customSubDomainName: '${defaultName}-aiservices'
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
  }
  name: '${defaultName}-aiservices'
  location: location
  tags: azdTags
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_AI_AISERVICES_ID string = aiservices_account.id
output AZURE_AI_AISERVICES_NAME string = aiservices_account.name
output AZURE_AI_AISERVICES_RESOURCE_GROUP string = resourceGroup().name
output AZURE_AI_AISERVICES_ENDPOINT string = aiservices_account.properties.endpoint


resource searchservice 'Microsoft.Search/searchServices@2024-06-01-Preview' = {
  properties: {
    publicNetworkAccess: 'Disabled'
  }
  name: defaultName
  sku: {
    name: 'basic'
  }
  location: location
  tags: azdTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_SEARCH_ID string = searchservice.id
output AZURE_SEARCH_NAME string = searchservice.name
output AZURE_SEARCH_RESOURCE_GROUP string = resourceGroup().name
output AZURE_SEARCH_ENDPOINT string = 'https://${searchservice.name}.search.windows.net/'


resource storageaccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  properties: {
    accessTier: 'Hot'
    allowCrossTenantReplication: false
    allowSharedKeyAccess: false
  }
  name: defaultName
  location: location
  tags: azdTags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_STORAGE_ID string = storageaccount.id
output AZURE_STORAGE_NAME string = storageaccount.name
output AZURE_STORAGE_RESOURCE_GROUP string = resourceGroup().name


resource blobservice 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: storageaccount
  properties: {}
  name: 'default'
}

output AZURE_BLOBS_ENDPOINT string = storageaccount.properties.primaryEndpoints.blob


resource vault 'Microsoft.KeyVault/vaults@2024-12-01-preview' = {
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    publicNetworkAccess: 'Enabled'
    tenantId: tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
  name: defaultName
  location: location
  tags: azdTags
}

output AZURE_KEYVAULT_ID string = vault.id
output AZURE_KEYVAULT_NAME string = vault.name
output AZURE_KEYVAULT_RESOURCE_GROUP string = resourceGroup().name
output AZURE_KEYVAULT_ENDPOINT string = vault.properties.vaultUri


resource hub_workspace 'Microsoft.MachineLearningServices/workspaces@2024-04-01-preview' = {
  kind: 'Hub'
  properties: {
    publicNetworkAccess: 'Enabled'
    enableDataIsolation: true
    v1LegacyMode: false
    hbiWorkspace: false
    managedNetwork: {
      isolationMode: 'Disabled'
    }
    primaryUserAssignedIdentity: userassignedidentity.id
    workspaceHubConfig: {
      defaultWorkspaceResourceGroup: resourceGroup().id
    }
    storageAccount: storageaccount.id
    keyVault: vault.id
  }
  name: '${defaultName}-hub'
  location: location
  tags: azdTags
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_AIFOUNDRY_HUB_ID string = hub_workspace.id
output AZURE_AIFOUNDRY_HUB_NAME string = hub_workspace.name
output AZURE_AIFOUNDRY_HUB_RESOURCE_GROUP string = resourceGroup().name


resource connection_xedrqlelyhtxcrfwrxif 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
  parent: hub_workspace
  properties: {
    authType: 'AAD'
    isSharedToAll: true
    sharedUserList: []
    category: 'CognitiveSearch'
    target: 'https://${searchservice.name}.search.windows.net/'
    metadata: {
      ApiType: 'Azure'
      ResourceId: searchservice.id
      location: location
    }
  }
  name: guid(defaultName, 'connection', 'Hub', 'AISearch')
}



resource connection_hfpudimwwntoylmqeene 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
  parent: hub_workspace
  properties: {
    authType: 'AAD'
    isSharedToAll: true
    sharedUserList: []
    category: 'AIServices'
    target: aiservices_account.properties.endpoint
    metadata: {
      ApiType: 'Azure'
      ResourceId: aiservices_account.id
      location: location
    }
  }
  name: guid(defaultName, 'connection', 'Hub', 'AIServices')
}



resource project_workspace 'Microsoft.MachineLearningServices/workspaces@2024-04-01-preview' = {
  kind: 'Project'
  properties: {
    publicNetworkAccess: 'Enabled'
    enableDataIsolation: true
    v1LegacyMode: false
    hbiWorkspace: false
    primaryUserAssignedIdentity: userassignedidentity.id
    workspaceHubConfig: {
      defaultWorkspaceResourceGroup: resourceGroup().id
    }
    hubResourceId: hub_workspace.id
  }
  name: '${defaultName}-project'
  location: location
  tags: azdTags
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_AIFOUNDRY_PROJECT_ID string = project_workspace.id
output AZURE_AIFOUNDRY_PROJECT_NAME string = project_workspace.name
output AZURE_AIFOUNDRY_PROJECT_RESOURCE_GROUP string = resourceGroup().name
output AZURE_AIFOUNDRY_PROJECT_ENDPOINT string = project_workspace.properties.discoveryUrl


resource connection_fevfjhqjccofnnzyaakt 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
  parent: project_workspace
  properties: {
    authType: 'AAD'
    isSharedToAll: true
    sharedUserList: []
    category: 'CognitiveSearch'
    target: 'https://${searchservice.name}.search.windows.net/'
    metadata: {
      ApiType: 'Azure'
      ResourceId: searchservice.id
      location: location
    }
  }
  name: guid(defaultName, 'connection', 'Project', 'AISearch')
}



resource connection_sijgpdkolsbeganjpujf 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
  parent: project_workspace
  properties: {
    authType: 'AAD'
    isSharedToAll: true
    sharedUserList: []
    category: 'AIServices'
    target: aiservices_account.properties.endpoint
    metadata: {
      ApiType: 'Azure'
      ResourceId: aiservices_account.id
      location: location
    }
  }
  name: guid(defaultName, 'connection', 'Project', 'AIServices')
}



resource roleassignment_prmcdnytekaxfpxlctiu 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a001fd3d-188f-4b5d-821b-7da978bf7442'
    )

  }
  scope: aiservices_account
}



resource roleassignment_eueecqmosdtphyvvcakz 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68'
    )

  }
  scope: aiservices_account
}



resource roleassignment_iixyucpvhqitrkqrnbqa 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI User')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    )

  }
  scope: aiservices_account
}



resource roleassignment_olhkahcaximxljdwfqux 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services User')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a97b65f3-24c7-4388-baec-2e87135dc908'
    )

  }
  scope: aiservices_account
}



resource roleassignment_guvkdgrgirgwzahwnvou 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a001fd3d-188f-4b5d-821b-7da978bf7442'
    )

  }
  scope: aiservices_account
}



resource roleassignment_lkopfjwianflbxodoeiq 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68'
    )

  }
  scope: aiservices_account
}



resource roleassignment_ddsjnquihdmohlbeapox 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI User')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    )

  }
  scope: aiservices_account
}



resource roleassignment_wbpjzrvrnkarixpwhfwh 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services User')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a97b65f3-24c7-4388-baec-2e87135dc908'
    )

  }
  scope: aiservices_account
}



resource roleassignment_npmrnriktxggevypexnt 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'ServicePrincipal', 'Search Index Data Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
    )

  }
  scope: searchservice
}



resource roleassignment_tcntafhtedyooituoovj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'ServicePrincipal', 'Search Index Data Reader')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '1407120a-92aa-4202-b7e9-c0e197c71c8f'
    )

  }
  scope: searchservice
}



resource roleassignment_zcwvdaahcvxqfctejcey 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'ServicePrincipal', 'Search Service Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
    )

  }
  scope: searchservice
}



resource roleassignment_qmbddeizydnvppopafhn 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'User', 'Search Index Data Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
    )

  }
  scope: searchservice
}



resource roleassignment_lwgbaxmwgckeacgtyitj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'User', 'Search Index Data Reader')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '1407120a-92aa-4202-b7e9-c0e197c71c8f'
    )

  }
  scope: searchservice
}



resource roleassignment_hanzilafpyksoxhwmdrt 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'User', 'Search Service Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
    )

  }
  scope: searchservice
}



resource roleassignment_bopldzzxbodmidnqjpaj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', 'default', 'ServicePrincipal', 'Storage Blob Data Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )

  }
  scope: blobservice
}



resource roleassignment_kutzxiqaacvpglqusjyi 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', 'default', 'User', 'Storage Blob Data Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )

  }
  scope: blobservice
}



resource roleassignment_qgdjhyhljucznkoutsgj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', defaultName, 'ServicePrincipal', 'Key Vault Administrator')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )

  }
  scope: vault
}



resource roleassignment_xotjgqfzvwectdhbwwhf 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', defaultName, 'User', 'Key Vault Administrator')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )

  }
  scope: vault
}



resource roleassignment_pvnezisjxmzvzycxpdgz 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftMachineLearningServicesworkspaces', '${defaultName}-project', 'ServicePrincipal', 'Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'b24988ac-6180-42a0-ab88-20f7382dd24c'
    )

  }
  scope: project_workspace
}



resource roleassignment_jadfqovrjrbvlmlpppfa 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftMachineLearningServicesworkspaces', '${defaultName}-project', 'User', 'Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'b24988ac-6180-42a0-ab88-20f7382dd24c'
    )

  }
  scope: project_workspace
}



