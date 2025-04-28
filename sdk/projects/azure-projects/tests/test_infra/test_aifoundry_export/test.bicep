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



resource configurationstore 'Microsoft.AppConfiguration/configurationStores@2024-05-01' = {
  name: defaultName
  sku: {
    name: 'Standard'
  }
  properties: {
    disableLocalAuth: true
    createMode: 'Default'
    dataPlaneProxy: {
      authenticationMode: 'Pass-through'
      privateLinkDelegation: 'Disabled'
    }
    publicNetworkAccess: 'Enabled'
  }
  location: location
  tags: azdTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_APPCONFIG_ID string = configurationstore.id
output AZURE_APPCONFIG_NAME string = configurationstore.name
output AZURE_APPCONFIG_RESOURCE_GROUP string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT string = configurationstore.properties.endpoint


resource aiservices_account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  kind: 'AIServices'
  name: '${defaultName}-aiservices'
  location: location
  tags: azdTags
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
    customSubDomainName: '${defaultName}-aiservices'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_AI_AISERVICES_ID_AI string = aiservices_account.id
output AZURE_AI_AISERVICES_NAME_AI string = aiservices_account.name
output AZURE_AI_AISERVICES_RESOURCE_GROUP_AI string = resourceGroup().name
output AZURE_AI_AISERVICES_ENDPOINT_AI string = aiservices_account.properties.endpoint


resource searchservice 'Microsoft.Search/searchServices@2024-06-01-Preview' = {
  name: defaultName
  sku: {
    name: 'basic'
  }
  properties: {
    publicNetworkAccess: 'Disabled'
  }
  location: location
  tags: azdTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_SEARCH_ID_SEARCH string = searchservice.id
output AZURE_SEARCH_NAME_SEARCH string = searchservice.name
output AZURE_SEARCH_RESOURCE_GROUP_SEARCH string = resourceGroup().name
output AZURE_SEARCH_ENDPOINT_SEARCH string = 'https://${searchservice.name}.search.windows.net/'


resource storageaccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: defaultName
  location: location
  tags: azdTags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  properties: {
    accessTier: 'Hot'
    allowCrossTenantReplication: false
    allowSharedKeyAccess: false
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_STORAGE_ID_STORAGE string = storageaccount.id
output AZURE_STORAGE_NAME_STORAGE string = storageaccount.name
output AZURE_STORAGE_RESOURCE_GROUP_STORAGE string = resourceGroup().name


resource blobservice 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: storageaccount
  name: 'default'
}

output AZURE_BLOBS_ENDPOINT_STORAGE string = storageaccount.properties.primaryEndpoints.blob


resource vault 'Microsoft.KeyVault/vaults@2024-12-01-preview' = {
  name: defaultName
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
  location: location
  tags: azdTags
}

output AZURE_KEYVAULT_ID_VAULT string = vault.id
output AZURE_KEYVAULT_NAME_VAULT string = vault.name
output AZURE_KEYVAULT_RESOURCE_GROUP_VAULT string = resourceGroup().name
output AZURE_KEYVAULT_ENDPOINT_VAULT string = vault.properties.vaultUri


resource hub_workspace 'Microsoft.MachineLearningServices/workspaces@2024-04-01-preview' = {
  kind: 'Hub'
  properties: {
    primaryUserAssignedIdentity: userassignedidentity.id
    publicNetworkAccess: 'Enabled'
    enableDataIsolation: true
    v1LegacyMode: false
    hbiWorkspace: false
    managedNetwork: {
      isolationMode: 'Disabled'
    }
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
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_AIFOUNDRY_HUB_ID_HUB string = hub_workspace.id
output AZURE_AIFOUNDRY_HUB_NAME_HUB string = hub_workspace.name
output AZURE_AIFOUNDRY_HUB_RESOURCE_GROUP_HUB string = resourceGroup().name


resource connection_buifsaivbkhdryzkibjl 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
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



resource connection_hmdjuiutdbnirxnlxqbn 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
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
    primaryUserAssignedIdentity: userassignedidentity.id
    publicNetworkAccess: 'Enabled'
    enableDataIsolation: true
    v1LegacyMode: false
    hbiWorkspace: false
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
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_AIFOUNDRY_PROJECT_ID_PROJECT string = project_workspace.id
output AZURE_AIFOUNDRY_PROJECT_NAME_PROJECT string = project_workspace.name
output AZURE_AIFOUNDRY_PROJECT_RESOURCE_GROUP_PROJECT string = resourceGroup().name
output AZURE_AIFOUNDRY_PROJECT_ENDPOINT_PROJECT string = project_workspace.properties.discoveryUrl


resource connection_qazdrbswuvwkfewfrwcp 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
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



resource connection_vxwdzretqhgneqwxyhbo 'Microsoft.MachineLearningServices/workspaces/connections@2025-01-01-preview' = {
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



resource keyvalue_azureappconfigid 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_ID'
  properties: {
    value: configurationstore.id
  }
}



resource keyvalue_azureappconfigname 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_NAME'
  properties: {
    value: configurationstore.name
  }
}



resource keyvalue_azureappconfigresourcegroup 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_RESOURCE_GROUP'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureappconfigendpoint 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_ENDPOINT'
  properties: {
    value: configurationstore.properties.endpoint
  }
}



resource keyvalue_azureaiaiservicesidai 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_ID_AI'
  properties: {
    value: aiservices_account.id
  }
}



resource keyvalue_azureaiaiservicesnameai 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_NAME_AI'
  properties: {
    value: aiservices_account.name
  }
}



