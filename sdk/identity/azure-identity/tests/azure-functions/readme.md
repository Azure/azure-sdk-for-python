# testing azure-identity in Azure Functions
This directory contains artifacts for testing azure-identity in Azure Functions.

# prerequisite tools
- Azure CLI
- Azure Functions Core Tools 3.x
  - https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?#v2
- Docker CLI
  - https://hub.docker.com/search?q=&type=edition&offering=community

# Azure resources
This test requires instances of these Azure resources:
- Azure Key Vault
- Azure Managed Identity
  - with secrets/set and secrets/delete permission for the Key Vault
- Azure Storage account
- Azure App Service Plan
- Azure Function App x2
  - one for system-assigned identity, one for user-assigned

The rest of this section is a walkthrough of deploying these resources.

## Set environment variables
- RESOURCE_GROUP
  - name of an Azure resource group
  - must be unique in the Azure subscription
  - e.g. 'identity-test-rg'
- ACR_NAME
  - name of an Azure Container Registry
  - 5-50 alphanumeric characters
  - must be globally unique
- APP_SERVICE_PLAN
  - name of an Azure App Service Plan
- FUNCTION_APP_SYSTEM_ASSIGNED
  - name of an Azure function app
  - must be globally unique
- FUNCTION_APP_USER_ASSIGNED
  - name of an Azure function app
  - must be globally unique
- MANAGED_IDENTITY_NAME
  - name of the user-assigned identity
  - 3-128 alphanumeric characters
  - must be unique in the resource group
- STORAGE_ACCOUNT_NAME
  - 3-24 alphanumeric characters
  - must be globally unique (check it with `az storage account check-name`)
- KEY_VAULT_NAME
  - 3-24 alphanumeric characters
  - must begin with a letter
  - must be globally unique

## resource group
```sh
az group create -n $RESOURCE_GROUP --location westus2
```

### container registry
```sh
az acr create -g $RESOURCE_GROUP -n $ACR_NAME --admin-enabled --sku basic
```

## Key Vault:
```sh
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard
```

## Storage account
```sh
az storage account create -g $RESOURCE_GROUP -n $STORAGE_ACCOUNT_NAME
```

## App Service Plan
```sh
az appservice plan create -g $RESOURCE_GROUP -n $APP_SERVICE_PLAN -l westus2 --sku B1 --is-linux
```

## Functions App: system-assigned identity
```sh
az functionapp create -g $RESOURCE_GROUP -n $FUNCTION_APP_SYSTEM_ASSIGNED -s $STORAGE_ACCOUNT_NAME -p $APP_SERVICE_PLAN --runtime python
```

Set app configuration:
```sh
az functionapp config appsettings set -g $RESOURCE_GROUP -n $FUNCTION_APP_SYSTEM_ASSIGNED \
  --settings AZURE_IDENTITY_TEST_VAULT_URL=$(az keyvault show -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --query properties.vaultUri -o tsv)
```

Attach a system-assigned identity:
```sh
az functionapp identity assign -g $RESOURCE_GROUP -n $FUNCTION_APP_SYSTEM_ASSIGNED
```

Allow the system-assigned identity to access the Key Vault:
```sh
az keyvault set-policy -n $KEY_VAULT_NAME \
    --object-id $(az functionapp identity show -g $RESOURCE_GROUP -n $FUNCTION_APP_SYSTEM_ASSIGNED --query principalId -o tsv) \
    --secret-permissions set delete
```


## managed identity
Create the identity:
```sh
az identity create -n $MANAGED_IDENTITY_NAME -g $RESOURCE_GROUP -l westus2
```

Allow it to access the Key Vault:
```sh
az keyvault set-policy -n $KEY_VAULT_NAME \
    --object-id $(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME --query principalId -o tsv) \
    --secret-permissions set delete
```


## Functions App: user-assigned identity
```sh
az functionapp create -g $RESOURCE_GROUP -n $FUNCTION_APP_USER_ASSIGNED -s $STORAGE_ACCOUNT_NAME -p $APP_SERVICE_PLAN --runtime python
```

Set app configuration:
```sh
az functionapp config appsettings set -g $RESOURCE_GROUP -n $FUNCTION_APP_USER_ASSIGNED \
  --settings AZURE_IDENTITY_TEST_VAULT_URL=$(az keyvault show -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --query properties.vaultUri -o tsv) \
   AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID=$(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME -o tsv --query clientId)
```

At the time of writing, attaching user-assigned identities is impossible through the Azure CLI
([Azure/azure-cli#9887](https://github.com/Azure/azure-cli/issues/9887)).
Use the Azure Portal to attached the managed identity created above to the Functions App (see
[App Service documentation](https://docs.microsoft.com/en-us/azure/app-service/overview-managed-identity?tabs=dotnet#adding-a-user-assigned-identity)).


# build the Docker image
The test Functions are deployed as a container. The following command lines assume this working directory:
> `azure-sdk-for-python/sdk/identity/azure-identity/tests/azure-functions`


### authenticate to ACR
```sh
az acr login -n $ACR_NAME
```

### set a variable for the image name
```sh
export IMAGE=$(az acr show -n $ACR_NAME --query loginServer -o tsv)/functions-managed-id-test
```

### build the image
```sh
docker build --no-cache -t $IMAGE .
```

### push the image to the container registry
```sh
docker push $IMAGE
```

# deploy test code
Configure the Function Apps to use the image. For example, for the app using system-assigned identity:
```sh
az functionapp config container set -g $RESOURCE_GROUP -n $FUNCTION_APP_SYSTEM_ASSIGNED \
  -i $IMAGE \
  -r $(az acr show -n $ACR_NAME --query loginServer -o tsv) \
  -p $(az acr credential show -n $ACR_NAME --query "passwords[0].value" -o tsv) \
  -u $(az acr credential show -n $ACR_NAME --query username -o tsv)
```
Do this again for the app using a user-assigned identity (replace `FUNCTION_APP_SYSTEM_ASSIGNED` with `FUNCTION_APP_USER_ASSIGNED`).


# run tests
For each Functions App, get the tests' invocation URLs, and browse to each. For example, for the app using system-assigned identity:
```sh
func azure functionapp list-functions $FUNCTION_APP_SYSTEM_ASSIGNED --show-keys
```
Do this again for the app using a user-assigned identity (replace `FUNCTION_APP_SYSTEM_ASSIGNED` with `FUNCTION_APP_USER_ASSIGNED`).

The Function may execute before the App Service managed identity endpoint is ready, causing a test to fail initially. If this happens,
try again after a few minutes.

# Delete Azure resources
```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```
