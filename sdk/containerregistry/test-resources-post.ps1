# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

param (
    [hashtable] $DeploymentOutputs,
    [string] $TenantId,
    [string] $TestApplicationId,
    [string] $TestApplicationSecret
)

if ($IsMacOS) {
    Update-Module -Name Az.ContainerRegistry -Force
}

az acr import --name $DeploymentOutputs['CONTAINERREGISTRY_USERNAME'] --resource-group $DeploymentOutputs['CONTAINERREGISTRY_RESOURCE_GROUP'] docker.io/library/hello-world:latest -t library/hello-world:latest -t library/hello-world:latest:v1 -t library/hello-world:latest:v2 -t library/hello-world:latest:v3 -t library/hello-world:latest:v4 --force
az acr import --name $DeploymentOutputs['CONTAINERREGISTRY_USERNAME'] --resource-group $DeploymentOutputs['CONTAINERREGISTRY_RESOURCE_GROUP'] docker.io/library/alpine:latest -t library/alpine --force
az acr import --name $DeploymentOutputs['CONTAINERREGISTRY_USERNAME'] --resource-group $DeploymentOutputs['CONTAINERREGISTRY_RESOURCE_GROUP'] docker.io/library/busybox:latest -t library/busybox --force


Import-AzContainerRegistryImage `
    -ResourceGroupName $DeploymentOutputs['CONTAINERREGISTRY_RESOURCE_GROUP'] `
    -RegistryName $DeploymentOutputs['CONTAINERREGISTRY_USERNAME'] `
    -SourceImage 'library/hello-world' -SourceRegistryUri 'registry.hub.docker.com' `
    -TargetTag @('library/hello-world:latest', 'library/hello-world:v1', 'library/hello-world:v2', 'library/hello-world:v3', 'library/hello-world:v4') `
    -Mode 'Force'

Import-AzContainerRegistryImage `
    -ResourceGroupName $DeploymentOutputs['CONTAINERREGISTRY_RESOURCE_GROUP'] `
    -RegistryName $DeploymentOutputs['CONTAINERREGISTRY_USERNAME'] `
    -SourceImage 'library/alpine' -SourceRegistryUri 'registry.hub.docker.com' `
    -Mode 'Force'

Import-AzContainerRegistryImage `
    -ResourceGroupName $DeploymentOutputs['CONTAINERREGISTRY_RESOURCE_GROUP'] `
    -RegistryName $DeploymentOutputs['CONTAINERREGISTRY_USERNAME'] `
    -SourceImage 'library/busybox' -SourceRegistryUri 'registry.hub.docker.com' `
    -Mode 'Force'
