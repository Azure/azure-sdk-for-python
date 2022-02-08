# Testing managed identity in Azure Kubernetes Service

# prerequisite tools
- Azure CLI
  - https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest
- Docker CLI
  - https://hub.docker.com/search?q=&type=edition&offering=community
- Helm 2.x (3.x doesn't handle CRDs properly at time of writing)
  - https://github.com/helm/helm/releases


# Azure resources
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

### set environment variables to simplify copy-pasting
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

### resource group
```sh
az group create -n $RESOURCE_GROUP --location westus2
```

### managed identity
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

### Key Vault
Create the Vault:
```sh
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard
```

Add an access policy for the managed identity:
```sh
az keyvault set-policy -n $KEY_VAULT_NAME --object-id $MANAGED_IDENTITY_PRINCIPAL_ID --secret-permissions list
```

### container registry
```sh
az acr create -g $RESOURCE_GROUP -n $ACR_NAME --admin-enabled --sku basic
```

### Kubernetes
Deploy the cluster (this will take several minutes):
```sh
az aks create -g $RESOURCE_GROUP -n $AKS_NAME --generate-ssh-keys --node-count 1 --disable-rbac --attach-acr $ACR_NAME
```

Grant the cluster's service principal permission to use the managed identity:
```sh
az role assignment create --role "Managed Identity Operator" \
  --assignee $(az aks show -g $RESOURCE_GROUP -n $AKS_NAME --query servicePrincipalProfile.clientId -o tsv) \
  --scope $MANAGED_IDENTITY_ID
```


# build images
The test application must be packaged as a Docker image before deployment.
Test runs must include Python 3.6+.

### authenticate to ACR
```sh
az acr login -n $ACR_NAME
```

### acquire the test code
```sh
git clone https://github.com/Azure/azure-sdk-for-python/ --branch master --single-branch --depth 1
```

The rest of this section assumes this working directory:
```sh
cd azure-sdk-for-python/sdk/identity/azure-identity/tests
```

### build images and push them to the container registry
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

# run the test

### install kubectl
```sh
az aks install-cli
```

### authenticate kubectl and helm
```sh
az aks get-credentials -g $RESOURCE_GROUP -n $AKS_NAME
```

### install tiller
```sh
helm init --wait
```

### run the test script
With `PYTHON_VERSION=3.x`
(replacing x with the latest Python 3 minor version):
```sh
python ./pod-identity/run-test.py \
 --client-id $MANAGED_IDENTITY_CLIENT_ID \
 --resource-id $MANAGED_IDENTITY_ID \
 --vault-url https://$KEY_VAULT_NAME.vault.azure.net \
 --repository $REPOSITORY \
 --image-name $IMAGE_NAME \
 --image-tag $PYTHON_VERSION
```

### delete Azure resources
```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```
