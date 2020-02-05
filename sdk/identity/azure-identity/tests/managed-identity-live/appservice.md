# Testing azure-identity in Azure App Service

# prerequisite tools
- Azure CLI
- Docker CLI
  - https://hub.docker.com/search?q=&type=edition&offering=community

# Azure resources
This test requires instances of these Azure resources:
- Azure Key Vault
- Azure Managed Identity
  - with secrets/set and secrets/delete permission for the Key Vault
- Azure App Service Plan
- Azure Web App

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
- APP_SERVICE_PLAN
  - name of an Azure App Service Plan
- WEB_APP_SYSTEM_ASSIGNED
- WEB_APP_USER_ASSIGNED

## resource group
```sh
az group create -n $RESOURCE_GROUP -l westus2
```

## container registry
```sh
az acr create -g $RESOURCE_GROUP -n $ACR_NAME --admin-enabled --sku basic
```

## key vault
```sh
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard
```

## app service plan
```sh
az appservice plan create -g $RESOURCE_GROUP -n $APP_SERVICE_PLAN -l westus2 --sku B1 --is-linux
```

## web app: system-assigned identity
```sh
az webapp create -n $WEB_APP_SYSTEM_ASSIGNED -g $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "python|3.6"
```

Attach a system-assigned identity:
```sh
az webapp identity assign -n $WEB_APP_SYSTEM_ASSIGNED -g $RESOURCE_GROUP
```

Set app configuration:
```sh
az webapp config appsettings set -g $RESOURCE_GROUP -n $WEB_APP_SYSTEM_ASSIGNED \
  --settings AZURE_IDENTITY_TEST_VAULT_URL=$(az keyvault show -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --query properties.vaultUri -o tsv)
```

Allow the system-assigned identity to access the Key Vault:
```sh
az keyvault set-policy -n $KEY_VAULT_NAME -g $RESOURCE_GROUP \
    --object-id $(az webapp show -n $WEB_APP_SYSTEM_ASSIGNED -g $RESOURCE_GROUP --query identity.principalId -o tsv) \
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

## web app: user-assigned identity
```sh
az webapp create -n $WEB_APP_USER_ASSIGNED -g $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "python|3.6"
```

Set app configuration:
```sh
az webapp config appsettings set -g $RESOURCE_GROUP -n $WEB_APP_USER_ASSIGNED \
  --settings AZURE_IDENTITY_TEST_VAULT_URL=$(az keyvault show -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --query properties.vaultUri -o tsv) \
   AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID=$(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME -o tsv --query clientId)
```

At the time of writing, attaching user-assigned identities is impossible through the Azure CLI
([Azure/azure-cli#9887](https://github.com/Azure/azure-cli/issues/9887)).
Use the Azure Portal to attached the managed identity created above to the Web App (see
[App Service documentation](https://docs.microsoft.com/en-us/azure/app-service/overview-managed-identity?tabs=dotnet#adding-a-user-assigned-identity)).

# build the Docker image
The test are deployed as a container. The following command lines assume this working directory:
> `azure-sdk-for-python/sdk/identity/azure-identity/tests`

### authenticate to ACR
```sh
az acr login -n $ACR_NAME
```

### set a variable for the image name
```sh
export IMAGE_NAME=$(az acr show -n $ACR_NAME --query loginServer -o tsv)/webapp-managed-id-test \
    PYTHON_VERSION=2.7
```

### build the image
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

# deploy test code
Configure the Web Apps to use the image. For example, for the app using system-assigned identity:
```sh
az webapp config container set -g $RESOURCE_GROUP -n $WEB_APP_SYSTEM_ASSIGNED \
  -i $IMAGE_NAME:$PYTHON_VERSION \
  -r $(az acr show -n $ACR_NAME --query loginServer -o tsv) \
  -p $(az acr credential show -n $ACR_NAME --query "passwords[0].value" -o tsv) \
  -u $(az acr credential show -n $ACR_NAME --query username -o tsv)
```
Do this again for the app using a user-assigned identity (replace `WEB_APP_SYSTEM_ASSIGNED` with `WEB_APP_USER_ASSIGNED`).

# run tests
For each Web App, get the tests' invocation URLs, and browse to each. For example, for the app using system-assigned identity:
```sh
func azure functionapp list-functions $WEB_APP_SYSTEM_ASSIGNED --show-keys
```
Do this again for the app using a user-assigned identity (replace `WEB_APP_SYSTEM_ASSIGNED` with `WEB_APP_USER_ASSIGNED`).

# Delete Azure resources
```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```