# Testing azure-identity in Service Fabric

Setup for a Service Fabric cluster and two apps, used for testing managed identity using Azure.Identity.

The `sfmitestsystem` and `sfmitestuser` directories contain mock applications that use Azure.Identity's `ServiceFabricCredential` to request and verify Key Vault access tokens. The former application uses a system-assigned managed identity to do so, and the latter application uses a user-assigned managed identity.

The `arm-templates` directory contains Azure resource templates for creating these applications as well as a Service Fabric cluster to host them. The cluster template also deploys other resources that are necessary for running a cluster: a load balancer, public IP address, virtual machine scale set, virtual network, and two storage accounts.

### Environment requirements

> **Note:** All Azure resources used in the sample should be in the same region & resource group.

- This sample requires access to an Azure subscription and required privileges to create resources.
- [An SSH key pair is required.](https://docs.microsoft.com/azure/virtual-machines/linux/mac-create-ssh-keys#provide-an-ssh-public-key-when-deploying-a-vm)
- [Azure CLI is used to deploy resources and applications.](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest)
- Docker is needed to build and push the sample containerized services. Docker should be using Linux containers for building the application images that are provided.

### Clone this repository

From a command prompt window, run
```
git clone https://github.com/Azure/azure-sdk-for-python --single-branch --branch master --depth 1
cd azure-sdk-for-python/sdk/identity/azure-identity/tests/managed-identity-live/service-fabric
```

### Sections
- [Resource setup](#set-up-resources)
- [Application deployment](#set-up-and-deploy-the-applications)
- [Test validation](#run-the-tests)

## Set Up Resources

You can skip to [Set Up and Deploy the Applications](#set-up-and-deploy-the-applications) if you have an existing Service Fabric cluster, key vault, storage account, container registry, and managed identity named "AdminUser".

### Create a resource group

From a command prompt window, run:
```
az login
az group create -n $RESOURCE_GROUP --location $LOCATION --subscription $SUBSCRIPTION_NAME
```

### Create a user-assigned managed identity

From your command prompt window, run:
```
az identity create -g $RESOURCE_GROUP -n AdminUser
```

You will be prompted for this identity's principal ID and client ID in later steps. You can get these IDs by running:
```
az identity show -g $RESOURCE_GROUP -n AdminUser
```

### Create a key vault, certificate, and secret

Create your key vault:
```
az keyvault create -g $RESOURCE_GROUP -n $KEY_VAULT_NAME --sku standard --enabled-for-deployment true --enabled-for-template-deployment true
```

After creating the vault, [create a self-signed certificate](https://docs.microsoft.com/azure/key-vault/certificates/quick-create-portal#add-a-certificate-to-key-vault) in it using the [Azure Portal](https://portal.azure.com/). You'll need to insert some of this certificate's properties into the cluster template later on.

### Create an Azure Container Registry

From your command prompt window, run:
```
az acr create -g $RESOURCE_GROUP -n $ACR_NAME --admin-enabled --sku basic
```

### Deploy a managed identity-enabled cluster

At the time of writing, Service Fabric clusters must be deployed using the Azure Resource Manager in order to enable managed identity. Provided is a cluster ARM template that can be used to create a managed identity-enabled cluster once some required fields are completed. The template uses the cluster certificate provided by your key vault, creates a system-assigned identity, and enables the managed identity token service so deployed applications can access their identities.

To use the provided template:

1. Open `arm-templates/cluster.parameters.json` and complete the fields `clusterLocation`, `adminUserName`, `adminPassword`, `sourceVaultValue`, `certificateUrlValue`, `certificateThumbprint`, and `sshKeyData`. The placeholder values will describe how they should be completed.
2. In `arm-templates/cluster.parameters.json`, change all instances of `sfmi-test` to a unique name, like `<myusername>-sfmi-test`. Also, change the values of `applicationDiagnosticsStorageAccountName` and `supportLogStorageAccountName` to be similarly unique, but without hyphens. This will help ensure the deployment resource names do not conflict with the names of other public resources.
3. Start the deployment by running the following command in your command prompt:
```
az deployment group create --resource-group $RESOURCE_GROUP --template-file arm-templates\cluster.template.json --parameters arm-templates\cluster.parameters.json
```

This will begin to deploy a Service Fabric cluster as well as other necessary resources: a load balancer, public IP address, virtual machine scale set, virtual network, and two storage accounts.

## Set Up and Deploy the Applications

### Build and publish a Docker image for each application

For this manual test, each application will use a Docker image to run managed identity tests. To make these images available to Service Fabric, you need to publish them to a container registry.

1. Ensure Docker is running and is using Linux containers.
2. Authenticate to ACR:
```
az acr login -n $ACR_NAME
```
3. Build the images:
```
docker build --no-cache -t $ACR_NAME.azurecr.io/sfmitestsystem ..
docker build --no-cache -t $ACR_NAME.azurecr.io/sfmitestuser ..
```
4. Publish the images:
```
docker push $ACR_NAME.azurecr.io/sfmitestsystem
docker push $ACR_NAME.azurecr.io/sfmitestuser
```

### Package each application

Your Service Fabric cluster will target each application by referencing a `.sfpkg` in a storage account. First, you need to target your application images and create the package files.

1. In `sfmitestsystem/ApplicationManifest.xml` and `sfmitestuser/ApplicationManifest.xml`, fill in the values for your Azure Container Registry name and password in
```xml
<RepositoryCredentials AccountName="<ACR_NAME>" Password="<found in Access keys page of registry in Portal>" PasswordEncrypted="false"/>
```
2. In `sfmitestsystem/sfmitestsystemfrontPkg/ServiceManifest.xml`, replace `{ACR_NAME}` with your Azure Container Registry name in
```xml
<ImageName>{ACR_NAME}.azurecr.io/sfmitestsystem</ImageName>
```
3. Also in `sfmitestsystem/sfmitestsystemfrontPkg/ServiceManifest.xml`, replace `<KEY_VAULT_URL>` with your key vault's vault URI in
```xml
<EnvironmentVariable Name="AZURE_IDENTITY_TEST_VAULT_URL" Value="<KEY_VAULT_URL>"/>
```
4. Open the `sfmitestsystem` directory in File Explorer, select `sfmitestsystemfrontPkg` and `ApplicationManifest.xml`, and compress them into a zip file.
5. Rename the zip file `sfmitestsystem.sfpkg`.
6. In `sfmitestuser/sfmitestuserfrontPkg/ServiceManifest.xml`, replace `{ACR_NAME}` with your Azure Container Registry name in
```xml
<ImageName>{ACR_NAME}.azurecr.io/sfmitestuser</ImageName>
```
7. Also in `sfmitestuser/sfmitestuserfrontPkg/ServiceManifest.xml`, replace `<KEY_VAULT_URL>` with your key vault's vault URI and `<AdminUser client ID>` with the user-assigned managed identity's client ID in
```xml
<EnvironmentVariable Name="AZURE_IDENTITY_TEST_VAULT_URL" Value="<KEY_VAULT_URL>"/>
<EnvironmentVariable Name="AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID" Value="<AdminUser client ID>"/>
```
8. Open the `sfmitestuser` directory in File Explorer, select `sfmitestuserfrontPkg` and `ApplicationManifest.xml`, and compress them into a zip file.
9. Rename the zip file `sfmitestuser.sfpkg`.

### Upload the application packages to a storage account

If using an existing cluster, ensure your resource group has a storage account connected to your cluster. If you deployed a cluster using the template provided, two storage accounts were created but only one needs to store the `.sfpkg` files for the applications (the one with the name corresponding to `applicationDiagnosticsStorageAccountName` in the template). 

Go to your resource group in the [Azure Portal](https://portal.azure.com) and click on the storage account. Go to the "Containers" page and create a new container named "apps" -- be sure the set the public access level to Blob.

Open the apps container and upload the `.sfpkg` files you created earlier in the walkthrough. The container should now contain `sfmitestsystem.sfpkg` and `sfmitestuser.sfpkg`. Keep this page open to complete the next step.

### Deploy the applications

This sample also provides templates for deploying Service Fabric applications with Azure CLI.

To use the provided templates:

1. Open `arm-templates/sfmitestsystem.parameters.json` and complete the fields `clusterName`, `clusterLocation`, and `applicationPackageUrl`. `clusterName` and `clusterLocation` should match the name and location of your Service Fabric cluster. `applicationPackageUrl` is the URL of the `.sfpkg` you uploaded to a storage account in the previous step. To find the URL, click on `sfmitestsystem.sfpkg` in the Portal to view its properties.
2. Open `arm-templates/sfmitestuser.parameters.json` and complete the same fields, using the URL of `sfmitestuser.sfpkg` for `applicationPackageUrl`.
3. Start the deployment by running the following commands in your command prompt:
```
az deployment group create --resource-group $RESOURCE_GROUP --template-file arm-templates\sfmitestsystem.template.json --parameters arm-templates\sfmitestsystem.parameters.json
az deployment group create --resource-group $RESOURCE_GROUP --template-file arm-templates\sfmitestuser.template.json --parameters arm-templates\sfmitestuser.parameters.json
```

### Give the applications access to your key vault

If the applications were accessed now, they would report an error. This is because their managed identities don't have permission to access secrets in the key vault you created. 

To grant them access:

1. Get the object ID (`objectId`) of `sfmitestsystem`'s system-assigned managed identity. In your command prompt, run:
```
az ad sp list --display-name $CLUSTER_NAME/applications/sfmitestsystem
```
2. Give the application secret list permissions by setting an access policy:
```
az keyvault set-policy -n $KEY_VAULT_NAME --secret-permissions list --object-id $OBJECT_ID
```
3. Get the principal ID (`principalId`) of `sfmitestuser`'s user-assigned managed identity. In your command prompt, run:
```
az identity show -g $RESOURCE_GROUP -n AdminUser
```
4. Give the application secret list permissions by setting an access policy:
```
az keyvault set-policy -n $KEY_VAULT_NAME --secret-permissions list --object-id $PRINCIPAL_ID
```

## Run the Tests

Once running on your cluster, the applications should each perform the same task: using a `ManagedIdentityCredential` to list your key vault's secret properties. One uses a system-assigned managed identity to do so, while the other uses a user-assigned managed identity. To verify that they have each done their job correctly, you can access the application logs in your cluster's Service Fabric Explorer page.

Verify in a browser:

1. [Connect to your cluster on Service Fabric Explorer](https://docs.microsoft.com/azure/service-fabric/service-fabric-connect-to-secure-cluster#connect-to-a-secure-cluster-using-service-fabric-explorer).
2. In the Explorer, you should see the applications running under the Applications tab. Otherwise, you may need to double check your deployment process.
3. Under the Nodes tab, expand each node tab to see if it hosts an application ("fabric:/sfmitestsystem" or "fabric:/sfmitestuser").
4. When you find an application entry, click the "+" sign by the name to expand it. There should be a "code" entry -- click on that to bring up a page that has a "Container Logs" tab.
5. Go to the "Container Logs" tab to see the test output. The tests will re-run every so often, so you may have to watch the page for a short while to see the output. Verify that `test_managed_identity_live` shows `PASSED`.

This shows that the `ManagedIdentityCredential` works for Python 2.7. To test on Python 3.5, you'll need to re-build the Docker images and re-deploy the applications so they can target the new images.

1. Remove each application from the cluster. In the Service Fabric Explorer, expand the Applications tab and sfmitestsystemType tab. Click on "fabric:/sfmitestsystem", and in the application page, use the "Actions" tab at the top right to delete the application.
2. Now, remove the other application. Click on "fabric:/sfmitestuser" and use the "Actions" tab to delete the application.
3. Re-build the docker images, targeting Python 3.5 with `--build-arg`. In your command prompt, run:
```
docker build --no-cache --build-arg PYTHON_VERSION=3.5 -t $ACR_NAME.azurecr.io/sfmitestsystem ..
docker build --no-cache --build-arg PYTHON_VERSION=3.5 -t $ACR_NAME.azurecr.io/sfmitestuser ..
```
4. Publish the new images to your ACR:
```
docker push $ACR_NAME.azurecr.io/sfmitestsystem
docker push $ACR_NAME.azurecr.io/sfmitestuser
```
5. Re-deploy the applications:
```
az deployment group create --resource-group $RESOURCE_GROUP --template-file arm-templates\sfmitestsystem.template.json --parameters arm-templates\sfmitestsystem.parameters.json
az deployment group create --resource-group $RESOURCE_GROUP --template-file arm-templates\sfmitestuser.template.json --parameters arm-templates\sfmitestuser.parameters.json
```
6. Verify the test output again, as you did above. You should now also see that `test_managed_identity_live_async` shows `PASSED`.
