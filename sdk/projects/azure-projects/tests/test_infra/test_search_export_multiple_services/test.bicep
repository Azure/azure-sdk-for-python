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
  properties: {
    disableLocalAuth: true
    createMode: 'Default'
    dataPlaneProxy: {
      authenticationMode: 'Pass-through'
      privateLinkDelegation: 'Disabled'
    }
    publicNetworkAccess: 'Enabled'
  }
  name: defaultName
  sku: {
    name: 'Standard'
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
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_SEARCH_ID string = searchservice.id
output AZURE_SEARCH_NAME string = searchservice.name
output AZURE_SEARCH_RESOURCE_GROUP string = resourceGroup().name
output AZURE_SEARCH_ENDPOINT string = 'https://${searchservice.name}.search.windows.net/'


resource searchservice_foo 'Microsoft.Search/searchServices@2024-06-01-Preview' = {
  properties: {
    publicNetworkAccess: 'Enabled'
  }
  name: 'foo'
  sku: {
    name: 'basic'
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

output AZURE_SEARCH_ID_FOO string = searchservice_foo.id
output AZURE_SEARCH_NAME_FOO string = searchservice_foo.name
output AZURE_SEARCH_RESOURCE_GROUP_FOO string = resourceGroup().name
output AZURE_SEARCH_ENDPOINT_FOO string = 'https://${searchservice_foo.name}.search.windows.net/'


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



resource keyvalue_azuresearchid 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_ID'
  properties: {
    value: searchservice.id
  }
}



resource keyvalue_azuresearchname 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_NAME'
  properties: {
    value: searchservice.name
  }
}



resource keyvalue_azuresearchresourcegroup 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_RESOURCE_GROUP'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azuresearchendpoint 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_ENDPOINT'
  properties: {
    value: 'https://${searchservice.name}.search.windows.net/'
  }
}



resource keyvalue_azuresearchidfoo 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_ID_FOO'
  properties: {
    value: searchservice_foo.id
  }
}



resource keyvalue_azuresearchnamefoo 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_NAME_FOO'
  properties: {
    value: searchservice_foo.name
  }
}



resource keyvalue_azuresearchresourcegroupfoo 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_RESOURCE_GROUP_FOO'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azuresearchendpointfoo 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_SEARCH_ENDPOINT_FOO'
  properties: {
    value: 'https://${searchservice_foo.name}.search.windows.net/'
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



resource roleassignment_wjiabjeybprroodbllpu 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, 'foo', 'ServicePrincipal', 'Search Index Data Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
    )

  }
  scope: searchservice_foo
}



resource roleassignment_picsxtzdxekegkbhzrds 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, 'foo', 'ServicePrincipal', 'Search Index Data Reader')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '1407120a-92aa-4202-b7e9-c0e197c71c8f'
    )

  }
  scope: searchservice_foo
}



resource roleassignment_uslydeuddigaymtmlpgi 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, 'foo', 'ServicePrincipal', 'Search Service Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
    )

  }
  scope: searchservice_foo
}



resource roleassignment_yvpwnndoanzxcsygtgpc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, 'foo', 'User', 'Search Index Data Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
    )

  }
  scope: searchservice_foo
}



resource roleassignment_hviqnnlkauvhovslxjjj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, 'foo', 'User', 'Search Index Data Reader')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '1407120a-92aa-4202-b7e9-c0e197c71c8f'
    )

  }
  scope: searchservice_foo
}



resource roleassignment_zjshshwzpzzayzizhino 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', environmentName, 'foo', 'User', 'Search Service Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
    )

  }
  scope: searchservice_foo
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



