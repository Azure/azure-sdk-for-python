// Standard agent setup

@allowed([
  'australiaeast'
  'canadaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'japaneast'
  'koreacentral'
  'norwayeast'
  'polandcentral'
  'southindia'
  'swedencentral'
  'switzerlandnorth'
  'uaenorth'
  'uksouth'
  'westus'
  'westus3'
  'westeurope'
  'southeastasia'
])
@description('The Azure region where your AI Foundry resource and project will be created.')
param location string = 'eastus'

@maxLength(9)
@description('The name of the Azure AI Foundry resource.')
param aiServices string = 'foundry'

@description('Name for your project resource.')
param firstProjectName string = 'project'

@description('This project will be a sub-resource of your account')
param projectDescription string = 'some description'

@description('The display name of the project')
param displayName string = 'project'

// Model deployment parameters
@description('The name of the model you want to deploy')
param modelName string = 'gpt-4'

@description('The provider of your model')
param modelFormat string = 'OpenAI'

@description('The version of your model')
param modelVersion string = 'turbo-2024-04-09'

@description('The sku of your model deployment')
param modelSkuName string = 'GlobalStandard'

@description('The tokens per minute (TPM) of your model deployment')
param modelCapacity int = 1

// Optionally bring existing resources
@description('The AI Search Service full ARM Resource ID. This is an optional field, and if not provided, the resource will be created.')
param aiSearchResourceId string = ''

@description('The AI Storage Account full ARM Resource ID. This is an optional field, and if not provided, the resource will be created.')
param azureStorageAccountResourceId string = ''

param projectCapHost string = 'caphostproj'
param accountCapHost string = 'caphostacc'

// Create a short, unique suffix, that will be unique to each resource group
param deploymentTimestamp string = utcNow('yyyyMMddHHmmss')
var uniqueSuffix = substring(uniqueString('${resourceGroup().id}-${deploymentTimestamp}'), 0, 4)
var accountName = toLower('${aiServices}${uniqueSuffix}')
var projectName = toLower('${firstProjectName}${uniqueSuffix}')


var aiSearchName = toLower('${uniqueSuffix}search')
var azureStorageName = toLower('${uniqueSuffix}storage')

// Check if existing resources have been passed in
var storagePassedIn = azureStorageAccountResourceId != ''
var searchPassedIn = aiSearchResourceId != ''

var acsParts = split(aiSearchResourceId, '/')
var aiSearchServiceSubscriptionId = searchPassedIn ? acsParts[2] : subscription().subscriptionId
var aiSearchServiceResourceGroupName = searchPassedIn ? acsParts[4] : resourceGroup().name

var storageParts = split(azureStorageAccountResourceId, '/')
var azureStorageSubscriptionId = storagePassedIn ? storageParts[2] : subscription().subscriptionId
var azureStorageResourceGroupName = storagePassedIn ? storageParts[4] : resourceGroup().name

/*
  Validate existing resources
  This module will check if the AI Search Service and Storage Account already exist.
  If they do, it will set the corresponding output to true. If they do not exist, it will set the output to false.
*/
module validateExistingResources 'modules-standard/validate-existing-resources.bicep' = {
  name: 'validate-existing-resources-${uniqueSuffix}-deployment'
  params: {
    aiSearchResourceId: aiSearchResourceId
    azureStorageAccountResourceId: azureStorageAccountResourceId
  }
}

// This module will create new agent dependent resources
// An AI Search Service and a Storage Account are created if they do not already exist
module aiDependencies 'modules-standard/standard-dependent-resources.bicep' = {
  name: 'dependencies-${accountName}-${uniqueSuffix}-deployment'
  params: {
    location: location
    azureStorageName: azureStorageName
    aiSearchName: aiSearchName

    // AI Search Service parameters
    aiSearchResourceId: aiSearchResourceId
    aiSearchExists: validateExistingResources.outputs.aiSearchExists

    // Storage Account
    azureStorageAccountResourceId: azureStorageAccountResourceId
    azureStorageExists: validateExistingResources.outputs.azureStorageExists
  }
}

