# Test Azure Identity in Azure Container Instances

# Prerequisite tools
- Azure CLI
  - https://learn.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest
- Docker CLI
  - https://hub.docker.com/search?q=&type=edition&offering=community


# Azure resources
This test requires instances of these Azure resources:
- Azure Key Vault
- Azure Managed Identity
  - with secrets/set and secrets/delete permission for the Key Vault
- Azure Container Registry

The rest of this section is a walkthrough of deploying these resources.

## Set environment variables to simplify copy-pasting
- RESOURCE_GROUP
  - name of an Azure resource group
  - must be unique in the Azure subscription
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

## Create resource group
```sh
az group create -n $RESOURCE_GROUP --location westus2
```

## Create a managed identity
### Create the managed identity
```sh
az identity create -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME
```

### Save its ARM URI for later
```sh
export MANAGED_IDENTITY_ID=$(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME --query id -o tsv)
```

## Key Vault
### Create the Vault
```sh
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard
```

### Add an access policy for the managed identity
```sh
az keyvault set-policy -n $KEY_VAULT_NAME \
  --object-id $(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME --query principalId -o tsv) \
  --secret-permissions set delete list
```

## Create Container Registry
```sh
az acr create -g $RESOURCE_GROUP -n $ACR_NAME --admin-enabled --sku basic
```

# Build container images
The test application must be packaged as a Docker image.

## Authenticate to ACR
```sh
az acr login -n $ACR_NAME
```

## Acquire the test code
```sh
git clone https://github.com/Azure/azure-sdk-for-python/ --branch main --single-branch --depth 1
```

The rest of this section assumes this working directory:
```sh
cd azure-sdk-for-python/sdk/identity/azure-identity/tests
```

## Build and push images to container registry
### Set environment variables
```sh
export REPOSITORY=$(az acr show -g $RESOURCE_GROUP -n $ACR_NAME --query loginServer -o tsv) \
  IMAGE_NAME=test-pod-identity \
  PYTHON_VERSION=3.10
```

### Build image
```sh
docker build --no-cache --build-arg PYTHON_VERSION=$PYTHON_VERSION -t $REPOSITORY/$IMAGE_NAME:$PYTHON_VERSION ./managed-identity-live
```

### Push image
```sh
docker push $REPOSITORY/$IMAGE_NAME:$PYTHON_VERSION
```

Then set `PYTHON_VERSION` to the latest 3.x and run the above `docker build`
and `docker push` commands again. (It's safe--and faster--to omit
`--no-cache` from `docker build` the second time.)

# Run tests

Run these commands to run the tests in a container instance.

## Set a name for the container group
```sh
export CONTAINER_NAME=managed-id-container-test-python${PYTHON_VERSION::1}
```

## Run the test
```sh
az container create -g $RESOURCE_GROUP -n $CONTAINER_NAME \
 --assign-identity $MANAGED_IDENTITY_ID \
 --restart-policy OnFailure \
 --registry-username $(az acr credential show -n $ACR_NAME --query username -o tsv) \
 --registry-password $(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv) \
 --image $REPOSITORY/$IMAGE_NAME:$PYTHON_VERSION \
 -e AZURE_IDENTITY_TEST_VAULT_URL=$(az keyvault show -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --query properties.vaultUri -o tsv)
```

## Inspect output
```sh
az container logs -g $RESOURCE_GROUP -n $CONTAINER_NAME
```

Success looks like this:
```
============================= test session starts ==============================
platform linux -- Python 3.10.8, pytest-7.2.0, pluggy-1.0.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /sdk/identity/azure-identity
plugins: asyncio-0.20.1, cov-4.0.0
asyncio: mode=strict
collecting ... collected 4 items

test_cloud_shell.py::test_cloud_shell_live SKIPPED (Cloud Shell MSI ...)  [ 25%]
test_cloud_shell_async.py::test_cloud_shell_live SKIPPED (Cloud Shell...) [ 50%]
test_managed_identity_live.py::test_managed_identity_live PASSED          [ 75%]
test_managed_identity_live_async.py::test_managed_identity_live PASSED    [100%]

=========================== short test summary info ============================
SKIPPED [2] conftest.py:46: Cloud Shell MSI unavailable
========================= 2 passed, 2 skipped in 1.30s =========================
```
`test_managed_identity_live` must pass. Other test cases may be skipped. No test case may fail.

# Delete Azure resources
Finally, delete the resources created above:
```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```
