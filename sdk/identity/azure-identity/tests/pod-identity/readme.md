# Testing managed identity in Azure Kubernetes Service

## Prerequisite tools
- Azure CLI
  - https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest
- Docker CLI
  - https://hub.docker.com/search?q=&type=edition&offering=community
- Helm 3.x
  - https://helm.sh/docs/intro/install/


## Azure resources
This test requires instances of these Azure resources:
- Azure Key Vault
- Azure Managed Identity
  - with secrets/set and secrets/delete permission for the Key Vault
- Azure Container Registry
- Azure Kubernetes Service
  - RBAC requires additional configuration not provided here, so an RBAC-disabled cluster is preferable
  - the cluster's service principal must have 'Managed Identity Operator' role over the managed identity
  - must be able to pull from the Container Registry

The rest of this section is a walkthrough of deploying these resources.

### Set environment variables to simplify copy-pasting
- RESOURCE_GROUP
  - name of an Azure resource group
  - must be unique in the Azure subscription
  - e.g. 'pod-identity-test'
- AKS_NAME
  - name of an Azure Kubernetes Service
  - must be unique in the resource group
  - e.g. 'pod-identity-test'
- ACR_NAME
  - name of an Azure Container Registry
  - 5-50 alphanumeric characters
  - must be globally unique
- MANAGED_IDENTITY_NAME
  - 3-128 alphanumeric characters
  - must be unique in the resource group
- KEY_VAULT_NAME
  - 3-24 alphanumeric characters
  - must begin with a letter
  - must be globally unique

### Create resource group
```sh
az group create -n $RESOURCE_GROUP --location westus2
```

### Create managed identity
Create the managed identity:
```sh
az identity create -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME
```

Save its `clientId`, `id` (ARM URI), and `principalId` (object ID) for later:
```sh
export MANAGED_IDENTITY_CLIENT_ID=$(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME --query clientId -o tsv) \
       MANAGED_IDENTITY_ID=$(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME --query id -o tsv) \
       MANAGED_IDENTITY_PRINCIPAL_ID=$(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME --query principalId -o tsv)
```

### Create key vault
Create the Vault:
```sh
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard
```

Add an access policy for the managed identity:
```sh
az keyvault set-policy -n $KEY_VAULT_NAME --object-id $MANAGED_IDENTITY_PRINCIPAL_ID --secret-permissions list
```

### Create container registry
```sh
az acr create -g $RESOURCE_GROUP -n $ACR_NAME --admin-enabled --sku basic
```

### Create Kubernetes cluster
Deploy the cluster (this will take several minutes):
```sh
az aks create -g $RESOURCE_GROUP -n $AKS_NAME --generate-ssh-keys --node-count 1 --disable-rbac --attach-acr $ACR_NAME --enable-managed-identity
```

Save information about the cluster's node resource group:
```sh
export NODE_RESOURCE_GROUP=$(az aks show -g $RESOURCE_GROUP -n $AKS_NAME --query nodeResourceGroup -o tsv)
export NODE_RESOURCE_GROUP_SCOPE=$(az group show -n $NODE_RESOURCE_GROUP --query id -o tsv)
export KUBELET_IDENTITY_CLIENT_ID=$(az aks show -g $RESOURCE_GROUP -n $AKS_NAME --query identityProfile.kubeletidentity.clientId -o tsv)

```

### Create role assignments
Assign needed roles to the cluster managed identity:
```sh
az role assignment create --role "Managed Identity Operator" --assignee $KUBELET_IDENTITY_CLIENT_ID --scope $MANAGED_IDENTITY_ID
```

Add role assignments required by AAD Pod Identity:
```sh
az role assignment create --role "Managed Identity Operator" --assignee $KUBELET_IDENTITY_CLIENT_ID --scope $NODE_RESOURCE_GROUP_SCOPE
az role assignment create --role "Virtual Machine Contributor" --assignee $KUBELET_IDENTITY_CLIENT_ID --scope $NODE_RESOURCE_GROUP_SCOPE

```

**Note**: Sometimes the role assignments can take several minutes to propagate which may cause `Init:Error` statuses in the test pod
if the tests are run too soon after the role assignments are created. If this is encountered, wait a few more minutes and try again.

## Build images
The test application must be packaged as a Docker image before deployment.
Test runs must include Python 3.7+.

### Authenticate to ACR
```sh
az acr login -n $ACR_NAME
```

### Acquire the test code
```sh
git clone https://github.com/Azure/azure-sdk-for-python/ --branch main --single-branch --depth 1
```

The rest of this section assumes this working directory:
```sh
cd azure-sdk-for-python/sdk/identity/azure-identity/tests
```

### Build image and push them to the container registry
Set environment variables:
```sh
export REPOSITORY=$ACR_NAME.azurecr.io IMAGE_NAME=test-pod-identity PYTHON_VERSION=3.9
```

Build an image:
```sh
docker build --no-cache --build-arg PYTHON_VERSION=$PYTHON_VERSION -t $REPOSITORY/$IMAGE_NAME:$PYTHON_VERSION ./managed-identity-live
```

Push it to ACR:
```sh
docker push $REPOSITORY/$IMAGE_NAME:$PYTHON_VERSION
```

## Run the tests

### Install kubectl
```sh
az aks install-cli
```

### Authenticate kubectl and helm
```sh
az aks get-credentials -g $RESOURCE_GROUP -n $AKS_NAME
```

### Run the test script
```sh
python ./pod-identity/run-test.py \
 --client-id $MANAGED_IDENTITY_CLIENT_ID \
 --resource-id $MANAGED_IDENTITY_ID \
 --vault-url https://$KEY_VAULT_NAME.vault.azure.net \
 --repository $REPOSITORY \
 --image-name $IMAGE_NAME \
 --image-tag $PYTHON_VERSION
```

Successful test output looks like this:
```
============================= test session starts ==============================
platform linux -- Python 3.9.15, pytest-7.2.0, pluggy-1.0.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /sdk/identity/azure-identity
plugins: cov-4.0.0, asyncio-0.20.2
asyncio: mode=strict
collecting ... collected 4 items

test_cloud_shell.py::test_cloud_shell_live SKIPPED (Cloud Shell MSI ...) [ 25%]
test_cloud_shell_async.py::test_cloud_shell_live SKIPPED (Cloud Shel...) [ 50%]
test_managed_identity_live.py::test_managed_identity_live PASSED         [ 75%]
test_managed_identity_live_async.py::test_managed_identity_live PASSED   [100%]

=========================== short test summary info ============================
SKIPPED [2] conftest.py:46: Cloud Shell MSI unavailable
========================= 2 passed, 2 skipped in 1.29s =========================
```

**Note**: The `run_test.py` script may hang for a long time after the tests complete as it waits
for one of the test resources (AzureAssignedIdentity) to be deleted. Feel free to Ctrl-C if
the cluster will just be deleted afterwards.

## Delete Azure resources
```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```
