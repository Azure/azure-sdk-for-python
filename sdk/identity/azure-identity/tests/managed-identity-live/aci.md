# Testing managed identity with Azure Container Instances

# prerequisite tools
- Azure CLI
  - https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest
- Docker CLI
  - https://hub.docker.com/search?q=&type=edition&offering=community


# Azure resources
This test requires instances of these Azure resources:
- Azure Key Vault
- Azure Managed Identity
  - with secrets/set and secrets/delete permission for the Key Vault
- Azure Container Registry

The rest of this section is a walkthrough of deploying these resources.

## set environment variables to simplify copy-pasting
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

## resource group
```sh
az group create -n $RESOURCE_GROUP --location westus2
```

## managed identity
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
  --secret-permissions set delete
```

## container registry
```sh
az acr create -g $RESOURCE_GROUP -n $ACR_NAME --admin-enabled --sku basic
```

# build images
The test application must be packaged as a Docker image. Two images are needed
because the test must run on Python 2 and 3.

## authenticate to ACR
```sh
az acr login -n $ACR_NAME
```

## acquire the test code
```sh
git clone https://github.com/Azure/azure-sdk-for-python/ --branch master --single-branch --depth 1
```

The rest of this section assumes this working directory:
```sh
cd azure-sdk-for-python/sdk/identity/azure-identity/tests
```

## build images and push them to the container registry
### set environment variables
```sh
export REPOSITORY=$(az acr show -g $RESOURCE_GROUP -n $ACR_NAME --query loginServer -o tsv) \
  IMAGE_NAME=test-pod-identity \
  PYTHON_VERSION=2.7
```

### build an image
```sh
docker build --no-cache --build-arg PYTHON_TAG=$PYTHON_VERSION -t $REPOSITORY/$IMAGE_NAME:$PYTHON_VERSION ./managed-identity-live
```

### push it to the registry
```sh
docker push $REPOSITORY/$IMAGE_NAME:$PYTHON_VERSION
```

Then set `PYTHON_VERSION` to the latest 3.x and run the above `docker build`
and `docker push` commands again. (It's safe--and faster--to omit
`--no-cache` from `docker build` the second time.)


# run tests

Run these commands twice, once with `PYTHON_VERSION=2.7` and again with the
latest 3.x.

## set a name for the container group
```sh
export CONTAINER_NAME=managed-id-test-python${PYTHON_VERSION::1}
```

## run the test
```sh
az container create -g $RESOURCE_GROUP -n $CONTAINER_NAME \
 --assign-identity $MANAGED_IDENTITY_ID \
 --restart-policy OnFailure \
 --registry-username $(az acr credential show -n $ACR_NAME --query username -o tsv) \
 --registry-password $(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv) \
 --image $REPOSITORY/$IMAGE_NAME:$PYTHON_VERSION \
 -e AZURE_IDENTITY_TEST_VAULT_URL=$(az keyvault show -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --query properties.vaultUri -o tsv)
```

## inspect output
```sh
az container logs -g $RESOURCE_GROUP -n $CONTAINER_NAME
```

Success looks like this:
```
============================= test session starts ==============================
platform linux -- Python 3.8.1, pytest-5.3.2, py-1.8.1, pluggy-0.13.1 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /azure-sdk-for-python, inifile: setup.cfg
plugins: asyncio-0.10.0
collecting ... collected 2 items

test_managed_identity_live.py::test_managed_identity_live PASSED
test_managed_identity_live_async.py::test_managed_identity_live PASSED

============================= 2 passed in 0.43s ================================
```
`test_managed_identity_live` must pass. Other test cases may be skipped. No test case may fail.

# Delete Azure resources
Finally, delete the resources created above:
```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```