resource keyvalue_azureaiaiservicesresourcegroupai 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_RESOURCE_GROUP_AI'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureaiaiservicesendpointai 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_ENDPOINT_AI'
  properties: {
    value: aiservices_account.properties.endpoint
  }
}



resource keyvalue_azuresearchidsearch 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_ID_SEARCH'
  properties: {
    value: searchservice.id
  }
}



resource keyvalue_azuresearchnamesearch 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_NAME_SEARCH'
  properties: {
    value: searchservice.name
  }
}



resource keyvalue_azuresearchresourcegroupsearch 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_RESOURCE_GROUP_SEARCH'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azuresearchendpointsearch 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_ENDPOINT_SEARCH'
  properties: {
    value: 'https://${searchservice.name}.search.windows.net/'
  }
}



resource keyvalue_azurestorageidstorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_ID_STORAGE'
  properties: {
    value: storageaccount.id
  }
}



resource keyvalue_azurestoragenamestorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_NAME_STORAGE'
  properties: {
    value: storageaccount.name
  }
}



resource keyvalue_azurestorageresourcegroupstorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_RESOURCE_GROUP_STORAGE'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureblobsendpointstorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOBS_ENDPOINT_STORAGE'
  properties: {
    value: storageaccount.properties.primaryEndpoints.blob
  }
}



resource keyvalue_azurekeyvaultidvault 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_ID_VAULT'
  properties: {
    value: vault.id
  }
}



resource keyvalue_azurekeyvaultnamevault 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_NAME_VAULT'
  properties: {
    value: vault.name
  }
}



resource keyvalue_azurekeyvaultresourcegroupvault 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_RESOURCE_GROUP_VAULT'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azurekeyvaultendpointvault 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_ENDPOINT_VAULT'
  properties: {
    value: vault.properties.vaultUri
  }
}



resource keyvalue_azureaifoundryhubidhub 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AIFOUNDRY_HUB_ID_HUB'
  properties: {
    value: hub_workspace.id
  }
}



resource keyvalue_azureaifoundryhubnamehub 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AIFOUNDRY_HUB_NAME_HUB'
  properties: {
    value: hub_workspace.name
  }
}



resource keyvalue_azureaifoundryhubresourcegrouphub 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AIFOUNDRY_HUB_RESOURCE_GROUP_HUB'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureaifoundryprojectidproject 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AIFOUNDRY_PROJECT_ID_PROJECT'
  properties: {
    value: project_workspace.id
  }
}



