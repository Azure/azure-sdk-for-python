// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

targetScope = 'subscription'

import { SharedIdentities as SharedIdentityDictionary } from './identities.bicep'

@sealed()
type RoleAssignmentMetadata = {
  roleAssignmentId: string
  principalId: string
  roleDefinitionId: string
  scope: string
  condition: string
  conditionVersion: string
}

@sealed()
type BootstrapRoleAssignments = {
  project: RoleAssignmentMetadata[]
  pipeline: RoleAssignmentMetadata?
}

// The guarded entry point derives these names from the explicit set and canonical
// region and rejects existing resources. ARM declarations alone are NOT create-only.
@minLength(1)
@maxLength(90)
param identityResourceGroup string

@minLength(1)
@maxLength(33)
param namePrefix string

@minLength(1)
@maxLength(30)
param location string

@minLength(32)
@maxLength(32)
param ownerToken string

// Empty principal AND assignment ID mean no pipeline grant. A reused grant is
// verified by the entry point, but is deliberately absent from the deployment.
param pipelinePrincipalId string
param pipelineRoleAssignmentId string
param createPipelineGrant bool

var locationSuffix = location

resource identityResources 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: identityResourceGroup
  location: location
  tags: {
    purpose: 'azsdk-sample-identities'
    'sample-ci-owner': ownerToken
    'sample-ci-retention': 'permanent'
  }
}

module sharedIdentities './identities.bicep' = {
  name: 'shared-identities-${uniqueString(identityResources.id, namePrefix, locationSuffix)}'
  scope: identityResources
  params: {
    namePrefix: namePrefix
    location: location
    locationSuffix: locationSuffix
    ownerToken: ownerToken
  }
}

var approvedRoleDefinitionIds = {
  foundryUser: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '53ca6127-db72-4b80-b1b0-d745d6d5456d')
  storageBlobDataContributor: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  storageBlobDataOwner: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b')
  cosmosDbOperator: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '230815da-be43-4aae-9cb4-875f7bd000aa')
  searchServiceContributor: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
  searchIndexDataContributor: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
}

// Preserve the reviewed condition byte-for-byte, including whitespace. Only these
// three actions are suffix-restricted; other Blob Data Owner permissions remain.
var storageBlobOwnerCondition = '((!(ActionMatches{\'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read\'})  AND  !(ActionMatches{\'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/filter/action\'}) AND  !(ActionMatches{\'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write\'}) ) OR (@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringLikeIgnoreCase \'*-azureml-agent\'))'

var projectServiceGrants = [
  { roleDefinitionId: approvedRoleDefinitionIds.foundryUser, condition: '' }
  { roleDefinitionId: approvedRoleDefinitionIds.storageBlobDataContributor, condition: '' }
  { roleDefinitionId: approvedRoleDefinitionIds.storageBlobDataOwner, condition: storageBlobOwnerCondition }
  { roleDefinitionId: approvedRoleDefinitionIds.cosmosDbOperator, condition: '' }
  { roleDefinitionId: approvedRoleDefinitionIds.searchServiceContributor, condition: '' }
  { roleDefinitionId: approvedRoleDefinitionIds.searchIndexDataContributor, condition: '' }
]

var projectIdentityResourceId = resourceId(
  subscription().subscriptionId,
  identityResourceGroup,
  'Microsoft.ManagedIdentity/userAssignedIdentities',
  '${namePrefix}-project-${locationSuffix}'
)

resource projectRoleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for grant in projectServiceGrants: {
  // Keep the original UUIDv5 seeds, including full lowercase role definition ID
  // and the empty final argument for an unconditioned role.
  name: guid(toLower(projectIdentityResourceId), toLower(subscription().id), toLower(grant.roleDefinitionId), grant.condition)
  scope: subscription()
  properties: {
    principalId: sharedIdentities.outputs.identities.project.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: grant.roleDefinitionId
    condition: empty(grant.condition) ? null : grant.condition
    conditionVersion: empty(grant.condition) ? null : '2.0'
  }
}]

resource pipelineFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (createPipelineGrant) {
  name: guid(toLower(pipelinePrincipalId), toLower(subscription().id), toLower(approvedRoleDefinitionIds.foundryUser), '')
  scope: subscription()
  properties: {
    principalId: pipelinePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: approvedRoleDefinitionIds.foundryUser
  }
}

output identityResourceGroupId string = identityResources.id
output identities SharedIdentityDictionary = sharedIdentities.outputs.identities
output roleDefinitionIds object = approvedRoleDefinitionIds
output blobOwnerCondition string = storageBlobOwnerCondition
output roleAssignments BootstrapRoleAssignments = {
  project: map(projectServiceGrants, grant => {
    roleAssignmentId: subscriptionResourceId('Microsoft.Authorization/roleAssignments', guid(toLower(projectIdentityResourceId), toLower(subscription().id), toLower(grant.roleDefinitionId), grant.condition))
    principalId: sharedIdentities.outputs.identities.project.principalId
    roleDefinitionId: grant.roleDefinitionId
    scope: subscription().id
    condition: grant.condition
    conditionVersion: empty(grant.condition) ? '' : '2.0'
  })
  pipeline: empty(pipelinePrincipalId) ? null : {
    roleAssignmentId: pipelineRoleAssignmentId
    principalId: pipelinePrincipalId
    roleDefinitionId: approvedRoleDefinitionIds.foundryUser
    scope: subscription().id
    condition: ''
    conditionVersion: ''
  }
}

