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



resource configurationstore_testconfig 'Microsoft.AppConfiguration/configurationStores@2024-05-01' = {
  properties: {
    disableLocalAuth: true
    createMode: 'Default'
    dataPlaneProxy: {
      authenticationMode: 'Pass-through'
      privateLinkDelegation: 'Disabled'
    }
    publicNetworkAccess: 'Enabled'
  }
  name: 'testconfig'
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

output AZURE_APPCONFIG_ID_TESTCONFIG string = configurationstore_testconfig.id
output AZURE_APPCONFIG_NAME_TESTCONFIG string = configurationstore_testconfig.name
output AZURE_APPCONFIG_RESOURCE_GROUP_TESTCONFIG string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT_TESTCONFIG string = configurationstore_testconfig.properties.endpoint


resource keyvalue_foo 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'foo'
  properties: {
    value: 'bar'
  }
}



resource keyvalue_testconfig_azureappconfigid 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_ID'
  properties: {
    value: configurationstore_testconfig.id
  }
}



resource keyvalue_testconfig_azureappconfigname 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_NAME'
  properties: {
    value: configurationstore_testconfig.name
  }
}



resource keyvalue_testconfig_azureappconfigresourcegroup 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_RESOURCE_GROUP'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_testconfig_azureappconfigendpoint 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_ENDPOINT'
  properties: {
    value: configurationstore_testconfig.properties.endpoint
  }
}



resource roleassignment_qogxikugotebchvshxhg 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, 'testconfig', 'ServicePrincipal', 'App Configuration Data Reader')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '516239f1-63e1-4d78-a4de-a74fb236a071'
    )

  }
  scope: configurationstore_testconfig
}



resource roleassignment_xuveegsvkevnnlargjxd 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, 'testconfig', 'User', 'App Configuration Data Owner')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b'
    )

  }
  scope: configurationstore_testconfig
}



resource roleassignment_cjanxuzqqzqoebkzaspn 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftResourcesresourceGroups', environmentName, 'testconfig', 'User', 'App Configuration Data Owner')
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