resource keyvalue_azureaifoundryprojectnameproject 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AIFOUNDRY_PROJECT_NAME_PROJECT'
  properties: {
    value: project_workspace.name
  }
}



resource keyvalue_azureaifoundryprojectresourcegroupproject 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AIFOUNDRY_PROJECT_RESOURCE_GROUP_PROJECT'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureaifoundryprojectendpointproject 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AIFOUNDRY_PROJECT_ENDPOINT_PROJECT'
  properties: {
    value: project_workspace.properties.discoveryUrl
  }
}



resource roleassignment_gxaeyfznpvgorjrkpllp 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, defaultName, 'ServicePrincipal', 'App Configuration Data Reader')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '516239f1-63e1-4d78-a4de-a74fb236a071'
    )

  }
  scope: configurationstore
}



resource roleassignment_unxsuzdqhucrcsmcfuyc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, defaultName, 'User', 'App Configuration Data Owner')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b'
    )

  }
  scope: configurationstore
}



resource roleassignment_iwqyskxadwyqpexjwfcy 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI Contributor')
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



resource roleassignment_hmfasjqbixwvwxlvyigx 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services Contributor')
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



resource roleassignment_qiwviqlvorhviuoikyhn 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI User')
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



resource roleassignment_vqsitscwkobrdvlojpeo 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services User')
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



resource roleassignment_djccqiqwpzkgpvmsxtpg 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI Contributor')
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



resource roleassignment_rgqwxelwqrhtwxkejhyc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'User', 'Cognitive Services Contributor')
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



resource roleassignment_eiambevcfusbcnjuoefk 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI User')
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



resource roleassignment_ulmeiktaicqeonwxbgkw 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'User', 'Cognitive Services User')
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



resource roleassignment_abzfoushrjbmnlrhqrnd 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, defaultName, 'ServicePrincipal', 'Search Index Data Contributor')
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



resource roleassignment_hvisesjfcmlfirhfodqk 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, defaultName, 'ServicePrincipal', 'Search Index Data Reader')
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



resource roleassignment_hjoxkiksaauprlvmtajt 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, defaultName, 'ServicePrincipal', 'Search Service Contributor')
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



resource roleassignment_xbkkwfxuhxhkoubdvkgs 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, defaultName, 'User', 'Search Index Data Contributor')
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



resource roleassignment_fozyeqjragxsjygyqahr 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, defaultName, 'User', 'Search Index Data Reader')
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



resource roleassignment_miizhpyelsmuregyflxu 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, defaultName, 'User', 'Search Service Contributor')
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



resource roleassignment_qdxwvfwdcxdhyslfngyw 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', environmentName, storageaccount.name, 'default', 'ServicePrincipal', 'Storage Blob Data Contributor')
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



resource roleassignment_coargsxbrhdmojcevwkk 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', environmentName, storageaccount.name, 'default', 'User', 'Storage Blob Data Contributor')
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



resource roleassignment_gcbdbuudnabzzeifflkj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', environmentName, defaultName, 'ServicePrincipal', 'Key Vault Administrator')
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



resource roleassignment_nqvjjhotidgzatrnakyo 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', environmentName, defaultName, 'User', 'Key Vault Administrator')
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



resource roleassignment_spqbmvwxoqzqsqzxfotj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftMachineLearningServicesworkspaces', environmentName, '${defaultName}-project', 'ServicePrincipal', 'Contributor')
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



resource roleassignment_jrohwqfrqxqaoskjukqf 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftMachineLearningServicesworkspaces', environmentName, '${defaultName}-project', 'User', 'Contributor')
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



resource roleassignment_kvjoxlocbytxyhtrwdln 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftResourcesresourceGroups', environmentName, defaultName, 'User', 'App Configuration Data Owner')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b'
    )

  }
  scope: resourceGroup()
}