/*
  Create the AI Services account and gpt-4o model deployment
*/
module aiAccount 'modules-standard/ai-account-identity.bicep' = {
  name: 'ai-${accountName}-${uniqueSuffix}-deployment'
  params: {
    accountName: accountName
    location: location
    modelName: modelName
    modelFormat: modelFormat
    modelVersion: modelVersion
    modelSkuName: modelSkuName
    modelCapacity: modelCapacity
  }
  dependsOn: [
    validateExistingResources, aiDependencies
  ]
}

/*
  Creates a new project (sub-resource of the AI Services account)
*/
module aiProject 'modules-standard/ai-project-identity.bicep' = {
  name: 'ai-${projectName}-${uniqueSuffix}-deployment'
  params: {
    projectName: projectName
    projectDescription: projectDescription
    displayName: displayName
    location: location

    aiSearchName: aiDependencies.outputs.aiSearchName
    aiSearchServiceResourceGroupName: aiDependencies.outputs.aiSearchServiceResourceGroupName
    aiSearchServiceSubscriptionId: aiDependencies.outputs.aiSearchServiceSubscriptionId

    azureStorageName: aiDependencies.outputs.azureStorageName
    azureStorageSubscriptionId: aiDependencies.outputs.azureStorageSubscriptionId
    azureStorageResourceGroupName: aiDependencies.outputs.azureStorageResourceGroupName

    accountName: aiAccount.outputs.accountName
  }
}

module formatProjectWorkspaceId 'modules-standard/format-project-workspace-id.bicep' = {
  name: 'format-project-workspace-id-${uniqueSuffix}-deployment'
  params: {
    projectWorkspaceId: aiProject.outputs.projectWorkspaceId
  }
}

/*
  Assigns the project SMI the storage blob data contributor role on the storage account
*/
module storageAccountRoleAssignment 'modules-standard/azure-storage-account-role-assignment.bicep' = {
  name: 'storage-${azureStorageName}-${uniqueSuffix}-deployment'
  scope: resourceGroup(azureStorageSubscriptionId, azureStorageResourceGroupName)
  params: {
    azureStorageName: aiDependencies.outputs.azureStorageName
    projectPrincipalId: aiProject.outputs.projectPrincipalId
  }
}


// This role can be assigned before or after the caphost is created
module aiSearchRoleAssignments 'modules-standard/ai-search-role-assignments.bicep' = {
  name: 'ai-search-ra-${uniqueSuffix}-deployment'
  scope: resourceGroup(aiSearchServiceSubscriptionId, aiSearchServiceResourceGroupName)
  params: {
    aiSearchName: aiDependencies.outputs.aiSearchName
    projectPrincipalId: aiProject.outputs.projectPrincipalId
  }
  dependsOn:[
    storageAccountRoleAssignment
  ]
}

module addProjectCapabilityHost 'modules-standard/add-project-capability-host.bicep' = {
  name: 'capabilityHost-configuration-${uniqueSuffix}-deployment'
  params: {
    accountName: aiAccount.outputs.accountName
    projectName: aiProject.outputs.projectName
    azureStorageConnection: aiProject.outputs.azureStorageConnection
    aiSearchConnection: aiProject.outputs.aiSearchConnection

    projectCapHost: projectCapHost
    accountCapHost: accountCapHost
  }
  dependsOn: [
    aiSearchRoleAssignments, storageAccountRoleAssignment
  ]
}

// The Storage Blob Data Owner role must be assigned before the caphost is created
module storageContainersRoleAssignment 'modules-standard/blob-storage-container-role-assignments.bicep' = {
  name: 'storage-containers-${uniqueSuffix}-deployment'
  scope: resourceGroup(azureStorageSubscriptionId, azureStorageResourceGroupName)
  params: {
    aiProjectPrincipalId: aiProject.outputs.projectPrincipalId
    storageName: aiDependencies.outputs.azureStorageName
    workspaceId: formatProjectWorkspaceId.outputs.projectWorkspaceIdGuid
  }
  dependsOn: [
    addProjectCapabilityHost
  ]
}
