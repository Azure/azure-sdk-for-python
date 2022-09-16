# Testing azure-identity in Azure App Service

## Prerequisite tools

- Azure CLI
- Docker CLI
  - https://hub.docker.com/search?q=&type=edition&offering=community

## Azure resources

This test requires instances of these Azure resources:

- Azure Key Vault
- Azure Managed Identity
  - with secrets/set and secrets/delete permission for the Key Vault
- Azure App Service Plan
- Azure Web App

The rest of this section is a walkthrough of deploying these resources.

### Set environment variables to simplify copy-pasting

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

### Resource group

```sh
az group create -n $RESOURCE_GROUP -l westus2
```

### Container registry

```sh
az acr create -g $RESOURCE_GROUP -n $ACR_NAME --admin-enabled --sku basic
```

### Key vault

```sh
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard
```

### App service plan

```sh
az appservice plan create -g $RESOURCE_GROUP -n $APP_SERVICE_PLAN -l westus2 --sku B1 --is-linux
```

### Web app: system-assigned identity

```sh
az webapp create -n $WEB_APP_SYSTEM_ASSIGNED -g $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "python|3.9"
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
    --secret-permissions list
```

### Managed identity
Create the identity:

```sh
az identity create -n $MANAGED_IDENTITY_NAME -g $RESOURCE_GROUP -l westus2
```

Allow it to access the Key Vault:

```sh
az keyvault set-policy -n $KEY_VAULT_NAME \
    --object-id $(az identity show -g $RESOURCE_GROUP -n $MANAGED_IDENTITY_NAME --query principalId -o tsv) \
    --secret-permissions list
```

### Web app: user-assigned identity

```sh
az webapp create -n $WEB_APP_USER_ASSIGNED -g $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime "python|3.9"
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
[App Service documentation](https://docs.microsoft.com/azure/app-service/overview-managed-identity?tabs=dotnet#adding-a-user-assigned-identity)).

## Build the Docker image

The test are deployed as a container. The following command lines assume this working directory:
> `azure-sdk-for-python/sdk/identity/azure-identity/tests`

We only need to test on Python 3.x

### Authenticate to ACR

```sh
az acr login -n $ACR_NAME
```

### Set a variable for the image name

```sh
export IMAGE_NAME=$(az acr show -n $ACR_NAME --query loginServer -o tsv)/webapp-managed-id-test  \
        PYTHON_VERSION=3.x 
```

### Build the image

```sh
docker build --no-cache --build-arg PYTHON_TAG=$PYTHON_VERSION -t $IMAGE_NAME:$PYTHON_VERSION ./managed-identity-live
```

### Push it to the registry

```sh
docker push $IMAGE_NAME:$PYTHON_VERSION
```

## Run tests

### Deploy test code

Configure the Web Apps to use the image. For example, for the app using system-assigned identity:

```sh
az webapp config container set -g $RESOURCE_GROUP -n $WEB_APP_SYSTEM_ASSIGNED \
  -i $IMAGE_NAME:$PYTHON_VERSION \
  -r $(az acr show -n $ACR_NAME --query loginServer -o tsv) \
  -p $(az acr credential show -n $ACR_NAME --query "passwords[0].value" -o tsv) \
  -u $(az acr credential show -n $ACR_NAME --query username -o tsv)
```

Do this again for the app using a user-assigned identity (replace `WEB_APP_SYSTEM_ASSIGNED` with `WEB_APP_USER_ASSIGNED`).

### Start the tests

We can start the test run by sending a request to the webapp.

e.g. for the app using system-assigned identity:

```sh
curl https://$WEB_APP_SYSTEM_ASSIGNED.azurewebsites.net
```

Do this again for the app using a user-assigned identity (replace `WEB_APP_SYSTEM_ASSIGNED` with `WEB_APP_USER_ASSIGNED`).

### Inspect output

#### Download the log file

```sh
az webapp log download -g $RESOURCE_GROUP -n $WEB_APP_SYSTEM_ASSIGNED
```

#### Unzip it

```sh
unzip webapp_logs.zip
```

check the logs in the file that ends with "default_docker.log"

Success looks like this:
```
============================= test session starts ==============================
platform linux -- Python 3.8.1, pytest-5.3.2, py-1.8.1, pluggy-0.13.1 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /azure-sdk-for-python, inifile: setup.cfg
plugins: asyncio-0.10.0
collecting ... collected 2 items
test_cloud_shell.py::test_cloud_shell_live SKIPPED
test_managed_identity_live.py::test_managed_identity_live PASSED
============================= 2 passed in 0.43s ================================
```

`test_managed_identity_live` must pass. Other test cases may be skipped. No test case may fail.

## Delete Azure resources

```sh
az group delete -n $RESOURCE_GROUP -y --no-wait
```
