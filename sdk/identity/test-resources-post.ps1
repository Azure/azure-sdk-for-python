# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# IMPORTANT: Do not invoke this file directly. Please instead run eng/New-TestResources.ps1 from the repository root.

param (
  [Parameter(ValueFromRemainingArguments = $true)]
  $RemainingArguments,

  [Parameter()]
  [hashtable] $DeploymentOutputs,

  [Parameter()]
  [hashtable] $AdditionalParameters = @{}
)

$ProvisionLiveResources = $AdditionalParameters['ProvisionLiveResources']
Write-Host "ProvisionLiveResources: $ProvisionLiveResources"
if ($CI -and !$ProvisionLiveResources) {
    Write-Host "Skipping test resource post-provisioning."
    return
}

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

$webappRoot = "$PSScriptRoot/azure-identity/tests/integration" | Resolve-Path
$workingFolder = $webappRoot;

Write-Host "Working directory: $workingFolder"

Write-Host "Sleeping for a bit to ensure container registry is ready."
Start-Sleep -s 60

az acr login -n $DeploymentOutputs['IDENTITY_ACR_NAME']
$loginServer = $DeploymentOutputs['IDENTITY_ACR_LOGIN_SERVER']


# Azure Functions app deployment
$image = "$loginServer/identity-functions-test-image"
docker build --no-cache -t $image "$workingFolder/azure-functions"
docker push $image

az functionapp config container set -g $DeploymentOutputs['IDENTITY_RESOURCE_GROUP'] -n $DeploymentOutputs['IDENTITY_FUNCTION_NAME'] -i $image -r $loginServer -p $(az acr credential show -n $DeploymentOutputs['IDENTITY_ACR_NAME'] --query "passwords[0].value" -o tsv) -u $(az acr credential show -n $DeploymentOutputs['IDENTITY_ACR_NAME'] --query username -o tsv)


# Azure Web Apps app deployment
Compress-Archive -Path "$workingFolder/azure-web-apps/*" -DestinationPath "$workingFolder/azure-web-apps/app.zip" -Force
az webapp deploy --resource-group $DeploymentOutputs['IDENTITY_RESOURCE_GROUP'] --name $DeploymentOutputs['IDENTITY_WEBAPP_NAME'] --src-path "$workingFolder/azure-web-apps/app.zip" --async true
Remove-Item -Force "$workingFolder/azure-web-apps/app.zip"


# Azure Kubernetes Service deployment
$image = "$loginServer/identity-aks-test-image"
docker build --no-cache -t $image "$workingFolder/azure-kubernetes-service"
docker push $image

# Attach the ACR to the AKS cluster
Write-Host "Attaching ACR to AKS cluster"
az aks update -n $DeploymentOutputs['IDENTITY_AKS_CLUSTER_NAME'] -g $DeploymentOutputs['IDENTITY_RESOURCE_GROUP'] --attach-acr $DeploymentOutputs['IDENTITY_ACR_NAME']

$MIClientId = $DeploymentOutputs['IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID']
$MIName = $DeploymentOutputs['IDENTITY_USER_DEFINED_IDENTITY_NAME']
$SaAccountName = 'workload-identity-sa'
$PodName = $DeploymentOutputs['IDENTITY_AKS_POD_NAME']
$storageName = $DeploymentOutputs['IDENTITY_STORAGE_NAME_2']

# Get the aks cluster credentials
Write-Host "Getting AKS credentials"
az aks get-credentials --resource-group $DeploymentOutputs['IDENTITY_RESOURCE_GROUP'] --name $DeploymentOutputs['IDENTITY_AKS_CLUSTER_NAME']

#Get the aks cluster OIDC issuer
Write-Host "Getting AKS OIDC issuer"
$AKS_OIDC_ISSUER = az aks show -n $DeploymentOutputs['IDENTITY_AKS_CLUSTER_NAME'] -g $DeploymentOutputs['IDENTITY_RESOURCE_GROUP'] --query "oidcIssuerProfile.issuerUrl" -otsv

# Create the federated identity
Write-Host "Creating federated identity"
az identity federated-credential create --name $MIName --identity-name $MIName --resource-group $DeploymentOutputs['IDENTITY_RESOURCE_GROUP'] --issuer $AKS_OIDC_ISSUER --subject system:serviceaccount:default:workload-identity-sa

# Build the kubernetes deployment yaml
$kubeConfig = @"
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: $MIClientId
  name: $SaAccountName
  namespace: default
---
apiVersion: v1
kind: Pod
metadata:
  name: $PodName
  namespace: default
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: $SaAccountName
  containers:
  - name: $PodName
    image: $image
    env:
    - name: IDENTITY_STORAGE_NAME
      value: "$StorageName"
    ports:
    - containerPort: 80
  nodeSelector:
    kubernetes.io/os: linux
"@

Set-Content -Path "$workingFolder/kubeconfig.yaml" -Value $kubeConfig
Write-Host "Created kubeconfig.yaml with contents:"
Write-Host $kubeConfig

# Apply the config
kubectl apply -f "$workingFolder/kubeconfig.yaml" --overwrite=true
Write-Host "Applied kubeconfig.yaml"

# Virtual machine setup
$vmScript = @"
sudo apt update && sudo apt install python3-pip -y --no-install-recommends &&
git clone https://github.com/Azure/azure-sdk-for-python.git --depth 1 --single-branch --branch main /sdk &&
cd /sdk/sdk/identity/azure-identity/tests/integration/azure-vms &&
pip install -r requirements.txt
"@
az vm run-command invoke -n $DeploymentOutputs['IDENTITY_VM_NAME'] -g $DeploymentOutputs['IDENTITY_RESOURCE_GROUP'] --command-id RunShellScript --scripts "$vmScript"


# ACI is easier to provision here than in the bicep file because the image isn't available before now
Write-Host "Deploying Azure Container Instance"
az container create -g $($DeploymentOutputs['IDENTITY_RESOURCE_GROUP']) -n $($DeploymentOutputs['IDENTITY_CONTAINER_INSTANCE_NAME']) --image $image `
  --acr-identity $($DeploymentOutputs['IDENTITY_USER_DEFINED_IDENTITY']) `
  --assign-identity [system] $($DeploymentOutputs['IDENTITY_USER_DEFINED_IDENTITY']) `
  --cpu 1 `
  --memory 1.0 `
  --os-type Linux `
  --role "Storage Blob Data Reader" `
  --scope $($DeploymentOutputs['IDENTITY_STORAGE_ID_1']) `
  -e IDENTITY_STORAGE_NAME=$($DeploymentOutputs['IDENTITY_STORAGE_NAME_1']) `
     IDENTITY_STORAGE_NAME_USER_ASSIGNED=$($DeploymentOutputs['IDENTITY_STORAGE_NAME_2']) `
     IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID=$($DeploymentOutputs['IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID']) `
     FUNCTIONS_CUSTOMHANDLER_PORT=80
